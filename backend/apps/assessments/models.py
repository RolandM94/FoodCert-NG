from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


class AppointmentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    RESCHEDULED = "rescheduled", "Rescheduled"
    CANCELLED = "cancelled", "Cancelled"
    COMPLETED = "completed", "Completed"
    NO_SHOW = "no_show", "No Show"


class AssessmentStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PAYMENT_PENDING = "payment_pending", "Payment Pending"
    PAYMENT_CONFIRMED = "payment_confirmed", "Payment Confirmed"
    APPOINTMENT_BOOKED = "appointment_booked", "Appointment Booked"
    DECLARATION_SUBMITTED = "declaration_submitted", "Declaration Submitted"
    DECLARATION_VALIDATED = "declaration_validated", "Declaration Validated"
    PHYSICAL_EXAM_COMPLETED = "physical_exam_completed", "Physical Exam Completed"
    LAB_TESTS_PENDING = "lab_tests_pending", "Lab Tests Pending"
    LAB_RESULTS_REVIEWED = "lab_results_reviewed", "Lab Results Reviewed"
    VACCINATION_REVIEWED = "vaccination_reviewed", "Vaccination Reviewed"
    DOCTOR_DECISION_PENDING = "doctor_decision_pending", "Doctor Decision Pending"
    FIT = "fit", "Fit"
    TEMPORARILY_NOT_FIT = "temporarily_not_fit", "Temporarily Not Fit"
    NOT_FIT = "not_fit", "Not Fit"
    SUBMITTED_FOR_STATE_VALIDATION = "submitted_for_state_validation", "Submitted For State Validation"
    STATE_CLARIFICATION_REQUESTED = "state_clarification_requested", "State Clarification Requested"
    STATE_CLARIFICATION_RESPONDED = "state_clarification_responded", "State Clarification Responded"
    APPROVED_BY_STATE = "approved_by_state", "Approved By State"
    REJECTED_BY_STATE = "rejected_by_state", "Rejected By State"
    CERTIFICATE_ISSUED = "certificate_issued", "Certificate Issued"
    CLOSED = "closed", "Closed"


class StepStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SUBMITTED = "submitted", "Submitted"
    VALIDATED = "validated", "Validated"
    COMPLETED = "completed", "Completed"
    REVIEWED = "reviewed", "Reviewed"


class FitnessDecision(models.TextChoices):
    PENDING = "pending", "Pending"
    FIT = "fit", "Fit"
    TEMPORARILY_NOT_FIT = "temporarily_not_fit", "Temporarily Not Fit"
    NOT_FIT = "not_fit", "Not Fit"
    REQUIRES_VACCINATION = "requires_vaccination", "Requires Vaccination"
    REQUIRES_LAB_TEST = "requires_lab_test", "Requires Lab Test"
    REQUIRES_RECHECK = "requires_recheck", "Requires Recheck"
    REQUIRES_TREATMENT = "requires_treatment", "Requires Treatment"
    REQUIRES_PUBLIC_HEALTH_CLEARANCE = "requires_public_health_clearance", "Requires Public Health Clearance"
    RETURN_TO_WORK_ON_DATE = "return_to_work_on_date", "Return To Work On Date"


class AssessmentFormScope(models.TextChoices):
    SYSTEM = "system", "System"
    NATIONAL = "national", "National"
    STATE = "state", "State"
    FACILITY = "facility", "Facility"


class AssessmentFormStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING_APPROVAL = "pending_approval", "Pending Approval"
    APPROVED = "approved", "Approved"
    PUBLISHED = "published", "Published"
    ACTIVE = "active", "Active"
    RETIRED = "retired", "Retired"
    REJECTED = "rejected", "Rejected"
    ARCHIVED = "archived", "Archived"


