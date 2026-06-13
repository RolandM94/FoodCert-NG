from rest_framework import serializers

from apps.forms.models import (
    FormAssignment,
    FormRecipient,
    FormResponse,
    FormResponseActivityLog,
    FormResponseAttachment,
    FormTemplate,
    FormTemplateVersion,
    OfflineSyncQueue,
)


class FormTemplateSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner_organization.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    response_count = serializers.SerializerMethodField()

    class Meta:
        model = FormTemplate
        fields = (
            "id", "title", "description", "purpose", "owner_organization", "owner_name",
            "target_respondent_type", "primary_module", "module_context", "default_context_type",
            "language", "settings_json", "status", "current_version", "created_by",
            "created_by_name", "response_count", "archived_at", "created_at", "updated_at",
        )
        read_only_fields = ("id", "owner_name", "created_by_name", "response_count", "archived_at", "created_at", "updated_at")
        extra_kwargs = {"owner_organization": {"required": False}}

    def get_response_count(self, obj):
        return obj.responses.count()


class FormTemplateVersionSerializer(serializers.ModelSerializer):
    published_by_name = serializers.CharField(source="published_by.get_full_name", read_only=True)

    class Meta:
        model = FormTemplateVersion
        fields = (
            "id", "template", "version_number", "schema_json", "logic_json", "scoring_json",
            "conditional_logic_json", "settings_json", "published_by", "published_by_name",
            "published_at", "status", "created_at",
        )
        read_only_fields = ("id", "published_by_name", "created_at")


class FormAssignmentSerializer(serializers.ModelSerializer):
    template_title = serializers.CharField(source="template.title", read_only=True)
    assigned_by_name = serializers.CharField(source="assigned_by.get_full_name", read_only=True)
    response_count = serializers.SerializerMethodField()
    total_recipients = serializers.SerializerMethodField()
    status_summary = serializers.SerializerMethodField()
    response_rate = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()

    class Meta:
        model = FormAssignment
        fields = (
            "id", "title", "template", "template_title", "template_version",
            "purpose", "assigned_by", "assigned_by_name",
            "assigned_to_type", "assigned_to_id", "recipient_role",
            "context_type", "context_id",
            "start_date", "due_date",
            "allow_draft", "allow_offline", "allow_multiple_submissions", "allow_late_submission",
            "requires_review", "reviewer_role",
            "status", "response_count", "total_recipients", "status_summary",
            "response_rate", "completion_rate", "closed_at", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "assigned_by_name", "template_title", "response_count",
            "total_recipients", "status_summary", "response_rate", "completion_rate",
            "closed_at", "created_at", "updated_at",
        )

    def get_response_count(self, obj):
        return obj.responses.count()

    def get_total_recipients(self, obj):
        recipient_count = getattr(obj, "recipient_count", None)
        if recipient_count is not None:
            return recipient_count
        return obj.recipients.count()

    def get_status_summary(self, obj):
        recipient_statuses = list(obj.recipients.values_list("status", flat=True))
        response_statuses = list(obj.responses.values_list("status", flat=True))
        summary = {
            "total_recipients": len(recipient_statuses),
            "not_started": recipient_statuses.count("not_started"),
            "in_progress": recipient_statuses.count("in_progress"),
            "submitted": recipient_statuses.count("submitted"),
            "reviewed": recipient_statuses.count("reviewed"),
            "returned": recipient_statuses.count("returned"),
            "overdue": recipient_statuses.count("overdue"),
            "cancelled": recipient_statuses.count("cancelled"),
            "draft_responses": response_statuses.count("draft"),
            "sync_pending": response_statuses.count("sync_pending"),
            "sync_failed": response_statuses.count("sync_failed"),
        }
        if not summary["total_recipients"]:
            summary["total_recipients"] = obj.responses.count()
            summary["not_started"] = max(summary["total_recipients"] - obj.responses.exclude(status="not_started").count(), 0)
        return summary

    def get_response_rate(self, obj):
        summary = self.get_status_summary(obj)
        total = summary["total_recipients"]
        if not total:
            return 0
        started = total - summary["not_started"] - summary["cancelled"]
        return round((max(started, 0) / total) * 100, 1)

    def get_completion_rate(self, obj):
        summary = self.get_status_summary(obj)
        total = summary["total_recipients"]
        if not total:
            return 0
        complete = summary["submitted"] + summary["reviewed"]
        return round((complete / total) * 100, 1)


