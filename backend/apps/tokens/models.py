import uuid

from django.db import models


class GasToken(models.Model):
    """Generated prepaid gas credit token from Stron Vending API."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        GENERATED = "generated", "Generated"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.OneToOneField(
        "payments.Transaction",
        on_delete=models.CASCADE,
        related_name="gas_token",
    )
    token = models.CharField(max_length=100)
    token_units = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    token_amount = models.DecimalField(max_digits=12, decimal_places=2)
    meter_number = models.CharField(max_length=20, db_index=True)
    stron_receipt_number = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    stron_response = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tokens"
        ordering = ["-generated_at"]

    def __str__(self):
        return f"Token for {self.meter_number} - {self.token_units} units"


# Backward-compatible alias used by existing code paths
ElectricityToken = GasToken


class StronTransaction(models.Model):
    """Audit log of all Stron Power API calls."""

    class Action(models.TextChoices):
        QUERY_CUSTOMER_INFO = "query_customer_info", "Query Customer Info"
        QUERY_METER_INFO = "query_meter_info", "Query Meter Info"
        QUERY_METER_CREDIT = "query_meter_credit", "Query Meter Credit"
        QUERY_CUSTOMER_CREDIT = "query_customer_credit", "Query Customer Credit"
        VENDING_PREVIEW = "vending_preview", "Vending Preview"
        VENDING_PURCHASE = "vending_purchase", "Vending Purchase"
        VENDING_METER = "vending_meter", "Vending Meter"
        CLEAR_CREDIT = "clear_credit", "Clear Credit"
        CLEAR_TAMPER = "clear_tamper", "Clear Tamper"

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(
        "payments.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stron_logs",
    )
    meter_number = models.CharField(max_length=20, db_index=True)
    action = models.CharField(max_length=30, choices=Action.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices)
    request_payload = models.JSONField(default=dict)
    response_payload = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    initiated_by_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "stron_transactions"
        ordering = ["-created_at"]
