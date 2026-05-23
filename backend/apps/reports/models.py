from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class ReportType(models.TextChoices):
    EMPLOYER_COMPLIANCE = "employer_compliance", "Employer Compliance"
    EMPLOYER_CERTIFICATES = "employer_certificates", "Employer Certificate Expiry"
    EMPLOYER_VACCINATIONS = "employer_vaccinations", "Employer Vaccination Compliance"
    FACILITY_PERFORMANCE = "facility_performance", "Facility Performance"
    STATE_MONTHLY = "state_monthly", "State Monthly"
    NATIONAL = "national", "National"
    VACCINATION_COVERAGE = "vaccination_coverage", "Vaccination Coverage"
    ILLNESS_TRENDS = "illness_trends", "Illness Trends"
    INSPECTION_OUTCOMES = "inspection_outcomes", "Inspection Outcomes"
    MEDICAL_EXAMINATION = "medical_examination", "Medical Examination Report"
    TEMPORARILY_NOT_FIT = "temporarily_not_fit_report", "Temporarily Not Fit Report"
    RETURN_TO_WORK = "return_to_work_report", "Return To Work Report"
    ASSESSMENT_COMPLETION = "assessment_completion", "Assessment Completion Summary"
    VACCINATION_REVIEW = "vaccination_review_report", "Vaccination Review Report"
    RESTRICTED_LAB_SUMMARY = "restricted_lab_summary", "Restricted Lab Summary"


class ReportFormat(models.TextChoices):
    JSON = "json", "JSON"
    CSV = "csv", "CSV"
    PDF = "pdf", "PDF"
    EXCEL = "excel", "Excel"


class ReportScheduleStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    PAUSED = "paused", "Paused"
    CANCELLED = "cancelled", "Cancelled"


class GeneratedReportStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    GENERATED = "generated", "Generated"
    FAILED = "failed", "Failed"


class ReportSchedule(BaseModel):
    report_type = models.CharField(max_length=64, choices=ReportType.choices, db_index=True)
    frequency = models.CharField(max_length=32, default="monthly")
    filters = models.JSONField(default=dict, blank=True)
    recipients = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=16, choices=ReportScheduleStatus.choices, default=ReportScheduleStatus.ACTIVE, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="report_schedules")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["report_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]


class GeneratedReport(BaseModel):
    report_type = models.CharField(max_length=64, choices=ReportType.choices, db_index=True)
    file_format = models.CharField(max_length=16, choices=ReportFormat.choices, default=ReportFormat.JSON)
    filters = models.JSONField(default=dict, blank=True)
    summary = models.JSONField(default=dict, blank=True)
    file_url = models.URLField(blank=True)
    status = models.CharField(max_length=16, choices=GeneratedReportStatus.choices, default=GeneratedReportStatus.PENDING, db_index=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="generated_reports")
    schedule = models.ForeignKey(ReportSchedule, on_delete=models.SET_NULL, null=True, blank=True, related_name="generated_reports")
    failure_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["report_type"]),
            models.Index(fields=["file_format"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]