class FormRecipientSerializer(serializers.ModelSerializer):
    assignment_title = serializers.CharField(source="assignment.title", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = FormRecipient
        fields = (
            "id", "assignment", "assignment_title", "recipient_type", "recipient_id",
            "organization", "organization_name", "role_id", "status", "notified_at",
            "started_at", "submitted_at", "reviewed_at", "created_at", "updated_at",
        )
        read_only_fields = ("id", "assignment_title", "organization_name", "created_at", "updated_at")


class FormResponseAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.get_full_name", read_only=True)

    class Meta:
        model = FormResponseAttachment
        fields = (
            "id", "response", "question_key", "repeat_group_key", "repeat_item_id",
            "file", "file_url", "file_type", "file_name", "file_size", "mime_type",
            "uploaded_by", "uploaded_by_name", "captured_at", "gps_latitude",
            "gps_longitude", "metadata_json", "sync_status", "created_at", "updated_at",
        )
        read_only_fields = ("id", "uploaded_by_name", "created_at", "updated_at")

    def validate(self, attrs):
        uploaded_file = attrs.get("file")
        if uploaded_file:
            attrs["file_name"] = attrs.get("file_name") or uploaded_file.name
            attrs["file_size"] = attrs.get("file_size") or uploaded_file.size
            attrs["mime_type"] = attrs.get("mime_type") or getattr(uploaded_file, "content_type", "")
            attrs["file_type"] = attrs.get("file_type") or (attrs["mime_type"].split("/")[0] if attrs.get("mime_type") else "")
        if not uploaded_file and not attrs.get("file_url"):
            raise serializers.ValidationError("Upload a file or provide a file URL.")
        return attrs


class FormResponseActivityLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.get_full_name", read_only=True)

    class Meta:
        model = FormResponseActivityLog
        fields = (
            "id", "response", "actor", "actor_name", "action", "details_json",
            "ip_address", "device_id", "created_at",
        )
        read_only_fields = fields


class FormResponseSerializer(serializers.ModelSerializer):
    template_title = serializers.CharField(source="template.title", read_only=True)
    assignment_title = serializers.CharField(source="assignment.title", read_only=True)
    respondent_name = serializers.CharField(source="respondent_user.get_full_name", read_only=True)
    respondent_email = serializers.EmailField(source="respondent_user.email", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)
    template_schema = serializers.SerializerMethodField()
    template_logic = serializers.SerializerMethodField()
    template_settings = serializers.SerializerMethodField()

    class Meta:
        model = FormResponse
        fields = (
            "id", "assignment", "assignment_title", "template", "template_title",
            "template_version", "recipient", "respondent_user", "respondent_name", "respondent_email",
            "respondent_organization", "context_type", "context_id",
            "response_json", "score", "risk_rating",
            "status", "sync_status", "device_id", "offline_created_at", "started_at",
            "last_saved_at", "submitted_at",
            "reviewed_by", "reviewed_by_name", "reviewed_at",
            "review_notes", "returned_reason",
            "template_schema", "template_logic", "template_settings",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "template_title", "assignment_title", "respondent_name",
                            "respondent_email", "reviewed_by_name", "template_schema",
                            "template_logic", "template_settings", "created_at", "updated_at")

    def get_template_schema(self, obj):
        return obj.template_version.schema_json if obj.template_version_id else {}

    def get_template_logic(self, obj):
        return obj.template_version.logic_json if obj.template_version_id else {}

    def get_template_settings(self, obj):
        if obj.template_version_id:
            return obj.template_version.settings_json
        return obj.template.settings_json


class OfflineSyncQueueSerializer(serializers.ModelSerializer):
    assignment_title = serializers.CharField(source="assignment.title", read_only=True)
    response_status = serializers.CharField(source="response.status", read_only=True)

    class Meta:
        model = OfflineSyncQueue
        fields = (
            "id", "user", "assignment", "assignment_title", "response",
            "response_status", "local_response_id", "operation_type", "payload_json",
            "media_payload_ref", "status", "attempt_count", "last_attempt_at",
            "error_message", "created_at", "updated_at",
        )
        read_only_fields = fields
