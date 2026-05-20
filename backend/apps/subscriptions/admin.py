from django.contrib import admin

from apps.subscriptions.models import EmployerSubscription, EmployerSubscriptionPlan


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
