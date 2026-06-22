import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Platform user with role-based access."""

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        LANDLORD = "landlord", "Landlord"
        DISTRIBUTOR = "distributor", "Gas Distributor"
        ADMIN = "admin", "Administrator"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, unique=True, db_index=True)
    national_id = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER, db_index=True)
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["username", "email"]

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.phone_number})"

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_landlord(self):
        return self.role == self.Role.LANDLORD

    @property
    def is_distributor(self):
        return self.role == self.Role.DISTRIBUTOR


class CustomerProfile(models.Model):
    """Extended customer profile linked to Stron customer ID."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")
    stron_customer_id = models.CharField(max_length=50, blank=True, db_index=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    estate = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customers"

    def __str__(self):
        return f"Customer {self.user.phone_number}"
