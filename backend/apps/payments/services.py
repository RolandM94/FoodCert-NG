from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.assessments.models import AssessmentStatus, MedicalAssessment
from apps.facilities.models import MedicalFacility
from apps.payments.models import (
    ActiveStatus,
    AssessmentFee,
    LedgerEntryType,
    PayerType,
    PaymentAllocation,
    PaymentAllocationStatus,
    PaymentLedgerEntry,
    PaymentReconciliationRecord,
    PaymentStatus,
    PaymentTransaction,
    PaymentWebhookEvent,
    ReconciliationStatus,
    RefundRequest,
    RefundStatus,
    Receipt,
    WebhookProcessingStatus,
)
from apps.payments.providers import active_provider_config, get_payment_provider


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
    def assessment_payment_quote(cls, *, assessment: MedicalAssessment):
        if not assessment.facility.can_conduct_assessments:
            raise ValueError("FACILITY_NOT_ACCREDITED")
        fee = cls.current_assessment_fee(state=assessment.facility.state, facility_type=assessment.facility.facility_type)
        if not fee:
            raise ValueError("No active assessment fee is configured for this state and facility type.")
        return {
            "assessment_id": assessment.id,
            "fee_schedule_id": fee.id,
            "fee_name": fee.fee_name,
            "facility_name": assessment.facility.facility_name,
            "state_name": assessment.facility.state.name,
            "amount": fee.amount,
            "currency": fee.currency,
            "state_fee": fee.state_fee,
            "facility_fee": fee.facility_fee,
            "platform_fee": fee.platform_fee,
            "refund_policy_summary": "Refunds are reviewed according to state policy and payment provider rules.",
            "terms_notice": "By continuing, you confirm the assessment details and agree to FoodCert NG payment terms.",
        }

    @classmethod
    def bulk_assessment_payment_quote(cls, *, employer, assessment_ids):
        if not assessment_ids:
            raise ValueError("Select at least one assessment.")
        if len(assessment_ids) != len(set(str(item) for item in assessment_ids)):
            raise ValueError("Duplicate assessments are not allowed in one bulk payment.")
        assessments = list(
            MedicalAssessment.objects.select_related(
                "food_handler",
                "employer",
                "facility",
                "facility__state",
                "payment_transaction",
            ).filter(id__in=assessment_ids)
        )
        if len(assessments) != len(assessment_ids):
            raise ValueError("One or more assessments could not be found.")
        allowed_statuses = {AssessmentStatus.DRAFT, AssessmentStatus.PAYMENT_PENDING}
        line_items = []
        currency = None
        total = Decimal("0.00")
        for assessment in assessments:
            if assessment.employer_id != employer.id:
                raise ValueError("All assessments must belong to this employer.")
            if assessment.status not in allowed_statuses:
                raise ValueError("Only draft or payment-pending assessments can be paid in bulk.")
            if assessment.payment_transaction and assessment.payment_transaction.status == PaymentStatus.SUCCESS:
                raise ValueError("One or more assessments have already been paid.")
            quote = cls.assessment_payment_quote(assessment=assessment)
            if currency and quote["currency"] != currency:
                raise ValueError("All selected assessments must use the same currency.")
            currency = quote["currency"]
            total += Decimal(str(quote["amount"]))
            line_items.append({
                "assessment_id": str(assessment.id),
                "food_handler_id": str(assessment.food_handler_id),
                "food_handler_name": assessment.food_handler.full_name,
                "facility_id": str(assessment.facility_id),
                "facility_name": assessment.facility.facility_name,
                "state_id": str(assessment.facility.state_id),
                "state_name": assessment.facility.state.name,
                "fee_schedule_id": str(quote["fee_schedule_id"]),
                "fee_name": quote["fee_name"],
                "amount": str(quote["amount"]),
                "currency": quote["currency"],
                "state_fee": str(quote["state_fee"]),
                "facility_fee": str(quote["facility_fee"]),
                "platform_fee": str(quote["platform_fee"]),
            })
        return {
            "employer_id": str(employer.id),
            "employer_name": employer.business_name,
            "assessment_count": len(line_items),
            "amount": total,
            "currency": currency or "NGN",
            "line_items": line_items,
            "terms_notice": "Bulk payments are allocated per assessment and must be refreshed if any selected assessment changes before checkout.",
        }

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
    def initiate_assessment_payment_for_assessment(cls, *, payer_user, assessment: MedicalAssessment):
        if assessment.payment_transaction and assessment.payment_transaction.status == PaymentStatus.SUCCESS:
            return assessment.payment_transaction
        quote = cls.assessment_payment_quote(assessment=assessment)
        fee = AssessmentFee.objects.get(id=quote["fee_schedule_id"])
        reference = cls._reference("ASS")
        provider = get_payment_provider()
        transaction_obj = PaymentTransaction.objects.create(
            payer_user=payer_user,
            payer_type=PayerType.FOOD_HANDLER,
            related_entity_type="medical_assessment",
            related_entity_id=assessment.id,
            amount=fee.amount,
            currency=fee.currency,
            payment_provider=provider.provider_name,
            internal_reference=reference,
            metadata={
                "assessment_id": str(assessment.id),
                "food_handler_id": str(assessment.food_handler_id),
                "facility_id": str(assessment.facility_id),
                "state_id": str(assessment.facility.state_id),
                "assessment_fee_id": str(fee.id),
                "fee_name": fee.fee_name,
                "state_fee": str(fee.state_fee),
                "facility_fee": str(fee.facility_fee),
                "platform_fee": str(fee.platform_fee),
            },
        )
        initialization = provider.initialize_payment(fee.amount, payer_user.email, reference, transaction_obj.metadata)
        transaction_obj.provider_reference = initialization.provider_reference
        transaction_obj.metadata = {**transaction_obj.metadata, "authorization_url": initialization.authorization_url}
        transaction_obj.save(update_fields=["provider_reference", "metadata", "updated_at"])
        assessment.payment_transaction = transaction_obj
        assessment.status = AssessmentStatus.PAYMENT_PENDING
        assessment.save(update_fields=["payment_transaction", "status", "updated_at"])
        log_action(action=AuditAction.PAYMENT_EVENT, actor=payer_user, target=transaction_obj, metadata={"event": "assessment_payment_initialized", "assessment_id": str(assessment.id)})
        return transaction_obj

    @classmethod
    @transaction.atomic
    def initiate_bulk_assessment_payment(cls, *, payer_user, employer, assessment_ids):
        quote = cls.bulk_assessment_payment_quote(employer=employer, assessment_ids=assessment_ids)
        reference = cls._reference("BULKASS")
        provider = get_payment_provider()
        transaction_obj = PaymentTransaction.objects.create(
            payer_user=payer_user,
            payer_type=PayerType.EMPLOYER,
            related_entity_type="employer_bulk_assessment_payment",
            related_entity_id=employer.id,
            amount=quote["amount"],
            currency=quote["currency"],
            payment_provider=provider.provider_name,
            internal_reference=reference,
            metadata={
                "employer_id": str(employer.id),
                "assessment_ids": [item["assessment_id"] for item in quote["line_items"]],
                "line_items": quote["line_items"],
                "payment_scope": "bulk_assessments",
            },
        )
        initialization = provider.initialize_payment(quote["amount"], payer_user.email, reference, transaction_obj.metadata)
        transaction_obj.provider_reference = initialization.provider_reference
        transaction_obj.metadata = {**transaction_obj.metadata, "authorization_url": initialization.authorization_url}
        transaction_obj.save(update_fields=["provider_reference", "metadata", "updated_at"])
        MedicalAssessment.objects.filter(id__in=transaction_obj.metadata["assessment_ids"]).update(
            payment_transaction=transaction_obj,
            status=AssessmentStatus.PAYMENT_PENDING,
            updated_at=timezone.now(),
        )
        log_action(action=AuditAction.PAYMENT_EVENT, actor=payer_user, target=transaction_obj, metadata={"event": "bulk_assessment_payment_initialized", "employer_id": str(employer.id)})
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
            currency=getattr(plan, "currency", "NGN"),
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
            if str(verification.amount) not in {"0", "0.0", "0.00", str(transaction_obj.amount)}:
                transaction_obj.status = PaymentStatus.FAILED
                transaction_obj.metadata = {**transaction_obj.metadata, "verification": verification.metadata, "amount_mismatch": {"expected": str(transaction_obj.amount), "received": str(verification.amount)}}
                transaction_obj.save(update_fields=["status", "metadata", "updated_at"])
                log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=transaction_obj, metadata={"event": "payment_amount_mismatch"})
                return transaction_obj
            transaction_obj.status = PaymentStatus.SUCCESS
            transaction_obj.paid_at = timezone.now()
            event = "payment_confirmed"
        else:
            transaction_obj.status = PaymentStatus.FAILED
            event = "payment_failed"
        transaction_obj.provider_reference = verification.provider_reference
        transaction_obj.metadata = {**transaction_obj.metadata, "verification": verification.metadata}
        transaction_obj.save(update_fields=["status", "paid_at", "provider_reference", "metadata", "updated_at"])
        if transaction_obj.status == PaymentStatus.SUCCESS:
            cls._post_successful_payment(transaction_obj=transaction_obj, actor=actor)
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=transaction_obj, metadata={"event": event})
        return transaction_obj

    @classmethod
    def _receipt_number(cls):
        return cls._reference("RCT")

    @classmethod
    def receipt_for_payment(cls, *, transaction_obj: PaymentTransaction):
        metadata = transaction_obj.metadata or {}
        facility = None
        if metadata.get("facility_id"):
            facility = MedicalFacility.objects.filter(id=metadata["facility_id"]).first()
        receipt, _created = Receipt.objects.get_or_create(
            payment_transaction=transaction_obj,
            defaults={
                "receipt_number": cls._receipt_number(),
                "payer_name": transaction_obj.payer_user.get_full_name() or transaction_obj.payer_user.email,
                "payer_email": transaction_obj.payer_user.email,
                "payer_type": transaction_obj.payer_type,
                "payment_purpose": transaction_obj.related_entity_type,
                "amount": transaction_obj.amount,
                "currency": transaction_obj.currency,
                "payment_method": metadata.get("payment_method", ""),
                "provider_reference": transaction_obj.provider_reference,
                "facility": facility,
                "state": facility.state if facility else None,
                "line_items": metadata.get("line_items", []),
            },
        )
        return receipt

    @classmethod
    def _post_successful_payment(cls, *, transaction_obj: PaymentTransaction, actor=None):
        cls.receipt_for_payment(transaction_obj=transaction_obj)
        if transaction_obj.related_entity_type == "employer_bulk_assessment_payment":
            allocations = cls.allocations_for_bulk_payment(transaction_obj=transaction_obj)
            for allocation in allocations:
                cls.ledger_entries_for_allocation(allocation=allocation)
            assessment_ids = (transaction_obj.metadata or {}).get("assessment_ids", [])
            if assessment_ids:
                MedicalAssessment.objects.filter(id__in=assessment_ids).update(
                    payment_transaction=transaction_obj,
                    status=AssessmentStatus.PAYMENT_CONFIRMED,
                    updated_at=timezone.now(),
                )
            return
        allocation = cls.allocation_for_payment(transaction_obj=transaction_obj)
        if allocation:
            cls.ledger_entries_for_allocation(allocation=allocation)
        assessment_id = (transaction_obj.metadata or {}).get("assessment_id")
        if not assessment_id and transaction_obj.related_entity_type == "medical_assessment":
            assessment_id = transaction_obj.related_entity_id
        if assessment_id:
            MedicalAssessment.objects.filter(id=assessment_id).update(
                payment_transaction=transaction_obj,
                status=AssessmentStatus.PAYMENT_CONFIRMED,
                updated_at=timezone.now(),
            )

    @classmethod
    def allocations_for_bulk_payment(cls, *, transaction_obj: PaymentTransaction):
        allocations = []
        for item in (transaction_obj.metadata or {}).get("line_items", []):
            fee = AssessmentFee.objects.filter(id=item.get("fee_schedule_id")).first()
            facility = MedicalFacility.objects.filter(id=item.get("facility_id")).first()
            assessment = MedicalAssessment.objects.filter(id=item.get("assessment_id")).first()
            if not fee or not facility or not assessment:
                continue
            allocation, _created = PaymentAllocation.objects.get_or_create(
                payment_transaction=transaction_obj,
                assessment=assessment,
                defaults={
                    "fee_schedule": fee,
                    "facility": facility,
                    "state": facility.state,
                    "gross_amount": Decimal(str(item["amount"])),
                    "facility_amount": Decimal(str(item["facility_fee"])),
                    "state_amount": Decimal(str(item["state_fee"])),
                    "platform_amount": Decimal(str(item["platform_fee"])),
                    "provider_fee": Decimal(str(item.get("provider_fee", "0"))),
                    "metadata": {
                        "fee_schedule_id": str(fee.id),
                        "fee_name": fee.fee_name,
                        "payment_reference": transaction_obj.internal_reference,
                        "bulk_payment": True,
                        "food_handler_id": item.get("food_handler_id"),
                    },
                },
            )
            allocations.append(allocation)
        return allocations

    @classmethod
    def allocation_for_payment(cls, *, transaction_obj: PaymentTransaction):
        metadata = transaction_obj.metadata or {}
        fee_id = metadata.get("assessment_fee_id")
        facility_id = metadata.get("facility_id")
        if not fee_id or not facility_id:
            return None
        fee = AssessmentFee.objects.filter(id=fee_id).first()
        facility = MedicalFacility.objects.filter(id=facility_id).first()
        if not fee or not facility:
            return None
        assessment = None
        assessment_id = metadata.get("assessment_id")
        if assessment_id:
            assessment = MedicalAssessment.objects.filter(id=assessment_id).first()
        allocation, _created = PaymentAllocation.objects.get_or_create(
            payment_transaction=transaction_obj,
            assessment=assessment,
            defaults={
                "fee_schedule": fee,
                "facility": facility,
                "state": facility.state,
                "gross_amount": transaction_obj.amount,
                "facility_amount": Decimal(str(metadata.get("facility_fee", fee.facility_fee))),
                "state_amount": Decimal(str(metadata.get("state_fee", fee.state_fee))),
                "platform_amount": Decimal(str(metadata.get("platform_fee", fee.platform_fee))),
                "provider_fee": Decimal(str(metadata.get("provider_fee", "0"))),
                "metadata": {
                    "fee_schedule_id": str(fee.id),
                    "fee_name": fee.fee_name,
                    "payment_reference": transaction_obj.internal_reference,
                },
            },
        )
        return allocation

    @classmethod
    def ledger_entries_for_allocation(cls, *, allocation: PaymentAllocation):
        transaction_obj = allocation.payment_transaction
        specs = [
            (LedgerEntryType.COLLECTION, "cash", "debit", allocation.gross_amount),
            (LedgerEntryType.FACILITY_PAYABLE, "facility_payable", "credit", allocation.facility_amount),
            (LedgerEntryType.STATE_REVENUE, "state_revenue", "credit", allocation.state_amount),
            (LedgerEntryType.PLATFORM_REVENUE, "platform_revenue", "credit", allocation.platform_amount),
        ]
        if allocation.provider_fee:
            specs.append((LedgerEntryType.PROVIDER_FEE, "provider_fee", "debit", allocation.provider_fee))
        entries = []
        for entry_type, account, direction, amount in specs:
            reference = f"LED-{transaction_obj.internal_reference}-{allocation.id.hex[:8]}-{entry_type}".replace("_", "-")[:120]
            entry, _created = PaymentLedgerEntry.objects.get_or_create(
                reference=reference,
                defaults={
                    "payment_transaction": transaction_obj,
                    "allocation": allocation,
                    "entry_type": entry_type,
                    "account": account,
                    "direction": direction,
                    "amount": amount,
                    "currency": transaction_obj.currency,
                    "metadata": {
                        "allocation_id": str(allocation.id),
                        "fee_schedule_id": str(allocation.fee_schedule_id),
                    },
                },
            )
            entries.append(entry)
        return entries

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

    @classmethod
    @transaction.atomic
    def request_refund(cls, *, transaction_obj: PaymentTransaction, actor, reason: str, amount=None, payment_allocation=None):
        if transaction_obj.status != PaymentStatus.SUCCESS:
            raise ValueError("Only successful payments can be considered for refund.")
        if not reason.strip():
            raise ValueError("Refund reason is required.")
        refund_amount = amount or transaction_obj.amount
        if payment_allocation and payment_allocation.payment_transaction_id != transaction_obj.id:
            raise ValueError("Refund allocation must belong to this payment transaction.")
        if payment_allocation and refund_amount > payment_allocation.gross_amount:
            raise ValueError("Refund amount cannot exceed the selected allocation.")
        if refund_amount <= 0 or refund_amount > transaction_obj.amount:
            raise ValueError("Refund amount must be greater than zero and cannot exceed the payment amount.")
        existing = transaction_obj.refund_requests.filter(
            status__in=[RefundStatus.REQUESTED, RefundStatus.UNDER_REVIEW, RefundStatus.APPROVED, RefundStatus.PROCESSING]
        ).first()
        if existing:
            return existing
        refund = RefundRequest.objects.create(
            payment_transaction=transaction_obj,
            payment_allocation=payment_allocation,
            requested_by=actor,
            amount=refund_amount,
            reason=reason,
            status=RefundStatus.REQUESTED,
        )
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=refund, metadata={"event": "refund_requested", "payment_transaction_id": str(transaction_obj.id)})
        return refund

    @classmethod
    @transaction.atomic
    def approve_refund(cls, *, refund_request: RefundRequest, actor, notes=""):
        if refund_request.status not in {RefundStatus.REQUESTED, RefundStatus.UNDER_REVIEW}:
            raise ValueError("Only requested refunds can be approved.")
        refund_request.status = RefundStatus.APPROVED
        refund_request.approved_by = actor
        refund_request.approved_at = timezone.now()
        refund_request.review_notes = notes
        refund_request.save(update_fields=["status", "approved_by", "approved_at", "review_notes", "updated_at"])
        cls._hold_settlements_for_refund(refund_request=refund_request, actor=actor)
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=refund_request, metadata={"event": "refund_approved"})
        return refund_request

    @classmethod
    @transaction.atomic
    def reject_refund(cls, *, refund_request: RefundRequest, actor, notes=""):
        if refund_request.status not in {RefundStatus.REQUESTED, RefundStatus.UNDER_REVIEW, RefundStatus.APPROVED}:
            raise ValueError("Only open refunds can be rejected.")
        refund_request.status = RefundStatus.REJECTED
        refund_request.approved_by = actor
        refund_request.approved_at = timezone.now()
        refund_request.review_notes = notes
        refund_request.save(update_fields=["status", "approved_by", "approved_at", "review_notes", "updated_at"])
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=refund_request, metadata={"event": "refund_rejected"})
        return refund_request

    @classmethod
    @transaction.atomic
    def process_refund(cls, *, refund_request: RefundRequest, actor):
        if refund_request.status != RefundStatus.APPROVED:
            raise ValueError("Only approved refunds can be processed.")
        refund_request.status = RefundStatus.PROCESSING
        refund_request.save(update_fields=["status", "updated_at"])
        provider = get_payment_provider()
        provider_refund = provider.refund_payment(
            refund_request.payment_transaction.internal_reference,
            amount=refund_request.amount,
        )
        refund_request.status = RefundStatus.REFUNDED
        refund_request.provider_refund_reference = provider_refund.get("reference", "")
        refund_request.processed_at = timezone.now()
        refund_request.save(update_fields=["status", "provider_refund_reference", "processed_at", "updated_at"])
        cls.refund_ledger_entries(refund_request=refund_request)
        cls._sync_refunded_payment_and_allocations(refund_request=refund_request)
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=refund_request, metadata={"event": "refund_processed"})
        return refund_request

    @classmethod
    def refund_ledger_entries(cls, *, refund_request: RefundRequest):
        transaction_obj = refund_request.payment_transaction
        allocations = [refund_request.payment_allocation] if refund_request.payment_allocation_id else list(transaction_obj.allocations.all())
        if not allocations:
            reference = f"LED-{transaction_obj.internal_reference}-REFUND-{refund_request.id.hex[:8]}".replace("_", "-")[:120]
            PaymentLedgerEntry.objects.get_or_create(
                reference=reference,
                defaults={
                    "payment_transaction": transaction_obj,
                    "entry_type": LedgerEntryType.REFUND,
                    "account": "cash",
                    "direction": "credit",
                    "amount": refund_request.amount,
                    "currency": transaction_obj.currency,
                    "metadata": {"refund_request_id": str(refund_request.id)},
                },
            )
            return

        remaining = Decimal(str(refund_request.amount))
        for allocation in allocations:
            if remaining <= 0:
                break
            amount = min(remaining, allocation.gross_amount)
            ratio = amount / allocation.gross_amount if allocation.gross_amount else Decimal("0")
            specs = [
                (LedgerEntryType.REFUND, "cash", "credit", amount),
                (LedgerEntryType.REVERSAL, "facility_payable", "debit", allocation.facility_amount * ratio),
                (LedgerEntryType.REVERSAL, "state_revenue", "debit", allocation.state_amount * ratio),
                (LedgerEntryType.REVERSAL, "platform_revenue", "debit", allocation.platform_amount * ratio),
            ]
            for entry_type, account, direction, entry_amount in specs:
                reference = f"LED-{transaction_obj.internal_reference}-{allocation.id.hex[:8]}-{refund_request.id.hex[:8]}-{entry_type}-{account}".replace("_", "-")[:120]
                PaymentLedgerEntry.objects.get_or_create(
                    reference=reference,
                    defaults={
                        "payment_transaction": transaction_obj,
                        "allocation": allocation,
                        "entry_type": entry_type,
                        "account": account,
                        "direction": direction,
                        "amount": entry_amount.quantize(Decimal("0.01")),
                        "currency": transaction_obj.currency,
                        "metadata": {"refund_request_id": str(refund_request.id), "refund_amount": str(amount)},
                    },
                )
            remaining -= amount

    @classmethod
    def _sync_refunded_payment_and_allocations(cls, *, refund_request: RefundRequest):
        transaction_obj = refund_request.payment_transaction
        refunded_total = sum((item.amount for item in transaction_obj.refund_requests.filter(status=RefundStatus.REFUNDED)), Decimal("0.00"))
        transaction_obj.metadata = {**transaction_obj.metadata, "refunded_amount": str(refunded_total)}
        if refunded_total >= transaction_obj.amount:
            transaction_obj.status = PaymentStatus.REFUNDED
            transaction_obj.save(update_fields=["status", "metadata", "updated_at"])
        else:
            transaction_obj.save(update_fields=["metadata", "updated_at"])

        allocations = [refund_request.payment_allocation] if refund_request.payment_allocation_id else list(transaction_obj.allocations.all())
        for allocation in allocations:
            allocation_refunded = sum((item.amount for item in allocation.refund_requests.filter(status=RefundStatus.REFUNDED)), Decimal("0.00"))
            allocation.status = PaymentAllocationStatus.REFUNDED if allocation_refunded >= allocation.gross_amount else PaymentAllocationStatus.PARTIALLY_REFUNDED
            allocation.save(update_fields=["status", "updated_at"])

    @classmethod
    def _hold_settlements_for_refund(cls, *, refund_request: RefundRequest, actor=None):
        from apps.settlements.models import SettlementStatus
        from apps.settlements.services import SettlementService

        settlements = refund_request.payment_transaction.settlements.exclude(settlement_status=SettlementStatus.PAID)
        if refund_request.payment_allocation_id:
            settlements = settlements.filter(payment_allocation=refund_request.payment_allocation)
        for settlement in settlements:
            if settlement.settlement_status != SettlementStatus.HELD:
                SettlementService.hold(settlement=settlement, actor=actor, reason="Refund or chargeback activity pending.")

    @classmethod
    @transaction.atomic
    def record_chargeback(cls, *, transaction_obj: PaymentTransaction, actor=None, amount=None, reason="Provider chargeback"):
        refund = cls.request_refund(
            transaction_obj=transaction_obj,
            actor=actor or transaction_obj.payer_user,
            reason=reason,
            amount=amount or transaction_obj.amount,
        )
        refund.status = RefundStatus.APPROVED
        refund.approved_by = actor
        refund.approved_at = timezone.now()
        refund.review_notes = "Automatically approved from provider chargeback notification."
        refund.save(update_fields=["status", "approved_by", "approved_at", "review_notes", "updated_at"])
        cls._hold_settlements_for_refund(refund_request=refund, actor=actor)
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=refund, metadata={"event": "chargeback_recorded"})
        return refund

    @classmethod
    @transaction.atomic
    def process_webhook(cls, *, provider_code=None, payload, body: bytes, signature: str = ""):
        provider_config = active_provider_config(provider_code)
        provider = get_payment_provider(provider_code or (provider_config.code if provider_config else None))
        webhook_secret = (provider_config.webhook_secret if provider_config else "") or getattr(settings, "PAYMENT_WEBHOOK_SECRET", "")
        signature_valid = provider.verify_webhook_signature(body=body, signature=signature, secret=webhook_secret)
        parsed = provider.parse_webhook_payload(payload)
        event_defaults = {
            "provider": provider_config,
            "provider_code": provider_code or (provider_config.code if provider_config else provider.provider_name),
            "event_type": parsed.event_type,
            "provider_reference": parsed.provider_reference,
            "raw_payload": payload,
            "signature_valid": signature_valid,
            "processing_status": WebhookProcessingStatus.RECEIVED,
        }
        webhook_event, created = PaymentWebhookEvent.objects.get_or_create(
            idempotency_key=parsed.idempotency_key,
            defaults=event_defaults,
        )
        if not created and webhook_event.processing_status in {WebhookProcessingStatus.PROCESSED, WebhookProcessingStatus.DUPLICATE}:
            webhook_event.processing_status = WebhookProcessingStatus.DUPLICATE
            webhook_event.processing_message = "Duplicate webhook event ignored."
            webhook_event.processed_at = timezone.now()
            webhook_event.save(update_fields=["processing_status", "processing_message", "processed_at", "updated_at"])
            transaction_obj = PaymentTransaction.objects.filter(internal_reference=parsed.reference).first()
            return transaction_obj, webhook_event
        if not signature_valid:
            webhook_event.signature_valid = False
            webhook_event.processing_status = WebhookProcessingStatus.REJECTED
            webhook_event.processing_message = "Invalid payment webhook signature."
            webhook_event.processed_at = timezone.now()
            webhook_event.save(update_fields=["signature_valid", "processing_status", "processing_message", "processed_at", "updated_at"])
            raise PermissionError("Invalid payment webhook signature.")
        if not parsed.reference:
            webhook_event.processing_status = WebhookProcessingStatus.REJECTED
            webhook_event.processing_message = "Webhook payload did not include a payment reference."
            webhook_event.processed_at = timezone.now()
            webhook_event.save(update_fields=["processing_status", "processing_message", "processed_at", "updated_at"])
            raise ValueError("Payment webhook reference is required.")
        transaction_obj = cls.verify_payment(reference=parsed.reference)
        webhook_event.signature_valid = True
        webhook_event.processing_status = WebhookProcessingStatus.PROCESSED
        webhook_event.processing_message = "Payment webhook processed."
        webhook_event.processed_at = timezone.now()
        webhook_event.save(update_fields=["signature_valid", "processing_status", "processing_message", "processed_at", "updated_at"])
        log_action(action=AuditAction.PAYMENT_EVENT, target=transaction_obj, metadata={"event": "payment_webhook", "webhook_event_id": str(webhook_event.id)})
        return transaction_obj, webhook_event


