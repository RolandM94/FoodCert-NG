import hashlib
import re
from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation

from django.conf import settings
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
    AssessmentFormScope,
    AssessmentFormSection,
    AssessmentFormStatus,
    AssessmentFormTemplate,
    AssessmentFormType,
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
from apps.payments.models import PaymentStatus
from apps.policy.models import NationalPolicyConfig
from apps.reports.models import GeneratedReport, GeneratedReportStatus, ReportFormat, ReportType


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
        if template.form_type not in cls.FACILITY_ALLOWED_FORM_TYPES:
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
        template.status = AssessmentFormStatus.PENDING_APPROVAL
        template.review_requested_at = timezone.now()
        template.reviewed_by = None
        template.reviewed_at = None
        template.review_comment = ""
        template.save(update_fields=["status", "review_requested_at", "reviewed_by", "reviewed_at", "review_comment", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=template, metadata={"event": "assessment_form_submitted_for_approval"})
        return template

    @classmethod
    @transaction.atomic
    def approve(cls, *, template, actor):
        cls.ensure_can_approve(template=template, actor=actor)
        if template.status != AssessmentFormStatus.PENDING_APPROVAL:
            raise ValidationError("Only pending assessment form templates can be approved.")
        if template.scope == AssessmentFormScope.FACILITY:
            AssessmentFormValidationService.validate_template(template)
        template.status = AssessmentFormStatus.APPROVED
        template.approved_by = actor
        template.approved_at = timezone.now()
        template.reviewed_by = actor
        template.reviewed_at = timezone.now()
        template.review_comment = ""
        template.save(update_fields=["status", "approved_by", "approved_at", "reviewed_by", "reviewed_at", "review_comment", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=template, metadata={"event": "assessment_form_approved"})
        AssessmentFormNotificationService.notify_template_review(template=template, event="approved")
        return template

    @classmethod
    @transaction.atomic
    def reject(cls, *, template, actor, reason=""):
        cls.ensure_can_approve(template=template, actor=actor)
        if template.status != AssessmentFormStatus.PENDING_APPROVAL:
            raise ValidationError("Only pending assessment form templates can be rejected.")
        template.status = AssessmentFormStatus.REJECTED
        template.approved_by = None
        template.approved_at = None
        template.reviewed_by = actor
        template.reviewed_at = timezone.now()
        template.review_comment = reason
        template.save(update_fields=["status", "approved_by", "approved_at", "reviewed_by", "reviewed_at", "review_comment", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=template, metadata={"event": "assessment_form_rejected", "reason": reason})
        AssessmentFormNotificationService.notify_template_review(template=template, event="rejected", message_suffix=reason)
        return template

    @classmethod
    @transaction.atomic
    def request_changes(cls, *, template, actor, reason=""):
        cls.ensure_can_approve(template=template, actor=actor)
        if template.status != AssessmentFormStatus.PENDING_APPROVAL:
            raise ValidationError("Only pending assessment form templates can have changes requested.")
        template.status = AssessmentFormStatus.CHANGES_REQUESTED
        template.approved_by = None
        template.approved_at = None
        template.reviewed_by = actor
        template.reviewed_at = timezone.now()
        template.review_comment = reason
        template.save(update_fields=["status", "approved_by", "approved_at", "reviewed_by", "reviewed_at", "review_comment", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=template, metadata={"event": "assessment_form_changes_requested", "reason": reason})
        AssessmentFormNotificationService.notify_template_review(template=template, event="changes_requested", message_suffix=reason)
        return template

    @classmethod
    @transaction.atomic
    def publish(cls, *, template, actor):
        cls.ensure_can_approve(template=template, actor=actor)
        if template.status != AssessmentFormStatus.APPROVED:
            raise ValidationError("Only approved assessment form templates can be published.")
        AssessmentFormValidationService.validate_template(template)
        template.status = AssessmentFormStatus.PUBLISHED
        template.published_at = timezone.now()
        template.save(update_fields=["status", "published_at", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=template, metadata={"event": "assessment_form_published"})
        if template.parent_template_id:
            AssessmentFormNotificationService.notify_template_review(template=template, event="new_version_published")
        return template

    @classmethod
    @transaction.atomic
    def activate(cls, *, template, actor):
        cls.ensure_can_approve(template=template, actor=actor)
        if template.status != AssessmentFormStatus.PUBLISHED:
            raise ValidationError("Only published assessment form templates can be activated.")
        template.status = AssessmentFormStatus.ACTIVE
        template.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=template, metadata={"event": "assessment_form_activated"})
        return template

    @classmethod
    @transaction.atomic
    def retire(cls, *, template, actor):
        cls.ensure_can_approve(template=template, actor=actor)
        if template.status not in {AssessmentFormStatus.PUBLISHED, AssessmentFormStatus.ACTIVE}:
            raise ValidationError("Only published or active assessment form templates can be retired.")
        template.status = AssessmentFormStatus.RETIRED
        template.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=template, metadata={"event": "assessment_form_retired"})
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
            version=version,
            status=AssessmentFormStatus.DRAFT,
            is_mandatory=template.is_mandatory,
            requires_approval=template.requires_approval,
            effective_from=template.effective_from,
            effective_to=template.effective_to,
            created_by=actor,
            parent_template=root,
        )
        for section in template.sections.all():
            new_section = AssessmentFormSection.objects.create(
                template=duplicate,
                key=section.key,
                title=section.title,
                description=section.description,
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
                        question_type=question.question_type,
                        required=question.required,
                        options=question.options,
                        validation_rules=question.validation_rules,
                        conditional_logic=question.conditional_logic,
                        risk_flag_rules=question.risk_flag_rules,
                        privacy_classification=question.privacy_classification,
                        respondent_role=question.respondent_role,
                        sort_order=question.sort_order,
                        is_active=question.is_active,
                    )
                    for question in section.questions.all()
                ]
            )
        log_action(action=AuditAction.CREATE, actor=actor, target=duplicate, metadata={"event": "assessment_form_duplicated", "source_template_id": str(template.id)})
        return duplicate


