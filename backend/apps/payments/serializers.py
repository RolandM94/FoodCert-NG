from rest_framework import serializers

from apps.facilities.models import MedicalFacility
from apps.payments.models import AssessmentFee, PaymentAllocation, PaymentProvider, PaymentReconciliationRecord, PaymentTransaction, PaymentWebhookEvent, Receipt, RefundRequest
from apps.payments.permissions import redacted_finance_metadata
from apps.payments.services import PaymentService


class AssessmentFeeSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    platform_fee = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentFee
        fields = (
            "id",
            "state",
            "state_name",
            "facility_type",
            "fee_name",
            "amount",
            "currency",
            "state_fee",
            "facility_fee",
            "platform_fee",
            "provider_fee_handling",
            "effective_from",
            "effective_to",
            "status",
            "created_by",
            "approved_by",
            "approved_at",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "approved_by", "approved_at", "platform_fee", "created_at", "updated_at")

    def get_platform_fee(self, obj):
        return f"{PaymentService.current_platform_fee(currency=obj.currency):.2f}"


class PaymentTransactionSerializer(serializers.ModelSerializer):
    payer_email = serializers.EmailField(source="payer_user.email", read_only=True)
    metadata = serializers.SerializerMethodField()

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

    def get_metadata(self, obj):
        return redacted_finance_metadata(obj.metadata)


class PaymentProviderSerializer(serializers.ModelSerializer):
    encrypted_secret_key = serializers.CharField(write_only=True, required=False, allow_blank=True)
    webhook_secret = serializers.CharField(write_only=True, required=False, allow_blank=True)
    has_secret_key = serializers.SerializerMethodField()
    has_webhook_secret = serializers.SerializerMethodField()

    class Meta:
        model = PaymentProvider
        fields = (
            "id",
            "name",
            "code",
            "environment",
            "public_key",
            "encrypted_secret_key",
            "webhook_secret",
            "callback_url",
            "webhook_url",
            "supported_methods",
            "supports_refunds",
            "supports_transfers",
            "is_active",
            "has_secret_key",
            "has_webhook_secret",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "has_secret_key", "has_webhook_secret", "created_at", "updated_at")

    def get_has_secret_key(self, obj):
        return bool(obj.encrypted_secret_key)

    def get_has_webhook_secret(self, obj):
        return bool(obj.webhook_secret)


class PaymentWebhookEventSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source="provider.name", read_only=True)

    class Meta:
        model = PaymentWebhookEvent
        fields = (
            "id",
            "provider",
            "provider_name",
            "provider_code",
            "event_type",
            "provider_reference",
            "idempotency_key",
            "signature_valid",
            "processing_status",
            "processing_message",
            "processed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class PaymentReconciliationRecordSerializer(serializers.ModelSerializer):
    payment_reference = serializers.CharField(source="payment_transaction.internal_reference", read_only=True)
    resolved_by_email = serializers.EmailField(source="resolved_by.email", read_only=True)

    class Meta:
        model = PaymentReconciliationRecord
        fields = (
            "id",
            "provider_code",
            "provider_reference",
            "internal_reference",
            "payment_transaction",
            "payment_reference",
            "amount",
            "currency",
            "status",
            "provider_payload",
            "matched_at",
            "resolved_by",
            "resolved_by_email",
            "resolved_at",
            "resolution_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ReconciliationImportRecordSerializer(serializers.Serializer):
    provider_reference = serializers.CharField()
    internal_reference = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(required=False, default="NGN")
    provider_payload = serializers.JSONField(required=False)


class ReconciliationImportSerializer(serializers.Serializer):
    provider_code = serializers.CharField()
    records = ReconciliationImportRecordSerializer(many=True)


class ReconciliationResolveSerializer(serializers.Serializer):
    notes = serializers.CharField()


class ProviderPerformanceSerializer(serializers.Serializer):
    provider_code = serializers.CharField()
    total_records = serializers.IntegerField()
    matched_records = serializers.IntegerField()
    issue_records = serializers.IntegerField()
    manually_resolved_records = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=14, decimal_places=2, allow_null=True)


class AssessmentPaymentQuoteSerializer(serializers.Serializer):
    assessment_id = serializers.UUIDField()
    fee_schedule_id = serializers.UUIDField()
    fee_name = serializers.CharField()
    facility_name = serializers.CharField()
    state_name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField()
    state_fee = serializers.DecimalField(max_digits=12, decimal_places=2)
    facility_fee = serializers.DecimalField(max_digits=12, decimal_places=2)
    platform_fee = serializers.DecimalField(max_digits=12, decimal_places=2)
    refund_policy_summary = serializers.CharField()
    terms_notice = serializers.CharField()


class BulkAssessmentPaymentLineItemSerializer(serializers.Serializer):
    assessment_id = serializers.UUIDField()
    food_handler_id = serializers.UUIDField()
    food_handler_name = serializers.CharField()
    facility_id = serializers.UUIDField()
    facility_name = serializers.CharField()
    state_id = serializers.UUIDField()
    state_name = serializers.CharField()
    fee_schedule_id = serializers.UUIDField()
    fee_name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField()
    state_fee = serializers.DecimalField(max_digits=12, decimal_places=2)
    facility_fee = serializers.DecimalField(max_digits=12, decimal_places=2)
    platform_fee = serializers.DecimalField(max_digits=12, decimal_places=2)


class BulkAssessmentPaymentQuoteSerializer(serializers.Serializer):
    employer_id = serializers.UUIDField()
    employer_name = serializers.CharField()
    assessment_count = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField()
    line_items = BulkAssessmentPaymentLineItemSerializer(many=True)
    terms_notice = serializers.CharField()


class ReceiptSerializer(serializers.ModelSerializer):
    payment_reference = serializers.CharField(source="payment_transaction.internal_reference", read_only=True)
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)

    class Meta:
        model = Receipt
        fields = (
            "id",
            "receipt_number",
            "payment_transaction",
            "payment_reference",
            "payer_name",
            "payer_email",
            "payer_type",
            "payment_purpose",
            "amount",
            "currency",
            "payment_method",
            "provider_reference",
            "facility",
            "facility_name",
            "state",
            "state_name",
            "line_items",
            "issued_at",
            "receipt_url",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class RefundRequestSerializer(serializers.ModelSerializer):
    payment_reference = serializers.CharField(source="payment_transaction.internal_reference", read_only=True)
    requested_by_email = serializers.EmailField(source="requested_by.email", read_only=True)

    class Meta:
        model = RefundRequest
        fields = (
            "id",
            "payment_transaction",
            "payment_allocation",
            "payment_reference",
            "requested_by",
            "requested_by_email",
            "approved_by",
            "amount",
            "reason",
            "review_notes",
            "status",
            "provider_refund_reference",
            "approved_at",
            "processed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "payment_reference",
            "requested_by",
            "requested_by_email",
            "approved_by",
            "payment_allocation",
            "status",
            "review_notes",
            "provider_refund_reference",
            "approved_at",
            "processed_at",
            "created_at",
            "updated_at",
        )


class RefundRequestCreateSerializer(serializers.Serializer):
    payment_allocation = serializers.PrimaryKeyRelatedField(queryset=PaymentAllocation.objects.all(), required=False)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    reason = serializers.CharField()


class RefundReviewSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)


class ChargebackSerializer(serializers.Serializer):
    reference = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    reason = serializers.CharField(required=False, allow_blank=True)


class InitiateAssessmentPaymentSerializer(serializers.Serializer):
    food_handler_id = serializers.UUIDField()
    facility = serializers.PrimaryKeyRelatedField(queryset=MedicalFacility.objects.all())


class BulkAssessmentPaymentRequestSerializer(serializers.Serializer):
    assessment_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)


class InitiateSubscriptionPaymentSerializer(serializers.Serializer):
    employer_id = serializers.UUIDField()
    plan_id = serializers.UUIDField()
    billing_cycle = serializers.ChoiceField(choices=["monthly", "yearly"])


class PaymentWebhookSerializer(serializers.Serializer):
    reference = serializers.CharField(required=False, allow_blank=True)
    event = serializers.CharField(required=False, allow_blank=True)
    event_type = serializers.CharField(required=False, allow_blank=True)
    provider_reference = serializers.CharField(required=False, allow_blank=True)
    idempotency_key = serializers.CharField(required=False, allow_blank=True)
    event_id = serializers.CharField(required=False, allow_blank=True)
    data = serializers.JSONField(required=False)

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if isinstance(data, dict):
            for key, item in data.items():
                value.setdefault(key, item)
        return value
