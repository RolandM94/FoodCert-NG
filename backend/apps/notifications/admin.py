from django.contrib import admin

from apps.notifications.models import (
    BroadcastMessage,
    Notification,
    NotificationDelivery,
    NotificationEvent,
    NotificationPreference,
    NotificationProvider,
    NotificationTemplate,
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "recipient_type", "category", "priority", "is_read", "created_at")
    list_filter = ("category", "priority", "is_read", "created_at")
    search_fields = ("title", "message", "recipient__email", "recipient_email", "recipient_phone")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "template_key", "category", "channel", "scope", "version", "status", "created_at")
    list_filter = ("category", "channel", "scope", "status", "language")
    search_fields = ("name", "template_key", "subject", "body")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):
    list_display = ("notification", "channel", "provider", "destination", "status", "retry_count", "created_at")
    list_filter = ("channel", "status", "provider", "created_at")
    search_fields = ("destination", "provider_message_id", "error_message", "notification__title")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("notification",)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "channel", "is_enabled", "digest_enabled", "created_at")
    list_filter = ("category", "channel", "is_enabled", "digest_enabled")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(NotificationProvider)
class NotificationProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "channel", "sender_id", "is_default", "is_active", "priority_order", "rate_limit_per_minute")
    list_filter = ("channel", "is_default", "is_active")
    search_fields = ("name", "sender_id")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(NotificationEvent)
class NotificationEventAdmin(admin.ModelAdmin):
    list_display = ("event_key", "source_module", "related_object_type", "processed", "processed_at", "created_at")
    list_filter = ("source_module", "processed", "created_at")
    search_fields = ("event_key", "source_module", "related_object_type")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "priority", "status", "audience_type", "estimated_recipient_count", "sent_count", "created_at")
    list_filter = ("category", "priority", "status", "audience_type", "created_at")
    search_fields = ("title", "message")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("created_by", "approved_by")
