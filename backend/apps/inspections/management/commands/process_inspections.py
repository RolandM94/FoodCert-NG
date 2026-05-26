from django.core.management.base import BaseCommand

from apps.inspections.services import InspectionJobService


class Command(BaseCommand):
    help = "Process inspection reminders, notice deadlines, and enforcement analytics."

    def handle(self, *args, **options):
        result = InspectionJobService.process_all()
        self.stdout.write(
            self.style.SUCCESS(
                f"Sent {result['reminders_sent']} inspection reminder(s); "
                f"{result['notice_notifications']} notice notification(s); "
                f"analytics: {result['analytics_results']['analytics']}"
            )
        )
