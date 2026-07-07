from django.core.management.base import BaseCommand

from apps.core.config_check import integration_status


class Command(BaseCommand):
    help = "Verify M-Pesa and Stron integration configuration"

    def handle(self, *args, **options):
        status = integration_status()

        for name, cfg in (("M-Pesa", status["mpesa"]), ("Stron", status["stron"])):
            if cfg["configured"]:
                self.stdout.write(self.style.SUCCESS(f"{name}: configured"))
            else:
                self.stdout.write(self.style.ERROR(f"{name}: missing {', '.join(cfg['missing'])}"))

        if status["ready_for_purchase"]:
            self.stdout.write(self.style.SUCCESS("Purchase flow: ready"))
        else:
            self.stdout.write(self.style.ERROR("Purchase flow: NOT ready — update backend/.env and restart containers"))
