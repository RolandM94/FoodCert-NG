from django.contrib import admin

from apps.lab_tests.models import LabTest


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ("assessment", "test_type", "status", "requested_by", "reviewed_by", "created_at")
    list_filter = ("test_type", "status", "created_at")
    search_fields = ("assessment__food_handler__full_name", "test_name")
