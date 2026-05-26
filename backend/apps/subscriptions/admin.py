from django.contrib import admin

from apps.subscriptions.models import EmployerInvoice, EmployerSubscription, EmployerSubscriptionPlan


@admin.register(EmployerSubscriptionPlan)
class EmployerSubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price_monthly", "price_yearly", "max_food_handlers", "status")
    list_filter = ("status",)
    search_fields = ("name",)


@admin.register(EmployerSubscription)
class EmployerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("employer", "plan", "billing_cycle", "status", "starts_at", "expires_at")
    list_filter = ("billing_cycle", "status", "starts_at", "expires_at")
    search_fields = ("employer__business_name", "plan__name")


@admin.register(EmployerInvoice)
class EmployerInvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "employer", "amount_due", "amount_paid", "currency", "status", "due_date")
    list_filter = ("status", "currency", "due_date")
    search_fields = ("invoice_number", "employer__business_name", "payment_transaction__internal_reference")
