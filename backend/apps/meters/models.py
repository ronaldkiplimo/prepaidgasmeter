import uuid

from django.conf import settings
from django.db import models


class Meter(models.Model):
    """Customer electricity meter registered on the platform."""

    class MeterType(models.TextChoices):
        SINGLE_PHASE = "single_phase", "Single Phase"
        THREE_PHASE = "three_phase", "Three Phase"
        PREPAID = "prepaid", "Prepaid"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="meters",
    )
    meter_number = models.CharField(max_length=20, db_index=True)
    account_number = models.CharField(max_length=30, blank=True)
    nickname = models.CharField(max_length=100, blank=True)
    meter_type = models.CharField(
        max_length=20,
        choices=MeterType.choices,
        default=MeterType.PREPAID,
    )
    utility_provider = models.CharField(max_length=100, default="Kenya Power")
    location = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "meters"
        ordering = ["-is_primary", "-created_at"]
        unique_together = [("user", "meter_number")]
        indexes = [
            models.Index(fields=["meter_number"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        label = self.nickname or self.meter_number
        return f"{label} ({self.user.phone_number})"

    def save(self, *args, **kwargs):
        if self.is_primary:
            Meter.objects.filter(user=self.user, is_primary=True).exclude(pk=self.pk).update(
                is_primary=False
            )
        super().save(*args, **kwargs)
