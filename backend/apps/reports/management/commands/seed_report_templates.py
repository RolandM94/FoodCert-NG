from django.core.management.base import BaseCommand

from apps.reports.models import ReportFormat, ReportTemplate, ReportType


TEMPLATE_SCOPES = {
    ReportType.EMPLOYER_COMPLIANCE: "employer",
    ReportType.EMPLOYER_CERTIFICATES: "employer",
    ReportType.EMPLOYER_VACCINATIONS: "employer",
    ReportType.FACILITY_PERFORMANCE: "facility",
    ReportType.STATE_MONTHLY: "state",
    ReportType.NATIONAL: "federal",
    ReportType.VACCINATION_COVERAGE: "state",
    ReportType.ILLNESS_TRENDS: "state",
    ReportType.INSPECTION_OUTCOMES: "state",
    ReportType.MEDICAL_EXAMINATION: "facility",
    ReportType.TEMPORARILY_NOT_FIT: "facility",
    ReportType.RETURN_TO_WORK: "facility",
    ReportType.ASSESSMENT_COMPLETION: "facility",
    ReportType.VACCINATION_REVIEW: "facility",
    ReportType.RESTRICTED_LAB_SUMMARY: "facility",
}

PRIVACY_LEVELS = {
    "food_handler": "private",
    "employer": "employer_safe",
    "facility": "clinical_restricted",
    "state": "state_aggregate",
    "federal": "national_aggregate",
    "admin": "platform_sensitive",
}


class Command(BaseCommand):
    help = "Seed default report templates from the ReportType enum."

    def handle(self, *args, **options):
        formats = [ReportFormat.JSON, ReportFormat.CSV, ReportFormat.PDF, ReportFormat.EXCEL]
        created = 0
        updated = 0
        for report_type in ReportType:
            scope = TEMPLATE_SCOPES.get(report_type, "admin")
            _template, was_created = ReportTemplate.objects.update_or_create(
                code=report_type.value,
                defaults={
                    "name": report_type.label,
                    "description": f"Default FoodCert NG template for {report_type.label.lower()} reports.",
                    "module": "reports",
                    "scope": scope,
                    "output_formats": formats,
                    "default_filters": {},
                    "required_permissions": [scope],
                    "privacy_level": PRIVACY_LEVELS.get(scope, "platform_sensitive"),
                    "is_active": True,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded report templates: {created} created, {updated} updated."))
