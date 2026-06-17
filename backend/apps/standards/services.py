from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.locations.models import State
from apps.notifications.models import (
    NotificationCategory,
    NotificationChannel,
    NotificationPriority,
)
from apps.notifications.services import NotificationService

from .models import (
    Approval,
    ApprovalStatus,
    ImpactLevel,
    PolicyVersion,
    PolicyVersionStatus,
    StateAcknowledgement,
)

User = get_user_model()

ACTIVE_STANDARDS_CACHE_VERSION_KEY = "standards:active:cache_version"


def bump_active_standards_cache_version():
    current = cache.get(ACTIVE_STANDARDS_CACHE_VERSION_KEY, 1)
    cache.set(ACTIVE_STANDARDS_CACHE_VERSION_KEY, int(current) + 1, None)


def _recipient_for_user(user):
    if not user:
        return []
    return [{
        "user_id": str(user.id),
        "email": user.email or "",
        "phone": user.phone or "",
        "recipient_type": user.role or "",
        "organization_id": str(user.organization_id) if user.organization_id else "",
        "organization_unit_id": str(user.unit_id) if user.unit_id else "",
    }]


def _recipients_for_roles(roles):
    users = User.objects.filter(is_active=True, role__in=roles)
    return [
        {
            "user_id": str(user.id),
            "email": user.email or "",
            "phone": user.phone or "",
            "recipient_type": user.role or "",
            "organization_id": str(user.organization_id) if user.organization_id else "",
            "organization_unit_id": str(user.unit_id) if user.unit_id else "",
        }
        for user in users
    ]


def _send_standards_notification(*, title, message, recipients, action_url="", priority=NotificationPriority.NORMAL, related_object_id=""):
    if not recipients:
        return
    NotificationService.send(
        category=NotificationCategory.SYSTEM,
        priority=priority,
        title=title,
        message=message,
        action_url=action_url,
        recipients=recipients,
        channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
        related_object_type="StandardsPolicy",
        related_object_id=str(related_object_id) if related_object_id else "",
    )


