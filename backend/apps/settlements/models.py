from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


class SettlementStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class SettlementDisputeStatus(models.TextChoices):
    NONE = "none", "None"
    OPEN = "open", "Open"
    UNDER_REVIEW = "under_review", "Under Review"
    RESOLVED = "resolved", "Resolved"
    REJECTED = "rejected", "Rejected"


class Settlement(BaseModel):
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.PROTECT, related_name="settlements")
    state = models.ForeignKey("locations.State", on_delete=models.PROTECT, related_name="settlements")
    payment_transaction = models.ForeignKey("payments.PaymentTransaction", on_delete=models.PROTECT, related_name="settlements")
    assessment = models.ForeignKey(
        "assessments.MedicalAssessment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="settlements",
    )
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    facility_amount = models.DecimalField(max_digits=12, decimal_places=2)
    state_amount = models.DecimalField(max_digits=12, decimal_places=2)
    platform_amount = models.DecimalField(max_digits=12, decimal_places=2)
    settlement_status = models.CharField(
        max_length=16,
        choices=SettlementStatus.choices,
        default=SettlementStatus.PENDING,
        db_index=True,
    )
    settlement_reference = models.CharField(max_length=120, blank=True, db_index=True)
    settled_at = models.DateTimeField(null=True, blank=True)
    dispute_status = models.CharField(
        max_length=24,
        choices=SettlementDisputeStatus.choices,
        default=SettlementDisputeStatus.NONE,
        db_index=True,
    )
    dispute_reason = models.TextField(blank=True)
    disputed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="settlement_disputes",
    )
    disputed_at = models.DateTimeField(null=True, blank=True)
    dispute_resolution = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["facility"]),
            models.Index(fields=["state"]),
            models.Index(fields=["payment_transaction"]),
            models.Index(fields=["settlement_status"]),
            models.Index(fields=["dispute_status"], name="settlements_dispute_800255_idx"),
        ]

    def mark_paid(self, reference: str):
        self.settlement_status = SettlementStatus.PAID
        self.settlement_reference = reference
        self.settled_at = timezone.now()
        self.save(update_fields=["settlement_status", "settlement_reference", "settled_at", "updated_at"])