class AssessmentFormType(models.TextChoices):
    HEALTH_DECLARATION = "health_declaration", "Health Declaration"
    FACILITY_INTAKE = "facility_intake", "Facility Intake"
    DOCTOR_CLINICAL_REVIEW = "doctor_clinical_review", "Doctor Clinical Review"
    LAB_RESULT = "lab_result", "Lab Result"
    VACCINATION_REVIEW = "vaccination_review", "Vaccination Review"
    RETURN_TO_WORK = "return_to_work", "Return To Work"
    ILLNESS_REPORT = "illness_report", "Illness Report"
    STATE_VALIDATION_CHECKLIST = "state_validation_checklist", "State Validation Checklist"
    INSPECTION_SUPPORT = "inspection_support", "Inspection Support"


class AssessmentQuestionType(models.TextChoices):
    SHORT_TEXT = "short_text", "Short Text"
    LONG_TEXT = "long_text", "Long Text"
    NUMBER = "number", "Number"
    DATE = "date", "Date"
    TIME = "time", "Time"
    DATETIME = "datetime", "Date and Time"
    YES_NO = "yes_no", "Yes or No"
    SINGLE_CHOICE = "single_choice", "Single Choice"
    MULTIPLE_CHOICE = "multiple_choice", "Multiple Choice"
    CHECKBOX = "checkbox", "Checkbox Confirmation"
    DROPDOWN = "dropdown", "Dropdown"
    PHONE = "phone", "Phone Number"
    EMAIL = "email", "Email"
    FILE_UPLOAD = "file_upload", "File Upload"
    TEMPERATURE = "temperature", "Temperature"
    WEIGHT = "weight", "Weight"
    HEIGHT = "height", "Height"
    BLOOD_PRESSURE = "blood_pressure", "Blood Pressure"
    PULSE_RATE = "pulse_rate", "Pulse Rate"
    SYMPTOM_CHECKLIST = "symptom_checklist", "Symptom Checklist"
    EXPOSURE_HISTORY = "exposure_history", "Exposure History"
    VACCINATION_DATE = "vaccination_date", "Vaccination Date"
    VACCINE_DOSE = "vaccine_dose", "Vaccine Dose"
    LAB_RESULT_STATUS = "lab_result_status", "Lab Result Status"
    CLINICAL_NOTE = "clinical_note", "Clinical Note"
    DOCTOR_ONLY_NOTE = "doctor_only_note", "Doctor-only Note"
    LAB_ONLY_NOTE = "lab_only_note", "Lab-only Note"


class AssessmentPrivacyClassification(models.TextChoices):
    PUBLIC_SAFE = "public_safe", "Public Safe"
    EMPLOYER_SAFE_SUMMARY = "employer_safe_summary", "Employer Safe Summary"
    INSPECTOR_SAFE_SUMMARY = "inspector_safe_summary", "Inspector Safe Summary"
    MEDICAL_SENSITIVE = "medical_sensitive", "Medical Sensitive"
    RESTRICTED_MEDICAL = "restricted_medical", "Restricted Medical"
    INTERNAL_ADMINISTRATIVE = "internal_administrative", "Internal Administrative"
    REGULATORY_RESTRICTED = "regulatory_restricted", "Regulatory Restricted"


class AssessmentRespondentRole(models.TextChoices):
    FOOD_HANDLER = "food_handler", "Food Handler"
    DOCTOR = "doctor", "Doctor"
    LAB_STAFF = "lab_staff", "Lab Staff"
    FACILITY_STAFF = "facility_staff", "Facility Staff"
    STATE_USER = "state_user", "State User"
    INSPECTOR = "inspector", "Inspector"


class AssessmentType(models.TextChoices):
    STANDARD = "standard", "Standard New Assessment"
    RENEWAL = "renewal", "Certificate Renewal"
    RETURN_TO_WORK = "return_to_work", "Return To Work"
    HIGH_RISK = "high_risk", "High-risk Food Handler"
    OUTBREAK_RESPONSE = "outbreak_response", "Outbreak Response"


class AssessmentRequirementSetStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ACTIVE = "active", "Active"
    RETIRED = "retired", "Retired"


