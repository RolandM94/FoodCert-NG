import hashlib
import re
from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.accounts.models import UserRole
from apps.assessments.models import (
    AssessmentFormQuestion,
    AssessmentFormResponse,
    AssessmentFormResponseStatus,
    AssessmentFormTemplateAdoption,
    AssessmentFormTemplateSnapshot,
    AssessmentFormScope,
    AssessmentFormSection,
    AssessmentFormStatus,
    AssessmentFormTemplate,
    AssessmentFormType,
    AssessmentOwnerLevel,
    AssessmentPrivacyClassification,
    AssessmentQuestionType,
    AssessmentRespondentRole,
    AssessmentRequirementSet,
    AssessmentRequirementSetStatus,
    AssessmentType,
    AssessmentStatus,
    AppointmentStatus,
    FitnessDecision,
    HealthDeclaration,
    IdentityVerificationStatus,
    MedicalAssessment,
    PhysicalExamination,
    StepStatus,
)
from apps.assessments.permissions import can_approve_assessment_form_template, can_manage_assessment_form_template, can_manage_assessment_requirement_set
from apps.audit.models import AuditAction, AuditLog
from apps.audit.services import log_action
from apps.food_handlers.models import FoodHandlerStatus
from apps.illness.models import ClearanceStatus, IllnessReport, SuspectedCondition
from apps.nin_verification.models import NINVerificationStatus
from apps.notifications.models import Notification, NotificationCategory
from apps.notifications.services import NotificationService
from apps.organizations.models import OrganizationUnitType
from apps.payments.models import PaymentStatus
from apps.policy.models import NationalPolicyConfig
from apps.reports.models import GeneratedReport, GeneratedReportStatus, ReportFormat, ReportType

User = get_user_model()


def assessment_audit_metadata(*, event, actor=None, entity=None, owner_level="", reason="", **extra):
    metadata = {
        "event": event,
        "actor_user_id": str(actor.id) if actor and getattr(actor, "id", None) else "",
        "actor_role": getattr(actor, "role", ""),
        "owner_level": owner_level or getattr(entity, "owner_level", ""),
        "entity_type": entity.__class__.__name__ if entity is not None else "",
        "entity_id": str(getattr(entity, "id", "")) if entity is not None else "",
        "reason": reason,
        "timestamp": timezone.now().isoformat(),
    }
    metadata.update(extra)
    return metadata


def template_audit_snapshot(template):
    return {
        "id": str(template.id),
        "name": template.name,
        "form_type": template.form_type,
        "scope": template.scope,
        "owner_level": template.owner_level,
        "owner_id": str(template.owner_id) if template.owner_id else "",
        "status": template.status,
        "version": template.version,
        "parent_template_id": str(template.parent_template_id) if template.parent_template_id else "",
        "base_template_id": str(template.base_template_id) if template.base_template_id else "",
    }


def section_audit_snapshot(section):
    return {
        "id": str(section.id),
        "template_id": str(section.template_id),
        "key": section.key,
        "title": section.title,
        "owner_level": section.owner_level,
        "owner_id": str(section.owner_id) if section.owner_id else "",
        "locked": section.locked,
    }


def question_audit_snapshot(question):
    return {
        "id": str(question.id),
        "section_id": str(question.section_id),
        "template_id": str(question.section.template_id),
        "key": question.key,
        "label": question.label,
        "owner_level": question.owner_level,
        "owner_id": str(question.owner_id) if question.owner_id else "",
        "locked": question.locked,
    }


def declaration_audit_snapshot(declaration):
    return {
        "id": str(declaration.id),
        "assessment_id": str(declaration.assessment_id),
        "version": declaration.version,
        "risk_flag": declaration.risk_flag,
        "is_locked": declaration.is_locked,
        "submitted_at": declaration.submitted_at.isoformat() if declaration.submitted_at else "",
        "validated_at": declaration.validated_at.isoformat() if declaration.validated_at else "",
        "clarification_requested_at": declaration.clarification_requested_at.isoformat() if declaration.clarification_requested_at else "",
    }


def template_creation_event(template):
    if template.form_type == AssessmentFormType.HEALTH_DECLARATION and template.scope == AssessmentFormScope.NATIONAL:
        return "federal_template_created"
    return "assessment_form_created"


def field_addition_event(template):
    if template.form_type != AssessmentFormType.HEALTH_DECLARATION:
        return ""
    if template.scope == AssessmentFormScope.STATE:
        return "state_field_added"
    if template.scope == AssessmentFormScope.FACILITY:
        return "facility_field_added"
    return ""


def ensure_approved_facility(facility):
    if not facility.can_conduct_assessments:
        raise ValidationError("Only approved facilities can conduct medical assessments.")


def ensure_doctor_for_facility(user, facility):
    if user.role != UserRole.DOCTOR:
        raise PermissionDenied("Only doctors can perform this assessment action.")
    if user.organization_id != facility.organization_id:
        raise PermissionDenied("Doctors can only act for their own facility.")


def ensure_clinical_staff_for_facility(user, facility):
    if user.role not in {UserRole.DOCTOR, UserRole.LAB_STAFF}:
        raise PermissionDenied("Only facility clinical staff can perform this action.")
    if user.organization_id != facility.organization_id:
        raise PermissionDenied("Clinical staff can only act for their own facility.")


def ensure_facility_admin_for_facility(user, facility):
    if user.role != UserRole.FACILITY_ADMIN:
        raise PermissionDenied("Only facility admins can manage facility appointments.")
    if user.organization_id != facility.organization_id:
        raise PermissionDenied("Facility admins can only manage their own facility.")


def ensure_assigned_doctor_for_assessment(user, assessment):
    ensure_doctor_for_facility(user, assessment.facility)
    if assessment.doctor_id != user.id:
        raise PermissionDenied("Doctors can only perform clinical actions on assigned assessments.")


def ensure_assigned_or_override_doctor_for_assessment(user, assessment):
    if user.role == UserRole.FACILITY_ADMIN and user.organization_id == assessment.facility.organization_id:
        return
    ensure_assigned_doctor_for_assessment(user, assessment)


def ensure_assigned_or_override_lab_staff_for_assessment(user, assessment):
    if user.role == UserRole.FACILITY_ADMIN and user.organization_id == assessment.facility.organization_id:
        return
    if user.role != UserRole.LAB_STAFF or user.organization_id != assessment.facility.organization_id:
        raise PermissionDenied("Only assigned lab staff can perform this action.")
    if assessment.assigned_lab_staff_id:
        if assessment.assigned_lab_staff_id != user.id:
            raise PermissionDenied("This assessment is assigned to another lab staff member.")
        return
    if assessment.assigned_lab_unit_id and getattr(user, "unit_id", None) == assessment.assigned_lab_unit_id:
        return
    raise PermissionDenied("This assessment has not been assigned to you or your lab unit.")


class AssessmentFormValidationService:
    RISK_FLAGS = {
        "medical_review_required",
        "lab_test_required",
        "vaccination_required",
        "temporary_exclusion_recommended",
        "return_to_work_required",
        "public_health_clearance_required",
        "state_review_required",
    }
    CONDITION_OPERATORS = {
        "equals",
        "not_equals",
        "in",
        "not_in",
        "contains",
        "greater_than",
        "greater_than_or_equal",
        "less_than",
        "less_than_or_equal",
        "is_truthy",
        "is_falsy",
        "exists",
    }
    TEXT_TYPES = {
        AssessmentQuestionType.SHORT_TEXT,
        AssessmentQuestionType.LONG_TEXT,
        AssessmentQuestionType.PHONE,
        AssessmentQuestionType.EMAIL,
        AssessmentQuestionType.CLINICAL_NOTE,
        AssessmentQuestionType.DOCTOR_ONLY_NOTE,
        AssessmentQuestionType.LAB_ONLY_NOTE,
    }
    NUMBER_TYPES = {
        AssessmentQuestionType.NUMBER,
        AssessmentQuestionType.TEMPERATURE,
        AssessmentQuestionType.WEIGHT,
        AssessmentQuestionType.HEIGHT,
        AssessmentQuestionType.PULSE_RATE,
        AssessmentQuestionType.VACCINE_DOSE,
    }
    SINGLE_CHOICE_TYPES = {
        AssessmentQuestionType.SINGLE_CHOICE,
        AssessmentQuestionType.DROPDOWN,
        AssessmentQuestionType.LAB_RESULT_STATUS,
    }
    MULTIPLE_CHOICE_TYPES = {
        AssessmentQuestionType.MULTIPLE_CHOICE,
        AssessmentQuestionType.SYMPTOM_CHECKLIST,
        AssessmentQuestionType.EXPOSURE_HISTORY,
    }
    DATE_TYPES = {AssessmentQuestionType.DATE, AssessmentQuestionType.VACCINATION_DATE}
    FACILITY_ALLOWED_FORM_TYPES = {AssessmentFormType.FACILITY_INTAKE}
    FACILITY_ALLOWED_PRIVACY_CLASSIFICATIONS = {
        AssessmentPrivacyClassification.MEDICAL_SENSITIVE,
        AssessmentPrivacyClassification.RESTRICTED_MEDICAL,
        AssessmentPrivacyClassification.INTERNAL_ADMINISTRATIVE,
        AssessmentPrivacyClassification.REGULATORY_RESTRICTED,
    }
    MISSING = object()

    @classmethod
    def _snapshot_questions(cls, snapshot):
        for section in snapshot.get("sections", []):
            for question in section.get("questions", []):
                yield section, question

    @classmethod
    def _validate_condition(cls, condition, *, question_keys, label):
        if not condition:
            return
        if not isinstance(condition, dict):
            raise ValidationError({label: "Conditional logic must be an object."})
        groups = [key for key in ("all", "any") if key in condition]
        if groups:
            if len(groups) != 1 or len(condition) != 1:
                raise ValidationError({label: "Conditional groups must contain exactly one of 'all' or 'any'."})
            conditions = condition[groups[0]]
            if not isinstance(conditions, list) or not conditions:
                raise ValidationError({label: f"Conditional '{groups[0]}' must contain at least one rule."})
            for child in conditions:
                cls._validate_condition(child, question_keys=question_keys, label=label)
            return
        question = condition.get("question")
        if question and question not in question_keys:
            raise ValidationError({label: f"Conditional logic references unknown question '{question}'."})
        operator = condition.get("operator", "equals")
        if operator not in cls.CONDITION_OPERATORS:
            raise ValidationError({label: f"Unsupported conditional operator '{operator}'."})
        if not question and not condition.get("use_current_answer"):
            raise ValidationError({label: "Conditional logic must reference a question."})
        if operator not in {"is_truthy", "is_falsy", "exists"} and "value" not in condition:
            raise ValidationError({label: f"Conditional operator '{operator}' requires a value."})
        if operator in {"in", "not_in"} and not isinstance(condition.get("value"), list):
            raise ValidationError({label: f"Conditional operator '{operator}' requires a list value."})

    @classmethod
    def _validate_risk_rules(cls, rules, *, question_keys, label):
        if not rules:
            return
        rules = rules if isinstance(rules, list) else [rules]
        if not all(isinstance(rule, dict) for rule in rules):
            raise ValidationError({label: "Risk flag rules must be an object or a list of objects."})
        for rule in rules:
            flags = rule.get("flags", [])
            if not isinstance(flags, list) or not flags:
                raise ValidationError({label: "Each risk rule must contain at least one flag."})
            invalid = sorted(set(flags) - cls.RISK_FLAGS)
            if invalid:
                raise ValidationError({label: f"Unsupported risk flags: {', '.join(invalid)}."})
            cls._validate_condition(
                rule.get("when", {"use_current_answer": True, "operator": "is_truthy"}),
                question_keys=question_keys,
                label=label,
            )

    @classmethod
    def validate_template(cls, template):
        questions = list(template.sections.prefetch_related("questions").values_list("questions__key", flat=True))
        question_keys = {key for key in questions if key}
        for section in template.sections.prefetch_related("questions").all():
            cls._validate_condition(section.visibility_rules, question_keys=question_keys, label=f"section:{section.key}")
            for question in section.questions.all():
                label = f"question:{question.key}"
                if not isinstance(question.validation_rules, dict):
                    raise ValidationError({label: "Validation rules must be an object."})
                if not isinstance(question.conditional_logic, dict):
                    raise ValidationError({label: "Conditional logic must be an object."})
                if question.question_type in cls.SINGLE_CHOICE_TYPES | cls.MULTIPLE_CHOICE_TYPES and not question.options:
                    raise ValidationError({label: "Choice questions must contain at least one option."})
                for condition_name in ("visible_if", "required_if"):
                    cls._validate_condition(question.conditional_logic.get(condition_name), question_keys=question_keys, label=label)
                cls._validate_risk_rules(question.risk_flag_rules, question_keys=question_keys, label=label)
                minimum = question.validation_rules.get("min_value")
                maximum = question.validation_rules.get("max_value")
                try:
                    if minimum is not None:
                        Decimal(str(minimum))
                    if maximum is not None:
                        Decimal(str(maximum))
                    if minimum is not None and maximum is not None and Decimal(str(minimum)) > Decimal(str(maximum)):
                        raise ValidationError({label: "Minimum value cannot exceed maximum value."})
                except InvalidOperation as exc:
                    raise ValidationError({label: "Minimum and maximum values must be numeric."}) from exc
                for length_rule in ("min_length", "max_length", "max_size"):
                    if length_rule in question.validation_rules and (
                        not isinstance(question.validation_rules[length_rule], int)
                        or question.validation_rules[length_rule] < 0
                    ):
                        raise ValidationError({label: f"'{length_rule}' must be a non-negative integer."})
                for date_rule in ("date_before", "date_after"):
                    if question.validation_rules.get(date_rule):
                        try:
                            date.fromisoformat(question.validation_rules[date_rule])
                        except (TypeError, ValueError) as exc:
                            raise ValidationError({label: f"'{date_rule}' must be an ISO date."}) from exc
                pattern = question.validation_rules.get("pattern")
                if pattern:
                    try:
                        re.compile(pattern)
                    except re.error as exc:
                        raise ValidationError({label: f"Invalid regex pattern: {exc}."}) from exc
        cls.validate_facility_template_controls(template)

    @classmethod
    def validate_facility_template_controls(cls, template):
        if template.scope != AssessmentFormScope.FACILITY:
            return
        if template.form_type not in {AssessmentFormType.FACILITY_INTAKE, AssessmentFormType.HEALTH_DECLARATION}:
            raise ValidationError({"form_type": "Facility supplementary forms must use the facility intake form type."})
        if not template.facility_id:
            raise ValidationError({"facility": "Facility supplementary forms require a facility."})
        official_question_keys = set(
            AssessmentFormQuestion.objects.filter(
                section__template__scope__in=[AssessmentFormScope.NATIONAL, AssessmentFormScope.STATE],
                section__template__status__in=[AssessmentFormStatus.PUBLISHED, AssessmentFormStatus.ACTIVE],
                section__template__is_mandatory=True,
            )
            .filter(Q(section__template__state__isnull=True) | Q(section__template__state=template.facility.state))
            .values_list("key", flat=True)
        )
        for section in template.sections.prefetch_related("questions").all():
            for question in section.questions.all():
                if question.key in official_question_keys:
                    raise ValidationError({f"question:{question.key}": "Facility forms cannot duplicate or override mandatory national or State questions."})
                if question.privacy_classification not in cls.FACILITY_ALLOWED_PRIVACY_CLASSIFICATIONS:
                    raise ValidationError({f"question:{question.key}": "Facility forms cannot mark questionnaire answers as public or employer-visible."})

    @classmethod
    def _condition_matches(cls, condition, *, data, current_answer=MISSING):
        if not condition:
            return True
        if "all" in condition:
            return all(cls._condition_matches(child, data=data, current_answer=current_answer) for child in condition["all"])
        if "any" in condition:
            return any(cls._condition_matches(child, data=data, current_answer=current_answer) for child in condition["any"])
        answer = current_answer if condition.get("use_current_answer") else data.get(condition.get("question"), cls.MISSING)
        operator = condition.get("operator", "equals")
        expected = condition.get("value")
        if operator == "exists":
            return answer is not cls.MISSING and answer not in (None, "")
        if answer is cls.MISSING:
            return False
        if operator == "equals":
            return answer == expected
        if operator == "not_equals":
            return answer != expected
        if operator in {"in", "not_in", "contains"}:
            try:
                if operator == "in":
                    return answer in expected
                if operator == "not_in":
                    return answer not in expected
                return expected in answer
            except TypeError:
                return False
        if operator == "is_truthy":
            return bool(answer)
        if operator == "is_falsy":
            return not bool(answer)
        try:
            actual_number = Decimal(str(answer))
            expected_number = Decimal(str(expected))
        except (InvalidOperation, TypeError, ValueError):
            return False
        if operator == "greater_than":
            return actual_number > expected_number
        if operator == "greater_than_or_equal":
            return actual_number >= expected_number
        if operator == "less_than":
            return actual_number < expected_number
        return actual_number <= expected_number

    @staticmethod
    def _is_missing(value):
        return value is AssessmentFormValidationService.MISSING or value is None or value == "" or value == []

    @classmethod
    def _validate_answer(cls, *, response, question, value):
        question_type = question["question_type"]
        rules = question.get("validation_rules") or {}
        if question_type in cls.TEXT_TYPES:
            if not isinstance(value, str):
                return "Enter text."
            if question_type == AssessmentQuestionType.EMAIL:
                try:
                    validate_email(value)
                except DjangoValidationError:
                    return "Enter a valid email address."
            if rules.get("min_length") is not None and len(value) < rules["min_length"]:
                return f"Enter at least {rules['min_length']} characters."
            if rules.get("max_length") is not None and len(value) > rules["max_length"]:
                return f"Enter no more than {rules['max_length']} characters."
            if rules.get("pattern") and not re.fullmatch(rules["pattern"], value):
                return "Enter a value in the required format."
        elif question_type in cls.NUMBER_TYPES:
            if isinstance(value, bool):
                return "Enter a number."
            try:
                number = Decimal(str(value))
            except (InvalidOperation, TypeError, ValueError):
                return "Enter a number."
            if rules.get("min_value") is not None and number < Decimal(str(rules["min_value"])):
                return f"Enter a value greater than or equal to {rules['min_value']}."
            if rules.get("max_value") is not None and number > Decimal(str(rules["max_value"])):
                return f"Enter a value less than or equal to {rules['max_value']}."
        elif question_type in {AssessmentQuestionType.YES_NO, AssessmentQuestionType.CHECKBOX}:
            if not isinstance(value, bool):
                return "Select yes or no."
        elif question_type in cls.SINGLE_CHOICE_TYPES:
            if value not in (rules.get("allowed_choices") or question.get("options") or []):
                return "Select one of the allowed options."
        elif question_type in cls.MULTIPLE_CHOICE_TYPES:
            allowed = rules.get("allowed_choices") or question.get("options") or []
            if not isinstance(value, list) or any(item not in allowed for item in value):
                return "Select only allowed options."
        elif question_type in cls.DATE_TYPES:
            try:
                parsed = date.fromisoformat(value)
            except (TypeError, ValueError):
                return "Enter a valid date."
            if rules.get("date_before") and parsed >= date.fromisoformat(rules["date_before"]):
                return f"Enter a date before {rules['date_before']}."
            if rules.get("date_after") and parsed <= date.fromisoformat(rules["date_after"]):
                return f"Enter a date after {rules['date_after']}."
        elif question_type == AssessmentQuestionType.TIME:
            try:
                time.fromisoformat(value)
            except (TypeError, ValueError):
                return "Enter a valid time."
        elif question_type == AssessmentQuestionType.DATETIME:
            try:
                datetime.fromisoformat(value)
            except (TypeError, ValueError):
                return "Enter a valid date and time."
        elif question_type == AssessmentQuestionType.BLOOD_PRESSURE:
            if not isinstance(value, dict) or not {"systolic", "diastolic"} <= set(value):
                return "Enter systolic and diastolic blood pressure values."
            if any(isinstance(value[item], bool) or not isinstance(value[item], (int, float)) or value[item] <= 0 for item in ("systolic", "diastolic")):
                return "Enter valid systolic and diastolic blood pressure values."
        elif question_type == AssessmentQuestionType.FILE_UPLOAD:
            if not isinstance(value, dict) or not value.get("name"):
                return "Upload a file."
            allowed_types = rules.get("file_types") or []
            if allowed_types and value.get("content_type") not in allowed_types:
                return "Upload a permitted file type."
            if rules.get("max_size") is not None and value.get("size", 0) > rules["max_size"]:
                return "Upload a file within the permitted size."
        if rules.get("unique_within_assessment") and AssessmentFormResponse.objects.filter(
            assessment=response.assessment,
            response_data__contains={question["key"]: value},
        ).exclude(id=response.id).exclude(status__in=[AssessmentFormResponseStatus.SUPERSEDED, AssessmentFormResponseStatus.ARCHIVED]).exists():
            return "This value must be unique within the assessment."
        return ""

    @classmethod
    def validate_response(cls, response):
        data = response.response_data or {}
        questions = list(cls._snapshot_questions(response.question_snapshot))
        known_keys = {question["key"] for _, question in questions}
        errors = {key: "This question is not part of the assigned form." for key in data if key not in known_keys}
        risk_flags = set()
        for section, question in questions:
            section_visible = cls._condition_matches(section.get("visibility_rules") or {}, data=data)
            logic = question.get("conditional_logic") or {}
            visible = section_visible and cls._condition_matches(logic.get("visible_if") or {}, data=data)
            if not visible:
                continue
            value = data.get(question["key"], cls.MISSING)
            required_if = logic.get("required_if")
            required = question.get("required", False) or bool(required_if and cls._condition_matches(required_if, data=data))
            if cls._is_missing(value):
                if required:
                    errors[question["key"]] = "This field is required."
                continue
            error = cls._validate_answer(response=response, question=question, value=value)
            if error:
                errors[question["key"]] = error
                continue
            rules = question.get("risk_flag_rules") or []
            for rule in rules if isinstance(rules, list) else [rules]:
                when = rule.get("when", {"use_current_answer": True, "operator": "is_truthy"})
                if cls._condition_matches(when, data=data, current_answer=value):
                    risk_flags.update(rule.get("flags", []))
        if errors:
            raise ValidationError(errors)
        return sorted(risk_flags)


