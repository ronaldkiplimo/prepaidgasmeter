import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ElectricityToken",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("token", models.CharField(max_length=100)),
                ("token_units", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("token_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("meter_number", models.CharField(db_index=True, max_length=20)),
                ("stron_receipt_number", models.CharField(blank=True, max_length=50)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("generated", "Generated"),
                            ("delivered", "Delivered"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("stron_response", models.JSONField(blank=True, default=dict)),
                ("generated_at", models.DateTimeField(auto_now_add=True)),
                ("delivered_at", models.DateTimeField(blank=True, null=True)),
                (
                    "transaction",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="electricity_token",
                        to="payments.transaction",
                    ),
                ),
            ],
            options={
                "db_table": "electricity_tokens",
                "ordering": ["-generated_at"],
            },
        ),
    ]
