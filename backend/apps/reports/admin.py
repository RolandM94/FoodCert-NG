from django.contrib import admin

from apps.reports.models import (
    AnalyticsDataset,
    AnalyticsWidget,
    AnalyticsWorksheet,
    DashboardCanvas,
    DashboardCanvasBlock,
    DashboardTemplate,
    DashboardWidget,
    DataQualityIssue,
    GeneratedReport,
    MEIndicator,
    MEIndicatorValue,
    PublishedDashboard,
    ReportSchedule,
    ReportTemplate,
    ScheduledReport,
)


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ("report_type", "frequency", "status", "created_by", "created_at")
    list_filter = ("report_type", "frequency", "status")
    search_fields = ("created_by__email",)


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ("name", "report_template", "owner", "schedule_frequency", "output_format", "is_active", "next_run_at", "last_run_at")
    list_filter = ("schedule_frequency", "output_format", "is_active", "report_template__scope")
    search_fields = ("name", "report_template__code", "report_template__name", "owner__email", "recipients")
    readonly_fields = ("created_at", "updated_at", "last_run_at")
    ordering = ("next_run_at", "name")


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "scope", "module", "privacy_level", "is_active")
    list_filter = ("scope", "module", "privacy_level", "is_active")
    search_fields = ("code", "name", "description", "module")


@admin.register(MEIndicator)
class MEIndicatorAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "category", "reporting_frequency", "visualization_type", "is_active")
    list_filter = ("category", "reporting_frequency", "visualization_type", "is_active")
    search_fields = ("code", "name", "description", "formula")


@admin.register(MEIndicatorValue)
class MEIndicatorValueAdmin(admin.ModelAdmin):
    list_display = ("indicator", "state", "lga", "organization", "period_start", "period_end", "calculated_value", "calculated_at")
    list_filter = ("indicator__category", "state", "period_end")
    search_fields = ("indicator__code", "indicator__name", "organization__name")


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "dashboard_scope", "widget_type", "metric_code", "sort_order", "is_active")
    list_filter = ("dashboard_scope", "widget_type", "is_active")
    search_fields = ("code", "name", "metric_code")
    ordering = ("dashboard_scope", "sort_order", "name")


@admin.register(AnalyticsDataset)
class AnalyticsDatasetAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "module_source", "privacy_level", "is_active")
    list_filter = ("module_source", "privacy_level", "is_active")
    search_fields = ("code", "name", "description")


@admin.register(AnalyticsWorksheet)
class AnalyticsWorksheetAdmin(admin.ModelAdmin):
    list_display = ("name", "account_type", "dataset", "owner", "scope_type", "is_active", "is_template")
    list_filter = ("account_type", "scope_type", "is_active", "is_template")
    search_fields = ("name", "description", "dataset__code", "owner__email")


@admin.register(AnalyticsWidget)
class AnalyticsWidgetAdmin(admin.ModelAdmin):
    list_display = ("title", "account_type", "worksheet", "widget_type", "scope_type", "is_active")
    list_filter = ("account_type", "widget_type", "scope_type", "is_active")
    search_fields = ("title", "worksheet__name", "owner__email")


@admin.register(DashboardCanvas)
class DashboardCanvasAdmin(admin.ModelAdmin):
    list_display = ("name", "account_type", "owner", "scope_type", "is_draft", "is_active")
    list_filter = ("account_type", "scope_type", "is_draft", "is_active")
    search_fields = ("name", "description", "owner__email")


@admin.register(DashboardCanvasBlock)
class DashboardCanvasBlockAdmin(admin.ModelAdmin):
    list_display = ("canvas", "block_type", "title", "sort_order", "is_active")
    list_filter = ("block_type", "is_active")
    search_fields = ("canvas__name", "title")


@admin.register(PublishedDashboard)
class PublishedDashboardAdmin(admin.ModelAdmin):
    list_display = ("canvas", "version_label", "visibility_scope", "published_by", "published_at", "is_active")
    list_filter = ("visibility_scope", "is_active")
    search_fields = ("canvas__name", "version_label", "published_by__email")


@admin.register(DashboardTemplate)
class DashboardTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "account_type", "scope_type", "is_system_template", "is_active")
    list_filter = ("account_type", "scope_type", "is_system_template", "is_active")
    search_fields = ("name", "description", "created_by__email")


@admin.register(DataQualityIssue)
class DataQualityIssueAdmin(admin.ModelAdmin):
    list_display = ("issue_type", "severity", "module", "target_type", "state", "organization", "status", "assigned_to", "created_at")
    list_filter = ("severity", "status", "module", "target_type", "state")
    search_fields = ("issue_type", "description", "target_type", "target_id", "organization__name", "assigned_to__email")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ("report_type", "file_format", "status", "generated_by", "created_at")
    list_filter = ("report_type", "file_format", "status")
    search_fields = ("generated_by__email", "file_url")
