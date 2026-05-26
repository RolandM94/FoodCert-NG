from django.contrib import admin

from apps.inspections.models import Inspection, InspectionCertificateScan, InspectionChecklistItem


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ("reference", "employer", "inspector", "inspection_type", "priority", "inspection_date", "compliance_score", "enforcement_action", "status")
    list_filter = ("status", "enforcement_action", "inspection_type", "priority", "inspection_date")
    search_fields = ("reference", "employer__business_name", "inspector__email")


@admin.register(InspectionCertificateScan)
class InspectionCertificateScanAdmin(admin.ModelAdmin):
    list_display = ("inspection", "certificate_number", "result", "scanned_at")
    list_filter = ("result", "scanned_at")
    search_fields = ("certificate_number",)


@admin.register(InspectionChecklistItem)
class InspectionChecklistItemAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "severity_if_failed", "is_active", "sort_order")
    list_filter = ("category", "severity_if_failed", "is_active")
    list_editable = ("is_active", "sort_order", "severity_if_failed")
    search_fields = ("question",)
