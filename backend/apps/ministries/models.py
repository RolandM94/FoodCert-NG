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


class StateReportStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    GENERATED = "generated", "Generated"
    SUBMITTED = "submitted", "Submitted"
    RETURNED = "returned", "Returned"
    ACCEPTED = "accepted", "Accepted"


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
            models.Index(fields=["state"]),
            models.Index(fields=["report_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["reporting_period_start", "reporting_period_end"]),
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
            models.Index(fields=["state"]),
            models.Index(fields=["category"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.state} - {self.subject}"
