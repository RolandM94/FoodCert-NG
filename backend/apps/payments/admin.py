from django.contrib import admin

from apps.payments.models import AssessmentFee, PaymentAllocation, PaymentLedgerEntry, PaymentProvider, PaymentReconciliationRecord, PaymentTransaction, PaymentWebhookEvent, RefundRequest


@admin.register(AssessmentFee)
class AssessmentFeeAdmin(admin.ModelAdmin):
    list_display = ("state", "facility_type", "fee_name", "amount", "currency", "status", "effective_from", "effective_to", "approved_at")
    list_filter = ("state", "facility_type", "status")
    search_fields = ("state__name", "state__code", "facility_type", "fee_name")


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("internal_reference", "payer_user", "payer_type", "amount", "currency", "status", "created_at")
    list_filter = ("payer_type", "status", "payment_provider", "created_at")
    search_fields = ("internal_reference", "provider_reference", "payer_user__email")


@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "environment", "is_active", "supports_refunds", "supports_transfers")
    list_filter = ("environment", "is_active", "supports_refunds", "supports_transfers")
    search_fields = ("name", "code")


@admin.register(PaymentWebhookEvent)
class PaymentWebhookEventAdmin(admin.ModelAdmin):
    list_display = ("provider_code", "event_type", "provider_reference", "processing_status", "signature_valid", "created_at")
    list_filter = ("provider_code", "processing_status", "signature_valid", "created_at")
    search_fields = ("provider_reference", "idempotency_key")


@admin.register(PaymentReconciliationRecord)
class PaymentReconciliationRecordAdmin(admin.ModelAdmin):
    list_display = ("provider_code", "provider_reference", "internal_reference", "amount", "currency", "status", "created_at", "resolved_at")
    list_filter = ("provider_code", "status", "currency", "created_at")
    search_fields = ("provider_reference", "internal_reference", "payment_transaction__internal_reference")
    readonly_fields = ("matched_at", "resolved_at")


@admin.register(PaymentAllocation)
class PaymentAllocationAdmin(admin.ModelAdmin):
    list_display = ("payment_transaction", "assessment", "facility", "state", "gross_amount", "status")
    list_filter = ("status", "state", "facility", "created_at")
    search_fields = ("payment_transaction__internal_reference", "facility__facility_name")


@admin.register(PaymentLedgerEntry)
class PaymentLedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("reference", "payment_transaction", "entry_type", "account", "direction", "amount", "currency")
    list_filter = ("entry_type", "direction", "account", "created_at")
    search_fields = ("reference", "payment_transaction__internal_reference")

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ("payment_transaction", "requested_by", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("payment_transaction__internal_reference", "requested_by__email", "reason")
