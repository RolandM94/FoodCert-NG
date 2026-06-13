from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


class InspectionType(models.TextChoices):
    ROUTINE = "routine", "Routine Inspection"
    FOLLOW_UP = "follow_up", "Follow-Up Inspection"
    COMPLAINT_BASED = "complaint_based", "Complaint-Based Inspection"
    CERTIFICATE_SWEEP = "certificate_sweep", "Certificate Verification Sweep"
    ILLNESS_RISK = "illness_risk", "Illness / Public Health Risk Inspection"
    FACILITY_LINKED = "facility_linked", "Facility-Linked Verification"


class InspectionPriority(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class EnforcementAction(models.TextChoices):
    NONE = "none", "None"
    ADVISORY = "advisory", "Advisory"
    WARNING = "warning", "Warning"
    COMPLIANCE_NOTICE = "compliance_notice", "Compliance Notice"
    FOLLOW_UP_REQUIRED = "follow_up_required", "Follow Up Required"
    SANCTION_RECOMMENDED = "sanction_recommended", "Sanction Recommended"
    ESCALATED_TO_STATE = "escalated_to_state", "Escalated To State"


class InspectionStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ASSIGNED = "assigned", "Assigned"
    ACCEPTED = "accepted", "Accepted"
    SCHEDULED = "scheduled", "Scheduled"
    IN_PROGRESS = "in_progress", "In Progress"
    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    RETURNED_FOR_CORRECTION = "returned_for_correction", "Returned for Correction"
    NOTICE_ISSUED = "notice_issued", "Notice Issued"
    CORRECTIVE_ACTION_PENDING = "corrective_action_pending", "Corrective Action Pending"
    CORRECTIVE_ACTION_SUBMITTED = "corrective_action_submitted", "Corrective Action Submitted"
    FOLLOW_UP_REQUIRED = "follow_up_required", "Follow-Up Required"
    FOLLOW_UP_SCHEDULED = "follow_up_scheduled", "Follow-Up Scheduled"
    RESOLVED = "resolved", "Resolved"
    ESCALATED = "escalated", "Escalated"
    CLOSED = "closed", "Closed"
    CANCELLED = "cancelled", "Cancelled"


class InspectionResponseType(models.TextChoices):
    ACKNOWLEDGE = "acknowledge", "Acknowledge"
    CORRECTIVE_ACTION = "corrective_action", "Corrective Action"
    EVIDENCE = "evidence", "Evidence"
    COMMENT = "comment", "Comment"


INSPECTION_STATUS_TRANSITIONS = {
    InspectionStatus.DRAFT: [InspectionStatus.ASSIGNED, InspectionStatus.CANCELLED],
    InspectionStatus.ASSIGNED: [InspectionStatus.ACCEPTED, InspectionStatus.CANCELLED],
    InspectionStatus.ACCEPTED: [InspectionStatus.SCHEDULED, InspectionStatus.IN_PROGRESS, InspectionStatus.ASSIGNED, InspectionStatus.CANCELLED],
    InspectionStatus.SCHEDULED: [InspectionStatus.IN_PROGRESS, InspectionStatus.CANCELLED],
    InspectionStatus.IN_PROGRESS: [InspectionStatus.SUBMITTED, InspectionStatus.ESCALATED, InspectionStatus.CANCELLED],
    InspectionStatus.SUBMITTED: [InspectionStatus.UNDER_REVIEW, InspectionStatus.CORRECTIVE_ACTION_SUBMITTED, InspectionStatus.ESCALATED, InspectionStatus.CANCELLED],
    InspectionStatus.UNDER_REVIEW: [
        InspectionStatus.RETURNED_FOR_CORRECTION,
        InspectionStatus.NOTICE_ISSUED,
        InspectionStatus.RESOLVED,
        InspectionStatus.ESCALATED,
        InspectionStatus.CANCELLED,
    ],
    InspectionStatus.RETURNED_FOR_CORRECTION: [InspectionStatus.IN_PROGRESS, InspectionStatus.SUBMITTED, InspectionStatus.CANCELLED],
    InspectionStatus.NOTICE_ISSUED: [
        InspectionStatus.CORRECTIVE_ACTION_PENDING,
        InspectionStatus.FOLLOW_UP_SCHEDULED,
        InspectionStatus.CLOSED,
        InspectionStatus.ESCALATED,
    ],
    InspectionStatus.CORRECTIVE_ACTION_PENDING: [
        InspectionStatus.CORRECTIVE_ACTION_SUBMITTED,
        InspectionStatus.FOLLOW_UP_SCHEDULED,
        InspectionStatus.ESCALATED,
        InspectionStatus.CANCELLED,
    ],
    InspectionStatus.CORRECTIVE_ACTION_SUBMITTED: [
        InspectionStatus.FOLLOW_UP_REQUIRED,
        InspectionStatus.RESOLVED,
        InspectionStatus.UNDER_REVIEW,
        InspectionStatus.ESCALATED,
    ],
    InspectionStatus.FOLLOW_UP_REQUIRED: [InspectionStatus.FOLLOW_UP_SCHEDULED, InspectionStatus.CANCELLED],
    InspectionStatus.FOLLOW_UP_SCHEDULED: [InspectionStatus.IN_PROGRESS, InspectionStatus.CANCELLED],
    InspectionStatus.RESOLVED: [InspectionStatus.CLOSED],
    InspectionStatus.ESCALATED: [InspectionStatus.UNDER_REVIEW, InspectionStatus.CLOSED],
    InspectionStatus.CLOSED: [],
    InspectionStatus.CANCELLED: [],
}


def validate_status_transition(inspection, new_status):
    if not inspection.pk:
        return
    current_value = Inspection.objects.filter(pk=inspection.pk).values_list("status", flat=True).first()
    if current_value is None:
        return
    if current_value == new_status:
        return
    current = InspectionStatus(current_value)
    allowed = INSPECTION_STATUS_TRANSITIONS.get(current, [])
    target = InspectionStatus(new_status)
    if target not in allowed:
        raise ValidationError(
            f"Cannot transition inspection from '{current.label}' to '{target.label}'."
        )


class Inspection(BaseModel):
    reference = models.CharField(max_length=100, unique=True, blank=True, db_index=True)
    inspection_type = models.CharField(
        max_length=80, choices=InspectionType.choices, default=InspectionType.ROUTINE, db_index=True
    )
    priority = models.CharField(
        max_length=50, choices=InspectionPriority.choices, default=InspectionPriority.MEDIUM, db_index=True
    )
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="inspections")
    employer = models.ForeignKey("employers.Employer", on_delete=models.PROTECT, related_name="inspections")
    branch = models.ForeignKey(
        "organizations.OrganizationUnit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inspections",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_inspection_assignments",
    )
    supervising_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervised_inspections",
    )
    parent_inspection = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="follow_up_inspections",
    )
    linked_complaint_id = models.UUIDField(null=True, blank=True)
    linked_illness_report_id = models.UUIDField(null=True, blank=True)
    inspection_date = models.DateTimeField(default=timezone.now)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    gps_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    reason = models.TextField(blank=True)
    checklist_responses = models.JSONField(default=dict, blank=True)
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    enforcement_action = models.CharField(max_length=32, choices=EnforcementAction.choices, default=EnforcementAction.NONE, db_index=True)
    findings = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    evidence_files = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=50, choices=InspectionStatus.choices, default=InspectionStatus.DRAFT, db_index=True)
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-inspection_date"]
        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["inspector"]),
            models.Index(fields=["employer"]),
            models.Index(fields=["branch"]),
            models.Index(fields=["assigned_by"]),
            models.Index(fields=["inspection_date"]),
            models.Index(fields=["inspection_type"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["enforcement_action"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        ref = self.reference or str(self.id)[:8]
        return f"{ref} - {self.inspection_date:%Y-%m-%d}"

    def clean(self):
        if self.employer_id and self.branch_id and self.branch.organization_id != self.employer.organization_id:
            raise ValidationError("Branch must belong to the employer's organization.")

    def save(self, *args, **kwargs):
        validate_status_transition(self, self.status)
        if not self.reference:
            self.reference = self._generate_reference()
        super().save(*args, **kwargs)

    def _generate_reference(self):
        today = timezone.now()
        prefix = f"FCN-INS-{today.year}"
        latest = (
            Inspection.objects.filter(reference__startswith=prefix)
            .order_by("-reference")
            .values_list("reference", flat=True)
            .first()
        )
        if latest:
            try:
                seq = int(latest.split("-")[-1]) + 1
            except (IndexError, ValueError):
                seq = 1
        else:
            seq = 1
        return f"{prefix}-{seq:06d}"

    def transition_to(self, new_status):
        validate_status_transition(self, new_status)
        self.status = new_status
        self.save(update_fields=["status", "updated_at"])


class InspectionCertificateScan(BaseModel):
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name="certificate_scans")
    certificate_number = models.CharField(max_length=64, db_index=True)
    certificate = models.ForeignKey("certificates.Certificate", on_delete=models.SET_NULL, null=True, blank=True, related_name="inspection_scans")
    result = models.CharField(max_length=32, db_index=True)
    scanned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-scanned_at"]
        indexes = [
            models.Index(fields=["inspection"]),
            models.Index(fields=["certificate_number"]),
            models.Index(fields=["result"]),
        ]


class InspectionResponse(BaseModel):
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name="employer_responses")
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="inspection_responses")
    response_type = models.CharField(max_length=32, choices=InspectionResponseType.choices, db_index=True)
    content = models.TextField(blank=True)
    evidence_file_url = models.URLField(blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["inspection"]),
            models.Index(fields=["submitted_by"]),
            models.Index(fields=["response_type"]),
            models.Index(fields=["submitted_at"]),
        ]


