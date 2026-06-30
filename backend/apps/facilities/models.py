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
    MORE_INFORMATION_REQUIRED = "more_information_required", "More Information Required"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    SUSPENDED = "suspended", "Suspended"
    EXPIRED = "expired", "Expired"
    REACCREDITATION_DUE = "reaccreditation_due", "Re-accreditation Due"


class FacilityDocumentStatus(models.TextChoices):
    UPLOADED = "uploaded", "Uploaded"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"


class FacilityDocumentType(models.TextChoices):
    FACILITY_LICENSE = "facility_license", "Facility license"
    CORPORATE_REGISTRATION = "corporate_registration", "Corporate registration"
    MEDICAL_DIRECTOR_CREDENTIAL = "medical_director_credential", "Medical director credential"
    DOCTOR_LICENSE = "doctor_license", "Doctor license"
    LAB_STAFF_CREDENTIAL = "lab_staff_credential", "Lab staff credential"
    LABORATORY_LICENSE = "laboratory_license", "Laboratory license"
    DOCUMENTATION_POLICY = "documentation_policy", "Documentation policy"
    CONFIDENTIALITY_POLICY = "confidentiality_policy", "Confidentiality policy"
    FACILITY_PHOTO = "facility_photo", "Facility photo"
    EQUIPMENT_LIST = "equipment_list", "Equipment list"
    DIGITAL_READINESS = "digital_readiness", "Digital readiness"
    BANK_DETAILS = "bank_details", "Bank details"
    STATE_REQUIRED_FORM = "state_required_form", "State required form"
    OTHER = "other", "Other"


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
    ward = models.CharField(max_length=120, blank=True)
    contact_person = models.CharField(max_length=255)
    phone = models.CharField(max_length=32)
    email = models.EmailField()
    operating_hours = models.CharField(max_length=255, blank=True)
    service_capacity = models.PositiveIntegerField(default=0)
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
    is_active = models.BooleanField(default=True, db_index=True)

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
        return self.is_active and self.is_accreditation_current

    @property
    def profile_complete(self) -> bool:
        required_values = [
            self.facility_name,
            self.facility_type,
            self.ownership_type,
            self.license_number,
            self.address,
            self.state_id,
            self.contact_person,
            self.phone,
            self.email,
        ]
        return all(bool(value) for value in required_values)

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
    has_valid_facility_license = models.BooleanField(default=False)
    has_laboratory_capacity = models.BooleanField(default=False)
    has_valid_doctor_credentials = models.BooleanField(default=False)
    has_valid_lab_staff_credentials = models.BooleanField(default=False)
    has_infection_prevention_readiness = models.BooleanField(default=False)
    has_confidentiality_policy = models.BooleanField(default=False)
    supporting_document = models.FileField(upload_to="facility_accreditation/", blank=True)
    is_renewal = models.BooleanField(default=False, db_index=True)
    renewal_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="renewal_applications",
    )
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
                self.has_valid_facility_license,
                self.has_laboratory_capacity,
                self.has_valid_doctor_credentials,
                self.has_valid_lab_staff_credentials,
                self.has_infection_prevention_readiness,
                self.has_confidentiality_policy,
            ]
        )


