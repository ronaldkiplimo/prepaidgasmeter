from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.core.models import Tariff, SystemSetting
from apps.meters.models import Meter

User = get_user_model()


class Command(BaseCommand):
    help = "Seed PrepaidGas Kenya with demo data"

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            phone_number="254700000001",
            defaults={
                "username": "admin",
                "email": "admin@prepaidgas.co.ke",
                "first_name": "System",
                "last_name": "Admin",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("Admin@12345")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created admin: 254700000001 / Admin@12345"))

        customer, created = User.objects.get_or_create(
            phone_number="254712345678",
            defaults={
                "username": "demo_customer",
                "email": "customer@example.com",
                "first_name": "Demo",
                "last_name": "Customer",
                "role": User.Role.CUSTOMER,
            },
        )
        if created:
            customer.set_password("Demo@12345")
            customer.save()
            self.stdout.write(self.style.SUCCESS("Created customer: 254712345678 / Demo@12345"))

        Tariff.objects.get_or_create(
            name="Standard Residential",
            defaults={"price_per_unit": 120, "unit_label": "m³", "vat_rate": 16, "service_fee": 0},
        )

        SystemSetting.objects.get_or_create(
            key="mpesa_config",
            defaults={"value": {"env": "sandbox"}, "description": "M-Pesa Daraja configuration"},
        )
        SystemSetting.objects.get_or_create(
            key="stron_config",
            defaults={
                "value": {"base_url": "http://www.server-newv.stronpower.com/api"},
                "description": "Stron Power API configuration",
            },
        )

        self.stdout.write(self.style.SUCCESS("Seed data complete."))