class ChecklistCategory(models.TextChoices):
    FOOD_HANDLER_CERT = "food_handler_certification", "A. Food Handler Certification"
    FITNESS_EXCLUSION = "fitness_exclusion_compliance", "B. Fitness and Exclusion Compliance"
    VACCINATION = "vaccination_compliance", "C. Vaccination Compliance"
    EMPLOYER_RECORDS = "employer_records", "D. Employer Records"
    HYGIENE = "hygiene_food_safety", "E. Hygiene and Food Safety Practices"
    CERT_AUTHENTICITY = "certificate_authenticity", "F. Certificate Authenticity"
    CORRECTIVE_ACTION = "corrective_action_compliance", "G. Corrective Action Compliance"


class ChecklistSeverity(models.TextChoices):
    MINOR = "minor", "Minor"
    MAJOR = "major", "Major"
    CRITICAL = "critical", "Critical"


class InspectionChecklistItem(BaseModel):
    category = models.CharField(max_length=50, choices=ChecklistCategory.choices, db_index=True)
    question = models.TextField()
    severity_if_failed = models.CharField(max_length=50, choices=ChecklistSeverity.choices, default=ChecklistSeverity.MAJOR)
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["category", "sort_order"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"[{self.get_category_display()}] {self.question[:80]}"


class ChecklistResponseChoice(models.TextChoices):
    YES = "yes", "Yes"
    NO = "no", "No"
    NOT_APPLICABLE = "n_a", "Not Applicable"
    NOT_OBSERVED = "not_observed", "Not Observed"
    NEEDS_FOLLOW_UP = "needs_follow_up", "Needs Follow-Up"


class InspectionChecklistResponse(BaseModel):
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name="checklist_item_responses")
    checklist_item = models.ForeignKey(InspectionChecklistItem, on_delete=models.PROTECT, related_name="inspection_responses")
    response = models.CharField(max_length=50, choices=ChecklistResponseChoice.choices, default=ChecklistResponseChoice.NOT_OBSERVED)
    severity = models.CharField(max_length=50, choices=ChecklistSeverity.choices, blank=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="checklist_responses")

    class Meta:
        ordering = ["checklist_item__category", "checklist_item__sort_order"]
        indexes = [
            models.Index(fields=["inspection"]),
            models.Index(fields=["checklist_item"]),
            models.Index(fields=["response"]),
        ]
        unique_together = [("inspection", "checklist_item")]

    def __str__(self) -> str:
        return f"{self.inspection.reference} - {self.checklist_item.question[:50]} -> {self.response}"


