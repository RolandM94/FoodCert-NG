import calendar
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.facilities.models import (
    AccreditationStatus,
    FacilityProfessionalCategory,
    FacilityRole,
    FacilityRolePermission,
    FacilityStaffProfile,
    FacilityTeamMemberStatus,
    MedicalFacility,
)
from apps.policy.models import StatePolicyConfig, default_medical_facility_settings


FACILITY_PROTECTED_PERMISSION_RULES = {
    "declaration.validate": {FacilityProfessionalCategory.DOCTOR},
    "physical_exam.create": {FacilityProfessionalCategory.DOCTOR},
    "doctor_review.final_decision": {FacilityProfessionalCategory.DOCTOR},
    "lab_results.create": {
        FacilityProfessionalCategory.LAB_TECHNICIAN,
        FacilityProfessionalCategory.LAB_SCIENTIST,
        FacilityProfessionalCategory.LAB_SUPERVISOR,
    },
    "lab_results.submit": {
        FacilityProfessionalCategory.LAB_TECHNICIAN,
        FacilityProfessionalCategory.LAB_SCIENTIST,
        FacilityProfessionalCategory.LAB_SUPERVISOR,
    },
}


DEFAULT_FACILITY_ROLE_TEMPLATES = [
    {
        "code": "facility_owner_super_admin",
        "name": "Facility Owner / Super Admin",
        "description": "Full control of the facility account and workflow.",
        "professional_category": FacilityProfessionalCategory.ADMIN,
        "permissions": [
            "facility.profile.view",
            "facility.profile.edit",
            "facility.team.invite",
            "facility.team.remove",
            "facility.roles.create",
            "facility.roles.edit",
            "facility.roles.assign_permissions",
            "appointments.view",
            "appointments.confirm",
            "appointments.cancel",
            "assessment.check_in",
            "assessment.verify_identity",
            "declaration.view",
            "lab_requests.view",
            "certificates.view",
            "unfit_reports.view",
            "finance.view_payments",
            "finance.confirm_payment",
            "compliance.view_dashboard",
            "audit_logs.view",
        ],
    },
    {
        "code": "facility_administrator",
        "name": "Facility Administrator",
        "description": "Manages facility setup, bookings, and team administration.",
        "professional_category": FacilityProfessionalCategory.ADMIN,
        "permissions": [
            "facility.profile.view",
            "facility.profile.edit",
            "facility.team.invite",
            "facility.team.remove",
            "facility.roles.create",
            "facility.roles.edit",
            "facility.roles.assign_permissions",
            "appointments.view",
            "appointments.confirm",
            "appointments.cancel",
            "assessment.check_in",
            "assessment.verify_identity",
            "declaration.view",
            "lab_requests.view",
            "certificates.view",
            "finance.view_payments",
            "compliance.view_dashboard",
            "audit_logs.view",
        ],
    },
    {
        "code": "front_desk_reception_officer",
        "name": "Front Desk / Reception Officer",
        "description": "Handles appointment intake, check-in, and identity verification.",
        "professional_category": FacilityProfessionalCategory.FRONT_DESK,
        "permissions": [
            "appointments.view",
            "appointments.confirm",
            "appointments.cancel",
            "assessment.check_in",
            "assessment.verify_identity",
        ],
    },
    {
        "code": "medical_doctor",
        "name": "Medical Doctor",
        "description": "Reviews declarations, conducts exams, and confirms final decisions.",
        "professional_category": FacilityProfessionalCategory.DOCTOR,
        "permissions": [
            "appointments.view",
            "declaration.view",
            "declaration.validate",
            "declaration.request_correction",
            "physical_exam.create",
            "lab_requests.view",
            "lab_results.review",
            "doctor_review.view",
            "doctor_review.final_decision",
            "certificates.view",
            "unfit_reports.view",
        ],
    },
    {
        "code": "lab_technician_lab_scientist",
        "name": "Lab Technician / Lab Scientist",
        "description": "Collects samples and records lab results for doctor review.",
        "professional_category": FacilityProfessionalCategory.LAB_TECHNICIAN,
        "permissions": [
            "appointments.view",
            "lab_requests.view",
            "lab_results.create",
            "lab_results.submit",
        ],
    },
    {
        "code": "lab_supervisor",
        "name": "Lab Supervisor",
        "description": "Oversees laboratory result entry and review readiness.",
        "professional_category": FacilityProfessionalCategory.LAB_SUPERVISOR,
        "permissions": [
            "appointments.view",
            "lab_requests.view",
            "lab_results.create",
            "lab_results.submit",
            "lab_results.review",
        ],
    },
    {
        "code": "finance_billing_officer",
        "name": "Finance / Billing Officer",
        "description": "Handles payments, confirmations, and receipts.",
        "professional_category": FacilityProfessionalCategory.FINANCE,
        "permissions": [
            "appointments.view",
            "finance.view_payments",
            "finance.confirm_payment",
        ],
    },
    {
        "code": "records_officer",
        "name": "Records Officer",
        "description": "Manages operational records and generated outputs.",
        "professional_category": FacilityProfessionalCategory.RECORDS,
        "permissions": [
            "appointments.view",
            "declaration.view",
            "lab_requests.view",
            "certificates.view",
            "unfit_reports.view",
        ],
    },
    {
        "code": "compliance_officer",
        "name": "Compliance Officer",
        "description": "Monitors facility compliance and audit trails.",
        "professional_category": FacilityProfessionalCategory.COMPLIANCE,
        "permissions": [
            "appointments.view",
            "compliance.view_dashboard",
            "audit_logs.view",
        ],
    },
    {
        "code": "viewer_auditor",
        "name": "Viewer / Auditor",
        "description": "Read-only oversight of approved facility workflow records.",
        "professional_category": FacilityProfessionalCategory.VIEWER,
        "permissions": [
            "appointments.view",
            "certificates.view",
            "unfit_reports.view",
            "compliance.view_dashboard",
            "audit_logs.view",
        ],
    },
]


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
    def get_facility_membership_for_user(cls, user):
        if not getattr(user, "is_authenticated", False):
            return None
        if getattr(user, "role", "") == UserRole.FACILITY_ADMIN:
            return cls.get_for_user(user)
        profile = FacilityStaffProfile.objects.select_related(
            "facility",
            "facility__organization",
            "facility__state",
            "facility__lga",
            "facility__approved_by",
        ).filter(
            user=user,
            is_active=True,
            status=FacilityTeamMemberStatus.ACTIVE,
        ).first()
        return getattr(profile, "facility", None)

    @classmethod
    @transaction.atomic
    def update_profile(cls, *, facility, actor, data):
        for field, value in data.items():
            setattr(facility, field, value)
        facility.save()
        log_action(action=AuditAction.UPDATE, actor=actor, target=facility, metadata={"event": "facility_profile_updated"})
        return facility


