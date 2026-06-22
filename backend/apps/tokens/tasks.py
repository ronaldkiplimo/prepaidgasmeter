import logging

from celery import shared_task
from django.db import transaction as db_transaction
from django.utils import timezone

from apps.audit.services import log_audit
from apps.meters.models import Meter
from apps.notifications.tasks import send_token_notification_task
from apps.payments.models import Transaction
from apps.tokens.models import GasToken
from apps.tokens.services.stron import StronAPIError, StronVendingService
from apps.tokens.services.stron_logger import log_stron_call

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def generate_token_task(self, transaction_id: str):
    """Vend gas credit via Stron VendingMeterPurchase after M-Pesa confirmation."""
    try:
        txn = Transaction.objects.select_related("meter", "user").get(id=transaction_id)
    except Transaction.DoesNotExist:
        logger.error("Transaction %s not found", transaction_id)
        return

    if txn.status not in (Transaction.Status.PAYMENT_CONFIRMED, Transaction.Status.TOKEN_GENERATING):
        logger.warning("Transaction %s invalid state: %s", transaction_id, txn.status)
        return

    txn.status = Transaction.Status.TOKEN_GENERATING
    txn.save(update_fields=["status", "updated_at"])

    stron = StronVendingService()
    try:
        result = stron.vending_purchase(
            meter_id=txn.meter.meter_number,
            amount=float(txn.amount),
            transaction_reference=txn.reference,
        )

        log_stron_call(
            action="vending_purchase",
            meter_number=txn.meter.meter_number,
            request_payload={"MeterID": txn.meter.meter_number, "Amount": str(txn.amount)},
            response_payload=result.get("raw_response", result),
            transaction=txn,
            user_id=str(txn.user_id),
        )

        with db_transaction.atomic():
            token_obj, _ = GasToken.objects.update_or_create(
                transaction=txn,
                defaults={
                    "token": result["token"],
                    "token_units": result["token_units"],
                    "token_amount": result["token_amount"],
                    "meter_number": txn.meter.meter_number,
                    "stron_receipt_number": result.get("receipt_number", ""),
                    "status": GasToken.Status.GENERATED,
                    "stron_response": result.get("raw_response", {}),
                },
            )

            Meter.objects.filter(pk=txn.meter_id).update(
                last_vending_date=timezone.now(),
                current_credit=result["token_units"],
            )

            txn.status = Transaction.Status.COMPLETED
            txn.completed_at = timezone.now()
            txn.save(update_fields=["status", "completed_at", "updated_at"])

        log_audit(
            user=txn.user,
            action="TOKEN_GENERATED",
            resource_type="GasToken",
            resource_id=str(token_obj.id),
            details={"reference": txn.reference, "units": str(token_obj.token_units)},
        )

        send_token_notification_task.delay(str(token_obj.id))

    except (StronAPIError, Exception) as exc:
        logger.exception("Token generation failed for %s", transaction_id)
        txn.status = Transaction.Status.FAILED
        txn.failure_reason = f"Vending failed: {exc}"
        txn.save(update_fields=["status", "failure_reason", "updated_at"])
        log_stron_call(
            action="vending_purchase",
            meter_number=txn.meter.meter_number,
            request_payload={"MeterID": txn.meter.meter_number},
            error_message=str(exc),
            transaction=txn,
            user_id=str(txn.user_id),
            success=False,
        )
        raise self.retry(exc=exc)
