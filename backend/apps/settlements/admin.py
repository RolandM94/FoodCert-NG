from django.contrib import admin

from apps.settlements.models import Settlement


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ("facility", "state", "gross_amount", "facility_amount", "settlement_status", "settled_at")
    list_filter = ("settlement_status", "state", "created_at")
    search_fields = ("facility__facility_name", "settlement_reference")
