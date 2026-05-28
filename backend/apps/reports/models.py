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


class ScheduledReportFrequency(models.TextChoices):
    DAILY = "daily", "Daily"
    WEEKLY = "weekly", "Weekly"
    MONTHLY = "monthly", "Monthly"
    QUARTERLY = "quarterly", "Quarterly"


class GeneratedReportStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    GENERATING = "generating", "Generating"
    GENERATED = "generated", "Generated"
    FAILED = "failed", "Failed"
    SUBMITTED = "submitted", "Submitted"
    RETURNED_FOR_CORRECTION = "returned_for_correction", "Returned for Correction"
    ACCEPTED = "accepted", "Accepted"
    ARCHIVED = "archived", "Archived"


class DataQualityIssueSeverity(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class DataQualityIssueStatus(models.TextChoices):
    OPEN = "open", "Open"
    ASSIGNED = "assigned", "Assigned"
    IN_PROGRESS = "in_progress", "In Progress"
    RESOLVED = "resolved", "Resolved"
    REJECTED = "rejected", "Rejected"
    ESCALATED = "escalated", "Escalated"


class ReportTemplate(BaseModel):
    code = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    module = models.CharField(max_length=100)
    scope = models.CharField(max_length=50, db_index=True)
    output_formats = models.JSONField(default=list, blank=True)
    default_filters = models.JSONField(default=dict, blank=True)
    required_permissions = models.JSONField(default=list, blank=True)
    privacy_level = models.CharField(max_length=50, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_report_templates")

    class Meta:
        ordering = ["scope", "name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["scope", "is_active"]),
            models.Index(fields=["privacy_level"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.scope})"


class MEIndicator(BaseModel):
    code = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, db_index=True)
    numerator_definition = models.TextField(blank=True)
    denominator_definition = models.TextField(blank=True)
    formula = models.TextField()
    data_sources = models.JSONField(default=list, blank=True)
    reporting_frequency = models.CharField(max_length=50, db_index=True)
    disaggregation_fields = models.JSONField(default=list, blank=True)
    target_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    warning_threshold = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    critical_threshold = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    visualization_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["category", "name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["reporting_frequency"]),
        ]

    def __str__(self) -> str:
        return self.name


class MEIndicatorValue(BaseModel):
    indicator = models.ForeignKey(MEIndicator, on_delete=models.CASCADE, related_name="values")
    state = models.ForeignKey("locations.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="me_indicator_values")
    lga = models.ForeignKey("locations.LGA", on_delete=models.SET_NULL, null=True, blank=True, related_name="me_indicator_values")
    organization = models.ForeignKey("organizations.Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="me_indicator_values")
    period_start = models.DateField()
    period_end = models.DateField()
    numerator_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    denominator_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    calculated_value = models.DecimalField(max_digits=18, decimal_places=4)
    disaggregation = models.JSONField(default=dict, blank=True)
    calculated_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-period_end", "indicator__category", "indicator__name"]
        indexes = [
            models.Index(fields=["indicator", "period_start", "period_end"]),
            models.Index(fields=["state", "period_end"]),
            models.Index(fields=["lga", "period_end"]),
            models.Index(fields=["organization", "period_end"]),
            models.Index(fields=["calculated_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.indicator.code} {self.period_start} - {self.period_end}"


class DashboardWidget(BaseModel):
    code = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    dashboard_scope = models.CharField(max_length=50, db_index=True)
    widget_type = models.CharField(max_length=50, db_index=True)
    metric_code = models.CharField(max_length=100, blank=True)
    configuration = models.JSONField(default=dict, blank=True)
    required_permissions = models.JSONField(default=list, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["dashboard_scope", "sort_order", "name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["dashboard_scope", "is_active"]),
            models.Index(fields=["widget_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.dashboard_scope})"


class DataQualityIssue(BaseModel):
    issue_type = models.CharField(max_length=100, db_index=True)
    severity = models.CharField(max_length=50, choices=DataQualityIssueSeverity.choices, default=DataQualityIssueSeverity.MEDIUM, db_index=True)
    module = models.CharField(max_length=100, db_index=True)
    target_type = models.CharField(max_length=100, db_index=True)
    target_id = models.UUIDField(null=True, blank=True, db_index=True)
    state = models.ForeignKey("locations.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="data_quality_issues")
    organization = models.ForeignKey("organizations.Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="data_quality_issues")
    description = models.TextField()
    status = models.CharField(max_length=50, choices=DataQualityIssueStatus.choices, default=DataQualityIssueStatus.OPEN, db_index=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_data_quality_issues")
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="resolved_data_quality_issues")
    resolved_at = models.DateTimeField(null=True, blank=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["issue_type"]),
            models.Index(fields=["severity", "status"]),
            models.Index(fields=["module", "target_type"]),
            models.Index(fields=["state", "status"]),
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["resolved_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.issue_type} [{self.severity}] - {self.status}"


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


class ScheduledReport(BaseModel):
    report_template = models.ForeignKey(ReportTemplate, on_delete=models.PROTECT, related_name="scheduled_reports")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="scheduled_reports")
    name = models.CharField(max_length=255)
    schedule_frequency = models.CharField(max_length=50, choices=ScheduledReportFrequency.choices, db_index=True)
    filters = models.JSONField(default=dict, blank=True)
    output_format = models.CharField(max_length=20, choices=ReportFormat.choices)
    delivery_channels = models.JSONField(default=list, blank=True)
    recipients = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["next_run_at", "name"]
        indexes = [
            models.Index(fields=["owner", "is_active"]),
            models.Index(fields=["report_template", "is_active"]),
            models.Index(fields=["schedule_frequency"]),
            models.Index(fields=["next_run_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.schedule_frequency})"


class GeneratedReport(BaseModel):
    title = models.CharField(max_length=255, blank=True)
    report_type = models.CharField(max_length=64, choices=ReportType.choices, db_index=True)
    organization = models.ForeignKey("organizations.Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="generated_reports")
    state = models.ForeignKey("locations.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="generated_reports")
    reporting_period_start = models.DateField(null=True, blank=True)
    reporting_period_end = models.DateField(null=True, blank=True)
    file_format = models.CharField(max_length=16, choices=ReportFormat.choices, default=ReportFormat.JSON)
    filters = models.JSONField(default=dict, blank=True)
    summary = models.JSONField(default=dict, blank=True)
    data_snapshot = models.JSONField(default=dict, blank=True)
    file_url = models.URLField(blank=True)
    status = models.CharField(max_length=50, choices=GeneratedReportStatus.choices, default=GeneratedReportStatus.PENDING, db_index=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="generated_reports")
    schedule = models.ForeignKey(ReportSchedule, on_delete=models.SET_NULL, null=True, blank=True, related_name="generated_reports")
    failure_reason = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    submitted_to_federal_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_generated_reports")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_status = models.CharField(max_length=50, blank=True)
    review_comment = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["report_type"]),
            models.Index(fields=["organization"]),
            models.Index(fields=["state"]),
            models.Index(fields=["file_format"]),
            models.Index(fields=["status"]),
            models.Index(fields=["reporting_period_start", "reporting_period_end"]),
            models.Index(fields=["created_at"]),
        ]
