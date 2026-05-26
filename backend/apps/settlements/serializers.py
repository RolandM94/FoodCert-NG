from rest_framework import serializers

from apps.settlements.models import Settlement, SettlementBatch


class SettlementSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)
    payment_reference = serializers.CharField(source="payment_transaction.internal_reference", read_only=True)
    payment_status = serializers.CharField(source="payment_transaction.status", read_only=True)
    disputed_by_name = serializers.CharField(source="disputed_by.get_full_name", read_only=True)
    fee_schedule_name = serializers.CharField(source="fee_schedule.fee_name", read_only=True)
    payment_allocation_reference = serializers.CharField(source="payment_allocation.id", read_only=True)

    class Meta:
        model = Settlement
        fields = (
            "id",
            "facility",
            "facility_name",
            "state",
            "state_name",
            "payment_transaction",
            "payment_allocation",
            "payment_allocation_reference",
            "payment_reference",
            "payment_status",
            "fee_schedule",
            "fee_schedule_name",
            "assessment",
            "gross_amount",
            "facility_amount",
            "state_amount",
            "platform_amount",
            "eligibility_checked_at",
            "eligibility_reason",
            "batch",
            "settlement_status",
            "settlement_reference",
            "settled_at",
            "payout_attempts",
            "last_payout_error",
            "held_at",
            "hold_reason",
            "released_at",
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


class EligibleSettlementAllocationSerializer(serializers.Serializer):
    payment_allocation = serializers.UUIDField(source="id")
    payment_transaction = serializers.UUIDField(source="payment_transaction_id")
    payment_reference = serializers.CharField(source="payment_transaction.internal_reference")
    assessment = serializers.UUIDField(source="assessment_id", allow_null=True)
    facility = serializers.UUIDField(source="facility_id")
    facility_name = serializers.CharField(source="facility.facility_name")
    state = serializers.UUIDField(source="state_id")
    state_name = serializers.CharField(source="state.name")
    fee_schedule = serializers.UUIDField(source="fee_schedule_id")
    fee_schedule_name = serializers.CharField(source="fee_schedule.fee_name")
    gross_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    facility_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    state_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    platform_amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class SettlementDisputeSerializer(serializers.Serializer):
    reason = serializers.CharField()


class SettlementActionReasonSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class SettlementDisputeResolutionSerializer(serializers.Serializer):
    resolution = serializers.CharField()
    approved = serializers.BooleanField(default=True)


class SettlementBatchSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    approved_by_email = serializers.EmailField(source="approved_by.email", read_only=True)
    processed_by_email = serializers.EmailField(source="processed_by.email", read_only=True)

    class Meta:
        model = SettlementBatch
        fields = (
            "id",
            "batch_reference",
            "status",
            "settlement_count",
            "gross_amount",
            "facility_amount",
            "state_amount",
            "platform_amount",
            "created_by",
            "created_by_email",
            "approved_by",
            "approved_by_email",
            "processed_by",
            "processed_by_email",
            "approved_at",
            "processed_at",
            "payout_reference",
            "failure_reason",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class SettlementBatchCreateSerializer(serializers.Serializer):
    settlements = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)


class SettlementBatchProcessSerializer(serializers.Serializer):
    simulate_failure = serializers.BooleanField(default=False)
    failure_reason = serializers.CharField(required=False, allow_blank=True)
