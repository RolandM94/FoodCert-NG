from django.contrib import admin

from apps.policy.models import StatePolicyConfig


@admin.register(StatePolicyConfig)
class StatePolicyConfigAdmin(admin.ModelAdmin):
    list_display = (
        "state",
        "requires_state_certificate_validation",
        "certificate_validity_months",
        "typhoid_validity_years",
        "updated_by",
    )
    list_filter = ("requires_state_certificate_validation", "state")
    search_fields = ("state__name", "state__code")
