from datetime import timedelta
from uuid import uuid4

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import UserRole
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.food_handlers.models import FoodHandlerStatus
from apps.illness.models import ClearanceStatus, IllnessReport, SuspectedCondition
from apps.notifications.models import Notification, NotificationCategory


class IllnessService:
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
        if food_handler.employer and food_handler.employer.user:
            Notification.objects.create(
                recipient=food_handler.employer.user,
                category=NotificationCategory.ASSESSMENT,
                title="Food handler temporarily excluded",
                message=f"{food_handler.full_name} must not be assigned food handling duties until cleared.",
            )
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
            if report.food_handler.user:
                Notification.objects.create(
                    recipient=report.food_handler.user,
                    category=NotificationCategory.ASSESSMENT,
                    title="Return to work cleared",
                    message="You have been cleared to return to food handling duties.",
                )
        report.save(update_fields=["reviewed_by_doctor", "cleared_at", "clearance_status", "notes", "return_to_work_certificate_number", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=report,
            metadata={"event": "return_to_work_clearance", "cleared": cleared},
        )
        return report
