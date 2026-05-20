from django.contrib import admin

from apps.reports.models import GeneratedReport, ReportSchedule


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ("report_type", "frequency", "status", "created_by", "created_at")
    list_filter = ("report_type", "frequency", "status")
    search_fields = ("created_by__email",)


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ("report_type", "file_format", "status", "generated_by", "created_at")
    list_filter = ("report_type", "file_format", "status")
    search_fields = ("generated_by__email", "file_url")
