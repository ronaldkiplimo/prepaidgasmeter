import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Meter",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("meter_number", models.CharField(db_index=True, max_length=20)),
                ("account_number", models.CharField(blank=True, max_length=30)),
                ("nickname", models.CharField(blank=True, max_length=100)),
                (
                    "meter_type",
                    models.CharField(
                        choices=[
                            ("single_phase", "Single Phase"),
                            ("three_phase", "Three Phase"),
                            ("prepaid", "Prepaid"),
                        ],
                        default="prepaid",
                        max_length=20,
                    ),
                ),
                ("utility_provider", models.CharField(default="Kenya Power", max_length=100)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("is_primary", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="meters",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "meters",
                "ordering": ["-is_primary", "-created_at"],
                "unique_together": {("user", "meter_number")},
            },
        ),
        migrations.AddIndex(
            model_name="meter",
            index=models.Index(fields=["meter_number"], name="meters_meter_n_abc123_idx"),
        ),
        migrations.AddIndex(
            model_name="meter",
            index=models.Index(fields=["user", "is_active"], name="meters_user_id_def456_idx"),
        ),
    ]
