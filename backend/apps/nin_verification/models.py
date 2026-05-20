from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class NINVerificationStatus(models.TextChoices):
    NOT_SUBMITTED = "not_submitted", "Not Submitted"
    PENDING_VERIFICATION = "pending_verification", "Pending Verification"
    VERIFIED = "verified", "Verified"
    FAILED = "failed", "Failed"
    MISMATCH = "mismatch", "Mismatch"
    MANUAL_REVIEW_REQUIRED = "manual_review_required", "Manual Review Required"
    OVERRIDE_APPROVED = "override_approved", "Override Approved"


class NINVerification(BaseModel):
    food_handler = models.ForeignKey(
        "food_handlers.FoodHandlerProfile",
        on_delete=models.CASCADE,
        related_name="nin_verifications",
    )
    nin = models.CharField(max_length=32)
    provider = models.CharField(max_length=64, default=settings.NIN_PROVIDER)
    provider_reference = models.CharField(max_length=120, blank=True)
    status = models.CharField(
        max_length=32,
        choices=NINVerificationStatus.choices,
        default=NINVerificationStatus.PENDING_VERIFICATION,
        db_index=True,
    )
    verified_full_name = models.CharField(max_length=255, blank=True)
    verified_date_of_birth = models.DateField(null=True, blank=True)
    verified_gender = models.CharField(max_length=16, blank=True)
    verified_photo_url = models.URLField(blank=True)
    match_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    mismatch_fields = models.JSONField(default=dict, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_nin_verifications",
    )
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["food_handler"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    @property
    def masked_nin(self) -> str:
        if not self.nin:
            return ""
        return f"{'*' * max(len(self.nin) - 4, 0)}{self.nin[-4:]}"