class FacilityTeamService:
    @staticmethod
    def has_permission(*, user, facility, permission_key):
        if getattr(user, "role", "") == UserRole.SUPER_ADMIN:
            return True
        if getattr(user, "organization_id", None) != facility.organization_id:
            return False
        if getattr(user, "role", "") == UserRole.FACILITY_ADMIN:
            return True
        profile = FacilityStaffProfile.objects.select_related("role").filter(
            user=user,
            facility=facility,
            is_active=True,
            status=FacilityTeamMemberStatus.ACTIVE,
        ).first()
        if not profile or not profile.role_id:
            return False
        return profile.role.permissions.filter(permission_key=permission_key, allowed=True).exists()

    @staticmethod
    def protected_permissions_for_category(professional_category):
        return {
            permission
            for permission, categories in FACILITY_PROTECTED_PERMISSION_RULES.items()
            if professional_category not in categories
        }

    @staticmethod
    def validate_permission_assignment(*, professional_category, permission_keys):
        blocked_permissions = [
            permission_key
            for permission_key in permission_keys
            if permission_key in FACILITY_PROTECTED_PERMISSION_RULES
            and professional_category not in FACILITY_PROTECTED_PERMISSION_RULES[permission_key]
        ]
        if blocked_permissions:
            allowed_categories = {
                permission_key: sorted(FACILITY_PROTECTED_PERMISSION_RULES[permission_key])
                for permission_key in blocked_permissions
            }
            raise ValueError(
                {
                    "blocked_permissions": blocked_permissions,
                    "allowed_categories": allowed_categories,
                }
            )

    @classmethod
    @transaction.atomic
    def ensure_default_roles(cls, *, facility, actor=None):
        roles = []
        for definition in DEFAULT_FACILITY_ROLE_TEMPLATES:
            role, created = FacilityRole.objects.update_or_create(
                facility=facility,
                name=definition["name"],
                defaults={
                    "description": definition["description"],
                    "professional_category": definition["professional_category"],
                    "is_system_default": True,
                    "is_custom": False,
                    "created_by": actor,
                },
            )
            cls.validate_permission_assignment(
                professional_category=definition["professional_category"],
                permission_keys=definition["permissions"],
            )
            role.permissions.exclude(permission_key__in=definition["permissions"]).delete()
            for permission_key in definition["permissions"]:
                FacilityRolePermission.objects.update_or_create(
                    role=role,
                    permission_key=permission_key,
                    defaults={"allowed": True},
                )
            roles.append(role)
            if created:
                log_action(
                    action=AuditAction.CREATE,
                    actor=actor,
                    target=role,
                    metadata={"event": "facility_default_role_seeded", "facility_role_code": definition["code"]},
                )
        return roles


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

    @staticmethod
    def federal_minimum_rules():
        """Active mandatory federal facility accreditation criteria, if any are published."""
        from apps.standards.services import ActivePolicyRuleService

        active = ActivePolicyRuleService.get_active_policy_version()
        if not active:
            return []
        return list(active.facility_requirement_rules.filter(mandatory=True))

    @classmethod
    def assert_meets_federal_minimum(cls, application):
        """Block approval when the federal minimum accreditation criteria are not satisfied.

        Federal criteria are enforced as the state-level baseline: when the Federal
        Ministry has published mandatory facility requirement rules, the application's
        accreditation checklist (which encodes the federal minimum) must be complete.
        """
        from rest_framework.exceptions import ValidationError

        if not cls.federal_minimum_rules():
            return
        if not application.checklist_complete:
            raise ValidationError(
                "This facility does not meet the Federal minimum accreditation criteria. "
                "All mandatory accreditation checklist items must be satisfied before approval."
            )

    @classmethod
    @transaction.atomic
    def approve(cls, *, application, reviewer, review_comment=""):
        cls.assert_meets_federal_minimum(application)
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