class AssessmentFormResponseStatus(models.TextChoices):
    NOT_STARTED = "not_started", "Not Started"
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    CLARIFICATION_REQUESTED = "clarification_requested", "Clarification Requested"
    REOPENED = "reopened", "Reopened"
    RESUBMITTED = "resubmitted", "Resubmitted"
    VALIDATED = "validated", "Validated"
    LOCKED = "locked", "Locked"
    SUPERSEDED = "superseded", "Superseded"
    ARCHIVED = "archived", "Archived"


class Appointment(BaseModel):
    food_handler = models.ForeignKey("food_handlers.FoodHandlerProfile", on_delete=models.PROTECT, related_name="appointments")
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.PROTECT, related_name="appointments")
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_appointments",
    )
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=32, choices=AppointmentStatus.choices, default=AppointmentStatus.PENDING, db_index=True)
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-appointment_date"]
        indexes = [
            models.Index(fields=["food_handler"]),
            models.Index(fields=["facility"]),
            models.Index(fields=["doctor"], name="assessments_doctor__00f435_idx"),
            models.Index(fields=["status"]),
            models.Index(fields=["appointment_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.food_handler} at {self.facility} on {self.appointment_date:%Y-%m-%d}"


class MedicalAssessment(BaseModel):
    food_handler = models.ForeignKey("food_handlers.FoodHandlerProfile", on_delete=models.PROTECT, related_name="assessments")
    employer = models.ForeignKey("employers.Employer", on_delete=models.SET_NULL, null=True, blank=True, related_name="assessments")
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.PROTECT, related_name="assessments")
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctor_assessments",
    )
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name="assessments")
    assessment_date = models.DateTimeField(null=True, blank=True)
    payment_transaction = models.ForeignKey(
        "payments.PaymentTransaction",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="medical_assessments",
    )
    assessment_type = models.CharField(max_length=32, choices=AssessmentType.choices, default=AssessmentType.STANDARD, db_index=True)
    status = models.CharField(max_length=48, choices=AssessmentStatus.choices, default=AssessmentStatus.DRAFT, db_index=True)
    declaration_status = models.CharField(max_length=32, choices=StepStatus.choices, default=StepStatus.PENDING)
    physical_exam_status = models.CharField(max_length=32, choices=StepStatus.choices, default=StepStatus.PENDING)
    lab_status = models.CharField(max_length=32, choices=StepStatus.choices, default=StepStatus.PENDING)
    vaccination_status = models.CharField(max_length=32, choices=StepStatus.choices, default=StepStatus.PENDING)
    final_decision = models.CharField(max_length=64, choices=FitnessDecision.choices, default=FitnessDecision.PENDING, db_index=True)
    return_to_work_date = models.DateField(null=True, blank=True)
    doctor_notes = models.TextField(blank=True)
    decision_draft = models.CharField(max_length=64, choices=FitnessDecision.choices, default=FitnessDecision.PENDING)
    decision_draft_return_to_work_date = models.DateField(null=True, blank=True)
    decision_draft_notes = models.TextField(blank=True)
    decision_draft_saved_at = models.DateTimeField(null=True, blank=True)
    digital_signature_hash = models.CharField(max_length=128, blank=True)
    signed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="signed_medical_assessments",
    )
    signed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["food_handler"]),
            models.Index(fields=["employer"]),
            models.Index(fields=["facility"]),
            models.Index(fields=["doctor"]),
            models.Index(fields=["status"]),
            models.Index(fields=["final_decision"]),
            models.Index(fields=["signed_at"], name="assessments_signed__7338f5_idx"),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.food_handler} - {self.facility} - {self.status}"

    @property
    def can_request_certificate(self) -> bool:
        return self.final_decision == FitnessDecision.FIT and self.signed_at is not None


