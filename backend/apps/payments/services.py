from decimal import Decimal
from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.facilities.models import MedicalFacility
from apps.payments.models import ActiveStatus, AssessmentFee, PayerType, PaymentStatus, PaymentTransaction
from apps.payments.providers import get_payment_provider


class PaymentService:
    @classmethod
    def _reference(cls, prefix):
        return f"{prefix}-{timezone.now():%Y%m%d}-{uuid4().hex[:10].upper()}"

    @classmethod
    def current_assessment_fee(cls, *, state, facility_type) -> AssessmentFee:
        today = timezone.localdate()
        return (
            AssessmentFee.objects.filter(
                state=state,
                facility_type=facility_type,
                status=ActiveStatus.ACTIVE,
                effective_from__lte=today,
            )
            .filter(effective_to__isnull=True)
            .order_by("-effective_from")
            .first()
            or AssessmentFee.objects.filter(
                state=state,
                facility_type=facility_type,
                status=ActiveStatus.ACTIVE,
                effective_from__lte=today,
                effective_to__gte=today,
            )
            .order_by("-effective_from")
            .first()
        )

    @classmethod
    @transaction.atomic
    def initiate_assessment_payment(cls, *, payer_user, facility: MedicalFacility, food_handler_id):
        if not facility.can_conduct_assessments:
            raise ValueError("FACILITY_NOT_ACCREDITED")
        fee = cls.current_assessment_fee(state=facility.state, facility_type=facility.facility_type)
        if not fee:
            raise ValueError("No active assessment fee is configured for this state and facility type.")

        reference = cls._reference("ASS")
        provider = get_payment_provider()
        transaction_obj = PaymentTransaction.objects.create(
            payer_user=payer_user,
            payer_type=PayerType.FOOD_HANDLER,
            related_entity_type="food_handler_assessment",
            related_entity_id=food_handler_id,
            amount=fee.amount,
            currency=fee.currency,
            payment_provider=provider.provider_name,
            internal_reference=reference,
            metadata={
                "facility_id": str(facility.id),
                "state_id": str(facility.state_id),
                "assessment_fee_id": str(fee.id),
                "state_fee": str(fee.state_fee),
                "facility_fee": str(fee.facility_fee),
                "platform_fee": str(fee.platform_fee),
            },
        )
        initialization = provider.initialize_payment(fee.amount, payer_user.email, reference, transaction_obj.metadata)
        transaction_obj.provider_reference = initialization.provider_reference
        transaction_obj.metadata = {**transaction_obj.metadata, "authorization_url": initialization.authorization_url}
        transaction_obj.save(update_fields=["provider_reference", "metadata", "updated_at"])
        log_action(action=AuditAction.PAYMENT_EVENT, actor=payer_user, target=transaction_obj, metadata={"event": "payment_initialized"})
        return transaction_obj

    @classmethod
    @transaction.atomic
    def initiate_subscription_payment(cls, *, payer_user, employer, plan, billing_cycle):
        amount = plan.price_yearly if billing_cycle == "yearly" else plan.price_monthly
        reference = cls._reference("SUB")
        provider = get_payment_provider()
        transaction_obj = PaymentTransaction.objects.create(
            payer_user=payer_user,
            payer_type=PayerType.EMPLOYER,
            related_entity_type="employer_subscription",
            related_entity_id=employer.id,
            amount=amount,
            currency="NGN",
            payment_provider=provider.provider_name,
            internal_reference=reference,
            metadata={"employer_id": str(employer.id), "plan_id": str(plan.id), "billing_cycle": billing_cycle},
        )
        initialization = provider.initialize_payment(amount, payer_user.email, reference, transaction_obj.metadata)
        transaction_obj.provider_reference = initialization.provider_reference
        transaction_obj.metadata = {**transaction_obj.metadata, "authorization_url": initialization.authorization_url}
        transaction_obj.save(update_fields=["provider_reference", "metadata", "updated_at"])
        log_action(action=AuditAction.PAYMENT_EVENT, actor=payer_user, target=transaction_obj, metadata={"event": "subscription_payment_initialized"})
        return transaction_obj

    @classmethod
    @transaction.atomic
    def verify_payment(cls, *, reference, actor=None):
        transaction_obj = PaymentTransaction.objects.select_for_update().get(internal_reference=reference)
        if transaction_obj.status == PaymentStatus.SUCCESS:
            log_action(
                action=AuditAction.PAYMENT_EVENT,
                actor=actor,
                target=transaction_obj,
                metadata={"event": "payment_verification_idempotent"},
            )
            return transaction_obj
        provider = get_payment_provider()
        verification = provider.verify_payment(reference)
        if verification.status == "success":
            transaction_obj.status = PaymentStatus.SUCCESS
            transaction_obj.paid_at = timezone.now()
            event = "payment_confirmed"
        else:
            transaction_obj.status = PaymentStatus.FAILED
            event = "payment_failed"
        transaction_obj.provider_reference = verification.provider_reference
        transaction_obj.metadata = {**transaction_obj.metadata, "verification": verification.metadata}
        transaction_obj.save(update_fields=["status", "paid_at", "provider_reference", "metadata", "updated_at"])
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=transaction_obj, metadata={"event": event})
        return transaction_obj

    @classmethod
    @transaction.atomic
    def mark_refunded(cls, *, transaction_obj, actor=None, amount=None):
        provider = get_payment_provider()
        refund = provider.refund_payment(transaction_obj.internal_reference, amount=amount)
        transaction_obj.status = PaymentStatus.REFUNDED
        transaction_obj.metadata = {**transaction_obj.metadata, "refund": refund}
        transaction_obj.save(update_fields=["status", "metadata", "updated_at"])
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=transaction_obj, metadata={"event": "refund_initiated"})
        return transaction_obj
