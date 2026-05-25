from django.core.management.base import BaseCommand

from apps.certificates.services import CertificateLifecycleJobService


class Command(BaseCommand):
    help = "Process FoodCert NG certificate expiry status and renewal reminders."

    def handle(self, *args, **options):
        result = CertificateLifecycleJobService.process_expiry_and_reminders()
        self.stdout.write(
            self.style.SUCCESS(
                f"Marked {result['expired_marked']} expired certificate(s); sent {result['reminders_sent']} reminder notification(s)."
            )
        )
