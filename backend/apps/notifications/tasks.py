import logging

from celery import shared_task
from django.utils import timezone

from apps.tokens.models import ElectricityToken
from .services import NotificationService

logger = logging.getLogger(__name__)


@shared_task
def send_token_notification_task(token_id: str):
    """Send SMS and email with generated token."""
    try:
        token_obj = ElectricityToken.objects.select_related(
            "transaction", "transaction__user", "transaction__payment"
        ).get(id=token_id)
    except ElectricityToken.DoesNotExist:
        logger.error("Token %s not found for notification", token_id)
        return

    txn = token_obj.transaction
    user = txn.user

    NotificationService.notify_token_delivery(user, token_obj, txn)

    token_obj.status = ElectricityToken.Status.DELIVERED
    token_obj.delivered_at = timezone.now()
    token_obj.save(update_fields=["status", "delivered_at"])
