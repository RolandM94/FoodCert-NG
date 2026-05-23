from django.conf import settings
from django.db import transaction

from apps.assessments.models import AssessmentStatus, StepStatus
from apps.assessments.services import ensure_approved_facility, ensure_doctor_for_facility
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.vaccinations.models import VaccinationRecord, VaccinationStatus


class VaccinationService:
    @classmethod
    @transaction.atomic
    def record(cls, *, assessment, recorded_by, data):
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(recorded_by, assessment.facility)
        record = VaccinationRecord(
            assessment=assessment,
            food_handler=assessment.food_handler,
            recorded_by=recorded_by,
            **data,
        )
        record.derive_dates_and_status(
            typhoid_validity_years=settings.DEFAULT_TYPHOID_VALIDITY_YEARS,
            hepatitis_a_second_dose_months=settings.DEFAULT_HEPATITIS_A_SECOND_DOSE_MONTHS,
        )
        record.save()
        assessment.doctor = recorded_by
        assessment.vaccination_status = StepStatus.REVIEWED
        assessment.status = AssessmentStatus.VACCINATION_REVIEWED
        assessment.save(update_fields=["doctor", "vaccination_status", "status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=recorded_by, target=assessment, metadata={"event": "vaccination_reviewed"})
        return record

    @classmethod
    @transaction.atomic
    def review_assessment(cls, *, assessment, doctor, data):
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        explicit_status = data.pop("status", "")
        action = data.pop("action", "")
        if action:
            explicit_status = {
                "mark_valid": VaccinationStatus.VALID,
                "mark_missing": VaccinationStatus.MISSING,
                "mark_expired": VaccinationStatus.EXPIRED,
                "mark_incomplete": VaccinationStatus.INCOMPLETE,
                "prescribe": VaccinationStatus.PRESCRIBED,
                "administer": VaccinationStatus.ADMINISTERED,
            }.get(action, explicit_status)
        record = VaccinationRecord(
            assessment=assessment,
            food_handler=assessment.food_handler,
            recorded_by=doctor,
            **data,
        )
        record.derive_dates_and_status(
            typhoid_validity_years=settings.DEFAULT_TYPHOID_VALIDITY_YEARS,
            hepatitis_a_second_dose_months=settings.DEFAULT_HEPATITIS_A_SECOND_DOSE_MONTHS,
        )
        if explicit_status:
            record.status = explicit_status
            if explicit_status == VaccinationStatus.DOCTOR_CLEARED:
                record.doctor_clearance = True
        record.save()
        assessment.doctor = doctor
        assessment.vaccination_status = StepStatus.REVIEWED
        assessment.status = AssessmentStatus.VACCINATION_REVIEWED
        assessment.save(update_fields=["doctor", "vaccination_status", "status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=assessment,
            metadata={"event": "vaccination_reviewed", "vaccination_status": record.status},
        )
        return record