class PolicyVersionService:

    @classmethod
    def _validate_publishable(cls, policy_version):
        has_cert_template = policy_version.certificate_templates.exists()
        has_test_rule = policy_version.medical_test_rules.exists()
        has_validity_rule = policy_version.certificate_validity_rules.exists()
        has_reporting_template = policy_version.reporting_templates.exists()

        errors = []
        if not has_cert_template:
            errors.append("At least one certificate template is required.")
        if not has_test_rule:
            errors.append("At least one medical test rule group is required.")
        if not has_validity_rule:
            errors.append("At least one certificate validity rule is required.")
        if not has_reporting_template:
            errors.append("At least one reporting template is required.")
        if errors:
            raise ValueError(" ".join(errors))

    @classmethod
    @transaction.atomic
    def submit_for_review(cls, policy_version, user, request=None):
        if policy_version.status != PolicyVersionStatus.DRAFT:
            raise ValueError("Only draft versions can be submitted for review.")

        cls._validate_publishable(policy_version)

        old_status = policy_version.status
        policy_version.status = PolicyVersionStatus.UNDER_REVIEW
        policy_version.submitted_by = user
        policy_version.submitted_at = timezone.now()
        policy_version.save()

        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=user,
            target=policy_version,
            old_value={"status": old_status},
            new_value={"status": PolicyVersionStatus.UNDER_REVIEW},
            metadata={"event": "policy_version_submitted_for_review"},
            request=request,
        )

        Approval.objects.create(
            entity_type="PolicyVersion",
            entity_id=policy_version.id,
            requested_by=user,
            impact_level=ImpactLevel.HIGH,
            request_comment=f"Policy version {policy_version.version_code} submitted for review.",
        )
        _send_standards_notification(
            title="Policy version submitted for review",
            message=f"{policy_version.version_code} has been submitted for approval.",
            recipients=_recipients_for_roles(["super_admin", "federal_admin"]),
            action_url=f"/federal/standards-policy/policy-governance/policy-versions/{policy_version.id}",
            priority=NotificationPriority.HIGH,
            related_object_id=policy_version.id,
        )

        return policy_version

    @classmethod
    @transaction.atomic
    def approve(cls, policy_version, user, comment="", request=None):
        if policy_version.status != PolicyVersionStatus.UNDER_REVIEW:
            raise ValueError("Only versions under review can be approved.")

        old_status = policy_version.status
        policy_version.status = PolicyVersionStatus.APPROVED
        policy_version.approved_by = user
        policy_version.approved_at = timezone.now()
        policy_version.save()

        approval = Approval.objects.filter(
            entity_type="PolicyVersion",
            entity_id=policy_version.id,
            status=ApprovalStatus.PENDING,
        ).first()
        if approval:
            approval.approver = user
            approval.status = ApprovalStatus.APPROVED
            approval.approval_comment = comment
            approval.approved_at = timezone.now()
            approval.save()

        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=user,
            target=policy_version,
            old_value={"status": old_status},
            new_value={"status": PolicyVersionStatus.APPROVED},
            metadata={"event": "policy_version_approved", "comment": comment},
            request=request,
        )
        _send_standards_notification(
            title="Policy version approved",
            message=f"{policy_version.version_code} has been approved. {comment}".strip(),
            recipients=_recipient_for_user(policy_version.submitted_by),
            action_url=f"/federal/standards-policy/policy-governance/policy-versions/{policy_version.id}",
            priority=NotificationPriority.NORMAL,
            related_object_id=policy_version.id,
        )

        return policy_version

    @classmethod
    @transaction.atomic
    def return_for_correction(cls, policy_version, user, comment="", request=None):
        if policy_version.status != PolicyVersionStatus.UNDER_REVIEW:
            raise ValueError("Only versions under review can be returned.")

        old_status = policy_version.status
        policy_version.status = PolicyVersionStatus.RETURNED
        policy_version.save()

        approval = Approval.objects.filter(
            entity_type="PolicyVersion",
            entity_id=policy_version.id,
            status=ApprovalStatus.PENDING,
        ).first()
        if approval:
            approval.reviewer = user
            approval.status = ApprovalStatus.RETURNED
            approval.review_comment = comment
            approval.reviewed_at = timezone.now()
            approval.save()

        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=user,
            target=policy_version,
            old_value={"status": old_status},
            new_value={"status": PolicyVersionStatus.RETURNED},
            metadata={"event": "policy_version_returned", "comment": comment},
            request=request,
        )
        _send_standards_notification(
            title="Policy version returned for correction",
            message=f"{policy_version.version_code} was returned for correction. {comment}".strip(),
            recipients=_recipient_for_user(policy_version.submitted_by),
            action_url=f"/federal/standards-policy/policy-governance/policy-versions/{policy_version.id}",
            priority=NotificationPriority.HIGH,
            related_object_id=policy_version.id,
        )

        return policy_version

    @classmethod
    @transaction.atomic
    def reject(cls, policy_version, user, comment="", request=None):
        if policy_version.status != PolicyVersionStatus.UNDER_REVIEW:
            raise ValueError("Only versions under review can be rejected.")

        old_status = policy_version.status
        policy_version.status = PolicyVersionStatus.RETURNED
        policy_version.save()

        approval = Approval.objects.filter(
            entity_type="PolicyVersion",
            entity_id=policy_version.id,
            status=ApprovalStatus.PENDING,
        ).first()
        if approval:
            approval.reviewer = user
            approval.status = ApprovalStatus.REJECTED
            approval.review_comment = comment
            approval.reviewed_at = timezone.now()
            approval.save()

        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=user,
            target=policy_version,
            old_value={"status": old_status},
            new_value={"status": PolicyVersionStatus.RETURNED},
            metadata={"event": "policy_version_rejected", "comment": comment},
            request=request,
        )
        _send_standards_notification(
            title="Policy version rejected",
            message=f"{policy_version.version_code} was rejected. {comment}".strip(),
            recipients=_recipient_for_user(policy_version.submitted_by),
            action_url=f"/federal/standards-policy/policy-governance/policy-versions/{policy_version.id}",
            priority=NotificationPriority.HIGH,
            related_object_id=policy_version.id,
        )

        return policy_version

    @classmethod
    @transaction.atomic
    def publish(cls, policy_version, user, effective_date=None, comment="", request=None):
        if policy_version.status not in (
            PolicyVersionStatus.APPROVED, PolicyVersionStatus.SCHEDULED,
        ):
            raise ValueError("Only approved or scheduled versions can be published.")

        cls._validate_publishable(policy_version)

        if effective_date and effective_date > timezone.now():
            policy_version.status = PolicyVersionStatus.SCHEDULED
            policy_version.effective_start_date = effective_date
            policy_version.save()

            log_action(
                action=AuditAction.WORKFLOW_TRANSITION,
                actor=user,
                target=policy_version,
                old_value={"status": PolicyVersionStatus.APPROVED},
                new_value={"status": PolicyVersionStatus.SCHEDULED},
                metadata={
                    "event": "policy_version_scheduled",
                    "effective_date": str(effective_date),
                },
                request=request,
            )
            return policy_version

        PolicyVersion.objects.filter(
            status=PolicyVersionStatus.ACTIVE,
        ).update(
            status=PolicyVersionStatus.RETIRED,
            retired_at=timezone.now(),
            retired_by=user,
        )

        old_status = policy_version.status
        policy_version.status = PolicyVersionStatus.ACTIVE
        policy_version.published_by = user
        policy_version.published_at = timezone.now()
        if not policy_version.effective_start_date:
            policy_version.effective_start_date = timezone.now()
        policy_version.save()

        if policy_version.requires_state_acknowledgement:
            cls._create_state_acknowledgements(policy_version)
            _send_standards_notification(
                title="State acknowledgement required",
                message=f"{policy_version.version_code} is active and requires state acknowledgement.",
                recipients=_recipients_for_roles(["state_admin"]),
                action_url=f"/federal/standards-policy/policy-governance/policy-versions/{policy_version.id}",
                priority=NotificationPriority.HIGH,
                related_object_id=policy_version.id,
            )
        bump_active_standards_cache_version()

        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=user,
            target=policy_version,
            old_value={"status": old_status},
            new_value={"status": PolicyVersionStatus.ACTIVE},
            metadata={"event": "policy_version_published", "comment": comment},
            request=request,
        )

        return policy_version

    @classmethod
    @transaction.atomic
    def retire(cls, policy_version, user, request=None):
        if policy_version.status != PolicyVersionStatus.ACTIVE:
            raise ValueError("Only active versions can be retired.")

        old_status = policy_version.status
        policy_version.status = PolicyVersionStatus.RETIRED
        policy_version.retired_by = user
        policy_version.retired_at = timezone.now()
        policy_version.save()

        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=user,
            target=policy_version,
            old_value={"status": old_status},
            new_value={"status": PolicyVersionStatus.RETIRED},
            metadata={"event": "policy_version_retired"},
            request=request,
        )

        return policy_version

    @classmethod
    @transaction.atomic
    def clone(cls, source_version, user, new_version_code, new_title, request=None):
        new_version = PolicyVersion.objects.create(
            version_code=new_version_code,
            title=new_title,
            description=source_version.description,
            version_type=source_version.version_type,
            change_summary=f"Cloned from {source_version.version_code}",
            requires_state_acknowledgement=source_version.requires_state_acknowledgement,
            created_by=user,
        )

        related_models = [
            ("food_handler_categories", ["policy_version", "id", "created_at", "updated_at", "status", "created_by"]),
            ("establishment_categories", ["policy_version", "id", "created_at", "updated_at", "status", "created_by"]),
            ("medical_test_rules", ["policy_version", "id", "created_at", "updated_at", "status", "created_by"]),
            ("physical_examination_rules", ["policy_version", "id", "created_at", "updated_at", "status", "created_by"]),
            ("vaccination_rules", ["policy_version", "id", "created_at", "updated_at", "status", "created_by"]),
            ("certificate_templates", ["policy_version", "id", "created_at", "updated_at", "status", "created_by"]),
            ("certificate_validity_rules", ["policy_version", "id", "created_at", "updated_at", "status", "created_by"]),
            ("return_to_work_rules", ["policy_version", "id", "created_at", "updated_at", "status", "created_by"]),
            ("facility_requirement_rules", ["policy_version", "id", "created_at", "updated_at", "status", "created_by"]),
            ("reporting_templates", ["policy_version", "id", "created_at", "updated_at", "status", "created_by"]),
            ("me_indicators", ["policy_version", "id", "created_at", "updated_at", "status", "created_by"]),
            ("state_configuration_controls", ["policy_version", "id", "created_at", "updated_at", "created_by"]),
        ]

        for relation_name, exclude_fields in related_models:
            source_items = getattr(source_version, relation_name).all()
            for item in source_items:
                item.pk = None
                item.id = None
                item.policy_version = new_version
                item.created_by = user
                if hasattr(item, "status"):
                    item.status = "draft"
                item.save()

        log_action(
            action=AuditAction.CREATE,
            actor=user,
            target=new_version,
            metadata={
                "event": "policy_version_cloned",
                "source_version": str(source_version.id),
                "source_code": source_version.version_code,
            },
            request=request,
        )

        return new_version

    @classmethod
    @transaction.atomic
    def archive(cls, policy_version, user, request=None):
        if policy_version.status != PolicyVersionStatus.RETIRED:
            raise ValueError("Only retired versions can be archived.")

        old_status = policy_version.status
        policy_version.status = PolicyVersionStatus.ARCHIVED
        policy_version.save()

        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=user,
            target=policy_version,
            old_value={"status": old_status},
            new_value={"status": PolicyVersionStatus.ARCHIVED},
            metadata={"event": "policy_version_archived"},
            request=request,
        )

        return policy_version

    @classmethod
    def _create_state_acknowledgements(cls, policy_version):
        states = State.objects.all()
        acknowledgements = [
            StateAcknowledgement(
                policy_version=policy_version,
                state=state,
            )
            for state in states
        ]
        StateAcknowledgement.objects.bulk_create(
            acknowledgements, ignore_conflicts=True,
        )
