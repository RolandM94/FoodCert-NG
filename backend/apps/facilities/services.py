from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.facilities.models import AccreditationStatus, MedicalFacility


class FacilityAccreditationService:
    """Handles auditable state transitions for medical facility accreditation."""

    @classmethod
    @transaction.atomic
    def submit(cls, *, application, actor):
        application.application_status = AccreditationStatus.SUBMITTED
        application.submitted_at = timezone.now()
        application.save(update_fields=["application_status", "submitted_at", "updated_at"])
        application.facility.accreditation_status = AccreditationStatus.SUBMITTED
        application.facility.save(update_fields=["accreditation_status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=application, metadata={"event": "facility_submitted"})
        return application

    @classmethod
    @transaction.atomic
    def approve(cls, *, application, reviewer, review_comment=""):
        today = timezone.localdate()
        application.application_status = AccreditationStatus.APPROVED
        application.reviewer = reviewer
        application.review_comment = review_comment
        application.reviewed_at = timezone.now()
        application.save(update_fields=["application_status", "reviewer", "review_comment", "reviewed_at", "updated_at"])

        facility = application.facility
        facility.accreditation_status = AccreditationStatus.APPROVED
        facility.accreditation_start_date = today
        facility.accreditation_expiry_date = MedicalFacility.default_expiry_date(today)
        facility.approved_by = reviewer
        facility.save(
            update_fields=[
                "accreditation_status",
                "accreditation_start_date",
                "accreditation_expiry_date",
                "approved_by",
                "updated_at",
            ]
        )
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=reviewer, target=application, metadata={"event": "facility_approved"})
        return application

    @classmethod
    @transaction.atomic
    def reject(cls, *, application, reviewer, review_comment=""):
        application.application_status = AccreditationStatus.REJECTED
        application.reviewer = reviewer
        application.review_comment = review_comment
        application.reviewed_at = timezone.now()
        application.save(update_fields=["application_status", "reviewer", "review_comment", "reviewed_at", "updated_at"])
        application.facility.accreditation_status = AccreditationStatus.REJECTED
        application.facility.save(update_fields=["accreditation_status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=reviewer, target=application, metadata={"event": "facility_rejected"})
        return application

    @classmethod
    @transaction.atomic
    def suspend(cls, *, application, reviewer, review_comment=""):
        application.application_status = AccreditationStatus.SUSPENDED
        application.reviewer = reviewer
        application.review_comment = review_comment
        application.reviewed_at = timezone.now()
        application.save(update_fields=["application_status", "reviewer", "review_comment", "reviewed_at", "updated_at"])
        application.facility.accreditation_status = AccreditationStatus.SUSPENDED
        application.facility.save(update_fields=["accreditation_status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=reviewer, target=application, metadata={"event": "facility_suspended"})
        return application

    @classmethod
    @transaction.atomic
    def reactivate(cls, *, application, reviewer, review_comment=""):
        today = timezone.localdate()
        application.application_status = AccreditationStatus.APPROVED
        application.reviewer = reviewer
        application.review_comment = review_comment
        application.reviewed_at = timezone.now()
        application.save(update_fields=["application_status", "reviewer", "review_comment", "reviewed_at", "updated_at"])
        application.facility.accreditation_status = AccreditationStatus.APPROVED
        if not application.facility.accreditation_start_date:
            application.facility.accreditation_start_date = today
        if not application.facility.accreditation_expiry_date or application.facility.accreditation_expiry_date < today:
            application.facility.accreditation_expiry_date = MedicalFacility.default_expiry_date(today)
        application.facility.approved_by = reviewer
        application.facility.save(
            update_fields=[
                "accreditation_status",
                "accreditation_start_date",
                "accreditation_expiry_date",
                "approved_by",
                "updated_at",
            ]
        )
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=reviewer, target=application, metadata={"event": "facility_reactivated"})
        return application
