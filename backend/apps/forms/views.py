import csv
import io
import json
import zipfile
from uuid import UUID

from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import views, viewsets, status, response
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.forms.permissions import (
    CanCreateAssignment,
    CanCreateTemplate,
    CanExportResponses,
    CanPublishTemplate,
    CanReviewResponse,
    filter_sensitive_fields,
    filter_response_json_by_sensitivity,
    get_user_form_permissions,
    user_can_view_sensitivity,
    user_has_form_permission,
)
from apps.forms.models import (
    AssignmentStatus,
    FormAssignment,
    FormRecipient,
    FormRecipientStatus,
    FormResponse,
    FormResponseActivityLog,
    FormResponseAttachment,
    FormSyncStatus,
    OfflineSyncQueue,
    FormTemplate,
    FormTemplateStatus,
    FormTemplateVersion,
    ResponseStatus,
)
from apps.forms.serializers import (
    FormAssignmentSerializer,
    FormRecipientSerializer,
    FormResponseSerializer,
    FormResponseActivityLogSerializer,
    FormResponseAttachmentSerializer,
    FormTemplateSerializer,
    FormTemplateVersionSerializer,
    OfflineSyncQueueSerializer,
)
from apps.forms.exporting import attachment_export_row, response_export_row
from apps.forms.validation import validate_form_response
from apps.inspections.models import Inspection


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_response_activity(form_response, actor, action, details=None, request=None):
    FormResponseActivityLog.objects.create(
        response=form_response,
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        details_json=details or {},
        ip_address=_client_ip(request) if request else None,
        device_id=getattr(form_response, "device_id", "") or "",
    )


def _valid_uuid(value):
    try:
        UUID(str(value))
    except (TypeError, ValueError):
        return None
    return str(value)


def _user_org_id(user):
    return str(user.organization_id) if getattr(user, "organization_id", None) else ""


def _user_unit_id(user):
    return str(user.unit_id) if getattr(user, "unit_id", None) else ""


def user_assignment_filter(user):
    org_id = _user_org_id(user)
    unit_id = _user_unit_id(user)
    filters = Q(assigned_to_type="user", assigned_to_id=str(user.id)) | Q(responses__respondent_user=user)
    if org_id:
        filters |= Q(assigned_to_type="organization", assigned_to_id=org_id)
        filters |= Q(context_id=org_id)
    if unit_id:
        filters |= Q(assigned_to_type="unit", assigned_to_id=unit_id)
        filters |= Q(context_id=unit_id)
    return filters


def scoped_templates_for_user(user, queryset):
    if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
        return queryset
    if user.role == UserRole.STATE_ADMIN:
        if getattr(user, "organization_id", None):
            return queryset.filter(owner_organization_id=user.organization_id)
        if getattr(user, "state_id", None):
            return queryset.filter(owner_organization__state_id=user.state_id)
    return queryset.filter(owner_organization_id=getattr(user, "organization_id", None))


def scoped_assignments_for_user(user, queryset):
    if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
        return queryset
    if user.role == UserRole.STATE_ADMIN:
        if getattr(user, "organization_id", None):
            return queryset.filter(template__owner_organization_id=user.organization_id)
        if getattr(user, "state_id", None):
            return queryset.filter(template__owner_organization__state_id=user.state_id)
    return queryset.filter(user_assignment_filter(user)).distinct()


def scoped_responses_for_user(user, queryset):
    if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
        return queryset
    if user.role == UserRole.STATE_ADMIN:
        if getattr(user, "organization_id", None):
            return queryset.filter(template__owner_organization_id=user.organization_id)
        if getattr(user, "state_id", None):
            return queryset.filter(template__owner_organization__state_id=user.state_id)
    return queryset.filter(Q(respondent_user=user) | Q(assignment__in=scoped_assignments_for_user(user, FormAssignment.objects.all()))).distinct()


def serialize_form_response(form_response, user):
    data = FormResponseSerializer(form_response).data
    schema = form_response.template_version.schema_json if form_response and form_response.template_version_id else {}
    data["template_schema"] = filter_sensitive_fields(data.get("template_schema") or schema, user)
    data["response_json"] = filter_response_json_by_sensitivity(schema, data.get("response_json") or {}, user)
    return data


def serialize_form_responses(form_responses, user):
    return [serialize_form_response(item, user) for item in form_responses]


def export_safe_response_json(schema, response_json):
    if not schema or not response_json:
        return response_json
    allowed = set()
    repeat_allowed = {}
    for question in _schema_questions(schema):
        sensitivity = question.get("sensitivity", "public")
        if sensitivity not in {"public", "internal"}:
            continue
        if question.get("repeat_group"):
            repeat_allowed.setdefault(question["repeat_group"], set()).add(question.get("key", "").split(".", 1)[-1])
            allowed.add(question["repeat_group"])
        else:
            allowed.add(question.get("key"))
    filtered = {}
    for key, value in (response_json or {}).items():
        if key not in allowed:
            continue
        if key in repeat_allowed and isinstance(value, list):
            nested_allowed = repeat_allowed[key]
            filtered[key] = [
                {nested_key: nested_value for nested_key, nested_value in item.items() if nested_key in nested_allowed}
                for item in value
                if isinstance(item, dict)
            ]
        else:
            filtered[key] = value
    return filtered


def export_safe_schema(schema):
    if not schema or not schema.get("sections"):
        return schema
    safe_sections = []
    for section in schema.get("sections", []) or []:
        safe_questions = []
        for question in section.get("questions", []) or []:
            if question.get("sensitivity", "public") not in {"public", "internal"}:
                continue
            if question.get("type") == "repeat_group":
                nested = [
                    item
                    for item in question.get("questions", []) or []
                    if item.get("sensitivity", "public") in {"public", "internal"}
                ]
                safe_questions.append({**question, "questions": nested})
            else:
                safe_questions.append(question)
        safe_sections.append({**section, "questions": safe_questions})
    return {**schema, "sections": safe_sections}


def export_visible_attachment_key(schema, question_key):
    if not schema or not schema.get("sections"):
        return True
    for question in _schema_questions(schema):
        key = question.get("key", "")
        raw_key = key.split(".", 1)[-1] if question.get("repeat_group") else key
        if question_key in {key, raw_key}:
            return question.get("sensitivity", "public") in {"public", "internal"}
    return False


def audit_form_event(request, *, action, target, event, metadata=None):
    log_action(
        action=action,
        actor=request.user,
        target=target,
        request=request,
        metadata={"event": event, **(metadata or {})},
    )


def mark_assignment_overdue(assignment):
    if not assignment.due_date or assignment.due_date >= timezone.now() or assignment.status in {AssignmentStatus.CANCELLED, AssignmentStatus.CLOSED}:
        return assignment
    pending_recipients = assignment.recipients.exclude(
        status__in=[FormRecipientStatus.SUBMITTED, FormRecipientStatus.REVIEWED, FormRecipientStatus.CANCELLED]
    )
    pending_recipients.update(status=FormRecipientStatus.OVERDUE)
    assignment.responses.exclude(
        status__in=[ResponseStatus.SUBMITTED, ResponseStatus.REVIEWED, ResponseStatus.APPROVED, ResponseStatus.REJECTED, ResponseStatus.CANCELLED]
    ).update(status=ResponseStatus.OVERDUE)
    if assignment.status not in {AssignmentStatus.REVIEWED, AssignmentStatus.SUBMITTED}:
        assignment.status = AssignmentStatus.OVERDUE
        assignment.save(update_fields=["status", "updated_at"])
    return assignment


