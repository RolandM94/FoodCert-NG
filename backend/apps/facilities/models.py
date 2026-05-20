from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


class FacilityType(models.TextChoices):
    HOSPITAL = "hospital", "Hospital"
    CLINIC = "clinic", "Clinic"
    DIAGNOSTIC_CENTRE = "diagnostic_centre", "Diagnostic centre"
    PRIMARY_HEALTH_CENTRE = "primary_health_centre", "Primary health centre"
    MOBILE_HEALTH_UNIT = "mobile_health_unit", "Mobile health unit"


class OwnershipType(models.TextChoices):
    PUBLIC = "public", "Public"
    PRIVATE = "private", "Private"
    MISSION = "mission", "Mission"
    NGO = "ngo", "NGO"


class AccreditationStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    SUSPENDED = "suspended", "Suspended"
    EXPIRED = "expired", "Expired"
    REACCREDITATION_DUE = "reaccreditation_due", "Re-accreditation Due"


class MedicalFacility(BaseModel):
    organization = models.OneToOneField(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="medical_facility",
    )
    facility_name = models.CharField(max_length=255)
    facility_type = models.CharField(max_length=32, choices=FacilityType.choices)
    ownership_type = models.CharField(max_length=32, choices=OwnershipType.choices)
    license_number = models.CharField(max_length=120, db_index=True)
    registration_number = models.CharField(max_length=120, blank=True, db_index=True)
    address = models.TextField()
    state = models.ForeignKey("locations.State", on_delete=models.PROTECT, related_name="medical_facilities")
    lga = models.ForeignKey(
        "locations.LGA",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="medical_facilities",
    )
    contact_person = models.CharField(max_length=255)
    phone = models.CharField(max_length=32)
    email = models.EmailField()
    accreditation_status = models.CharField(
        max_length=32,
        choices=AccreditationStatus.choices,
        default=AccreditationStatus.DRAFT,
        db_index=True,
    )
    accreditation_start_date = models.DateField(null=True, blank=True)
    accreditation_expiry_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_medical_facilities",
    )
    standard_assessment_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        indexes = [
            models.Index(fields=["state"]),
            models.Index(fields=["lga"]),
            models.Index(fields=["accreditation_status"]),
            models.Index(fields=["facility_type"]),
        ]

    def __str__(self) -> str:
        return self.facility_name

    @property
    def is_accreditation_current(self) -> bool:
        return bool(
            self.accreditation_status == AccreditationStatus.APPROVED
            and self.accreditation_expiry_date
            and self.accreditation_expiry_date >= timezone.localdate()
        )

    @property
    def can_conduct_assessments(self) -> bool:
        return self.is_accreditation_current

    @staticmethod
    def default_expiry_date(start_date):
        return start_date + timedelta(days=365)


class FacilityAccreditationApplication(BaseModel):
    facility = models.ForeignKey(
        MedicalFacility,
        on_delete=models.CASCADE,
        related_name="accreditation_applications",
    )
    application_status = models.CharField(
        max_length=32,
        choices=AccreditationStatus.choices,
        default=AccreditationStatus.DRAFT,
        db_index=True,
    )
    has_reporting_policy = models.BooleanField(default=False)
    has_medical_records_computers = models.BooleanField(default=False)
    has_computer_operators = models.BooleanField(default=False)
    has_standard_forms = models.BooleanField(default=False)
    has_laboratory_request_forms = models.BooleanField(default=False)
    has_patient_files = models.BooleanField(default=False)
    has_qr_certificate_capability = models.BooleanField(default=False)
    has_internet_access = models.BooleanField(default=False)
    has_trained_records_staff = models.BooleanField(default=False)
    has_trained_clinical_staff = models.BooleanField(default=False)
    has_trained_non_clinical_staff = models.BooleanField(default=False)
    supporting_document = models.FileField(upload_to="facility_accreditation/", blank=True)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_facility_applications",
    )
    review_comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["facility"]),
            models.Index(fields=["application_status"]),
            models.Index(fields=["submitted_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.facility.facility_name} - {self.application_status}"

    @property
    def checklist_complete(self) -> bool:
        return all(
            [
                self.has_reporting_policy,
                self.has_medical_records_computers,
                self.has_computer_operators,
                self.has_standard_forms,
                self.has_laboratory_request_forms,
                self.has_patient_files,
                self.has_qr_certificate_capability,
                self.has_internet_access,
                self.has_trained_records_staff,
                self.has_trained_clinical_staff,
                self.has_trained_non_clinical_staff,
            ]
        )