class AssessmentFormTemplate(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    form_type = models.CharField(max_length=64, choices=AssessmentFormType.choices, db_index=True)
    scope = models.CharField(max_length=16, choices=AssessmentFormScope.choices, db_index=True)
    state = models.ForeignKey("locations.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="assessment_form_templates")
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.SET_NULL, null=True, blank=True, related_name="assessment_form_templates")
    owner_organization = models.ForeignKey("organizations.Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="assessment_form_templates")
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=32, choices=AssessmentFormStatus.choices, default=AssessmentFormStatus.DRAFT, db_index=True)
    is_mandatory = models.BooleanField(default=False, db_index=True)
    requires_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_assessment_form_templates")
    approved_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_assessment_form_templates")
    parent_template = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="versions")

    class Meta:
        ordering = ["name", "-version"]
        indexes = [
            models.Index(fields=["scope", "status"], name="assess_form_scope_status_idx"),
            models.Index(fields=["form_type", "status"], name="assess_form_type_status_idx"),
            models.Index(fields=["state", "status"], name="assess_form_state_status_idx"),
            models.Index(fields=["facility", "status"], name="assess_form_facility_idx"),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(version__gte=1), name="assessments_form_version_positive"),
        ]

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"

    def clean(self):
        super().clean()
        errors = {}
        if self.scope in {AssessmentFormScope.SYSTEM, AssessmentFormScope.NATIONAL} and (self.state_id or self.facility_id):
            errors["scope"] = "System and national forms cannot be assigned to a State or facility."
        if self.scope == AssessmentFormScope.STATE and (not self.state_id or self.facility_id):
            errors["scope"] = "State forms require a State and cannot be assigned to a facility."
        if self.scope == AssessmentFormScope.FACILITY and not self.facility_id:
            errors["scope"] = "Facility forms require a medical facility."
        if self.facility_id and self.state_id and self.facility.state_id != self.state_id:
            errors["state"] = "The selected State must match the medical facility State."
        if self.effective_from and self.effective_to and self.effective_to < self.effective_from:
            errors["effective_to"] = "The effective end date cannot be earlier than the start date."
        if errors:
            raise ValidationError(errors)


class AssessmentFormSection(BaseModel):
    template = models.ForeignKey(AssessmentFormTemplate, on_delete=models.CASCADE, related_name="sections")
    key = models.SlugField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    visibility_rules = models.JSONField(default=dict, blank=True)
    required_completion = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order", "created_at"]
        constraints = [
            models.UniqueConstraint(fields=["template", "key"], name="assessments_unique_section_key"),
        ]

    def __str__(self) -> str:
        return f"{self.template} / {self.title}"


