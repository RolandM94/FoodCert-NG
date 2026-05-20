from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import User


@admin.register(User)
class FoodCertUserAdmin(UserAdmin):
    list_display = ("username", "email", "phone", "role", "status", "organization", "state", "is_active")
    list_filter = ("role", "status", "is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        (
            "FoodCert Access",
            {"fields": ("phone", "role", "status", "email_verified", "phone_verified", "organization", "state")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("FoodCert Access", {"fields": ("email", "phone", "role", "status", "organization", "state")}),
    )
