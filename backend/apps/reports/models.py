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


class DashboardAccountType(models.TextChoices):
    FEDERAL = "federal", "Federal Ministry"
    STATE = "state", "State Ministry"
    EMPLOYER = "employer", "Employer / Food Business"
    MEDICAL_FACILITY = "medical_facility", "Medical Facility"
    PLATFORM_ADMIN = "platform_admin", "Platform Admin"


class DashboardScopeType(models.TextChoices):
    PRIVATE = "private", "Private"
    ORGANIZATION = "organization", "Organization"
    ROLE_BASED = "role_based", "Role Based"
    SELECTED_USERS = "selected_users", "Selected Users"
    FEDERAL_ONLY = "federal_only", "Federal Only"
    STATE_ONLY = "state_only", "State Only"
    PUBLIC = "public", "Public"


class DashboardPrivacyLevel(models.TextChoices):
    PUBLIC = "public", "Public"
    INTERNAL = "internal", "Internal"
    CONFIDENTIAL = "confidential", "Confidential"
    PII = "pii", "PII"
    MEDICAL = "medical", "Medical"
    FINANCIAL = "financial", "Financial"
    SECURITY = "security", "Security"


class DashboardBlockType(models.TextChoices):
    WIDGET = "widget", "Widget Block"
    TEXT = "text", "Text Block"
    FILTER = "filter", "Filter Block"
    AI_INSIGHT = "ai_insight", "AI Insight Block"
    DATASET_PREVIEW = "dataset_preview", "Dataset Preview Block"
    QUICK_ACTION = "quick_action", "Quick Action Block"
    DIVIDER = "divider", "Divider / Section Header"


class DashboardAlertOperator(models.TextChoices):
    GREATER_THAN = "gt", "Greater Than"
    GREATER_THAN_OR_EQUAL = "gte", "Greater Than or Equal"
    LESS_THAN = "lt", "Less Than"
    LESS_THAN_OR_EQUAL = "lte", "Less Than or Equal"
    EQUAL = "eq", "Equal"
    NOT_EQUAL = "neq", "Not Equal"


class DashboardAlertStatus(models.TextChoices):
    TRIGGERED = "triggered", "Triggered"
    RESOLVED = "resolved", "Resolved"
    NO_DATA = "no_data", "No Data"


class DashboardExportJobStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


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


