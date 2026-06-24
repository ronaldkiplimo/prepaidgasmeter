import uuid

from django.conf import settings
from django.db import models


class Meter(models.Model):
    """Prepaid gas meter registered on PrepaidGas Kenya."""

    class MeterType(models.TextChoices):
        RESIDENTIAL = "residential", "Residential"
        COMMERCIAL = "commercial", "Commercial"
        INDUSTRIAL = "industrial", "Industrial"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        OFFLINE = "offline", "Offline"
        TAMPERED = "tampered", "Tampered"
        MAINTENANCE = "maintenance", "Maintenance"

    class ValveStatus(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        UNKNOWN = "unknown", "Unknown"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="meters",
    )
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_meters",
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tenant_meters",
    )
    meter_number = models.CharField(max_length=20, db_index=True, unique=True)
    meter_serial = models.CharField(max_length=50, blank=True)
    stron_customer_id = models.CharField(max_length=50, blank=True, db_index=True)
    customer_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    account_number = models.CharField(max_length=30, blank=True)
    nickname = models.CharField(max_length=100, blank=True)
    meter_type = models.CharField(max_length=20, choices=MeterType.choices, default=MeterType.RESIDENTIAL)
    location = models.CharField(max_length=255, blank=True)
    estate = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    valve_status = models.CharField(max_length=20, choices=ValveStatus.choices, default=ValveStatus.UNKNOWN)
    tamper_status = models.BooleanField(default=False)
    current_credit = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    installation_date = models.DateField(null=True, blank=True)
    last_vending_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "meters"
        ordering = ["-is_primary", "-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["landlord", "status"]),
        ]

    def __str__(self):
        label = self.nickname or self.meter_number
        return f"{label} ({self.meter_number})"

    def save(self, *args, **kwargs):
        if self.is_primary:
            Meter.objects.filter(user=self.user, is_primary=True).exclude(pk=self.pk).update(
                is_primary=False
            )
        super().save(*args, **kwargs)


class MeterReading(models.Model):
    """Historical meter consumption readings."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name="readings")
    reading_date = models.DateTimeField(db_index=True)
    units_consumed = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    credit_remaining = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    balance_remaining = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    source = models.CharField(max_length=30, default="stron")
    raw_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "meter_readings"
        ordering = ["-reading_date"]
