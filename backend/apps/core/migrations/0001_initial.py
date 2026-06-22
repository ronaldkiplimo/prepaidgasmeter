import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tariff",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("price_per_unit", models.DecimalField(decimal_places=4, max_digits=10)),
                ("unit_label", models.CharField(default="m³", max_length=20)),
                ("vat_rate", models.DecimalField(decimal_places=2, default=16, max_digits=5)),
                ("service_fee", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "tariffs", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="SystemSetting",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("key", models.CharField(db_index=True, max_length=100, unique=True)),
                ("value", models.JSONField(default=dict)),
                ("description", models.TextField(blank=True)),
                ("is_encrypted", models.BooleanField(default=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "system_settings"},
        ),
    ]
