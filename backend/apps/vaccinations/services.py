from django.conf import settings
from django.db import transaction

from apps.assessments.models import AssessmentStatus, StepStatus
from apps.assessments.services import ensure_approved_facility, ensure_doctor_for_facility
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.vaccinations.models import VaccinationRecord


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