class AssessmentFormTemplateService:
    EDITABLE_STATUSES = {AssessmentFormStatus.DRAFT, AssessmentFormStatus.REJECTED, AssessmentFormStatus.CHANGES_REQUESTED}
    IMMUTABLE_STATUSES = {
        AssessmentFormStatus.PUBLISHED,
        AssessmentFormStatus.ACTIVE,
        AssessmentFormStatus.RETIRED,
        AssessmentFormStatus.ARCHIVED,
    }

    @staticmethod
    def owner_level_for_scope(scope):
        if scope == AssessmentFormScope.STATE:
            return AssessmentOwnerLevel.STATE
        if scope == AssessmentFormScope.FACILITY:
            return AssessmentOwnerLevel.FACILITY
        return AssessmentOwnerLevel.FEDERAL

    @classmethod
    def owner_id_for_template(cls, template):
        if template.scope == AssessmentFormScope.STATE:
            return template.state_id
        if template.scope == AssessmentFormScope.FACILITY:
            return template.facility_id
        return None

    @classmethod
    def initialize_template_ownership(cls, template):
        template.owner_level = cls.owner_level_for_scope(template.scope)
        template.owner_id = cls.owner_id_for_template(template)
        if template.base_template_id:
            return
        if template.scope == AssessmentFormScope.NATIONAL and template.pk:
            template.base_template = template
            return
        if template.parent_template_id:
            template.base_template = template.parent_template.base_template or template.parent_template

    @classmethod
    def sync_template_ownership(cls, *, template):
        cls.initialize_template_ownership(template)
        AssessmentFormTemplate.objects.filter(pk=template.pk).update(
            owner_level=template.owner_level,
            owner_id=template.owner_id,
            base_template=template.base_template,
        )
        template.refresh_from_db()
        return template

    @classmethod
    def ensure_section_editable(cls, *, section, actor):
        cls.ensure_can_edit(template=section.template, actor=actor)
        if section.locked and not section.editable_by_child:
            log_action(
                action=AuditAction.SECURITY_EVENT,
                actor=actor,
                target=section,
                old_value=section_audit_snapshot(section),
                metadata=assessment_audit_metadata(
                    event="locked_inherited_field_modification_blocked",
                    actor=actor,
                    entity=section,
                    attempted_action="section_edit",
                ),
            )
            raise PermissionDenied("Inherited sections are locked and cannot be edited.")

    @classmethod
    def ensure_question_editable(cls, *, question, actor):
        cls.ensure_can_edit(template=question.section.template, actor=actor)
        if question.locked and not question.editable_by_child:
            log_action(
                action=AuditAction.SECURITY_EVENT,
                actor=actor,
                target=question,
                old_value=question_audit_snapshot(question),
                metadata=assessment_audit_metadata(
                    event="locked_inherited_field_modification_blocked",
                    actor=actor,
                    entity=question,
                    attempted_action="question_edit",
                ),
            )
            raise PermissionDenied("Inherited fields are locked and cannot be edited.")

    @classmethod
    def ensure_question_deletable(cls, *, question, actor):
        cls.ensure_can_edit(template=question.section.template, actor=actor)
        if question.locked and not question.deletable_by_child:
            log_action(
                action=AuditAction.SECURITY_EVENT,
                actor=actor,
                target=question,
                old_value=question_audit_snapshot(question),
                metadata=assessment_audit_metadata(
                    event="locked_inherited_field_modification_blocked",
                    actor=actor,
                    entity=question,
                    attempted_action="question_delete",
                ),
            )
            raise PermissionDenied("Inherited fields cannot be deleted.")

    @classmethod
    def ensure_section_deletable(cls, *, section, actor):
        cls.ensure_can_edit(template=section.template, actor=actor)
        if section.locked and not section.deletable_by_child:
            log_action(
                action=AuditAction.SECURITY_EVENT,
                actor=actor,
                target=section,
                old_value=section_audit_snapshot(section),
                metadata=assessment_audit_metadata(
                    event="locked_inherited_field_modification_blocked",
                    actor=actor,
                    entity=section,
                    attempted_action="section_delete",
                ),
            )
            raise PermissionDenied("Inherited sections cannot be deleted.")

    @classmethod
    def clone_sections_into_template(cls, *, source_template, target_template, lock_inherited):
        for section in source_template.sections.all():
            new_section = AssessmentFormSection.objects.create(
                template=target_template,
                key=section.key,
                title=section.title,
                description=section.description,
                owner_level=section.owner_level,
                owner_id=section.owner_id,
                locked=lock_inherited,
                inherited_from_section=section if lock_inherited else section.inherited_from_section,
                editable_by_child=False if lock_inherited else section.editable_by_child,
                deletable_by_child=False if lock_inherited else section.deletable_by_child,
                sort_order=section.sort_order,
                visibility_rules=section.visibility_rules,
                required_completion=section.required_completion,
            )
            AssessmentFormQuestion.objects.bulk_create(
                [
                    AssessmentFormQuestion(
                        section=new_section,
                        key=question.key,
                        label=question.label,
                        help_text=question.help_text,
                        placeholder=question.placeholder,
                        owner_level=question.owner_level,
                        owner_id=question.owner_id,
                        locked=lock_inherited,
                        inherited_from_question=question if lock_inherited else question.inherited_from_question,
                        editable_by_child=False if lock_inherited else question.editable_by_child,
                        deletable_by_child=False if lock_inherited else question.deletable_by_child,
                        question_type=question.question_type,
                        required=question.required,
                        options=question.options,
                        validation_rules=question.validation_rules,
                        conditional_logic=question.conditional_logic,
                        risk_flag=question.risk_flag,
                        risk_flag_rules=question.risk_flag_rules,
                        privacy_classification=question.privacy_classification,
                        respondent_role=question.respondent_role,
                        sort_order=question.sort_order,
                        is_active=question.is_active,
                    )
                    for question in section.questions.all()
                ]
            )

    @classmethod
    def initialize_section_ownership(cls, *, section):
        section.owner_level = section.template.owner_level
        section.owner_id = section.template.owner_id
        return section

    @classmethod
    def initialize_question_ownership(cls, *, question):
        question.owner_level = question.section.owner_level
        question.owner_id = question.section.owner_id
        return question

    @classmethod
    def ensure_can_manage(cls, *, template, actor):
        if not can_manage_assessment_form_template(actor, template):
            raise PermissionDenied("You cannot manage this assessment form template.")

    @classmethod
    def ensure_can_edit(cls, *, template, actor):
        cls.ensure_can_manage(template=template, actor=actor)
        if template.status not in cls.EDITABLE_STATUSES:
            raise ValidationError("Only draft or rejected assessment form templates can be edited.")

    @classmethod
    def ensure_can_approve(cls, *, template, actor):
        if not can_approve_assessment_form_template(actor, template):
            raise PermissionDenied("You cannot approve this assessment form template.")

    @classmethod
    @transaction.atomic
    def submit_for_approval(cls, *, template, actor):
        cls.ensure_can_edit(template=template, actor=actor)
        old_status = template.status
        template.status = AssessmentFormStatus.PENDING_APPROVAL
        template.review_requested_at = timezone.now()
        template.reviewed_by = None
        template.reviewed_at = None
        template.review_comment = ""
        template.save(update_fields=["status", "review_requested_at", "reviewed_by", "reviewed_at", "review_comment", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=template,
            old_value={"status": old_status},
            new_value={"status": template.status},
            metadata=assessment_audit_metadata(
                event="assessment_form_submitted_for_approval",
                actor=actor,
                entity=template,
            ),
        )
        return template

    @classmethod
    @transaction.atomic
    def approve(cls, *, template, actor):
        cls.ensure_can_approve(template=template, actor=actor)
        if template.status != AssessmentFormStatus.PENDING_APPROVAL:
            raise ValidationError("Only pending assessment form templates can be approved.")
        if template.scope == AssessmentFormScope.FACILITY:
            AssessmentFormValidationService.validate_template(template)
        old_status = template.status
        template.status = AssessmentFormStatus.APPROVED
        template.approved_by = actor
        template.approved_at = timezone.now()
        template.reviewed_by = actor
        template.reviewed_at = timezone.now()
        template.review_comment = ""
        template.save(update_fields=["status", "approved_by", "approved_at", "reviewed_by", "reviewed_at", "review_comment", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=template,
            old_value={"status": old_status},
            new_value={"status": template.status},
            metadata=assessment_audit_metadata(event="assessment_form_approved", actor=actor, entity=template),
        )
        AssessmentFormNotificationService.notify_template_review(template=template, event="approved")
        return template

    @classmethod
    @transaction.atomic
    def reject(cls, *, template, actor, reason=""):
        cls.ensure_can_approve(template=template, actor=actor)
        if template.status != AssessmentFormStatus.PENDING_APPROVAL:
            raise ValidationError("Only pending assessment form templates can be rejected.")
        old_status = template.status
        template.status = AssessmentFormStatus.REJECTED
        template.approved_by = None
        template.approved_at = None
        template.reviewed_by = actor
        template.reviewed_at = timezone.now()
        template.review_comment = reason
        template.save(update_fields=["status", "approved_by", "approved_at", "reviewed_by", "reviewed_at", "review_comment", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=template,
            old_value={"status": old_status},
            new_value={"status": template.status},
            metadata=assessment_audit_metadata(event="assessment_form_rejected", actor=actor, entity=template, reason=reason),
        )
        AssessmentFormNotificationService.notify_template_review(template=template, event="rejected", message_suffix=reason)
        return template

    @classmethod
    @transaction.atomic
    def request_changes(cls, *, template, actor, reason=""):
        cls.ensure_can_approve(template=template, actor=actor)
        if template.status != AssessmentFormStatus.PENDING_APPROVAL:
            raise ValidationError("Only pending assessment form templates can have changes requested.")
        old_status = template.status
        template.status = AssessmentFormStatus.CHANGES_REQUESTED
        template.approved_by = None
        template.approved_at = None
        template.reviewed_by = actor
        template.reviewed_at = timezone.now()
        template.review_comment = reason
        template.save(update_fields=["status", "approved_by", "approved_at", "reviewed_by", "reviewed_at", "review_comment", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=template,
            old_value={"status": old_status},
            new_value={"status": template.status},
            metadata=assessment_audit_metadata(event="assessment_form_changes_requested", actor=actor, entity=template, reason=reason),
        )
        AssessmentFormNotificationService.notify_template_review(template=template, event="changes_requested", message_suffix=reason)
        return template

    @classmethod
    @transaction.atomic
    def publish(cls, *, template, actor):
        cls.ensure_can_approve(template=template, actor=actor)
        if template.status != AssessmentFormStatus.APPROVED:
            raise ValidationError("Only approved assessment form templates can be published.")
        AssessmentFormValidationService.validate_template(template)
        old_status = template.status
        template.status = AssessmentFormStatus.PUBLISHED
        template.published_at = timezone.now()
        template.save(update_fields=["status", "published_at", "updated_at"])
        publish_event = "assessment_form_published"
        if template.form_type == AssessmentFormType.HEALTH_DECLARATION and template.scope == AssessmentFormScope.NATIONAL:
            publish_event = "federal_template_published"
        elif template.form_type == AssessmentFormType.HEALTH_DECLARATION and template.scope == AssessmentFormScope.STATE:
            publish_event = "state_template_published"
        elif template.form_type == AssessmentFormType.HEALTH_DECLARATION and template.scope == AssessmentFormScope.FACILITY:
            publish_event = "facility_template_published"
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=template,
            old_value={"status": old_status},
            new_value={"status": template.status},
            metadata=assessment_audit_metadata(event=publish_event, actor=actor, entity=template),
        )
        AssessmentFormNotificationService.notify_declaration_template_published(template=template)
        if template.parent_template_id:
            AssessmentFormNotificationService.notify_template_review(template=template, event="new_version_published")
        return template

    @classmethod
    @transaction.atomic
    def activate(cls, *, template, actor):
        cls.ensure_can_approve(template=template, actor=actor)
        if template.status != AssessmentFormStatus.PUBLISHED:
            raise ValidationError("Only published assessment form templates can be activated.")
        old_status = template.status
        siblings = AssessmentFormTemplate.objects.filter(
            form_type=template.form_type,
            scope=template.scope,
            state_id=template.state_id,
            facility_id=template.facility_id,
            status=AssessmentFormStatus.ACTIVE,
        ).exclude(pk=template.pk)
        for sibling in siblings:
            sibling.status = AssessmentFormStatus.RETIRED
            sibling.superseded_by = template
            sibling.save(update_fields=["status", "superseded_by", "updated_at"])
        template.status = AssessmentFormStatus.ACTIVE
        template.save(update_fields=["status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=template,
            old_value={"status": old_status},
            new_value={"status": template.status},
            metadata=assessment_audit_metadata(event="assessment_form_activated", actor=actor, entity=template),
        )
        return template

    @classmethod
    @transaction.atomic
    def retire(cls, *, template, actor):
        cls.ensure_can_approve(template=template, actor=actor)
        if template.status not in {AssessmentFormStatus.PUBLISHED, AssessmentFormStatus.ACTIVE}:
            raise ValidationError("Only published or active assessment form templates can be retired.")
        old_status = template.status
        template.status = AssessmentFormStatus.RETIRED
        template.save(update_fields=["status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=template,
            old_value={"status": old_status},
            new_value={"status": template.status},
            metadata=assessment_audit_metadata(event="assessment_form_retired", actor=actor, entity=template),
        )
        return template

    @classmethod
    @transaction.atomic
    def duplicate(cls, *, template, actor):
        cls.ensure_can_manage(template=template, actor=actor)
        root = template.parent_template or template
        version = AssessmentFormTemplate.objects.filter(models.Q(id=root.id) | models.Q(parent_template=root)).aggregate(models.Max("version"))["version__max"] + 1
        duplicate = AssessmentFormTemplate.objects.create(
            name=template.name,
            description=template.description,
            form_type=template.form_type,
            scope=template.scope,
            state=template.state,
            facility=template.facility,
            owner_organization=template.owner_organization,
            owner_level=template.owner_level,
            owner_id=template.owner_id,
            base_template=template.base_template or (template if template.scope == AssessmentFormScope.NATIONAL else None),
            version=version,
            status=AssessmentFormStatus.DRAFT,
            is_mandatory=template.is_mandatory,
            requires_approval=template.requires_approval,
            effective_from=template.effective_from,
            effective_to=template.effective_to,
            created_by=actor,
            parent_template=root,
        )
        cls.clone_sections_into_template(source_template=template, target_template=duplicate, lock_inherited=False)
        log_action(
            action=AuditAction.CREATE,
            actor=actor,
            target=duplicate,
            new_value=template_audit_snapshot(duplicate),
            metadata=assessment_audit_metadata(
                event="assessment_form_duplicated",
                actor=actor,
                entity=duplicate,
                source_template_id=str(template.id),
            ),
        )
        return duplicate

    @classmethod
    @transaction.atomic
    def adopt(cls, *, parent_template, actor):
        if parent_template.status not in {AssessmentFormStatus.PUBLISHED, AssessmentFormStatus.ACTIVE}:
            raise ValidationError("Only published or active templates can be adopted.")
        if actor.role == UserRole.STATE_ADMIN:
            if parent_template.scope != AssessmentFormScope.NATIONAL:
                raise ValidationError("State templates can only adopt national parent templates.")
            scope = AssessmentFormScope.STATE
            state = actor.state
            facility = None
            owner_organization = getattr(actor, "organization", None)
        elif actor.role == UserRole.FACILITY_ADMIN:
            if parent_template.scope not in {AssessmentFormScope.NATIONAL, AssessmentFormScope.STATE}:
                raise ValidationError("Facility templates can only adopt national or state parent templates.")
            facility = getattr(getattr(actor, "organization", None), "medical_facility", None)
            if facility is None:
                raise ValidationError("Facility adoption requires an accredited facility linked to this account.")
            ensure_approved_facility(facility)
            scope = AssessmentFormScope.FACILITY
            state = facility.state
            owner_organization = facility.organization
        else:
            raise PermissionDenied("Only State or facility admins can adopt declaration templates.")

        existing_draft = AssessmentFormTemplate.objects.filter(
            form_type=parent_template.form_type,
            scope=scope,
            state=state,
            facility=facility,
            status=AssessmentFormStatus.DRAFT,
            parent_template=parent_template,
        ).first()
        if existing_draft:
            return existing_draft

        template = AssessmentFormTemplate.objects.create(
            name=parent_template.name,
            description=parent_template.description,
            form_type=parent_template.form_type,
            scope=scope,
            state=state,
            facility=facility,
            owner_organization=owner_organization,
            owner_level=cls.owner_level_for_scope(scope),
            owner_id=state.id if scope == AssessmentFormScope.STATE else facility.id,
            version=1,
            status=AssessmentFormStatus.DRAFT,
            is_mandatory=parent_template.is_mandatory,
            requires_approval=True,
            effective_from=parent_template.effective_from,
            effective_to=parent_template.effective_to,
            created_by=actor,
            parent_template=parent_template,
            base_template=parent_template.base_template or parent_template,
        )
        cls.clone_sections_into_template(source_template=parent_template, target_template=template, lock_inherited=True)
        AssessmentFormTemplateAdoption.objects.create(
            parent_template=parent_template,
            child_template=template,
            adopted_by_level=cls.owner_level_for_scope(scope),
            adopted_by_id=template.owner_id,
        )
        adopt_event = "assessment_form_adopted"
        if parent_template.form_type == AssessmentFormType.HEALTH_DECLARATION and scope == AssessmentFormScope.STATE:
            adopt_event = "state_template_adopted"
        elif parent_template.form_type == AssessmentFormType.HEALTH_DECLARATION and scope == AssessmentFormScope.FACILITY:
            adopt_event = "facility_template_adopted"
        log_action(
            action=AuditAction.CREATE,
            actor=actor,
            target=template,
            old_value=template_audit_snapshot(parent_template),
            new_value=template_audit_snapshot(template),
            metadata=assessment_audit_metadata(
                event=adopt_event,
                actor=actor,
                entity=template,
                parent_template_id=str(parent_template.id),
            ),
        )
        return template


class AssessmentFormNotificationService:
    @staticmethod
    def _deduped_recipients(recipients):
        unique = []
        seen = set()
        for recipient in recipients:
            user_id = recipient.get("user_id")
            email = recipient.get("email", "")
            key = user_id or email
            if not key or key in seen:
                continue
            seen.add(key)
            unique.append(recipient)
        return unique

    @classmethod
    def _send(cls, *, recipients, category, title, message, action_url="", related_object=None):
        if not recipients:
            return []
        return NotificationService.send(
            category=category,
            title=title,
            message=message,
            action_url=action_url,
            recipients=cls._deduped_recipients(recipients),
            related_object_type=related_object.__class__.__name__ if related_object else "",
            related_object_id=str(related_object.id) if related_object else "",
        )

    @staticmethod
    def _create(*, recipient, category, title, message, related_object, action_url=""):
        if not recipient:
            return None
        return Notification.objects.create(
            recipient=recipient,
            organization=getattr(recipient, "organization", None),
            category=category,
            title=title,
            message=message,
            action_url=action_url,
            related_object_type=related_object.__class__.__name__,
            related_object_id=related_object.id,
        )

    @classmethod
    def notify_assignment(cls, *, response):
        cls._create(
            recipient=response.respondent,
            category=NotificationCategory.ASSESSMENT,
            title="Assessment form assigned",
            message=f"{response.template.name} has been assigned for completion.",
            related_object=response,
            action_url=f"/forms/{response.id}",
        )

    @classmethod
    def notify_submission(cls, *, response):
        cls._create(
            recipient=response.assessment.doctor,
            category=NotificationCategory.ASSESSMENT,
            title="Assessment form submitted",
            message=f"{response.template.name} has been submitted for review.",
            related_object=response,
            action_url=f"/doctor/forms?assessment={response.assessment_id}",
        )

    @classmethod
    def notify_clarification(cls, *, response):
        cls._create(
            recipient=response.respondent,
            category=NotificationCategory.ASSESSMENT,
            title="Assessment form requires clarification",
            message=f"{response.template.name} has been reopened for clarification.",
            related_object=response,
            action_url=f"/forms/{response.id}",
        )

    @classmethod
    def notify_template_review(cls, *, template, event, message_suffix=""):
        event_labels = {
            "approved": ("Facility form approved", "approved"),
            "rejected": ("Facility form rejected", "rejected"),
            "changes_requested": ("Facility form changes requested", "returned for changes"),
            "new_version_published": ("Assessment form version published", "published as a new version"),
        }
        title, status_text = event_labels[event]
        suffix = f" Reason: {message_suffix}" if message_suffix else ""
        cls._create(
            recipient=template.created_by,
            category=NotificationCategory.FACILITY_ACCREDITATION if template.scope == AssessmentFormScope.FACILITY else NotificationCategory.ASSESSMENT,
            title=title,
            message=f"{template.name} was {status_text}.{suffix}",
            related_object=template,
            action_url=f"/facility/forms?template={template.id}" if template.scope == AssessmentFormScope.FACILITY else f"/state/forms?template={template.id}",
        )

    @classmethod
    def notify_declaration_template_published(cls, *, template):
        if template.form_type != AssessmentFormType.HEALTH_DECLARATION:
            return []
        if template.scope == AssessmentFormScope.NATIONAL:
            recipients = [
                {
                    "user_id": str(user.id),
                    "email": user.email or "",
                    "recipient_type": "state_admin",
                    "organization_id": str(user.organization_id) if user.organization_id else "",
                }
                for user in User.objects.filter(role=UserRole.STATE_ADMIN, status="active")
            ]
            return cls._send(
                recipients=recipients,
                category=NotificationCategory.ASSESSMENT,
                title="Federal declaration template published",
                message=f"{template.name} v{template.version} is available for State adoption.",
                action_url=f"/state/forms?template={template.id}",
                related_object=template,
            )
        if template.scope == AssessmentFormScope.STATE:
            facility_users = [
                {
                    "user_id": str(user.id),
                    "email": user.email or "",
                    "recipient_type": user.role,
                    "organization_id": str(user.organization_id) if user.organization_id else "",
                }
                for user in User.objects.filter(
                    role__in=[UserRole.FACILITY_ADMIN, UserRole.DOCTOR, UserRole.LAB_STAFF],
                    state_id=template.state_id,
                    status="active",
                )
            ]
            facility_admins = [
                recipient
                for recipient in facility_users
                if recipient["recipient_type"] == UserRole.FACILITY_ADMIN
            ]
            cls._send(
                recipients=facility_users,
                category=NotificationCategory.ASSESSMENT,
                title="State declaration extension published",
                message=f"{template.name} v{template.version} has been published for facilities in your State.",
                action_url=f"/facility/forms?template={template.id}",
                related_object=template,
            )
            return cls._send(
                recipients=facility_admins,
                category=NotificationCategory.FACILITY_ACCREDITATION,
                title="Adopt latest State declaration template",
                message=f"Review and adopt {template.name} v{template.version} for your facility workflow.",
                action_url=f"/facility/forms?template={template.id}",
                related_object=template,
            )
        return []

    @classmethod
    def notify_declaration_required(cls, *, assessment):
        notifications = []
        food_handler_user = getattr(assessment.food_handler, "user", None)
        if food_handler_user:
            exists = Notification.objects.filter(
                recipient=food_handler_user,
                related_object_type="MedicalAssessment",
                related_object_id=assessment.id,
                title="Health declaration required",
            ).exists()
            if not exists:
                notification = cls._create(
                    recipient=food_handler_user,
                    category=NotificationCategory.ASSESSMENT,
                    title="Health declaration required",
                    message="Your health declaration is now required before your assessment can move forward.",
                    related_object=assessment,
                    action_url=f"/food-handler/declaration?assessment={assessment.id}",
                )
                if notification:
                    notifications.append(notification)
        employer_user = getattr(getattr(assessment, "employer", None), "user", None)
        if employer_user:
            exists = Notification.objects.filter(
                recipient=employer_user,
                related_object_type="MedicalAssessment",
                related_object_id=assessment.id,
                title="Staff declaration pending",
            ).exists()
            if not exists:
                notification = cls._create(
                    recipient=employer_user,
                    category=NotificationCategory.ASSESSMENT,
                    title="Staff declaration pending",
                    message="A staff member has a pending health declaration required for an upcoming assessment.",
                    related_object=assessment,
                    action_url=f"/employer/dashboard",
                )
                if notification:
                    notifications.append(notification)
        return notifications

    @classmethod
    def notify_declaration_submitted(cls, *, declaration):
        assessment = declaration.assessment
        recipients = []
        if assessment.doctor_id:
            recipients.append(
                {
                    "user_id": str(assessment.doctor_id),
                    "email": assessment.doctor.email or "",
                    "recipient_type": "doctor",
                    "organization_id": str(assessment.doctor.organization_id) if assessment.doctor.organization_id else "",
                }
            )
        for admin in User.objects.filter(
            role=UserRole.FACILITY_ADMIN,
            organization_id=assessment.facility.organization_id,
            status="active",
        ):
            recipients.append(
                {
                    "user_id": str(admin.id),
                    "email": admin.email or "",
                    "recipient_type": "facility_admin",
                    "organization_id": str(admin.organization_id) if admin.organization_id else "",
                }
            )
        return cls._send(
            recipients=recipients,
            category=NotificationCategory.ASSESSMENT,
            title="Health declaration submitted",
            message="A health declaration has been submitted and is ready for facility review.",
            action_url=f"/doctor/assessments/{assessment.id}",
            related_object=declaration,
        )

    @classmethod
    def notify_declaration_correction_required(cls, *, declaration):
        assessment = declaration.assessment
        recipient = assessment.food_handler.user if assessment.food_handler and assessment.food_handler.user_id else None
        if not recipient:
            return None
        return cls._create(
            recipient=recipient,
            category=NotificationCategory.ASSESSMENT,
            title="Health declaration requires correction",
            message="Your declaration needs clarification before the medical workflow can continue.",
            related_object=declaration,
            action_url=f"/food-handler/declaration?assessment={assessment.id}",
        )

    @classmethod
    def notify_appointment_blocked_missing_declaration(cls, *, assessment):
        recipients = []
        food_handler_user = getattr(assessment.food_handler, "user", None)
        if food_handler_user:
            recipients.append(
                {
                    "user_id": str(food_handler_user.id),
                    "email": food_handler_user.email or "",
                    "recipient_type": "food_handler",
                }
            )
        employer_user = getattr(getattr(assessment, "employer", None), "user", None)
        if employer_user:
            recipients.append(
                {
                    "user_id": str(employer_user.id),
                    "email": employer_user.email or "",
                    "recipient_type": "employer",
                    "organization_id": str(employer_user.organization_id) if employer_user.organization_id else "",
                }
            )
        existing = Notification.objects.filter(
            related_object_type="MedicalAssessment",
            related_object_id=assessment.id,
            title="Appointment blocked by missing declaration",
        ).exists()
        if existing:
            return []
        return cls._send(
            recipients=recipients,
            category=NotificationCategory.APPOINTMENT,
            title="Appointment blocked by missing declaration",
            message="The appointment cannot be confirmed until the required health declaration is submitted.",
            action_url=f"/food-handler/declaration?assessment={assessment.id}",
            related_object=assessment,
        )

    @classmethod
    def notify_high_risk_declaration_validation_required(cls, *, declaration):
        if not declaration.risk_flag:
            return []
        assessment = declaration.assessment
        recipients = []
        if assessment.doctor_id:
            recipients.append(
                {
                    "user_id": str(assessment.doctor_id),
                    "email": assessment.doctor.email or "",
                    "recipient_type": "doctor",
                    "organization_id": str(assessment.doctor.organization_id) if assessment.doctor.organization_id else "",
                }
            )
        else:
            for doctor in User.objects.filter(
                role=UserRole.DOCTOR,
                organization_id=assessment.facility.organization_id,
                status="active",
            ):
                recipients.append(
                    {
                        "user_id": str(doctor.id),
                        "email": doctor.email or "",
                        "recipient_type": "doctor",
                        "organization_id": str(doctor.organization_id) if doctor.organization_id else "",
                    }
                )
        return cls._send(
            recipients=recipients,
            category=NotificationCategory.ASSESSMENT,
            title="High-risk declaration requires validation",
            message="A submitted declaration contains high-risk answers and needs doctor review.",
            action_url=f"/doctor/assessments/{assessment.id}",
            related_object=declaration,
        )

    @classmethod
    def send_reminders(cls, *, actor=None, older_than_days=3):
        cutoff = timezone.now() - timedelta(days=older_than_days)
        queryset = AssessmentFormResponse.objects.select_related("template", "respondent").filter(
            is_required=True,
            status__in=[
                AssessmentFormResponseStatus.NOT_STARTED,
                AssessmentFormResponseStatus.DRAFT,
                AssessmentFormResponseStatus.REOPENED,
                AssessmentFormResponseStatus.CLARIFICATION_REQUESTED,
            ],
            created_at__lte=cutoff,
            respondent__isnull=False,
        )
        sent = []
        for response in queryset:
            exists = Notification.objects.filter(
                recipient=response.respondent,
                related_object_type=response.__class__.__name__,
                related_object_id=response.id,
                title="Assessment form reminder",
                created_at__gte=timezone.now() - timedelta(days=1),
            ).exists()
            if exists:
                continue
            notification = cls._create(
                recipient=response.respondent,
                category=NotificationCategory.ASSESSMENT,
                title="Assessment form reminder",
                message=f"{response.template.name} is still pending completion.",
                related_object=response,
                action_url=f"/forms/{response.id}",
            )
            if notification:
                sent.append(notification)
                log_action(
                    action=AuditAction.WORKFLOW_TRANSITION,
                    actor=actor,
                    target=response,
                    metadata={"event": "assessment_form_response_reminder_sent", "assessment_id": str(response.assessment_id)},
                )
        return sent


class AssessmentFormAnalyticsService:
    @classmethod
    def responses_for_actor(cls, actor):
        queryset = AssessmentFormResponse.objects.select_related("assessment", "assessment__facility", "assessment__employer", "template")
        if actor.role == UserRole.SUPER_ADMIN:
            return queryset
        if actor.role == UserRole.FEDERAL_ADMIN:
            return queryset
        if actor.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR} and actor.state_id:
            return queryset.filter(assessment__facility__state_id=actor.state_id)
        if actor.role == UserRole.EMPLOYER and hasattr(actor, "employer"):
            return queryset.filter(assessment__employer=actor.employer)
        if actor.role == UserRole.FOOD_HANDLER:
            return queryset.filter(assessment__food_handler__user=actor)
        if actor.role in {UserRole.FACILITY_ADMIN, UserRole.DOCTOR, UserRole.LAB_STAFF} and actor.organization_id:
            return queryset.filter(assessment__facility__organization_id=actor.organization_id)
        return queryset.none()

    @staticmethod
    def _increment(target, key, amount=1):
        target[key] = target.get(key, 0) + amount

    @classmethod
    def aggregate(cls, *, actor):
        queryset = cls.responses_for_actor(actor)
        total = queryset.count()
        submitted_statuses = {
            AssessmentFormResponseStatus.SUBMITTED,
            AssessmentFormResponseStatus.UNDER_REVIEW,
            AssessmentFormResponseStatus.RESUBMITTED,
            AssessmentFormResponseStatus.VALIDATED,
            AssessmentFormResponseStatus.LOCKED,
        }
        incomplete_statuses = {
            AssessmentFormResponseStatus.NOT_STARTED,
            AssessmentFormResponseStatus.DRAFT,
            AssessmentFormResponseStatus.CLARIFICATION_REQUESTED,
            AssessmentFormResponseStatus.REOPENED,
        }
        status_counts = {}
        risk_flag_counts = {}
        usage_by_template = {}
        usage_by_form_type = {}
        version_counts = {}
        clarification_counts = {
            AssessmentFormResponseStatus.CLARIFICATION_REQUESTED: 0,
            AssessmentFormResponseStatus.REOPENED: 0,
            AssessmentFormResponseStatus.RESUBMITTED: 0,
        }
        overdue_cutoff = timezone.now() - timedelta(days=7)
        overdue = 0
        submitted = 0

        for response in queryset:
            cls._increment(status_counts, response.status)
            if response.status in submitted_statuses:
                submitted += 1
            if response.status in incomplete_statuses and response.created_at <= overdue_cutoff:
                overdue += 1
            if response.status in clarification_counts:
                clarification_counts[response.status] += 1
            template_key = str(response.template_id)
            if template_key not in usage_by_template:
                usage_by_template[template_key] = {
                    "template_id": template_key,
                    "name": response.template.name,
                    "form_type": response.template.form_type,
                    "assigned": 0,
                    "submitted": 0,
                }
            usage_by_template[template_key]["assigned"] += 1
            if response.status in submitted_statuses:
                usage_by_template[template_key]["submitted"] += 1
            cls._increment(usage_by_form_type, response.template.form_type)
            cls._increment(version_counts, f"{template_key}:v{response.template_version}")
            for flag in response.risk_flags or []:
                cls._increment(risk_flag_counts, flag)

        completion_rate = round((submitted / total) * 100, 2) if total else 0
        return {
            "total_responses": total,
            "submitted_responses": submitted,
            "completion_rate": completion_rate,
            "overdue_responses": overdue,
            "status_counts": status_counts,
            "risk_flag_counts": risk_flag_counts,
            "usage_by_template": list(usage_by_template.values()),
            "usage_by_form_type": usage_by_form_type,
            "version_counts": version_counts,
            "clarification_counts": clarification_counts,
        }


class AssessmentRequirementResolutionService:
    SCOPE_ORDER = {
        AssessmentFormScope.SYSTEM: 0,
        AssessmentFormScope.NATIONAL: 1,
        AssessmentFormScope.STATE: 2,
        AssessmentFormScope.FACILITY: 3,
    }

    @staticmethod
    def _append_unique(target, values):
        for value in values:
            if value not in target:
                target.append(value)

    @classmethod
    def ensure_can_manage(cls, *, requirement_set, actor):
        if not can_manage_assessment_requirement_set(actor, requirement_set):
            raise PermissionDenied("You cannot manage this assessment requirement set.")

    @classmethod
    @transaction.atomic
    def publish(cls, *, requirement_set, actor):
        cls.ensure_can_manage(requirement_set=requirement_set, actor=actor)
        if requirement_set.status not in {AssessmentRequirementSetStatus.DRAFT, AssessmentRequirementSetStatus.PUBLISHED}:
            raise ValidationError("Only draft or published requirement sets can be activated.")
        requirement_set.status = AssessmentRequirementSetStatus.ACTIVE
        requirement_set.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=requirement_set, metadata={"event": "assessment_requirement_set_published"})
        return requirement_set

    @classmethod
    @transaction.atomic
    def retire(cls, *, requirement_set, actor):
        cls.ensure_can_manage(requirement_set=requirement_set, actor=actor)
        if requirement_set.status not in {AssessmentRequirementSetStatus.PUBLISHED, AssessmentRequirementSetStatus.ACTIVE}:
            raise ValidationError("Only published or active requirement sets can be retired.")
        requirement_set.status = AssessmentRequirementSetStatus.RETIRED
        requirement_set.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=requirement_set, metadata={"event": "assessment_requirement_set_retired"})
        return requirement_set

    @classmethod
    def applicable_sets(cls, *, assessment, assessment_type=None):
        assessment_type = assessment_type or assessment.assessment_type
        today = timezone.localdate()
        illness_conditions = set(
            IllnessReport.objects.filter(food_handler=assessment.food_handler)
            .exclude(clearance_status__in=[ClearanceStatus.CLEARED, ClearanceStatus.REJECTED])
            .exclude(suspected_condition="")
            .values_list("suspected_condition", flat=True)
        )
        queryset = (
            AssessmentRequirementSet.objects.filter(
                status=AssessmentRequirementSetStatus.ACTIVE,
            )
            .filter(Q(effective_from__isnull=True) | Q(effective_from__lte=today))
            .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=today))
            .filter(Q(scope__in=[AssessmentFormScope.SYSTEM, AssessmentFormScope.NATIONAL]) | Q(scope=AssessmentFormScope.STATE, state=assessment.facility.state) | Q(scope=AssessmentFormScope.FACILITY, facility=assessment.facility))
            .filter(Q(assessment_type="") | Q(assessment_type=assessment_type))
            .filter(Q(food_handler_category="") | Q(food_handler_category=assessment.food_handler.food_handler_category))
            .filter(Q(employer_category="") | Q(employer_category=getattr(assessment.employer, "establishment_category", "")))
            .prefetch_related("required_forms")
        )
        requirement_sets = [
            requirement_set
            for requirement_set in queryset
            if not requirement_set.illness_condition or requirement_set.illness_condition in illness_conditions
        ]
        return sorted(requirement_sets, key=lambda requirement_set: (cls.SCOPE_ORDER[requirement_set.scope], requirement_set.created_at, str(requirement_set.id)))

    @classmethod
    def resolve(cls, *, assessment, actor=None, assessment_type=None):
        requirement_sets = cls.applicable_sets(assessment=assessment, assessment_type=assessment_type)
        output = {
            "assessment_id": str(assessment.id),
            "assessment_type": assessment_type or assessment.assessment_type,
            "applied_requirement_sets": [],
            "required_forms": [],
            "required_documents": [],
            "required_lab_tests": [],
            "required_vaccinations": [],
            "required_approvals": [],
            "blocking_requirements": [],
            "advisory_requirements": [],
        }
        seen_forms = set()
        for requirement_set in requirement_sets:
            output["applied_requirement_sets"].append(
                {
                    "id": str(requirement_set.id),
                    "name": requirement_set.name,
                    "scope": requirement_set.scope,
                    "version": requirement_set.version,
                }
            )
            for template in requirement_set.required_forms.filter(status__in=[AssessmentFormStatus.PUBLISHED, AssessmentFormStatus.ACTIVE]):
                if template.id not in seen_forms:
                    output["required_forms"].append(
                        {
                            "id": str(template.id),
                            "name": template.name,
                            "form_type": template.form_type,
                            "scope": template.scope,
                            "version": template.version,
                            "mandatory": template.is_mandatory or requirement_set.scope in {AssessmentFormScope.SYSTEM, AssessmentFormScope.NATIONAL, AssessmentFormScope.STATE},
                        }
                    )
                    seen_forms.add(template.id)
            cls._append_unique(output["required_documents"], requirement_set.required_documents)
            cls._append_unique(output["required_lab_tests"], requirement_set.required_lab_tests)
            cls._append_unique(output["required_vaccinations"], requirement_set.required_vaccinations)
            cls._append_unique(output["required_approvals"], requirement_set.required_approvals)
            cls._append_unique(output["blocking_requirements"], requirement_set.blocking_requirements)
            cls._append_unique(output["advisory_requirements"], requirement_set.advisory_requirements)
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={"event": "assessment_requirements_resolved", "requirement_set_ids": [item["id"] for item in output["applied_requirement_sets"]]},
        )
        return output

    @classmethod
    @transaction.atomic
    def assign_forms(cls, *, assessment, actor=None):
        resolved = cls.resolve(assessment=assessment, actor=actor)
        assigned = []
        for required_form in resolved["required_forms"]:
            template = AssessmentFormTemplate.objects.get(id=required_form["id"])
            response = AssessmentFormResponseService.assign(
                assessment=assessment,
                template=template,
                is_required=required_form["mandatory"],
                actor=actor,
            )
            assigned.append(response)
        return assigned


