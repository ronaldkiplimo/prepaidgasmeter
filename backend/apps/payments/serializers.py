import logging
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import transaction as db_transaction
from rest_framework import serializers

from apps.audit.services import log_audit
from apps.accounts.serializers import normalize_phone_number
from apps.meters.models import Meter
from apps.payments.models import Payment, Transaction
from apps.payments.services.mpesa import MpesaService
from apps.tokens.models import GasToken
from apps.tokens.services.stron import StronAPIError, StronVendingService

logger = logging.getLogger(__name__)


class VendingPreviewSerializer(serializers.Serializer):
    meter_id = serializers.UUIDField(required=False)
    meter_number = serializers.CharField(required=False)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate(self, attrs):
        user = self.context["request"].user
        meter = None
        meter_number = None

        if attrs.get("meter_id"):
            meter = Meter.objects.filter(id=attrs["meter_id"], user=user, is_active=True).first()
            if meter:
                meter_number = meter.meter_number
        if not meter_number and attrs.get("meter_number"):
            meter_number = attrs["meter_number"].strip().upper()
            meter = Meter.objects.filter(meter_number=meter_number, user=user, is_active=True).first()

        if not meter_number:
            raise serializers.ValidationError("Provide a valid meter_id or meter_number.")

        amount = attrs["amount"]
        min_amt = Decimal(str(settings.MIN_PURCHASE_AMOUNT))
        max_amt = Decimal(str(settings.MAX_PURCHASE_AMOUNT))
        if amount < min_amt or amount > max_amt:
            raise serializers.ValidationError(f"Amount must be between KES {min_amt} and KES {max_amt}.")

        attrs["meter"] = meter
        attrs["meter_number"] = meter.meter_number if meter else meter_number
        return attrs

    def save(self):
        meter_number = self.validated_data["meter_number"]
        amount = self.validated_data["amount"]
        stron = StronVendingService()
        try:
            meter_info = stron.query_meter_info(meter_number)
            preview = stron.vending_preview(meter_number, amount)
        except StronAPIError as exc:
            raise serializers.ValidationError({"detail": str(exc)})

        fee = Decimal(str(settings.SERVICE_FEE_PERCENT if hasattr(settings, "SERVICE_FEE_PERCENT") else 0))
        service_fee = (amount * fee / 100).quantize(Decimal("0.01")) if fee else Decimal("0")
        total = amount + service_fee

        return {
            "meter_number": meter_number,
            "amount": str(amount),
            "expected_units": str(preview.get("expected_units", 0)),
            "expected_credit": str(preview.get("expected_credit", amount)),
            "vat": str(preview.get("vat", 0)),
            "service_fee": str(service_fee),
            "total": str(total),
            "meter_info": meter_info,
            "preview": preview.get("raw_response", {}),
        }


class PurchaseTokenSerializer(serializers.Serializer):
    meter_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    phone_number = serializers.CharField(max_length=15, required=False)

    def validate_amount(self, value):
        min_amt = Decimal(str(settings.MIN_PURCHASE_AMOUNT))
        max_amt = Decimal(str(settings.MAX_PURCHASE_AMOUNT))
        if value < min_amt:
            raise serializers.ValidationError(f"Minimum purchase is KES {min_amt}.")
        if value > max_amt:
            raise serializers.ValidationError(f"Maximum purchase is KES {max_amt}.")
        return value

    def validate_meter_id(self, value):
        user = self.context["request"].user
        try:
            meter = Meter.objects.get(id=value, user=user, is_active=True)
        except Meter.DoesNotExist:
            raise serializers.ValidationError("Meter not found or inactive.")
        self.context["meter"] = meter
        return value

    def validate_phone_number(self, value):
        if not value:
            return value
        return normalize_phone_number(value)

    def create(self, validated_data):
        user = self.context["request"].user
        meter = self.context["meter"]
        amount = validated_data["amount"]
        phone = validated_data.get("phone_number") or user.phone_number

        stron = StronVendingService()
        try:
            preview = stron.vending_preview(meter.meter_number, amount)
        except StronAPIError as exc:
            raise serializers.ValidationError({"detail": f"Meter validation failed: {exc}"})

        reference = f"PGK{uuid.uuid4().hex[:12].upper()}"
        service_fee = Decimal("0")
        total = amount + service_fee

        with db_transaction.atomic():
            txn = Transaction.objects.create(
                reference=reference,
                user=user,
                meter=meter,
                amount=amount,
                expected_units=preview.get("expected_units", 0),
                expected_credit=preview.get("expected_credit", amount),
                service_fee=service_fee,
                total_amount=total,
                phone_number=phone,
                status=Transaction.Status.PAYMENT_INITIATED,
            )
            Payment.objects.create(
                transaction=txn,
                amount=total,
                phone_number=phone,
                status=Payment.Status.INITIATED,
            )

        mpesa = MpesaService()
        try:
            stk = mpesa.initiate_stk_push(
                phone_number=phone,
                amount=float(total),
                account_reference=reference,
                transaction_desc=f"PrepaidGas {meter.meter_number}",
            )
            payment = txn.payment
            payment.checkout_request_id = stk.get("CheckoutRequestID", "")
            payment.merchant_request_id = stk.get("MerchantRequestID", "")
            payment.status = Payment.Status.PENDING
            payment.save(update_fields=["checkout_request_id", "merchant_request_id", "status", "updated_at"])

            log_audit(
                user=user,
                action="PAYMENT_INITIATED",
                resource_type="Transaction",
                resource_id=str(txn.id),
                details={"reference": reference, "amount": str(total), "meter": meter.meter_number},
            )
        except Exception as exc:
            logger.exception("STK Push failed for %s", reference)
            txn.status = Transaction.Status.FAILED
            txn.failure_reason = str(exc)
            txn.save(update_fields=["status", "failure_reason", "updated_at"])
            txn.payment.status = Payment.Status.FAILED
            txn.payment.save(update_fields=["status", "updated_at"])
            raise serializers.ValidationError({"detail": "Failed to initiate M-Pesa payment."})

        return txn


class TransactionSerializer(serializers.ModelSerializer):
    meter_number = serializers.CharField(source="meter.meter_number", read_only=True)
    meter_nickname = serializers.CharField(source="meter.nickname", read_only=True)
    token = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()
    mpesa_receipt = serializers.CharField(source="payment.mpesa_receipt_number", read_only=True, default=None)

    class Meta:
        model = Transaction
        fields = (
            "id", "reference", "meter_number", "meter_nickname", "amount",
            "expected_units", "expected_credit", "service_fee", "total_amount",
            "status", "phone_number", "failure_reason", "token", "payment_status",
            "mpesa_receipt", "created_at", "completed_at",
        )

    def get_token(self, obj):
        if hasattr(obj, "gas_token"):
            t = obj.gas_token
            return {"token": t.token, "units": str(t.token_units), "status": t.status}
        return None

    def get_payment_status(self, obj):
        return obj.payment.status if hasattr(obj, "payment") else None


class GasTokenSerializer(serializers.ModelSerializer):
    transaction_reference = serializers.CharField(source="transaction.reference", read_only=True)

    class Meta:
        model = GasToken
        fields = (
            "id", "token", "token_units", "token_amount", "meter_number",
            "stron_receipt_number", "status", "transaction_reference",
            "generated_at", "delivered_at",
        )


ElectricityTokenSerializer = GasTokenSerializer
