from django.contrib import admin

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


@admin.register(FormTemplate)
class FormTemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "purpose", "primary_module", "visibility", "status", "current_version", "owner_organization", "updated_at")
    list_filter = ("purpose", "primary_module", "visibility", "status", "language")
    search_fields = ("title", "description", "owner_organization__name")
    readonly_fields = ("created_at", "updated_at", "archived_at")
    filter_horizontal = ("shared_with_states",)


@admin.register(FormTemplateVersion)
class FormTemplateVersionAdmin(admin.ModelAdmin):
    list_display = ("template", "version_number", "status", "published_by", "published_at")
    list_filter = ("status",)
    search_fields = ("template__title",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(FormAssignment)
class FormAssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "template", "purpose", "assigned_to_type", "status", "due_date", "created_at")
    list_filter = ("purpose", "assigned_to_type", "context_type", "status", "allow_offline")
    search_fields = ("title", "template__title", "assigned_to_id", "context_id")
    readonly_fields = ("created_at", "updated_at", "closed_at")


@admin.register(FormRecipient)
class FormRecipientAdmin(admin.ModelAdmin):
    list_display = ("assignment", "recipient_type", "recipient_id", "organization", "status")
    list_filter = ("recipient_type", "status")
    search_fields = ("assignment__title", "recipient_id", "organization__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    list_display = ("template", "assignment", "respondent_user", "status", "sync_status", "submitted_at", "reviewed_at")
    list_filter = ("status", "sync_status", "context_type", "risk_rating")
    search_fields = ("template__title", "assignment__title", "respondent_user__email", "context_id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(FormResponseAttachment)
class FormResponseAttachmentAdmin(admin.ModelAdmin):
    list_display = ("response", "question_key", "file_name", "mime_type", "sync_status", "created_at")
    list_filter = ("sync_status", "file_type", "mime_type")
    search_fields = ("response__template__title", "question_key", "file_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(FormResponseActivityLog)
class FormResponseActivityLogAdmin(admin.ModelAdmin):
    list_display = ("response", "action", "actor", "created_at")
    list_filter = ("action",)
    search_fields = ("response__template__title", "action", "actor__email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(OfflineSyncQueue)
class OfflineSyncQueueAdmin(admin.ModelAdmin):
    list_display = ("user", "assignment", "local_response_id", "operation_type", "status", "attempt_count", "last_attempt_at")
    list_filter = ("operation_type", "status")
    search_fields = ("user__email", "local_response_id", "assignment__title")
    readonly_fields = ("created_at", "updated_at", "last_attempt_at")