class FindingType(models.TextChoices):
    COMPLIANCE_CONFIRMED = "compliance_confirmed", "Compliance Confirmed"
    MINOR_NON_COMPLIANCE = "minor_non_compliance", "Minor Non-Compliance"
    MAJOR_NON_COMPLIANCE = "major_non_compliance", "Major Non-Compliance"
    CRITICAL_NON_COMPLIANCE = "critical_non_compliance", "Critical Non-Compliance"
    SUSPICIOUS_CERTIFICATE = "suspicious_certificate", "Suspicious Certificate"
    PUBLIC_HEALTH_RISK = "public_health_risk", "Public Health Risk"
    DOCUMENTATION_GAP = "documentation_gap", "Documentation Gap"
    REPEAT_VIOLATION = "repeat_violation", "Repeat Violation"


class FindingStatus(models.TextChoices):
    OPEN = "open", "Open"
    UNDER_REVIEW = "under_review", "Under Review"
    NOTICE_ISSUED = "notice_issued", "Notice Issued"
    CORRECTIVE_ACTION_PENDING = "corrective_action_pending", "Corrective Action Pending"
    CORRECTED = "corrected", "Corrected"
    NOT_CORRECTED = "not_corrected", "Not Corrected"
    ESCALATED = "escalated", "Escalated"
    CLOSED = "closed", "Closed"


