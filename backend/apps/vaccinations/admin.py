from django.contrib import admin

from apps.vaccinations.models import VaccinationRecord


@admin.register(VaccinationRecord)
class VaccinationRecordAdmin(admin.ModelAdmin):
    list_display = ("food_handler", "vaccine_type", "dose_number", "status", "expiry_date", "recorded_by")
    list_filter = ("vaccine_type", "status", "expiry_date")
    search_fields = ("food_handler__full_name", "vaccine_name")