class AnalyticsDataset(BaseModel):
    code = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    module_source = models.CharField(max_length=100, db_index=True)
    allowed_account_types = models.JSONField(default=list, blank=True)
    allowed_roles = models.JSONField(default=list, blank=True)
    available_fields = models.JSONField(default=list, blank=True)
    field_labels = models.JSONField(default=dict, blank=True)
    field_types = models.JSONField(default=dict, blank=True)
    field_type_metadata = models.JSONField(default=dict, blank=True)
    sensitive_fields = models.JSONField(default=list, blank=True)
    default_filters = models.JSONField(default=dict, blank=True)
    joinable_datasets = models.JSONField(default=list, blank=True)
    aggregation_rules = models.JSONField(default=dict, blank=True)
    required_permissions = models.JSONField(default=list, blank=True)
    privacy_level = models.CharField(max_length=32, choices=DashboardPrivacyLevel.choices, default=DashboardPrivacyLevel.INTERNAL, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["module_source", "name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["module_source", "is_active"]),
            models.Index(fields=["privacy_level", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.module_source})"


class AnalyticsWorksheet(BaseModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="analytics_worksheets")
    organization = models.ForeignKey("organizations.Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="analytics_worksheets")
    state = models.ForeignKey("locations.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="analytics_worksheets")
    account_type = models.CharField(max_length=32, choices=DashboardAccountType.choices, db_index=True)
    scope_type = models.CharField(max_length=32, choices=DashboardScopeType.choices, default=DashboardScopeType.PRIVATE, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    dataset = models.ForeignKey(AnalyticsDataset, on_delete=models.PROTECT, related_name="worksheets")
    metrics = models.JSONField(default=list, blank=True)
    dimensions = models.JSONField(default=list, blank=True)
    filters = models.JSONField(default=list, blank=True)
    aggregations = models.JSONField(default=list, blank=True)
    derived_fields = models.JSONField(default=list, blank=True)
    query_rules = models.JSONField(default=dict, blank=True)
    chart_recommendation = models.CharField(max_length=50, blank=True, default="")
    preview_output = models.JSONField(default=dict, blank=True)
    required_permissions = models.JSONField(default=list, blank=True)
    privacy_metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_template = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["account_type", "name"]
        indexes = [
            models.Index(fields=["owner", "is_active"]),
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["state", "is_active"]),
            models.Index(fields=["account_type", "scope_type"]),
            models.Index(fields=["dataset", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.name


class AnalyticsWidget(BaseModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="analytics_widgets")
    organization = models.ForeignKey("organizations.Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="analytics_widgets")
    state = models.ForeignKey("locations.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="analytics_widgets")
    account_type = models.CharField(max_length=32, choices=DashboardAccountType.choices, db_index=True)
    scope_type = models.CharField(max_length=32, choices=DashboardScopeType.choices, default=DashboardScopeType.PRIVATE, db_index=True)
    worksheet = models.ForeignKey(AnalyticsWorksheet, on_delete=models.CASCADE, related_name="widgets")
    title = models.CharField(max_length=255)
    widget_type = models.CharField(max_length=50, db_index=True)
    visual_config = models.JSONField(default=dict, blank=True)
    filter_behavior = models.JSONField(default=dict, blank=True)
    refresh_behavior = models.JSONField(default=dict, blank=True)
    export_options = models.JSONField(default=dict, blank=True)
    required_permissions = models.JSONField(default=list, blank=True)
    privacy_metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["account_type", "title"]
        indexes = [
            models.Index(fields=["owner", "is_active"]),
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["state", "is_active"]),
            models.Index(fields=["account_type", "scope_type"]),
            models.Index(fields=["worksheet", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.title


class DashboardAlertRule(BaseModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dashboard_alert_rules")
    organization = models.ForeignKey("organizations.Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="dashboard_alert_rules")
    state = models.ForeignKey("locations.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="dashboard_alert_rules")
    account_type = models.CharField(max_length=32, choices=DashboardAccountType.choices, db_index=True)
    scope_type = models.CharField(max_length=32, choices=DashboardScopeType.choices, default=DashboardScopeType.PRIVATE, db_index=True)
    widget = models.ForeignKey(AnalyticsWidget, on_delete=models.CASCADE, related_name="alert_rules")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    metric_key = models.CharField(max_length=120)
    metric_label = models.CharField(max_length=255, blank=True)
    operator = models.CharField(max_length=8, choices=DashboardAlertOperator.choices, default=DashboardAlertOperator.LESS_THAN)
    threshold_value = models.DecimalField(max_digits=18, decimal_places=4)
    notification_channels = models.JSONField(default=list, blank=True)
    recipient_user_ids = models.JSONField(default=list, blank=True)
    required_permissions = models.JSONField(default=list, blank=True)
    privacy_metadata = models.JSONField(default=dict, blank=True)
    last_evaluated_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True, db_index=True)
    trigger_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["account_type", "name"]
        indexes = [
            models.Index(fields=["owner", "is_active"]),
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["state", "is_active"]),
            models.Index(fields=["account_type", "scope_type"]),
            models.Index(fields=["widget", "is_active"]),
            models.Index(fields=["last_triggered_at"]),
        ]

    def __str__(self) -> str:
        return self.name


class DashboardAlertEvent(BaseModel):
    rule = models.ForeignKey(DashboardAlertRule, on_delete=models.CASCADE, related_name="history")
    widget = models.ForeignKey(AnalyticsWidget, on_delete=models.CASCADE, related_name="alert_events")
    status = models.CharField(max_length=24, choices=DashboardAlertStatus.choices, db_index=True)
    observed_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    threshold_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    notification_count = models.PositiveIntegerField(default=0)
    notified_channels = models.JSONField(default=list, blank=True)
    message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["rule", "created_at"]),
            models.Index(fields=["widget", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.rule.name} {self.status}"


class DashboardCanvas(BaseModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dashboard_canvases")
    organization = models.ForeignKey("organizations.Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="dashboard_canvases")
    state = models.ForeignKey("locations.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="dashboard_canvases")
    account_type = models.CharField(max_length=32, choices=DashboardAccountType.choices, db_index=True)
    scope_type = models.CharField(max_length=32, choices=DashboardScopeType.choices, default=DashboardScopeType.PRIVATE, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    layout_config = models.JSONField(default=dict, blank=True)
    global_filters = models.JSONField(default=list, blank=True)
    required_permissions = models.JSONField(default=list, blank=True)
    privacy_metadata = models.JSONField(default=dict, blank=True)
    is_draft = models.BooleanField(default=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["account_type", "name"]
        indexes = [
            models.Index(fields=["owner", "is_active"]),
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["state", "is_active"]),
            models.Index(fields=["account_type", "scope_type"]),
            models.Index(fields=["is_draft", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.name


class DashboardCanvasBlock(BaseModel):
    canvas = models.ForeignKey(DashboardCanvas, on_delete=models.CASCADE, related_name="blocks")
    widget = models.ForeignKey(AnalyticsWidget, on_delete=models.SET_NULL, null=True, blank=True, related_name="canvas_blocks")
    block_type = models.CharField(max_length=32, choices=DashboardBlockType.choices, db_index=True)
    title = models.CharField(max_length=255, blank=True)
    content = models.JSONField(default=dict, blank=True)
    position = models.JSONField(default=dict, blank=True)
    visibility_rules = models.JSONField(default=dict, blank=True)
    required_permissions = models.JSONField(default=list, blank=True)
    privacy_metadata = models.JSONField(default=dict, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["canvas", "sort_order", "created_at"]
        indexes = [
            models.Index(fields=["canvas", "sort_order"]),
            models.Index(fields=["block_type", "is_active"]),
            models.Index(fields=["widget", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.canvas.name} / {self.block_type}"


class PublishedDashboard(BaseModel):
    canvas = models.ForeignKey(DashboardCanvas, on_delete=models.CASCADE, related_name="published_versions")
    published_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="published_dashboards")
    version_label = models.CharField(max_length=64, blank=True, default="")
    visibility_scope = models.CharField(max_length=32, choices=DashboardScopeType.choices, default=DashboardScopeType.PRIVATE, db_index=True)
    share_settings = models.JSONField(default=dict, blank=True)
    snapshot = models.JSONField(default=dict, blank=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["canvas", "is_active"]),
            models.Index(fields=["visibility_scope", "is_active"]),
            models.Index(fields=["published_by", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.version_label or f"{self.canvas.name} publication"


class DashboardExportJob(BaseModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dashboard_export_jobs")
    published_dashboard = models.ForeignKey(PublishedDashboard, on_delete=models.CASCADE, related_name="export_jobs")
    block_id = models.CharField(max_length=64, blank=True)
    export_format = models.CharField(max_length=16, db_index=True)
    status = models.CharField(max_length=24, choices=DashboardExportJobStatus.choices, default=DashboardExportJobStatus.PENDING, db_index=True)
    payload = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["published_dashboard", "status"]),
            models.Index(fields=["export_format", "status"]),
            models.Index(fields=["completed_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.published_dashboard_id}:{self.export_format}:{self.status}"


class DashboardTemplate(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    account_type = models.CharField(max_length=32, choices=DashboardAccountType.choices, db_index=True)
    scope_type = models.CharField(max_length=32, choices=DashboardScopeType.choices, default=DashboardScopeType.PRIVATE, db_index=True)
    source_canvas = models.ForeignKey(DashboardCanvas, on_delete=models.SET_NULL, null=True, blank=True, related_name="templates")
    source_published_dashboard = models.ForeignKey(PublishedDashboard, on_delete=models.SET_NULL, null=True, blank=True, related_name="templates")
    template_config = models.JSONField(default=dict, blank=True)
    required_permissions = models.JSONField(default=list, blank=True)
    privacy_metadata = models.JSONField(default=dict, blank=True)
    is_system_template = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="dashboard_templates")

    class Meta:
        ordering = ["account_type", "name"]
        indexes = [
            models.Index(fields=["account_type", "is_active"]),
            models.Index(fields=["scope_type", "is_active"]),
            models.Index(fields=["is_system_template", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.name


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
