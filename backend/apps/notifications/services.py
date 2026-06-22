import logging

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Notification, SMSLog, EmailLog

logger = logging.getLogger(__name__)


class NotificationService:
    """SMS (Africa's Talking / Twilio) and Email (SendGrid / SMTP) notifications."""

    @staticmethod
    def send_sms(phone_number: str, message: str, user=None, notification_type="general") -> bool:
        log = SMSLog.objects.create(
            user=user,
            phone_number=phone_number,
            message=message,
            provider=settings.SMS_PROVIDER,
            notification_type=notification_type,
        )
        success = False
        try:
            if settings.SMS_PROVIDER == "africas_talking" and settings.AFRICAS_TALKING_API_KEY:
                resp = requests.post(
                    "https://api.africastalking.com/version1/messaging",
                    headers={"apiKey": settings.AFRICAS_TALKING_API_KEY},
                    data={
                        "username": settings.AFRICAS_TALKING_USERNAME,
                        "to": phone_number,
                        "message": message,
                        "from": settings.SMS_SENDER_ID,
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                success = True
            elif settings.SMS_PROVIDER == "twilio" and settings.TWILIO_ACCOUNT_SID:
                from urllib.parse import urlencode
                auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                resp = requests.post(
                    f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json",
                    auth=auth,
                    data={"To": phone_number, "From": settings.TWILIO_PHONE_NUMBER, "Body": message},
                    timeout=30,
                )
                resp.raise_for_status()
                success = True
            elif settings.SMS_API_URL:
                resp = requests.post(
                    settings.SMS_API_URL,
                    json={"api_key": settings.SMS_API_KEY, "sender_id": settings.SMS_SENDER_ID,
                          "phone": phone_number, "message": message},
                    timeout=30,
                )
                resp.raise_for_status()
                success = True
            else:
                logger.info("SMS (dev) -> %s: %s", phone_number, message)
                success = True
        except Exception as exc:
            log.error_message = str(exc)
            logger.exception("SMS failed to %s", phone_number)

        log.status = SMSLog.Status.SENT if success else SMSLog.Status.FAILED
        log.sent_at = timezone.now() if success else None
        log.save()
        return success

    @staticmethod
    def send_email(to_email: str, subject: str, message: str, user=None, notification_type="general") -> bool:
        log = EmailLog.objects.create(
            user=user,
            email=to_email,
            subject=subject,
            message=message,
            provider=settings.EMAIL_PROVIDER,
            notification_type=notification_type,
        )
        success = False
        try:
            if settings.EMAIL_PROVIDER == "sendgrid" and settings.SENDGRID_API_KEY:
                resp = requests.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={"Authorization": f"Bearer {settings.SENDGRID_API_KEY}"},
                    json={
                        "personalizations": [{"to": [{"email": to_email}]}],
                        "from": {"email": settings.DEFAULT_FROM_EMAIL},
                        "subject": subject,
                        "content": [{"type": "text/plain", "value": message}],
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                success = True
            else:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)
                success = True
        except Exception as exc:
            log.error_message = str(exc)
            logger.exception("Email failed to %s", to_email)

        log.status = EmailLog.Status.SENT if success else EmailLog.Status.FAILED
        log.sent_at = timezone.now() if success else None
        log.save()
        return success

    @classmethod
    def notify_token_delivery(cls, user, token_obj, transaction) -> None:
        sms_message = (
            f"PrepaidGas Kenya\n"
            f"Meter: {token_obj.meter_number}\n"
            f"Token: {token_obj.token}\n"
            f"Units: {token_obj.token_units}\n"
            f"Amount: KES {token_obj.token_amount}\n"
            f"Ref: {transaction.reference}"
        )
        email_subject = f"Gas Token Receipt - {transaction.reference}"
        email_message = (
            f"Dear {user.display_name},\n\n"
            f"Your gas credit purchase was successful.\n\n"
            f"Meter: {token_obj.meter_number}\n"
            f"Token: {token_obj.token}\n"
            f"Units: {token_obj.token_units}\n"
            f"Amount: KES {token_obj.token_amount}\n"
            f"Ref: {transaction.reference}\n\n"
            f"Enter the token on your meter to load gas credit.\n\n"
            f"PrepaidGas Kenya"
        )

        cls.send_sms(user.phone_number, sms_message, user=user, notification_type="token_delivery")
        Notification.objects.create(
            user=user, channel=Notification.Channel.SMS,
            notification_type=Notification.Type.TOKEN_DELIVERY,
            recipient=user.phone_number, message=sms_message, status=Notification.Status.SENT,
            transaction=transaction, sent_at=timezone.now(),
        )
        if user.email:
            cls.send_email(user.email, email_subject, email_message, user=user, notification_type="token_delivery")
            Notification.objects.create(
                user=user, channel=Notification.Channel.EMAIL,
                notification_type=Notification.Type.TOKEN_DELIVERY,
                recipient=user.email, subject=email_subject, message=email_message,
                status=Notification.Status.SENT, transaction=transaction, sent_at=timezone.now(),
            )
