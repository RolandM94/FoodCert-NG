from django.contrib import admin

from apps.facilities.models import FacilityAccreditationApplication, MedicalFacility


@admin.register(MedicalFacility)
class MedicalFacilityAdmin(admin.ModelAdmin):
    list_display = ("facility_name", "facility_type", "state", "accreditation_status", "accreditation_expiry_date")
    list_filter = ("facility_type", "ownership_type", "accreditation_status", "state")
    search_fields = ("facility_name", "license_number", "registration_number", "email", "phone")


@admin.register(FacilityAccreditationApplication)
class FacilityAccreditationApplicationAdmin(admin.ModelAdmin):
    list_display = ("facility", "application_status", "reviewer", "submitted_at", "reviewed_at")
    list_filter = ("application_status", "submitted_at", "reviewed_at")
    search_fields = ("facility__facility_name", "review_comment")
