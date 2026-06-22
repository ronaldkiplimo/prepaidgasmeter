import logging

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.audit.services import log_audit
from apps.core.permissions import IsAdminRole
from apps.payments.models import Payment, Transaction
from apps.payments.serializers import (
    GasTokenSerializer,
    PurchaseTokenSerializer,
    TransactionSerializer,
    VendingPreviewSerializer,
)
from apps.payments.services.mpesa import MpesaService
from apps.tokens.services.stron import StronAPIError, StronVendingService
from apps.tokens.tasks import generate_token_task

logger = logging.getLogger(__name__)


class VendingPreviewView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Purchase"], summary="Preview gas units before M-Pesa payment")
    def post(self, request):
        serializer = VendingPreviewSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())


class PurchaseTokenView(generics.CreateAPIView):
    serializer_class = PurchaseTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Purchase"], summary="Buy gas credit via M-Pesa STK Push")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        txn = serializer.save()
        return Response(TransactionSerializer(txn).data, status=status.HTTP_201_CREATED)


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status"]
    search_fields = ["reference", "meter__meter_number"]

    def get_queryset(self):
        user = self.request.user
        qs = Transaction.objects.select_related("meter", "payment").prefetch_related("gas_token")
        if user.role in ("admin",) or user.is_superuser:
            return qs
        if user.role == "landlord":
            return qs.filter(meter__landlord=user)
        if user.role == "distributor":
            return qs.all()
        return qs.filter(user=user)

    @extend_schema(tags=["Transactions"], summary="List transactions")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "reference"

    def get_queryset(self):
        return Transaction.objects.select_related("meter", "payment").prefetch_related("gas_token")


class MeterLookupView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Meters"], summary="Query Stron meter info and credit")
    def get(self, request, meter_number):
        stron = StronVendingService()
        try:
            info = stron.query_meter_info(meter_number)
            credit = stron.query_meter_credit(meter_number)
            return Response({"meter_info": info, "credit_records": credit})
        except StronAPIError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class MpesaCallbackView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(tags=["Payments"], summary="M-Pesa STK Push callback webhook")
    def post(self, request):
        payload = request.data
        logger.info("M-Pesa callback received")

        if not MpesaService.verify_callback(payload):
            return Response({"ResultCode": 1, "ResultDesc": "Invalid payload"})

        parsed = MpesaService.parse_callback(payload)
        checkout_id = parsed["checkout_request_id"]

        try:
            payment = Payment.objects.select_related("transaction").get(checkout_request_id=checkout_id)
        except Payment.DoesNotExist:
            logger.error("Payment not found for checkout ID: %s", checkout_id)
            return Response({"ResultCode": 0, "ResultDesc": "Accepted"})

        if payment.status == Payment.Status.SUCCESS:
            return Response({"ResultCode": 0, "ResultDesc": "Already processed"})

        from django.db import transaction as db_transaction

        with db_transaction.atomic():
            payment.callback_payload = payload
            payment.save(update_fields=["callback_payload", "updated_at"])
            txn = payment.transaction

            if parsed["success"]:
                payment.status = Payment.Status.SUCCESS
                payment.mpesa_receipt_number = parsed["mpesa_receipt_number"]
                if parsed["transaction_date"]:
                    payment.mpesa_transaction_date = timezone.make_aware(parsed["transaction_date"])
                payment.save()

                txn.status = Transaction.Status.PAYMENT_CONFIRMED
                txn.save(update_fields=["status", "updated_at"])

                log_audit(
                    user=txn.user,
                    action="PAYMENT_CONFIRMED",
                    resource_type="Transaction",
                    resource_id=str(txn.id),
                    details={"mpesa_receipt": parsed["mpesa_receipt_number"], "amount": str(txn.amount)},
                )
                generate_token_task.delay(str(txn.id))
            else:
                payment.status = Payment.Status.FAILED
                payment.save(update_fields=["status", "updated_at"])
                txn.status = Transaction.Status.FAILED
                txn.failure_reason = parsed["result_desc"]
                txn.save(update_fields=["status", "failure_reason", "updated_at"])
                log_audit(
                    user=txn.user,
                    action="PAYMENT_FAILED",
                    resource_type="Transaction",
                    resource_id=str(txn.id),
                    details={"reason": parsed["result_desc"]},
                )

        return Response({"ResultCode": 0, "ResultDesc": "Accepted"})


class AdminTransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAdminRole]
    queryset = Transaction.objects.select_related("user", "meter", "payment").prefetch_related("gas_token")
    filterset_fields = ["status"]
    search_fields = ["reference", "user__phone_number", "meter__meter_number"]
