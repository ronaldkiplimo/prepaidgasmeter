import uuid

from django.conf import settings
from django.db import models


class Transaction(models.Model):
    """End-to-end token purchase transaction."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAYMENT_INITIATED = "payment_initiated", "Payment Initiated"
        PAYMENT_CONFIRMED = "payment_confirmed", "Payment Confirmed"
        TOKEN_GENERATING = "token_generating", "Token Generating"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    meter = models.ForeignKey(
        "meters.Meter",
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expected_units = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    expected_credit = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    phone_number = models.CharField(max_length=15)
    failure_reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["reference"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.reference} - KES {self.amount} ({self.status})"


class Payment(models.Model):
    """M-Pesa payment record linked to a transaction."""

    class Status(models.TextChoices):
        INITIATED = "initiated", "Initiated"
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"
        TIMEOUT = "timeout", "Timeout"

    class Method(models.TextChoices):
        MPESA_STK = "mpesa_stk", "M-Pesa STK Push"
        MPESA_PAYBILL = "mpesa_paybill", "M-Pesa Paybill"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name="payment",
    )
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.MPESA_STK)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INITIATED,
        db_index=True,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    phone_number = models.CharField(max_length=15)

    # M-Pesa specific fields
    checkout_request_id = models.CharField(max_length=100, blank=True, db_index=True)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, db_index=True)
    mpesa_transaction_date = models.DateTimeField(null=True, blank=True)

    callback_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mpesa_transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.id} - {self.status}"
