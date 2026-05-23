from django.conf import settings
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