class InspectionFinding(BaseModel):
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name="structured_findings")
    category = models.CharField(max_length=100, choices=ChecklistCategory.choices)
    finding_type = models.CharField(max_length=100, choices=FindingType.choices, default=FindingType.MINOR_NON_COMPLIANCE)
    severity = models.CharField(max_length=50, choices=ChecklistSeverity.choices, default=ChecklistSeverity.MINOR)
    description = models.TextField()
    recommended_action = models.TextField(blank=True)
    food_handler = models.ForeignKey(
        "food_handlers.FoodHandlerProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inspection_findings",
    )
    certificate = models.ForeignKey(
        "certificates.Certificate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inspection_findings",
    )
    status = models.CharField(max_length=50, choices=FindingStatus.choices, default=FindingStatus.OPEN, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="findings_created"
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["inspection"]),
            models.Index(fields=["finding_type"]),
            models.Index(fields=["severity"]),
            models.Index(fields=["status"]),
            models.Index(fields=["food_handler"]),
            models.Index(fields=["certificate"]),
        ]

    def __str__(self) -> str:
        return f"Finding #{self.id.hex[:8]} [{self.severity}] - {self.description[:80]}"


class EvidenceType(models.TextChoices):
    PHOTO = "photo", "Photo"
    VIDEO = "video", "Video"
    DOCUMENT = "document", "Document"
    CERT_SCREENSHOT = "cert_screenshot", "Certificate Screenshot"
    SIGNED_NOTICE = "signed_notice", "Signed Notice"
    EMPLOYER_RESPONSE_DOC = "employer_response_doc", "Employer Response Document"
    INSPECTOR_NOTE = "inspector_note", "Inspector Note"
    GPS_LOCATION = "gps_location", "GPS/Location Metadata"


class InspectionEvidence(BaseModel):
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name="evidence_entries")
    finding = models.ForeignKey(
        InspectionFinding,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="evidence",
    )
    evidence_type = models.CharField(max_length=50, choices=EvidenceType.choices, default=EvidenceType.PHOTO)
    file_url = models.URLField()
    caption = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="evidence_uploaded"
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["inspection"]),
            models.Index(fields=["finding"]),
            models.Index(fields=["evidence_type"]),
        ]

    def __str__(self) -> str:
        return f"Evidence #{self.id.hex[:8]} [{self.evidence_type}]"


class NoticeType(models.TextChoices):
    ADVISORY = "advisory", "Advisory Notice"
    WARNING = "warning", "Warning Notice"
    COMPLIANCE = "compliance", "Compliance Notice"
    CORRECTIVE_ACTION = "corrective_action", "Corrective Action Notice"
    FOLLOW_UP = "follow_up", "Follow-Up Notice"
    SUSPENSION_RECOMMENDATION = "suspension_recommendation", "Suspension Recommendation"
    CLOSURE_RECOMMENDATION = "closure_recommendation", "Closure Recommendation"
    PUBLIC_HEALTH_ESCALATION = "public_health_escalation", "Public Health Escalation"
    CERT_REVIEW_RECOMMENDATION = "cert_review_recommendation", "Certificate Review Recommendation"
    FACILITY_REVIEW_RECOMMENDATION = "facility_review_recommendation", "Facility Review Recommendation"


class NoticeStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING_APPROVAL = "pending_approval", "Pending Approval"
    ISSUED = "issued", "Issued"
    ACKNOWLEDGED = "acknowledged", "Acknowledged"
    CORRECTIVE_ACTION_PENDING = "corrective_action_pending", "Corrective Action Pending"
    RESPONSE_SUBMITTED = "response_submitted", "Response Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    FOLLOW_UP_REQUIRED = "follow_up_required", "Follow-Up Required"
    ESCALATED = "escalated", "Escalated"
    CLOSED = "closed", "Closed"


