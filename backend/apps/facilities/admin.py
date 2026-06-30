from django.contrib import admin

from apps.facilities.models import (
    FacilityAccreditationApplication,
    FacilityDocument,
    FacilityInvitation,
    FacilityProfessionalProfile,
    FacilityRole,
    FacilityRolePermission,
    FacilityStaffProfile,
    MedicalFacility,
)


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
    list_display = ("user", "facility", "staff_type", "professional_category", "status", "department", "is_active")
    list_filter = ("staff_type", "professional_category", "status", "is_active", "facility")
    search_fields = ("user__email", "user__first_name", "user__last_name", "professional_registration_number")


@admin.register(FacilityRole)
class FacilityRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "facility", "organization_role", "is_system_default", "is_custom", "created_by")
    list_filter = ("facility", "is_system_default", "is_custom")
    search_fields = ("name", "description", "facility__facility_name")


@admin.register(FacilityRolePermission)
class FacilityRolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "permission_key", "allowed")
    list_filter = ("allowed", "role__facility")
    search_fields = ("role__name", "permission_key")


@admin.register(FacilityInvitation)
class FacilityInvitationAdmin(admin.ModelAdmin):
    list_display = ("facility", "invite", "role", "professional_category", "status", "created_at")
    list_filter = ("facility", "professional_category", "status")
    search_fields = ("invite__email", "facility__facility_name", "role__name")


@admin.register(FacilityProfessionalProfile)
class FacilityProfessionalProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "facility", "professional_category", "license_number", "verification_status")
    list_filter = ("facility", "professional_category", "verification_status")
    search_fields = ("user__email", "user__first_name", "user__last_name", "license_number", "license_issuing_body")
