from rest_framework import serializers

from apps.policy.models import NationalPolicyConfig, StatePolicyConfig


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
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "state_name", "updated_by", "created_at", "updated_at")
