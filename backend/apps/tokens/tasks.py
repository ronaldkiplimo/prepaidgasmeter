import logging

from celery import shared_task
from django.db import transaction as db_transaction
from django.utils import timezone

from apps.audit.services import log_audit
from apps.notifications.tasks import send_token_notification_task
from apps.payments.models import Transaction
from apps.tokens.models import ElectricityToken
from apps.tokens.services.stron import StronVendingService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def generate_token_task(self, transaction_id: str):
    """Generate electricity token via Stron API after payment confirmation."""
    try:
        txn = Transaction.objects.select_related("meter", "user").get(id=transaction_id)
    except Transaction.DoesNotExist:
        logger.error("Transaction %s not found for token generation", transaction_id)
        return

    if txn.status not in (
        Transaction.Status.PAYMENT_CONFIRMED,
        Transaction.Status.TOKEN_GENERATING,
    ):
        logger.warning("Transaction %s in invalid state: %s", transaction_id, txn.status)
        return

    txn.status = Transaction.Status.TOKEN_GENERATING
    txn.save(update_fields=["status", "updated_at"])

    stron = StronVendingService()
    try:
        result = stron.generate_token(
            meter_number=txn.meter.meter_number,
            amount=float(txn.amount),
            transaction_reference=txn.reference,
            phone_number=txn.phone_number,
        )

        with db_transaction.atomic():
            token_obj, _ = ElectricityToken.objects.update_or_create(
                transaction=txn,
                defaults={
                    "token": result["token"],
                    "token_units": result["token_units"],
                    "token_amount": result["token_amount"],
                    "meter_number": txn.meter.meter_number,
                    "stron_receipt_number": result.get("receipt_number", ""),
                    "status": ElectricityToken.Status.GENERATED,
                    "stron_response": result.get("raw_response", {}),
                },
            )

            txn.status = Transaction.Status.COMPLETED
            txn.completed_at = timezone.now()
            txn.save(update_fields=["status", "completed_at", "updated_at"])

        log_audit(
            user=txn.user,
            action="TOKEN_GENERATED",
            resource_type="ElectricityToken",
            resource_id=str(token_obj.id),
            details={
                "reference": txn.reference,
                "units": str(token_obj.token_units),
            },
        )

        send_token_notification_task.delay(str(token_obj.id))

    except Exception as exc:
        logger.exception("Token generation failed for %s", transaction_id)
        txn.status = Transaction.Status.FAILED
        txn.failure_reason = f"Token generation failed: {exc}"
        txn.save(update_fields=["status", "failure_reason", "updated_at"])

        log_audit(
            user=txn.user,
            action="TOKEN_GENERATION_FAILED",
            resource_type="Transaction",
            resource_id=str(txn.id),
            details={"error": str(exc)},
        )

        raise self.retry(exc=exc)
