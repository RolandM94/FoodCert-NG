from django.core.management.base import BaseCommand

from apps.notifications.services import DigestService


class Command(BaseCommand):
    help = "Send daily digest notifications to users with digest enabled."

    def handle(self, *args, **options):
        count = DigestService.send_daily_digest()
        self.stdout.write(self.style.SUCCESS(f"Sent {count} daily digest(s)."))
