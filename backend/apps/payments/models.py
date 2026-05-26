from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


class ActiveStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING_APPROVAL = "pending_approval", "Pending Approval"
    ACTIVE = "active", "Active"
    SCHEDULED = "scheduled", "Scheduled"
    EXPIRED = "expired", "Expired"
    SUSPENDED = "suspended", "Suspended"
    REPLACED = "replaced", "Replaced"
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


class PaymentAllocationStatus(models.TextChoices):
    ALLOCATED = "allocated", "Allocated"
    HELD = "held", "Held"
    REFUNDED = "refunded", "Refunded"
    PARTIALLY_REFUNDED = "partially_refunded", "Partially Refunded"
    DISPUTED = "disputed", "Disputed"


class RefundStatus(models.TextChoices):
    REQUESTED = "requested", "Requested"
    UNDER_REVIEW = "under_review", "Under Review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    PROCESSING = "processing", "Processing"
    REFUNDED = "refunded", "Refunded"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class LedgerEntryType(models.TextChoices):
    COLLECTION = "collection", "Collection"
    FACILITY_PAYABLE = "facility_payable", "Facility Payable"
    STATE_REVENUE = "state_revenue", "State Revenue"
    PLATFORM_REVENUE = "platform_revenue", "Platform Revenue"
    PROVIDER_FEE = "provider_fee", "Provider Fee"
    REFUND = "refund", "Refund"
    REVERSAL = "reversal", "Reversal"


class ProviderEnvironment(models.TextChoices):
    TEST = "test", "Test"
    LIVE = "live", "Live"


class WebhookProcessingStatus(models.TextChoices):
    RECEIVED = "received", "Received"
    PROCESSED = "processed", "Processed"
    DUPLICATE = "duplicate", "Duplicate"
    REJECTED = "rejected", "Rejected"
    FAILED = "failed", "Failed"


class ReconciliationStatus(models.TextChoices):
    MATCHED = "matched", "Matched"
    MISSING_INTERNAL = "missing_internal", "Missing Internal"
    MISSING_PROVIDER = "missing_provider", "Missing Provider"
    AMOUNT_MISMATCH = "amount_mismatch", "Amount Mismatch"
    CURRENCY_MISMATCH = "currency_mismatch", "Currency Mismatch"
    DUPLICATE_PROVIDER_REFERENCE = "duplicate_provider_reference", "Duplicate Provider Reference"
    MANUALLY_RESOLVED = "manually_resolved", "Manually Resolved"