class EnforcementNotice(BaseModel):
    notice_reference = models.CharField(max_length=100, unique=True, db_index=True)
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name="notices")
    employer = models.ForeignKey("employers.Employer", on_delete=models.PROTECT, related_name="enforcement_notices")
    branch = models.ForeignKey(
        "organizations.OrganizationUnit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enforcement_notices",
    )
    notice_type = models.CharField(max_length=50, choices=NoticeType.choices, db_index=True)
    status = models.CharField(max_length=50, choices=NoticeStatus.choices, default=NoticeStatus.DRAFT, db_index=True)
    description = models.TextField()
    required_corrective_actions = models.TextField()
    deadline = models.DateField(null=True, blank=True)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="notices_issued", on_delete=models.SET_NULL, null=True
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="notices_approved", on_delete=models.SET_NULL, null=True, blank=True
    )
    issued_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closure_note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["notice_reference"]),
            models.Index(fields=["inspection"]),
            models.Index(fields=["employer"]),
            models.Index(fields=["notice_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["deadline"]),
        ]

    def __str__(self) -> str:
        return f"Notice {self.notice_reference} [{self.get_notice_type_display()}]"


class CorrectiveActionStatus(models.TextChoices):
    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    MORE_EVIDENCE_REQUESTED = "more_evidence_requested", "More Evidence Requested"


class CorrectiveActionResponse(BaseModel):
    notice = models.ForeignKey(EnforcementNotice, on_delete=models.CASCADE, related_name="corrective_actions")
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="corrective_actions_submitted"
    )
    response_note = models.TextField()
    action_taken = models.TextField()
    status = models.CharField(max_length=50, choices=CorrectiveActionStatus.choices, default=CorrectiveActionStatus.SUBMITTED)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="corrective_actions_reviewed", on_delete=models.SET_NULL, null=True, blank=True
    )
    review_note = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["notice"]),
            models.Index(fields=["submitted_by"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"Response #{self.id.hex[:8]} to {self.notice.notice_reference}"


class CaseStatus(models.TextChoices):
    OPEN = "open", "Open"
    UNDER_REVIEW = "under_review", "Under Review"
    AWAITING_EMPLOYER_RESPONSE = "awaiting_employer_response", "Awaiting Employer Response"
    FOLLOW_UP_REQUIRED = "follow_up_required", "Follow-Up Required"
    ESCALATED = "escalated", "Escalated"
    RESOLVED = "resolved", "Resolved"
    CLOSED = "closed", "Closed"


class CaseSeverity(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class EscalationLevel(models.TextChoices):
    COORDINATOR = "inspectorate_coordinator", "Inspectorate Coordinator"
    STATE_ADMIN = "state_admin", "State Ministry Admin"
    FEDERAL = "federal", "Federal Ministry Oversight"
    OTHER_AUTHORITY = "other_authority", "Other Regulatory Body"


class EnforcementCase(BaseModel):
    case_reference = models.CharField(max_length=100, unique=True, db_index=True)
    state = models.ForeignKey("locations.State", on_delete=models.PROTECT, related_name="enforcement_cases")
    employer = models.ForeignKey("employers.Employer", on_delete=models.PROTECT, related_name="enforcement_cases")
    branch = models.ForeignKey(
        "organizations.OrganizationUnit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enforcement_cases",
    )
    status = models.CharField(max_length=50, choices=CaseStatus.choices, default=CaseStatus.OPEN, db_index=True)
    severity = models.CharField(max_length=50, choices=CaseSeverity.choices, default=CaseSeverity.MEDIUM)
    summary = models.TextField()
    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="enforcement_cases_opened", on_delete=models.SET_NULL, null=True
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="enforcement_cases_assigned", on_delete=models.SET_NULL, null=True, blank=True
    )
    escalated_to = models.CharField(max_length=50, choices=EscalationLevel.choices, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closure_note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["case_reference"]),
            models.Index(fields=["state"]),
            models.Index(fields=["employer"]),
            models.Index(fields=["status"]),
            models.Index(fields=["severity"]),
        ]

    def __str__(self) -> str:
        return f"Case {self.case_reference} [{self.get_status_display()}]"
