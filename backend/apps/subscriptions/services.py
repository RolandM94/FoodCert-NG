from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.employers.models import SubscriptionStatus as EmployerSubscriptionStatus
from apps.payments.models import PaymentStatus
from apps.subscriptions.models import BillingCycle, EmployerSubscription, SubscriptionStatus


class EmployerSubscriptionService:
    @classmethod
    @transaction.atomic
    def activate(cls, *, employer, plan, billing_cycle, payment_transaction, actor=None):
        if payment_transaction.status != PaymentStatus.SUCCESS:
            raise ValueError("PAYMENT_REQUIRED")
        starts_at = timezone.now()
        EmployerSubscription.objects.filter(
            employer=employer,
            status__in=[SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE, SubscriptionStatus.PAST_DUE],
        ).update(status=SubscriptionStatus.CANCELLED, cancelled_at=starts_at, updated_at=starts_at)
        subscription = EmployerSubscription.objects.create(
            employer=employer,
            plan=plan,
            billing_cycle=billing_cycle,
            status=SubscriptionStatus.ACTIVE,
            starts_at=starts_at,
            expires_at=EmployerSubscription.expiry_for_cycle(starts_at, billing_cycle),
            last_payment_transaction=payment_transaction,
        )
        employer.subscription_status = EmployerSubscriptionStatus.ACTIVE
        employer.save(update_fields=["subscription_status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=actor, target=subscription, metadata={"event": "subscription_activated"})
        return subscription

    @classmethod
    @transaction.atomic
    def change_plan(cls, *, employer, plan, billing_cycle, payment_transaction, actor=None):
        subscription = cls.activate(
            employer=employer,
            plan=plan,
            billing_cycle=billing_cycle,
            payment_transaction=payment_transaction,
            actor=actor,
        )
        log_action(
            action=AuditAction.UPDATE,
            actor=actor,
            target=subscription,
            metadata={"event": "subscription_plan_changed", "plan_id": str(plan.id), "billing_cycle": billing_cycle},
        )
        return subscription

    @classmethod
    def current_for_employer(cls, employer):
        return (
            EmployerSubscription.objects.filter(employer=employer)
            .select_related("plan", "last_payment_transaction")
            .order_by("-created_at")
            .first()
        )

    @classmethod
    def has_capacity_for_new_handler(cls, employer):
        subscription = cls.current_for_employer(employer)
        if not subscription or not subscription.is_active:
            return employer.food_handlers.count() < 5
        return employer.food_handlers.count() < subscription.plan.max_food_handlers
