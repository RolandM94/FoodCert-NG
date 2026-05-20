from datetime import timedelta

from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


class PlanStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"


class BillingCycle(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    YEARLY = "yearly", "Yearly"


class SubscriptionStatus(models.TextChoices):
    TRIAL = "trial", "Trial"
    ACTIVE = "active", "Active"
    PAST_DUE = "past_due", "Past Due"
    SUSPENDED = "suspended", "Suspended"
    CANCELLED = "cancelled", "Cancelled"
    EXPIRED = "expired", "Expired"


class EmployerSubscriptionPlan(BaseModel):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    max_food_handlers = models.PositiveIntegerField(default=0)
    max_locations = models.PositiveIntegerField(default=1)
    price_monthly = models.DecimalField(max_digits=12, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=12, decimal_places=2)
    features = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=PlanStatus.choices, default=PlanStatus.ACTIVE, db_index=True)

    class Meta:
        ordering = ["price_monthly", "name"]
        indexes = [models.Index(fields=["status"])]

    def __str__(self) -> str:
        return self.name


class EmployerSubscription(BaseModel):
    employer = models.ForeignKey("employers.Employer", on_delete=models.PROTECT, related_name="subscriptions")
    plan = models.ForeignKey(EmployerSubscriptionPlan, on_delete=models.PROTECT, related_name="subscriptions")
    billing_cycle = models.CharField(max_length=16, choices=BillingCycle.choices)
    status = models.CharField(max_length=16, choices=SubscriptionStatus.choices, default=SubscriptionStatus.ACTIVE, db_index=True)
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)
    last_payment_transaction = models.ForeignKey(
        "payments.PaymentTransaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employer_subscriptions",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["employer"]),
            models.Index(fields=["status"]),
            models.Index(fields=["expires_at"]),
        ]

    @property
    def is_active(self) -> bool:
        return self.status == SubscriptionStatus.ACTIVE and self.expires_at > timezone.now()

    @staticmethod
    def expiry_for_cycle(starts_at, billing_cycle):
        if billing_cycle == BillingCycle.YEARLY:
            return starts_at + timedelta(days=365)
        return starts_at + timedelta(days=30)
