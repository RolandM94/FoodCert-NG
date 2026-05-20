from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class NationalPolicyConfig(BaseModel):
    certificate_validity_months = models.PositiveIntegerField(default=settings.DEFAULT_CERTIFICATE_VALIDITY_MONTHS)
    renewal_reminder_days = models.JSONField(default=list)
    typhoid_validity_years = models.PositiveIntegerField(default=settings.DEFAULT_TYPHOID_VALIDITY_YEARS)
    hepatitis_a_second_dose_months = models.PositiveIntegerField(default=settings.DEFAULT_HEPATITIS_A_SECOND_DOSE_MONTHS)
    nin_required = models.BooleanField(default=True)
    payment_before_assessment_required = models.BooleanField(default=True)
    state_validation_before_certificate_required = models.BooleanField(default=True)
    public_qr_verification_enabled = models.BooleanField(default=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_national_policy_configs",
    )

    def save(self, *args, **kwargs):
        if not self.renewal_reminder_days:
            self.renewal_reminder_days = [30, 7]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return "National policy configuration"


class StatePolicyConfig(BaseModel):
    state = models.OneToOneField("locations.State", on_delete=models.CASCADE, related_name="policy_config")
    requires_state_certificate_validation = models.BooleanField(default=True)
    certificate_validity_months = models.PositiveIntegerField(default=settings.DEFAULT_CERTIFICATE_VALIDITY_MONTHS)
    typhoid_validity_years = models.PositiveIntegerField(default=settings.DEFAULT_TYPHOID_VALIDITY_YEARS)
    hepatitis_a_second_dose_months = models.PositiveIntegerField(default=settings.DEFAULT_HEPATITIS_A_SECOND_DOSE_MONTHS)
    auto_renewal_reminder_days = models.JSONField(default=list)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_state_policy_configs",
    )

    class Meta:
        indexes = [models.Index(fields=["state"])]

    def save(self, *args, **kwargs):
        if not self.auto_renewal_reminder_days:
            self.auto_renewal_reminder_days = [30, 7]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.state.name} policy"
