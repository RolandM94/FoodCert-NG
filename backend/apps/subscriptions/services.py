from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.employers.models import SubscriptionStatus as EmployerSubscriptionStatus
from apps.payments.models import PaymentStatus
from apps.subscriptions.models import BillingCycle, EmployerInvoice, EmployerSubscription, InvoiceStatus, SubscriptionStatus


class EmployerSubscriptionService:
    GRACE_PERIOD_DAYS = 7
    RENEWAL_REMINDER_DAYS = 7

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
            grace_period_ends_at=None,
            auto_renew=True,
            last_payment_transaction=payment_transaction,
        )
        employer.subscription_status = EmployerSubscriptionStatus.ACTIVE
        employer.save(update_fields=["subscription_status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=actor, target=subscription, metadata={"event": "subscription_activated"})
        return subscription

    @classmethod
    @transaction.atomic
    def renew(cls, *, employer, payment_transaction, actor=None):
        current = cls.current_for_employer(employer)
        if not current:
            raise ValueError("NO_SUBSCRIPTION")
        return cls.activate(
            employer=employer,
            plan=current.plan,
            billing_cycle=current.billing_cycle,
            payment_transaction=payment_transaction,
            actor=actor,
        )

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
    @transaction.atomic
    def cancel(cls, *, employer, actor=None, reason=""):
        subscription = cls.current_for_employer(employer)
        if not subscription:
            raise ValueError("NO_SUBSCRIPTION")
        now = timezone.now()
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = now
        subscription.auto_renew = False
        subscription.cancellation_reason = reason
        subscription.save(update_fields=["status", "cancelled_at", "auto_renew", "cancellation_reason", "updated_at"])
        employer.subscription_status = EmployerSubscriptionStatus.CANCELLED
        employer.save(update_fields=["subscription_status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=actor, target=subscription, metadata={"event": "subscription_cancelled"})
        return subscription

    @classmethod
    @transaction.atomic
    def sync_lifecycle_status(cls, *, subscription, actor=None):
        now = timezone.now()
        if subscription.status == SubscriptionStatus.ACTIVE and subscription.expires_at <= now:
            subscription.status = SubscriptionStatus.PAST_DUE
            subscription.grace_period_ends_at = now + timedelta(days=cls.GRACE_PERIOD_DAYS)
            subscription.save(update_fields=["status", "grace_period_ends_at", "updated_at"])
            subscription.employer.subscription_status = EmployerSubscriptionStatus.EXPIRED
            subscription.employer.save(update_fields=["subscription_status", "updated_at"])
            log_action(action=AuditAction.UPDATE, actor=actor, target=subscription, metadata={"event": "subscription_past_due"})
        if (
            subscription.status == SubscriptionStatus.PAST_DUE
            and subscription.grace_period_ends_at
            and subscription.grace_period_ends_at <= now
        ):
            subscription.status = SubscriptionStatus.EXPIRED
            subscription.save(update_fields=["status", "updated_at"])
            subscription.employer.subscription_status = EmployerSubscriptionStatus.EXPIRED
            subscription.employer.save(update_fields=["subscription_status", "updated_at"])
            log_action(action=AuditAction.UPDATE, actor=actor, target=subscription, metadata={"event": "subscription_expired"})
        return subscription

    @classmethod
    def sync_due_lifecycle_statuses(cls):
        subscriptions = EmployerSubscription.objects.select_related("employer", "plan").filter(
            status__in=[SubscriptionStatus.ACTIVE, SubscriptionStatus.PAST_DUE],
            expires_at__lte=timezone.now(),
        )
        count = 0
        for subscription in subscriptions:
            before = subscription.status
            cls.sync_lifecycle_status(subscription=subscription)
            count += int(before != subscription.status)
        return count

    @classmethod
    def renewal_reminders_due(cls):
        now = timezone.now()
        return EmployerSubscription.objects.select_related("employer", "plan").filter(
            status=SubscriptionStatus.ACTIVE,
            auto_renew=True,
            renewal_reminder_sent_at__isnull=True,
            expires_at__gt=now,
            expires_at__lte=now + timedelta(days=cls.RENEWAL_REMINDER_DAYS),
        )

    @classmethod
    @transaction.atomic
    def mark_renewal_reminder_sent(cls, *, subscription, actor=None):
        subscription.renewal_reminder_sent_at = timezone.now()
        subscription.save(update_fields=["renewal_reminder_sent_at", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=actor, target=subscription, metadata={"event": "subscription_renewal_reminder_sent"})
        return subscription

    @classmethod
    def current_for_employer(cls, employer):
        subscription = (
            EmployerSubscription.objects.filter(employer=employer)
            .select_related("plan", "last_payment_transaction")
            .order_by("-created_at")
            .first()
        )
        if subscription:
            subscription = cls.sync_lifecycle_status(subscription=subscription)
        return subscription

    @classmethod
    def entitlements_for_employer(cls, employer):
        subscription = cls.current_for_employer(employer)
        active = bool(subscription and subscription.is_active)
        plan = subscription.plan if subscription else None
        return {
            "regulatory_access": True,
            "premium_features_active": active,
            "subscription_status": subscription.status if subscription else "none",
            "plan_id": str(plan.id) if plan else None,
            "plan_name": plan.name if plan else None,
            "limits": {
                "max_food_handlers": plan.max_food_handlers if active and plan else 5,
                "max_locations": plan.max_locations if active and plan else 1,
                "max_users": plan.max_users if active and plan else 1,
            },
            "features": plan.features if active and plan else {},
            "restricted_features": [] if active else ["premium_reports", "bulk_exports", "advanced_branch_analytics"],
        }

    @classmethod
    def has_capacity_for_new_handler(cls, employer):
        entitlements = cls.entitlements_for_employer(employer)
        return employer.food_handlers.count() < entitlements["limits"]["max_food_handlers"]


class EmployerInvoiceService:
    @classmethod
    def _invoice_number(cls, *, employer):
        return f"INV-{timezone.now():%Y%m%d}-{str(employer.id).split('-')[0].upper()}-{timezone.now():%H%M%S%f}"

    @classmethod
    def amount_for_plan(cls, *, plan, billing_cycle):
        return plan.price_yearly if billing_cycle == BillingCycle.YEARLY else plan.price_monthly

    @classmethod
    @transaction.atomic
    def create_for_subscription_checkout(cls, *, employer, plan, billing_cycle, payment_transaction, actor=None):
        amount = cls.amount_for_plan(plan=plan, billing_cycle=billing_cycle)
        due_date = timezone.localdate() + timedelta(days=7)
        invoice, created = EmployerInvoice.objects.get_or_create(
            payment_transaction=payment_transaction,
            defaults={
                "invoice_number": cls._invoice_number(employer=employer),
                "employer": employer,
                "description": f"{plan.name} employer subscription ({billing_cycle})",
                "line_items": [
                    {
                        "description": f"{plan.name} subscription",
                        "billing_cycle": billing_cycle,
                        "quantity": 1,
                        "unit_amount": str(amount),
                        "amount": str(amount),
                    }
                ],
                "amount_due": amount,
                "currency": getattr(plan, "currency", "NGN"),
                "due_date": due_date,
            },
        )
        if created:
            log_action(action=AuditAction.CREATE, actor=actor, target=invoice, metadata={"event": "employer_invoice_issued"})
        return invoice

    @classmethod
    @transaction.atomic
    def mark_paid(cls, *, invoice, subscription=None, actor=None):
        if invoice.status == InvoiceStatus.PAID:
            return invoice
        now = timezone.now()
        invoice.status = InvoiceStatus.PAID
        invoice.amount_paid = invoice.amount_due
        invoice.paid_at = now
        if subscription:
            invoice.subscription = subscription
        invoice.save(update_fields=["status", "amount_paid", "paid_at", "subscription", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=actor, target=invoice, metadata={"event": "employer_invoice_paid"})
        return invoice
