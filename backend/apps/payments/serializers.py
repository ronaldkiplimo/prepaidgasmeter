import logging
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import transaction as db_transaction
from django.utils import timezone
from rest_framework import serializers

from apps.audit.services import log_audit
from apps.meters.models import Meter
from apps.payments.models import Payment, Transaction
from apps.payments.services.mpesa import MpesaService
from apps.tokens.models import ElectricityToken
from apps.tokens.tasks import generate_token_task

logger = logging.getLogger(__name__)


class PurchaseTokenSerializer(serializers.Serializer):
    meter_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    phone_number = serializers.CharField(max_length=15, required=False)

    def validate_amount(self, value):
        min_amt = Decimal(str(settings.MIN_PURCHASE_AMOUNT))
        max_amt = Decimal(str(settings.MAX_PURCHASE_AMOUNT))
        if value < min_amt:
            raise serializers.ValidationError(f"Minimum purchase amount is KES {min_amt}.")
        if value > max_amt:
            raise serializers.ValidationError(f"Maximum purchase amount is KES {max_amt}.")
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
        normalized = value.strip().replace(" ", "")
        if normalized.startswith("0"):
            normalized = "254" + normalized[1:]
        elif normalized.startswith("+"):
            normalized = normalized[1:]
        if not normalized.isdigit() or len(normalized) < 10 or len(normalized) > 15:
            raise serializers.ValidationError("Enter a valid M-Pesa phone number.")
        return normalized

    def create(self, validated_data):
        user = self.context["request"].user
        meter = self.context["meter"]
        amount = validated_data["amount"]
        phone = validated_data.get("phone_number") or self.validate_phone_number(user.phone_number)

        reference = f"TXN{uuid.uuid4().hex[:12].upper()}"

        with db_transaction.atomic():
            txn = Transaction.objects.create(
                reference=reference,
                user=user,
                meter=meter,
                amount=amount,
                phone_number=phone,
                status=Transaction.Status.PAYMENT_INITIATED,
            )
            payment = Payment.objects.create(
                transaction=txn,
                amount=amount,
                phone_number=phone,
                status=Payment.Status.INITIATED,
            )

        mpesa = MpesaService()
        try:
            stk_response = mpesa.initiate_stk_push(
                phone_number=phone,
                amount=float(amount),
                account_reference=reference,
                transaction_desc=f"Gas token purchase {meter.meter_number}",
            )
            payment.checkout_request_id = stk_response.get("CheckoutRequestID", "")
            payment.merchant_request_id = stk_response.get("MerchantRequestID", "")
            payment.status = Payment.Status.PENDING
            payment.save(update_fields=["checkout_request_id", "merchant_request_id", "status", "updated_at"])

            log_audit(
                user=user,
                action="PAYMENT_INITIATED",
                resource_type="Transaction",
                resource_id=str(txn.id),
                details={"reference": reference, "amount": str(amount)},
            )
        except Exception as exc:
            logger.exception("STK Push failed for %s", reference)
            txn.status = Transaction.Status.FAILED
            txn.failure_reason = str(exc)
            txn.save(update_fields=["status", "failure_reason", "updated_at"])
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=["status", "updated_at"])
            if isinstance(exc, ValueError):
                raise serializers.ValidationError({"detail": str(exc)})
            raise serializers.ValidationError({"detail": "Failed to initiate M-Pesa payment. Please try again."})

        return txn


class TransactionSerializer(serializers.ModelSerializer):
    meter_number = serializers.CharField(source="meter.meter_number", read_only=True)
    meter_nickname = serializers.CharField(source="meter.nickname", read_only=True)
    token = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = (
            "id",
            "reference",
            "meter_number",
            "meter_nickname",
            "amount",
            "status",
            "phone_number",
            "failure_reason",
            "token",
            "payment_status",
            "created_at",
            "completed_at",
        )

    def get_token(self, obj):
        if hasattr(obj, "electricity_token"):
            return {
                "token": obj.electricity_token.token,
                "units": str(obj.electricity_token.token_units),
                "status": obj.electricity_token.status,
            }
        return None

    def get_payment_status(self, obj):
        if hasattr(obj, "payment"):
            return obj.payment.status
        return None


class ElectricityTokenSerializer(serializers.ModelSerializer):
    transaction_reference = serializers.CharField(source="transaction.reference", read_only=True)

    class Meta:
        model = ElectricityToken
        fields = (
            "id",
            "token",
            "token_units",
            "token_amount",
            "meter_number",
            "stron_receipt_number",
            "status",
            "transaction_reference",
            "generated_at",
            "delivered_at",
        )