class PaymentProvider(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    environment = models.CharField(max_length=20, choices=ProviderEnvironment.choices, default=ProviderEnvironment.TEST)
    public_key = models.CharField(max_length=255, blank=True)
    encrypted_secret_key = models.TextField(blank=True)
    webhook_secret = models.TextField(blank=True)
    callback_url = models.URLField(blank=True)
    webhook_url = models.URLField(blank=True)
    supported_methods = models.JSONField(default=list, blank=True)
    supports_refunds = models.BooleanField(default=False)
    supports_transfers = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_payment_providers",
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["environment"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class AssessmentFee(BaseModel):
    state = models.ForeignKey("locations.State", on_delete=models.PROTECT, related_name="assessment_fees")
    facility_type = models.CharField(max_length=32)
    fee_name = models.CharField(max_length=255, default="Assessment fee")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="NGN")
    state_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    facility_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    platform_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    provider_fee_handling = models.CharField(max_length=50, default="deduct_from_platform")
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=24, choices=ActiveStatus.choices, default=ActiveStatus.ACTIVE, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_assessment_fees",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_assessment_fees",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

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


class Receipt(BaseModel):
    receipt_number = models.CharField(max_length=100, unique=True, db_index=True)
    payment_transaction = models.OneToOneField(PaymentTransaction, on_delete=models.PROTECT, related_name="receipt")
    payer_name = models.CharField(max_length=255)
    payer_email = models.EmailField(blank=True)
    payer_type = models.CharField(max_length=32, choices=PayerType.choices)
    payment_purpose = models.CharField(max_length=80)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="NGN")
    payment_method = models.CharField(max_length=50, blank=True)
    provider_reference = models.CharField(max_length=160, blank=True)
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.SET_NULL, null=True, blank=True, related_name="payment_receipts")
    state = models.ForeignKey("locations.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="payment_receipts")
    line_items = models.JSONField(default=list, blank=True)
    issued_at = models.DateTimeField(default=timezone.now, db_index=True)
    receipt_url = models.URLField(blank=True)

    class Meta:
        ordering = ["-issued_at"]
        indexes = [
            models.Index(fields=["receipt_number"]),
            models.Index(fields=["payer_type"]),
            models.Index(fields=["payment_purpose"]),
            models.Index(fields=["issued_at"]),
        ]

    def __str__(self) -> str:
        return self.receipt_number


class PaymentAllocation(BaseModel):
    payment_transaction = models.ForeignKey(PaymentTransaction, on_delete=models.PROTECT, related_name="allocations")
    assessment = models.ForeignKey(
        "assessments.MedicalAssessment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_allocations",
    )
    fee_schedule = models.ForeignKey(AssessmentFee, on_delete=models.PROTECT, related_name="payment_allocations")
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.PROTECT, related_name="payment_allocations")
    state = models.ForeignKey("locations.State", on_delete=models.PROTECT, related_name="payment_allocations")
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    facility_amount = models.DecimalField(max_digits=12, decimal_places=2)
    state_amount = models.DecimalField(max_digits=12, decimal_places=2)
    platform_amount = models.DecimalField(max_digits=12, decimal_places=2)
    provider_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=32, choices=PaymentAllocationStatus.choices, default=PaymentAllocationStatus.ALLOCATED, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["payment_transaction", "assessment"], name="unique_payment_assessment_allocation"),
        ]
        indexes = [
            models.Index(fields=["payment_transaction"]),
            models.Index(fields=["assessment"]),
            models.Index(fields=["fee_schedule"]),
            models.Index(fields=["facility"]),
            models.Index(fields=["state"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.payment_transaction.internal_reference} allocation"


class PaymentLedgerEntry(BaseModel):
    payment_transaction = models.ForeignKey(PaymentTransaction, on_delete=models.PROTECT, related_name="ledger_entries")
    allocation = models.ForeignKey(PaymentAllocation, on_delete=models.PROTECT, null=True, blank=True, related_name="ledger_entries")
    entry_type = models.CharField(max_length=32, choices=LedgerEntryType.choices, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="NGN")
    direction = models.CharField(max_length=8, choices=[("debit", "Debit"), ("credit", "Credit")])
    account = models.CharField(max_length=80, db_index=True)
    reference = models.CharField(max_length=120, unique=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(fields=["payment_transaction"]),
            models.Index(fields=["allocation"]),
            models.Index(fields=["entry_type"]),
            models.Index(fields=["account"]),
            models.Index(fields=["created_at"]),
        ]

    def save(self, *args, **kwargs):
        if self.pk and PaymentLedgerEntry.objects.filter(pk=self.pk).exists():
            raise ValueError("Ledger entries are immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Ledger entries cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.reference} {self.entry_type}"


class RefundRequest(BaseModel):
    payment_transaction = models.ForeignKey(PaymentTransaction, on_delete=models.PROTECT, related_name="refund_requests")
    payment_allocation = models.ForeignKey(
        PaymentAllocation,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="refund_requests",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refunds_requested",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refunds_approved",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    review_notes = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=RefundStatus.choices, default=RefundStatus.REQUESTED, db_index=True)
    provider_refund_reference = models.CharField(max_length=255, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["payment_transaction"]),
            models.Index(fields=["requested_by"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.payment_transaction.internal_reference} refund {self.status}"


class PaymentWebhookEvent(BaseModel):
    provider = models.ForeignKey(
        PaymentProvider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="webhook_events",
    )
    provider_code = models.CharField(max_length=50, blank=True, db_index=True)
    event_type = models.CharField(max_length=100, blank=True, db_index=True)
    provider_reference = models.CharField(max_length=255, blank=True, db_index=True)
    idempotency_key = models.CharField(max_length=128, unique=True, null=True, blank=True, db_index=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    signature_valid = models.BooleanField(default=False)
    processing_status = models.CharField(
        max_length=24,
        choices=WebhookProcessingStatus.choices,
        default=WebhookProcessingStatus.RECEIVED,
        db_index=True,
    )
    processing_message = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["provider_code"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["provider_reference"]),
            models.Index(fields=["processing_status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.provider_code or 'unknown'} {self.event_type or 'event'} {self.processing_status}"


class PaymentReconciliationRecord(BaseModel):
    provider_code = models.CharField(max_length=64, db_index=True)
    provider_reference = models.CharField(max_length=255, db_index=True)
    internal_reference = models.CharField(max_length=120, blank=True, db_index=True)
    payment_transaction = models.ForeignKey(
        PaymentTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reconciliation_records",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="NGN")
    status = models.CharField(max_length=40, choices=ReconciliationStatus.choices, db_index=True)
    provider_payload = models.JSONField(default=dict, blank=True)
    matched_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_payment_reconciliations",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["provider_code", "status"]),
            models.Index(fields=["provider_code", "provider_reference"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.provider_code} {self.provider_reference} {self.status}"
