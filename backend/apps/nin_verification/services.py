from django.db import transaction

from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.food_handlers.models import FoodHandlerStatus
from apps.nin_verification.models import NINVerification, NINVerificationStatus
from apps.nin_verification.providers import get_nin_provider, verification_timestamp_for_status


class NINVerificationService:
    """Runs NIN provider checks and records auditable verification outcomes."""

    MATCH_THRESHOLD = 100

    @classmethod
    @transaction.atomic
    def verify(cls, *, food_handler, actor=None) -> NINVerification:
        provider = get_nin_provider()
        response = provider.verify_nin(food_handler)
        match_score, mismatch_fields = provider.calculate_match(food_handler, response)
        status = (
            NINVerificationStatus.VERIFIED
            if match_score >= cls.MATCH_THRESHOLD
            else NINVerificationStatus.MANUAL_REVIEW_REQUIRED
        )

        verification = NINVerification.objects.create(
            food_handler=food_handler,
            nin=food_handler.nin,
            provider=provider.provider_name,
            provider_reference=response.provider_reference,
            status=status,
            verified_full_name=response.full_name,
            verified_date_of_birth=response.date_of_birth,
            verified_gender=response.gender,
            verified_photo_url=response.photo_url,
            match_score=match_score,
            mismatch_fields=mismatch_fields,
            verified_at=verification_timestamp_for_status(status),
        )

        food_handler.current_status = (
            FoodHandlerStatus.CERTIFICATION_PENDING
            if status == NINVerificationStatus.VERIFIED
            else FoodHandlerStatus.NIN_PENDING
        )
        food_handler.save(update_fields=["current_status", "updated_at"])

        log_action(
            action=AuditAction.UPDATE,
            actor=actor,
            target=verification,
            metadata={"event": "nin_verification", "status": status},
        )
        return verification

    @classmethod
    @transaction.atomic
    def approve_override(cls, *, verification, reviewer, notes="") -> NINVerification:
        verification.status = NINVerificationStatus.OVERRIDE_APPROVED
        verification.reviewed_by = reviewer
        verification.review_notes = notes
        verification.save(update_fields=["status", "reviewed_by", "review_notes", "updated_at"])
        verification.food_handler.current_status = FoodHandlerStatus.CERTIFICATION_PENDING
        verification.food_handler.save(update_fields=["current_status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=reviewer, target=verification, metadata={"event": "nin_override_approved"})
        return verification

    @classmethod
    @transaction.atomic
    def reject_override(cls, *, verification, reviewer, notes="") -> NINVerification:
        verification.status = NINVerificationStatus.MISMATCH
        verification.reviewed_by = reviewer
        verification.review_notes = notes
        verification.save(update_fields=["status", "reviewed_by", "review_notes", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=reviewer, target=verification, metadata={"event": "nin_override_rejected"})
        return verification
