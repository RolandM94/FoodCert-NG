from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


# ---- Choice Enums ----

class NotificationChannel(models.TextChoices):
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"
    IN_APP = "in_app", "In App"
    WHATSAPP = "whatsapp", "WhatsApp"


class NotificationCategory(models.TextChoices):
    ACCOUNT = "account", "Account"
    IDENTITY_VERIFICATION = "identity_verification", "Identity Verification"
    EMPLOYER_MANAGEMENT = "employer_management", "Employer Management"
    FACILITY_ACCREDITATION = "facility_accreditation", "Facility Accreditation"
    APPOINTMENT = "appointment", "Appointment"
    ASSESSMENT = "assessment", "Assessment"
    LAB_WORKFLOW = "lab_workflow", "Lab Workflow"
    VACCINATION = "vaccination", "Vaccination"
    CERTIFICATE = "certificate", "Certificate"
    RENEWAL = "renewal", "Renewal"
    PAYMENTS = "payments", "Payments"
    SUBSCRIPTIONS = "subscriptions", "Subscriptions"
    SETTLEMENTS = "settlements", "Settlements"
    INSPECTION = "inspection", "Inspection"
    ENFORCEMENT = "enforcement", "Enforcement"
    REPORTS = "reports", "Reports"
    M_AND_E = "m_and_e", "M&E"
    DATA_QUALITY = "data_quality", "Data Quality"
    SECURITY = "security", "Security"
    SYSTEM = "system", "System"


class NotificationPriority(models.TextChoices):
    LOW = "low", "Low"
    NORMAL = "normal", "Normal"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class DeliveryStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    QUEUED = "queued", "Queued"
    SENDING = "sending", "Sending"
    SENT = "sent", "Sent"
    DELIVERED = "delivered", "Delivered"
    FAILED = "failed", "Failed"
    BOUNCED = "bounced", "Bounced"
    REJECTED = "rejected", "Rejected"
    OPENED = "opened", "Opened"
    CLICKED = "clicked", "Clicked"
    READ = "read", "Read"
    CANCELLED = "cancelled", "Cancelled"


class TemplateStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING_APPROVAL = "pending_approval", "Pending Approval"
    ACTIVE = "active", "Active"
    ARCHIVED = "archived", "Archived"
    REJECTED = "rejected", "Rejected"


class TemplateScope(models.TextChoices):
    SYSTEM = "system", "System"
    NATIONAL = "national", "National"
    STATE = "state", "State"


class BroadcastStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING_APPROVAL = "pending_approval", "Pending Approval"
    APPROVED = "approved", "Approved"
    SENDING = "sending", "Sending"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


# Backward-compatibility aliases for existing code.
NotificationStatus = DeliveryStatus
NotificationType = NotificationCategory


# ---- Models ----

class Notification(BaseModel):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    recipient_email = models.EmailField(blank=True)
    recipient_phone = models.CharField(max_length=50, blank=True)
    recipient_type = models.CharField(max_length=50, blank=True)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    organization_unit = models.ForeignKey(
        "organizations.OrganizationUnit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    category = models.CharField(
        max_length=80,
        choices=NotificationCategory.choices,
        default=NotificationCategory.SYSTEM,
        db_index=True,
    )
    priority = models.CharField(
        max_length=50,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        db_index=True,
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    action_url = models.URLField(blank=True)
    related_object_type = models.CharField(max_length=100, blank=True)
    related_object_id = models.UUIDField(null=True, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["recipient"]),
            models.Index(fields=["category"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["is_read"]),
            models.Index(fields=["organization"]),
            models.Index(fields=["organization_unit"]),
            models.Index(fields=["related_object_type", "related_object_id"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class NotificationTemplate(BaseModel):
    template_key = models.CharField(max_length=150)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=80, choices=NotificationCategory.choices)
    channel = models.CharField(max_length=50, choices=NotificationChannel.choices)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    allowed_variables = models.JSONField(default=list)
    language = models.CharField(max_length=20, default="en")
    scope = models.CharField(max_length=50, choices=TemplateScope.choices, default=TemplateScope.SYSTEM)
    state = models.ForeignKey(
        "locations.State",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_templates",
    )
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=50,
        choices=TemplateStatus.choices,
        default=TemplateStatus.DRAFT,
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="notification_templates_created",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_templates_approved",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("template_key", "channel", "language", "version")
        indexes = [
            models.Index(fields=["template_key"]),
            models.Index(fields=["category"]),
            models.Index(fields=["channel"]),
            models.Index(fields=["status"]),
            models.Index(fields=["scope", "state"]),
        ]
        ordering = ["template_key", "-version"]

    def __str__(self) -> str:
        return f"{self.name} v{self.version} ({self.channel})"


class NotificationDelivery(BaseModel):
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    channel = models.CharField(max_length=50, choices=NotificationChannel.choices)
    provider = models.CharField(max_length=100, blank=True)
    destination = models.CharField(max_length=255)
    status = models.CharField(
        max_length=50,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
        db_index=True,
    )
    provider_message_id = models.CharField(max_length=255, blank=True)
    provider_response = models.JSONField(default=dict)
    error_code = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["notification"]),
            models.Index(fields=["channel"]),
            models.Index(fields=["status"]),
            models.Index(fields=["provider"]),
            models.Index(fields=["next_retry_at"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.notification.title} — {self.channel} ({self.status})"


class NotificationPreference(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    category = models.CharField(max_length=80, choices=NotificationCategory.choices)
    channel = models.CharField(max_length=50, choices=NotificationChannel.choices)
    is_enabled = models.BooleanField(default=True)
    digest_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "category", "channel")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["category"]),
            models.Index(fields=["channel"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} — {self.category}/{self.channel} (enabled={self.is_enabled})"


class NotificationProvider(BaseModel):
    name = models.CharField(max_length=100)
    channel = models.CharField(max_length=50, choices=NotificationChannel.choices)
    sender_id = models.CharField(max_length=100, blank=True)
    config = models.JSONField(default=dict)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    priority_order = models.PositiveIntegerField(default=1)
    rate_limit_per_minute = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["channel"]),
            models.Index(fields=["is_default"]),
            models.Index(fields=["is_active"]),
        ]
        ordering = ["priority_order", "name"]

    def __str__(self) -> str:
        default_tag = " [default]" if self.is_default else ""
        return f"{self.name} ({self.channel}){default_tag}"


class NotificationEvent(BaseModel):
    event_key = models.CharField(max_length=150, db_index=True)
    source_module = models.CharField(max_length=100)
    related_object_type = models.CharField(max_length=100, blank=True)
    related_object_id = models.UUIDField(null=True, blank=True)
    payload = models.JSONField(default=dict)
    processed = models.BooleanField(default=False, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["event_key"]),
            models.Index(fields=["source_module"]),
            models.Index(fields=["processed"]),
            models.Index(fields=["scheduled_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_key} (processed={self.processed})"


class BroadcastMessage(BaseModel):
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=80, choices=NotificationCategory.choices)
    priority = models.CharField(
        max_length=50,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
    )
    audience_type = models.CharField(max_length=100)
    audience_filters = models.JSONField(default=dict)
    channels = models.JSONField(default=list)
    status = models.CharField(
        max_length=50,
        choices=BroadcastStatus.choices,
        default=BroadcastStatus.DRAFT,
        db_index=True,
    )
    estimated_recipient_count = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="broadcasts_created",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="broadcasts_approved",
    )
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
