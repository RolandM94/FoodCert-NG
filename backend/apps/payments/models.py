from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


class ActiveStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"


class PayerType(models.TextChoices):
    FOOD_HANDLER = "food_handler", "Food Handler"
    EMPLOYER = "employer", "Employer"
    FACILITY = "facility", "Facility"
    PLATFORM = "platform", "Platform"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"
    REFUNDED = "refunded", "Refunded"


class AssessmentFee(BaseModel):
    state = models.ForeignKey("locations.State", on_delete=models.PROTECT, related_name="assessment_fees")
    facility_type = models.CharField(max_length=32)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="NGN")
    state_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    facility_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    platform_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=ActiveStatus.choices, default=ActiveStatus.ACTIVE, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_assessment_fees",
    )

    class Meta:
        ordering = ["-effective_from"]
        indexes = [
            models.Index(fields=["state"]),
            models.Index(fields=["facility_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["effective_from", "effective_to"]),
        ]

    def __str__(self) -> str:
        return f"{self.state.code} {self.facility_type} {self.amount} {self.currency}"

    @property
    def is_current(self) -> bool:
        today = timezone.localdate()
        return self.status == ActiveStatus.ACTIVE and self.effective_from <= today and (
            self.effective_to is None or self.effective_to >= today
        )


class PaymentTransaction(BaseModel):
    payer_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payment_transactions",
    )
    payer_type = models.CharField(max_length=32, choices=PayerType.choices)
    related_entity_type = models.CharField(max_length=120)
    related_entity_id = models.UUIDField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="NGN")
    payment_provider = models.CharField(max_length=64)
    provider_reference = models.CharField(max_length=160, blank=True)
    internal_reference = models.CharField(max_length=80, unique=True, db_index=True)
    status = models.CharField(max_length=16, choices=PaymentStatus.choices, default=PaymentStatus.PENDING, db_index=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["payer_user"]),
            models.Index(fields=["payer_type"]),
            models.Index(fields=["related_entity_type", "related_entity_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.internal_reference} - {self.status}"
