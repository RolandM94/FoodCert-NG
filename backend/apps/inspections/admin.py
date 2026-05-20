from django.contrib import admin

from apps.inspections.models import Inspection, InspectionCertificateScan


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ("employer", "inspector", "inspection_date", "compliance_score", "enforcement_action", "status")
    list_filter = ("status", "enforcement_action", "inspection_date")
    search_fields = ("employer__business_name", "inspector__email")


@admin.register(InspectionCertificateScan)
class InspectionCertificateScanAdmin(admin.ModelAdmin):
    list_display = ("inspection", "certificate_number", "result", "scanned_at")
    list_filter = ("result", "scanned_at")
    search_fields = ("certificate_number",)
