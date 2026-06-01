from django.core.management.base import BaseCommand

from apps.notifications.services import NotificationService


class Command(BaseCommand):
    help = "Process due scheduled notification reminders."

    def handle(self, *args, **options):
        count = NotificationService.process_due_reminders()
        self.stdout.write(self.style.SUCCESS(f"Processed {count} scheduled reminder(s)."))
