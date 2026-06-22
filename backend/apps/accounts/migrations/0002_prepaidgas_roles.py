import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(model_name="user", name="role", field=models.CharField(
            choices=[("customer", "Customer"), ("landlord", "Landlord"),
                     ("distributor", "Gas Distributor"), ("admin", "Administrator")],
            db_index=True, default="customer", max_length=20)),
        migrations.AddField(model_name="user", name="email_verified", field=models.BooleanField(default=False)),
        migrations.AddField(model_name="user", name="mfa_enabled", field=models.BooleanField(default=False)),
        migrations.AddField(model_name="user", name="mfa_secret", field=models.CharField(blank=True, max_length=64)),
        migrations.CreateModel(
            name="CustomerProfile",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("stron_customer_id", models.CharField(blank=True, db_index=True, max_length=50)),
                ("address", models.CharField(blank=True, max_length=255)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("estate", models.CharField(blank=True, max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                 related_name="customer_profile", to="accounts.user")),
            ],
            options={"db_table": "customers"},
        ),
    ]
