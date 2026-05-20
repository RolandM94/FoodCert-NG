from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class AuditAction(models.TextChoices):
    CREATE = "create", "Create"
    UPDATE = "update", "Update"
    DELETE = "delete", "Delete"
    LOGIN = "login", "Login"
    ROLE_CHANGE = "role_change", "Role Change"
    WORKFLOW_TRANSITION = "workflow_transition", "Workflow Transition"
    PAYMENT_EVENT = "payment_event", "Payment Event"
    MEDICAL_RECORD_ACCESS = "medical_record_access", "Medical Record Access"
    CERTIFICATE_EVENT = "certificate_event", "Certificate Event"
    PUBLIC_VERIFICATION = "public_verification", "Public Verification"
    SECURITY_EVENT = "security_event", "Security Event"


class AuditLog(BaseModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=64, choices=AuditAction.choices, db_index=True)
    target_type = models.CharField(max_length=120, blank=True)
    target_id = models.CharField(max_length=120, blank=True)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    state = models.ForeignKey(
        "locations.State",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["target_type", "target_id"]),
            models.Index(fields=["organization"]),
            models.Index(fields=["state"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.target_type}:{self.target_id}"