class AssessmentFormQuestion(BaseModel):
    section = models.ForeignKey(AssessmentFormSection, on_delete=models.CASCADE, related_name="questions")
    key = models.SlugField(max_length=100)
    label = models.TextField()
    help_text = models.TextField(blank=True)
    placeholder = models.CharField(max_length=255, blank=True)
    question_type = models.CharField(max_length=48, choices=AssessmentQuestionType.choices, db_index=True)
    required = models.BooleanField(default=False)
    options = models.JSONField(default=list, blank=True)
    validation_rules = models.JSONField(default=dict, blank=True)
    conditional_logic = models.JSONField(default=dict, blank=True)
    risk_flag_rules = models.JSONField(default=dict, blank=True)
    privacy_classification = models.CharField(max_length=32, choices=AssessmentPrivacyClassification.choices, db_index=True)
    respondent_role = models.CharField(max_length=32, choices=AssessmentRespondentRole.choices, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["section__sort_order", "sort_order", "created_at"]
        constraints = [
            models.UniqueConstraint(fields=["section", "key"], name="assessments_unique_question_key"),
        ]
        indexes = [
            models.Index(fields=["privacy_classification"], name="assess_question_privacy_idx"),
            models.Index(fields=["respondent_role", "is_active"], name="assess_question_role_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.section} / {self.label}"

    def clean(self):
        super().clean()
        duplicate = AssessmentFormQuestion.objects.filter(section__template=self.section.template, key=self.key)
        if self.pk:
            duplicate = duplicate.exclude(pk=self.pk)
        if duplicate.exists():
            raise ValidationError({"key": "Question keys must be unique within a form template version."})


class AssessmentRequirementSet(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scope = models.CharField(max_length=16, choices=AssessmentFormScope.choices, db_index=True)
    state = models.ForeignKey("locations.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="assessment_requirement_sets")
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.SET_NULL, null=True, blank=True, related_name="assessment_requirement_sets")
    assessment_type = models.CharField(max_length=32, choices=AssessmentType.choices, blank=True, db_index=True)
    food_handler_category = models.CharField(max_length=64, blank=True, db_index=True)
    employer_category = models.CharField(max_length=64, blank=True, db_index=True)
    illness_condition = models.CharField(max_length=64, blank=True, db_index=True)
    required_forms = models.ManyToManyField(AssessmentFormTemplate, blank=True, related_name="requirement_sets")
    required_documents = models.JSONField(default=list, blank=True)
    required_lab_tests = models.JSONField(default=list, blank=True)
    required_vaccinations = models.JSONField(default=list, blank=True)
    required_approvals = models.JSONField(default=list, blank=True)
    blocking_requirements = models.JSONField(default=list, blank=True)
    advisory_requirements = models.JSONField(default=list, blank=True)
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=16, choices=AssessmentRequirementSetStatus.choices, default=AssessmentRequirementSetStatus.DRAFT, db_index=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_assessment_requirement_sets")

    class Meta:
        ordering = ["scope", "name", "-version"]
        indexes = [
            models.Index(fields=["scope", "status"], name="assess_req_scope_status_idx"),
            models.Index(fields=["state", "status"], name="assess_req_state_status_idx"),
            models.Index(fields=["facility", "status"], name="assess_req_facility_idx"),
            models.Index(fields=["assessment_type", "status"], name="assess_req_type_status_idx"),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(version__gte=1), name="assessments_req_version_positive"),
        ]

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"

    def clean(self):
        super().clean()
        errors = {}
        if self.scope in {AssessmentFormScope.SYSTEM, AssessmentFormScope.NATIONAL} and (self.state_id or self.facility_id):
            errors["scope"] = "System and national requirement sets cannot be assigned to a State or facility."
        if self.scope == AssessmentFormScope.STATE and (not self.state_id or self.facility_id):
            errors["scope"] = "State requirement sets require a State and cannot be assigned to a facility."
        if self.scope == AssessmentFormScope.FACILITY and not self.facility_id:
            errors["scope"] = "Facility requirement sets require a medical facility."
        if self.facility_id and self.state_id and self.facility.state_id != self.state_id:
            errors["state"] = "The selected State must match the medical facility State."
        if self.effective_from and self.effective_to and self.effective_to < self.effective_from:
            errors["effective_to"] = "The effective end date cannot be earlier than the start date."
        if errors:
            raise ValidationError(errors)


class AssessmentFormResponse(BaseModel):
    assessment = models.ForeignKey(MedicalAssessment, on_delete=models.CASCADE, related_name="form_responses")
    template = models.ForeignKey(AssessmentFormTemplate, on_delete=models.PROTECT, related_name="responses")
    template_version = models.PositiveIntegerField()
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assessment_form_responses",
    )
    respondent_role = models.CharField(max_length=32, choices=AssessmentRespondentRole.choices, db_index=True)
    status = models.CharField(max_length=32, choices=AssessmentFormResponseStatus.choices, default=AssessmentFormResponseStatus.NOT_STARTED, db_index=True)
    response_data = models.JSONField(default=dict, blank=True)
    question_snapshot = models.JSONField(default=dict)
    risk_flags = models.JSONField(default=list, blank=True)
    is_required = models.BooleanField(default=True, db_index=True)
    is_locked = models.BooleanField(default=False, db_index=True)
    version = models.PositiveIntegerField(default=1)
    previous_response = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="next_versions")
    submitted_at = models.DateTimeField(null=True, blank=True)
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_assessment_form_responses",
    )
    validated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["assessment", "template__name", "-version"]
        indexes = [
            models.Index(fields=["assessment", "status"], name="assess_resp_assessment_idx"),
            models.Index(fields=["template", "template_version"], name="assess_resp_template_idx"),
            models.Index(fields=["respondent", "status"], name="assess_resp_respondent_idx"),
            models.Index(fields=["is_locked"], name="assess_resp_locked_idx"),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(template_version__gte=1), name="assessments_response_template_version_positive"),
            models.CheckConstraint(check=models.Q(version__gte=1), name="assessments_response_version_positive"),
        ]

    def __str__(self) -> str:
        return f"{self.assessment} / {self.template} response v{self.version}"


