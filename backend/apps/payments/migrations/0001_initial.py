import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("meters", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("reference", models.CharField(db_index=True, max_length=50, unique=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("payment_initiated", "Payment Initiated"),
                            ("payment_confirmed", "Payment Confirmed"),
                            ("token_generating", "Token Generating"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                            ("refunded", "Refunded"),
                        ],
                        db_index=True,
                        default="pending",
                        max_length=30,
                    ),
                ),
                ("phone_number", models.CharField(max_length=15)),
                ("failure_reason", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "meter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transactions",
                        to="meters.meter",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "transactions",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "method",
                    models.CharField(
                        choices=[
                            ("mpesa_stk", "M-Pesa STK Push"),
                            ("mpesa_paybill", "M-Pesa Paybill"),
                        ],
                        default="mpesa_stk",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("initiated", "Initiated"),
                            ("pending", "Pending"),
                            ("success", "Success"),
                            ("failed", "Failed"),
                            ("cancelled", "Cancelled"),
                            ("timeout", "Timeout"),
                        ],
                        db_index=True,
                        default="initiated",
                        max_length=20,
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("phone_number", models.CharField(max_length=15)),
                ("checkout_request_id", models.CharField(blank=True, db_index=True, max_length=100)),
                ("merchant_request_id", models.CharField(blank=True, max_length=100)),
                ("mpesa_receipt_number", models.CharField(blank=True, db_index=True, max_length=50)),
                ("mpesa_transaction_date", models.DateTimeField(blank=True, null=True)),
                ("callback_payload", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "transaction",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment",
                        to="payments.transaction",
                    ),
                ),
            ],
            options={
                "db_table": "payments",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="transaction",
            index=models.Index(fields=["user", "status"], name="transaction_user_status_idx"),
        ),
        migrations.AddIndex(
            model_name="transaction",
            index=models.Index(fields=["reference"], name="transaction_reference_idx"),
        ),
        migrations.AddIndex(
            model_name="transaction",
            index=models.Index(fields=["created_at"], name="transaction_created_idx"),
        ),
    ]
