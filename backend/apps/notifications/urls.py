from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.notifications.views import (
    BroadcastViewSet,
    DashboardStatsView,
    EmailWebhookView,
    InternalEventView,
    InternalScheduleView,
    InternalSendTemplateView,
    InternalSendView,
    NotificationDeliveryViewSet,
    NotificationPreferenceViewSet,
    NotificationProviderViewSet,
    NotificationTemplateViewSet,
    NotificationViewSet,
    SMSWebhookView,
    WhatsAppWebhookView,
)

router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename="notifications")
router.register("notification-preferences", NotificationPreferenceViewSet, basename="notification-preferences")
router.register("admin/notification-templates", NotificationTemplateViewSet, basename="notification-templates")
router.register("admin/notification-providers", NotificationProviderViewSet, basename="notification-providers")
router.register("admin/notification-deliveries", NotificationDeliveryViewSet, basename="notification-deliveries")
router.register("admin/broadcasts", BroadcastViewSet, basename="notification-broadcasts")

urlpatterns = router.urls + [
    path("internal/notifications/events", InternalEventView.as_view(), name="internal-notification-event"),
    path("internal/notifications/send", InternalSendView.as_view(), name="internal-notification-send"),
    path("internal/notifications/send-template", InternalSendTemplateView.as_view(), name="internal-notification-send-template"),
    path("internal/notifications/schedule", InternalScheduleView.as_view(), name="internal-notification-schedule"),
    path("webhooks/email-provider", EmailWebhookView.as_view(), name="webhook-email-provider"),
    path("webhooks/sms-provider", SMSWebhookView.as_view(), name="webhook-sms-provider"),
    path("webhooks/whatsapp-provider", WhatsAppWebhookView.as_view(), name="webhook-whatsapp-provider"),
    path("admin/notifications/dashboard", DashboardStatsView.as_view(), name="notification-dashboard"),
]
