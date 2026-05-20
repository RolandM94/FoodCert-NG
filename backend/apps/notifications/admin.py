from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "notification_type", "channel", "status", "subject", "created_at")
    list_filter = ("notification_type", "channel", "status", "created_at")
    search_fields = ("recipient__username", "recipient__email", "subject")
