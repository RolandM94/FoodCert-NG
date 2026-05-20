from rest_framework import serializers

from apps.facilities.models import MedicalFacility
from apps.payments.models import AssessmentFee, PaymentTransaction


class AssessmentFeeSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)

    class Meta:
        model = AssessmentFee
        fields = (
            "id",
            "state",
            "state_name",
            "facility_type",
            "amount",
            "currency",
            "state_fee",
            "facility_fee",
            "platform_fee",
            "effective_from",
            "effective_to",
            "status",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")


class PaymentTransactionSerializer(serializers.ModelSerializer):
    payer_email = serializers.EmailField(source="payer_user.email", read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = (
            "id",
            "payer_user",
            "payer_email",
            "payer_type",
            "related_entity_type",
            "related_entity_id",
            "amount",
            "currency",
            "payment_provider",
            "provider_reference",
            "internal_reference",
            "status",
            "paid_at",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class InitiateAssessmentPaymentSerializer(serializers.Serializer):
    food_handler_id = serializers.UUIDField()
    facility = serializers.PrimaryKeyRelatedField(queryset=MedicalFacility.objects.all())


class InitiateSubscriptionPaymentSerializer(serializers.Serializer):
    employer_id = serializers.UUIDField()
    plan_id = serializers.UUIDField()
    billing_cycle = serializers.ChoiceField(choices=["monthly", "yearly"])


class PaymentWebhookSerializer(serializers.Serializer):
    reference = serializers.CharField()
    event = serializers.CharField(required=False, allow_blank=True)
