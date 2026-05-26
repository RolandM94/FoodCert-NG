from decimal import Decimal
from uuid import uuid4

from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.assessments.models import AssessmentStatus, FitnessDecision
from apps.certificates.models import CertificateRequestStatus
from apps.facilities.models import MedicalFacility
from apps.payments.models import PaymentAllocation, PaymentStatus, PaymentTransaction, RefundStatus
from apps.payments.permissions import ensure_facility_finance_access
from apps.settlements.models import Settlement, SettlementBatch, SettlementBatchStatus, SettlementDisputeStatus, SettlementStatus


class SettlementService:
    @classmethod
    def ensure_facility_finance_access(cls, *, user, facility):
        ensure_facility_finance_access(user, facility)

    @classmethod
    def validate_settlement_eligible(cls, *, settlement=None, payment_transaction=None, assessment=None):
        payment = payment_transaction or settlement.payment_transaction
        if payment.status != PaymentStatus.SUCCESS:
            raise ValidationError("Only successful payments can be settled.")
        if payment.refund_requests.exclude(
            status__in=[RefundStatus.REJECTED, RefundStatus.CANCELLED, RefundStatus.FAILED]
        ).exists():
            raise ValidationError("Payments with active refund activity cannot be settled.")
        assessment = assessment or getattr(settlement, "assessment", None)
        if not assessment:
            return
        if assessment.final_decision == FitnessDecision.FIT:
            certificate_request = getattr(assessment, "certificate_request", None)
            if not getattr(assessment, "certificate", None) and (
                not certificate_request or certificate_request.status != CertificateRequestStatus.APPROVED
            ):
                raise ValidationError("Fit assessments require completed State validation before settlement.")
            return
        if assessment.signed_at and assessment.status in {
            AssessmentStatus.TEMPORARILY_NOT_FIT,
            AssessmentStatus.NOT_FIT,
            AssessmentStatus.DOCTOR_DECISION_PENDING,
        }:
            return
        raise ValidationError("Assessment must have a finalized doctor decision before settlement.")

    @classmethod
    @transaction.atomic
    def create_for_allocation(cls, *, allocation: PaymentAllocation, actor=None):
        payment_transaction = allocation.payment_transaction
        cls.validate_settlement_eligible(
            payment_transaction=payment_transaction,
            assessment=allocation.assessment,
        )
        settlement, created = Settlement.objects.get_or_create(
            payment_allocation=allocation,
            defaults={
                "facility": allocation.facility,
                "state": allocation.state,
                "payment_transaction": payment_transaction,
                "fee_schedule": allocation.fee_schedule,
                "assessment": allocation.assessment,
                "gross_amount": allocation.gross_amount,
                "facility_amount": allocation.facility_amount,
                "state_amount": allocation.state_amount,
                "platform_amount": allocation.platform_amount,
                "eligibility_checked_at": timezone.now(),
                "eligibility_reason": "Eligible from successful payment allocation.",
            },
        )
        if created:
            log_action(
                action=AuditAction.PAYMENT_EVENT,
                actor=actor,
                target=settlement,
                metadata={"event": "settlement_created", "allocation_id": str(allocation.id)},
            )
        return settlement

    @classmethod
    @transaction.atomic
    def create_for_assessment_payment(cls, *, payment_transaction: PaymentTransaction, assessment_id=None, actor=None):
        if payment_transaction.status != PaymentStatus.SUCCESS:
            raise ValueError("PAYMENT_REQUIRED")
        allocations = list(
            payment_transaction.allocations.select_related("assessment", "fee_schedule", "facility", "state").all()
        )
        if assessment_id:
            allocations = [allocation for allocation in allocations if str(allocation.assessment_id) == str(assessment_id)]
        if allocations:
            settlements = [cls.create_for_allocation(allocation=allocation, actor=actor) for allocation in allocations]
            return settlements[0] if len(settlements) == 1 else settlements

        assessment = None
        if assessment_id:
            from apps.assessments.models import MedicalAssessment

            assessment = MedicalAssessment.objects.filter(id=assessment_id).first()
        cls.validate_settlement_eligible(payment_transaction=payment_transaction, assessment=assessment)
        facility = MedicalFacility.objects.get(id=payment_transaction.metadata["facility_id"])
        settlement, created = Settlement.objects.get_or_create(
            payment_transaction=payment_transaction,
            assessment=assessment,
            defaults={
                "facility": facility,
                "state": facility.state,
                "fee_schedule_id": payment_transaction.metadata.get("assessment_fee_id"),
                "gross_amount": payment_transaction.amount,
                "facility_amount": payment_transaction.metadata.get("facility_fee", 0),
                "state_amount": payment_transaction.metadata.get("state_fee", 0),
                "platform_amount": payment_transaction.metadata.get("platform_fee", 0),
                "eligibility_checked_at": timezone.now(),
                "eligibility_reason": "Eligible from successful legacy assessment payment.",
            },
        )
        if created:
            log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=settlement, metadata={"event": "settlement_created"})
        return settlement

    @classmethod
    def eligible_allocations(cls, *, facility=None):
        queryset = PaymentAllocation.objects.select_related(
            "payment_transaction",
            "assessment",
            "fee_schedule",
            "facility",
            "state",
        ).filter(
            payment_transaction__status=PaymentStatus.SUCCESS,
            settlement__isnull=True,
        )
        if facility:
            queryset = queryset.filter(facility=facility)
        eligible = []
        for allocation in queryset:
            try:
                cls.validate_settlement_eligible(
                    payment_transaction=allocation.payment_transaction,
                    assessment=allocation.assessment,
                )
            except ValidationError:
                continue
            eligible.append(allocation)
        return eligible

    @classmethod
    @transaction.atomic
    def process(cls, *, settlement, actor=None):
        if settlement.settlement_status == SettlementStatus.PAID:
            raise ValidationError("Paid settlements cannot be processed again.")
        if settlement.settlement_status == SettlementStatus.HELD:
            raise ValidationError("Held settlements must be released before processing.")
        if settlement.dispute_status in {SettlementDisputeStatus.OPEN, SettlementDisputeStatus.UNDER_REVIEW}:
            raise ValidationError("Settlements with open disputes cannot be processed.")
        cls.validate_settlement_eligible(settlement=settlement)
        reference = f"SET-{uuid4().hex[:12].upper()}"
        settlement.payout_attempts += 1
        settlement.last_payout_error = ""
        settlement.save(update_fields=["payout_attempts", "last_payout_error", "updated_at"])
        settlement.mark_paid(reference)
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=settlement, metadata={"event": "settlement_paid"})
        return settlement

    @classmethod
    @transaction.atomic
    def hold(cls, *, settlement, actor=None, reason=""):
        if settlement.settlement_status == SettlementStatus.PAID:
            raise ValidationError("Paid settlements cannot be placed on hold.")
        if not reason.strip():
            raise ValidationError("Hold reason is required.")
        settlement.settlement_status = SettlementStatus.HELD
        settlement.held_at = timezone.now()
        settlement.hold_reason = reason
        settlement.save(update_fields=["settlement_status", "held_at", "hold_reason", "updated_at"])
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=settlement, metadata={"event": "settlement_held"})
        return settlement

    @classmethod
    @transaction.atomic
    def release_hold(cls, *, settlement, actor=None):
        if settlement.settlement_status != SettlementStatus.HELD:
            raise ValidationError("Only held settlements can be released.")
        settlement.settlement_status = SettlementStatus.PENDING
        settlement.released_at = timezone.now()
        settlement.save(update_fields=["settlement_status", "released_at", "updated_at"])
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=settlement, metadata={"event": "settlement_hold_released"})
        return settlement

    @classmethod
    @transaction.atomic
    def mark_failed(cls, *, settlement, actor=None, reason=""):
        if settlement.settlement_status == SettlementStatus.PAID:
            raise ValidationError("Paid settlements cannot be marked failed.")
        settlement.settlement_status = SettlementStatus.FAILED
        settlement.payout_attempts += 1
        settlement.last_payout_error = reason
        settlement.save(update_fields=["settlement_status", "payout_attempts", "last_payout_error", "updated_at"])
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=settlement, metadata={"event": "settlement_failed", "reason": reason})
        return settlement

    @classmethod
    @transaction.atomic
    def retry_failed(cls, *, settlement, actor=None):
        if settlement.settlement_status != SettlementStatus.FAILED:
            raise ValidationError("Only failed settlements can be retried.")
        settlement.settlement_status = SettlementStatus.PENDING
        settlement.last_payout_error = ""
        settlement.save(update_fields=["settlement_status", "last_payout_error", "updated_at"])
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=settlement, metadata={"event": "settlement_retry_requested"})
        return settlement

    @classmethod
    @transaction.atomic
    def dispute(cls, *, settlement, actor, reason):
        cls.ensure_facility_finance_access(user=actor, facility=settlement.facility)
        if not reason.strip():
            raise ValidationError("Dispute reason is required.")
        if settlement.dispute_status in {SettlementDisputeStatus.OPEN, SettlementDisputeStatus.UNDER_REVIEW}:
            raise ValidationError("This settlement already has an open dispute.")
        settlement.dispute_status = SettlementDisputeStatus.OPEN
        settlement.dispute_reason = reason
        settlement.disputed_by = actor
        settlement.disputed_at = timezone.now()
        settlement.save(update_fields=["dispute_status", "dispute_reason", "disputed_by", "disputed_at", "updated_at"])
        log_action(
            action=AuditAction.PAYMENT_EVENT,
            actor=actor,
            target=settlement,
            metadata={"event": "settlement_dispute_created", "settlement_status": settlement.settlement_status},
        )
        return settlement

    @classmethod
    @transaction.atomic
    def resolve_dispute(cls, *, settlement, actor, resolution, approved=True):
        if settlement.dispute_status not in {SettlementDisputeStatus.OPEN, SettlementDisputeStatus.UNDER_REVIEW}:
            raise ValidationError("Only open disputes can be resolved.")
        if not resolution.strip():
            raise ValidationError("Dispute resolution is required.")
        settlement.dispute_status = SettlementDisputeStatus.RESOLVED if approved else SettlementDisputeStatus.REJECTED
        settlement.dispute_resolution = resolution
        settlement.save(update_fields=["dispute_status", "dispute_resolution", "updated_at"])
        log_action(
            action=AuditAction.PAYMENT_EVENT,
            actor=actor,
            target=settlement,
            metadata={"event": "settlement_dispute_resolved", "approved": approved},
        )
        return settlement


