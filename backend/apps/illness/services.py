from datetime import timedelta
from uuid import uuid4

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import User, UserRole
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.food_handlers.models import FoodHandlerStatus
from apps.illness.models import ClearanceStatus, IllnessReport, SuspectedCondition
from apps.notifications.models import Notification, NotificationCategory, NotificationPriority


STATE_EXCEPTION_CONDITIONS = {
    SuspectedCondition.CHOLERA,
    SuspectedCondition.SHIGELLA,
    SuspectedCondition.LASSA_FEVER,
}


class IllnessService:
    @classmethod
    def _notify(cls, *, recipient, category, title, message, priority=NotificationPriority.NORMAL, report=None):
        if not recipient:
            return None
        return Notification.objects.create(
            recipient=recipient,
            category=category,
            priority=priority,
            title=title,
            message=message,
            related_object_type="IllnessReport" if report else "",
            related_object_id=report.id if report else None,
        )

    @classmethod
    def _doctor_review_users(cls, report):
        return User.objects.filter(role=UserRole.DOCTOR, state_id=report.food_handler.state_id, is_active=True)

    @classmethod
    def _state_exception_users(cls, report):
        return User.objects.filter(role=UserRole.STATE_ADMIN, state_id=report.food_handler.state_id, is_active=True)

    @classmethod
    def _is_state_exception(cls, report):
        return report.clearance_required or report.suspected_condition in STATE_EXCEPTION_CONDITIONS

    @classmethod
    def _notify_report_created(cls, report):
        food_handler = report.food_handler
        employer = report.employer
        cls._notify(
            recipient=food_handler.user,
            category=NotificationCategory.ASSESSMENT,
            title="Illness exclusion recorded",
            message="You are temporarily excluded from food handling duties until the required return-to-work step is complete.",
            priority=NotificationPriority.HIGH,
            report=report,
        )
        if employer and employer.user:
            cls._notify(
                recipient=employer.user,
                category=NotificationCategory.ASSESSMENT,
                title="Food handler temporarily excluded",
                message=f"{food_handler.full_name} must not be assigned food handling duties until cleared.",
                priority=NotificationPriority.HIGH,
                report=report,
            )
        if report.clearance_required:
            for doctor in cls._doctor_review_users(report):
                cls._notify(
                    recipient=doctor,
                    category=NotificationCategory.ASSESSMENT,
                    title="Return-to-work review required",
                    message=f"{food_handler.full_name} has a return-to-work case awaiting medical review.",
                    priority=NotificationPriority.HIGH,
                    report=report,
                )
        if cls._is_state_exception(report):
            for state_user in cls._state_exception_users(report):
                cls._notify(
                    recipient=state_user,
                    category=NotificationCategory.ENFORCEMENT,
                    title="Illness exclusion exception",
                    message="A clearance-required illness exclusion has been recorded in your state.",
                    priority=NotificationPriority.HIGH,
                    report=report,
                )

    @classmethod
    def _notify_review_updated(cls, report):
        cls._notify(
            recipient=report.food_handler.user,
            category=NotificationCategory.ASSESSMENT,
            title="Return-to-work review updated",
            message="Your return-to-work case is under medical review.",
            report=report,
        )
        if report.employer and report.employer.user:
            cls._notify(
                recipient=report.employer.user,
                category=NotificationCategory.ASSESSMENT,
                title="Return-to-work case under review",
                message=f"{report.food_handler.full_name}'s return-to-work case is under medical review.",
                report=report,
            )

    @classmethod
    def _notify_clearance_outcome(cls, report, *, cleared):
        title = "Return to work cleared" if cleared else "Return to work not cleared"
        handler_message = (
            "You have been cleared to return to food handling duties."
            if cleared else
            "You are not yet cleared to return to food handling duties. Follow the next medical instruction from your facility or doctor."
        )
        employer_message = (
            f"{report.food_handler.full_name} has been cleared to return to food handling duties."
            if cleared else
            f"{report.food_handler.full_name} is not yet cleared to return to food handling duties."
        )
        cls._notify(
            recipient=report.food_handler.user,
            category=NotificationCategory.ASSESSMENT,
            title=title,
            message=handler_message,
            priority=NotificationPriority.HIGH,
            report=report,
        )
        if report.employer and report.employer.user:
            cls._notify(
                recipient=report.employer.user,
                category=NotificationCategory.ASSESSMENT,
                title=title,
                message=employer_message,
                priority=NotificationPriority.HIGH,
                report=report,
            )

    @classmethod
    def earliest_return_date(cls, *, condition, symptom_end_date, symptom_start_date):
        if condition == SuspectedCondition.GENERAL_DIARRHOEA_VOMITING and symptom_end_date:
            return symptom_end_date + timedelta(days=2)
        if condition == SuspectedCondition.HEPATITIS_A and symptom_start_date:
            return symptom_start_date + timedelta(days=7)
        if condition == SuspectedCondition.AMOEBIC_DYSENTERY and symptom_end_date:
            return symptom_end_date + timedelta(days=7)
        if condition == SuspectedCondition.TAENIA_SOLIUM and symptom_end_date:
            return symptom_end_date + timedelta(days=14)
        return None

    @classmethod
    def clearance_required(cls, condition) -> bool:
        return condition in {
            SuspectedCondition.CHOLERA,
            SuspectedCondition.SHIGELLA,
            SuspectedCondition.LASSA_FEVER,
            SuspectedCondition.AMOEBIC_DYSENTERY,
            SuspectedCondition.TAENIA_SOLIUM,
        } or not condition

    @classmethod
    def can_report_for_handler(cls, *, actor, food_handler):
        if actor.role == UserRole.FOOD_HANDLER and food_handler.user_id == actor.id:
            return True
        if actor.role == UserRole.EMPLOYER and food_handler.employer_id:
            if getattr(actor, "unit_restricted", False) and actor.unit_id:
                return food_handler.employer.organization_id == actor.organization_id and food_handler.business_branch_id == actor.unit_id
            return food_handler.employer.organization_id == actor.organization_id
        if actor.role in {UserRole.DOCTOR, UserRole.INSPECTOR, UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return True
        return False

    @classmethod
    @transaction.atomic
    def report(cls, *, food_handler, reported_by, symptoms, suspected_condition="", symptom_start_date=None, symptom_end_date=None, notes=""):
        if not cls.can_report_for_handler(actor=reported_by, food_handler=food_handler):
            raise PermissionDenied("You cannot report illness for this food handler.")
        earliest = cls.earliest_return_date(
            condition=suspected_condition,
            symptom_end_date=symptom_end_date,
            symptom_start_date=symptom_start_date,
        )
        report = IllnessReport.objects.create(
            food_handler=food_handler,
            employer=food_handler.employer,
            reported_by=reported_by,
            symptoms=symptoms,
            suspected_condition=suspected_condition,
            symptom_start_date=symptom_start_date,
            symptom_end_date=symptom_end_date,
            earliest_return_date=earliest,
            clearance_required=cls.clearance_required(suspected_condition),
            notes=notes,
        )
        food_handler.current_status = FoodHandlerStatus.TEMPORARILY_EXCLUDED
        food_handler.save(update_fields=["current_status", "updated_at"])
        cls._notify_report_created(report)
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=reported_by, target=report, metadata={"event": "illness_reported"})
        return report

    @classmethod
    def ensure_doctor_can_review(cls, *, doctor, report):
        if doctor.role != UserRole.DOCTOR:
            raise PermissionDenied("Only doctors can review illness reports.")
        # A doctor may review cases for a handler assessed by their facility or as a general clearance doctor.
        if doctor.state_id and report.food_handler.state_id != doctor.state_id:
            raise PermissionDenied("Doctors can only review illness reports in their state.")

    @classmethod
    @transaction.atomic
    def review(cls, *, report, doctor, notes="", symptom_end_date=None, suspected_condition=None):
        cls.ensure_doctor_can_review(doctor=doctor, report=report)
        if suspected_condition is not None:
            report.suspected_condition = suspected_condition
        if symptom_end_date:
            report.symptom_end_date = symptom_end_date
        report.earliest_return_date = cls.earliest_return_date(
            condition=report.suspected_condition,
            symptom_end_date=report.symptom_end_date,
            symptom_start_date=report.symptom_start_date,
        )
        report.clearance_required = cls.clearance_required(report.suspected_condition)
        report.clearance_status = ClearanceStatus.UNDER_REVIEW
        report.reviewed_by_doctor = doctor
        report.reviewed_at = timezone.now()
        report.notes = notes or report.notes
        report.save(
            update_fields=[
                "suspected_condition",
                "symptom_end_date",
                "earliest_return_date",
                "clearance_required",
                "clearance_status",
                "reviewed_by_doctor",
                "reviewed_at",
                "notes",
                "updated_at",
            ]
        )
        cls._notify_review_updated(report)
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=doctor, target=report, metadata={"event": "illness_reviewed"})
        return report

    @classmethod
    @transaction.atomic
    def clearance(cls, *, report, doctor, cleared, notes=""):
        cls.ensure_doctor_can_review(doctor=doctor, report=report)
        today = timezone.localdate()
        if cleared and report.earliest_return_date and report.earliest_return_date > today:
            raise ValidationError("Food handler cannot return before the calculated earliest return date.")
        report.reviewed_by_doctor = doctor
        report.cleared_at = timezone.now() if cleared else None
        report.clearance_status = ClearanceStatus.CLEARED if cleared else ClearanceStatus.REJECTED
        report.notes = notes or report.notes
        if cleared:
            report.return_to_work_certificate_number = report.return_to_work_certificate_number or f"RTW-{today:%Y%m%d}-{uuid4().hex[:8].upper()}"
            report.food_handler.current_status = FoodHandlerStatus.FIT
            report.food_handler.save(update_fields=["current_status", "updated_at"])
        report.save(update_fields=["reviewed_by_doctor", "cleared_at", "clearance_status", "notes", "return_to_work_certificate_number", "updated_at"])
        cls._notify_clearance_outcome(report, cleared=cleared)
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=report,
            metadata={"event": "return_to_work_clearance", "cleared": cleared},
        )
        return report
