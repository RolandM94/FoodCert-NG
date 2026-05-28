from django.core.management.base import BaseCommand

from apps.reports.models import DashboardWidget


WIDGETS = [
    ("food_handler", "food_handler_certificate_status", "Certificate status", "kpi_card", "certificate_status", {"tone": "trust", "size": "compact"}),
    ("food_handler", "food_handler_assessment_status", "Assessment status", "trend_card", "assessment_status", {"trend_window": "30d"}),
    ("food_handler", "food_handler_vaccination_status", "Vaccination status", "kpi_card", "vaccination_status", {"required_vaccines": ["typhoid", "hepatitis_a"]}),
    ("food_handler", "food_handler_renewal_reminders", "Renewal reminders", "table", "renewal_reminders", {"limit": 5}),
    ("employer", "employer_compliance_percentage", "Compliance percentage", "kpi_card", "compliance_percentage", {"format": "percentage"}),
    ("employer", "employer_expiring_certificates", "Expiring certificates", "table", "expiring_certificates", {"days": 30}),
    ("employer", "employer_vaccination_due", "Vaccinations due", "bar_chart", "vaccination_due", {"group_by": "branch"}),
    ("employer", "employer_illness_return_to_work", "Return-to-work cases", "table", "illness_return_to_work", {"limit": 10}),
    ("facility", "facility_appointments_today", "Appointments today", "kpi_card", "appointments_today", {"date": "today"}),
    ("facility", "facility_assessments_in_progress", "Assessments in progress", "bar_chart", "assessments_in_progress", {"group_by": "status"}),
    ("facility", "facility_lab_requests_pending", "Lab requests pending", "table", "lab_requests_pending", {"limit": 10}),
    ("facility", "facility_settled_amount", "Settled amount", "trend_card", "settled_amount", {"format": "currency", "currency": "NGN"}),
    ("doctor", "doctor_assigned_assessments", "Assigned assessments", "kpi_card", "assigned_assessments", {"date_range": "current_week"}),
    ("doctor", "doctor_lab_results_pending_review", "Lab results pending review", "table", "lab_results_pending_review", {"limit": 10}),
    ("doctor", "doctor_decisions_pending", "Decisions pending", "kpi_card", "decisions_pending", {"priority": "oldest_first"}),
    ("lab", "lab_samples_pending_collection", "Samples pending collection", "kpi_card", "samples_pending_collection", {"sla_hours": 24}),
    ("lab", "lab_results_pending_upload", "Results pending upload", "table", "results_pending_upload", {"limit": 10}),
    ("lab", "lab_repeat_tests_required", "Repeat tests required", "bar_chart", "repeat_tests_required", {"group_by": "test_type"}),
    ("inspector", "inspector_assigned_inspections", "Assigned inspections", "kpi_card", "assigned_inspections", {"date_range": "current_month"}),
    ("inspector", "inspector_due_today", "Due today", "table", "due_today", {"date": "today"}),
    ("inspector", "inspector_overdue", "Overdue inspections", "kpi_card", "overdue", {"tone": "risk"}),
    ("inspector", "inspector_notices_issued", "Notices issued", "line_chart", "notices_issued", {"period": "monthly"}),
    ("state", "state_registered_food_handlers", "Registered food handlers", "kpi_card", "registered_food_handlers", {"scope": "state"}),
    ("state", "state_certification_coverage_rate", "Certification coverage", "trend_card", "certification_coverage_rate", {"format": "percentage"}),
    ("state", "state_pending_certificate_validations", "Pending certificate validations", "table", "pending_certificate_validations", {"limit": 15}),
    ("state", "state_revenue_trend", "Revenue trend", "line_chart", "assessment_revenue", {"period": "monthly", "format": "currency"}),
    ("federal", "federal_national_certification_coverage", "National certification coverage", "trend_card", "national_certification_coverage", {"format": "percentage"}),
    ("federal", "federal_states_with_overdue_reports", "States with overdue reports", "table", "states_with_overdue_reports", {"limit": 15}),
    ("federal", "federal_state_comparison_table", "State performance comparison", "table", "state_comparison_table", {"privacy": "aggregate"}),
    ("federal", "federal_data_quality_risks", "Data quality risks", "bar_chart", "data_quality_risks", {"group_by": "state"}),
    ("admin", "admin_platform_activity", "Platform activity", "line_chart", "platform_activity", {"period": "daily"}),
    ("admin", "admin_report_generation_volume", "Report generation volume", "bar_chart", "report_generation_volume", {"group_by": "report_type"}),
    ("admin", "admin_data_quality_issue_queue", "Data quality issue queue", "table", "data_quality_issue_queue", {"limit": 20}),
]


class Command(BaseCommand):
    help = "Seed default FoodCert NG dashboard widgets."

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for sort_order, (scope, code, name, widget_type, metric_code, configuration) in enumerate(WIDGETS, start=1):
            _widget, was_created = DashboardWidget.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "dashboard_scope": scope,
                    "widget_type": widget_type,
                    "metric_code": metric_code,
                    "configuration": configuration,
                    "required_permissions": [scope],
                    "sort_order": sort_order,
                    "is_active": True,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded dashboard widgets: {created} created, {updated} updated."))
