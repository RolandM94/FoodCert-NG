import hashlib

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.accounts.models import UserRole
from apps.assessments.models import (
    AssessmentStatus,
    AppointmentStatus,
    FitnessDecision,
    HealthDeclaration,
    MedicalAssessment,
    PhysicalExamination,
    StepStatus,
)
from apps.audit.models import AuditAction, AuditLog
from apps.audit.services import log_action
from apps.food_handlers.models import FoodHandlerStatus
from apps.illness.models import ClearanceStatus, IllnessReport, SuspectedCondition
from apps.nin_verification.models import NINVerificationStatus
from apps.notifications.models import Notification, NotificationChannel, NotificationType
from apps.payments.models import PaymentStatus
from apps.policy.models import NationalPolicyConfig
from apps.reports.models import GeneratedReport, GeneratedReportStatus, ReportFormat, ReportType


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


def ensure_facility_admin_for_facility(user, facility):
    if user.role != UserRole.FACILITY_ADMIN:
        raise PermissionDenied("Only facility admins can manage facility appointments.")
    if user.organization_id != facility.organization_id:
        raise PermissionDenied("Facility admins can only manage their own facility.")


def ensure_assigned_doctor_for_assessment(user, assessment):
    ensure_doctor_for_facility(user, assessment.facility)
    if assessment.doctor_id != user.id:
        raise PermissionDenied("Doctors can only perform clinical actions on assigned assessments.")


