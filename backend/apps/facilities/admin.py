from django.contrib import admin

from apps.facilities.models import FacilityAccreditationApplication, FacilityDocument, FacilityStaffProfile, MedicalFacility


@admin.register(MedicalFacility)
class MedicalFacilityAdmin(admin.ModelAdmin):
    list_display = ("facility_name", "facility_type", "state", "accreditation_status", "accreditation_expiry_date")
    list_filter = ("facility_type", "ownership_type", "accreditation_status", "state")
    search_fields = ("facility_name", "license_number", "registration_number", "email", "phone")


@admin.register(FacilityAccreditationApplication)
class FacilityAccreditationApplicationAdmin(admin.ModelAdmin):
    list_display = ("facility", "application_status", "is_renewal", "reviewer", "submitted_at", "reviewed_at")
    list_filter = ("application_status", "is_renewal", "submitted_at", "reviewed_at")
    search_fields = ("facility__facility_name", "review_comment")


@admin.register(FacilityDocument)
class FacilityDocumentAdmin(admin.ModelAdmin):
    list_display = ("facility", "document_type", "status", "uploaded_by", "created_at")
    list_filter = ("document_type", "status", "created_at")
    search_fields = ("facility__facility_name", "uploaded_by__email", "review_comment")


@admin.register(FacilityStaffProfile)
class FacilityStaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "facility", "staff_type", "department", "is_active")
    list_filter = ("staff_type", "is_active", "facility")
    search_fields = ("user__email", "user__first_name", "user__last_name", "professional_registration_number")
