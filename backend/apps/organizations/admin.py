from django.contrib import admin

from apps.organizations.models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "organization_type", "status", "state", "lga", "email", "phone", "created_at")
    list_filter = ("organization_type", "status", "state")
    search_fields = ("name", "email", "phone")
