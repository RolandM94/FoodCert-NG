from django.contrib import admin

from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "target_type", "target_id", "state", "created_at")
    list_filter = ("action", "state", "created_at")
    search_fields = ("target_type", "target_id", "actor__username", "actor__email")
    readonly_fields = ("created_at", "updated_at")
