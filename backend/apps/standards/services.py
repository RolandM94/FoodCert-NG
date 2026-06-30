from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models, transaction
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
    CertificateTemplate,
    CertificateValidityRule,
    FacilityRequirementCategory,
    FacilityRequirementRule,
    ImpactLevel,
    PolicyVersion,
    PolicyVersionStatus,
    ReturnToWorkRule,
    StandardStatus,
    StateAcknowledgement,
    TemplateStatus,
)

User = get_user_model()

ACTIVE_STANDARDS_CACHE_VERSION_KEY = "standards:active:cache_version"


class ActivePolicyRuleError(ValueError):
    pass


def bump_active_standards_cache_version():
    current = cache.get(ACTIVE_STANDARDS_CACHE_VERSION_KEY, 1)
    cache.set(ACTIVE_STANDARDS_CACHE_VERSION_KEY, int(current) + 1, None)


class ActivePolicyRuleService:
    VALIDITY_STANDARD_CODE = "FH-VALIDITY-2024-001"
    FACILITY_STANDARD_CODE = "FH-FAC-2024-001"
    CERTIFICATE_STANDARD_CODE = "FH-CERT-2024-001"
    RETURN_TO_WORK_STANDARD_CODE = "FH-RTW-2024-001"

    STANDARD_RESOLVERS = {
        VALIDITY_STANDARD_CODE: "_resolve_validity_standard",
        FACILITY_STANDARD_CODE: "_resolve_facility_standard",
        CERTIFICATE_STANDARD_CODE: "_resolve_certificate_standard",
        RETURN_TO_WORK_STANDARD_CODE: "_resolve_return_to_work_standard",
    }

    @classmethod
    def get_active_policy_version(cls):
        now = timezone.now()
        return PolicyVersion.objects.filter(
            status=PolicyVersionStatus.ACTIVE,
        ).filter(
            models.Q(effective_start_date__isnull=True) | models.Q(effective_start_date__lte=now),
        ).filter(
            models.Q(effective_end_date__isnull=True) | models.Q(effective_end_date__gte=now),
        ).order_by("-effective_start_date", "-published_at", "-created_at").first()

    @classmethod
    def get_active_policy_standard_by_code(cls, standard_code):
        policy_version = cls.get_active_policy_version()
        if not policy_version:
            raise ActivePolicyRuleError("Active policy rule not found for this KPI calculation.")

        resolver_name = cls.STANDARD_RESOLVERS.get(standard_code)
        if not resolver_name:
            raise ActivePolicyRuleError("Active policy rule not found for this KPI calculation.")

        resolver = getattr(cls, resolver_name)
        return resolver(policy_version)

    @classmethod
    def get_policy_rule_parameter(cls, standard_code, parameter_key):
        standard = cls.get_active_policy_standard_by_code(standard_code)
        parameters = standard.get("parameters", {})
        if parameter_key not in parameters:
            raise ActivePolicyRuleError("Active policy rule not found for this KPI calculation.")
        return parameters[parameter_key]

    @classmethod
    def _resolve_validity_standard(cls, policy_version):
        rule = CertificateValidityRule.objects.filter(
            policy_version=policy_version,
            status=TemplateStatus.ACTIVE,
        ).order_by("-created_at").first()
        if not rule:
            raise ActivePolicyRuleError("Active policy rule not found for this KPI calculation.")
        return {
            "policy_version_id": str(policy_version.id),
            "policy_standard_code": cls.VALIDITY_STANDARD_CODE,
            "policy_standard_id": str(rule.id),
            "parameters": {
                "certificate_validity_days": rule.certificate_validity_days,
                "certificate_validity_months": cls._months_from_days(rule.certificate_validity_days),
                "assessment_validity_days": rule.routine_assessment_interval_days,
                "assessment_validity_months": cls._months_from_days(rule.routine_assessment_interval_days),
                "renewal_window_days": rule.renewal_window_days,
                "grace_period_days": rule.grace_period_days,
                "illness_suspension_enabled": rule.illness_suspension_enabled,
                "emergency_revalidation_enabled": rule.emergency_revalidation_enabled,
            },
        }

    @classmethod
    def _resolve_facility_standard(cls, policy_version):
        rules = FacilityRequirementRule.objects.filter(
            policy_version=policy_version,
            status=StandardStatus.ACTIVE,
        ).order_by("requirement_name")
        if not rules.exists():
            raise ActivePolicyRuleError("Active policy rule not found for this KPI calculation.")
        reaccreditation_rule = rules.filter(
            category=FacilityRequirementCategory.REACCREDITATION,
            renewal_required=True,
            renewal_interval_days__isnull=False,
        ).order_by("-renewal_interval_days", "-created_at").first()
        if not reaccreditation_rule:
            raise ActivePolicyRuleError("Active policy rule not found for this KPI calculation.")
        return {
            "policy_version_id": str(policy_version.id),
            "policy_standard_code": cls.FACILITY_STANDARD_CODE,
            "policy_standard_id": str(reaccreditation_rule.id),
            "parameters": {
                "reaccreditation_interval_days": reaccreditation_rule.renewal_interval_days,
                "reaccreditation_interval_months": cls._months_from_days(reaccreditation_rule.renewal_interval_days),
                "mandatory_requirement_count": rules.filter(mandatory=True).count(),
            },
        }

    @classmethod
    def _resolve_certificate_standard(cls, policy_version):
        template = CertificateTemplate.objects.filter(
            policy_version=policy_version,
            status=TemplateStatus.ACTIVE,
        ).order_by("-created_at").first()
        if not template:
            raise ActivePolicyRuleError("Active policy rule not found for this KPI calculation.")
        qr_config = template.qr_payload_config or {}
        required_fields = template.required_fields or []
        requires_qr_code = "qr_code" in required_fields or bool(qr_config.get("verification_enabled"))
        digitally_verifiable = bool(qr_config.get("verification_enabled")) and bool(qr_config.get("central_database_validation"))
        return {
            "policy_version_id": str(policy_version.id),
            "policy_standard_code": cls.CERTIFICATE_STANDARD_CODE,
            "policy_standard_id": str(template.id),
            "parameters": {
                "requires_qr_code": requires_qr_code,
                "certificate_must_be_digitally_verifiable": digitally_verifiable,
                "verification_enabled": bool(qr_config.get("verification_enabled")),
                "central_database_validation": bool(qr_config.get("central_database_validation")),
            },
        }

    @classmethod
    def _resolve_return_to_work_standard(cls, policy_version):
        rules = ReturnToWorkRule.objects.filter(
            policy_version=policy_version,
            status=StandardStatus.ACTIVE,
        ).order_by("condition_name")
        if not rules.exists():
            raise ActivePolicyRuleError("Active policy rule not found for this KPI calculation.")
        default_rule = rules.filter(condition_code="RTW-EXCLUDE-48H").first()
        if not default_rule:
            default_rule = rules.filter(default_exclusion_hours__gt=0).order_by("default_exclusion_hours").first()
        if not default_rule:
            raise ActivePolicyRuleError("Active policy rule not found for this KPI calculation.")
        return {
            "policy_version_id": str(policy_version.id),
            "policy_standard_code": cls.RETURN_TO_WORK_STANDARD_CODE,
            "policy_standard_id": str(default_rule.id),
            "parameters": {
                "standard_exclusion_period_hours_after_symptoms_stop": default_rule.default_exclusion_hours,
                "specific_infection_clearance_rules": [
                    {
                        "condition_code": rule.condition_code,
                        "condition_name": rule.condition_name,
                        "default_exclusion_hours": rule.default_exclusion_hours,
                        "requires_medical_clearance": rule.requires_medical_clearance,
                        "requires_lab_clearance": rule.requires_lab_clearance,
                        "negative_samples_required": rule.negative_samples_required,
                        "sample_interval_hours": rule.sample_interval_hours,
                        "requires_health_authority_approval": rule.requires_health_authority_approval,
                        "employer_acknowledgement_required": rule.employer_acknowledgement_required,
                        "clearance_document_required": rule.clearance_document_required,
                    }
                    for rule in rules
                ],
            },
        }

    @staticmethod
    def _months_from_days(days):
        if days in (None, ""):
            return None
        return int(round(int(days) / 30))


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
            policy_category=source_version.policy_category,
            legal_basis=source_version.legal_basis,
            scope=source_version.scope,
            affected_entities=source_version.affected_entities,
            review_date=source_version.review_date,
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
