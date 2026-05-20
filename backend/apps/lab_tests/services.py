from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.assessments.models import AssessmentStatus, StepStatus
from apps.assessments.services import ensure_approved_facility, ensure_clinical_staff_for_facility, ensure_doctor_for_facility
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.lab_tests.models import LabTest, LabTestStatus


class LabTestService:
    @classmethod
    @transaction.atomic
    def request_tests(cls, *, assessment, requested_by, tests):
        ensure_approved_facility(assessment.facility)
        ensure_clinical_staff_for_facility(requested_by, assessment.facility)
        created = [
            LabTest.objects.create(
                assessment=assessment,
                requested_by=requested_by,
                test_type=item["test_type"],
                test_name=item.get("test_name", ""),
            )
            for item in tests
        ]
        assessment.lab_status = StepStatus.PENDING
        assessment.status = AssessmentStatus.LAB_TESTS_PENDING
        assessment.save(update_fields=["lab_status", "status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=requested_by, target=assessment, metadata={"event": "lab_tests_requested"})
        return created

    @classmethod
    @transaction.atomic
    def record_result(cls, *, lab_test, actor, status, result_value="", result_notes=""):
        ensure_approved_facility(lab_test.assessment.facility)
        ensure_clinical_staff_for_facility(actor, lab_test.assessment.facility)
        if status not in {LabTestStatus.POSITIVE, LabTestStatus.NEGATIVE, LabTestStatus.INCONCLUSIVE, LabTestStatus.REPEAT_REQUIRED}:
            raise ValidationError("Result status must be positive, negative, inconclusive, or repeat_required.")
        lab_test.status = status
        lab_test.result_value = result_value
        lab_test.result_notes = result_notes
        lab_test.resulted_by = actor
        lab_test.resulted_at = timezone.now()
        lab_test.save(update_fields=["status", "result_value", "result_notes", "resulted_by", "resulted_at", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=lab_test, metadata={"event": "lab_result_recorded", "status": status})
        return lab_test

    @classmethod
    @transaction.atomic
    def review(cls, *, lab_test, doctor):
        assessment = lab_test.assessment
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        if lab_test.status not in {LabTestStatus.POSITIVE, LabTestStatus.NEGATIVE, LabTestStatus.INCONCLUSIVE, LabTestStatus.REPEAT_REQUIRED}:
            raise ValidationError("Lab result must be submitted before doctor review.")
        lab_test.status = LabTestStatus.REVIEWED
        lab_test.reviewed_by = doctor
        lab_test.reviewed_at = timezone.now()
        lab_test.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
        if assessment.lab_tests.exclude(status=LabTestStatus.REVIEWED).count() == 0:
            assessment.lab_status = StepStatus.REVIEWED
            assessment.status = AssessmentStatus.LAB_RESULTS_REVIEWED
            assessment.save(update_fields=["lab_status", "status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=doctor, target=lab_test, metadata={"event": "lab_result_reviewed"})
        return lab_test
