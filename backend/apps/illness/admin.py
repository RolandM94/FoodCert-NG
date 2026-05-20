from django.contrib import admin

from apps.illness.models import IllnessReport


@admin.register(IllnessReport)
class IllnessReportAdmin(admin.ModelAdmin):
    list_display = ("food_handler", "employer", "suspected_condition", "clearance_status", "earliest_return_date", "reviewed_by_doctor")
    list_filter = ("clearance_status", "suspected_condition", "clearance_required", "created_at")
    search_fields = ("food_handler__full_name", "employer__business_name", "return_to_work_certificate_number")
