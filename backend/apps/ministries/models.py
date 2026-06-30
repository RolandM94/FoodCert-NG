from django.db import models

from apps.common.models import BaseModel


class MinistryType(models.TextChoices):
    STATE = "state", "State Ministry"
    FEDERAL = "federal", "Federal Ministry"


class MinistryStaffRole(models.TextChoices):
    STATE_SUPER_ADMIN = "state_super_admin", "State Ministry Super Admin"
    FOOD_SAFETY_OFFICER = "food_safety_officer", "Food Safety Directorate Officer"
    CERTIFICATE_VERIFICATION_OFFICER = "certificate_verification_officer", "Certificate Verification Officer"
    FACILITY_ACCREDITATION_OFFICER = "facility_accreditation_officer", "Facility Accreditation Officer"
    POLICY_FINANCE_OFFICER = "policy_finance_officer", "Policy and Finance Officer"
    INSPECTORATE_COORDINATOR = "inspectorate_coordinator", "Inspectorate Coordinator"
    LGA_OFFICER = "lga_officer", "LGA Office Officer"
    FEDERAL_SUPER_ADMIN = "federal_super_admin", "Federal Ministry Super Admin"
    NATIONAL_FOOD_SAFETY_OFFICER = "national_food_safety_officer", "National Food Safety Programme Officer"
    NATIONAL_ME_OFFICER = "national_me_officer", "National M&E Officer"
    NATIONAL_POLICY_OFFICER = "national_policy_officer", "National Policy Officer"
    NATIONAL_FINANCE_OFFICER = "national_finance_officer", "National Finance/Oversight Officer"
    FEDERAL_VIEWER = "federal_viewer", "Federal Viewer"


