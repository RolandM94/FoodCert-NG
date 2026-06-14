from rest_framework import serializers

from apps.audit.models import AuditLog
from apps.policy.models import (
    NationalPolicyConfig,
    StatePolicyConfig,
    default_medical_facility_settings,
    default_notification_settings,
    default_security_access_settings,
    default_state_profile_settings,
)


class NationalPolicyConfigSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source="updated_by.get_full_name", read_only=True)

    class Meta:
        model = NationalPolicyConfig
        fields = (
            "id",
            "certificate_validity_months",
            "renewal_reminder_days",
            "typhoid_validity_years",
            "hepatitis_a_second_dose_months",
            "nin_required",
            "payment_before_assessment_required",
            "state_validation_before_certificate_required",
            "public_qr_verification_enabled",
            "state_certificate_template_overrides_enabled",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "updated_by", "updated_by_name", "created_at", "updated_at")


class StatePolicyConfigSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)

    class Meta:
        model = StatePolicyConfig
        fields = (
            "id",
            "state",
            "state_name",
            "requires_state_certificate_validation",
            "certificate_validity_months",
            "typhoid_validity_years",
            "hepatitis_a_second_dose_months",
            "auto_renewal_reminder_days",
            "medical_facility_settings",
            "state_profile_settings",
            "notification_settings",
            "security_access_settings",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "state_name", "updated_by", "created_at", "updated_at")

    def validate_medical_facility_settings(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Medical facility settings must be an object.")

        defaults = default_medical_facility_settings()
        merged = {**defaults, **value}

        positive_number_fields = (
            "validity_duration",
            "initial_review_sla",
            "correction_window",
        )
        zero_or_positive_number_fields = (
            "renewal_window_days",
            "grace_period_days",
        )
        for field in positive_number_fields:
            if not isinstance(merged.get(field), int) or merged[field] < 1:
                raise serializers.ValidationError({field: "Must be a positive integer."})
        for field in zero_or_positive_number_fields:
            if not isinstance(merged.get(field), int) or merged[field] < 0:
                raise serializers.ValidationError({field: "Must be zero or a positive integer."})

        if merged.get("validity_unit") not in {"days", "months", "years"}:
            raise serializers.ValidationError({"validity_unit": "Must be days, months, or years."})
        if merged.get("review_day_type") not in {"working_days", "calendar_days"}:
            raise serializers.ValidationError({"review_day_type": "Must be working_days or calendar_days."})
        if merged.get("correction_day_type") not in {"working_days", "calendar_days"}:
            raise serializers.ValidationError({"correction_day_type": "Must be working_days or calendar_days."})

        for field in ("reminder_days_before_expiry", "escalation_days_after_sla"):
            values = merged.get(field)
            if not isinstance(values, list) or any(not isinstance(item, int) or item < 0 for item in values):
                raise serializers.ValidationError({field: "Must be a list of zero or positive integers."})

        boolean_fields = (
            "disable_assessments_when_expired",
            "disable_assessments_when_suspended",
            "allow_renewal_after_expiry",
            "allow_suspended_renewal",
            "auto_expire_on_expiry_date",
            "require_state_approval_to_reactivate",
            "require_reinspection_before_reactivation",
        )
        for field in boolean_fields:
            if not isinstance(merged.get(field), bool):
                raise serializers.ValidationError({field: "Must be true or false."})

        for field in ("accreditation_template", "reaccreditation_template"):
            if merged.get(field) is None:
                merged[field] = ""
            if not isinstance(merged.get(field), str):
                raise serializers.ValidationError({field: "Must be a template id string."})

        return merged

    def validate_state_profile_settings(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("State profile settings must be an object.")
        merged = {**default_state_profile_settings(), **value}
        if not isinstance(merged.get("signatories"), list):
            raise serializers.ValidationError({"signatories": "Must be a list."})
        if not isinstance(merged.get("working_days"), list):
            raise serializers.ValidationError({"working_days": "Must be a list."})
        return merged

    def validate_notification_settings(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Notification settings must be an object.")
        defaults = default_notification_settings()
        merged = {**defaults, **value}
        for key in ("channels", "event_rules", "reminder_schedules", "recipient_roles"):
            if not isinstance(merged.get(key), dict):
                raise serializers.ValidationError({key: "Must be an object."})
        return merged

    def validate_security_access_settings(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Security access settings must be an object.")
        merged = {**default_security_access_settings(), **value}
        positive_fields = ("minimum_password_length", "session_timeout_minutes", "idle_timeout_minutes", "failed_login_attempts")
        for field in positive_fields:
            if not isinstance(merged.get(field), int) or merged[field] < 1:
                raise serializers.ValidationError({field: "Must be a positive integer."})
        if not isinstance(merged.get("allowed_email_domains"), list):
            raise serializers.ValidationError({"allowed_email_domains": "Must be a list."})
        if not isinstance(merged.get("allowed_mfa_methods"), list):
            raise serializers.ValidationError({"allowed_mfa_methods": "Must be a list."})
        return merged


class StateAuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.get_full_name", read_only=True)
    actor_email = serializers.EmailField(source="actor.email", read_only=True)
    module = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "created_at",
            "actor_name",
            "actor_email",
            "action",
            "module",
            "event",
            "target_type",
            "target_id",
            "status",
            "ip_address",
            "user_agent",
            "metadata",
        )

    def get_module(self, obj):
        return obj.metadata.get("module") or obj.target_type or "Platform"

    def get_event(self, obj):
        return obj.metadata.get("event") or obj.get_action_display()

    def get_status(self, obj):
        return obj.metadata.get("status") or "success"
