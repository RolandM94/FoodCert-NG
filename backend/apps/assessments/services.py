from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import UserRole
from apps.assessments.models import (
    AssessmentStatus,
    FitnessDecision,
    HealthDeclaration,
    MedicalAssessment,
    PhysicalExamination,
    StepStatus,
)
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.nin_verification.models import NINVerificationStatus
from apps.payments.models import PaymentStatus


def ensure_approved_facility(facility):
    if not facility.can_conduct_assessments:
        raise ValidationError("Only approved facilities can conduct medical assessments.")


def ensure_doctor_for_facility(user, facility):
    if user.role != UserRole.DOCTOR:
        raise PermissionDenied("Only doctors can perform this assessment action.")
    if user.organization_id != facility.organization_id:
        raise PermissionDenied("Doctors can only act for their own facility.")


def ensure_clinical_staff_for_facility(user, facility):
    if user.role not in {UserRole.DOCTOR, UserRole.LAB_STAFF}:
        raise PermissionDenied("Only facility clinical staff can perform this action.")
    if user.organization_id != facility.organization_id:
        raise PermissionDenied("Clinical staff can only act for their own facility.")


class AssessmentService:
    @classmethod
    @transaction.atomic
    def create_assessment(cls, *, food_handler, facility, payment_transaction=None, appointment=None, actor=None):
        ensure_approved_facility(facility)
        if payment_transaction and payment_transaction.status == PaymentStatus.SUCCESS:
            status = AssessmentStatus.PAYMENT_CONFIRMED
        else:
            status = AssessmentStatus.PAYMENT_PENDING
        assessment = MedicalAssessment.objects.create(
            food_handler=food_handler,
            employer=food_handler.employer,
            facility=facility,
            appointment=appointment,
            assessment_date=appointment.appointment_date if appointment else None,
            payment_transaction=payment_transaction,
            status=status,
        )
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={"event": "assessment_created", "status": status},
        )
        return assessment

    @classmethod
    @transaction.atomic
    def submit_declaration(cls, *, assessment, data, actor):
        if actor.role == UserRole.FOOD_HANDLER and assessment.food_handler.user_id != actor.id:
            raise PermissionDenied("You can only submit your own declaration.")
        declaration, _ = HealthDeclaration.objects.update_or_create(
            assessment=assessment,
            defaults={**data, "submitted_at": timezone.now()},
        )
        declaration.risk_flag = declaration.calculate_risk_flag()
        declaration.save(update_fields=["risk_flag", "updated_at"])
        assessment.declaration_status = StepStatus.SUBMITTED
        assessment.status = AssessmentStatus.DECLARATION_SUBMITTED
        assessment.save(update_fields=["declaration_status", "status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={"event": "declaration_submitted", "risk_flag": declaration.risk_flag},
        )
        return declaration

    @classmethod
    @transaction.atomic
    def validate_declaration(cls, *, declaration, doctor):
        assessment = declaration.assessment
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        declaration.validated_by_doctor = doctor
        declaration.validated_at = timezone.now()
        declaration.save(update_fields=["validated_by_doctor", "validated_at", "updated_at"])
        assessment.doctor = doctor
        assessment.declaration_status = StepStatus.VALIDATED
        assessment.status = AssessmentStatus.DECLARATION_VALIDATED
        assessment.save(update_fields=["doctor", "declaration_status", "status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=doctor, target=assessment, metadata={"event": "declaration_validated"})
        return declaration

    @classmethod
    @transaction.atomic
    def complete_physical_exam(cls, *, assessment, doctor, data):
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        exam, _ = PhysicalExamination.objects.update_or_create(
            assessment=assessment,
            defaults={**data, "examined_by": doctor, "examined_at": timezone.now()},
        )
        assessment.doctor = doctor
        assessment.physical_exam_status = StepStatus.COMPLETED
        assessment.status = AssessmentStatus.PHYSICAL_EXAM_COMPLETED
        assessment.save(update_fields=["doctor", "physical_exam_status", "status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=doctor, target=assessment, metadata={"event": "physical_exam_completed"})
        return exam

    @classmethod
    def has_verified_identity(cls, assessment) -> bool:
        return assessment.food_handler.nin_verifications.filter(
            status__in=[NINVerificationStatus.VERIFIED, NINVerificationStatus.OVERRIDE_APPROVED]
        ).exists()

    @classmethod
    def validate_final_decision_ready(cls, assessment, doctor):
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        if not assessment.payment_transaction or assessment.payment_transaction.status != PaymentStatus.SUCCESS:
            raise ValidationError("Assessment payment must be successful before a final decision.")
        if not cls.has_verified_identity(assessment):
            raise ValidationError("Food handler NIN must be verified or override-approved before final decision.")
        if assessment.declaration_status != StepStatus.VALIDATED:
            raise ValidationError("Health declaration must be doctor-validated before final decision.")
        if assessment.physical_exam_status != StepStatus.COMPLETED:
            raise ValidationError("Physical examination must be completed before final decision.")
        if assessment.lab_status != StepStatus.REVIEWED:
            raise ValidationError("Required lab tests must be reviewed before final decision.")
        if assessment.vaccination_status != StepStatus.REVIEWED:
            raise ValidationError("Vaccination status must be reviewed before final decision.")

    @classmethod
    @transaction.atomic
    def set_fitness_decision(cls, *, assessment, doctor, final_decision, doctor_notes="", return_to_work_date=None):
        cls.validate_final_decision_ready(assessment, doctor)
        if final_decision == FitnessDecision.RETURN_TO_WORK_ON_DATE and not return_to_work_date:
            raise ValidationError("Return-to-work date is required for this decision.")
        assessment.doctor = doctor
        assessment.final_decision = final_decision
        assessment.return_to_work_date = return_to_work_date
        assessment.doctor_notes = doctor_notes
        assessment.signed_at = timezone.now()
        if final_decision == FitnessDecision.FIT:
            assessment.status = AssessmentStatus.FIT
        elif final_decision == FitnessDecision.TEMPORARILY_NOT_FIT:
            assessment.status = AssessmentStatus.TEMPORARILY_NOT_FIT
        elif final_decision == FitnessDecision.NOT_FIT:
            assessment.status = AssessmentStatus.NOT_FIT
        else:
            assessment.status = AssessmentStatus.DOCTOR_DECISION_PENDING
        assessment.save(
            update_fields=[
                "doctor",
                "final_decision",
                "return_to_work_date",
                "doctor_notes",
                "signed_at",
                "status",
                "updated_at",
            ]
        )
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=assessment,
            metadata={"event": "fitness_decision", "decision": final_decision},
        )
        return assessment
