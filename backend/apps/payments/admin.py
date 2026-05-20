from django.contrib import admin

from apps.payments.models import AssessmentFee, PaymentTransaction


@admin.register(AssessmentFee)
class AssessmentFeeAdmin(admin.ModelAdmin):
    list_display = ("state", "facility_type", "amount", "currency", "status", "effective_from", "effective_to")
    list_filter = ("state", "facility_type", "status")
    search_fields = ("state__name", "state__code", "facility_type")


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("internal_reference", "payer_user", "payer_type", "amount", "currency", "status", "created_at")
    list_filter = ("payer_type", "status", "payment_provider", "created_at")
    search_fields = ("internal_reference", "provider_reference", "payer_user__email")
