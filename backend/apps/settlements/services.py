from uuid import uuid4

from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.assessments.models import AssessmentStatus, FitnessDecision
from apps.certificates.models import CertificateRequestStatus
from apps.facilities.models import MedicalFacility
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.settlements.models import Settlement, SettlementDisputeStatus, SettlementStatus


class SettlementService:
    @classmethod
    def ensure_facility_finance_access(cls, *, user, facility):
        if user.role in {"super_admin", "federal_admin"}:
            return
        if user.role == "state_admin" and facility.state_id == user.state_id:
            return
        if user.organization_id and facility.organization_id == user.organization_id:
            return
        raise PermissionDenied("You cannot view settlements for this facility.")

    @classmethod
    def validate_settlement_eligible(cls, *, settlement=None, payment_transaction=None, assessment=None):
        payment = payment_transaction or settlement.payment_transaction
        if payment.status != PaymentStatus.SUCCESS:
            raise ValidationError("Only successful payments can be settled.")
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
    def create_for_assessment_payment(cls, *, payment_transaction: PaymentTransaction, assessment_id=None, actor=None):
        if payment_transaction.status != PaymentStatus.SUCCESS:
            raise ValueError("PAYMENT_REQUIRED")
        cls.validate_settlement_eligible(payment_transaction=payment_transaction)
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
        cls.validate_settlement_eligible(settlement=settlement)
        reference = f"SET-{uuid4().hex[:12].upper()}"
        settlement.mark_paid(reference)
        log_action(action=AuditAction.PAYMENT_EVENT, actor=actor, target=settlement, metadata={"event": "settlement_paid"})
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