class HealthDeclaration(BaseModel):
    assessment = models.OneToOneField(MedicalAssessment, on_delete=models.CASCADE, related_name="health_declaration")
    diarrhoea_vomiting_last_7_days = models.BooleanField(default=False)
    fever_more_than_one_week = models.BooleanField(default=False)
    skin_trouble = models.BooleanField(default=False)
    boils_styes_sepsis = models.BooleanField(default=False)
    discharge_eye_ear_nose_mouth = models.BooleanField(default=False)
    recurring_skin_or_ear_infection = models.BooleanField(default=False)
    recurring_bowel_disorder = models.BooleanField(default=False)
    cholera_contact_last_5_days = models.BooleanField(default=False)
    diarrhoea_vomiting_contact_last_7_days = models.BooleanField(default=False)
    typhoid_paratyphoid_jaundice_contact_last_21_days = models.BooleanField(default=False)
    typhoid_or_paratyphoid_carrier = models.BooleanField(default=False)
    previous_or_current_typhoid = models.BooleanField(default=False)
    certified_true = models.BooleanField(default=False)
    risk_flag = models.BooleanField(default=False, db_index=True)
    version = models.PositiveIntegerField(default=1)
    is_locked = models.BooleanField(default=False, db_index=True)
    reopened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reopened_declarations",
    )
    reopened_at = models.DateTimeField(null=True, blank=True)
    reopen_reason = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    validated_by_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_declarations",
    )
    validated_at = models.DateTimeField(null=True, blank=True)
    clarification_requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_declaration_clarifications",
    )
    clarification_requested_at = models.DateTimeField(null=True, blank=True)
    clarification_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["risk_flag"]), models.Index(fields=["submitted_at"]), models.Index(fields=["is_locked"])]

    def calculate_risk_flag(self) -> bool:
        fields = [
            "diarrhoea_vomiting_last_7_days",
            "fever_more_than_one_week",
            "skin_trouble",
            "boils_styes_sepsis",
            "discharge_eye_ear_nose_mouth",
            "recurring_skin_or_ear_infection",
            "recurring_bowel_disorder",
            "cholera_contact_last_5_days",
            "diarrhoea_vomiting_contact_last_7_days",
            "typhoid_paratyphoid_jaundice_contact_last_21_days",
            "typhoid_or_paratyphoid_carrier",
            "previous_or_current_typhoid",
        ]
        return any(getattr(self, field) for field in fields)


class PhysicalExamination(BaseModel):
    assessment = models.OneToOneField(MedicalAssessment, on_delete=models.CASCADE, related_name="physical_examination")
    fever = models.BooleanField(default=False)
    jaundice = models.BooleanField(default=False)
    skin_infection = models.BooleanField(default=False)
    boils_styes_sepsis = models.BooleanField(default=False)
    discharge = models.BooleanField(default=False)
    diarrhoea = models.BooleanField(default=False)
    vomiting = models.BooleanField(default=False)
    sore_throat_with_fever = models.BooleanField(default=False)
    cough_or_flu = models.BooleanField(default=False)
    known_typhoid_carrier_history = models.BooleanField(default=False)
    other_notes = models.TextField(blank=True)
    risk_flag = models.BooleanField(default=False, db_index=True)
    is_completed = models.BooleanField(default=False, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    examined_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="physical_examinations")
    examined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-examined_at"]
        indexes = [models.Index(fields=["examined_by"]), models.Index(fields=["examined_at"]), models.Index(fields=["risk_flag"]), models.Index(fields=["is_completed"])]

    def calculate_risk_flag(self) -> bool:
        fields = [
            "fever",
            "jaundice",
            "skin_infection",
            "boils_styes_sepsis",
            "discharge",
            "diarrhoea",
            "vomiting",
            "sore_throat_with_fever",
            "cough_or_flu",
            "known_typhoid_carrier_history",
        ]
        return any(getattr(self, field) for field in fields)
