import calendar
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.facilities.models import AccreditationStatus, MedicalFacility
from apps.policy.models import StatePolicyConfig, default_medical_facility_settings


class FacilityProfileService:
    """Profile helpers for facility-admin owned medical facilities."""

    @classmethod
    def get_for_user(cls, user):
        if not user.organization_id:
            return None
        return MedicalFacility.objects.select_related("organization", "state", "lga", "approved_by").filter(
            organization=user.organization
        ).first()

    @classmethod
    @transaction.atomic
    def update_profile(cls, *, facility, actor, data):
        for field, value in data.items():
            setattr(facility, field, value)
        facility.save()
        log_action(action=AuditAction.UPDATE, actor=actor, target=facility, metadata={"event": "facility_profile_updated"})
        return facility


class FacilityAccreditationService:
    """Handles auditable state transitions for medical facility accreditation."""

    @staticmethod
    def accreditation_expiry_date(facility, start_date):
        settings = default_medical_facility_settings()
        if facility.state_id:
            config = StatePolicyConfig.objects.filter(state=facility.state).first()
            if config:
                settings = {**settings, **config.medical_facility_settings}

        duration = max(int(settings.get("validity_duration") or 12), 1)
        unit = settings.get("validity_unit") or "months"
        if unit == "days":
            return start_date + timedelta(days=duration)
        if unit == "years":
            target_year = start_date.year + duration
            try:
                return start_date.replace(year=target_year)
            except ValueError:
                return start_date.replace(year=target_year, day=28)

        month = start_date.month - 1 + duration
        year = start_date.year + month // 12
        month = month % 12 + 1
        day = min(start_date.day, calendar.monthrange(year, month)[1])
        return start_date.replace(year=year, month=month, day=day)

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
    def request_more_information(cls, *, application, reviewer, review_comment=""):
        application.application_status = AccreditationStatus.MORE_INFORMATION_REQUIRED
        application.reviewer = reviewer
        application.review_comment = review_comment
        application.reviewed_at = timezone.now()
        application.save(update_fields=["application_status", "reviewer", "review_comment", "reviewed_at", "updated_at"])
        application.facility.accreditation_status = AccreditationStatus.MORE_INFORMATION_REQUIRED
        application.facility.save(update_fields=["accreditation_status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=reviewer,
            target=application,
            metadata={"event": "facility_more_information_required"},
        )
        return application

    @classmethod
    @transaction.atomic
    def create_renewal(cls, *, facility, actor):
        latest_approved = facility.accreditation_applications.filter(
            application_status=AccreditationStatus.APPROVED
        ).order_by("-reviewed_at", "-created_at").first()
        renewal = facility.accreditation_applications.create(
            is_renewal=True,
            renewal_of=latest_approved,
            has_reporting_policy=True,
            has_medical_records_computers=True,
            has_computer_operators=True,
            has_standard_forms=True,
            has_laboratory_request_forms=True,
            has_patient_files=True,
            has_qr_certificate_capability=True,
            has_internet_access=True,
            has_trained_records_staff=True,
            has_trained_clinical_staff=True,
            has_trained_non_clinical_staff=True,
            has_valid_facility_license=True,
            has_laboratory_capacity=True,
            has_valid_doctor_credentials=True,
            has_valid_lab_staff_credentials=True,
            has_infection_prevention_readiness=True,
            has_confidentiality_policy=True,
        )
        facility.accreditation_status = AccreditationStatus.REACCREDITATION_DUE
        facility.save(update_fields=["accreditation_status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=renewal,
            metadata={"event": "facility_renewal_started"},
        )
        return renewal

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
        facility.accreditation_expiry_date = cls.accreditation_expiry_date(facility, today)
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
        from apps.certificates.services import CertificateService

        CertificateService.issue_facility_accreditation_certificate(application=application, actor=reviewer)
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
            application.facility.accreditation_expiry_date = cls.accreditation_expiry_date(application.facility, today)
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