class PaymentReconciliationService:
    @classmethod
    def _find_transaction(cls, *, internal_reference="", provider_reference=""):
        queryset = PaymentTransaction.objects.all()
        filters = Q()
        if internal_reference:
            filters |= Q(internal_reference=internal_reference)
        if provider_reference:
            filters |= Q(provider_reference=provider_reference)
        if not filters:
            return None
        return queryset.filter(filters).order_by("-created_at").first()

    @classmethod
    @transaction.atomic
    def reconcile_provider_record(cls, *, provider_code, record, actor=None):
        provider_reference = str(record.get("provider_reference", "")).strip()
        internal_reference = str(record.get("internal_reference", "")).strip()
        amount = Decimal(str(record.get("amount", "0.00")))
        currency = str(record.get("currency", "NGN")).upper()
        provider_payload = record.get("provider_payload") or {}
        if not provider_reference:
            raise ValueError("Provider reference is required.")
        if amount <= 0:
            raise ValueError("Provider amount must be greater than zero.")

        duplicate_exists = PaymentReconciliationRecord.objects.filter(
            provider_code=provider_code,
            provider_reference=provider_reference,
        ).exists()
        transaction_obj = cls._find_transaction(
            internal_reference=internal_reference,
            provider_reference=provider_reference,
        )
        if duplicate_exists:
            status = ReconciliationStatus.DUPLICATE_PROVIDER_REFERENCE
        elif not transaction_obj:
            status = ReconciliationStatus.MISSING_INTERNAL
        elif transaction_obj.currency != currency:
            status = ReconciliationStatus.CURRENCY_MISMATCH
        elif transaction_obj.amount != amount:
            status = ReconciliationStatus.AMOUNT_MISMATCH
        else:
            status = ReconciliationStatus.MATCHED

        reconciliation = PaymentReconciliationRecord.objects.create(
            provider_code=provider_code,
            provider_reference=provider_reference,
            internal_reference=internal_reference or (transaction_obj.internal_reference if transaction_obj else ""),
            payment_transaction=transaction_obj,
            amount=amount,
            currency=currency,
            status=status,
            matched_at=timezone.now() if status == ReconciliationStatus.MATCHED else None,
            provider_payload=provider_payload,
        )
        log_action(
            action=AuditAction.PAYMENT_EVENT,
            actor=actor,
            target=reconciliation,
            metadata={
                "event": "payment_reconciliation_imported",
                "status": status,
                "provider_code": provider_code,
                "provider_reference": provider_reference,
            },
        )
        return reconciliation

    @classmethod
    def import_provider_records(cls, *, provider_code, records, actor=None):
        return [
            cls.reconcile_provider_record(provider_code=provider_code, record=record, actor=actor)
            for record in records
        ]

    @classmethod
    @transaction.atomic
    def resolve(cls, *, reconciliation, actor, notes):
        if not notes or not notes.strip():
            raise ValueError("Resolution notes are required.")
        if reconciliation.status == ReconciliationStatus.MATCHED:
            raise ValueError("Matched reconciliation records do not need manual resolution.")
        reconciliation.status = ReconciliationStatus.MANUALLY_RESOLVED
        reconciliation.resolved_by = actor
        reconciliation.resolved_at = timezone.now()
        reconciliation.resolution_notes = notes.strip()
        reconciliation.save(update_fields=["status", "resolved_by", "resolved_at", "resolution_notes", "updated_at"])
        log_action(
            action=AuditAction.PAYMENT_EVENT,
            actor=actor,
            target=reconciliation,
            metadata={
                "event": "payment_reconciliation_resolved",
                "provider_code": reconciliation.provider_code,
                "provider_reference": reconciliation.provider_reference,
            },
        )
        return reconciliation

    @classmethod
    def provider_performance(cls, queryset=None):
        queryset = queryset or PaymentReconciliationRecord.objects.all()
        return list(
            queryset.values("provider_code")
            .annotate(
                total_records=Count("id"),
                matched_records=Count("id", filter=Q(status=ReconciliationStatus.MATCHED)),
                issue_records=Count(
                    "id",
                    filter=Q(
                        status__in=[
                            ReconciliationStatus.MISSING_INTERNAL,
                            ReconciliationStatus.MISSING_PROVIDER,
                            ReconciliationStatus.AMOUNT_MISMATCH,
                            ReconciliationStatus.CURRENCY_MISMATCH,
                            ReconciliationStatus.DUPLICATE_PROVIDER_REFERENCE,
                        ]
                    ),
                ),
                manually_resolved_records=Count("id", filter=Q(status=ReconciliationStatus.MANUALLY_RESOLVED)),
                total_amount=Sum("amount"),
            )
            .order_by("provider_code")
        )