def _schema_questions(schema):
    questions = []
    for section in (schema or {}).get("sections", []) or []:
        for question in section.get("questions", []) or []:
            if question.get("type") == "repeat_group":
                for nested in question.get("questions", []) or []:
                    questions.append({**nested, "key": f"{question.get('key')}.{nested.get('key')}", "repeat_group": question.get("key")})
            else:
                questions.append(question)
    return questions


def _answer_for_question(response_json, question):
    key = question.get("key")
    if question.get("repeat_group"):
        group_items = response_json.get(question["repeat_group"], [])
        nested_key = key.split(".", 1)[1] if "." in key else key
        if isinstance(group_items, list):
            return [item.get(nested_key) for item in group_items if isinstance(item, dict) and nested_key in item]
        return []
    return response_json.get(key)


def _analytics_value_key(value):
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value[:120]
    return None


def _structured_response_analytics(responses_qs, user, limit=12):
    media_types = {"image_upload", "file_upload", "video_upload", "audio_upload", "signature"}
    free_text_types = {"long_text", "short_text", "email", "phone", "url", "hidden", "platform_field"}
    summaries = {}
    for form_response in responses_qs.select_related("template", "template_version")[:500]:
        schema = form_response.template_version.schema_json if form_response.template_version_id else {}
        response_json = form_response.response_json or {}
        for question in _schema_questions(schema):
            sensitivity = question.get("sensitivity", "public")
            if not user_can_view_sensitivity(user, sensitivity):
                continue
            if sensitivity not in {"public", "internal"}:
                continue
            question_type = question.get("type", "")
            if question_type in media_types or question_type in free_text_types:
                continue
            key = f"{form_response.template_id}:{question.get('key')}"
            summary = summaries.setdefault(
                key,
                {
                    "template_id": str(form_response.template_id),
                    "template_title": form_response.template.title,
                    "question_key": question.get("key"),
                    "question_label": question.get("label") or question.get("key"),
                    "question_type": question_type,
                    "answered": 0,
                    "numeric_total": 0,
                    "numeric_count": 0,
                    "values": {},
                },
            )
            raw_value = _answer_for_question(response_json, question)
            values = raw_value if isinstance(raw_value, list) and question_type != "multiple_choice" else [raw_value]
            for value in values:
                if isinstance(value, list):
                    for item in value:
                        value_key = _analytics_value_key(item)
                        if value_key:
                            summary["values"][value_key] = summary["values"].get(value_key, 0) + 1
                    if value:
                        summary["answered"] += 1
                    continue
                value_key = _analytics_value_key(value)
                if not value_key:
                    continue
                summary["answered"] += 1
                summary["values"][value_key] = summary["values"].get(value_key, 0) + 1
                if isinstance(value, (int, float)):
                    summary["numeric_total"] += value
                    summary["numeric_count"] += 1
    rows = []
    for summary in summaries.values():
        top_values = sorted(summary.pop("values").items(), key=lambda item: item[1], reverse=True)[:8]
        numeric_count = summary.pop("numeric_count")
        numeric_total = summary.pop("numeric_total")
        rows.append({
            **summary,
            "top_values": [{"value": value, "count": count} for value, count in top_values],
            "average": round(numeric_total / numeric_count, 1) if numeric_count else None,
        })
    return sorted(rows, key=lambda row: row["answered"], reverse=True)[:limit]


class FormTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = FormTemplateSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = FormTemplate.objects.select_related("owner_organization", "created_by")
        purpose = self.request.query_params.get("purpose")
        status_param = self.request.query_params.get("status")
        if purpose:
            qs = qs.filter(purpose=purpose)
        if status_param:
            qs = qs.filter(status=status_param)
        qs = scoped_templates_for_user(user, qs)
        return qs.order_by("-updated_at")

    def perform_create(self, serializer):
        if not user_has_form_permission(self.request.user, "forms.template.create"):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to create form templates.")
        owner = serializer.validated_data.get("owner_organization") or getattr(self.request.user, "organization", None)
        template = serializer.save(created_by=self.request.user, owner_organization=owner)
        audit_form_event(self.request, action=AuditAction.CREATE, target=template, event="form_template_created")

    @action(detail=True, methods=["post"], url_path="save-draft")
    def save_draft(self, request, pk=None):
        template = self.get_object()
        if template.status != FormTemplateStatus.DRAFT:
            return response.Response({"error": "Only draft templates can be edited."}, status=400)
        schema_json = request.data.get("schema_json") or request.data.get("schema") or {"sections": []}
        logic_json = request.data.get("logic_json") or request.data.get("conditional_logic_json") or {}
        version, _ = FormTemplateVersion.objects.update_or_create(
            template=template,
            version_number=template.current_version,
            defaults={
                "schema_json": schema_json,
                "logic_json": logic_json,
                "conditional_logic_json": request.data.get("conditional_logic_json", logic_json),
                "scoring_json": request.data.get("scoring_json", {}),
                "settings_json": request.data.get("settings_json", template.settings_json),
                "status": "draft",
            },
        )
        if "settings_json" in request.data:
            template.settings_json = request.data["settings_json"]
            template.save(update_fields=["settings_json", "updated_at"])
        audit_form_event(request, action=AuditAction.UPDATE, target=template, event="form_template_draft_saved")
        return response.Response(FormTemplateVersionSerializer(version).data)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        if not user_has_form_permission(request.user, "forms.template.publish"):
            return response.Response({"error": "You do not have permission to publish templates."}, status=403)
        template = self.get_object()
        if template.status != FormTemplateStatus.DRAFT:
            return response.Response({"error": "Only draft templates can be published."}, status=400)
        schema_json = request.data.get("schema_json") or request.data.get("schema") or {"sections": []}
        logic_json = request.data.get("logic_json") or request.data.get("conditional_logic_json") or {}
        version = FormTemplateVersion.objects.create(
            template=template,
            version_number=template.current_version,
            schema_json=schema_json,
            logic_json=logic_json,
            conditional_logic_json=request.data.get("conditional_logic_json", logic_json),
            scoring_json=request.data.get("scoring_json", {}),
            settings_json=request.data.get("settings_json", template.settings_json),
            published_by=request.user,
            status=FormTemplateStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        template.status = FormTemplateStatus.PUBLISHED
        template.save(update_fields=["status", "updated_at"])
        audit_form_event(request, action=AuditAction.WORKFLOW_TRANSITION, target=template, event="form_template_published", metadata={"version_id": str(version.id)})
        return response.Response(FormTemplateSerializer(template).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        template = self.get_object()
        template.status = FormTemplateStatus.ARCHIVED
        template.archived_at = timezone.now()
        template.save(update_fields=["status", "archived_at", "updated_at"])
        audit_form_event(request, action=AuditAction.WORKFLOW_TRANSITION, target=template, event="form_template_archived")
        return response.Response(FormTemplateSerializer(template).data)

    @action(detail=True, methods=["post"])
    def new_version(self, request, pk=None):
        template = self.get_object()
        template.current_version += 1
        template.status = FormTemplateStatus.DRAFT
        template.save(update_fields=["current_version", "status", "updated_at"])
        audit_form_event(request, action=AuditAction.UPDATE, target=template, event="form_template_new_version")
        return response.Response(FormTemplateSerializer(template).data)

    @action(detail=True, methods=["get"])
    def versions(self, request, pk=None):
        template = self.get_object()
        versions = template.versions.order_by("-version_number")
        return response.Response(FormTemplateVersionSerializer(versions, many=True).data)

    @action(detail=True, methods=["get"])
    def preview(self, request, pk=None):
        template = self.get_object()
        latest = template.versions.order_by("-version_number").first()
        data = FormTemplateSerializer(template).data
        data["schema"] = filter_sensitive_fields(latest.schema_json if latest else {}, request.user)
        data["logic"] = latest.logic_json if latest else {}
        data["settings"] = latest.settings_json if latest else template.settings_json
        return response.Response(data)


class FormAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = FormAssignmentSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = FormAssignment.objects.select_related("template", "assigned_by").prefetch_related("recipients", "responses")
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        qs = scoped_assignments_for_user(user, qs)
        for assignment in qs.filter(due_date__lt=timezone.now()).exclude(status__in=[AssignmentStatus.CANCELLED, AssignmentStatus.CLOSED]):
            mark_assignment_overdue(assignment)
        return qs.order_by("-created_at")

    def perform_create(self, serializer):
        if not user_has_form_permission(self.request.user, "forms.assignment.create"):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to create form assignments.")
        assignment = serializer.save(assigned_by=self.request.user)
        if assignment.assigned_to_type and assignment.assigned_to_id:
            organization_id = _valid_uuid(assignment.assigned_to_id) if assignment.assigned_to_type == "organization" else None
            FormRecipient.objects.get_or_create(
                assignment=assignment,
                recipient_type=assignment.assigned_to_type,
                recipient_id=assignment.assigned_to_id,
                defaults={
                    "organization_id": organization_id,
                    "role_id": assignment.recipient_role,
                },
            )
        audit_form_event(self.request, action=AuditAction.CREATE, target=assignment, event="form_assignment_created")

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        assignment = self.get_object()
        assignment.status = AssignmentStatus.CANCELLED
        assignment.closed_at = timezone.now()
        assignment.recipients.exclude(status__in=["submitted", "reviewed"]).update(status="cancelled")
        assignment.save(update_fields=["status", "closed_at", "updated_at"])
        audit_form_event(request, action=AuditAction.WORKFLOW_TRANSITION, target=assignment, event="form_assignment_cancelled")
        return response.Response(FormAssignmentSerializer(assignment).data)

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        assignment = mark_assignment_overdue(self.get_object())
        data = FormAssignmentSerializer(assignment).data
        data["responses"] = serialize_form_responses(
            assignment.responses.select_related("template_version", "respondent_user", "reviewed_by").order_by("-updated_at"),
            request.user,
        )
        data["recipients"] = FormRecipientSerializer(assignment.recipients.select_related("organization"), many=True).data
        return response.Response(data)

    @action(detail=True, methods=["post"], url_path="send-reminder")
    def send_reminder(self, request, pk=None):
        assignment = mark_assignment_overdue(self.get_object())
        recipients = assignment.recipients.exclude(
            status__in=[FormRecipientStatus.SUBMITTED, FormRecipientStatus.REVIEWED, FormRecipientStatus.CANCELLED]
        )
        updated = recipients.update(notified_at=timezone.now())
        return response.Response({
            "assignment": FormAssignmentSerializer(assignment).data,
            "reminded_count": updated,
            "message": f"Reminder queued for {updated} pending recipient(s).",
        })

    @action(detail=True, methods=["get"])
    def recipients(self, request, pk=None):
        assignment = self.get_object()
        recipients = assignment.recipients.select_related("organization").order_by("recipient_type", "recipient_id")
        return response.Response(FormRecipientSerializer(recipients, many=True).data)

    @action(detail=True, methods=["get"])
    def responses(self, request, pk=None):
        assignment = self.get_object()
        responses = assignment.responses.select_related("assignment", "template", "respondent_user", "reviewed_by")
        return response.Response(serialize_form_responses(responses, request.user))


class FormResponseViewSet(viewsets.ModelViewSet):
    serializer_class = FormResponseSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = FormResponse.objects.select_related(
            "assignment", "template", "respondent_user", "reviewed_by"
        )
        status_param = self.request.query_params.get("status")
        assignment_id = self.request.query_params.get("assignment")
        if status_param:
            qs = qs.filter(status=status_param)
        if assignment_id:
            qs = qs.filter(assignment_id=assignment_id)
        qs = scoped_responses_for_user(user, qs)
        return qs.order_by("-created_at")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return response.Response(serialize_form_responses(queryset, request.user))

    def retrieve(self, request, *args, **kwargs):
        return response.Response(serialize_form_response(self.get_object(), request.user))

    def perform_create(self, serializer):
        if not user_has_form_permission(self.request.user, "forms.response.submit"):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to create form responses.")
        form_response = serializer.save(
            respondent_user=serializer.validated_data.get("respondent_user") or self.request.user,
            sync_status=serializer.validated_data.get("sync_status") or FormSyncStatus.ONLINE,
            started_at=timezone.now(),
            last_saved_at=timezone.now(),
        )
        log_response_activity(form_response, self.request.user, "created", request=self.request)
        audit_form_event(self.request, action=AuditAction.CREATE, target=form_response, event="form_response_created")

    @action(detail=True, methods=["post"])
    def save_draft(self, request, pk=None):
        r = self.get_object()
        r.response_json = request.data.get("response_json", r.response_json)
        r.status = ResponseStatus.DRAFT
        r.last_saved_at = timezone.now()
        r.sync_status = request.data.get("sync_status", r.sync_status)
        r.device_id = request.data.get("device_id", r.device_id)
        r.save(update_fields=["response_json", "status", "last_saved_at", "sync_status", "device_id", "updated_at"])
        if r.recipient_id and r.recipient.status == FormRecipientStatus.NOT_STARTED:
            r.recipient.status = FormRecipientStatus.IN_PROGRESS
            r.recipient.started_at = r.recipient.started_at or timezone.now()
            r.recipient.save(update_fields=["status", "started_at", "updated_at"])
        log_response_activity(r, request.user, "draft_saved", request=request)
        audit_form_event(request, action=AuditAction.UPDATE, target=r, event="form_response_draft_saved")
        return response.Response(serialize_form_response(r, request.user))

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        r = self.get_object()
        next_response_json = request.data.get("response_json", r.response_json)
        validation_errors = validate_form_response(
            r.template_version.schema_json if r.template_version_id else {},
            next_response_json,
            r.template_version.logic_json if r.template_version_id else {},
        )
        if validation_errors:
            return response.Response({"error": "Validation failed.", "errors": validation_errors}, status=400)
        r.status = ResponseStatus.SUBMITTED
        r.submitted_at = timezone.now()
        r.last_saved_at = r.submitted_at
        r.response_json = next_response_json
        r.score = request.data.get("score", r.score)
        r.sync_status = request.data.get("sync_status", FormSyncStatus.ONLINE)
        r.save(update_fields=["status", "submitted_at", "last_saved_at", "response_json", "score", "sync_status", "updated_at"])
        if r.recipient_id:
            r.recipient.status = "submitted"
            r.recipient.submitted_at = r.submitted_at
            r.recipient.save(update_fields=["status", "submitted_at", "updated_at"])
        log_response_activity(r, request.user, "submitted", request=request)
        audit_form_event(request, action=AuditAction.WORKFLOW_TRANSITION, target=r, event="form_response_submitted")
        return response.Response(serialize_form_response(r, request.user))

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        if not user_has_form_permission(request.user, "forms.response.review"):
            return response.Response({"error": "You do not have permission to review responses."}, status=403)
        r = self.get_object()
        r.status = ResponseStatus.REVIEWED
        r.reviewed_by = request.user
        r.reviewed_at = timezone.now()
        r.review_notes = request.data.get("review_notes", "")
        r.save(update_fields=["status", "reviewed_by", "reviewed_at", "review_notes", "updated_at"])
        if r.recipient_id:
            r.recipient.status = "reviewed"
            r.recipient.reviewed_at = r.reviewed_at
            r.recipient.save(update_fields=["status", "reviewed_at", "updated_at"])
        log_response_activity(r, request.user, "reviewed", {"review_notes": r.review_notes}, request=request)
        audit_form_event(request, action=AuditAction.WORKFLOW_TRANSITION, target=r, event="form_response_reviewed")
        return response.Response(serialize_form_response(r, request.user))

    @action(detail=True, methods=["post"])
    def return_response(self, request, pk=None):
        if not user_has_form_permission(request.user, "forms.response.return"):
            return response.Response({"error": "You do not have permission to return responses."}, status=403)
        r = self.get_object()
        r.status = ResponseStatus.RETURNED
        r.returned_reason = request.data.get("reason", "")
        r.save(update_fields=["status", "returned_reason", "updated_at"])
        if r.recipient_id:
            r.recipient.status = "returned"
            r.recipient.save(update_fields=["status", "updated_at"])
        log_response_activity(r, request.user, "returned", {"reason": r.returned_reason}, request=request)
        audit_form_event(request, action=AuditAction.WORKFLOW_TRANSITION, target=r, event="form_response_returned")
        return response.Response(serialize_form_response(r, request.user))

    @action(detail=True, methods=["get"])
    def activity(self, request, pk=None):
        r = self.get_object()
        activity = r.activity_logs.select_related("actor")
        return response.Response(FormResponseActivityLogSerializer(activity, many=True).data)

    @action(detail=True, methods=["get", "post"])
    def attachments(self, request, pk=None):
        r = self.get_object()
        if request.method.lower() == "get":
            attachments = r.attachments.select_related("uploaded_by")
            return response.Response(FormResponseAttachmentSerializer(attachments, many=True).data)

        data = request.data.copy()
        data["response"] = str(r.id)
        serializer = FormResponseAttachmentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        attachment = serializer.save(uploaded_by=request.user)
        log_response_activity(r, request.user, "attachment_uploaded", {"question_key": attachment.question_key}, request=request)
        audit_form_event(request, action=AuditAction.UPDATE, target=r, event="form_response_attachment_uploaded", metadata={"question_key": attachment.question_key})
        return response.Response(FormResponseAttachmentSerializer(attachment).data, status=status.HTTP_201_CREATED)


class OfflineAssignmentsView(views.APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        assignments = FormAssignment.objects.select_related("template", "template_version", "assigned_by").filter(allow_offline=True)
        assignments = scoped_assignments_for_user(request.user, assignments)
        return response.Response(FormAssignmentSerializer(assignments.order_by("-created_at"), many=True).data)


class OfflineAssignmentPackageView(views.APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request, assignment_id):
        assignment = scoped_assignments_for_user(
            request.user,
            FormAssignment.objects.select_related("template", "template_version", "assigned_by").filter(id=assignment_id),
        ).first()
        if not assignment:
            return response.Response({"error": "Assignment not found."}, status=404)
        if not assignment.allow_offline:
            return response.Response({"error": "This assignment is not available offline."}, status=400)
        form_response = assignment.responses.filter(respondent_user=request.user).select_related("template", "template_version", "assignment").first()
        payload = {
            "assignment": FormAssignmentSerializer(assignment).data,
            "template": FormTemplateSerializer(assignment.template).data,
            "template_version": {
                **FormTemplateVersionSerializer(assignment.template_version).data,
                "schema_json": filter_sensitive_fields(assignment.template_version.schema_json, request.user),
            } if assignment.template_version_id else None,
            "response": serialize_form_response(form_response, request.user) if form_response else None,
            "downloaded_at": timezone.now().isoformat(),
            "sync_statuses": [choice[0] for choice in FormSyncStatus.choices],
        }
        audit_form_event(request, action=AuditAction.SECURITY_EVENT, target=assignment, event="form_offline_package_downloaded")
        return response.Response(payload)


class OfflineSyncView(views.APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def post(self, request):
        local_response_id = request.data.get("local_response_id")
        operation_type = request.data.get("operation_type", "submit_response")
        payload_json = request.data.get("payload_json") or {}
        if not local_response_id:
            return response.Response({"error": "local_response_id is required."}, status=400)
        if operation_type not in {"save_draft", "submit_response"}:
            return response.Response({"error": "Unsupported sync operation."}, status=400)

        assignment = None
        if payload_json.get("assignment_id"):
            assignment = scoped_assignments_for_user(
                request.user,
                FormAssignment.objects.filter(id=payload_json.get("assignment_id")),
            ).first()
        form_response = None
        if payload_json.get("response_id"):
            form_response = scoped_responses_for_user(
                request.user,
                FormResponse.objects.select_related("template_version", "assignment").filter(id=payload_json.get("response_id")),
            ).first()
            assignment = assignment or form_response.assignment if form_response else assignment

        sync_job = OfflineSyncQueue.objects.create(
            user=request.user,
            assignment=assignment,
            response=form_response,
            local_response_id=local_response_id,
            operation_type=operation_type,
            payload_json=payload_json,
            media_payload_ref=request.data.get("media_payload_ref", ""),
            status=FormSyncStatus.SYNCING,
        )
        result = self._process_sync(request, sync_job, form_response, payload_json, operation_type)
        return response.Response(result, status=200 if result["status"] in {FormSyncStatus.SYNCED, FormSyncStatus.SYNC_PENDING} else 409)

    def _process_sync(self, request, sync_job, form_response, payload_json, operation_type):
        if not form_response:
            sync_job.mark_attempt("Response could not be found for this offline payload.")
            return {"status": sync_job.status, "sync_job": OfflineSyncQueueSerializer(sync_job).data, "error": sync_job.error_message}
        if form_response.status in {ResponseStatus.SUBMITTED, ResponseStatus.REVIEWED, ResponseStatus.APPROVED, ResponseStatus.REJECTED}:
            sync_job.status = FormSyncStatus.CONFLICT
            sync_job.error_message = "This response was already submitted or reviewed on another device."
            sync_job.mark_attempt(sync_job.error_message)
            sync_job.status = FormSyncStatus.CONFLICT
            sync_job.save(update_fields=["status", "updated_at"])
            return {"status": sync_job.status, "sync_job": OfflineSyncQueueSerializer(sync_job).data, "error": sync_job.error_message}

        response_json = payload_json.get("response_json") or {}
        if operation_type == "submit_response":
            validation_errors = validate_form_response(
                form_response.template_version.schema_json if form_response.template_version_id else {},
                response_json,
                form_response.template_version.logic_json if form_response.template_version_id else {},
            )
            if validation_errors:
                sync_job.mark_attempt("Offline response failed validation.")
                return {
                    "status": sync_job.status,
                    "sync_job": OfflineSyncQueueSerializer(sync_job).data,
                    "errors": validation_errors,
                }
            form_response.status = ResponseStatus.SUBMITTED
            form_response.submitted_at = timezone.now()
            log_action = "offline_submitted"
        else:
            form_response.status = ResponseStatus.DRAFT
            log_action = "offline_draft_synced"

        form_response.response_json = response_json
        form_response.sync_status = FormSyncStatus.SYNCED
        form_response.device_id = payload_json.get("device_id", form_response.device_id)
        form_response.offline_created_at = payload_json.get("offline_created_at") or form_response.offline_created_at
        form_response.last_saved_at = timezone.now()
        form_response.save(update_fields=["response_json", "status", "sync_status", "device_id", "offline_created_at", "last_saved_at", "submitted_at", "updated_at"])
        sync_job.response = form_response
        sync_job.status = FormSyncStatus.SYNCED
        sync_job.mark_attempt()
        log_response_activity(form_response, request.user, log_action, {"local_response_id": sync_job.local_response_id}, request=request)
        audit_form_event(request, action=AuditAction.WORKFLOW_TRANSITION, target=form_response, event=log_action, metadata={"local_response_id": sync_job.local_response_id})
        return {"status": sync_job.status, "sync_job": OfflineSyncQueueSerializer(sync_job).data, "response": serialize_form_response(form_response, request.user)}


class OfflineSyncStatusView(views.APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request, sync_job_id):
        sync_job = OfflineSyncQueue.objects.select_related("assignment", "response").get(id=sync_job_id, user=request.user)
        return response.Response(OfflineSyncQueueSerializer(sync_job).data)


class FormResponseExportView(views.APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        if not user_has_form_permission(request.user, "forms.export.create"):
            return response.Response({"error": "You do not have permission to export responses."}, status=403)
        export_format = request.query_params.get("format", "csv").lower()
        responses = self._filtered_responses(request)
        for item in responses:
            if item.template_version_id and item.template_version.schema_json:
                item.response_json = export_safe_response_json(item.template_version.schema_json, item.response_json)
                item.template_version.schema_json = export_safe_schema(item.template_version.schema_json)
        rows = [response_export_row(item) for item in responses]
        self._audit_export(request, responses, f"responses_{export_format}")
        if export_format == "json":
            return self._json_response(rows)
        if export_format == "pdf":
            return self._pdf_summary_response(rows)
        return self._csv_response(rows)

    def _filtered_responses(self, request):
        qs = FormResponse.objects.select_related("assignment", "template", "template_version", "respondent_user", "reviewed_by")
        user = request.user
        qs = scoped_responses_for_user(user, qs)
        filters = {
            "assignment": "assignment_id",
            "template": "template_id",
            "template_version": "template_version_id",
            "status": "status",
            "sync_status": "sync_status",
            "risk_rating": "risk_rating",
            "purpose": "assignment__purpose",
            "context_type": "context_type",
            "context_id": "context_id",
        }
        for query_key, lookup in filters.items():
            value = request.query_params.get(query_key)
            if value:
                qs = qs.filter(**{lookup: value})
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        return list(qs.order_by("-created_at"))

    def _audit_export(self, request, responses, export_type):
        log_action(
            action=AuditAction.SECURITY_EVENT,
            actor=request.user,
            request=request,
            metadata={
                "event": "form_export_created",
                "export_type": export_type,
                "response_count": len(responses),
                "filters": dict(request.query_params),
            },
        )
        for item in responses:
            log_response_activity(item, request.user, "exported", {"export_type": export_type}, request=request)

    def _csv_response(self, rows):
        output = io.StringIO()
        fieldnames = sorted({key for row in rows for key in row.keys()})
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        res = HttpResponse(output.getvalue(), content_type="text/csv")
        res["Content-Disposition"] = 'attachment; filename="form-responses.csv"'
        return res

    def _json_response(self, rows):
        res = HttpResponse(json.dumps(rows, default=str, indent=2), content_type="application/json")
        res["Content-Disposition"] = 'attachment; filename="form-responses.json"'
        return res

    def _pdf_summary_response(self, rows):
        lines = ["FoodCert NG Form Response Export Summary", "", f"Responses: {len(rows)}", ""]
        for row in rows[:100]:
            lines.append(f"{row.get('template_title')} | {row.get('respondent_email')} | {row.get('status')} | {row.get('submitted_at')}")
        res = HttpResponse("\n".join(lines), content_type="application/pdf")
        res["Content-Disposition"] = 'attachment; filename="form-responses-summary.pdf"'
        return res


class FormAttachmentExportView(FormResponseExportView):
    def get(self, request):
        if not user_has_form_permission(request.user, "forms.export.create"):
            return response.Response({"error": "You do not have permission to export attachments."}, status=403)
        responses = self._filtered_responses(request)
        attachments = FormResponseAttachment.objects.select_related("response", "response__template_version").filter(response__in=responses).order_by("response_id", "question_key", "created_at")
        self._audit_export(request, responses, "attachments_zip")
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            index_rows = []
            for attachment in attachments:
                schema = attachment.response.template_version.schema_json if attachment.response.template_version_id else {}
                if not export_visible_attachment_key(schema, attachment.question_key):
                    continue
                row = attachment_export_row(attachment)
                index_rows.append(row)
                if attachment.file:
                    filename = attachment.file_name or attachment.file.name.rsplit("/", 1)[-1]
                    archive.writestr(f"attachments/{attachment.response_id}/{filename}", attachment.file.read())
            index_output = io.StringIO()
            fieldnames = sorted({key for row in index_rows for key in row.keys()}) or ["attachment_id"]
            writer = csv.DictWriter(index_output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(index_rows)
            archive.writestr("attachments-index.csv", index_output.getvalue())
        buffer.seek(0)
        res = HttpResponse(buffer.getvalue(), content_type="application/zip")
        res["Content-Disposition"] = 'attachment; filename="form-attachments.zip"'
        return res


class PortalAssignedFormsView(views.APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    portal_context_types: tuple = ()
    portal_purposes: tuple = ()
    allowed_roles: tuple = ()

    def _ensure_portal_access(self, user):
        if self.allowed_roles and user.role not in self.allowed_roles:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You cannot access these assigned forms.")

    def _recipient_filter(self, user):
        user_filter = Q(responses__respondent_user=user)
        org_id = str(user.organization_id) if user.organization_id else ""
        if org_id:
            user_filter |= Q(assigned_to_type="organization", assigned_to_id=org_id)
        user_filter |= Q(assigned_to_type="user", assigned_to_id=str(user.id))
        if user.unit_id:
            user_filter |= Q(assigned_to_type="unit", assigned_to_id=str(user.unit_id))
        if self.portal_context_types:
            context_ids = [str(user.id)]
            if org_id:
                context_ids.append(org_id)
            if user.unit_id:
                context_ids.append(str(user.unit_id))
            user_filter |= Q(context_type__in=self.portal_context_types, context_id__in=context_ids)
        return user_filter

    def _assignment_queryset(self, user):
        self._ensure_portal_access(user)
        qs = FormAssignment.objects.select_related(
            "template", "template_version", "assigned_by"
        ).prefetch_related("recipients", "responses")
        qs = qs.filter(self._recipient_filter(user))
        if self.portal_purposes:
            qs = qs.filter(purpose__in=self.portal_purposes)
        return qs.distinct().exclude(
            status__in=[AssignmentStatus.CANCELLED]
        ).order_by("-created_at")

    def _response_for_user(self, assignment, user):
        return assignment.responses.filter(respondent_user=user).order_by("-created_at").first()

    def _serialize_assignment(self, assignment, user, include_schema=False):
        data = FormAssignmentSerializer(assignment).data
        form_response = self._response_for_user(assignment, user)
        data["response"] = serialize_form_response(form_response, user) if form_response else None
        data["response_id"] = str(form_response.id) if form_response else None
        data["response_status"] = form_response.status if form_response else "not_started"
        data["response_history"] = serialize_form_responses(
            assignment.responses.filter(respondent_user=user).order_by("-created_at"),
            user,
        )
        if include_schema and assignment.template_version_id:
            data["template_schema"] = filter_sensitive_fields(assignment.template_version.schema_json, user)
            data["template_logic"] = assignment.template_version.logic_json
            data["template_settings"] = assignment.template_version.settings_json
        return data

    def get(self, request):
        assignments = self._assignment_queryset(request.user)
        status_filter = request.query_params.get("status")
        if status_filter:
            if status_filter == "pending":
                assignments = assignments.exclude(responses__respondent_user=request.user)
            elif status_filter == "in_progress":
                assignments = assignments.filter(responses__respondent_user=request.user, responses__status__in=[ResponseStatus.DRAFT, ResponseStatus.IN_PROGRESS, ResponseStatus.SYNC_PENDING])
            elif status_filter == "submitted":
                assignments = assignments.filter(responses__respondent_user=request.user, responses__status__in=[ResponseStatus.SUBMITTED, ResponseStatus.REVIEWED, ResponseStatus.APPROVED])
            elif status_filter == "returned":
                assignments = assignments.filter(responses__respondent_user=request.user, responses__status=ResponseStatus.RETURNED)
            else:
                assignments = assignments.filter(status=status_filter)
        purpose_filter = request.query_params.get("purpose")
        if purpose_filter:
            assignments = assignments.filter(purpose=purpose_filter)
        return response.Response([
            self._serialize_assignment(a, request.user) for a in assignments[:100]
        ])


class PortalAssignedFormDetailView(views.APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    portal_context_types: tuple = ()
    portal_purposes: tuple = ()
    allowed_roles: tuple = ()

    def _portal_view(self):
        view = PortalAssignedFormsView()
        view.portal_context_types = self.portal_context_types
        view.portal_purposes = self.portal_purposes
        view.allowed_roles = self.allowed_roles
        return view

    def _get_assignment(self, user, assignment_id):
        return self._portal_view()._assignment_queryset(user).filter(id=assignment_id).first()

    def get(self, request, assignment_id):
        assignment = self._get_assignment(request.user, assignment_id)
        if not assignment:
            return response.Response({"error": "Assignment not found."}, status=404)
        return response.Response(self._portal_view()._serialize_assignment(assignment, request.user, include_schema=True))


class PortalAssignedFormResponseView(views.APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    portal_context_types: tuple = ()
    portal_purposes: tuple = ()
    allowed_roles: tuple = ()

    def _portal_view(self):
        view = PortalAssignedFormsView()
        view.portal_context_types = self.portal_context_types
        view.portal_purposes = self.portal_purposes
        view.allowed_roles = self.allowed_roles
        return view

    def _get_assignment(self, user, assignment_id):
        return self._portal_view()._assignment_queryset(user).filter(id=assignment_id).first()

    def post(self, request, assignment_id):
        assignment = self._get_assignment(request.user, assignment_id)
        if not assignment:
            return response.Response({"error": "Assignment not found."}, status=404)
        existing = assignment.responses.filter(respondent_user=request.user).first()
        if existing and not assignment.allow_multiple_submissions:
            return response.Response(serialize_form_response(existing, request.user))
        recipient_filter = Q(recipient_id=str(request.user.id))
        if request.user.organization_id:
            recipient_filter |= Q(recipient_id=str(request.user.organization_id))
        if request.user.unit_id:
            recipient_filter |= Q(recipient_id=str(request.user.unit_id))
        recipient = assignment.recipients.filter(recipient_filter).first()
        if not recipient:
            recipient, _ = FormRecipient.objects.get_or_create(
                assignment=assignment,
                recipient_type="user",
                recipient_id=str(request.user.id),
                defaults={
                    "organization_id": _valid_uuid(request.user.organization_id) if request.user.organization_id else None,
                    "role_id": request.user.role,
                },
            )
        form_response = FormResponse.objects.create(
            assignment=assignment,
            template=assignment.template,
            template_version=assignment.template_version,
            recipient=recipient,
            respondent_user=request.user,
            respondent_organization_id=request.user.organization_id,
            context_type=assignment.context_type,
            context_id=assignment.context_id,
            response_json=request.data.get("response_json", {}),
            sync_status=FormSyncStatus.ONLINE,
            started_at=timezone.now(),
            last_saved_at=timezone.now(),
        )
        if recipient.status == FormRecipientStatus.NOT_STARTED:
            recipient.status = FormRecipientStatus.IN_PROGRESS
            recipient.started_at = timezone.now()
            recipient.save(update_fields=["status", "started_at", "updated_at"])
        log_response_activity(form_response, request.user, "created", request=request)
        audit_form_event(request, action=AuditAction.CREATE, target=form_response, event="portal_form_response_created")
        return response.Response(serialize_form_response(form_response, request.user), status=status.HTTP_201_CREATED)


class FormsPermissionsView(views.APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        permissions = get_user_form_permissions(request.user)
        return response.Response({
            "permissions": permissions,
            "role": request.user.role,
        })


class FormsAnalyticsView(views.APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        user = request.user
        if user.role not in {"super_admin", "federal_admin", "state_admin"}:
            return response.Response({"error": "Only administrators can access form analytics."}, status=403)

        responses_qs = FormResponse.objects.select_related("template", "template_version", "assignment", "respondent_organization")
        assignments_qs = FormAssignment.objects.select_related("template", "template__owner_organization")
        templates_qs = FormTemplate.objects.select_related("owner_organization")

        if user.role not in {"super_admin", "federal_admin"}:
            org_id = getattr(user, "organization_id", None)
            if org_id:
                templates_qs = templates_qs.filter(owner_organization_id=org_id)
                assignments_qs = assignments_qs.filter(template__owner_organization_id=org_id)
                responses_qs = responses_qs.filter(template__owner_organization_id=org_id)
            elif getattr(user, "state_id", None):
                templates_qs = templates_qs.filter(owner_organization__state_id=user.state_id)
                assignments_qs = assignments_qs.filter(template__owner_organization__state_id=user.state_id)
                responses_qs = responses_qs.filter(template__owner_organization__state_id=user.state_id)

        template_filter = request.query_params.get("template")
        assignment_filter = request.query_params.get("assignment")
        purpose_filter = request.query_params.get("purpose")
        status_filter = request.query_params.get("status")
        context_type_filter = request.query_params.get("context_type")
        primary_module_filter = request.query_params.get("primary_module")
        module_context_filter = request.query_params.get("module_context")
        organization_filter = request.query_params.get("organization")
        state_filter = request.query_params.get("state")
        lga_filter = request.query_params.get("lga")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        if template_filter:
            assignments_qs = assignments_qs.filter(template_id=template_filter)
            responses_qs = responses_qs.filter(template_id=template_filter)
        if assignment_filter:
            assignments_qs = assignments_qs.filter(id=assignment_filter)
            responses_qs = responses_qs.filter(assignment_id=assignment_filter)
        if purpose_filter:
            assignments_qs = assignments_qs.filter(purpose=purpose_filter)
            responses_qs = responses_qs.filter(assignment__purpose=purpose_filter)
        if status_filter:
            responses_qs = responses_qs.filter(status=status_filter)
        if context_type_filter:
            assignments_qs = assignments_qs.filter(context_type=context_type_filter)
            responses_qs = responses_qs.filter(context_type=context_type_filter)
        if primary_module_filter:
            templates_qs = templates_qs.filter(primary_module=primary_module_filter)
            assignments_qs = assignments_qs.filter(template__primary_module=primary_module_filter)
            responses_qs = responses_qs.filter(template__primary_module=primary_module_filter)
        if module_context_filter:
            templates_qs = templates_qs.filter(module_context=module_context_filter)
            assignments_qs = assignments_qs.filter(template__module_context=module_context_filter)
            responses_qs = responses_qs.filter(template__module_context=module_context_filter)
        if organization_filter:
            assignments_qs = assignments_qs.filter(
                Q(template__owner_organization_id=organization_filter)
                | Q(assigned_to_id=organization_filter)
                | Q(responses__respondent_organization_id=organization_filter)
            ).distinct()
            responses_qs = responses_qs.filter(
                Q(template__owner_organization_id=organization_filter)
                | Q(respondent_organization_id=organization_filter)
                | Q(assignment__assigned_to_id=organization_filter)
            )
        if state_filter:
            templates_qs = templates_qs.filter(owner_organization__state_id=state_filter)
            assignments_qs = assignments_qs.filter(
                Q(template__owner_organization__state_id=state_filter)
                | Q(responses__respondent_organization__state_id=state_filter)
            ).distinct()
            responses_qs = responses_qs.filter(
                Q(template__owner_organization__state_id=state_filter)
                | Q(respondent_organization__state_id=state_filter)
            )
        if lga_filter:
            templates_qs = templates_qs.filter(owner_organization__lga_id=lga_filter)
            assignments_qs = assignments_qs.filter(
                Q(template__owner_organization__lga_id=lga_filter)
                | Q(responses__respondent_organization__lga_id=lga_filter)
            ).distinct()
            responses_qs = responses_qs.filter(
                Q(template__owner_organization__lga_id=lga_filter)
                | Q(respondent_organization__lga_id=lga_filter)
            )
        if date_from:
            responses_qs = responses_qs.filter(created_at__date__gte=date_from)
        if date_to:
            responses_qs = responses_qs.filter(created_at__date__lte=date_to)

        from django.db.models import Avg, Count
        from django.db.models.functions import TruncDate

        total_templates = templates_qs.count()
        total_assignments = assignments_qs.count()
        total_responses = responses_qs.count()
        submitted_count = responses_qs.filter(status__in=[ResponseStatus.SUBMITTED, ResponseStatus.REVIEWED, ResponseStatus.APPROVED]).count()
        completion_rate = round((submitted_count / total_responses) * 100, 1) if total_responses else 0
        avg_score = responses_qs.filter(score__isnull=False).aggregate(avg=Avg("score"))["avg"]

        status_breakdown = list(
            responses_qs.values("status").annotate(count=Count("id")).order_by("-count")
        )

        purpose_breakdown = list(
            assignments_qs.values("purpose").annotate(
                count=Count("id"),
                response_count=Count("responses"),
            ).order_by("-count")
        )

        submissions_over_time = list(
            responses_qs.filter(
                submitted_at__isnull=False
            ).annotate(
                date=TruncDate("submitted_at")
            ).values("date").annotate(
                count=Count("id")
            ).order_by("date")[:90]
        )

        score_ranges = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        for score_val in responses_qs.filter(score__isnull=False).values_list("score", flat=True):
            if score_val <= 20:
                score_ranges["0-20"] += 1
            elif score_val <= 40:
                score_ranges["21-40"] += 1
            elif score_val <= 60:
                score_ranges["41-60"] += 1
            elif score_val <= 80:
                score_ranges["61-80"] += 1
            else:
                score_ranges["81-100"] += 1
        score_distribution = [{"range": k, "count": v} for k, v in score_ranges.items()]

        risk_breakdown = list(
            responses_qs.exclude(risk_rating="").values("risk_rating").annotate(count=Count("id")).order_by("-count")
        )

        template_stats = list(
            responses_qs.values("template__title", "template_id").annotate(
                total=Count("id"),
                submitted=Count("id", filter=Q(status__in=["submitted", "reviewed", "approved"])),
                avg_score=Avg("score"),
            ).order_by("-total")[:20]
        )
        assignment_stats = []
        for assignment in assignments_qs.prefetch_related("recipients", "responses").order_by("-created_at")[:20]:
            response_total = assignment.responses.count()
            submitted_total = assignment.responses.filter(status__in=[ResponseStatus.SUBMITTED, ResponseStatus.REVIEWED, ResponseStatus.APPROVED]).count()
            recipient_total = assignment.recipients.count() or 1
            assignment_stats.append({
                "assignment_id": str(assignment.id),
                "assignment_title": assignment.title,
                "template_title": assignment.template.title,
                "purpose": assignment.purpose,
                "context_type": assignment.context_type,
                "recipient_count": assignment.recipients.count(),
                "response_count": response_total,
                "submitted_count": submitted_total,
                "response_rate": round((response_total / recipient_total) * 100, 1) if recipient_total else 0,
                "completion_rate": round((submitted_total / recipient_total) * 100, 1) if recipient_total else 0,
            })

        structured_response_analytics = _structured_response_analytics(responses_qs, user)
        inspection_response_ids = [
            _valid_uuid(context_id)
            for context_id in responses_qs.filter(
                Q(context_type="inspection") | Q(assignment__purpose="inspection_checklist")
            ).values_list("context_id", flat=True)
        ]
        inspection_response_ids = [item for item in inspection_response_ids if item]
        inspections_qs = Inspection.objects.filter(id__in=inspection_response_ids)
        inspection_average_score = inspections_qs.filter(compliance_score__isnull=False).aggregate(avg=Avg("compliance_score"))["avg"]
        inspection_status_breakdown = list(inspections_qs.values("status").annotate(count=Count("id")).order_by("-count"))
        inspection_enforcement_breakdown = list(inspections_qs.values("enforcement_action").annotate(count=Count("id")).order_by("-count"))
        organization_breakdown = list(
            responses_qs.values("respondent_organization_id", "respondent_organization__name").annotate(count=Count("id")).order_by("-count")[:20]
        )
        location_breakdown = list(
            responses_qs.values("respondent_organization__state_id", "respondent_organization__state__name").annotate(count=Count("id")).order_by("-count")[:20]
        )

        return response.Response({
            "summary": {
                "total_templates": total_templates,
                "total_assignments": total_assignments,
                "total_responses": total_responses,
                "submitted_responses": submitted_count,
                "completion_rate": completion_rate,
                "average_score": round(avg_score, 1) if avg_score is not None else None,
            },
            "status_breakdown": status_breakdown,
            "purpose_breakdown": purpose_breakdown,
            "submissions_over_time": [
                {"date": row["date"].isoformat() if row["date"] else None, "count": row["count"]}
                for row in submissions_over_time
            ],
            "score_distribution": score_distribution,
            "risk_breakdown": risk_breakdown,
            "assignment_stats": assignment_stats,
            "structured_response_analytics": structured_response_analytics,
            "inspection_analytics": {
                "inspection_count": inspections_qs.count(),
                "average_score": round(inspection_average_score, 1) if inspection_average_score is not None else None,
                "status_breakdown": inspection_status_breakdown,
                "enforcement_breakdown": inspection_enforcement_breakdown,
            },
            "organization_breakdown": [
                {
                    "organization_id": str(row["respondent_organization_id"]) if row["respondent_organization_id"] else None,
                    "organization_name": row["respondent_organization__name"] or "Unknown",
                    "count": row["count"],
                }
                for row in organization_breakdown
            ],
            "location_breakdown": [
                {
                    "state_id": str(row["respondent_organization__state_id"]) if row["respondent_organization__state_id"] else None,
                    "state_name": row["respondent_organization__state__name"] or "Unknown",
                    "count": row["count"],
                }
                for row in location_breakdown
            ],
            "template_stats": [
                {
                    "template_title": row["template__title"],
                    "template_id": str(row["template_id"]),
                    "total": row["total"],
                    "submitted": row["submitted"],
                    "completion_rate": round((row["submitted"] / row["total"]) * 100, 1) if row["total"] else 0,
                    "average_score": round(row["avg_score"], 1) if row["avg_score"] is not None else None,
                }
                for row in template_stats
            ],
            "filters": {
                "template": template_filter,
                "assignment": assignment_filter,
                "purpose": purpose_filter,
                "status": status_filter,
                "context_type": context_type_filter,
                "primary_module": primary_module_filter,
                "module_context": module_context_filter,
                "organization": organization_filter,
                "state": state_filter,
                "lga": lga_filter,
                "date_from": date_from,
                "date_to": date_to,
            },
        })


class EmployerAssignedFormsView(PortalAssignedFormsView):
    allowed_roles = (UserRole.EMPLOYER,)
    portal_context_types = ("employer", "employer_compliance", "branch")
    portal_purposes = (
        "employer_data_collection",
        "employer_compliance",
        "general_data_collection",
        "incident_report",
        "training_feedback",
    )


class EmployerAssignedFormDetailView(PortalAssignedFormDetailView):
    allowed_roles = EmployerAssignedFormsView.allowed_roles
    portal_context_types = EmployerAssignedFormsView.portal_context_types
    portal_purposes = EmployerAssignedFormsView.portal_purposes


class EmployerAssignedFormResponseView(PortalAssignedFormResponseView):
    allowed_roles = EmployerAssignedFormsView.allowed_roles
    portal_context_types = EmployerAssignedFormsView.portal_context_types
    portal_purposes = EmployerAssignedFormsView.portal_purposes


class FacilityAssignedFormsView(PortalAssignedFormsView):
    allowed_roles = (UserRole.FACILITY_ADMIN, UserRole.DOCTOR, UserRole.LAB_STAFF)
    portal_context_types = ("facility", "accreditation", "re_accreditation")
    portal_purposes = (
        "facility_data_collection",
        "facility_monthly_report",
        "accreditation_checklist",
        "re_accreditation_checklist",
        "general_data_collection",
    )


class FacilityAssignedFormDetailView(PortalAssignedFormDetailView):
    allowed_roles = FacilityAssignedFormsView.allowed_roles
    portal_context_types = FacilityAssignedFormsView.portal_context_types
    portal_purposes = FacilityAssignedFormsView.portal_purposes


class FacilityAssignedFormResponseView(PortalAssignedFormResponseView):
    allowed_roles = FacilityAssignedFormsView.allowed_roles
    portal_context_types = FacilityAssignedFormsView.portal_context_types
    portal_purposes = FacilityAssignedFormsView.portal_purposes


class FoodHandlerAssignedFormsView(PortalAssignedFormsView):
    allowed_roles = (UserRole.FOOD_HANDLER,)
    portal_context_types = ("food_handler",)
    portal_purposes = (
        "food_handler_survey",
        "food_handler_declaration",
        "general_data_collection",
        "training_feedback",
    )


class FoodHandlerAssignedFormDetailView(PortalAssignedFormDetailView):
    allowed_roles = FoodHandlerAssignedFormsView.allowed_roles
    portal_context_types = FoodHandlerAssignedFormsView.portal_context_types
    portal_purposes = FoodHandlerAssignedFormsView.portal_purposes


class FoodHandlerAssignedFormResponseView(PortalAssignedFormResponseView):
    allowed_roles = FoodHandlerAssignedFormsView.allowed_roles
    portal_context_types = FoodHandlerAssignedFormsView.portal_context_types
    portal_purposes = FoodHandlerAssignedFormsView.portal_purposes
