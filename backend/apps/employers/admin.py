from django.contrib import admin

from apps.employers.models import Employer


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ("business_name", "establishment_category", "state", "compliance_status", "subscription_status")
    list_filter = ("establishment_category", "compliance_status", "subscription_status", "state")
    search_fields = ("business_name", "business_registration_number", "contact_person_email")