class AssessmentFormResponseService:
    EDITABLE_STATUSES = {
        AssessmentFormResponseStatus.NOT_STARTED,
        AssessmentFormResponseStatus.DRAFT,
        AssessmentFormResponseStatus.REOPENED,
        AssessmentFormResponseStatus.CLARIFICATION_REQUESTED,
    }
    CURRENT_STATUSES = set(AssessmentFormResponseStatus.values) - {
        AssessmentFormResponseStatus.SUPERSEDED,
        AssessmentFormResponseStatus.ARCHIVED,
    }
    RESPONDENT_ROLES_BY_FORM_TYPE = {
        AssessmentFormType.DOCTOR_CLINICAL_REVIEW: AssessmentRespondentRole.DOCTOR,
        AssessmentFormType.LAB_RESULT: AssessmentRespondentRole.LAB_STAFF,
        AssessmentFormType.STATE_VALIDATION_CHECKLIST: AssessmentRespondentRole.STATE_USER,
        AssessmentFormType.INSPECTION_SUPPORT: AssessmentRespondentRole.INSPECTOR,
        AssessmentFormType.FACILITY_INTAKE: AssessmentRespondentRole.FACILITY_STAFF,
    }

    @classmethod
    def snapshot_template(cls, template):
        return {
            "template_id": str(template.id),
            "template_version": template.version,
            "name": template.name,
            "description": template.description,
            "form_type": template.form_type,
            "sections": [
                {
                    "id": str(section.id),
                    "key": section.key,
                    "title": section.title,
                    "description": section.description,
                    "sort_order": section.sort_order,
                    "visibility_rules": section.visibility_rules,
                    "required_completion": section.required_completion,
                    "questions": [
                        {
                            "id": str(question.id),
                            "key": question.key,
                            "label": question.label,
                            "help_text": question.help_text,
                            "placeholder": question.placeholder,
                            "question_type": question.question_type,
                            "required": question.required,
                            "options": question.options,
                            "validation_rules": question.validation_rules,
                            "conditional_logic": question.conditional_logic,
                            "risk_flag_rules": question.risk_flag_rules,
                            "privacy_classification": question.privacy_classification,
                            "respondent_role": question.respondent_role,
                            "sort_order": question.sort_order,
                        }
                        for question in section.questions.filter(is_active=True)
                    ],
                }
                for section in template.sections.all()
            ],
        }

    @classmethod
    def respondent_role_for_template(cls, template):
        roles = list(
            template.sections.values_list("questions__respondent_role", flat=True)
            .exclude(questions__respondent_role__isnull=True)
            .exclude(questions__respondent_role="")
            .distinct()
        )
        if len(roles) == 1:
            return roles[0]
        return cls.RESPONDENT_ROLES_BY_FORM_TYPE.get(template.form_type, AssessmentRespondentRole.FOOD_HANDLER)

    @classmethod
    def initial_respondent(cls, *, assessment, respondent_role):
        if respondent_role == AssessmentRespondentRole.FOOD_HANDLER:
            return assessment.food_handler.user
        if respondent_role == AssessmentRespondentRole.DOCTOR:
            return assessment.doctor
        return None

    @classmethod
    def can_view(cls, *, response, actor):
        if not actor or not actor.is_authenticated:
            return False
        assessment = response.assessment
        if actor.role == UserRole.SUPER_ADMIN:
            return True
        if actor.role == UserRole.FOOD_HANDLER:
            return assessment.food_handler.user_id == actor.id
        if actor.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return actor.state_id and assessment.facility.state_id == actor.state_id
        if actor.role in {UserRole.FACILITY_ADMIN, UserRole.DOCTOR, UserRole.LAB_STAFF}:
            return actor.organization_id and assessment.facility.organization_id == actor.organization_id
        return False

    @classmethod
    def ensure_can_view(cls, *, response, actor):
        if not cls.can_view(response=response, actor=actor):
            raise PermissionDenied("You cannot access this assessment form response.")

    @classmethod
    def ensure_can_edit(cls, *, response, actor):
        cls.ensure_can_view(response=response, actor=actor)
        if response.is_locked or response.status not in cls.EDITABLE_STATUSES:
            raise ValidationError("This assessment form response is locked.")
        role = response.respondent_role
        assessment = response.assessment
        allowed = actor.role == UserRole.SUPER_ADMIN
        if role == AssessmentRespondentRole.FOOD_HANDLER:
            allowed = allowed or (actor.role == UserRole.FOOD_HANDLER and assessment.food_handler.user_id == actor.id)
        elif role == AssessmentRespondentRole.DOCTOR:
            allowed = allowed or (actor.role == UserRole.DOCTOR and assessment.doctor_id == actor.id)
        elif role == AssessmentRespondentRole.LAB_STAFF:
            allowed = allowed or (actor.role == UserRole.LAB_STAFF and assessment.facility.organization_id == actor.organization_id)
        elif role == AssessmentRespondentRole.FACILITY_STAFF:
            allowed = allowed or (actor.role == UserRole.FACILITY_ADMIN and assessment.facility.organization_id == actor.organization_id)
        elif role == AssessmentRespondentRole.STATE_USER:
            allowed = allowed or (actor.role == UserRole.STATE_ADMIN and assessment.facility.state_id == actor.state_id)
        elif role == AssessmentRespondentRole.INSPECTOR:
            allowed = allowed or (actor.role == UserRole.INSPECTOR and assessment.facility.state_id == actor.state_id)
        if not allowed:
            raise PermissionDenied("You cannot complete this assessment form response.")

    @classmethod
    def ensure_can_review(cls, *, response, actor):
        cls.ensure_can_view(response=response, actor=actor)
        assessment = response.assessment
        if actor.role == UserRole.SUPER_ADMIN:
            return
        if actor.role == UserRole.DOCTOR and assessment.doctor_id == actor.id:
            return
        if actor.role == UserRole.STATE_ADMIN and assessment.facility.state_id == actor.state_id:
            return
        raise PermissionDenied("You cannot review this assessment form response.")

    @classmethod
    @transaction.atomic
    def assign(cls, *, assessment, template, is_required=True, actor=None):
        existing = (
            AssessmentFormResponse.objects.filter(
                assessment=assessment,
                template=template,
                status__in=cls.CURRENT_STATUSES,
            )
            .order_by("-version")
            .first()
        )
        if existing:
            return existing
        respondent_role = cls.respondent_role_for_template(template)
        response = AssessmentFormResponse.objects.create(
            assessment=assessment,
            template=template,
            template_version=template.version,
            respondent=cls.initial_respondent(assessment=assessment, respondent_role=respondent_role),
            respondent_role=respondent_role,
            question_snapshot=cls.snapshot_template(template),
            is_required=is_required,
        )
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=response,
            metadata={"event": "assessment_form_response_assigned", "assessment_id": str(assessment.id), "template_id": str(template.id)},
        )
        AssessmentFormNotificationService.notify_assignment(response=response)
        return response

    @classmethod
    @transaction.atomic
    def save_draft(cls, *, response, response_data, actor):
        cls.ensure_can_edit(response=response, actor=actor)
        response.response_data = response_data
        response.respondent = actor
        if response.status != AssessmentFormResponseStatus.REOPENED:
            response.status = AssessmentFormResponseStatus.DRAFT
        response.save(update_fields=["response_data", "respondent", "status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=actor, target=response, metadata={"event": "assessment_form_response_draft_saved", "assessment_id": str(response.assessment_id)})
        return response

    @classmethod
    @transaction.atomic
    def submit(cls, *, response, actor):
        cls.ensure_can_edit(response=response, actor=actor)
        response.risk_flags = AssessmentFormValidationService.validate_response(response)
        response.respondent = actor
        response.status = AssessmentFormResponseStatus.RESUBMITTED if response.version > 1 else AssessmentFormResponseStatus.SUBMITTED
        response.submitted_at = timezone.now()
        response.is_locked = True
        response.save(update_fields=["respondent", "status", "risk_flags", "submitted_at", "is_locked", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=response, metadata={"event": "assessment_form_response_submitted", "assessment_id": str(response.assessment_id)})
        AssessmentFormNotificationService.notify_submission(response=response)
        return response

    @classmethod
    @transaction.atomic
    def mark_under_review(cls, *, response, actor):
        cls.ensure_can_review(response=response, actor=actor)
        if response.status not in {AssessmentFormResponseStatus.SUBMITTED, AssessmentFormResponseStatus.RESUBMITTED}:
            raise ValidationError("Only submitted responses can be marked under review.")
        response.status = AssessmentFormResponseStatus.UNDER_REVIEW
        response.save(update_fields=["status", "updated_at"])
        return response

    @classmethod
    @transaction.atomic
    def validate(cls, *, response, actor):
        cls.ensure_can_review(response=response, actor=actor)
        if response.status not in {AssessmentFormResponseStatus.SUBMITTED, AssessmentFormResponseStatus.RESUBMITTED, AssessmentFormResponseStatus.UNDER_REVIEW}:
            raise ValidationError("Only submitted responses can be validated.")
        response.status = AssessmentFormResponseStatus.VALIDATED
        response.is_locked = True
        response.validated_by = actor
        response.validated_at = timezone.now()
        response.save(update_fields=["status", "is_locked", "validated_by", "validated_at", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=response, metadata={"event": "assessment_form_response_validated", "assessment_id": str(response.assessment_id)})
        return response

    @classmethod
    @transaction.atomic
    def reopen(cls, *, response, actor, reason=""):
        cls.ensure_can_review(response=response, actor=actor)
        if response.status not in {
            AssessmentFormResponseStatus.SUBMITTED,
            AssessmentFormResponseStatus.RESUBMITTED,
            AssessmentFormResponseStatus.UNDER_REVIEW,
            AssessmentFormResponseStatus.VALIDATED,
            AssessmentFormResponseStatus.LOCKED,
        }:
            raise ValidationError("Only submitted or validated responses can be reopened.")
        response.status = AssessmentFormResponseStatus.SUPERSEDED
        response.is_locked = True
        response.save(update_fields=["status", "is_locked", "updated_at"])
        reopened = AssessmentFormResponse.objects.create(
            assessment=response.assessment,
            template=response.template,
            template_version=response.template_version,
            respondent=response.respondent,
            respondent_role=response.respondent_role,
            response_data=response.response_data,
            question_snapshot=response.question_snapshot,
            risk_flags=response.risk_flags,
            is_required=response.is_required,
            status=AssessmentFormResponseStatus.REOPENED,
            version=response.version + 1,
            previous_response=response,
        )
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=reopened,
            metadata={"event": "assessment_form_response_reopened", "assessment_id": str(response.assessment_id), "previous_response_id": str(response.id), "reason": reason},
        )
        AssessmentFormNotificationService.notify_clarification(response=reopened)
        return reopened


class AssessmentService:
    @classmethod
    def doctor_work_started(cls, assessment):
        return (
            assessment.declaration_status != StepStatus.PENDING
            or assessment.physical_exam_status != StepStatus.PENDING
            or assessment.decision_draft != FitnessDecision.PENDING
            or bool(assessment.signed_at)
        )

    @classmethod
    def lab_work_started(cls, assessment):
        return assessment.lab_tests.filter(
            Q(sample_collected_at__isnull=False)
            | Q(resulted_at__isnull=False)
            | Q(submitted_to_doctor_at__isnull=False)
            | Q(reviewed_at__isnull=False)
        ).exists()

    CLINICAL_STATUSES = {
        AssessmentStatus.DECLARATION_SUBMITTED,
        AssessmentStatus.DECLARATION_VALIDATED,
        AssessmentStatus.PHYSICAL_EXAM_COMPLETED,
        AssessmentStatus.LAB_TESTS_PENDING,
        AssessmentStatus.LAB_RESULTS_REVIEWED,
        AssessmentStatus.VACCINATION_REVIEWED,
        AssessmentStatus.DOCTOR_DECISION_PENDING,
        AssessmentStatus.FIT,
        AssessmentStatus.TEMPORARILY_NOT_FIT,
        AssessmentStatus.NOT_FIT,
        AssessmentStatus.SUBMITTED_FOR_STATE_VALIDATION,
        AssessmentStatus.CERTIFICATE_ISSUED,
    }

    TERMINAL_STATUSES = {
        AssessmentStatus.FIT,
        AssessmentStatus.TEMPORARILY_NOT_FIT,
        AssessmentStatus.NOT_FIT,
        AssessmentStatus.SUBMITTED_FOR_STATE_VALIDATION,
        AssessmentStatus.CERTIFICATE_ISSUED,
        AssessmentStatus.CLOSED,
    }

    TIMELINE_LABELS = {
        "assessment_created": "Assessment created",
        "assessment_cancelled": "Assessment cancelled",
        "assessment_closed": "Assessment closed",
        "assessment_status_checked": "Prerequisite status checked",
        "appointment_created": "Appointment created",
        "appointment_updated": "Appointment updated",
        "declaration_draft_saved": "Declaration draft saved",
        "declaration_submitted": "Declaration submitted",
        "declaration_validated": "Declaration validated",
        "declaration_clarification_requested": "Declaration clarification requested",
        "declaration_reopened": "Declaration reopened",
        "physical_exam_draft_saved": "Physical exam draft saved",
        "physical_exam_completed": "Physical exam completed",
        "lab_tests_requested": "Lab tests requested",
        "lab_sample_collected": "Lab sample collected",
        "lab_result_recorded": "Lab result recorded",
        "lab_result_document_uploaded": "Lab result document uploaded",
        "lab_submitted_to_doctor": "Lab submitted to doctor",
        "lab_result_submitted_to_doctor": "Lab submitted to doctor",
        "lab_result_reviewed": "Lab result reviewed",
        "lab_repeat_requested": "Repeat lab test requested",
        "vaccination_reviewed": "Vaccination reviewed",
        "fitness_decision_draft_saved": "Decision draft saved",
        "fitness_decision": "Final fitness decision signed",
        "medical_report_generated": "Medical report generated",
        "return_to_work_case_linked": "Return-to-work workflow linked",
        "facility_submitted_assessment_to_state": "Submitted to State validation",
        "facility_certificate_clarification_responded": "State clarification responded",
        "certificate_request_clarification_requested": "State clarification requested",
        "certificate_request_approved": "State certificate request approved",
        "certificate_request_rejected": "State certificate request rejected",
        "certificate_issued": "Certificate issued",
        "assessment_detail_read": "Assessment detail viewed",
        "doctor_assessment_detail_read": "Doctor assessment detail viewed",
        "assessment_audit_timeline_viewed": "Audit timeline viewed",
        "physical_exam_read": "Physical exam viewed",
        "lab_result_read": "Lab result viewed",
        "assessment_report_read": "Assessment report viewed",
    }

    @classmethod
    def timeline_label(cls, log):
        event = (log.metadata or {}).get("event", "")
        if event in cls.TIMELINE_LABELS:
            return cls.TIMELINE_LABELS[event]
        return event.replace("_", " ").title() if event else log.get_action_display()

    @classmethod
    def assessment_timeline(cls, *, assessment, user):
        cls.ensure_assessment_report_access(assessment=assessment, user=user, kind="summary")
        role = getattr(user, "role", "")
        if role in {UserRole.FOOD_HANDLER, UserRole.EMPLOYER}:
            raise PermissionDenied("You cannot access the assessment audit timeline.")
        related_ids = {str(assessment.id)}
        declaration = getattr(assessment, "health_declaration", None)
        if declaration:
            related_ids.add(str(declaration.id))
        exam = getattr(assessment, "physical_examination", None)
        if exam:
            related_ids.add(str(exam.id))
        related_ids.update(str(item.id) for item in assessment.lab_tests.all())
        related_ids.update(str(item.id) for item in assessment.vaccinations.all())
        certificate_request = getattr(assessment, "certificate_request", None)
        if certificate_request:
            related_ids.add(str(certificate_request.id))
        certificate = getattr(assessment, "certificate", None)
        if certificate:
            related_ids.add(str(certificate.id))

        logs = (
            AuditLog.objects.select_related("actor")
            .filter(Q(target_id__in=related_ids) | Q(metadata__assessment_id=str(assessment.id)))
            .order_by("created_at", "id")
        )
        return [
            {
                "id": log.id,
                "action": log.action,
                "event": (log.metadata or {}).get("event", ""),
                "label": cls.timeline_label(log),
                "actor_name": (log.actor.get_full_name() or log.actor.email) if log.actor else "",
                "actor_role": getattr(log.actor, "role", "") if log.actor else "",
                "target_type": log.target_type,
                "target_id": log.target_id,
                "metadata": log.metadata or {},
                "created_at": log.created_at,
            }
            for log in logs
        ]

    @classmethod
    def _active_policy(cls):
        return NationalPolicyConfig.objects.order_by("-updated_at").first()

    @classmethod
    def payment_required(cls) -> bool:
        policy = cls._active_policy()
        return True if policy is None else policy.payment_before_assessment_required

    @classmethod
    def profile_complete(cls, assessment) -> bool:
        food_handler = assessment.food_handler
        required_values = [
            food_handler.full_name,
            food_handler.date_of_birth,
            food_handler.gender,
            food_handler.nin,
            food_handler.phone,
            food_handler.email,
            food_handler.home_address,
            food_handler.state_id,
            food_handler.food_handler_category,
        ]
        return all(bool(value) for value in required_values)

    @classmethod
    def has_confirmed_payment(cls, assessment) -> bool:
        return bool(assessment.payment_transaction and assessment.payment_transaction.status == PaymentStatus.SUCCESS)

    @classmethod
    def has_ready_appointment(cls, assessment) -> bool:
        if not assessment.appointment_id:
            return False
        return assessment.appointment.status in {
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.COMPLETED,
        }

    @classmethod
    def declaration_ready_for_appointment(cls, assessment) -> bool:
        return assessment.declaration_status in {StepStatus.SUBMITTED, StepStatus.VALIDATED}

    @classmethod
    def _blocker(cls, code, label, detail, *, blocking=True):
        return {
            "code": code,
            "label": label,
            "detail": detail,
            "blocking": blocking,
        }

    @classmethod
    def prerequisite_blockers(cls, assessment):
        blockers = []
        warnings = []

        if not cls.profile_complete(assessment):
            blockers.append(
                cls._blocker(
                    "profile_incomplete",
                    "Profile incomplete",
                    "Complete the food handler profile before the assessment can continue.",
                )
            )
        if not cls.has_verified_identity(assessment):
            blockers.append(
                cls._blocker(
                    "nin_unverified",
                    "NIN not verified",
                    "Verify or approve an override for the food handler NIN before clinical sign-off.",
                )
            )
        if not assessment.facility.can_conduct_assessments:
            blockers.append(
                cls._blocker(
                    "facility_not_current",
                    "Facility accreditation not current",
                    "The selected facility must be active and currently accredited.",
                )
            )
        if cls.payment_required() and not cls.has_confirmed_payment(assessment):
            blockers.append(
                cls._blocker(
                    "payment_required",
                    "Payment pending",
                    "Successful assessment payment is required before the appointment can be confirmed.",
                )
            )
        if (
            assessment.status != AssessmentStatus.PAYMENT_PENDING
            and assessment.appointment_id
            and assessment.appointment.status in {AppointmentStatus.PENDING, AppointmentStatus.RESCHEDULED}
            and not cls.declaration_ready_for_appointment(assessment)
        ):
            blockers.append(
                cls._blocker(
                    "declaration_required_for_confirmation",
                    "Declaration required before appointment confirmation",
                    "The food handler must submit the health declaration before the facility can confirm this appointment.",
                )
            )
        if assessment.status != AssessmentStatus.PAYMENT_PENDING and not cls.has_ready_appointment(assessment):
            blockers.append(
                cls._blocker(
                    "appointment_required",
                    "Appointment not confirmed",
                    "Book and confirm an appointment before clinical workflow begins.",
                )
            )
        if assessment.status in cls.CLINICAL_STATUSES and not assessment.doctor_id:
            blockers.append(
                cls._blocker(
                    "doctor_unassigned",
                    "Doctor not assigned",
                    "Assign an authorized doctor from the assessment facility.",
                )
            )
        if assessment.doctor_id and assessment.doctor.organization_id != assessment.facility.organization_id:
            blockers.append(
                cls._blocker(
                    "doctor_not_authorized",
                    "Doctor not authorized",
                    "The assigned doctor must belong to the assessment facility organization.",
                )
            )
        if assessment.employer_id and not assessment.food_handler.business_branch_id:
            warnings.append(
                cls._blocker(
                    "branch_missing",
                    "Branch not linked",
                    "Linking the handler to a business branch improves employer compliance reporting.",
                    blocking=False,
                )
            )
        if IllnessReport.objects.filter(food_handler=assessment.food_handler).exclude(
            clearance_status__in=[ClearanceStatus.CLEARED, ClearanceStatus.REJECTED]
        ).exists():
            blockers.append(
                cls._blocker(
                    "unresolved_illness",
                    "Unresolved illness report",
                    "Resolve active illness or exclusion records before final fitness sign-off.",
                )
            )
        return blockers, warnings

    @classmethod
    def status_steps(cls, assessment):
        step_values = [
            ("profile", "Profile", cls.profile_complete(assessment)),
            ("identity", "Identity", cls.has_verified_identity(assessment)),
            ("payment", "Payment", cls.has_confirmed_payment(assessment) or not cls.payment_required()),
            ("appointment", "Appointment", cls.has_ready_appointment(assessment)),
            ("declaration", "Declaration", assessment.declaration_status in {StepStatus.SUBMITTED, StepStatus.VALIDATED}),
            ("physical_exam", "Physical exam", assessment.physical_exam_status == StepStatus.COMPLETED),
            ("lab", "Lab review", assessment.lab_status == StepStatus.REVIEWED),
            ("vaccination", "Vaccination review", assessment.vaccination_status == StepStatus.REVIEWED),
            ("decision", "Doctor decision", assessment.final_decision != FitnessDecision.PENDING and assessment.signed_at is not None),
            ("certificate", "Certificate", assessment.status == AssessmentStatus.CERTIFICATE_ISSUED),
        ]
        return [
            {"code": code, "label": label, "status": "complete" if complete else "pending"}
            for code, label, complete in step_values
        ]

    @classmethod
    def next_action(cls, assessment, blockers):
        blocker_actions = {
            "profile_incomplete": ("complete_profile", "Complete food handler profile"),
            "nin_unverified": ("verify_nin", "Verify NIN"),
            "facility_not_current": ("select_facility", "Use an approved facility"),
            "payment_required": ("complete_payment", "Complete payment"),
            "declaration_required_for_confirmation": ("submit_declaration", "Submit health declaration"),
            "appointment_required": ("confirm_appointment", "Confirm appointment"),
            "doctor_unassigned": ("assign_doctor", "Assign doctor"),
            "doctor_not_authorized": ("assign_doctor", "Assign authorized doctor"),
            "unresolved_illness": ("resolve_illness", "Resolve illness case"),
        }
        for blocker in blockers:
            action = blocker_actions.get(blocker["code"])
            if action:
                return {"code": action[0], "label": action[1]}

        if assessment.status == AssessmentStatus.CLOSED:
            return {"code": "closed", "label": "Assessment closed"}
        if assessment.declaration_status == StepStatus.PENDING:
            return {"code": "submit_declaration", "label": "Submit health declaration"}
        if assessment.declaration_status == StepStatus.SUBMITTED:
            return {"code": "validate_declaration", "label": "Doctor validates declaration"}
        if assessment.physical_exam_status == StepStatus.PENDING:
            return {"code": "complete_physical_exam", "label": "Complete physical examination"}
        if assessment.lab_status != StepStatus.REVIEWED:
            return {"code": "complete_lab_workflow", "label": "Complete lab workflow"}
        if assessment.vaccination_status != StepStatus.REVIEWED:
            return {"code": "review_vaccination", "label": "Review vaccination status"}
        if assessment.final_decision == FitnessDecision.PENDING or not assessment.signed_at:
            return {"code": "finalize_decision", "label": "Sign final fitness decision"}
        if assessment.status == AssessmentStatus.FIT:
            return {"code": "request_certificate", "label": "Request certificate"}
        if assessment.status == AssessmentStatus.SUBMITTED_FOR_STATE_VALIDATION:
            return {"code": "await_state_validation", "label": "Await State validation"}
        if assessment.status == AssessmentStatus.CERTIFICATE_ISSUED:
            return {"code": "download_certificate", "label": "Download certificate"}
        return {"code": "monitor", "label": "Monitor assessment"}

    @classmethod
    def status_snapshot(cls, assessment):
        blockers, warnings = cls.prerequisite_blockers(assessment)
        return {
            "assessment": str(assessment.id),
            "current_status": assessment.status,
            "current_status_label": assessment.get_status_display(),
            "stage": assessment.status,
            "stage_label": assessment.get_status_display(),
            "next_action": cls.next_action(assessment, blockers),
            "blockers": blockers,
            "warnings": warnings,
            "steps": cls.status_steps(assessment),
            "can_cancel": assessment.status not in cls.TERMINAL_STATUSES,
            "can_close": assessment.status != AssessmentStatus.CLOSED,
            "can_proceed": not blockers,
            "updated_at": assessment.updated_at.isoformat() if assessment.updated_at else "",
        }

    @classmethod
    def ensure_can_cancel_assessment(cls, assessment, actor):
        if assessment.status in cls.TERMINAL_STATUSES:
            raise ValidationError("This assessment can no longer be cancelled.")
        if actor.role == UserRole.FOOD_HANDLER and assessment.food_handler.user_id == actor.id:
            return
        if actor.role == UserRole.EMPLOYER and getattr(actor, "employer", None) == assessment.employer:
            return
        if actor.role in {UserRole.FACILITY_ADMIN, UserRole.DOCTOR} and actor.organization_id == assessment.facility.organization_id:
            return
        if actor.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR} and actor.state_id == assessment.facility.state_id:
            return
        if actor.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return
        raise PermissionDenied("You do not have permission to cancel this assessment.")

    @classmethod
    def ensure_can_close_assessment(cls, assessment, actor):
        if assessment.status == AssessmentStatus.CLOSED:
            raise ValidationError("This assessment is already closed.")
        if actor.role in {UserRole.FACILITY_ADMIN, UserRole.DOCTOR} and actor.organization_id == assessment.facility.organization_id:
            return
        if actor.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR} and actor.state_id == assessment.facility.state_id:
            return
        if actor.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return
        raise PermissionDenied("You do not have permission to close this assessment.")

    @classmethod
    @transaction.atomic
    def cancel_assessment(cls, *, assessment, actor, reason="", notes=""):
        cls.ensure_can_cancel_assessment(assessment, actor)
        if assessment.appointment_id and assessment.appointment.status not in {AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED}:
            assessment.appointment.status = AppointmentStatus.CANCELLED
            if reason:
                assessment.appointment.reason = reason
            if notes:
                assessment.appointment.notes = notes
            assessment.appointment.save(update_fields=["status", "reason", "notes", "updated_at"])
        assessment.status = AssessmentStatus.CLOSED
        assessment.save(update_fields=["status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={"event": "assessment_cancelled", "reason": reason},
        )
        return assessment

    @classmethod
    @transaction.atomic
    def close_assessment(cls, *, assessment, actor, reason="", notes=""):
        cls.ensure_can_close_assessment(assessment, actor)
        assessment.status = AssessmentStatus.CLOSED
        assessment.save(update_fields=["status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={"event": "assessment_closed", "reason": reason, "notes": notes},
        )
        return assessment

    @classmethod
    def _appointment_assessment(cls, appointment):
        return appointment.assessments.select_related("payment_transaction", "employer", "food_handler__user").first()

    @classmethod
    def ensure_declaration_owner(cls, assessment, actor):
        if actor.role != UserRole.FOOD_HANDLER or assessment.food_handler.user_id != actor.id:
            raise PermissionDenied("You can only manage your own declaration.")

    @classmethod
    def _declaration_templates_queryset(cls, *, assessment):
        today = timezone.localdate()
        return (
            AssessmentFormTemplate.objects.filter(
                form_type=AssessmentFormType.HEALTH_DECLARATION,
                status__in=[AssessmentFormStatus.ACTIVE, AssessmentFormStatus.PUBLISHED],
            )
            .filter(Q(effective_from__isnull=True) | Q(effective_from__lte=today))
            .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=today))
            .filter(
                Q(scope=AssessmentFormScope.NATIONAL)
                | Q(scope=AssessmentFormScope.STATE, state=assessment.facility.state)
                | Q(scope=AssessmentFormScope.FACILITY, facility=assessment.facility)
            )
            .prefetch_related("sections__questions")
        )

    @classmethod
    def _pick_best_template(cls, queryset, *, scope, assessment):
        filters = {"scope": scope}
        if scope == AssessmentFormScope.STATE:
            filters["state"] = assessment.facility.state
        elif scope == AssessmentFormScope.FACILITY:
            filters["facility"] = assessment.facility
        return (
            queryset.filter(**filters)
            .order_by(
                models.Case(
                    models.When(status=AssessmentFormStatus.ACTIVE, then=0),
                    models.When(status=AssessmentFormStatus.PUBLISHED, then=1),
                    default=2,
                ),
                "-version",
                "-updated_at",
            )
            .first()
        )

    @classmethod
    def resolve_declaration_template_snapshot(cls, *, assessment):
        templates = cls._declaration_templates_queryset(assessment=assessment)
        federal_template = cls._pick_best_template(templates, scope=AssessmentFormScope.NATIONAL, assessment=assessment)
        state_template = cls._pick_best_template(templates, scope=AssessmentFormScope.STATE, assessment=assessment)
        facility_template = cls._pick_best_template(templates, scope=AssessmentFormScope.FACILITY, assessment=assessment)
        selected_template = facility_template or state_template or federal_template
        merged_schema = AssessmentFormResponseService.snapshot_template(selected_template) if selected_template else {}
        existing_snapshot = AssessmentFormTemplateSnapshot.objects.filter(assessment=assessment).first()
        previous_snapshot = None
        if existing_snapshot:
            previous_snapshot = {
                "federal_template_id": str(existing_snapshot.federal_template_id) if existing_snapshot.federal_template_id else "",
                "state_template_id": str(existing_snapshot.state_template_id) if existing_snapshot.state_template_id else "",
                "facility_template_id": str(existing_snapshot.facility_template_id) if existing_snapshot.facility_template_id else "",
                "selected_template_id": str(
                    existing_snapshot.facility_template_id
                    or existing_snapshot.state_template_id
                    or existing_snapshot.federal_template_id
                    or ""
                ),
            }
        snapshot, created = AssessmentFormTemplateSnapshot.objects.update_or_create(
            assessment=assessment,
            defaults={
                "federal_template": federal_template,
                "state_template": state_template,
                "facility_template": facility_template,
                "merged_schema": merged_schema,
                "generated_at": timezone.now(),
            },
        )
        current_snapshot = {
            "federal_template_id": str(federal_template.id) if federal_template else "",
            "state_template_id": str(state_template.id) if state_template else "",
            "facility_template_id": str(facility_template.id) if facility_template else "",
            "selected_template_id": str(selected_template.id) if selected_template else "",
        }
        if created or previous_snapshot != current_snapshot:
            log_action(
                action=AuditAction.CREATE if created else AuditAction.UPDATE,
                actor=getattr(assessment.food_handler, "user", None),
                target=assessment,
                old_value=previous_snapshot or {},
                new_value=current_snapshot,
                metadata=assessment_audit_metadata(
                    event="final_merged_form_generated",
                    actor=getattr(assessment.food_handler, "user", None),
                    entity=assessment,
                    owner_level=AssessmentOwnerLevel.FACILITY,
                    template_snapshot_id=str(snapshot.id),
                ),
            )
        return snapshot, selected_template

    @classmethod
    def _declaration_payload(cls, data):
        fields = [
            "diarrhoea_vomiting_last_7_days",
            "fever_more_than_one_week",
            "skin_trouble",
            "boils_styes_sepsis",
            "discharge_eye_ear_nose_mouth",
            "recurring_skin_or_ear_infection",
            "recurring_bowel_disorder",
            "cholera_contact_last_5_days",
            "diarrhoea_vomiting_contact_last_7_days",
            "typhoid_paratyphoid_jaundice_contact_last_21_days",
            "typhoid_or_paratyphoid_carrier",
            "previous_or_current_typhoid",
            "certified_true",
        ]
        return {field: data.get(field, False) for field in fields}

    @classmethod
    def _get_or_create_declaration(cls, assessment):
        declaration, _ = HealthDeclaration.objects.get_or_create(assessment=assessment)
        return declaration

    @classmethod
    def _current_declaration_response(cls, *, assessment):
        return (
            AssessmentFormResponse.objects.select_related("template_snapshot", "template")
            .filter(
                assessment=assessment,
                template__form_type=AssessmentFormType.HEALTH_DECLARATION,
            )
            .exclude(status=AssessmentFormResponseStatus.SUPERSEDED)
            .order_by("-version", "-updated_at")
            .first()
        )

    @classmethod
    def _declaration_response_from_data(cls, *, data):
        response_data = data.get("response_data")
        if isinstance(response_data, dict):
            return response_data
        return cls._declaration_payload(data)

    @classmethod
    def _sync_declaration_from_response(cls, *, declaration, response_data):
        updates = []
        for field, value in cls._declaration_payload(response_data).items():
            setattr(declaration, field, value)
            updates.append(field)
        declaration.certified_true = bool(response_data.get("certified_true", declaration.certified_true))
        declaration.risk_flag = declaration.calculate_risk_flag() or any(
            isinstance(value, bool) and value
            for key, value in response_data.items()
            if key != "certified_true"
        )
        updates.extend(["certified_true", "risk_flag"])
        declaration.save(update_fields=updates + ["updated_at"])
        return declaration

    @classmethod
    def _ensure_declaration_form_response(cls, *, assessment, actor=None):
        snapshot, template = cls.resolve_declaration_template_snapshot(assessment=assessment)
        if not template:
            return None, snapshot
        response = cls._current_declaration_response(assessment=assessment)
        if response:
            changed = False
            if response.template_id != template.id:
                response.template = template
                response.template_version = template.version
                response.question_snapshot = snapshot.merged_schema
                changed = True
            if response.template_snapshot_id != snapshot.id:
                response.template_snapshot = snapshot
                changed = True
            if changed:
                response.save(update_fields=["template", "template_version", "question_snapshot", "template_snapshot", "updated_at"])
            return response, snapshot
        response = AssessmentFormResponseService.assign(
            assessment=assessment,
            template=template,
            is_required=True,
            actor=actor,
        )
        response.template_snapshot = snapshot
        response.question_snapshot = snapshot.merged_schema
        response.save(update_fields=["template_snapshot", "question_snapshot", "updated_at"])
        return response, snapshot

    @classmethod
    def declaration_detail(cls, *, assessment, actor=None):
        declaration = cls._get_or_create_declaration(assessment)
        response, _ = cls._ensure_declaration_form_response(assessment=assessment, actor=actor)
        declaration._current_form_response = response
        return declaration

    @classmethod
    def _notify_appointment_change(cls, *, appointment, event, actor):
        assessment = cls._appointment_assessment(appointment)
        recipients = [appointment.food_handler.user]
        employer_user = getattr(getattr(appointment.food_handler, "employer", None), "user", None)
        if employer_user:
            recipients.append(employer_user)

        for recipient in {user for user in recipients if user}:
            Notification.objects.create(
                recipient=recipient,
                category=NotificationCategory.SYSTEM,
                title="Appointment updated",
                message=f"Your FoodCert NG assessment appointment was {event.replace('_', ' ')}.",
            )

    @classmethod
    def _payment_confirmed_for_appointment(cls, appointment):
        assessment = cls._appointment_assessment(appointment)
        if not assessment or not assessment.payment_transaction:
            return False
        if assessment.payment_transaction.status == PaymentStatus.SUCCESS:
            return True
        metadata = assessment.payment_transaction.metadata or {}
        return bool(metadata.get("pay_at_facility_allowed") or metadata.get("payment_override_status") == "waived")

    @classmethod
    @transaction.atomic
    def confirm_appointment(cls, *, appointment, actor, notes=""):
        ensure_facility_admin_for_facility(actor, appointment.facility)
        ensure_approved_facility(appointment.facility)
        if not cls._payment_confirmed_for_appointment(appointment):
            raise ValidationError("Successful payment is required before confirming this appointment.")
        appointment.status = AppointmentStatus.CONFIRMED
        if notes:
            appointment.notes = notes
        assessment = cls._appointment_assessment(appointment)
        if assessment:
            if not cls.declaration_ready_for_appointment(assessment):
                AssessmentFormNotificationService.notify_appointment_blocked_missing_declaration(assessment=assessment)
                log_action(
                    action=AuditAction.WORKFLOW_TRANSITION,
                    actor=actor,
                    target=assessment,
                    old_value={"declaration_status": assessment.declaration_status},
                    metadata=assessment_audit_metadata(
                        event="assessment_blocked_due_to_missing_declaration",
                        actor=actor,
                        entity=assessment,
                        reason="Health declaration submission is required before confirming this appointment.",
                    ),
                )
                raise ValidationError("Health declaration submission is required before confirming this appointment.")
            assessment.status = AssessmentStatus.APPOINTMENT_BOOKED
            assessment.assessment_date = appointment.appointment_date
            assessment.save(update_fields=["status", "assessment_date", "updated_at"])
        appointment.save(update_fields=["status", "notes", "updated_at"])
        cls._notify_appointment_change(appointment=appointment, event="appointment_confirmed", actor=actor)
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=appointment, metadata={"event": "appointment_confirmed"})
        return appointment

    @classmethod
    @transaction.atomic
    def reschedule_appointment(cls, *, appointment, actor, appointment_date, reason="", notes=""):
        ensure_facility_admin_for_facility(actor, appointment.facility)
        ensure_approved_facility(appointment.facility)
        appointment.appointment_date = appointment_date
        appointment.status = AppointmentStatus.RESCHEDULED
        if reason:
            appointment.reason = reason
        if notes:
            appointment.notes = notes
        appointment.save(update_fields=["appointment_date", "status", "reason", "notes", "updated_at"])
        assessment = cls._appointment_assessment(appointment)
        if assessment:
            assessment.assessment_date = appointment.appointment_date
            assessment.save(update_fields=["assessment_date", "updated_at"])
        cls._notify_appointment_change(appointment=appointment, event="appointment_rescheduled", actor=actor)
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=appointment, metadata={"event": "appointment_rescheduled"})
        return appointment

    @classmethod
    @transaction.atomic
    def cancel_appointment(cls, *, appointment, actor, reason="", notes=""):
        ensure_facility_admin_for_facility(actor, appointment.facility)
        appointment.status = AppointmentStatus.CANCELLED
        if reason:
            appointment.reason = reason
        if notes:
            appointment.notes = notes
        appointment.save(update_fields=["status", "reason", "notes", "updated_at"])
        cls._notify_appointment_change(appointment=appointment, event="appointment_cancelled", actor=actor)
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=appointment, metadata={"event": "appointment_cancelled"})
        return appointment

    @classmethod
    @transaction.atomic
    def mark_appointment_no_show(cls, *, appointment, actor, notes=""):
        ensure_facility_admin_for_facility(actor, appointment.facility)
        appointment.status = AppointmentStatus.NO_SHOW
        if notes:
            appointment.notes = notes
        appointment.save(update_fields=["status", "notes", "updated_at"])
        cls._notify_appointment_change(appointment=appointment, event="appointment_no_show", actor=actor)
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=appointment, metadata={"event": "appointment_no_show"})
        return appointment

    @classmethod
    @transaction.atomic
    def assign_appointment_doctor(cls, *, appointment, doctor, actor, reason=""):
        ensure_facility_admin_for_facility(actor, appointment.facility)
        ensure_doctor_for_facility(doctor, appointment.facility)
        assessment = cls._appointment_assessment(appointment)
        reassigning = bool(appointment.doctor_id and appointment.doctor_id != doctor.id)
        previous_doctor_id = str(appointment.doctor_id) if appointment.doctor_id else ""
        if reassigning and assessment and cls.doctor_work_started(assessment) and not reason:
            raise ValidationError("Reassignment reason is required once doctor work has started.")
        appointment.doctor = doctor
        appointment.save(update_fields=["doctor", "updated_at"])
        if assessment:
            assessment.doctor = doctor
            assessment.save(update_fields=["doctor", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=appointment,
            metadata={
                "event": "appointment_doctor_reassigned" if reassigning else "appointment_doctor_assigned",
                "doctor_id": str(doctor.id),
                "previous_doctor_id": previous_doctor_id,
                "reason": reason,
            },
        )
        return appointment

    @classmethod
    @transaction.atomic
    def assign_assessment_doctor(cls, *, assessment, doctor, actor, reason=""):
        ensure_facility_admin_for_facility(actor, assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        reassigning = bool(assessment.doctor_id and assessment.doctor_id != doctor.id)
        if reassigning and cls.doctor_work_started(assessment) and not reason:
            raise ValidationError("Reassignment reason is required once doctor work has started.")
        previous_doctor_id = str(assessment.doctor_id) if assessment.doctor_id else ""
        assessment.doctor = doctor
        assessment.save(update_fields=["doctor", "updated_at"])
        if assessment.appointment_id:
            assessment.appointment.doctor = doctor
            assessment.appointment.save(update_fields=["doctor", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={
                "event": "assessment_doctor_reassigned" if reassigning else "assessment_doctor_assigned",
                "doctor_id": str(doctor.id),
                "previous_doctor_id": previous_doctor_id,
                "reason": reason,
            },
        )
        return assessment

    @classmethod
    @transaction.atomic
    def assign_assessment_lab(cls, *, assessment, actor, lab_staff=None, lab_unit=None, reason=""):
        ensure_approved_facility(assessment.facility)
        if actor.organization_id != assessment.facility.organization_id:
            raise PermissionDenied("Facility staff can only assign internal cases for their own facility.")
        if actor.role not in {UserRole.FACILITY_ADMIN, UserRole.DOCTOR}:
            raise PermissionDenied("Only facility admins or doctors can assign lab work.")
        if actor.role == UserRole.DOCTOR:
            ensure_assigned_doctor_for_assessment(actor, assessment)
        if assessment.physical_exam_status != StepStatus.COMPLETED:
            raise ValidationError("Lab assignment can only happen after physical examination is completed.")
        if not lab_staff and not lab_unit:
            raise ValidationError("Select a lab staff member or lab unit to continue.")
        if lab_staff and lab_staff.role != UserRole.LAB_STAFF:
            raise ValidationError("Assigned lab staff must be a lab user.")
        if lab_staff and lab_staff.organization_id != assessment.facility.organization_id:
            raise ValidationError("Assigned lab staff must belong to this facility.")
        if lab_unit and (
            lab_unit.organization_id != assessment.facility.organization_id
            or lab_unit.unit_type != OrganizationUnitType.LAB_DEPARTMENT
        ):
            raise ValidationError("Assigned lab unit must be a lab department in this facility.")
        reassigning = (
            (assessment.assigned_lab_staff_id and getattr(lab_staff, "id", None) != assessment.assigned_lab_staff_id)
            or (assessment.assigned_lab_unit_id and getattr(lab_unit, "id", None) != assessment.assigned_lab_unit_id)
        )
        if reassigning and cls.lab_work_started(assessment) and not reason:
            raise ValidationError("Reassignment reason is required once lab work has started.")

        previous_staff_id = str(assessment.assigned_lab_staff_id) if assessment.assigned_lab_staff_id else ""
        previous_unit_id = str(assessment.assigned_lab_unit_id) if assessment.assigned_lab_unit_id else ""
        assigned_at = timezone.now()
        assessment.assigned_lab_staff = lab_staff
        assessment.assigned_lab_unit = lab_unit
        assessment.lab_assignment_reason = reason
        assessment.lab_assigned_by = actor
        assessment.lab_assigned_at = assigned_at
        assessment.save(
            update_fields=[
                "assigned_lab_staff",
                "assigned_lab_unit",
                "lab_assignment_reason",
                "lab_assigned_by",
                "lab_assigned_at",
                "updated_at",
            ]
        )
        assessment.lab_tests.update(assigned_lab_staff=lab_staff, assigned_lab_unit=lab_unit, updated_at=assigned_at)
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={
                "event": "assessment_lab_reassigned" if reassigning else "assessment_lab_assigned",
                "lab_staff_id": str(lab_staff.id) if lab_staff else "",
                "lab_unit_id": str(lab_unit.id) if lab_unit else "",
                "previous_lab_staff_id": previous_staff_id,
                "previous_lab_unit_id": previous_unit_id,
                "reason": reason,
            },
        )
        return assessment

    @classmethod
    @transaction.atomic
    def create_assessment(cls, *, food_handler, facility, payment_transaction=None, appointment=None, assessment_type=AssessmentType.STANDARD, actor=None):
        ensure_approved_facility(facility)
        if payment_transaction and payment_transaction.status == PaymentStatus.SUCCESS:
            status = AssessmentStatus.PAYMENT_CONFIRMED
        else:
            status = AssessmentStatus.PAYMENT_PENDING
        assessment = MedicalAssessment.objects.create(
            food_handler=food_handler,
            employer=food_handler.employer,
            facility=facility,
            appointment=appointment,
            assessment_date=appointment.appointment_date if appointment else None,
            payment_transaction=payment_transaction,
            assessment_type=assessment_type,
            status=status,
        )
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={"event": "assessment_created", "status": status},
        )
        AssessmentRequirementResolutionService.assign_forms(assessment=assessment, actor=actor)
        AssessmentFormNotificationService.notify_declaration_required(assessment=assessment)
        return assessment

    @classmethod
    @transaction.atomic
    def save_declaration_draft(cls, *, assessment, data, actor):
        cls.ensure_declaration_owner(assessment, actor)
        declaration = cls._get_or_create_declaration(assessment)
        response, _ = cls._ensure_declaration_form_response(assessment=assessment, actor=actor)
        if declaration.is_locked or declaration.validated_at:
            raise ValidationError("This declaration has been validated and is locked.")
        if declaration.submitted_at and not declaration.clarification_requested_at:
            raise ValidationError("Submitted declarations are read-only unless a doctor requests clarification.")
        if declaration.submitted_at and declaration.clarification_requested_at:
            declaration.version += 1
            declaration.submitted_at = None
            declaration.validated_by_doctor = None
            declaration.validated_at = None
        response_data = cls._declaration_response_from_data(data=data)
        if response:
            response = AssessmentFormResponseService.save_draft(
                response=response,
                response_data=response_data,
                actor=actor,
            )
            declaration._current_form_response = response
        cls._sync_declaration_from_response(declaration=declaration, response_data=response_data)
        declaration.is_locked = False
        declaration.save(
            update_fields=["version", "is_locked", "submitted_at", "validated_by_doctor", "validated_at", "updated_at"]
        )
        assessment.declaration_status = StepStatus.PENDING
        assessment.save(update_fields=["declaration_status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={"event": "declaration_draft_saved", "version": declaration.version, "risk_flag": declaration.risk_flag},
        )
        return declaration

    @classmethod
    @transaction.atomic
    def submit_declaration(cls, *, assessment, data, actor):
        cls.ensure_declaration_owner(assessment, actor)
        if not data.get("certified_true"):
            raise ValidationError("Food handler must certify that declaration answers are true.")
        declaration = getattr(assessment, "health_declaration", None)
        if declaration and (declaration.is_locked or declaration.validated_at):
            raise ValidationError("This declaration has already been validated and is locked.")
        if declaration and declaration.submitted_at and not declaration.clarification_requested_at:
            raise ValidationError("This declaration has already been submitted and is awaiting doctor review.")
        previous_snapshot = declaration_audit_snapshot(declaration) if declaration else {}
        correction_submission = bool(
            declaration
            and (
                declaration.clarification_requested_at
                or declaration.reopened_at
                or declaration.version > 1
            )
        )
        declaration = cls.save_declaration_draft(assessment=assessment, data=data, actor=actor)
        response = cls._current_declaration_response(assessment=assessment)
        if response:
            response = AssessmentFormResponseService.submit(response=response, actor=actor)
            declaration._current_form_response = response
        declaration.submitted_at = timezone.now()
        declaration.certified_true = True
        declaration.clarification_requested_by = None
        declaration.clarification_requested_at = None
        declaration.clarification_reason = ""
        declaration.save(
            update_fields=[
                "submitted_at",
                "certified_true",
                "clarification_requested_by",
                "clarification_requested_at",
                "clarification_reason",
                "updated_at",
            ]
        )
        assessment.declaration_status = StepStatus.SUBMITTED
        assessment.status = AssessmentStatus.DECLARATION_SUBMITTED
        assessment.save(update_fields=["declaration_status", "status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=declaration,
            old_value=previous_snapshot,
            new_value=declaration_audit_snapshot(declaration),
            metadata=assessment_audit_metadata(
                event="declaration_corrected" if correction_submission else "food_handler_declaration_submitted",
                actor=actor,
                entity=declaration,
                owner_level=AssessmentOwnerLevel.FACILITY,
                assessment_id=str(assessment.id),
                version=declaration.version,
                risk_flag=declaration.risk_flag,
            ),
        )
        AssessmentFormNotificationService.notify_declaration_submitted(declaration=declaration)
        AssessmentFormNotificationService.notify_high_risk_declaration_validation_required(declaration=declaration)
        return declaration

    @classmethod
    @transaction.atomic
    def validate_declaration(cls, *, declaration, doctor):
        assessment = declaration.assessment
        ensure_approved_facility(assessment.facility)
        ensure_assigned_doctor_for_assessment(doctor, assessment)
        if not declaration.submitted_at:
            raise ValidationError("Only submitted declarations can be validated.")
        if declaration.validated_at:
            raise ValidationError("This declaration has already been validated.")
        response = cls._current_declaration_response(assessment=assessment)
        if response and response.status != AssessmentFormResponseStatus.VALIDATED:
            response = AssessmentFormResponseService.validate(response=response, actor=doctor)
            declaration._current_form_response = response
        previous_snapshot = declaration_audit_snapshot(declaration)
        declaration.validated_by_doctor = doctor
        declaration.validated_at = timezone.now()
        declaration.is_locked = True
        declaration.save(update_fields=["validated_by_doctor", "validated_at", "is_locked", "updated_at"])
        assessment.doctor = doctor
        assessment.declaration_status = StepStatus.VALIDATED
        assessment.status = AssessmentStatus.DECLARATION_VALIDATED
        assessment.save(update_fields=["doctor", "declaration_status", "status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=declaration,
            old_value=previous_snapshot,
            new_value=declaration_audit_snapshot(declaration),
            metadata=assessment_audit_metadata(
                event="doctor_validated_declaration",
                actor=doctor,
                entity=declaration,
                owner_level=AssessmentOwnerLevel.FACILITY,
                assessment_id=str(assessment.id),
                version=declaration.version,
            ),
        )
        return declaration

    @classmethod
    @transaction.atomic
    def request_declaration_clarification(cls, *, declaration, doctor, reason):
        assessment = declaration.assessment
        ensure_approved_facility(assessment.facility)
        ensure_assigned_doctor_for_assessment(doctor, assessment)
        if declaration.validated_at:
            raise ValidationError("Validated declarations are locked and cannot be sent back for changes.")
        previous_snapshot = declaration_audit_snapshot(declaration)
        response = cls._current_declaration_response(assessment=assessment)
        if response and response.status not in {
            AssessmentFormResponseStatus.REOPENED,
            AssessmentFormResponseStatus.CLARIFICATION_REQUESTED,
            AssessmentFormResponseStatus.DRAFT,
            AssessmentFormResponseStatus.NOT_STARTED,
        }:
            response = AssessmentFormResponseService.reopen(response=response, actor=doctor, reason=reason)
        if response:
            declaration._current_form_response = response
        declaration.clarification_requested_by = doctor
        declaration.clarification_requested_at = timezone.now()
        declaration.clarification_reason = reason
        declaration.is_locked = False
        declaration.save(
            update_fields=[
                "clarification_requested_by",
                "clarification_requested_at",
                "clarification_reason",
                "is_locked",
                "updated_at",
            ]
        )
        assessment.declaration_status = StepStatus.PENDING
        assessment.save(update_fields=["declaration_status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=declaration,
            old_value=previous_snapshot,
            new_value=declaration_audit_snapshot(declaration),
            metadata=assessment_audit_metadata(
                event="doctor_rejected_declaration",
                actor=doctor,
                entity=declaration,
                owner_level=AssessmentOwnerLevel.FACILITY,
                assessment_id=str(assessment.id),
                reason=reason,
            ),
        )
        AssessmentFormNotificationService.notify_declaration_correction_required(declaration=declaration)
        return declaration

    @classmethod
    @transaction.atomic
    def reopen_declaration(cls, *, declaration, doctor, reason):
        assessment = declaration.assessment
        ensure_approved_facility(assessment.facility)
        ensure_assigned_doctor_for_assessment(doctor, assessment)
        if declaration.is_locked or declaration.validated_at:
            raise ValidationError("Validated declarations are locked and cannot be reopened.")
        previous_snapshot = declaration_audit_snapshot(declaration)
        response = cls._current_declaration_response(assessment=assessment)
        if response and response.status not in {
            AssessmentFormResponseStatus.REOPENED,
            AssessmentFormResponseStatus.CLARIFICATION_REQUESTED,
        }:
            response = AssessmentFormResponseService.reopen(response=response, actor=doctor, reason=reason)
        if response:
            declaration._current_form_response = response
        declaration.version += 1
        declaration.submitted_at = None
        declaration.certified_true = False
        declaration.reopened_by = doctor
        declaration.reopened_at = timezone.now()
        declaration.reopen_reason = reason
        declaration.clarification_requested_by = doctor
        declaration.clarification_requested_at = timezone.now()
        declaration.clarification_reason = reason
        declaration.save(
            update_fields=[
                "version",
                "submitted_at",
                "certified_true",
                "reopened_by",
                "reopened_at",
                "reopen_reason",
                "clarification_requested_by",
                "clarification_requested_at",
                "clarification_reason",
                "updated_at",
            ]
        )
        assessment.declaration_status = StepStatus.PENDING
        assessment.save(update_fields=["declaration_status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=declaration,
            old_value=previous_snapshot,
            new_value=declaration_audit_snapshot(declaration),
            metadata=assessment_audit_metadata(
                event="declaration_reopened",
                actor=doctor,
                entity=declaration,
                owner_level=AssessmentOwnerLevel.FACILITY,
                assessment_id=str(assessment.id),
                version=declaration.version,
                reason=reason,
            ),
        )
        AssessmentFormNotificationService.notify_declaration_correction_required(declaration=declaration)
        return declaration

    @classmethod
    @transaction.atomic
    def save_physical_exam_draft(cls, *, assessment, doctor, data):
        ensure_approved_facility(assessment.facility)
        ensure_assigned_doctor_for_assessment(doctor, assessment)
        exam, _ = PhysicalExamination.objects.update_or_create(
            assessment=assessment,
            defaults={**data, "examined_by": doctor, "examined_at": timezone.now(), "is_completed": False, "completed_at": None},
        )
        exam.risk_flag = exam.calculate_risk_flag()
        exam.save(update_fields=["risk_flag", "updated_at"])
        assessment.doctor = doctor
        assessment.physical_exam_status = StepStatus.SUBMITTED
        assessment.save(update_fields=["doctor", "physical_exam_status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=assessment,
            metadata={"event": "physical_exam_draft_saved", "risk_flag": exam.risk_flag},
        )
        return exam

    @classmethod
    @transaction.atomic
    def complete_physical_exam(cls, *, assessment, doctor, data):
        exam = cls.save_physical_exam_draft(assessment=assessment, doctor=doctor, data=data)
        exam.is_completed = True
        exam.completed_at = timezone.now()
        exam.risk_flag = exam.calculate_risk_flag()
        exam.save(update_fields=["is_completed", "completed_at", "risk_flag", "updated_at"])
        assessment.physical_exam_status = StepStatus.COMPLETED
        assessment.status = AssessmentStatus.PHYSICAL_EXAM_COMPLETED
        assessment.save(update_fields=["physical_exam_status", "status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=doctor, target=assessment, metadata={"event": "physical_exam_completed", "risk_flag": exam.risk_flag})
        return exam

    @classmethod
    def has_verified_identity(cls, assessment) -> bool:
        if assessment.identity_verification_status == IdentityVerificationStatus.MISMATCH:
            return False
        if assessment.identity_verification_status == IdentityVerificationStatus.VERIFIED:
            return True
        return assessment.food_handler.nin_verifications.filter(
            status__in=[NINVerificationStatus.VERIFIED, NINVerificationStatus.OVERRIDE_APPROVED]
        ).exists()

    @classmethod
    def has_identity_mismatch(cls, assessment) -> bool:
        return assessment.identity_verification_status == IdentityVerificationStatus.MISMATCH

    @classmethod
    def ensure_identity_clear_for_processing(cls, assessment):
        if cls.has_identity_mismatch(assessment):
            raise ValidationError("This assessment is paused because an identity mismatch has been flagged.")

    @classmethod
    @transaction.atomic
    def check_in_assessment(cls, *, assessment, actor, notes=""):
        ensure_approved_facility(assessment.facility)
        if actor.organization_id != assessment.facility.organization_id:
            raise PermissionDenied("Facility staff can only check in assessments for their own facility.")
        if not assessment.appointment_id:
            raise ValidationError("A linked appointment is required before check-in.")
        if assessment.appointment.status in {AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW}:
            raise ValidationError("This appointment cannot be checked in from its current status.")

        now = timezone.now()
        assessment.checked_in_at = now
        assessment.checked_in_by = actor
        assessment.check_in_notes = notes
        assessment.identity_verification_status = IdentityVerificationStatus.VERIFIED
        assessment.identity_verified_at = now
        assessment.identity_verified_by = actor
        assessment.identity_mismatch_reason = ""
        assessment.identity_mismatch_flagged_at = None
        assessment.identity_mismatch_flagged_by = None
        assessment.assessment_date = assessment.assessment_date or now
        if assessment.status in {
            AssessmentStatus.DRAFT,
            AssessmentStatus.PAYMENT_PENDING,
            AssessmentStatus.PAYMENT_CONFIRMED,
            AssessmentStatus.APPOINTMENT_BOOKED,
        }:
            assessment.status = AssessmentStatus.ASSESSMENT_IN_PROGRESS
        assessment.save(
            update_fields=[
                "checked_in_at",
                "checked_in_by",
                "check_in_notes",
                "identity_verification_status",
                "identity_verified_at",
                "identity_verified_by",
                "identity_mismatch_reason",
                "identity_mismatch_flagged_at",
                "identity_mismatch_flagged_by",
                "assessment_date",
                "status",
                "updated_at",
            ]
        )
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={"event": "facility_assessment_checked_in", "identity_status": assessment.identity_verification_status},
        )
        return assessment

    @classmethod
    @transaction.atomic
    def flag_identity_mismatch(cls, *, assessment, actor, reason):
        ensure_approved_facility(assessment.facility)
        if actor.organization_id != assessment.facility.organization_id:
            raise PermissionDenied("Facility staff can only manage assessments for their own facility.")
        if not assessment.appointment_id:
            raise ValidationError("A linked appointment is required before identity review.")

        assessment.identity_verification_status = IdentityVerificationStatus.MISMATCH
        assessment.identity_mismatch_reason = reason
        assessment.identity_mismatch_flagged_at = timezone.now()
        assessment.identity_mismatch_flagged_by = actor
        assessment.identity_verified_at = None
        assessment.identity_verified_by = None
        assessment.checked_in_at = None
        assessment.checked_in_by = None
        assessment.check_in_notes = ""
        if assessment.status == AssessmentStatus.ASSESSMENT_IN_PROGRESS:
            assessment.status = AssessmentStatus.APPOINTMENT_BOOKED
        assessment.save(
            update_fields=[
                "identity_verification_status",
                "identity_mismatch_reason",
                "identity_mismatch_flagged_at",
                "identity_mismatch_flagged_by",
                "identity_verified_at",
                "identity_verified_by",
                "checked_in_at",
                "checked_in_by",
                "check_in_notes",
                "status",
                "updated_at",
            ]
        )
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={"event": "facility_identity_mismatch_flagged", "reason": reason[:240]},
        )
        return assessment

    @classmethod
    def validate_final_decision_ready(cls, assessment, doctor):
        ensure_approved_facility(assessment.facility)
        ensure_assigned_doctor_for_assessment(doctor, assessment)
        if assessment.signed_at:
            raise ValidationError("Final decision has already been signed and cannot be changed.")
        if not assessment.payment_transaction or assessment.payment_transaction.status != PaymentStatus.SUCCESS:
            raise ValidationError("Assessment payment must be successful before a final decision.")
        if not cls.has_verified_identity(assessment):
            raise ValidationError("Food handler NIN must be verified or override-approved before final decision.")
        if assessment.declaration_status != StepStatus.VALIDATED:
            raise ValidationError("Health declaration must be doctor-validated before final decision.")
        if assessment.physical_exam_status != StepStatus.COMPLETED:
            raise ValidationError("Physical examination must be completed before final decision.")
        if assessment.lab_status != StepStatus.REVIEWED:
            raise ValidationError("Required lab tests must be reviewed before final decision.")
        if assessment.vaccination_status != StepStatus.REVIEWED:
            raise ValidationError("Vaccination status must be reviewed before final decision.")
        from apps.vaccinations.models import VaccinationStatus, VaccineType

        acceptable_statuses = {
            VaccinationStatus.VALID,
            VaccinationStatus.DOCTOR_CLEARED,
            VaccinationStatus.ADMINISTERED,
            VaccinationStatus.SECOND_DOSE_DUE,
        }
        has_typhoid_clearance = assessment.vaccinations.filter(
            vaccine_type=VaccineType.TYPHOID,
            status__in=acceptable_statuses,
        ).exists()
        has_hepatitis_clearance = assessment.vaccinations.filter(
            vaccine_type=VaccineType.HEPATITIS_A,
            status__in=acceptable_statuses,
        ).exists()
        if not has_typhoid_clearance or not has_hepatitis_clearance:
            raise ValidationError("Typhoid and Hepatitis A vaccination compliance must be reviewed before final decision.")
        if IllnessReport.objects.filter(food_handler=assessment.food_handler).exclude(
            clearance_status__in=[ClearanceStatus.CLEARED, ClearanceStatus.REJECTED]
        ).exists():
            raise ValidationError("Food handler has an unresolved illness or exclusion issue.")

    @classmethod
    def workflow_recommendation(cls, assessment):
        from apps.lab_tests.models import LabReviewRecommendation, LabTestStatus
        from apps.vaccinations.models import VaccinationStatus, VaccineType

        declaration = getattr(assessment, "health_declaration", None)
        physical_exam = getattr(assessment, "physical_examination", None)
        lab_tests = list(assessment.lab_tests.all())
        vaccinations = list(assessment.vaccinations.all())

        declaration_risk = bool(declaration and declaration.risk_flag)
        physical_exam_risk = bool(physical_exam and physical_exam.risk_flag)
        flagged_lab_results = [
            test for test in lab_tests
            if test.is_flagged or test.status in {LabTestStatus.POSITIVE, LabTestStatus.INCONCLUSIVE, LabTestStatus.REPEAT_REQUIRED}
        ]
        repeat_required_tests = [test for test in lab_tests if test.repeat_required or test.status == LabTestStatus.REPEAT_REQUIRED]

        vaccination_concerns = []
        tracked_vaccines = {VaccineType.TYPHOID, VaccineType.HEPATITIS_A}
        compliance_statuses = {record.vaccine_type: record.compliance_status for record in vaccinations if record.vaccine_type in tracked_vaccines}
        for vaccine_type in tracked_vaccines:
            compliance = compliance_statuses.get(vaccine_type)
            if compliance != "compliant":
                vaccination_concerns.append(vaccine_type)

        recommendation_priority = [
            LabReviewRecommendation.PUBLIC_HEALTH_CLEARANCE,
            LabReviewRecommendation.TEMPORARILY_NOT_FIT,
            LabReviewRecommendation.REPEAT_TEST,
            LabReviewRecommendation.CLEARED,
        ]
        reviewed_lab_recommendations = [test.doctor_recommendation for test in lab_tests if test.doctor_recommendation]
        highest_lab_recommendation = next(
            (value for value in recommendation_priority if value in reviewed_lab_recommendations),
            "",
        )

        reasons = []
        status = "ready"
        suggested_decision = FitnessDecision.FIT

        if assessment.declaration_status != StepStatus.VALIDATED:
            status = "blocked"
            suggested_decision = FitnessDecision.REQUIRES_RECHECK
            reasons.append("Health declaration still needs doctor validation.")
        if assessment.physical_exam_status != StepStatus.COMPLETED:
            status = "blocked"
            suggested_decision = FitnessDecision.REQUIRES_RECHECK
            reasons.append("Physical examination is not complete.")
        if assessment.lab_status != StepStatus.REVIEWED:
            status = "blocked"
            suggested_decision = FitnessDecision.REQUIRES_LAB_TEST
            reasons.append("Required lab tests are not fully reviewed yet.")
        if assessment.vaccination_status != StepStatus.REVIEWED:
            status = "blocked"
            suggested_decision = FitnessDecision.REQUIRES_VACCINATION
            reasons.append("Vaccination review is still pending.")

        if status != "blocked":
            if highest_lab_recommendation == LabReviewRecommendation.PUBLIC_HEALTH_CLEARANCE:
                status = "warning"
                suggested_decision = FitnessDecision.REQUIRES_PUBLIC_HEALTH_CLEARANCE
                reasons.append("Lab review indicates public health clearance is required.")
            elif highest_lab_recommendation == LabReviewRecommendation.TEMPORARILY_NOT_FIT:
                status = "warning"
                suggested_decision = FitnessDecision.TEMPORARILY_NOT_FIT
                reasons.append("Reviewed lab results indicate temporary exclusion from food handling.")
            elif highest_lab_recommendation == LabReviewRecommendation.REPEAT_TEST or repeat_required_tests:
                status = "warning"
                suggested_decision = FitnessDecision.REQUIRES_LAB_TEST
                reasons.append("At least one lab result requires repeat testing before clearance.")
            elif vaccination_concerns:
                status = "warning"
                suggested_decision = FitnessDecision.REQUIRES_VACCINATION
                reasons.append("Vaccination records still show missing, expired, or incomplete protection.")
            elif declaration_risk or physical_exam_risk or flagged_lab_results:
                status = "warning"
                suggested_decision = FitnessDecision.REQUIRES_RECHECK
                if declaration_risk:
                    reasons.append("Declaration answers disclosed food-safety risk symptoms or exposures.")
                if physical_exam_risk:
                    reasons.append("Physical examination recorded clinical risk indicators.")
                if flagged_lab_results:
                    reasons.append("Reviewed lab results were flagged for follow-up.")
            else:
                reasons.append("Declaration, physical exam, lab review, and vaccination review are aligned for fit clearance.")

        return {
            "status": status,
            "suggested_decision": suggested_decision,
            "rationale": reasons[0] if reasons else "",
            "reasons": reasons,
            "signals": {
                "declaration_risk": declaration_risk,
                "physical_exam_risk": physical_exam_risk,
                "flagged_lab_results": len(flagged_lab_results),
                "repeat_required_tests": len(repeat_required_tests),
                "highest_lab_recommendation": highest_lab_recommendation or "none",
                "vaccination_concerns": vaccination_concerns,
                "declaration_status": assessment.declaration_status,
                "physical_exam_status": assessment.physical_exam_status,
                "lab_status": assessment.lab_status,
                "vaccination_status": assessment.vaccination_status,
            },
        }

    @classmethod
    def signature_hash(cls, *, assessment, doctor, final_decision):
        payload = f"{assessment.id}:{doctor.id}:{final_decision}:{timezone.now().isoformat()}:{settings.SECRET_KEY}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def report_type_for_decision(cls, final_decision):
        if final_decision == FitnessDecision.TEMPORARILY_NOT_FIT:
            return ReportType.TEMPORARILY_NOT_FIT
        if final_decision == FitnessDecision.RETURN_TO_WORK_ON_DATE:
            return ReportType.RETURN_TO_WORK
        return ReportType.MEDICAL_EXAMINATION

    @classmethod
    def generate_medical_report(cls, *, assessment, doctor):
        report_type = cls.report_type_for_decision(assessment.final_decision)
        summary = {
            "cards": {
                "food_handler": assessment.food_handler.full_name,
                "facility": assessment.facility.facility_name,
                "final_decision": assessment.final_decision,
                "return_to_work_date": str(assessment.return_to_work_date or ""),
                "signed_at": assessment.signed_at.isoformat() if assessment.signed_at else "",
            },
            "sections": {
                "assessment_completion_summary": [
                    {
                        "payment": assessment.payment_transaction.status if assessment.payment_transaction else "missing",
                        "declaration": assessment.declaration_status,
                        "physical_exam": assessment.physical_exam_status,
                        "lab": assessment.lab_status,
                        "vaccination": assessment.vaccination_status,
                    }
                ],
                "restricted_lab_summary": [
                    {"test": test.test_name or test.test_type, "status": test.status}
                    for test in assessment.lab_tests.all()
                ],
                "vaccination_records": [
                    {"vaccine": record.vaccine_name or record.vaccine_type, "status": record.status}
                    for record in assessment.vaccinations.all()
                ],
            },
        }
        report = GeneratedReport.objects.create(
            report_type=report_type,
            file_format=ReportFormat.JSON,
            filters={"assessment_id": str(assessment.id)},
            summary=summary,
            generated_by=doctor,
            status=GeneratedReportStatus.GENERATED,
        )
        log_action(
            action=AuditAction.CREATE,
            actor=doctor,
            target=report,
            metadata={"event": "medical_report_generated", "assessment_id": str(assessment.id)},
        )
        return report

    @classmethod
    def _assessment_report_role(cls, user):
        return getattr(user, "role", "")

    @classmethod
    def _can_access_assessment_report(cls, *, assessment, user):
        role = cls._assessment_report_role(user)
        if role == UserRole.SUPER_ADMIN:
            return True
        if role == UserRole.FEDERAL_ADMIN:
            return False
        if role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return assessment.facility.state_id == user.state_id
        if role == UserRole.FOOD_HANDLER:
            return assessment.food_handler.user_id == user.id
        if role == UserRole.EMPLOYER:
            return getattr(user, "employer", None) and assessment.employer_id == user.employer.id
        if role == UserRole.DOCTOR:
            return assessment.doctor_id == user.id or assessment.facility.organization_id == user.organization_id
        if role in {UserRole.FACILITY_ADMIN, UserRole.LAB_STAFF}:
            return assessment.facility.organization_id == user.organization_id
        return False

    @classmethod
    def ensure_assessment_report_access(cls, *, assessment, user, kind):
        if not cls._can_access_assessment_report(assessment=assessment, user=user):
            raise PermissionDenied("You cannot access reports for this assessment.")
        if kind != "return_to_work":
            return
        role = cls._assessment_report_role(user)
        if role in {UserRole.SUPER_ADMIN, UserRole.STATE_ADMIN, UserRole.INSPECTOR, UserRole.FOOD_HANDLER, UserRole.EMPLOYER}:
            return
        if role == UserRole.DOCTOR and assessment.facility.organization_id == user.organization_id:
            return
        if role in {UserRole.FACILITY_ADMIN, UserRole.LAB_STAFF}:
            from apps.facilities.services import FacilityTeamService

            if FacilityTeamService.has_permission(user=user, facility=assessment.facility, permission_key="unfit_reports.view"):
                return
        raise PermissionDenied("You do not have permission to access temporary unfit reports for this assessment.")

    @classmethod
    def report_type_for_assessment_kind(cls, kind, assessment=None):
        if kind == "summary":
            return ReportType.ASSESSMENT_COMPLETION
        if kind == "return_to_work":
            return ReportType.RETURN_TO_WORK
        if kind == "lab":
            return ReportType.RESTRICTED_LAB_SUMMARY
        if kind == "vaccination":
            return ReportType.VACCINATION_REVIEW
        if assessment and assessment.final_decision == FitnessDecision.TEMPORARILY_NOT_FIT:
            return ReportType.TEMPORARILY_NOT_FIT
        return ReportType.MEDICAL_EXAMINATION

    @classmethod
    def _operational_assessment_cards(cls, assessment):
        return {
            "assessment_id": str(assessment.id),
            "food_handler": assessment.food_handler.full_name,
            "facility": assessment.facility.facility_name,
            "status": assessment.status,
            "final_decision": assessment.final_decision,
            "certificate_submission_status": (
                getattr(getattr(assessment, "certificate_request", None), "status", None)
                or ("certificate_issued" if getattr(assessment, "certificate", None) else "not_submitted")
            ),
            "return_to_work_date": assessment.return_to_work_date.isoformat() if assessment.return_to_work_date else "",
            "signed_at": assessment.signed_at.isoformat() if assessment.signed_at else "",
        }

    @classmethod
    def _summary_payload(cls, assessment, user):
        role = cls._assessment_report_role(user)
        cards = cls._operational_assessment_cards(assessment)
        payload = {
            "cards": cards,
            "sections": {
                "workflow_status": [
                    {
                        "payment": assessment.payment_transaction.status if assessment.payment_transaction else "missing",
                        "declaration": assessment.declaration_status,
                        "physical_exam": assessment.physical_exam_status,
                        "lab": assessment.lab_status,
                        "vaccination": assessment.vaccination_status,
                        "decision": assessment.final_decision,
                    }
                ],
            },
        }
        if role in {UserRole.DOCTOR, UserRole.FACILITY_ADMIN, UserRole.STATE_ADMIN, UserRole.INSPECTOR, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            payload["sections"]["state_evidence"] = [
                {
                    "fit_signed": assessment.final_decision == FitnessDecision.FIT and bool(assessment.signed_at),
                    "doctor_assigned": bool(assessment.doctor_id),
                    "certificate_request": cards["certificate_submission_status"],
                    "certificate_issued": bool(getattr(assessment, "certificate", None)),
                }
            ]
        return payload

    @classmethod
    def _lab_payload(cls, assessment, user):
        if cls._assessment_report_role(user) not in {UserRole.DOCTOR, UserRole.LAB_STAFF, UserRole.FACILITY_ADMIN, UserRole.STATE_ADMIN, UserRole.INSPECTOR, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("You cannot access lab report details for this assessment.")
        include_notes = cls._assessment_report_role(user) in {UserRole.DOCTOR, UserRole.SUPER_ADMIN}
        return {
            "cards": cls._operational_assessment_cards(assessment),
            "sections": {
                "restricted_lab_summary": [
                    {
                        "test_type": test.test_type,
                        "test_name": test.test_name,
                        "status": test.status,
                        "result_value": test.result_value,
                        "doctor_recommendation": test.doctor_recommendation,
                        **({"result_notes": test.result_notes, "doctor_review_notes": test.doctor_review_notes} if include_notes else {}),
                    }
                    for test in assessment.lab_tests.all()
                ]
            },
        }

    @classmethod
    def _vaccination_payload(cls, assessment, user):
        if cls._assessment_report_role(user) not in {UserRole.DOCTOR, UserRole.FOOD_HANDLER, UserRole.FACILITY_ADMIN, UserRole.STATE_ADMIN, UserRole.INSPECTOR, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("You cannot access vaccination report details for this assessment.")
        include_notes = cls._assessment_report_role(user) in {UserRole.DOCTOR, UserRole.SUPER_ADMIN}
        return {
            "cards": cls._operational_assessment_cards(assessment),
            "sections": {
                "vaccination_review": [
                    {
                        "vaccine_type": record.vaccine_type,
                        "dose_number": record.dose_number,
                        "date_administered": record.date_administered.isoformat() if record.date_administered else "",
                        "expiry_date": record.expiry_date.isoformat() if record.expiry_date else "",
                        "next_dose_date": record.next_dose_date.isoformat() if record.next_dose_date else "",
                        "status": record.status,
                        "compliance_status": record.compliance_status,
                        **({"notes": record.notes} if include_notes else {}),
                    }
                    for record in assessment.vaccinations.all()
                ]
            },
        }

    @classmethod
    def _medical_payload(cls, assessment, user):
        role = cls._assessment_report_role(user)
        if role == UserRole.LAB_STAFF:
            return cls._lab_payload(assessment, user)
        if role in {UserRole.EMPLOYER, UserRole.INSPECTOR, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("You cannot access the full medical report for this assessment.")
        if role == UserRole.FACILITY_ADMIN:
            return cls._summary_payload(assessment, user)
        include_clinical = role in {UserRole.DOCTOR, UserRole.SUPER_ADMIN}
        payload = cls._summary_payload(assessment, user)
        payload["sections"]["medical_decision"] = [
            {
                "final_decision": assessment.final_decision,
                "return_to_work_date": assessment.return_to_work_date.isoformat() if assessment.return_to_work_date else "",
                **({"doctor_notes": assessment.doctor_notes} if include_clinical else {}),
            }
        ]
        payload["sections"].update(cls._lab_payload(assessment, user)["sections"])
        payload["sections"].update(cls._vaccination_payload(assessment, user)["sections"])
        return payload

    @classmethod
    def _return_to_work_payload(cls, assessment, user):
        role = cls._assessment_report_role(user)
        if role == UserRole.EMPLOYER:
            return {
                "cards": {
                    "assessment_id": str(assessment.id),
                    "food_handler": assessment.food_handler.full_name,
                    "operational_status": assessment.food_handler.current_status,
                    "return_to_work_date": assessment.return_to_work_date.isoformat() if assessment.return_to_work_date else "",
                    "final_decision": assessment.final_decision,
                },
                "sections": {},
            }
        return {
            "cards": cls._operational_assessment_cards(assessment),
            "sections": {
                "return_to_work": [
                    {
                        "final_decision": assessment.final_decision,
                        "return_to_work_date": assessment.return_to_work_date.isoformat() if assessment.return_to_work_date else "",
                        "open_clearance_cases": assessment.food_handler.illness_reports.exclude(clearance_status__in=["cleared", "rejected"]).count(),
                    }
                ]
            },
        }

    @classmethod
    def assessment_report_payload(cls, *, assessment, user, kind):
        cls.ensure_assessment_report_access(assessment=assessment, user=user, kind=kind)
        builders = {
            "summary": cls._summary_payload,
            "medical": cls._medical_payload,
            "return_to_work": cls._return_to_work_payload,
            "lab": cls._lab_payload,
            "vaccination": cls._vaccination_payload,
        }
        builder = builders.get(kind)
        if not builder:
            raise NotFound("Unknown assessment report type.")
        payload = builder(assessment, user)
        payload["generated_at"] = timezone.now().isoformat()
        payload["report_kind"] = kind
        return payload

    @classmethod
    def ensure_assessment_report(cls, *, assessment, user, kind):
        payload = cls.assessment_report_payload(assessment=assessment, user=user, kind=kind)
        report = GeneratedReport.objects.create(
            report_type=cls.report_type_for_assessment_kind(kind, assessment),
            file_format=ReportFormat.JSON,
            filters={"assessment_id": str(assessment.id), "kind": kind},
            summary=payload,
            generated_by=user,
            status=GeneratedReportStatus.GENERATED,
        )
        return report

    @classmethod
    @transaction.atomic
    def save_fitness_decision_draft(cls, *, assessment, doctor, final_decision, doctor_notes="", return_to_work_date=None):
        ensure_approved_facility(assessment.facility)
        ensure_assigned_doctor_for_assessment(doctor, assessment)
        if assessment.signed_at:
            raise ValidationError("Final decision has already been signed and cannot be changed.")
        if final_decision == FitnessDecision.RETURN_TO_WORK_ON_DATE and not return_to_work_date:
            raise ValidationError("Return-to-work date is required for this decision.")
        assessment.doctor = doctor
        assessment.decision_draft = final_decision
        assessment.decision_draft_return_to_work_date = return_to_work_date
        assessment.decision_draft_notes = doctor_notes
        assessment.decision_draft_saved_at = timezone.now()
        assessment.save(
            update_fields=[
                "doctor",
                "decision_draft",
                "decision_draft_return_to_work_date",
                "decision_draft_notes",
                "decision_draft_saved_at",
                "updated_at",
            ]
        )
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=assessment,
            metadata={"event": "fitness_decision_draft_saved", "decision": final_decision},
        )
        return assessment

    @classmethod
    def _sync_handler_status_for_decision(cls, *, assessment):
        if assessment.final_decision == FitnessDecision.FIT:
            assessment.food_handler.current_status = FoodHandlerStatus.CERTIFICATION_PENDING
        elif assessment.final_decision == FitnessDecision.TEMPORARILY_NOT_FIT:
            assessment.food_handler.current_status = FoodHandlerStatus.TEMPORARILY_NOT_FIT
        elif assessment.final_decision in {FitnessDecision.NOT_FIT, FitnessDecision.REQUIRES_PUBLIC_HEALTH_CLEARANCE}:
            assessment.food_handler.current_status = FoodHandlerStatus.EXCLUDED
        elif assessment.final_decision in {
            FitnessDecision.REQUIRES_VACCINATION,
            FitnessDecision.REQUIRES_LAB_TEST,
            FitnessDecision.REQUIRES_RECHECK,
            FitnessDecision.REQUIRES_TREATMENT,
            FitnessDecision.RETURN_TO_WORK_ON_DATE,
        }:
            assessment.food_handler.current_status = FoodHandlerStatus.TEMPORARILY_EXCLUDED
        assessment.food_handler.save(update_fields=["current_status", "updated_at"])

    @classmethod
    def _ensure_return_to_work_case(cls, *, assessment, doctor):
        if assessment.final_decision not in {
            FitnessDecision.TEMPORARILY_NOT_FIT,
            FitnessDecision.REQUIRES_PUBLIC_HEALTH_CLEARANCE,
            FitnessDecision.RETURN_TO_WORK_ON_DATE,
        }:
            return None
        report = IllnessReport.objects.filter(
            food_handler=assessment.food_handler,
            clearance_status__in=[ClearanceStatus.PENDING, ClearanceStatus.UNDER_REVIEW, ClearanceStatus.CLEARANCE_REQUIRED],
        ).first()
        if not report:
            report = IllnessReport.objects.create(
                food_handler=assessment.food_handler,
                employer=assessment.employer or assessment.food_handler.employer,
                reported_by=doctor,
                symptoms={"source": "medical_assessment_decision", "assessment_id": str(assessment.id)},
                suspected_condition=SuspectedCondition.OTHER,
                symptom_start_date=timezone.localdate(),
                exclusion_start_date=timezone.localdate(),
                earliest_return_date=assessment.return_to_work_date,
                clearance_required=assessment.final_decision == FitnessDecision.REQUIRES_PUBLIC_HEALTH_CLEARANCE,
                clearance_status=(
                    ClearanceStatus.CLEARANCE_REQUIRED
                    if assessment.final_decision == FitnessDecision.REQUIRES_PUBLIC_HEALTH_CLEARANCE
                    else ClearanceStatus.PENDING
                ),
                reviewed_by_doctor=doctor,
                reviewed_at=timezone.now(),
                notes=assessment.doctor_notes,
            )
        else:
            report.reviewed_by_doctor = doctor
            report.reviewed_at = timezone.now()
            report.earliest_return_date = assessment.return_to_work_date or report.earliest_return_date
            report.notes = assessment.doctor_notes or report.notes
            if assessment.final_decision == FitnessDecision.REQUIRES_PUBLIC_HEALTH_CLEARANCE:
                report.clearance_required = True
                report.clearance_status = ClearanceStatus.CLEARANCE_REQUIRED
            report.save(update_fields=["reviewed_by_doctor", "reviewed_at", "earliest_return_date", "notes", "clearance_required", "clearance_status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=report,
            metadata={"event": "return_to_work_case_linked", "assessment_id": str(assessment.id), "decision": assessment.final_decision},
        )
        return report

    @classmethod
    @transaction.atomic
    def set_fitness_decision(cls, *, assessment, doctor, final_decision, doctor_notes="", return_to_work_date=None, digital_signature_confirmation=False):
        cls.validate_final_decision_ready(assessment, doctor)
        if not digital_signature_confirmation:
            raise ValidationError("Digital sign-off confirmation is required.")
        if final_decision == FitnessDecision.RETURN_TO_WORK_ON_DATE and not return_to_work_date:
            raise ValidationError("Return-to-work date is required for this decision.")
        assessment.doctor = doctor
        assessment.signed_by = doctor
        assessment.final_decision = final_decision
        assessment.return_to_work_date = return_to_work_date
        assessment.doctor_notes = doctor_notes
        assessment.signed_at = timezone.now()
        assessment.digital_signature_hash = cls.signature_hash(assessment=assessment, doctor=doctor, final_decision=final_decision)
        if final_decision == FitnessDecision.FIT:
            assessment.status = AssessmentStatus.FIT
        elif final_decision == FitnessDecision.TEMPORARILY_NOT_FIT:
            assessment.status = AssessmentStatus.TEMPORARILY_NOT_FIT
        elif final_decision == FitnessDecision.NOT_FIT:
            assessment.status = AssessmentStatus.NOT_FIT
        else:
            assessment.status = AssessmentStatus.DOCTOR_DECISION_PENDING
        assessment.save(
            update_fields=[
                "doctor",
                "signed_by",
                "final_decision",
                "return_to_work_date",
                "doctor_notes",
                "signed_at",
                "digital_signature_hash",
                "status",
                "updated_at",
            ]
        )
        cls._sync_handler_status_for_decision(assessment=assessment)
        cls._ensure_return_to_work_case(assessment=assessment, doctor=doctor)
        cls.generate_medical_report(assessment=assessment, doctor=doctor)
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=doctor,
            target=assessment,
            metadata={"event": "fitness_decision", "decision": final_decision},
        )
        return assessment