class MinistryStaffProfile(BaseModel):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="ministry_profile")
    ministry_type = models.CharField(max_length=16, choices=MinistryType.choices, db_index=True)
    sub_role = models.CharField(max_length=64, choices=MinistryStaffRole.choices, db_index=True)
    state = models.ForeignKey("locations.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="ministry_staff")
    lga = models.ForeignKey("locations.LGA", on_delete=models.SET_NULL, null=True, blank=True, related_name="ministry_staff")
    unit = models.ForeignKey("organizations.OrganizationUnit", on_delete=models.SET_NULL, null=True, blank=True, related_name="ministry_staff")
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="created_ministry_profiles")
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["user__email"]
        indexes = [
            models.Index(fields=["ministry_type"]),
            models.Index(fields=["sub_role"]),
            models.Index(fields=["state"]),
            models.Index(fields=["lga"]),
            models.Index(fields=["unit"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.get_sub_role_display()}"


class ReportingCycle(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    QUARTERLY = "quarterly", "Quarterly"
    ANNUAL = "annual", "Annual"


class CentralPortalStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"


class FederalProfile(BaseModel):
    """Singleton-style identity profile for the Federal Ministry of Health account."""

    ministry_name = models.CharField(max_length=255, default="Federal Ministry of Health and Social Welfare")
    department_name = models.CharField(max_length=255, blank=True)
    programme_name = models.CharField(max_length=255, blank=True)
    national_coordinator = models.CharField(max_length=255, blank=True)
    official_email = models.EmailField(blank=True)
    official_phone = models.CharField(max_length=32, blank=True)
    logo_url = models.URLField(blank=True)
    active_guideline_version = models.CharField(
        max_length=255,
        blank=True,
        default="National Guidelines for Food Handlers' Medical Test 2024",
    )
    reporting_cycle = models.CharField(max_length=16, choices=ReportingCycle.choices, default=ReportingCycle.QUARTERLY)
    central_portal_status = models.CharField(
        max_length=16,
        choices=CentralPortalStatus.choices,
        default=CentralPortalStatus.ACTIVE,
        db_index=True,
    )
    updated_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_federal_profiles",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.ministry_name or "Federal profile"


class StateReportStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    GENERATED = "generated", "Generated"
    SUBMITTED = "submitted", "Submitted"
    RETURNED = "returned", "Returned"
    ACCEPTED = "accepted", "Accepted"
    ESCALATED = "escalated", "Escalated"


class StateReport(BaseModel):
    state = models.ForeignKey("locations.State", on_delete=models.PROTECT, related_name="ministry_reports")
    report_type = models.CharField(max_length=64, db_index=True)
    reporting_period_start = models.DateField()
    reporting_period_end = models.DateField()
    status = models.CharField(max_length=16, choices=StateReportStatus.choices, default=StateReportStatus.GENERATED, db_index=True)
    generated_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="generated_state_reports")
    submitted_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="submitted_state_reports")
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_state_reports")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    file_url = models.URLField(blank=True)
    data_snapshot = models.JSONField(default=dict, blank=True)
    review_comment = models.TextField(blank=True)

    class Meta:
        ordering = ["-reporting_period_end", "-created_at"]
        indexes = [
            models.Index(fields=["state"], name="ministries__state_i_a36f89_idx"),
            models.Index(fields=["report_type"], name="ministries__report__268779_idx"),
            models.Index(fields=["status"], name="ministries__status_3f7640_idx"),
            models.Index(fields=["reporting_period_start", "reporting_period_end"], name="ministries__reporti_9284f0_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.state} {self.report_type} {self.reporting_period_start:%Y-%m-%d}"


class FederalStateQueryStatus(models.TextChoices):
    OPEN = "open", "Open"
    ASSIGNED = "assigned", "Assigned"
    AWAITING_STATE_RESPONSE = "awaiting_state_response", "Awaiting State Response"
    RESPONDED = "responded", "Responded"
    CLOSED = "closed", "Closed"


class FederalStateQueryPriority(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    URGENT = "urgent", "Urgent"


class PublicNoticeAudience(models.TextChoices):
    STATES = "states", "States"
    MEDICAL_FACILITIES = "medical_facilities", "Medical Facilities"
    FOOD_BUSINESSES = "food_businesses", "Food Businesses"
    FOOD_HANDLERS = "food_handlers", "Food Handlers"
    INSPECTORS = "inspectors", "Inspectors"
    GENERAL_PUBLIC = "general_public", "General Public"


class PublicNoticeStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class PublicNotice(BaseModel):
    title = models.CharField(max_length=255)
    body = models.TextField()
    audiences = models.JSONField(default=list, blank=True, help_text="List of PublicNoticeAudience values")
    attachments = models.JSONField(default=list, blank=True, help_text="List of {name, url} attachment objects")
    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=PublicNoticeStatus.choices, default=PublicNoticeStatus.DRAFT, db_index=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="created_public_notices")
    submitted_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="submitted_public_notices")
    approved_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_public_notices")
    published_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="published_public_notices")
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["effective_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"


class ComplianceAlertType(models.TextChoices):
    POLICY_NOT_ADOPTED = "policy_not_adopted", "State has not adopted active policy"
    REPORT_OVERDUE = "report_overdue", "State M&E report overdue"
    UNUSUAL_CERTIFICATE_PATTERN = "unusual_certificate_pattern", "Unusual certificate generation pattern"
    DUPLICATE_ACTIVE_CERTIFICATES = "duplicate_active_certificates", "Duplicate active certificates for same NIN"
    HIGH_FACILITY_SUSPENSION = "high_facility_suspension", "High facility suspension rate"
    HIGH_PENDING_LAB_RESULTS = "high_pending_lab_results", "High pending lab result rate"
    HIGH_EXPIRED_CERTIFICATES = "high_expired_certificates", "High expired certificate count"
    CERTIFICATE_VERIFICATION_FAILURE = "certificate_verification_failure", "Certificate verification failure spike"
    MANUAL = "manual", "Manual alert"


class ComplianceAlertSeverity(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class ComplianceAlertStatus(models.TextChoices):
    OPEN = "open", "Open"
    ACKNOWLEDGED = "acknowledged", "Acknowledged"
    IN_REVIEW = "in_review", "In Review"
    RESOLVED = "resolved", "Resolved"
    DISMISSED = "dismissed", "Dismissed"


class ComplianceAlert(BaseModel):
    alert_type = models.CharField(max_length=48, choices=ComplianceAlertType.choices, db_index=True)
    severity = models.CharField(max_length=16, choices=ComplianceAlertSeverity.choices, default=ComplianceAlertSeverity.MEDIUM, db_index=True)
    status = models.CharField(max_length=16, choices=ComplianceAlertStatus.choices, default=ComplianceAlertStatus.OPEN, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    state = models.ForeignKey("locations.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="compliance_alerts")
    entity_type = models.CharField(max_length=64, blank=True)
    entity_id = models.CharField(max_length=64, blank=True)
    metric_value = models.FloatField(null=True, blank=True)
    threshold_value = models.FloatField(null=True, blank=True)
    auto_generated = models.BooleanField(default=True, db_index=True)
    dedupe_key = models.CharField(max_length=255, blank=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="created_compliance_alerts")
    acknowledged_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="acknowledged_compliance_alerts")
    resolved_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="resolved_compliance_alerts")
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True)
    last_detected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["alert_type", "status"]),
            models.Index(fields=["state", "status"]),
            models.Index(fields=["severity"]),
            models.Index(fields=["dedupe_key"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_alert_type_display()} ({self.get_status_display()})"


class FederalStateQuery(BaseModel):
    state = models.ForeignKey("locations.State", on_delete=models.PROTECT, related_name="federal_queries")
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=64, db_index=True)
    priority = models.CharField(max_length=16, choices=FederalStateQueryPriority.choices, default=FederalStateQueryPriority.MEDIUM, db_index=True)
    status = models.CharField(max_length=32, choices=FederalStateQueryStatus.choices, default=FederalStateQueryStatus.OPEN, db_index=True)
    raised_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="raised_federal_queries")
    assigned_to = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_federal_queries")
    response = models.TextField(blank=True)
    responded_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="responded_federal_queries")
    responded_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["state"], name="ministries__state_i_652e24_idx"),
            models.Index(fields=["category"], name="ministries__categor_c77222_idx"),
            models.Index(fields=["priority"], name="ministries__priorit_07b82c_idx"),
            models.Index(fields=["status"], name="ministries__status_513085_idx"),
            models.Index(fields=["created_at"], name="ministries__created_dd00a4_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.state} - {self.subject}"
