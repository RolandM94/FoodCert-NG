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


class AccreditationCertificateType(models.TextChoices):
    EMPLOYER = "employer_accreditation", "Employer Accreditation"
    FACILITY = "facility_accreditation", "Facility Accreditation"


class VerificationResult(models.TextChoices):
    VALID = "valid", "Valid"
    EXPIRED = "expired", "Expired"
    REVOKED = "revoked", "Revoked"
    SUSPENDED = "suspended", "Suspended"
    REPLACED = "replaced", "Replaced"
    INVALID = "invalid", "Invalid"
    NOT_FOUND = "not_found", "Not Found"


class VerificationActorType(models.TextChoices):
    PUBLIC = "public", "Public"
    INSPECTOR = "inspector", "Inspector"
    EMPLOYER = "employer", "Employer"
    FOOD_HANDLER = "food_handler", "Food Handler"
    STATE = "state", "State Ministry"
    FEDERAL = "federal", "Federal Ministry"
    SYSTEM = "system", "System"


class CertificateTemplateScope(models.TextChoices):
    NATIONAL = "national", "National"
    STATE = "state", "State"


class CertificateTemplate(BaseModel):
    name = models.CharField(max_length=160)
    scope = models.CharField(max_length=24, choices=CertificateTemplateScope.choices, default=CertificateTemplateScope.NATIONAL, db_index=True)
    state = models.ForeignKey("locations.State", on_delete=models.CASCADE, null=True, blank=True, related_name="certificate_templates")
    ministry_name = models.CharField(max_length=180, default="FoodCert NG")
    subtitle = models.CharField(max_length=180, default="Official Food Handler Medical Fitness Certificate")
    logo_url = models.URLField(blank=True)
    accent_color = models.CharField(max_length=7, default="#0f5132")
    signatory_name = models.CharField(max_length=160, blank=True)
    signatory_title = models.CharField(max_length=160, default="Authorized Issuing Authority")
    footer_note = models.TextField(
        default="This certificate confirms fitness status only. It does not disclose lab results, diagnosis, clinical notes, or full NIN."
    )
    is_active = models.BooleanField(default=True, db_index=True)
    is_default = models.BooleanField(default=False, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_certificate_templates")

    class Meta:
        ordering = ["scope", "state__name", "-is_default", "name"]
        indexes = [
            models.Index(fields=["scope", "state", "is_default"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        scope = self.state.name if self.state_id else self.get_scope_display()
        return f"{self.name} ({scope})"


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
    facility_response = models.TextField(blank=True)
    facility_responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="facility_certificate_request_responses",
    )
    facility_responded_at = models.DateTimeField(null=True, blank=True)

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
    public_id = models.UUIDField(unique=True, db_index=True, null=True, blank=True)
    verification_token = models.CharField(max_length=96, unique=True, db_index=True, null=True, blank=True)
    food_handler = models.ForeignKey("food_handlers.FoodHandlerProfile", on_delete=models.PROTECT, related_name="certificates")
    assessment = models.OneToOneField("assessments.MedicalAssessment", on_delete=models.PROTECT, related_name="certificate")
    employer = models.ForeignKey("employers.Employer", on_delete=models.SET_NULL, null=True, blank=True, related_name="certificates")
    business_branch = models.ForeignKey(
        "organizations.OrganizationUnit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certificates",
    )
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
    template = models.ForeignKey(CertificateTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name="certificates")
    issue_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=32, choices=CertificateStatus.choices, default=CertificateStatus.ACTIVE, db_index=True)
    qr_code_url = models.URLField(blank=True)
    verification_url = models.URLField()
    pdf_url = models.URLField(blank=True)
    digital_signature_hash = models.CharField(max_length=128)
    replaced_by = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replaces")
    replacement_reason = models.TextField(blank=True)
    suspended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="suspended_certificates",
    )
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspension_reason = models.TextField(blank=True)
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
            models.Index(fields=["public_id"]),
            models.Index(fields=["verification_token"]),
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


class AccreditationCertificate(BaseModel):
    certificate_number = models.CharField(max_length=80, unique=True, db_index=True)
    certificate_type = models.CharField(max_length=40, choices=AccreditationCertificateType.choices, db_index=True)
    public_id = models.UUIDField(unique=True, db_index=True, null=True, blank=True)
    verification_token = models.CharField(max_length=96, unique=True, db_index=True, null=True, blank=True)
    employer = models.ForeignKey(
        "employers.Employer",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="accreditation_certificates",
    )
    facility = models.ForeignKey(
        "facilities.MedicalFacility",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="accreditation_certificates",
    )
    facility_application = models.ForeignKey(
        "facilities.FacilityAccreditationApplication",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accreditation_certificates",
    )
    issuing_state = models.ForeignKey("locations.State", on_delete=models.PROTECT, related_name="accreditation_certificates")
    issued_by_state_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_accreditation_certificates",
    )
    issue_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=32, choices=CertificateStatus.choices, default=CertificateStatus.ACTIVE, db_index=True)
    qr_code_url = models.URLField(blank=True)
    verification_url = models.URLField()
    pdf_url = models.URLField(blank=True)
    digital_signature_hash = models.CharField(max_length=128)
    suspended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="suspended_accreditation_certificates",
    )
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspension_reason = models.TextField(blank=True)
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revoked_accreditation_certificates",
    )
    revoked_at = models.DateTimeField(null=True, blank=True)
    revocation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-issue_date", "-created_at"]
        indexes = [
            models.Index(fields=["certificate_number"]),
            models.Index(fields=["certificate_type"]),
            models.Index(fields=["verification_token"]),
            models.Index(fields=["employer"]),
            models.Index(fields=["facility"]),
            models.Index(fields=["issuing_state"]),
            models.Index(fields=["status"]),
            models.Index(fields=["expiry_date"]),
        ]

    def __str__(self) -> str:
        return self.certificate_number

    @property
    def owner_name(self) -> str:
        if self.employer_id:
            return self.employer.business_name
        if self.facility_id:
            return self.facility.facility_name
        return ""

    @property
    def owner_type(self) -> str:
        if self.employer_id:
            return "employer"
        if self.facility_id:
            return "facility"
        return ""

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
    verification_token_submitted = models.CharField(max_length=96, blank=True, db_index=True)
    result = models.CharField(max_length=32, choices=VerificationResult.choices, db_index=True)
    verifier_type = models.CharField(max_length=32, choices=VerificationActorType.choices, default=VerificationActorType.PUBLIC, db_index=True)
    verifier_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certificate_verification_logs",
    )
    ip_address = models.CharField(max_length=64, blank=True)
    user_agent = models.TextField(blank=True)
    location_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    location_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    verified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-verified_at"]
        indexes = [
            models.Index(fields=["certificate_number_submitted"]),
            models.Index(fields=["verification_token_submitted"]),
            models.Index(fields=["result"]),
            models.Index(fields=["verifier_type"]),
            models.Index(fields=["verified_at"]),
        ]


class SuspiciousCertificateReport(BaseModel):
    certificate = models.ForeignKey(Certificate, on_delete=models.SET_NULL, null=True, blank=True, related_name="suspicious_reports")
    certificate_number_submitted = models.CharField(max_length=64, blank=True, db_index=True)
    verification_token_submitted = models.CharField(max_length=96, blank=True, db_index=True)
    reporter_name = models.CharField(max_length=255, blank=True)
    reporter_contact = models.CharField(max_length=255, blank=True)
    reason = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    ip_address = models.CharField(max_length=64, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["certificate_number_submitted"]),
            models.Index(fields=["verification_token_submitted"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return self.certificate_number_submitted or self.verification_token_submitted or str(self.id)
