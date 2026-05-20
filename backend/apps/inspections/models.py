from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


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
    IN_PROGRESS = "in_progress", "In Progress"
    SUBMITTED = "submitted", "Submitted"
    EMPLOYER_RESPONSE_SUBMITTED = "employer_response_submitted", "Employer Response Submitted"
    CLOSED = "closed", "Closed"


class InspectionResponseType(models.TextChoices):
    ACKNOWLEDGE = "acknowledge", "Acknowledge"
    CORRECTIVE_ACTION = "corrective_action", "Corrective Action"
    EVIDENCE = "evidence", "Evidence"
    COMMENT = "comment", "Comment"


class Inspection(BaseModel):
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="inspections")
    employer = models.ForeignKey("employers.Employer", on_delete=models.PROTECT, related_name="inspections")
    branch = models.ForeignKey(
        "organizations.OrganizationUnit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inspections",
    )
    inspection_date = models.DateTimeField(default=timezone.now)
    gps_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    checklist_responses = models.JSONField(default=dict, blank=True)
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    enforcement_action = models.CharField(max_length=32, choices=EnforcementAction.choices, default=EnforcementAction.NONE, db_index=True)
    findings = models.TextField(blank=True)
    evidence_files = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=32, choices=InspectionStatus.choices, default=InspectionStatus.DRAFT, db_index=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-inspection_date"]
        indexes = [
            models.Index(fields=["inspector"]),
            models.Index(fields=["employer"]),
            models.Index(fields=["branch"]),
            models.Index(fields=["inspection_date"]),
            models.Index(fields=["enforcement_action"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.employer} - {self.inspection_date:%Y-%m-%d}"


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
