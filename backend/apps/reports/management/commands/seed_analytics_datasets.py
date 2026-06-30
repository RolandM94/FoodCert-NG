from django.core.management.base import BaseCommand

from apps.reports.dataset_registry import sync_analytics_datasets


class Command(BaseCommand):
    help = "Seed the flexible analytics dataset catalogue."

    def handle(self, *args, **options):
        created, updated = sync_analytics_datasets()
        self.stdout.write(self.style.SUCCESS(f"Seeded analytics datasets: {created} created, {updated} updated."))
