import logging

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """Send SMS and email notifications."""

    @staticmethod
    def send_sms(phone_number: str, message: str) -> bool:
        if not settings.SMS_API_URL or not settings.SMS_API_KEY:
            logger.info("SMS (dev mode) to %s: %s", phone_number, message)
            return True

        try:
            response = requests.post(
                settings.SMS_API_URL,
                json={
                    "api_key": settings.SMS_API_KEY,
                    "sender_id": settings.SMS_SENDER_ID,
                    "phone": phone_number,
                    "message": message,
                },
                timeout=30,
            )
            response.raise_for_status()
            return True
        except Exception:
            logger.exception("SMS send failed to %s", phone_number)
            return False

    @staticmethod
    def send_email(to_email: str, subject: str, message: str) -> bool:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            return True
        except Exception:
            logger.exception("Email send failed to %s", to_email)
            return False

    @classmethod
    def notify_token_delivery(cls, user, token_obj, transaction) -> None:
        """Send token via SMS and email."""
        sms_message = (
            f"Your prepaid gas token for meter {token_obj.meter_number}:\n"
            f"Token: {token_obj.token}\n"
            f"Units: {token_obj.token_units}\n"
            f"Amount: KES {token_obj.token_amount}\n"
            f"Ref: {transaction.reference}"
        )
        email_subject = f"Gas Meter Token - {transaction.reference}"
        email_message = (
            f"Dear {user.display_name},\n\n"
            f"Your gas token purchase was successful.\n\n"
            f"Meter Number: {token_obj.meter_number}\n"
            f"Token: {token_obj.token}\n"
            f"Units: {token_obj.token_units}\n"
            f"Amount Paid: KES {token_obj.token_amount}\n"
            f"M-Pesa Ref: {transaction.payment.mpesa_receipt_number if hasattr(transaction, 'payment') else 'N/A'}\n"
            f"Transaction Ref: {transaction.reference}\n\n"
            f"Enter the token on your meter to load units.\n\n"
            f"Thank you for using Prepaid Gas Meter."
        )

        cls._create_and_send(
            user=user,
            channel=Notification.Channel.SMS,
            notification_type=Notification.Type.TOKEN_DELIVERY,
            recipient=user.phone_number,
            message=sms_message,
            transaction=transaction,
        )

        if user.email:
            cls._create_and_send(
                user=user,
                channel=Notification.Channel.EMAIL,
                notification_type=Notification.Type.TOKEN_DELIVERY,
                recipient=user.email,
                subject=email_subject,
                message=email_message,
                transaction=transaction,
            )

    @classmethod
    def _create_and_send(
        cls,
        user,
        channel,
        notification_type,
        recipient,
        message,
        subject="",
        transaction=None,
    ):
        notification = Notification.objects.create(
            user=user,
            channel=channel,
            notification_type=notification_type,
            recipient=recipient,
            subject=subject,
            message=message,
            transaction=transaction,
        )

        success = False
        if channel == Notification.Channel.SMS:
            success = cls.send_sms(recipient, message)
        elif channel == Notification.Channel.EMAIL:
            success = cls.send_email(recipient, subject, message)

        notification.status = Notification.Status.SENT if success else Notification.Status.FAILED
        if success:
            notification.sent_at = timezone.now()
        notification.save(update_fields=["status", "sent_at"])

        return notification
