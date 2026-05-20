from django.contrib import admin

from apps.nin_verification.models import NINVerification


@admin.register(NINVerification)
class NINVerificationAdmin(admin.ModelAdmin):
    list_display = ("food_handler", "provider", "status", "match_score", "reviewed_by", "created_at")
    list_filter = ("provider", "status", "created_at")
    search_fields = ("food_handler__full_name", "provider_reference")
    exclude = ("nin",)
