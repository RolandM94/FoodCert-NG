from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


class CertificateRequestStatus(models.TextChoices):
    PENDING_VALIDATION = "pending_validation", "Pending Validation"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CORRECTION_REQUESTED = "correction_requested", "Correction Requested"
    SUSPENDED = "suspended", "Suspended"


class CertificateStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    EXPIRED = "expired", "Expired"
    REVOKED = "revoked", "Revoked"
    SUSPENDED = "suspended", "Suspended"
    REPLACED = "replaced", "Replaced"
    PENDING_VALIDATION = "pending_validation", "Pending Validation"
    REJECTED = "rejected", "Rejected"


class VerificationResult(models.TextChoices):
    VALID = "valid", "Valid"
    EXPIRED = "expired", "Expired"
    REVOKED = "revoked", "Revoked"
    SUSPENDED = "suspended", "Suspended"
    INVALID = "invalid", "Invalid"
    NOT_FOUND = "not_found", "Not Found"


class CertificateRequest(BaseModel):
    assessment = models.OneToOneField("assessments.MedicalAssessment", on_delete=models.PROTECT, related_name="certificate_request")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="certificate_requests")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_certificate_requests",
    )
    status = models.CharField(
        max_length=32,
        choices=CertificateRequestStatus.choices,
        default=CertificateRequestStatus.PENDING_VALIDATION,
        db_index=True,
    )
    request_notes = models.TextField(blank=True)
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.assessment_id} - {self.status}"


class Certificate(BaseModel):
    certificate_number = models.CharField(max_length=64, unique=True, db_index=True)
    food_handler = models.ForeignKey("food_handlers.FoodHandlerProfile", on_delete=models.PROTECT, related_name="certificates")
    assessment = models.OneToOneField("assessments.MedicalAssessment", on_delete=models.PROTECT, related_name="certificate")
    employer = models.ForeignKey("employers.Employer", on_delete=models.SET_NULL, null=True, blank=True, related_name="certificates")
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.PROTECT, related_name="certificates")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="doctor_certificates")
    issuing_state = models.ForeignKey("locations.State", on_delete=models.PROTECT, related_name="certificates")
    issued_by_state_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_certificates",
    )
    issue_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=32, choices=CertificateStatus.choices, default=CertificateStatus.ACTIVE, db_index=True)
    qr_code_url = models.URLField(blank=True)
    verification_url = models.URLField()
    pdf_url = models.URLField(blank=True)
    digital_signature_hash = models.CharField(max_length=128)
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revoked_certificates",
    )
    revoked_at = models.DateTimeField(null=True, blank=True)
    revocation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-issue_date", "-created_at"]
        indexes = [
            models.Index(fields=["certificate_number"]),
            models.Index(fields=["food_handler"]),
            models.Index(fields=["assessment"]),
            models.Index(fields=["status"]),
            models.Index(fields=["expiry_date"]),
        ]

    def __str__(self) -> str:
        return self.certificate_number

    @property
    def is_expired(self) -> bool:
        return self.expiry_date < timezone.localdate()

    @property
    def effective_status(self) -> str:
        if self.status == CertificateStatus.ACTIVE and self.is_expired:
            return CertificateStatus.EXPIRED
        return self.status


class CertificateVerificationLog(BaseModel):
    certificate = models.ForeignKey(Certificate, on_delete=models.SET_NULL, null=True, blank=True, related_name="verification_logs")
    certificate_number_submitted = models.CharField(max_length=64, db_index=True)
    result = models.CharField(max_length=32, choices=VerificationResult.choices, db_index=True)
    ip_address = models.CharField(max_length=64, blank=True)
    user_agent = models.TextField(blank=True)
    verified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-verified_at"]
        indexes = [
            models.Index(fields=["certificate_number_submitted"]),
            models.Index(fields=["result"]),
            models.Index(fields=["verified_at"]),
        ]
