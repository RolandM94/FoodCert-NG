from rest_framework import serializers

from apps.settlements.models import Settlement


class SettlementSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)

    class Meta:
        model = Settlement
        fields = (
            "id",
            "facility",
            "facility_name",
            "state",
            "state_name",
            "payment_transaction",
            "assessment",
            "gross_amount",
            "facility_amount",
            "state_amount",
            "platform_amount",
            "settlement_status",
            "settlement_reference",
            "settled_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CreateSettlementSerializer(serializers.Serializer):
    payment_transaction = serializers.UUIDField()
    assessment = serializers.UUIDField(required=False)
