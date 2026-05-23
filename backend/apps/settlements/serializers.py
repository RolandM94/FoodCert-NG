from rest_framework import serializers

from apps.settlements.models import Settlement


class SettlementSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)
    payment_reference = serializers.CharField(source="payment_transaction.internal_reference", read_only=True)
    payment_status = serializers.CharField(source="payment_transaction.status", read_only=True)
    disputed_by_name = serializers.CharField(source="disputed_by.get_full_name", read_only=True)

    class Meta:
        model = Settlement
        fields = (
            "id",
            "facility",
            "facility_name",
            "state",
            "state_name",
            "payment_transaction",
            "payment_reference",
            "payment_status",
            "assessment",
            "gross_amount",
            "facility_amount",
            "state_amount",
            "platform_amount",
            "settlement_status",
            "settlement_reference",
            "settled_at",
            "dispute_status",
            "dispute_reason",
            "disputed_by",
            "disputed_by_name",
            "disputed_at",
            "dispute_resolution",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CreateSettlementSerializer(serializers.Serializer):
    payment_transaction = serializers.UUIDField()
    assessment = serializers.UUIDField(required=False)


class SettlementDisputeSerializer(serializers.Serializer):
    reason = serializers.CharField()
