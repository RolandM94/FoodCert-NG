from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class NotificationChannel(models.TextChoices):
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"
    IN_APP = "in_app", "In App"


class NotificationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    DELIVERED = "delivered", "Delivered"
    FAILED = "failed", "Failed"
    READ = "read", "Read"


class NotificationType(models.TextChoices):
    CERTIFICATE_EXPIRY_REMINDER = "certificate_expiry_reminder", "Certificate Expiry Reminder"
    CERTIFICATE_RENEWAL = "certificate_renewal", "Certificate Renewal"
    VACCINATION_DUE = "vaccination_due", "Vaccination Due"
    ACCREDITATION_EXPIRY = "accreditation_expiry", "Accreditation Expiry"
    ILLNESS_REPORTED = "illness_reported", "Illness Reported"
    RETURN_TO_WORK_CLEARED = "return_to_work_cleared", "Return To Work Cleared"
    SUBSCRIPTION_EXPIRY = "subscription_expiry", "Subscription Expiry"
    SETTLEMENT_PROCESSED = "settlement_processed", "Settlement Processed"
    INSPECTION_ASSIGNED = "inspection_assigned", "Inspection Assigned"
    COMPLIANCE_NOTICE = "compliance_notice", "Compliance Notice"
    SYSTEM_ANNOUNCEMENT = "system_announcement", "System Announcement"
    OTHER = "other", "Other"


class Notification(BaseModel):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(
        max_length=64,
        choices=NotificationType.choices,
        default=NotificationType.OTHER,
        db_index=True,
    )
    channel = models.CharField(max_length=16, choices=NotificationChannel.choices, default=NotificationChannel.IN_APP)
    status = models.CharField(
        max_length=16,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        db_index=True,
    )
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    template_name = models.CharField(max_length=120, blank=True)
    context_data = models.JSONField(default=dict, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["recipient"]),
            models.Index(fields=["notification_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["channel"]),
            models.Index(fields=["created_at"]),
        ]
