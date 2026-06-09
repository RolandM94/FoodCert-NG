from django.contrib import admin

from apps.organizations.models import Organization, OrganizationMembership, OrganizationUnit, Permission, PermissionOverride, Role, RolePermission


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "organization_type", "status", "parent", "state", "lga", "email", "phone", "created_at")
    list_filter = ("organization_type", "status", "state")
    search_fields = ("name", "email", "phone", "contact_person_name")


@admin.register(OrganizationUnit)
class OrganizationUnitAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "unit_type", "status", "is_active", "parent", "manager", "created_at")
    list_filter = ("unit_type", "status", "is_active", "organization")
    search_fields = ("name", "organization__name", "email", "phone")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "organization_type", "status", "is_system_role", "is_custom_role")
    list_filter = ("organization_type", "status", "is_system_role", "is_custom_role")
    search_fields = ("name", "code")


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "module", "is_sensitive")
    list_filter = ("module", "is_sensitive")
    search_fields = ("code", "name", "module")


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "permission")
    list_filter = ("role", "permission__module")
    search_fields = ("role__code", "permission__code")


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "role", "unit", "unit_restricted", "status", "joined_at")
    list_filter = ("status", "organization", "role", "unit_restricted")
    search_fields = ("user__username", "user__email", "organization__name", "role__code")


@admin.register(PermissionOverride)
class PermissionOverrideAdmin(admin.ModelAdmin):
    list_display = ("membership", "permission", "effect", "granted_by", "expires_at")
    list_filter = ("effect", "permission__module", "expires_at")
    search_fields = ("membership__user__email", "permission__code", "reason")
