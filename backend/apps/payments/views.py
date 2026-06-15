import logging

from django.db import transaction as db_transaction
from django.utils import timezone
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.audit.services import log_audit
from apps.payments.models import Payment, Transaction
from apps.payments.serializers import PurchaseTokenSerializer, TransactionSerializer
from apps.payments.services.mpesa import MpesaService
from apps.tokens.tasks import generate_token_task

logger = logging.getLogger(__name__)


class PurchaseTokenView(generics.CreateAPIView):
    serializer_class = PurchaseTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Tokens"], summary="Purchase electricity token via M-Pesa STK Push")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        txn = serializer.save()
        return Response(
            TransactionSerializer(txn).data,
            status=status.HTTP_201_CREATED,
        )


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status"]
    search_fields = ["reference", "meter__meter_number"]

    def get_queryset(self):
        return (
            Transaction.objects.filter(user=self.request.user)
            .select_related("meter", "payment")
            .prefetch_related("electricity_token")
        )

    @extend_schema(tags=["Transactions"], summary="List user transactions")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "reference"

    def get_queryset(self):
        return (
            Transaction.objects.filter(user=self.request.user)
            .select_related("meter", "payment")
            .prefetch_related("electricity_token")
        )

    @extend_schema(tags=["Transactions"], summary="Get transaction details")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MpesaCallbackView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(tags=["Payments"], summary="M-Pesa STK Push callback webhook")
    def post(self, request):
        payload = request.data
        logger.info("M-Pesa callback received: %s", payload)

        if not MpesaService.verify_callback(payload):
            logger.warning("Invalid M-Pesa callback payload")
            return Response({"ResultCode": 1, "ResultDesc": "Invalid payload"})

        parsed = MpesaService.parse_callback(payload)
        checkout_id = parsed["checkout_request_id"]

        try:
            payment = Payment.objects.select_related("transaction").get(
                checkout_request_id=checkout_id
            )
        except Payment.DoesNotExist:
            logger.error("Payment not found for checkout ID: %s", checkout_id)
            return Response({"ResultCode": 0, "ResultDesc": "Accepted"})

        if payment.status == Payment.Status.SUCCESS:
            return Response({"ResultCode": 0, "ResultDesc": "Already processed"})

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
                    details={
                        "mpesa_receipt": parsed["mpesa_receipt_number"],
                        "amount": str(txn.amount),
                    },
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
    permission_classes = [permissions.IsAdminUser]
    queryset = Transaction.objects.select_related("user", "meter", "payment").prefetch_related(
        "electricity_token"
    )
    filterset_fields = ["status"]
    search_fields = ["reference", "user__phone_number", "meter__meter_number"]

    @extend_schema(tags=["Admin"], summary="Admin: list all transactions")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
