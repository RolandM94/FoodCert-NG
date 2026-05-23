from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.assessments.models import AssessmentStatus, StepStatus
from apps.accounts.models import UserRole
from apps.assessments.services import ensure_approved_facility, ensure_clinical_staff_for_facility, ensure_doctor_for_facility
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.lab_tests.models import LabReviewRecommendation, LabTest, LabTestStatus, LabTestType


class LabTestService:
    REQUIRED_TESTS = (
        LabTestType.STOOL_MICROSCOPY,
        LabTestType.STOOL_CULTURE_SENSITIVITY,
        LabTestType.HEPATITIS_A_ANTIGEN,
    )

    @classmethod
    def required_test_items(cls):
        return [{"test_type": test_type, "test_name": ""} for test_type in cls.REQUIRED_TESTS]

    @classmethod
    def normalize_requested_tests(cls, tests, *, include_required=True):
        normalized = []
        seen = set()
        source = [*cls.required_test_items(), *tests] if include_required else tests
        for item in source:
            test_type = item["test_type"]
            key = (test_type, item.get("test_name", ""))
            if key in seen:
                continue
            seen.add(key)
            normalized.append({"test_type": test_type, "test_name": item.get("test_name", "")})
        return normalized

    @classmethod
    @transaction.atomic
    def request_tests(cls, *, assessment, requested_by, tests, include_required=True):
        ensure_approved_facility(assessment.facility)
        ensure_clinical_staff_for_facility(requested_by, assessment.facility)
        requested_tests = cls.normalize_requested_tests(tests, include_required=include_required)
        created = [
            LabTest.objects.create(
                assessment=assessment,
                requested_by=requested_by,
                test_type=item["test_type"],
                test_name=item.get("test_name", ""),
                status=LabTestStatus.SAMPLE_COLLECTION_PENDING,
            )
            for item in requested_tests
        ]
        assessment.lab_status = StepStatus.PENDING
        assessment.status = AssessmentStatus.LAB_TESTS_PENDING
        assessment.save(update_fields=["lab_status", "status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=requested_by,
            target=assessment,
            metadata={"event": "lab_tests_requested", "count": len(created), "include_required": include_required},
        )
        return created

    @classmethod
    @transaction.atomic
    def request_repeat(cls, *, lab_test, doctor, reason, test_name=""):
        assessment = lab_test.assessment
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        lab_test.repeat_required = True
        lab_test.repeat_reason = reason
        lab_test.status = LabTestStatus.REPEAT_REQUIRED
        lab_test.is_flagged = True
        lab_test.reviewed_by = doctor
        lab_test.reviewed_at = timezone.now()
        lab_test.save(update_fields=["repeat_required", "repeat_reason", "status", "is_flagged", "reviewed_by", "reviewed_at", "updated_at"])
        repeat = LabTest.objects.create(
            assessment=assessment,
            parent_lab_test=lab_test,
            requested_by=doctor,
            test_type=lab_test.test_type,
            test_name=test_name or lab_test.test_name,
            repeat_reason=reason,
        )
        assessment.lab_status = StepStatus.PENDING
        assessment.status = AssessmentStatus.LAB_TESTS_PENDING
        assessment.save(update_fields=["lab_status", "status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=lab_test,
            metadata={"event": "lab_repeat_requested", "repeat_lab_test_id": str(repeat.id), "reason": reason},
        )
        return repeat

    @classmethod
    @transaction.atomic
    def mark_sample_collected(cls, *, lab_test, actor, lab_staff_notes=""):
        ensure_approved_facility(lab_test.assessment.facility)
        if actor.role != UserRole.LAB_STAFF:
            raise PermissionDenied("Only lab staff can collect samples.")
        if actor.organization_id != lab_test.assessment.facility.organization_id:
            raise PermissionDenied("Lab staff can only process tests for their own facility.")
        lab_test.status = LabTestStatus.SAMPLE_COLLECTED
        lab_test.sample_collected_at = timezone.now()
        if lab_staff_notes:
            lab_test.lab_staff_notes = lab_staff_notes
        lab_test.save(update_fields=["status", "sample_collected_at", "lab_staff_notes", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=lab_test, metadata={"event": "lab_sample_collected"})
        return lab_test

    @classmethod
    @transaction.atomic
    def record_result(cls, *, lab_test, actor, status, result_value="", result_notes="", lab_staff_notes=""):
        ensure_approved_facility(lab_test.assessment.facility)
        ensure_clinical_staff_for_facility(actor, lab_test.assessment.facility)
        if status not in {LabTestStatus.POSITIVE, LabTestStatus.NEGATIVE, LabTestStatus.INCONCLUSIVE, LabTestStatus.REPEAT_REQUIRED}:
            raise ValidationError("Result status must be positive, negative, inconclusive, or repeat_required.")
        if actor.role != UserRole.LAB_STAFF:
            raise PermissionDenied("Only lab staff can enter lab results.")
        if not lab_test.sample_collected_at:
            lab_test.sample_collected_at = timezone.now()
        lab_test.status = status
        lab_test.is_flagged = status in {LabTestStatus.POSITIVE, LabTestStatus.INCONCLUSIVE, LabTestStatus.REPEAT_REQUIRED}
        lab_test.repeat_required = status == LabTestStatus.REPEAT_REQUIRED
        lab_test.result_value = result_value
        lab_test.result_notes = result_notes
        if lab_staff_notes:
            lab_test.lab_staff_notes = lab_staff_notes
        lab_test.resulted_by = actor
        lab_test.resulted_at = timezone.now()
        lab_test.save(
            update_fields=[
                "status",
                "is_flagged",
                "repeat_required",
                "result_value",
                "result_notes",
                "lab_staff_notes",
                "resulted_by",
                "resulted_at",
                "sample_collected_at",
                "updated_at",
            ]
        )
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=lab_test,
            metadata={"event": "lab_result_recorded", "status": status, "flagged": status != LabTestStatus.NEGATIVE},
        )
        return lab_test

    @classmethod
    @transaction.atomic
    def upload_result_document(cls, *, lab_test, actor, result_document, lab_staff_notes=""):
        ensure_approved_facility(lab_test.assessment.facility)
        if actor.role != UserRole.LAB_STAFF:
            raise PermissionDenied("Only lab staff can upload result documents.")
        if actor.organization_id != lab_test.assessment.facility.organization_id:
            raise PermissionDenied("Lab staff can only process tests for their own facility.")
        lab_test.result_document = result_document
        if lab_staff_notes:
            lab_test.lab_staff_notes = lab_staff_notes
        if lab_test.status in {LabTestStatus.REQUESTED, LabTestStatus.SAMPLE_COLLECTION_PENDING, LabTestStatus.SAMPLE_COLLECTED, LabTestStatus.IN_PROGRESS}:
            lab_test.status = LabTestStatus.RESULT_UPLOADED
        lab_test.submitted_to_doctor_at = timezone.now()
        lab_test.save(update_fields=["status", "result_document", "lab_staff_notes", "submitted_to_doctor_at", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=lab_test, metadata={"event": "lab_result_document_uploaded"})
        return lab_test

    @classmethod
    @transaction.atomic
    def submit_to_doctor(cls, *, lab_test, actor, lab_staff_notes=""):
        ensure_approved_facility(lab_test.assessment.facility)
        if actor.role != UserRole.LAB_STAFF:
            raise PermissionDenied("Only lab staff can submit lab results to the doctor.")
        if actor.organization_id != lab_test.assessment.facility.organization_id:
            raise PermissionDenied("Lab staff can only process tests for their own facility.")
        if lab_test.status not in {
            LabTestStatus.POSITIVE,
            LabTestStatus.NEGATIVE,
            LabTestStatus.INCONCLUSIVE,
            LabTestStatus.REPEAT_REQUIRED,
            LabTestStatus.RESULT_UPLOADED,
        }:
            raise ValidationError("A result or uploaded result document is required before doctor submission.")
        if lab_staff_notes:
            lab_test.lab_staff_notes = lab_staff_notes
        lab_test.submitted_to_doctor_at = timezone.now()
        if lab_test.status == LabTestStatus.RESULT_UPLOADED:
            lab_test.status = LabTestStatus.SUBMITTED_TO_DOCTOR
        lab_test.save(update_fields=["status", "lab_staff_notes", "submitted_to_doctor_at", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=lab_test, metadata={"event": "lab_result_submitted_to_doctor", "status": lab_test.status})
        return lab_test

    @classmethod
    @transaction.atomic
    def default_recommendation(cls, lab_test):
        if lab_test.status == LabTestStatus.INCONCLUSIVE:
            return LabReviewRecommendation.REPEAT_TEST
        if lab_test.status in {LabTestStatus.POSITIVE, LabTestStatus.REPEAT_REQUIRED}:
            return LabReviewRecommendation.TEMPORARILY_NOT_FIT
        return LabReviewRecommendation.CLEARED

    @classmethod
    @transaction.atomic
    def review(cls, *, lab_test, doctor, doctor_review_notes="", doctor_recommendation=""):
        assessment = lab_test.assessment
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        if lab_test.status not in {LabTestStatus.POSITIVE, LabTestStatus.NEGATIVE, LabTestStatus.INCONCLUSIVE, LabTestStatus.REPEAT_REQUIRED, LabTestStatus.SUBMITTED_TO_DOCTOR}:
            raise ValidationError("Lab result must be submitted before doctor review.")
        was_flagged = lab_test.calculate_flagged() or lab_test.is_flagged
        lab_test.status = LabTestStatus.REVIEWED
        lab_test.is_flagged = was_flagged
        lab_test.reviewed_by = doctor
        lab_test.reviewed_at = timezone.now()
        lab_test.doctor_review_notes = doctor_review_notes
        lab_test.doctor_recommendation = doctor_recommendation or cls.default_recommendation(lab_test)
        lab_test.save(update_fields=["status", "is_flagged", "reviewed_by", "reviewed_at", "doctor_review_notes", "doctor_recommendation", "updated_at"])
        if assessment.lab_tests.exclude(status=LabTestStatus.REVIEWED).count() == 0:
            assessment.lab_status = StepStatus.REVIEWED
            assessment.status = AssessmentStatus.LAB_RESULTS_REVIEWED
            assessment.save(update_fields=["lab_status", "status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=lab_test,
            metadata={"event": "lab_result_reviewed", "recommendation": lab_test.doctor_recommendation, "flagged": lab_test.is_flagged},
        )
        return lab_test