class AssessmentService:
    CLINICAL_STATUSES = {
        AssessmentStatus.DECLARATION_SUBMITTED,
        AssessmentStatus.DECLARATION_VALIDATED,
        AssessmentStatus.PHYSICAL_EXAM_COMPLETED,
        AssessmentStatus.LAB_TESTS_PENDING,
        AssessmentStatus.LAB_RESULTS_REVIEWED,
        AssessmentStatus.VACCINATION_REVIEWED,
        AssessmentStatus.DOCTOR_DECISION_PENDING,
        AssessmentStatus.FIT,
        AssessmentStatus.TEMPORARILY_NOT_FIT,
        AssessmentStatus.NOT_FIT,
        AssessmentStatus.SUBMITTED_FOR_STATE_VALIDATION,
        AssessmentStatus.CERTIFICATE_ISSUED,
    }

    TERMINAL_STATUSES = {
        AssessmentStatus.FIT,
        AssessmentStatus.TEMPORARILY_NOT_FIT,
        AssessmentStatus.NOT_FIT,
        AssessmentStatus.SUBMITTED_FOR_STATE_VALIDATION,
        AssessmentStatus.CERTIFICATE_ISSUED,
        AssessmentStatus.CLOSED,
    }

    TIMELINE_LABELS = {
        "assessment_created": "Assessment created",
        "assessment_cancelled": "Assessment cancelled",
        "assessment_closed": "Assessment closed",
        "assessment_status_checked": "Prerequisite status checked",
        "appointment_created": "Appointment created",
        "appointment_updated": "Appointment updated",
        "declaration_draft_saved": "Declaration draft saved",
        "declaration_submitted": "Declaration submitted",
        "declaration_validated": "Declaration validated",
        "declaration_clarification_requested": "Declaration clarification requested",
        "declaration_reopened": "Declaration reopened",
        "physical_exam_draft_saved": "Physical exam draft saved",
        "physical_exam_completed": "Physical exam completed",
        "lab_tests_requested": "Lab tests requested",
        "lab_sample_collected": "Lab sample collected",
        "lab_result_recorded": "Lab result recorded",
        "lab_result_document_uploaded": "Lab result document uploaded",
        "lab_submitted_to_doctor": "Lab submitted to doctor",
        "lab_result_submitted_to_doctor": "Lab submitted to doctor",
        "lab_result_reviewed": "Lab result reviewed",
        "lab_repeat_requested": "Repeat lab test requested",
        "vaccination_reviewed": "Vaccination reviewed",
        "fitness_decision_draft_saved": "Decision draft saved",
        "fitness_decision": "Final fitness decision signed",
        "medical_report_generated": "Medical report generated",
        "return_to_work_case_linked": "Return-to-work workflow linked",
        "facility_submitted_assessment_to_state": "Submitted to State validation",
        "facility_certificate_clarification_responded": "State clarification responded",
        "certificate_request_clarification_requested": "State clarification requested",
        "certificate_request_approved": "State certificate request approved",
        "certificate_request_rejected": "State certificate request rejected",
        "certificate_issued": "Certificate issued",
        "assessment_detail_read": "Assessment detail viewed",
        "doctor_assessment_detail_read": "Doctor assessment detail viewed",
        "assessment_audit_timeline_viewed": "Audit timeline viewed",
        "physical_exam_read": "Physical exam viewed",
        "lab_result_read": "Lab result viewed",
        "assessment_report_read": "Assessment report viewed",
    }

    @classmethod
    def timeline_label(cls, log):
        event = (log.metadata or {}).get("event", "")
        if event in cls.TIMELINE_LABELS:
            return cls.TIMELINE_LABELS[event]
        return event.replace("_", " ").title() if event else log.get_action_display()

    @classmethod
    def assessment_timeline(cls, *, assessment, user):
        cls.ensure_assessment_report_access(assessment=assessment, user=user)
        role = getattr(user, "role", "")
        if role in {UserRole.FOOD_HANDLER, UserRole.EMPLOYER}:
            raise PermissionDenied("You cannot access the assessment audit timeline.")
        related_ids = {str(assessment.id)}
        declaration = getattr(assessment, "health_declaration", None)
        if declaration:
            related_ids.add(str(declaration.id))
        exam = getattr(assessment, "physical_examination", None)
        if exam:
            related_ids.add(str(exam.id))
        related_ids.update(str(item.id) for item in assessment.lab_tests.all())
        related_ids.update(str(item.id) for item in assessment.vaccinations.all())
        certificate_request = getattr(assessment, "certificate_request", None)
        if certificate_request:
            related_ids.add(str(certificate_request.id))
        certificate = getattr(assessment, "certificate", None)
        if certificate:
            related_ids.add(str(certificate.id))

        logs = (
            AuditLog.objects.select_related("actor")
            .filter(Q(target_id__in=related_ids) | Q(metadata__assessment_id=str(assessment.id)))
            .order_by("created_at", "id")
        )
        return [
            {
                "id": log.id,
                "action": log.action,
                "event": (log.metadata or {}).get("event", ""),
                "label": cls.timeline_label(log),
                "actor_name": (log.actor.get_full_name() or log.actor.email) if log.actor else "",
                "actor_role": getattr(log.actor, "role", "") if log.actor else "",
                "target_type": log.target_type,
                "target_id": log.target_id,
                "metadata": log.metadata or {},
                "created_at": log.created_at,
            }
            for log in logs
        ]

    @classmethod
    def _active_policy(cls):
        return NationalPolicyConfig.objects.order_by("-updated_at").first()

    @classmethod
    def payment_required(cls) -> bool:
        policy = cls._active_policy()
        return True if policy is None else policy.payment_before_assessment_required

    @classmethod
    def profile_complete(cls, assessment) -> bool:
        food_handler = assessment.food_handler
        required_values = [
            food_handler.full_name,
            food_handler.date_of_birth,
            food_handler.gender,
            food_handler.nin,
            food_handler.phone,
            food_handler.email,
            food_handler.home_address,
            food_handler.state_id,
            food_handler.food_handler_category,
        ]
        return all(bool(value) for value in required_values)

    @classmethod
    def has_confirmed_payment(cls, assessment) -> bool:
        return bool(assessment.payment_transaction and assessment.payment_transaction.status == PaymentStatus.SUCCESS)

    @classmethod
    def has_ready_appointment(cls, assessment) -> bool:
        if not assessment.appointment_id:
            return False
        return assessment.appointment.status in {
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.COMPLETED,
        }

    @classmethod
    def _blocker(cls, code, label, detail, *, blocking=True):
        return {
            "code": code,
            "label": label,
            "detail": detail,
            "blocking": blocking,
        }

    @classmethod
    def prerequisite_blockers(cls, assessment):
        blockers = []
        warnings = []

        if not cls.profile_complete(assessment):
            blockers.append(
                cls._blocker(
                    "profile_incomplete",
                    "Profile incomplete",
                    "Complete the food handler profile before the assessment can continue.",
                )
            )
        if not cls.has_verified_identity(assessment):
            blockers.append(
                cls._blocker(
                    "nin_unverified",
                    "NIN not verified",
                    "Verify or approve an override for the food handler NIN before clinical sign-off.",
                )
            )
        if not assessment.facility.can_conduct_assessments:
            blockers.append(
                cls._blocker(
                    "facility_not_current",
                    "Facility accreditation not current",
                    "The selected facility must be active and currently accredited.",
                )
            )
        if cls.payment_required() and not cls.has_confirmed_payment(assessment):
            blockers.append(
                cls._blocker(
                    "payment_required",
                    "Payment pending",
                    "Successful assessment payment is required before the appointment can be confirmed.",
                )
            )
        if assessment.status != AssessmentStatus.PAYMENT_PENDING and not cls.has_ready_appointment(assessment):
            blockers.append(
                cls._blocker(
                    "appointment_required",
                    "Appointment not confirmed",
                    "Book and confirm an appointment before clinical workflow begins.",
                )
            )
        if assessment.status in cls.CLINICAL_STATUSES and not assessment.doctor_id:
            blockers.append(
                cls._blocker(
                    "doctor_unassigned",
                    "Doctor not assigned",
                    "Assign an authorized doctor from the assessment facility.",
                )
            )
        if assessment.doctor_id and assessment.doctor.organization_id != assessment.facility.organization_id:
            blockers.append(
                cls._blocker(
                    "doctor_not_authorized",
                    "Doctor not authorized",
                    "The assigned doctor must belong to the assessment facility organization.",
                )
            )
        if assessment.employer_id and not assessment.food_handler.business_branch_id:
            warnings.append(
                cls._blocker(
                    "branch_missing",
                    "Branch not linked",
                    "Linking the handler to a business branch improves employer compliance reporting.",
                    blocking=False,
                )
            )
        if IllnessReport.objects.filter(food_handler=assessment.food_handler).exclude(
            clearance_status__in=[ClearanceStatus.CLEARED, ClearanceStatus.REJECTED]
        ).exists():
            blockers.append(
                cls._blocker(
                    "unresolved_illness",
                    "Unresolved illness report",
                    "Resolve active illness or exclusion records before final fitness sign-off.",
                )
            )
        return blockers, warnings

    @classmethod
    def status_steps(cls, assessment):
        step_values = [
            ("profile", "Profile", cls.profile_complete(assessment)),
            ("identity", "Identity", cls.has_verified_identity(assessment)),
            ("payment", "Payment", cls.has_confirmed_payment(assessment) or not cls.payment_required()),
            ("appointment", "Appointment", cls.has_ready_appointment(assessment)),
            ("declaration", "Declaration", assessment.declaration_status in {StepStatus.SUBMITTED, StepStatus.VALIDATED}),
            ("physical_exam", "Physical exam", assessment.physical_exam_status == StepStatus.COMPLETED),
            ("lab", "Lab review", assessment.lab_status == StepStatus.REVIEWED),
            ("vaccination", "Vaccination review", assessment.vaccination_status == StepStatus.REVIEWED),
            ("decision", "Doctor decision", assessment.final_decision != FitnessDecision.PENDING and assessment.signed_at is not None),
            ("certificate", "Certificate", assessment.status == AssessmentStatus.CERTIFICATE_ISSUED),
        ]
        return [
            {"code": code, "label": label, "status": "complete" if complete else "pending"}
            for code, label, complete in step_values
        ]

    @classmethod
    def next_action(cls, assessment, blockers):
        blocker_actions = {
            "profile_incomplete": ("complete_profile", "Complete food handler profile"),
            "nin_unverified": ("verify_nin", "Verify NIN"),
            "facility_not_current": ("select_facility", "Use an approved facility"),
            "payment_required": ("complete_payment", "Complete payment"),
            "appointment_required": ("confirm_appointment", "Confirm appointment"),
            "doctor_unassigned": ("assign_doctor", "Assign doctor"),
            "doctor_not_authorized": ("assign_doctor", "Assign authorized doctor"),
            "unresolved_illness": ("resolve_illness", "Resolve illness case"),
        }
        for blocker in blockers:
            action = blocker_actions.get(blocker["code"])
            if action:
                return {"code": action[0], "label": action[1]}

        if assessment.status == AssessmentStatus.CLOSED:
            return {"code": "closed", "label": "Assessment closed"}
        if assessment.declaration_status == StepStatus.PENDING:
            return {"code": "submit_declaration", "label": "Submit health declaration"}
        if assessment.declaration_status == StepStatus.SUBMITTED:
            return {"code": "validate_declaration", "label": "Doctor validates declaration"}
        if assessment.physical_exam_status == StepStatus.PENDING:
            return {"code": "complete_physical_exam", "label": "Complete physical examination"}
        if assessment.lab_status != StepStatus.REVIEWED:
            return {"code": "complete_lab_workflow", "label": "Complete lab workflow"}
        if assessment.vaccination_status != StepStatus.REVIEWED:
            return {"code": "review_vaccination", "label": "Review vaccination status"}
        if assessment.final_decision == FitnessDecision.PENDING or not assessment.signed_at:
            return {"code": "finalize_decision", "label": "Sign final fitness decision"}
        if assessment.status == AssessmentStatus.FIT:
            return {"code": "request_certificate", "label": "Request certificate"}
        if assessment.status == AssessmentStatus.SUBMITTED_FOR_STATE_VALIDATION:
            return {"code": "await_state_validation", "label": "Await State validation"}
        if assessment.status == AssessmentStatus.CERTIFICATE_ISSUED:
            return {"code": "download_certificate", "label": "Download certificate"}
        return {"code": "monitor", "label": "Monitor assessment"}

    @classmethod
    def status_snapshot(cls, assessment):
        blockers, warnings = cls.prerequisite_blockers(assessment)
        return {
            "assessment": str(assessment.id),
            "current_status": assessment.status,
            "current_status_label": assessment.get_status_display(),
            "stage": assessment.status,
            "stage_label": assessment.get_status_display(),
            "next_action": cls.next_action(assessment, blockers),
            "blockers": blockers,
            "warnings": warnings,
            "steps": cls.status_steps(assessment),
            "can_cancel": assessment.status not in cls.TERMINAL_STATUSES,
            "can_close": assessment.status != AssessmentStatus.CLOSED,
            "can_proceed": not blockers,
            "updated_at": assessment.updated_at.isoformat() if assessment.updated_at else "",
        }

    @classmethod
    def ensure_can_cancel_assessment(cls, assessment, actor):
        if assessment.status in cls.TERMINAL_STATUSES:
            raise ValidationError("This assessment can no longer be cancelled.")
        if actor.role == UserRole.FOOD_HANDLER and assessment.food_handler.user_id == actor.id:
            return
        if actor.role == UserRole.EMPLOYER and getattr(actor, "employer", None) == assessment.employer:
            return
        if actor.role in {UserRole.FACILITY_ADMIN, UserRole.DOCTOR} and actor.organization_id == assessment.facility.organization_id:
            return
        if actor.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR} and actor.state_id == assessment.facility.state_id:
            return
        if actor.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return
        raise PermissionDenied("You do not have permission to cancel this assessment.")

    @classmethod
    def ensure_can_close_assessment(cls, assessment, actor):
        if assessment.status == AssessmentStatus.CLOSED:
            raise ValidationError("This assessment is already closed.")
        if actor.role in {UserRole.FACILITY_ADMIN, UserRole.DOCTOR} and actor.organization_id == assessment.facility.organization_id:
            return
        if actor.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR} and actor.state_id == assessment.facility.state_id:
            return
        if actor.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return
        raise PermissionDenied("You do not have permission to close this assessment.")

    @classmethod
    @transaction.atomic
    def cancel_assessment(cls, *, assessment, actor, reason="", notes=""):
        cls.ensure_can_cancel_assessment(assessment, actor)
        if assessment.appointment_id and assessment.appointment.status not in {AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED}:
            assessment.appointment.status = AppointmentStatus.CANCELLED
            if reason:
                assessment.appointment.reason = reason
            if notes:
                assessment.appointment.notes = notes
            assessment.appointment.save(update_fields=["status", "reason", "notes", "updated_at"])
        assessment.status = AssessmentStatus.CLOSED
        assessment.save(update_fields=["status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={"event": "assessment_cancelled", "reason": reason},
        )
        return assessment

    @classmethod
    @transaction.atomic
    def close_assessment(cls, *, assessment, actor, reason="", notes=""):
        cls.ensure_can_close_assessment(assessment, actor)
        assessment.status = AssessmentStatus.CLOSED
        assessment.save(update_fields=["status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={"event": "assessment_closed", "reason": reason, "notes": notes},
        )
        return assessment

    @classmethod
    def _appointment_assessment(cls, appointment):
        return appointment.assessments.select_related("payment_transaction", "employer", "food_handler__user").first()

    @classmethod
    def ensure_declaration_owner(cls, assessment, actor):
        if actor.role != UserRole.FOOD_HANDLER or assessment.food_handler.user_id != actor.id:
            raise PermissionDenied("You can only manage your own declaration.")

    @classmethod
    def _declaration_payload(cls, data):
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
            "certified_true",
        ]
        return {field: data.get(field, False) for field in fields}

    @classmethod
    def _get_or_create_declaration(cls, assessment):
        declaration, _ = HealthDeclaration.objects.get_or_create(assessment=assessment)
        return declaration

    @classmethod
    def _notify_appointment_change(cls, *, appointment, event, actor):
        assessment = cls._appointment_assessment(appointment)
        recipients = [appointment.food_handler.user]
        employer_user = getattr(getattr(appointment.food_handler, "employer", None), "user", None)
        if employer_user:
            recipients.append(employer_user)

        for recipient in {user for user in recipients if user}:
            Notification.objects.create(
                recipient=recipient,
                notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
                channel=NotificationChannel.IN_APP,
                subject="Appointment updated",
                body=f"Your FoodCert NG assessment appointment was {event.replace('_', ' ')}.",
                context_data={
                    "appointment_id": str(appointment.id),
                    "assessment_id": str(assessment.id) if assessment else "",
                    "event": event,
                    "actor_id": str(actor.id) if actor else "",
                },
            )

    @classmethod
    def _payment_confirmed_for_appointment(cls, appointment):
        assessment = cls._appointment_assessment(appointment)
        return bool(assessment and assessment.payment_transaction and assessment.payment_transaction.status == PaymentStatus.SUCCESS)

    @classmethod
    @transaction.atomic
    def confirm_appointment(cls, *, appointment, actor, notes=""):
        ensure_facility_admin_for_facility(actor, appointment.facility)
        ensure_approved_facility(appointment.facility)
        if not cls._payment_confirmed_for_appointment(appointment):
            raise ValidationError("Successful payment is required before confirming this appointment.")
        appointment.status = AppointmentStatus.CONFIRMED
        if notes:
            appointment.notes = notes
        appointment.save(update_fields=["status", "notes", "updated_at"])
        assessment = cls._appointment_assessment(appointment)
        if assessment:
            assessment.status = AssessmentStatus.APPOINTMENT_BOOKED
            assessment.assessment_date = appointment.appointment_date
            assessment.save(update_fields=["status", "assessment_date", "updated_at"])
        cls._notify_appointment_change(appointment=appointment, event="appointment_confirmed", actor=actor)
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=appointment, metadata={"event": "appointment_confirmed"})
        return appointment

    @classmethod
    @transaction.atomic
    def reschedule_appointment(cls, *, appointment, actor, appointment_date, reason="", notes=""):
        ensure_facility_admin_for_facility(actor, appointment.facility)
        ensure_approved_facility(appointment.facility)
        appointment.appointment_date = appointment_date
        appointment.status = AppointmentStatus.RESCHEDULED
        if reason:
            appointment.reason = reason
        if notes:
            appointment.notes = notes
        appointment.save(update_fields=["appointment_date", "status", "reason", "notes", "updated_at"])
        assessment = cls._appointment_assessment(appointment)
        if assessment:
            assessment.assessment_date = appointment.appointment_date
            assessment.save(update_fields=["assessment_date", "updated_at"])
        cls._notify_appointment_change(appointment=appointment, event="appointment_rescheduled", actor=actor)
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=appointment, metadata={"event": "appointment_rescheduled"})
        return appointment

    @classmethod
    @transaction.atomic
    def cancel_appointment(cls, *, appointment, actor, reason="", notes=""):
        ensure_facility_admin_for_facility(actor, appointment.facility)
        appointment.status = AppointmentStatus.CANCELLED
        if reason:
            appointment.reason = reason
        if notes:
            appointment.notes = notes
        appointment.save(update_fields=["status", "reason", "notes", "updated_at"])
        cls._notify_appointment_change(appointment=appointment, event="appointment_cancelled", actor=actor)
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=appointment, metadata={"event": "appointment_cancelled"})
        return appointment

    @classmethod
    @transaction.atomic
    def mark_appointment_no_show(cls, *, appointment, actor, notes=""):
        ensure_facility_admin_for_facility(actor, appointment.facility)
        appointment.status = AppointmentStatus.NO_SHOW
        if notes:
            appointment.notes = notes
        appointment.save(update_fields=["status", "notes", "updated_at"])
        cls._notify_appointment_change(appointment=appointment, event="appointment_no_show", actor=actor)
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=appointment, metadata={"event": "appointment_no_show"})
        return appointment

    @classmethod
    @transaction.atomic
    def assign_appointment_doctor(cls, *, appointment, doctor, actor):
        ensure_facility_admin_for_facility(actor, appointment.facility)
        ensure_doctor_for_facility(doctor, appointment.facility)
        appointment.doctor = doctor
        appointment.save(update_fields=["doctor", "updated_at"])
        assessment = cls._appointment_assessment(appointment)
        if assessment:
            assessment.doctor = doctor
            assessment.save(update_fields=["doctor", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=appointment,
            metadata={"event": "appointment_doctor_assigned", "doctor_id": str(doctor.id)},
        )
        return appointment

    @classmethod
    @transaction.atomic
    def assign_assessment_doctor(cls, *, assessment, doctor, actor):
        ensure_facility_admin_for_facility(actor, assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        assessment.doctor = doctor
        assessment.save(update_fields=["doctor", "updated_at"])
        if assessment.appointment_id:
            assessment.appointment.doctor = doctor
            assessment.appointment.save(update_fields=["doctor", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={"event": "assessment_doctor_assigned", "doctor_id": str(doctor.id)},
        )
        return assessment

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
    def save_declaration_draft(cls, *, assessment, data, actor):
        cls.ensure_declaration_owner(assessment, actor)
        declaration = cls._get_or_create_declaration(assessment)
        if declaration.is_locked or declaration.validated_at:
            raise ValidationError("This declaration has been validated and is locked.")
        if declaration.submitted_at and not declaration.clarification_requested_at:
            raise ValidationError("Submitted declarations are read-only unless a doctor requests clarification.")
        if declaration.submitted_at and declaration.clarification_requested_at:
            declaration.version += 1
            declaration.submitted_at = None
            declaration.validated_by_doctor = None
            declaration.validated_at = None
        for field, value in cls._declaration_payload(data).items():
            setattr(declaration, field, value)
        declaration.risk_flag = declaration.calculate_risk_flag()
        declaration.is_locked = False
        declaration.save(
            update_fields=[
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
                "certified_true",
                "risk_flag",
                "version",
                "is_locked",
                "submitted_at",
                "validated_by_doctor",
                "validated_at",
                "updated_at",
            ]
        )
        assessment.declaration_status = StepStatus.PENDING
        assessment.save(update_fields=["declaration_status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={"event": "declaration_draft_saved", "version": declaration.version, "risk_flag": declaration.risk_flag},
        )
        return declaration

    @classmethod
    @transaction.atomic
    def submit_declaration(cls, *, assessment, data, actor):
        cls.ensure_declaration_owner(assessment, actor)
        if not data.get("certified_true"):
            raise ValidationError("Food handler must certify that declaration answers are true.")
        declaration = getattr(assessment, "health_declaration", None)
        if declaration and (declaration.is_locked or declaration.validated_at):
            raise ValidationError("This declaration has already been validated and is locked.")
        if declaration and declaration.submitted_at and not declaration.clarification_requested_at:
            raise ValidationError("This declaration has already been submitted and is awaiting doctor review.")
        declaration = cls.save_declaration_draft(assessment=assessment, data=data, actor=actor)
        declaration.submitted_at = timezone.now()
        declaration.certified_true = True
        declaration.clarification_requested_by = None
        declaration.clarification_requested_at = None
        declaration.clarification_reason = ""
        declaration.save(
            update_fields=[
                "submitted_at",
                "certified_true",
                "clarification_requested_by",
                "clarification_requested_at",
                "clarification_reason",
                "updated_at",
            ]
        )
        assessment.declaration_status = StepStatus.SUBMITTED
        assessment.status = AssessmentStatus.DECLARATION_SUBMITTED
        assessment.save(update_fields=["declaration_status", "status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={"event": "declaration_submitted", "version": declaration.version, "risk_flag": declaration.risk_flag},
        )
        return declaration

    @classmethod
    @transaction.atomic
    def validate_declaration(cls, *, declaration, doctor):
        assessment = declaration.assessment
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        if not declaration.submitted_at:
            raise ValidationError("Only submitted declarations can be validated.")
        if declaration.validated_at:
            raise ValidationError("This declaration has already been validated.")
        declaration.validated_by_doctor = doctor
        declaration.validated_at = timezone.now()
        declaration.is_locked = True
        declaration.save(update_fields=["validated_by_doctor", "validated_at", "is_locked", "updated_at"])
        assessment.doctor = doctor
        assessment.declaration_status = StepStatus.VALIDATED
        assessment.status = AssessmentStatus.DECLARATION_VALIDATED
        assessment.save(update_fields=["doctor", "declaration_status", "status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=doctor, target=assessment, metadata={"event": "declaration_validated", "version": declaration.version})
        return declaration

    @classmethod
    @transaction.atomic
    def request_declaration_clarification(cls, *, declaration, doctor, reason):
        assessment = declaration.assessment
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        if declaration.validated_at:
            raise ValidationError("Validated declarations are locked and cannot be sent back for changes.")
        declaration.clarification_requested_by = doctor
        declaration.clarification_requested_at = timezone.now()
        declaration.clarification_reason = reason
        declaration.is_locked = False
        declaration.save(
            update_fields=[
                "clarification_requested_by",
                "clarification_requested_at",
                "clarification_reason",
                "is_locked",
                "updated_at",
            ]
        )
        assessment.declaration_status = StepStatus.PENDING
        assessment.save(update_fields=["declaration_status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=assessment,
            metadata={"event": "declaration_clarification_requested"},
        )
        return declaration

    @classmethod
    @transaction.atomic
    def reopen_declaration(cls, *, declaration, doctor, reason):
        assessment = declaration.assessment
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        if declaration.is_locked or declaration.validated_at:
            raise ValidationError("Validated declarations are locked and cannot be reopened.")
        declaration.version += 1
        declaration.submitted_at = None
        declaration.certified_true = False
        declaration.reopened_by = doctor
        declaration.reopened_at = timezone.now()
        declaration.reopen_reason = reason
        declaration.clarification_requested_by = doctor
        declaration.clarification_requested_at = timezone.now()
        declaration.clarification_reason = reason
        declaration.save(
            update_fields=[
                "version",
                "submitted_at",
                "certified_true",
                "reopened_by",
                "reopened_at",
                "reopen_reason",
                "clarification_requested_by",
                "clarification_requested_at",
                "clarification_reason",
                "updated_at",
            ]
        )
        assessment.declaration_status = StepStatus.PENDING
        assessment.save(update_fields=["declaration_status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=assessment,
            metadata={"event": "declaration_reopened", "version": declaration.version, "reason": reason},
        )
        return declaration

    @classmethod
    @transaction.atomic
    def save_physical_exam_draft(cls, *, assessment, doctor, data):
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        if assessment.doctor_id and assessment.doctor_id != doctor.id:
            raise PermissionDenied("Doctors can only edit physical exams for assigned assessments.")
        exam, _ = PhysicalExamination.objects.update_or_create(
            assessment=assessment,
            defaults={**data, "examined_by": doctor, "examined_at": timezone.now(), "is_completed": False, "completed_at": None},
        )
        exam.risk_flag = exam.calculate_risk_flag()
        exam.save(update_fields=["risk_flag", "updated_at"])
        assessment.doctor = doctor
        assessment.physical_exam_status = StepStatus.SUBMITTED
        assessment.save(update_fields=["doctor", "physical_exam_status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=assessment,
            metadata={"event": "physical_exam_draft_saved", "risk_flag": exam.risk_flag},
        )
        return exam

    @classmethod
    @transaction.atomic
    def complete_physical_exam(cls, *, assessment, doctor, data):
        exam = cls.save_physical_exam_draft(assessment=assessment, doctor=doctor, data=data)
        exam.is_completed = True
        exam.completed_at = timezone.now()
        exam.risk_flag = exam.calculate_risk_flag()
        exam.save(update_fields=["is_completed", "completed_at", "risk_flag", "updated_at"])
        assessment.physical_exam_status = StepStatus.COMPLETED
        assessment.status = AssessmentStatus.PHYSICAL_EXAM_COMPLETED
        assessment.save(update_fields=["physical_exam_status", "status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=doctor, target=assessment, metadata={"event": "physical_exam_completed", "risk_flag": exam.risk_flag})
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
        if assessment.signed_at:
            raise ValidationError("Final decision has already been signed and cannot be changed.")
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
        from apps.vaccinations.models import VaccinationStatus, VaccineType

        acceptable_statuses = {
            VaccinationStatus.VALID,
            VaccinationStatus.DOCTOR_CLEARED,
            VaccinationStatus.ADMINISTERED,
            VaccinationStatus.SECOND_DOSE_DUE,
        }
        has_typhoid_clearance = assessment.vaccinations.filter(
            vaccine_type=VaccineType.TYPHOID,
            status__in=acceptable_statuses,
        ).exists()
        has_hepatitis_clearance = assessment.vaccinations.filter(
            vaccine_type=VaccineType.HEPATITIS_A,
            status__in=acceptable_statuses,
        ).exists()
        if not has_typhoid_clearance or not has_hepatitis_clearance:
            raise ValidationError("Typhoid and Hepatitis A vaccination compliance must be reviewed before final decision.")
        if IllnessReport.objects.filter(food_handler=assessment.food_handler).exclude(
            clearance_status__in=[ClearanceStatus.CLEARED, ClearanceStatus.REJECTED]
        ).exists():
            raise ValidationError("Food handler has an unresolved illness or exclusion issue.")

    @classmethod
    def signature_hash(cls, *, assessment, doctor, final_decision):
        payload = f"{assessment.id}:{doctor.id}:{final_decision}:{timezone.now().isoformat()}:{settings.SECRET_KEY}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def report_type_for_decision(cls, final_decision):
        if final_decision == FitnessDecision.TEMPORARILY_NOT_FIT:
            return ReportType.TEMPORARILY_NOT_FIT
        if final_decision == FitnessDecision.RETURN_TO_WORK_ON_DATE:
            return ReportType.RETURN_TO_WORK
        return ReportType.MEDICAL_EXAMINATION

    @classmethod
    def generate_medical_report(cls, *, assessment, doctor):
        report_type = cls.report_type_for_decision(assessment.final_decision)
        summary = {
            "cards": {
                "food_handler": assessment.food_handler.full_name,
                "facility": assessment.facility.facility_name,
                "final_decision": assessment.final_decision,
                "return_to_work_date": str(assessment.return_to_work_date or ""),
                "signed_at": assessment.signed_at.isoformat() if assessment.signed_at else "",
            },
            "sections": {
                "assessment_completion_summary": [
                    {
                        "payment": assessment.payment_transaction.status if assessment.payment_transaction else "missing",
                        "declaration": assessment.declaration_status,
                        "physical_exam": assessment.physical_exam_status,
                        "lab": assessment.lab_status,
                        "vaccination": assessment.vaccination_status,
                    }
                ],
                "restricted_lab_summary": [
                    {"test": test.test_name or test.test_type, "status": test.status}
                    for test in assessment.lab_tests.all()
                ],
                "vaccination_records": [
                    {"vaccine": record.vaccine_name or record.vaccine_type, "status": record.status}
                    for record in assessment.vaccinations.all()
                ],
            },
        }
        report = GeneratedReport.objects.create(
            report_type=report_type,
            file_format=ReportFormat.JSON,
            filters={"assessment_id": str(assessment.id)},
            summary=summary,
            generated_by=doctor,
            status=GeneratedReportStatus.GENERATED,
        )
        log_action(
            action=AuditAction.CREATE,
            actor=doctor,
            target=report,
            metadata={"event": "medical_report_generated", "assessment_id": str(assessment.id)},
        )
        return report

    @classmethod
    def _assessment_report_role(cls, user):
        return getattr(user, "role", "")

    @classmethod
    def _can_access_assessment_report(cls, *, assessment, user):
        role = cls._assessment_report_role(user)
        if role == UserRole.SUPER_ADMIN:
            return True
        if role == UserRole.FEDERAL_ADMIN:
            return False
        if role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return assessment.facility.state_id == user.state_id
        if role == UserRole.FOOD_HANDLER:
            return assessment.food_handler.user_id == user.id
        if role == UserRole.EMPLOYER:
            return getattr(user, "employer", None) and assessment.employer_id == user.employer.id
        if role == UserRole.DOCTOR:
            return assessment.doctor_id == user.id or assessment.facility.organization_id == user.organization_id
        if role in {UserRole.FACILITY_ADMIN, UserRole.LAB_STAFF}:
            return assessment.facility.organization_id == user.organization_id
        return False

    @classmethod
    def ensure_assessment_report_access(cls, *, assessment, user):
        if not cls._can_access_assessment_report(assessment=assessment, user=user):
            raise PermissionDenied("You cannot access reports for this assessment.")

    @classmethod
    def report_type_for_assessment_kind(cls, kind, assessment=None):
        if kind == "summary":
            return ReportType.ASSESSMENT_COMPLETION
        if kind == "return_to_work":
            return ReportType.RETURN_TO_WORK
        if kind == "lab":
            return ReportType.RESTRICTED_LAB_SUMMARY
        if kind == "vaccination":
            return ReportType.VACCINATION_REVIEW
        if assessment and assessment.final_decision == FitnessDecision.TEMPORARILY_NOT_FIT:
            return ReportType.TEMPORARILY_NOT_FIT
        return ReportType.MEDICAL_EXAMINATION

    @classmethod
    def _operational_assessment_cards(cls, assessment):
        return {
            "assessment_id": str(assessment.id),
            "food_handler": assessment.food_handler.full_name,
            "facility": assessment.facility.facility_name,
            "status": assessment.status,
            "final_decision": assessment.final_decision,
            "certificate_submission_status": (
                getattr(getattr(assessment, "certificate_request", None), "status", None)
                or ("certificate_issued" if getattr(assessment, "certificate", None) else "not_submitted")
            ),
            "return_to_work_date": assessment.return_to_work_date.isoformat() if assessment.return_to_work_date else "",
            "signed_at": assessment.signed_at.isoformat() if assessment.signed_at else "",
        }

    @classmethod
    def _summary_payload(cls, assessment, user):
        role = cls._assessment_report_role(user)
        cards = cls._operational_assessment_cards(assessment)
        payload = {
            "cards": cards,
            "sections": {
                "workflow_status": [
                    {
                        "payment": assessment.payment_transaction.status if assessment.payment_transaction else "missing",
                        "declaration": assessment.declaration_status,
                        "physical_exam": assessment.physical_exam_status,
                        "lab": assessment.lab_status,
                        "vaccination": assessment.vaccination_status,
                        "decision": assessment.final_decision,
                    }
                ],
            },
        }
        if role in {UserRole.DOCTOR, UserRole.FACILITY_ADMIN, UserRole.STATE_ADMIN, UserRole.INSPECTOR, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            payload["sections"]["state_evidence"] = [
                {
                    "fit_signed": assessment.final_decision == FitnessDecision.FIT and bool(assessment.signed_at),
                    "doctor_assigned": bool(assessment.doctor_id),
                    "certificate_request": cards["certificate_submission_status"],
                    "certificate_issued": bool(getattr(assessment, "certificate", None)),
                }
            ]
        return payload

    @classmethod
    def _lab_payload(cls, assessment, user):
        if cls._assessment_report_role(user) not in {UserRole.DOCTOR, UserRole.LAB_STAFF, UserRole.FACILITY_ADMIN, UserRole.STATE_ADMIN, UserRole.INSPECTOR, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("You cannot access lab report details for this assessment.")
        include_notes = cls._assessment_report_role(user) in {UserRole.DOCTOR, UserRole.SUPER_ADMIN}
        return {
            "cards": cls._operational_assessment_cards(assessment),
            "sections": {
                "restricted_lab_summary": [
                    {
                        "test_type": test.test_type,
                        "test_name": test.test_name,
                        "status": test.status,
                        "result_value": test.result_value,
                        "doctor_recommendation": test.doctor_recommendation,
                        **({"result_notes": test.result_notes, "doctor_review_notes": test.doctor_review_notes} if include_notes else {}),
                    }
                    for test in assessment.lab_tests.all()
                ]
            },
        }

    @classmethod
    def _vaccination_payload(cls, assessment, user):
        if cls._assessment_report_role(user) not in {UserRole.DOCTOR, UserRole.FOOD_HANDLER, UserRole.FACILITY_ADMIN, UserRole.STATE_ADMIN, UserRole.INSPECTOR, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("You cannot access vaccination report details for this assessment.")
        include_notes = cls._assessment_report_role(user) in {UserRole.DOCTOR, UserRole.SUPER_ADMIN}
        return {
            "cards": cls._operational_assessment_cards(assessment),
            "sections": {
                "vaccination_review": [
                    {
                        "vaccine_type": record.vaccine_type,
                        "dose_number": record.dose_number,
                        "date_administered": record.date_administered.isoformat() if record.date_administered else "",
                        "expiry_date": record.expiry_date.isoformat() if record.expiry_date else "",
                        "next_dose_date": record.next_dose_date.isoformat() if record.next_dose_date else "",
                        "status": record.status,
                        "compliance_status": record.compliance_status,
                        **({"notes": record.notes} if include_notes else {}),
                    }
                    for record in assessment.vaccinations.all()
                ]
            },
        }

    @classmethod
    def _medical_payload(cls, assessment, user):
        role = cls._assessment_report_role(user)
        if role == UserRole.LAB_STAFF:
            return cls._lab_payload(assessment, user)
        if role in {UserRole.EMPLOYER, UserRole.INSPECTOR, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("You cannot access the full medical report for this assessment.")
        if role == UserRole.FACILITY_ADMIN:
            return cls._summary_payload(assessment, user)
        include_clinical = role in {UserRole.DOCTOR, UserRole.SUPER_ADMIN}
        payload = cls._summary_payload(assessment, user)
        payload["sections"]["medical_decision"] = [
            {
                "final_decision": assessment.final_decision,
                "return_to_work_date": assessment.return_to_work_date.isoformat() if assessment.return_to_work_date else "",
                **({"doctor_notes": assessment.doctor_notes} if include_clinical else {}),
            }
        ]
        payload["sections"].update(cls._lab_payload(assessment, user)["sections"])
        payload["sections"].update(cls._vaccination_payload(assessment, user)["sections"])
        return payload

    @classmethod
    def _return_to_work_payload(cls, assessment, user):
        role = cls._assessment_report_role(user)
        if role == UserRole.EMPLOYER:
            return {
                "cards": {
                    "assessment_id": str(assessment.id),
                    "food_handler": assessment.food_handler.full_name,
                    "operational_status": assessment.food_handler.current_status,
                    "return_to_work_date": assessment.return_to_work_date.isoformat() if assessment.return_to_work_date else "",
                    "final_decision": assessment.final_decision,
                },
                "sections": {},
            }
        return {
            "cards": cls._operational_assessment_cards(assessment),
            "sections": {
                "return_to_work": [
                    {
                        "final_decision": assessment.final_decision,
                        "return_to_work_date": assessment.return_to_work_date.isoformat() if assessment.return_to_work_date else "",
                        "open_clearance_cases": assessment.food_handler.illness_reports.exclude(clearance_status__in=["cleared", "rejected"]).count(),
                    }
                ]
            },
        }

    @classmethod
    def assessment_report_payload(cls, *, assessment, user, kind):
        cls.ensure_assessment_report_access(assessment=assessment, user=user)
        builders = {
            "summary": cls._summary_payload,
            "medical": cls._medical_payload,
            "return_to_work": cls._return_to_work_payload,
            "lab": cls._lab_payload,
            "vaccination": cls._vaccination_payload,
        }
        builder = builders.get(kind)
        if not builder:
            raise NotFound("Unknown assessment report type.")
        payload = builder(assessment, user)
        payload["generated_at"] = timezone.now().isoformat()
        payload["report_kind"] = kind
        return payload

    @classmethod
    def ensure_assessment_report(cls, *, assessment, user, kind):
        payload = cls.assessment_report_payload(assessment=assessment, user=user, kind=kind)
        report = GeneratedReport.objects.create(
            report_type=cls.report_type_for_assessment_kind(kind, assessment),
            file_format=ReportFormat.JSON,
            filters={"assessment_id": str(assessment.id), "kind": kind},
            summary=payload,
            generated_by=user,
            status=GeneratedReportStatus.GENERATED,
        )
        return report

    @classmethod
    @transaction.atomic
    def save_fitness_decision_draft(cls, *, assessment, doctor, final_decision, doctor_notes="", return_to_work_date=None):
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        if assessment.signed_at:
            raise ValidationError("Final decision has already been signed and cannot be changed.")
        if final_decision == FitnessDecision.RETURN_TO_WORK_ON_DATE and not return_to_work_date:
            raise ValidationError("Return-to-work date is required for this decision.")
        assessment.doctor = doctor
        assessment.decision_draft = final_decision
        assessment.decision_draft_return_to_work_date = return_to_work_date
        assessment.decision_draft_notes = doctor_notes
        assessment.decision_draft_saved_at = timezone.now()
        assessment.save(
            update_fields=[
                "doctor",
                "decision_draft",
                "decision_draft_return_to_work_date",
                "decision_draft_notes",
                "decision_draft_saved_at",
                "updated_at",
            ]
        )
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=assessment,
            metadata={"event": "fitness_decision_draft_saved", "decision": final_decision},
        )
        return assessment

    @classmethod
    def _sync_handler_status_for_decision(cls, *, assessment):
        if assessment.final_decision == FitnessDecision.FIT:
            assessment.food_handler.current_status = FoodHandlerStatus.CERTIFICATION_PENDING
        elif assessment.final_decision == FitnessDecision.TEMPORARILY_NOT_FIT:
            assessment.food_handler.current_status = FoodHandlerStatus.TEMPORARILY_NOT_FIT
        elif assessment.final_decision in {FitnessDecision.NOT_FIT, FitnessDecision.REQUIRES_PUBLIC_HEALTH_CLEARANCE}:
            assessment.food_handler.current_status = FoodHandlerStatus.EXCLUDED
        elif assessment.final_decision in {
            FitnessDecision.REQUIRES_VACCINATION,
            FitnessDecision.REQUIRES_LAB_TEST,
            FitnessDecision.REQUIRES_RECHECK,
            FitnessDecision.REQUIRES_TREATMENT,
            FitnessDecision.RETURN_TO_WORK_ON_DATE,
        }:
            assessment.food_handler.current_status = FoodHandlerStatus.TEMPORARILY_EXCLUDED
        assessment.food_handler.save(update_fields=["current_status", "updated_at"])

    @classmethod
    def _ensure_return_to_work_case(cls, *, assessment, doctor):
        if assessment.final_decision not in {
            FitnessDecision.TEMPORARILY_NOT_FIT,
            FitnessDecision.REQUIRES_PUBLIC_HEALTH_CLEARANCE,
            FitnessDecision.RETURN_TO_WORK_ON_DATE,
        }:
            return None
        report = IllnessReport.objects.filter(
            food_handler=assessment.food_handler,
            clearance_status__in=[ClearanceStatus.PENDING, ClearanceStatus.UNDER_REVIEW, ClearanceStatus.CLEARANCE_REQUIRED],
        ).first()
        if not report:
            report = IllnessReport.objects.create(
                food_handler=assessment.food_handler,
                employer=assessment.employer or assessment.food_handler.employer,
                reported_by=doctor,
                symptoms={"source": "medical_assessment_decision", "assessment_id": str(assessment.id)},
                suspected_condition=SuspectedCondition.OTHER,
                symptom_start_date=timezone.localdate(),
                exclusion_start_date=timezone.localdate(),
                earliest_return_date=assessment.return_to_work_date,
                clearance_required=assessment.final_decision == FitnessDecision.REQUIRES_PUBLIC_HEALTH_CLEARANCE,
                clearance_status=(
                    ClearanceStatus.CLEARANCE_REQUIRED
                    if assessment.final_decision == FitnessDecision.REQUIRES_PUBLIC_HEALTH_CLEARANCE
                    else ClearanceStatus.PENDING
                ),
                reviewed_by_doctor=doctor,
                reviewed_at=timezone.now(),
                notes=assessment.doctor_notes,
            )
        else:
            report.reviewed_by_doctor = doctor
            report.reviewed_at = timezone.now()
            report.earliest_return_date = assessment.return_to_work_date or report.earliest_return_date
            report.notes = assessment.doctor_notes or report.notes
            if assessment.final_decision == FitnessDecision.REQUIRES_PUBLIC_HEALTH_CLEARANCE:
                report.clearance_required = True
                report.clearance_status = ClearanceStatus.CLEARANCE_REQUIRED
            report.save(update_fields=["reviewed_by_doctor", "reviewed_at", "earliest_return_date", "notes", "clearance_required", "clearance_status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=report,
            metadata={"event": "return_to_work_case_linked", "assessment_id": str(assessment.id), "decision": assessment.final_decision},
        )
        return report

    @classmethod
    @transaction.atomic
    def set_fitness_decision(cls, *, assessment, doctor, final_decision, doctor_notes="", return_to_work_date=None, digital_signature_confirmation=False):
        cls.validate_final_decision_ready(assessment, doctor)
        if not digital_signature_confirmation:
            raise ValidationError("Digital sign-off confirmation is required.")
        if final_decision == FitnessDecision.RETURN_TO_WORK_ON_DATE and not return_to_work_date:
            raise ValidationError("Return-to-work date is required for this decision.")
        assessment.doctor = doctor
        assessment.signed_by = doctor
        assessment.final_decision = final_decision
        assessment.return_to_work_date = return_to_work_date
        assessment.doctor_notes = doctor_notes
        assessment.signed_at = timezone.now()
        assessment.digital_signature_hash = cls.signature_hash(assessment=assessment, doctor=doctor, final_decision=final_decision)
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
                "signed_by",
                "final_decision",
                "return_to_work_date",
                "doctor_notes",
                "signed_at",
                "digital_signature_hash",
                "status",
                "updated_at",
            ]
        )
        cls._sync_handler_status_for_decision(assessment=assessment)
        cls._ensure_return_to_work_case(assessment=assessment, doctor=doctor)
        cls.generate_medical_report(assessment=assessment, doctor=doctor)
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=assessment,
            metadata={"event": "fitness_decision", "decision": final_decision},
        )
        return assessment