class FacilityDocument(BaseModel):
    facility = models.ForeignKey(
        MedicalFacility,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    accreditation_application = models.ForeignKey(
        FacilityAccreditationApplication,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documents",
    )
    document_type = models.CharField(max_length=64, choices=FacilityDocumentType.choices, db_index=True)
    file = models.FileField(upload_to="facility_documents/")
    status = models.CharField(
        max_length=32,
        choices=FacilityDocumentStatus.choices,
        default=FacilityDocumentStatus.UPLOADED,
        db_index=True,
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_facility_documents",
    )
    review_comment = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["facility"], name="facilities__facilit_22951e_idx"),
            models.Index(fields=["accreditation_application"], name="facilities__accredi_5a2482_idx"),
            models.Index(fields=["document_type"], name="facilities__documen_365773_idx"),
            models.Index(fields=["status"], name="facilities__status_931409_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.facility.facility_name} - {self.document_type}"


class FacilityStaffType(models.TextChoices):
    FACILITY_ADMIN = "facility_admin", "Facility Admin"
    DOCTOR = "doctor", "Doctor"
    LAB_STAFF = "lab_staff", "Lab Staff"
    RECORDS_STAFF = "records_staff", "Medical Records Staff"
    FINANCE_USER = "finance_user", "Finance/Settlement User"
    VIEWER = "viewer", "Viewer"


class FacilityProfessionalCategory(models.TextChoices):
    ADMIN = "admin", "Admin"
    DOCTOR = "doctor", "Doctor"
    LAB_TECHNICIAN = "lab_technician", "Lab Technician"
    LAB_SCIENTIST = "lab_scientist", "Lab Scientist"
    LAB_SUPERVISOR = "lab_supervisor", "Lab Supervisor"
    FRONT_DESK = "front_desk", "Front Desk"
    FINANCE = "finance", "Finance"
    RECORDS = "records", "Records"
    COMPLIANCE = "compliance", "Compliance"
    VIEWER = "viewer", "Viewer / Auditor"


class FacilityTeamMemberStatus(models.TextChoices):
    INVITED = "invited", "Invited"
    PENDING_PROFILE = "pending_profile", "Pending Profile Completion"
    PENDING_LICENSE_VERIFICATION = "pending_license_verification", "Pending License Verification"
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    REMOVED = "removed", "Removed"


class FacilityProfessionalVerificationStatus(models.TextChoices):
    NOT_REQUIRED = "not_required", "Not Required"
    PENDING = "pending", "Pending"
    VERIFIED = "verified", "Verified"
    REJECTED = "rejected", "Rejected"


class FacilityRole(BaseModel):
    facility = models.ForeignKey(
        MedicalFacility,
        on_delete=models.CASCADE,
        related_name="facility_roles",
    )
    organization_role = models.ForeignKey(
        "organizations.Role",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="facility_roles",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    professional_category = models.CharField(
        max_length=32,
        choices=FacilityProfessionalCategory.choices,
        default=FacilityProfessionalCategory.ADMIN,
        db_index=True,
    )
    is_system_default = models.BooleanField(default=False, db_index=True)
    is_custom = models.BooleanField(default=False, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="facility_roles_created",
    )

    class Meta:
        ordering = ["facility__facility_name", "name"]
        constraints = [
            models.UniqueConstraint(fields=["facility", "name"], name="unique_facility_role_name"),
        ]
        indexes = [
            models.Index(fields=["facility"], name="facilities__facilit_fc7708_idx"),
            models.Index(fields=["professional_category"], name="facilities__profess_69f176_idx"),
            models.Index(fields=["organization_role"], name="facilities__organiz_16d263_idx"),
            models.Index(fields=["is_system_default"], name="facilities__is_syst_61ff47_idx"),
            models.Index(fields=["is_custom"], name="facilities__is_cust_2b444e_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.facility.facility_name} / {self.name}"


class FacilityRolePermission(BaseModel):
    role = models.ForeignKey(
        FacilityRole,
        on_delete=models.CASCADE,
        related_name="permissions",
    )
    permission_key = models.CharField(max_length=150, db_index=True)
    allowed = models.BooleanField(default=True)

    class Meta:
        ordering = ["role__name", "permission_key"]
        constraints = [
            models.UniqueConstraint(fields=["role", "permission_key"], name="unique_facility_role_permission"),
        ]
        indexes = [
            models.Index(fields=["role"], name="facilities__role_id_ce2b6d_idx"),
            models.Index(fields=["permission_key"], name="facilities__permiss_8f7a6d_idx"),
            models.Index(fields=["allowed"], name="facilities__allowed_6e752c_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.role}: {self.permission_key}"


class FacilityStaffProfile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="facility_staff_profile",
    )
    facility = models.ForeignKey(
        MedicalFacility,
        on_delete=models.CASCADE,
        related_name="staff_profiles",
    )
    department = models.ForeignKey(
        "organizations.OrganizationUnit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="facility_staff_profiles",
    )
    role = models.ForeignKey(
        FacilityRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_members",
    )
    staff_type = models.CharField(max_length=32, choices=FacilityStaffType.choices, db_index=True)
    professional_category = models.CharField(
        max_length=32,
        choices=FacilityProfessionalCategory.choices,
        default=FacilityProfessionalCategory.ADMIN,
        db_index=True,
    )
    status = models.CharField(
        max_length=40,
        choices=FacilityTeamMemberStatus.choices,
        default=FacilityTeamMemberStatus.ACTIVE,
        db_index=True,
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="facility_team_members_invited",
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    professional_registration_number = models.CharField(max_length=120, blank=True)
    digital_signature_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["user__email"]
        indexes = [
            models.Index(fields=["facility"], name="facilities__facilit_bc249d_idx"),
            models.Index(fields=["department"], name="facilities__departm_966049_idx"),
            models.Index(fields=["role"], name="facilities__role_id_bf93ef_idx"),
            models.Index(fields=["staff_type"], name="facilities__staff_t_bcbacd_idx"),
            models.Index(fields=["professional_category"], name="facilities__profess_27de17_idx"),
            models.Index(fields=["status"], name="facilities__status_5d4a6c_idx"),
            models.Index(fields=["is_active"], name="facilities__is_acti_834508_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.facility.facility_name}"


class FacilityInvitation(BaseModel):
    facility = models.ForeignKey(
        MedicalFacility,
        on_delete=models.CASCADE,
        related_name="team_invitations",
    )
    invite = models.OneToOneField(
        "accounts.UserInvite",
        on_delete=models.CASCADE,
        related_name="facility_invitation",
    )
    role = models.ForeignKey(
        FacilityRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invitations",
    )
    professional_category = models.CharField(
        max_length=32,
        choices=FacilityProfessionalCategory.choices,
        default=FacilityProfessionalCategory.ADMIN,
        db_index=True,
    )
    status = models.CharField(
        max_length=40,
        choices=FacilityTeamMemberStatus.choices,
        default=FacilityTeamMemberStatus.INVITED,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["facility"], name="facilities__facilit_fea6bf_idx"),
            models.Index(fields=["role"], name="facilities__role_id_99d0c1_idx"),
            models.Index(fields=["professional_category"], name="facilities__profess_b29385_idx"),
            models.Index(fields=["status"], name="facilities__status_32ec5d_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.invite.email} -> {self.facility.facility_name}"


class FacilityProfessionalProfile(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="facility_professional_profiles",
    )
    facility = models.ForeignKey(
        MedicalFacility,
        on_delete=models.CASCADE,
        related_name="professional_profiles",
    )
    team_member = models.OneToOneField(
        FacilityStaffProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="professional_profile",
    )
    professional_category = models.CharField(
        max_length=32,
        choices=FacilityProfessionalCategory.choices,
        db_index=True,
    )
    license_number = models.CharField(max_length=120, blank=True)
    license_issuing_body = models.CharField(max_length=255, blank=True)
    license_document_url = models.URLField(blank=True)
    verification_status = models.CharField(
        max_length=32,
        choices=FacilityProfessionalVerificationStatus.choices,
        default=FacilityProfessionalVerificationStatus.NOT_REQUIRED,
        db_index=True,
    )

    class Meta:
        ordering = ["facility__facility_name", "user__email"]
        constraints = [
            models.UniqueConstraint(fields=["user", "facility"], name="unique_facility_professional_profile"),
        ]
        indexes = [
            models.Index(fields=["user"], name="facilities__user_id_1f81a0_idx"),
            models.Index(fields=["facility"], name="facilities__facilit_5e24b6_idx"),
            models.Index(fields=["team_member"], name="facilities__team_me_ab8053_idx"),
            models.Index(fields=["professional_category"], name="facilities__profess_1dcac7_idx"),
            models.Index(fields=["verification_status"], name="facilities__verific_5b80bd_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user} / {self.professional_category}"
