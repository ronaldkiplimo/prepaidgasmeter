import logging
from datetime import timedelta

from django.db import transaction as db_transaction
from django.db.models import Count, Sum
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.audit.services import log_audit
from apps.core.permissions import IsAdminRole
from apps.meters.models import Meter
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
TOKEN_GENERATION_REQUEUE_AFTER = timedelta(seconds=60)


def schedule_token_generation(transaction_id: str) -> None:
    """Queue token generation only after payment state is committed."""

    db_transaction.on_commit(lambda: generate_token_task.delay(transaction_id))


def queue_token_generation_if_missing(txn: Transaction, *, force: bool = False) -> bool:
    if hasattr(txn, "gas_token"):
        return False
    if txn.status not in (Transaction.Status.PAYMENT_CONFIRMED, Transaction.Status.TOKEN_GENERATING):
        return False

    metadata = dict(txn.metadata or {})
    queued_at_value = metadata.get("token_generation_queued_at")
    queued_at = parse_datetime(queued_at_value) if queued_at_value else None
    if queued_at and timezone.is_naive(queued_at):
        queued_at = timezone.make_aware(queued_at)
    if (
        queued_at
        and timezone.now() - queued_at < TOKEN_GENERATION_REQUEUE_AFTER
        and (not force or txn.status == Transaction.Status.TOKEN_GENERATING)
    ):
        return False

    metadata["token_generation_queued_at"] = timezone.now().isoformat()
    txn.metadata = metadata

    update_fields = ["metadata", "updated_at"]
    if txn.status == Transaction.Status.PAYMENT_CONFIRMED:
        txn.status = Transaction.Status.TOKEN_GENERATING
        update_fields.append("status")

    txn.save(update_fields=update_fields)
    schedule_token_generation(str(txn.id))
    return True


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
        return qs.filter(user=user)

    @extend_schema(tags=["Transactions"], summary="List transactions")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "reference"

    def get_queryset(self):
        user = self.request.user
        qs = Transaction.objects.select_related("meter", "payment").prefetch_related("gas_token")
        if user.role == "admin" or user.is_superuser:
            return qs
        return qs.filter(user=user)


class RetryTokenGenerationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Transactions"], summary="Retry token generation for a confirmed payment")
    def post(self, request, reference):
        user = request.user
        qs = Transaction.objects.select_related("meter", "payment").prefetch_related("gas_token")
        if not (user.role == "admin" or user.is_superuser):
            qs = qs.filter(user=user)

        try:
            txn = qs.get(reference=reference)
        except Transaction.DoesNotExist:
            return Response({"detail": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)

        queued = queue_token_generation_if_missing(txn, force=True)
        if queued:
            txn.refresh_from_db()
        return Response({**TransactionSerializer(txn).data, "token_generation_queued": queued})


class ReconcilePaymentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Transactions"], summary="Check M-Pesa status and continue token generation")
    def post(self, request, reference):
        user = request.user
        qs = Transaction.objects.select_related("meter", "payment").prefetch_related("gas_token")
        if not (user.role == "admin" or user.is_superuser):
            qs = qs.filter(user=user)

        try:
            txn = qs.get(reference=reference)
        except Transaction.DoesNotExist:
            return Response({"detail": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)

        if txn.status in (Transaction.Status.COMPLETED, Transaction.Status.TOKEN_GENERATING):
            return Response({**TransactionSerializer(txn).data, "payment_reconciled": False})

        if not hasattr(txn, "payment") or not txn.payment.checkout_request_id:
            return Response(
                {"detail": "This transaction does not have an M-Pesa checkout request to check."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            mpesa_result = MpesaService().query_stk_push_status(txn.payment.checkout_request_id)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        result_code = str(mpesa_result.get("ResultCode", "")).strip()
        result_desc = mpesa_result.get("ResultDesc", "")
        metadata = dict(txn.metadata or {})
        metadata["mpesa_stk_query"] = mpesa_result

        if result_code != "0":
            txn.metadata = metadata
            txn.save(update_fields=["metadata", "updated_at"])
            return Response(
                {
                    **TransactionSerializer(txn).data,
                    "payment_reconciled": False,
                    "mpesa_result": mpesa_result,
                    "detail": result_desc or "M-Pesa has not confirmed this payment yet.",
                }
            )

        with db_transaction.atomic():
            payment = txn.payment
            payment.status = Payment.Status.SUCCESS
            payment.callback_payload = {
                **(payment.callback_payload or {}),
                "stk_query": mpesa_result,
            }
            payment.save(update_fields=["status", "callback_payload", "updated_at"])

            txn.status = Transaction.Status.PAYMENT_CONFIRMED
            txn.failure_reason = ""
            txn.metadata = metadata
            txn.save(update_fields=["status", "failure_reason", "metadata", "updated_at"])

            log_audit(
                user=txn.user,
                action="PAYMENT_RECONCILED",
                resource_type="Transaction",
                resource_id=str(txn.id),
                details={"reference": txn.reference, "mpesa_result": mpesa_result},
            )
            queue_token_generation_if_missing(txn, force=True)

        txn.refresh_from_db()
        return Response(
            {
                **TransactionSerializer(txn).data,
                "payment_reconciled": True,
                "mpesa_result": mpesa_result,
            }
        )


class MeterLookupView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Meters"], summary="Query Stron meter info and credit")
    def get(self, request, meter_number):
        normalized_meter_number = meter_number.strip().upper()
        user = request.user
        meter_qs = Meter.objects.filter(meter_number=normalized_meter_number, is_active=True)
        if not (user.role == "admin" or user.is_superuser):
            meter_qs = meter_qs.filter(user=user)
        meter = meter_qs.first()
        if not meter:
            return Response({"detail": "Meter not found."}, status=status.HTTP_404_NOT_FOUND)

        stron = StronVendingService()
        try:
            info = stron.query_meter_info(meter.meter_number)
            credit = stron.query_meter_credit(meter.meter_number)
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
            txn = payment.transaction
            queue_token_generation_if_missing(txn)
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
                    details={"mpesa_receipt": parsed["mpesa_receipt_number"], "amount": str(txn.amount)},
                )
                queue_token_generation_if_missing(txn, force=True)
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
