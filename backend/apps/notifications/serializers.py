from rest_framework import serializers

from apps.notifications.models import (
    BroadcastMessage,
    BroadcastStatus,
    Notification,
    NotificationCategory,
    NotificationChannel,
    NotificationDelivery,
    NotificationPreference,
    NotificationPriority,
    NotificationProvider,
    NotificationTemplate,
    TemplateScope,
    TemplateStatus,
)
from apps.notifications.services import SENSITIVE_VARIABLES


class NotificationSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    recipient_name = serializers.CharField(source="recipient.get_full_name", read_only=True, default="")
    organization_name = serializers.CharField(source="organization.name", read_only=True, default="")
    organization_unit_name = serializers.CharField(source="organization_unit.name", read_only=True, default="")

    class Meta:
        model = Notification
        fields = (
            "id",
            "recipient",
            "recipient_name",
            "recipient_email",
            "recipient_phone",
            "recipient_type",
            "organization",
            "organization_name",
            "organization_unit",
            "organization_unit_name",
            "category",
            "category_display",
            "priority",
            "priority_display",
            "title",
            "message",
            "action_url",
            "related_object_type",
            "related_object_id",
            "is_read",
            "is_archived",
            "read_at",
            "created_at",
        )
        read_only_fields = (
            "id",
            "recipient_name",
            "organization_name",
            "organization_unit_name",
            "category_display",
            "priority_display",
            "is_read",
            "is_archived",
            "read_at",
            "created_at",
        )


class NotificationListSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "category",
            "category_display",
            "priority",
            "priority_display",
            "title",
            "message",
            "action_url",
            "related_object_type",
            "related_object_id",
            "is_read",
            "is_archived",
            "read_at",
            "created_at",
        )
        read_only_fields = fields


class UnreadCountSerializer(serializers.Serializer):
    unread_count = serializers.IntegerField()


class MarkAllReadSerializer(serializers.Serializer):
    category = serializers.ChoiceField(choices=NotificationCategory.choices, required=False, allow_blank=True)


class CategoryFilterSerializer(serializers.Serializer):
    category = serializers.MultipleChoiceField(choices=NotificationCategory.choices, required=False)
    priority = serializers.MultipleChoiceField(choices=NotificationPriority.choices, required=False)
    is_read = serializers.BooleanField(required=False, allow_null=True)
    is_archived = serializers.BooleanField(required=False, allow_null=True)
    search = serializers.CharField(required=False, allow_blank=True, max_length=255)


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    channel_display = serializers.CharField(source="get_channel_display", read_only=True)

    class Meta:
        model = NotificationPreference
        fields = (
            "id",
            "user",
            "category",
            "category_display",
            "channel",
            "channel_display",
            "is_enabled",
            "digest_enabled",
            "quiet_hours_start",
            "quiet_hours_end",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "category_display", "channel_display", "created_at", "updated_at")


class NotificationPreferenceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = (
            "is_enabled",
            "digest_enabled",
            "quiet_hours_start",
            "quiet_hours_end",
        )


class BulkPreferenceUpdateSerializer(serializers.Serializer):
    preferences = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
    )

    def validate_preferences(self, value):
        valid_category_channels = set()
        for pref in value:
            category = pref.get("category")
            channel = pref.get("channel")
            if not category or not channel:
                raise serializers.ValidationError("Each preference needs 'category' and 'channel'.")
            key = f"{category}|{channel}"
            if key in valid_category_channels:
                raise serializers.ValidationError(f"Duplicate preference for {category}/{channel}.")
            valid_category_channels.add(key)
        return value


# ---- Template Serializers ----

class NotificationTemplateSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    channel_display = serializers.CharField(source="get_channel_display", read_only=True)
    scope_display = serializers.CharField(source="get_scope_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True, default="")
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True, default="")
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True, default="")

    class Meta:
        model = NotificationTemplate
        fields = (
            "id",
            "template_key",
            "name",
            "category",
            "category_display",
            "channel",
            "channel_display",
            "subject",
            "body",
            "allowed_variables",
            "language",
            "scope",
            "scope_display",
            "state",
            "state_name",
            "version",
            "status",
            "status_display",
            "created_by",
            "created_by_name",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "version",
            "status",
            "category_display",
            "channel_display",
            "scope_display",
            "status_display",
            "state_name",
            "created_by_name",
            "approved_by_name",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
        )


class NotificationTemplateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = (
            "template_key",
            "name",
            "category",
            "channel",
            "subject",
            "body",
            "allowed_variables",
            "language",
            "scope",
            "state",
        )

    def validate_allowed_variables(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("allowed_variables must be a list.")
        blocked = set(value) & SENSITIVE_VARIABLES
        if blocked:
            raise serializers.ValidationError(
                f"Sensitive variables are not allowed: {sorted(blocked)}"
            )
        return value


class NotificationTemplateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = (
            "name",
            "category",
            "channel",
            "subject",
            "body",
            "allowed_variables",
            "language",
            "scope",
            "state",
        )

    def validate_allowed_variables(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("allowed_variables must be a list.")
        blocked = set(value) & SENSITIVE_VARIABLES
        if blocked:
            raise serializers.ValidationError(
                f"Sensitive variables are not allowed: {sorted(blocked)}"
            )
        return value


class TemplatePreviewSerializer(serializers.Serializer):
    context = serializers.DictField(required=False, default=dict)


class TemplateApproveSerializer(serializers.Serializer):
    pass


class TemplateSubmitSerializer(serializers.Serializer):
    pass


# ---- Provider Serializers ----

class NotificationProviderSerializer(serializers.ModelSerializer):
    channel_display = serializers.CharField(source="get_channel_display", read_only=True)

    class Meta:
        model = NotificationProvider
        fields = (
            "id",
            "name",
            "channel",
            "channel_display",
            "sender_id",
            "config",
            "is_default",
            "is_active",
            "priority_order",
            "rate_limit_per_minute",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "channel_display", "created_at", "updated_at")


class NotificationProviderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationProvider
        fields = (
            "name",
            "channel",
            "sender_id",
            "config",
            "is_default",
            "is_active",
            "priority_order",
            "rate_limit_per_minute",
        )


class NotificationProviderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationProvider
        fields = (
            "name",
            "sender_id",
            "config",
            "is_default",
            "is_active",
            "priority_order",
            "rate_limit_per_minute",
        )


class ProviderTestSerializer(serializers.Serializer):
    pass


# ---- Delivery Serializers ----

class NotificationDeliverySerializer(serializers.ModelSerializer):
    channel_display = serializers.CharField(source="get_channel_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    notification_title = serializers.CharField(source="notification.title", read_only=True, default="")

    class Meta:
        model = NotificationDelivery
        fields = (
            "id",
            "notification",
            "notification_title",
            "channel",
            "channel_display",
            "provider",
            "destination",
            "status",
            "status_display",
            "provider_message_id",
            "provider_response",
            "error_code",
            "error_message",
            "retry_count",
            "next_retry_at",
            "sent_at",
            "delivered_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "notification_title",
            "channel_display",
            "status_display",
            "created_at",
            "updated_at",
        )


class DeliveryRetrySerializer(serializers.Serializer):
    pass


# ---- Broadcast Serializers ----

class BroadcastMessageSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True, default="")
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True, default="")

    class Meta:
        model = BroadcastMessage
        fields = (
            "id",
            "title",
            "message",
            "category",
            "category_display",
            "priority",
            "priority_display",
            "audience_type",
            "audience_filters",
            "channels",
            "status",
            "status_display",
            "estimated_recipient_count",
            "sent_count",
            "failed_count",
            "created_by",
            "created_by_name",
            "approved_by",
            "approved_by_name",
            "sent_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "category_display",
            "priority_display",
            "status_display",
            "created_by_name",
            "approved_by_name",
            "estimated_recipient_count",
            "sent_count",
            "failed_count",
            "approved_by",
            "sent_at",
            "created_at",
            "updated_at",
        )


class BroadcastCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastMessage
        fields = (
            "title",
            "message",
            "category",
            "priority",
            "audience_type",
            "audience_filters",
            "channels",
        )


class BroadcastUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastMessage
        fields = (
            "title",
            "message",
            "category",
            "priority",
            "audience_type",
            "audience_filters",
            "channels",
        )
