import uuid

from django.db import models


class ElectricityToken(models.Model):
    """Generated prepaid gas meter token."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        GENERATED = "generated", "Generated"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.OneToOneField(
        "payments.Transaction",
        on_delete=models.CASCADE,
        related_name="electricity_token",
    )
    token = models.CharField(max_length=100)
    token_units = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    token_amount = models.DecimalField(max_digits=12, decimal_places=2)
    meter_number = models.CharField(max_length=20, db_index=True)
    stron_receipt_number = models.CharField(max_length=50, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    stron_response = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "electricity_tokens"
        ordering = ["-generated_at"]

    def __str__(self):
        return f"Token for {self.meter_number} - {self.token_units} units"
