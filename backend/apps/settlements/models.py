from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.common.models import BaseModel


class SettlementStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    HELD = "held", "Held"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class SettlementDisputeStatus(models.TextChoices):
    NONE = "none", "None"
    OPEN = "open", "Open"
    UNDER_REVIEW = "under_review", "Under Review"
    RESOLVED = "resolved", "Resolved"
    REJECTED = "rejected", "Rejected"


class SettlementBatchStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    APPROVED = "approved", "Approved"
    PROCESSING = "processing", "Processing"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class SettlementBatch(BaseModel):
    batch_reference = models.CharField(max_length=120, unique=True, db_index=True)
    status = models.CharField(max_length=16, choices=SettlementBatchStatus.choices, default=SettlementBatchStatus.DRAFT, db_index=True)
    settlement_count = models.PositiveIntegerField(default=0)
    gross_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    facility_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    state_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    platform_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="created_settlement_batches")
    approved_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_settlement_batches")
    processed_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="processed_settlement_batches")
    approved_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    payout_reference = models.CharField(max_length=160, blank=True)
    failure_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return self.batch_reference


class Settlement(BaseModel):
    batch = models.ForeignKey(SettlementBatch, on_delete=models.SET_NULL, null=True, blank=True, related_name="settlements")
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.PROTECT, related_name="settlements")
    state = models.ForeignKey("locations.State", on_delete=models.PROTECT, related_name="settlements")
    payment_transaction = models.ForeignKey("payments.PaymentTransaction", on_delete=models.PROTECT, related_name="settlements")
    payment_allocation = models.OneToOneField(
        "payments.PaymentAllocation",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="settlement",
    )
    fee_schedule = models.ForeignKey(
        "payments.AssessmentFee",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="settlements",
    )
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
    eligibility_checked_at = models.DateTimeField(null=True, blank=True)
    eligibility_reason = models.TextField(blank=True)
    settlement_status = models.CharField(
        max_length=16,
        choices=SettlementStatus.choices,
        default=SettlementStatus.PENDING,
        db_index=True,
    )
    settlement_reference = models.CharField(max_length=120, blank=True, db_index=True)
    settled_at = models.DateTimeField(null=True, blank=True)
    payout_attempts = models.PositiveIntegerField(default=0)
    last_payout_error = models.TextField(blank=True)
    held_at = models.DateTimeField(null=True, blank=True)
    hold_reason = models.TextField(blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
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
            models.Index(fields=["batch"]),
            models.Index(fields=["state"]),
            models.Index(fields=["payment_transaction"]),
            models.Index(fields=["payment_allocation"]),
            models.Index(fields=["fee_schedule"]),
            models.Index(fields=["settlement_status"]),
            models.Index(fields=["dispute_status"], name="settlements_dispute_800255_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["payment_transaction", "assessment"],
                condition=Q(payment_allocation__isnull=True),
                name="unique_legacy_payment_assessment_settlement",
            ),
        ]

    def mark_paid(self, reference: str):
        self.settlement_status = SettlementStatus.PAID
        self.settlement_reference = reference
        self.settled_at = timezone.now()
        self.save(update_fields=["settlement_status", "settlement_reference", "settled_at", "updated_at"])
