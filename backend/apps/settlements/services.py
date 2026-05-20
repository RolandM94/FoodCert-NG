from uuid import uuid4

from django.db import transaction

from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.facilities.models import MedicalFacility
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.settlements.models import Settlement


class SettlementService:
    @classmethod
    @transaction.atomic
    def create_for_assessment_payment(cls, *, payment_transaction: PaymentTransaction, assessment_id=None, actor=None):
        if payment_transaction.status != PaymentStatus.SUCCESS:
            raise ValueError("PAYMENT_REQUIRED")
        facility = MedicalFacility.objects.get(id=payment_transaction.metadata["facility_id"])
        settlement, created = Settlement.objects.get_or_create(
            payment_transaction=payment_transaction,
            defaults={
                "facility": facility,
                "state": facility.state,
                "assessment_id": assessment_id,
                "gross_amount": payment_transaction.amount,
                "facility_amount": payment_transaction.metadata.get("facility_fee", 0),
                "state_amount": payment_transaction.metadata.get("state_fee", 0),
                "platform_amount": payment_transaction.metadata.get("platform_fee", 0),
            },
        )
        if created:
            log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=settlement, metadata={"event": "settlement_created"})
        return settlement

    @classmethod
    @transaction.atomic
    def process(cls, *, settlement, actor=None):
        reference = f"SET-{uuid4().hex[:12].upper()}"
        settlement.mark_paid(reference)
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=settlement, metadata={"event": "settlement_paid"})
        return settlement
