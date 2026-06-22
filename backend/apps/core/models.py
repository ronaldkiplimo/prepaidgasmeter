import uuid

from django.conf import settings
from django.db import models


class Tariff(models.Model):
    """Gas pricing tariff configuration."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=4)
    unit_label = models.CharField(max_length=20, default="m³")
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=16)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tariffs"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - KES {self.price_per_unit}/{self.unit_label}"


class SystemSetting(models.Model):
    """Key-value system configuration store."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.JSONField(default=dict)
    description = models.TextField(blank=True)
    is_encrypted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_settings"

    def __str__(self):
        return self.key