class SettlementBatchService:
    @classmethod
    def _reference(cls):
        return f"SB-{timezone.now():%Y%m%d}-{uuid4().hex[:10].upper()}"

    @classmethod
    def _totals(cls, settlements):
        return {
            "settlement_count": len(settlements),
            "gross_amount": sum((item.gross_amount for item in settlements), Decimal("0.00")),
            "facility_amount": sum((item.facility_amount for item in settlements), Decimal("0.00")),
            "state_amount": sum((item.state_amount for item in settlements), Decimal("0.00")),
            "platform_amount": sum((item.platform_amount for item in settlements), Decimal("0.00")),
        }

    @classmethod
    @transaction.atomic
    def create(cls, *, settlement_ids, actor=None):
        if not settlement_ids:
            raise ValidationError("Select at least one settlement.")
        settlements = list(
            Settlement.objects.select_for_update().filter(
                id__in=settlement_ids,
                settlement_status__in=[SettlementStatus.PENDING, SettlementStatus.FAILED],
                batch__isnull=True,
            )
        )
        if len(settlements) != len(settlement_ids):
            raise ValidationError("All selected settlements must be unbatched pending or failed records.")
        for settlement in settlements:
            SettlementService.validate_settlement_eligible(settlement=settlement)
            if settlement.dispute_status in {SettlementDisputeStatus.OPEN, SettlementDisputeStatus.UNDER_REVIEW}:
                raise ValidationError("Settlements with open disputes cannot be batched.")
        totals = cls._totals(settlements)
        batch = SettlementBatch.objects.create(
            batch_reference=cls._reference(),
            created_by=actor,
            **totals,
        )
        Settlement.objects.filter(id__in=[item.id for item in settlements]).update(batch=batch)
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=batch, metadata={"event": "settlement_batch_created", "count": len(settlements)})
        return batch

    @classmethod
    @transaction.atomic
    def approve(cls, *, batch, actor=None):
        if batch.status != SettlementBatchStatus.DRAFT:
            raise ValidationError("Only draft batches can be approved.")
        batch.status = SettlementBatchStatus.APPROVED
        batch.approved_by = actor
        batch.approved_at = timezone.now()
        batch.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=batch, metadata={"event": "settlement_batch_approved"})
        return batch

    @classmethod
    @transaction.atomic
    def process(cls, *, batch, actor=None, fail=False, failure_reason=""):
        if batch.status not in {SettlementBatchStatus.APPROVED, SettlementBatchStatus.FAILED}:
            raise ValidationError("Only approved or failed batches can be processed.")
        settlements = list(batch.settlements.select_for_update().all())
        if any(item.settlement_status == SettlementStatus.PAID for item in settlements):
            raise ValidationError("A batch containing paid settlements cannot be processed.")
        batch.status = SettlementBatchStatus.PROCESSING
        batch.processed_by = actor
        batch.processed_at = timezone.now()
        batch.save(update_fields=["status", "processed_by", "processed_at", "updated_at"])
        if fail:
            for settlement in settlements:
                SettlementService.mark_failed(settlement=settlement, actor=actor, reason=failure_reason)
            batch.status = SettlementBatchStatus.FAILED
            batch.failure_reason = failure_reason
            batch.save(update_fields=["status", "failure_reason", "updated_at"])
            log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=batch, metadata={"event": "settlement_batch_failed"})
            return batch
        for settlement in settlements:
            SettlementService.process(settlement=settlement, actor=actor)
        batch.status = SettlementBatchStatus.PAID
        batch.payout_reference = f"PO-{uuid4().hex[:12].upper()}"
        batch.save(update_fields=["status", "payout_reference", "updated_at"])
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=batch, metadata={"event": "settlement_batch_paid"})
        return batch

    @classmethod
    @transaction.atomic
    def retry(cls, *, batch, actor=None):
        if batch.status != SettlementBatchStatus.FAILED:
            raise ValidationError("Only failed batches can be retried.")
        for settlement in batch.settlements.filter(settlement_status=SettlementStatus.FAILED):
            SettlementService.retry_failed(settlement=settlement, actor=actor)
        batch.status = SettlementBatchStatus.APPROVED
        batch.failure_reason = ""
        batch.save(update_fields=["status", "failure_reason", "updated_at"])
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=batch, metadata={"event": "settlement_batch_retry_requested"})
        return batch

    @classmethod
    def facility_metrics(cls, *, facility, date_from=None, date_to=None):
        settlements = Settlement.objects.filter(facility=facility)
        payments = PaymentTransaction.objects.filter(metadata__facility_id=str(facility.id))
        if date_from:
            settlements = settlements.filter(created_at__date__gte=date_from)
            payments = payments.filter(created_at__date__gte=date_from)
        if date_to:
            settlements = settlements.filter(created_at__date__lte=date_to)
            payments = payments.filter(created_at__date__lte=date_to)
        successful_payments = payments.filter(status=PaymentStatus.SUCCESS)
        totals = settlements.aggregate(
            gross_amount=Sum("gross_amount"),
            facility_amount=Sum("facility_amount"),
            state_amount=Sum("state_amount"),
            platform_amount=Sum("platform_amount"),
        )
        status_counts = {item["settlement_status"]: item["total"] for item in settlements.values("settlement_status").annotate(total=Count("id"))}
        return {
            "cards": {
                "paid_assessments": successful_payments.count(),
                "completed_assessments": facility.assessments.filter(signed_at__isnull=False).count(),
                "pending_settlements": status_counts.get(SettlementStatus.PENDING, 0),
                "processing_settlements": status_counts.get(SettlementStatus.PROCESSING, 0),
                "paid_settlements": status_counts.get(SettlementStatus.PAID, 0),
                "failed_settlements": status_counts.get(SettlementStatus.FAILED, 0),
                "gross_amount": totals["gross_amount"] or 0,
                "facility_amount": totals["facility_amount"] or 0,
                "state_amount": totals["state_amount"] or 0,
                "platform_amount": totals["platform_amount"] or 0,
                "refunds": payments.filter(status=PaymentStatus.REFUNDED).count(),
                "disputes": settlements.exclude(dispute_status=SettlementDisputeStatus.NONE).count(),
            },
            "status": status_counts,
        }