class AssessmentFormNotificationService:
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
        cls.ensure_assessment_report_access(assessment=assessment, user=user)
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
        return bool(assessment and assessment.payment_transaction and assessment.payment_transaction.status == PaymentStatus.SUCCESS)

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
        appointment.save(update_fields=["status", "notes", "updated_at"])
        assessment = cls._appointment_assessment(appointment)
        if assessment:
            assessment.status = AssessmentStatus.APPOINTMENT_BOOKED
            assessment.assessment_date = appointment.appointment_date
            assessment.save(update_fields=["status", "assessment_date", "updated_at"])
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
    def assign_appointment_doctor(cls, *, appointment, doctor, actor):
        ensure_facility_admin_for_facility(actor, appointment.facility)
        ensure_doctor_for_facility(doctor, appointment.facility)
        appointment.doctor = doctor
        appointment.save(update_fields=["doctor", "updated_at"])
        assessment = cls._appointment_assessment(appointment)
        if assessment:
            assessment.doctor = doctor
            assessment.save(update_fields=["doctor", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=appointment,
            metadata={"event": "appointment_doctor_assigned", "doctor_id": str(doctor.id)},
        )
        return appointment

    @classmethod
    @transaction.atomic
    def assign_assessment_doctor(cls, *, assessment, doctor, actor):
        ensure_facility_admin_for_facility(actor, assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        assessment.doctor = doctor
        assessment.save(update_fields=["doctor", "updated_at"])
        if assessment.appointment_id:
            assessment.appointment.doctor = doctor
            assessment.appointment.save(update_fields=["doctor", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=assessment,
            metadata={"event": "assessment_doctor_assigned", "doctor_id": str(doctor.id)},
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
        return assessment

    @classmethod
    @transaction.atomic
    def save_declaration_draft(cls, *, assessment, data, actor):
        cls.ensure_declaration_owner(assessment, actor)
        declaration = cls._get_or_create_declaration(assessment)
        if declaration.is_locked or declaration.validated_at:
            raise ValidationError("This declaration has been validated and is locked.")
        if declaration.submitted_at and not declaration.clarification_requested_at:
            raise ValidationError("Submitted declarations are read-only unless a doctor requests clarification.")
        if declaration.submitted_at and declaration.clarification_requested_at:
            declaration.version += 1
            declaration.submitted_at = None
            declaration.validated_by_doctor = None
            declaration.validated_at = None
        for field, value in cls._declaration_payload(data).items():
            setattr(declaration, field, value)
        declaration.risk_flag = declaration.calculate_risk_flag()
        declaration.is_locked = False
        declaration.save(
            update_fields=[
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
                "risk_flag",
                "version",
                "is_locked",
                "submitted_at",
                "validated_by_doctor",
                "validated_at",
                "updated_at",
            ]
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
        declaration = cls.save_declaration_draft(assessment=assessment, data=data, actor=actor)
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
            target=assessment,
            metadata={"event": "declaration_submitted", "version": declaration.version, "risk_flag": declaration.risk_flag},
        )
        return declaration

    @classmethod
    @transaction.atomic
    def validate_declaration(cls, *, declaration, doctor):
        assessment = declaration.assessment
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        if not declaration.submitted_at:
            raise ValidationError("Only submitted declarations can be validated.")
        if declaration.validated_at:
            raise ValidationError("This declaration has already been validated.")
        declaration.validated_by_doctor = doctor
        declaration.validated_at = timezone.now()
        declaration.is_locked = True
        declaration.save(update_fields=["validated_by_doctor", "validated_at", "is_locked", "updated_at"])
        assessment.doctor = doctor
        assessment.declaration_status = StepStatus.VALIDATED
        assessment.status = AssessmentStatus.DECLARATION_VALIDATED
        assessment.save(update_fields=["doctor", "declaration_status", "status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=doctor, target=assessment, metadata={"event": "declaration_validated", "version": declaration.version})
        return declaration

    @classmethod
    @transaction.atomic
    def request_declaration_clarification(cls, *, declaration, doctor, reason):
        assessment = declaration.assessment
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        if declaration.validated_at:
            raise ValidationError("Validated declarations are locked and cannot be sent back for changes.")
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
            target=assessment,
            metadata={"event": "declaration_clarification_requested"},
        )
        return declaration

    @classmethod
    @transaction.atomic
    def reopen_declaration(cls, *, declaration, doctor, reason):
        assessment = declaration.assessment
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        if declaration.is_locked or declaration.validated_at:
            raise ValidationError("Validated declarations are locked and cannot be reopened.")
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
            target=assessment,
            metadata={"event": "declaration_reopened", "version": declaration.version, "reason": reason},
        )
        return declaration

    @classmethod
    @transaction.atomic
    def save_physical_exam_draft(cls, *, assessment, doctor, data):
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
        if assessment.doctor_id and assessment.doctor_id != doctor.id:
            raise PermissionDenied("Doctors can only edit physical exams for assigned assessments.")
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
        return assessment.food_handler.nin_verifications.filter(
            status__in=[NINVerificationStatus.VERIFIED, NINVerificationStatus.OVERRIDE_APPROVED]
        ).exists()

    @classmethod
    def validate_final_decision_ready(cls, assessment, doctor):
        ensure_approved_facility(assessment.facility)
        ensure_doctor_for_facility(doctor, assessment.facility)
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
    def ensure_assessment_report_access(cls, *, assessment, user):
        if not cls._can_access_assessment_report(assessment=assessment, user=user):
            raise PermissionDenied("You cannot access reports for this assessment.")

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
        cls.ensure_assessment_report_access(assessment=assessment, user=user)
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
        ensure_doctor_for_facility(doctor, assessment.facility)
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
