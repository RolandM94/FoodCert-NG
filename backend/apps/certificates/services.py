import hashlib
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import qrcode
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import UserRole
from apps.assessments.models import AssessmentStatus, FitnessDecision, StepStatus
from apps.assessments.services import AssessmentService
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.certificates.models import (
    Certificate,
    CertificateRequest,
    CertificateRequestStatus,
    CertificateStatus,
    VerificationResult,
)
from apps.food_handlers.models import FoodHandlerStatus
from apps.policy.models import StatePolicyConfig
from apps.payments.models import PaymentStatus
from apps.reports.models import GeneratedReport, ReportType
from apps.notifications.models import Notification, NotificationChannel, NotificationType

User = get_user_model()


def _absolute_media_url(path: str) -> str:
    return f"http://localhost:8000{settings.MEDIA_URL}{path}"


class CertificateService:
    @classmethod
    def _notify_assessment_people(cls, *, assessment, notification_type, subject, body, context_data=None):
        recipients = []
        if assessment.doctor_id:
            recipients.append(assessment.doctor)
        if assessment.food_handler.user_id:
            recipients.append(assessment.food_handler.user)
        recipients.extend(User.objects.filter(role=UserRole.FACILITY_ADMIN, organization_id=assessment.facility.organization_id, is_active=True))
        seen = set()
        for recipient in recipients:
            if not recipient or recipient.id in seen:
                continue
            seen.add(recipient.id)
            Notification.objects.create(
                recipient=recipient,
                notification_type=notification_type,
                channel=NotificationChannel.IN_APP,
                subject=subject,
                body=body,
                context_data=context_data or {},
            )

    @classmethod
    def policy_for_state(cls, state):
        config, _ = StatePolicyConfig.objects.get_or_create(state=state)
        return config

    @classmethod
    def validate_assessment_eligible(cls, assessment):
        if not AssessmentService.has_verified_identity(assessment):
            raise ValidationError("Food handler NIN must be verified or override-approved before certificate issuance.")
        if not assessment.payment_transaction or assessment.payment_transaction.status != PaymentStatus.SUCCESS:
            raise ValidationError("Assessment payment must be successful before certificate issuance.")
        if not assessment.facility.can_conduct_assessments:
            raise ValidationError("Certificate cannot be issued for an inactive or unapproved facility.")
        if not assessment.doctor or assessment.doctor.organization_id != assessment.facility.organization_id:
            raise ValidationError("Assessment doctor must be authorized under the facility.")
        if assessment.declaration_status != StepStatus.VALIDATED:
            raise ValidationError("Health declaration must be validated.")
        if assessment.physical_exam_status != StepStatus.COMPLETED:
            raise ValidationError("Physical examination must be completed.")
        if assessment.lab_status != StepStatus.REVIEWED:
            raise ValidationError("Lab results must be reviewed.")
        if assessment.vaccination_status != StepStatus.REVIEWED:
            raise ValidationError("Vaccination status must be reviewed.")
        if assessment.final_decision != FitnessDecision.FIT or not assessment.signed_at:
            raise ValidationError("Only fit, doctor-signed assessments can receive certificates.")

    @classmethod
    def validate_state_submission_ready(cls, assessment):
        cls.validate_assessment_eligible(assessment)
        if not GeneratedReport.objects.filter(
            filters__assessment_id=str(assessment.id),
            report_type__in=[
                ReportType.MEDICAL_EXAMINATION,
                ReportType.ASSESSMENT_COMPLETION,
            ],
        ).exists():
            raise ValidationError("A signed medical assessment report must be generated before State submission.")

    @classmethod
    @transaction.atomic
    def request_certificate(cls, *, assessment, actor, notes=""):
        cls.validate_assessment_eligible(assessment)
        existing_active = Certificate.objects.filter(
            food_handler=assessment.food_handler,
            status=CertificateStatus.ACTIVE,
            expiry_date__gte=timezone.localdate(),
        ).exclude(assessment=assessment)
        if existing_active.exists():
            raise ValidationError("Food handler already has an active certificate.")
        request, created = CertificateRequest.objects.get_or_create(
            assessment=assessment,
            defaults={"requested_by": actor, "request_notes": notes},
        )
        if not created and request.status == CertificateRequestStatus.REJECTED:
            request.status = CertificateRequestStatus.PENDING_VALIDATION
            request.request_notes = notes
            request.review_notes = ""
            request.facility_response = ""
            request.facility_responded_by = None
            request.facility_responded_at = None
            request.save(update_fields=["status", "request_notes", "review_notes", "facility_response", "facility_responded_by", "facility_responded_at", "updated_at"])
        log_action(
            action=AuditAction.CERTIFICATE_EVENT,
            actor=actor,
            target=request,
            metadata={"event": "certificate_requested", "status": request.status},
        )
        return request

    @classmethod
    @transaction.atomic
    def submit_to_state(cls, *, assessment, actor, notes=""):
        if actor.role != UserRole.FACILITY_ADMIN or actor.organization_id != assessment.facility.organization_id:
            raise PermissionDenied("Only this facility's admin can submit assessments to State validation.")
        cls.validate_state_submission_ready(assessment)
        request, created = CertificateRequest.objects.get_or_create(
            assessment=assessment,
            defaults={"requested_by": actor, "request_notes": notes},
        )
        if not created:
            if request.status == CertificateRequestStatus.CORRECTION_REQUESTED:
                raise ValidationError("Respond to the State clarification request before resubmitting.")
            if request.status == CertificateRequestStatus.REJECTED:
                request.status = CertificateRequestStatus.PENDING_VALIDATION
                request.requested_by = actor
                request.request_notes = notes
                request.review_notes = ""
                request.facility_response = ""
                request.facility_responded_by = None
                request.facility_responded_at = None
                request.save(update_fields=["status", "requested_by", "request_notes", "review_notes", "facility_response", "facility_responded_by", "facility_responded_at", "updated_at"])
        assessment.status = AssessmentStatus.SUBMITTED_FOR_STATE_VALIDATION
        assessment.save(update_fields=["status", "updated_at"])
        cls._notify_assessment_people(
            assessment=assessment,
            notification_type=NotificationType.COMPLIANCE_NOTICE,
            subject="Assessment submitted to State",
            body="A fit assessment has been submitted for State certificate validation.",
            context_data={"assessment_id": str(assessment.id), "certificate_request_id": str(request.id)},
        )
        log_action(
            action=AuditAction.CERTIFICATE_EVENT,
            actor=actor,
            target=request,
            metadata={"event": "facility_submitted_assessment_to_state", "assessment_id": str(assessment.id), "status": request.status},
        )
        return request

    @classmethod
    @transaction.atomic
    def respond_to_clarification(cls, *, certificate_request, actor, response):
        assessment = certificate_request.assessment
        if actor.role != UserRole.FACILITY_ADMIN or actor.organization_id != assessment.facility.organization_id:
            raise PermissionDenied("Only this facility's admin can respond to State clarification.")
        if certificate_request.status != CertificateRequestStatus.CORRECTION_REQUESTED:
            raise ValidationError("This certificate request is not awaiting facility clarification.")
        if not response.strip():
            raise ValidationError("Clarification response is required.")
        cls.validate_state_submission_ready(assessment)
        certificate_request.status = CertificateRequestStatus.PENDING_VALIDATION
        certificate_request.facility_response = response
        certificate_request.facility_responded_by = actor
        certificate_request.facility_responded_at = timezone.now()
        certificate_request.save(update_fields=["status", "facility_response", "facility_responded_by", "facility_responded_at", "updated_at"])
        assessment.status = AssessmentStatus.STATE_CLARIFICATION_RESPONDED
        assessment.save(update_fields=["status", "updated_at"])
        log_action(
            action=AuditAction.CERTIFICATE_EVENT,
            actor=actor,
            target=certificate_request,
            metadata={"event": "facility_certificate_clarification_responded", "assessment_id": str(assessment.id)},
        )
        if certificate_request.reviewed_by:
            Notification.objects.create(
                recipient=certificate_request.reviewed_by,
                notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
                channel=NotificationChannel.IN_APP,
                subject="Certificate clarification response received",
                body="A facility has responded to a State certificate validation clarification request.",
                context_data={
                    "certificate_request_id": str(certificate_request.id),
                    "assessment_id": str(assessment.id),
                    "facility_id": str(assessment.facility_id),
                },
            )
        return certificate_request

    @classmethod
    @transaction.atomic
    def request_clarification(cls, *, request, reviewer, notes):
        cls.ensure_state_reviewer(reviewer, request)
        request.status = CertificateRequestStatus.CORRECTION_REQUESTED
        request.reviewed_by = reviewer
        request.review_notes = notes
        request.reviewed_at = timezone.now()
        request.save(update_fields=["status", "reviewed_by", "review_notes", "reviewed_at", "updated_at"])
        request.assessment.status = AssessmentStatus.STATE_CLARIFICATION_REQUESTED
        request.assessment.save(update_fields=["status", "updated_at"])
        log_action(
            action=AuditAction.CERTIFICATE_EVENT,
            actor=reviewer,
            target=request,
            metadata={"event": "certificate_request_clarification_requested"},
        )
        facility_admins = User.objects.filter(role=UserRole.FACILITY_ADMIN, organization_id=request.assessment.facility.organization_id, is_active=True)
        for admin in facility_admins:
            Notification.objects.create(
                recipient=admin,
                notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
                channel=NotificationChannel.IN_APP,
                subject="State clarification requested",
                body="State validation requested clarification on a certificate submission.",
                context_data={
                    "certificate_request_id": str(request.id),
                    "assessment_id": str(request.assessment_id),
                    "facility_id": str(request.assessment.facility_id),
                },
            )
        return request

    @classmethod
    def ensure_state_reviewer(cls, user, request):
        if user.role == UserRole.SUPER_ADMIN:
            return
        if user.role == UserRole.STATE_ADMIN and request.assessment.facility.state_id == user.state_id:
            return
        raise PermissionDenied("Only the issuing state ministry can review this certificate request.")

    @classmethod
    @transaction.atomic
    def approve_request(cls, *, request, reviewer, notes=""):
        cls.ensure_state_reviewer(reviewer, request)
        cls.validate_assessment_eligible(request.assessment)
        request.status = CertificateRequestStatus.APPROVED
        request.reviewed_by = reviewer
        request.review_notes = notes
        request.reviewed_at = timezone.now()
        request.save(update_fields=["status", "reviewed_by", "review_notes", "reviewed_at", "updated_at"])
        request.assessment.status = AssessmentStatus.APPROVED_BY_STATE
        request.assessment.save(update_fields=["status", "updated_at"])
        cls._notify_assessment_people(
            assessment=request.assessment,
            notification_type=NotificationType.COMPLIANCE_NOTICE,
            subject="Assessment approved by State",
            body="State validation approved the certificate request.",
            context_data={"assessment_id": str(request.assessment_id), "certificate_request_id": str(request.id)},
        )
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=reviewer, target=request, metadata={"event": "certificate_request_approved"})
        return request

    @classmethod
    @transaction.atomic
    def reject_request(cls, *, request, reviewer, notes=""):
        cls.ensure_state_reviewer(reviewer, request)
        request.status = CertificateRequestStatus.REJECTED
        request.reviewed_by = reviewer
        request.review_notes = notes
        request.reviewed_at = timezone.now()
        request.save(update_fields=["status", "reviewed_by", "review_notes", "reviewed_at", "updated_at"])
        request.assessment.status = AssessmentStatus.REJECTED_BY_STATE
        request.assessment.save(update_fields=["status", "updated_at"])
        cls._notify_assessment_people(
            assessment=request.assessment,
            notification_type=NotificationType.COMPLIANCE_NOTICE,
            subject="Assessment rejected by State",
            body="State validation rejected the certificate request.",
            context_data={"assessment_id": str(request.assessment_id), "certificate_request_id": str(request.id)},
        )
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=reviewer, target=request, metadata={"event": "certificate_request_rejected"})
        return request

    @classmethod
    def certificate_number(cls, state_code):
        return f"FCN-{state_code}-{timezone.now():%Y%m%d}-{uuid4().hex[:8].upper()}"

    @classmethod
    def signature_hash(cls, *, certificate_number, assessment_id, food_handler_id, issue_date, expiry_date):
        payload = f"{certificate_number}:{assessment_id}:{food_handler_id}:{issue_date}:{expiry_date}:{settings.SECRET_KEY}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def build_verification_url(cls, certificate_number):
        return f"http://localhost:3000/verify/{certificate_number}"

    @classmethod
    def write_qr_code(cls, *, certificate_number, verification_url):
        relative_path = f"certificates/qr/{certificate_number}.png"
        output_path = Path(settings.MEDIA_ROOT) / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image = qrcode.make(verification_url)
        image.save(output_path)
        return _absolute_media_url(relative_path)

    @classmethod
    def write_pdf(cls, *, certificate):
        relative_path = f"certificates/pdf/{certificate.certificate_number}.pdf"
        output_path = Path(settings.MEDIA_ROOT) / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        pdf.setTitle(certificate.certificate_number)
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(72, 780, "FoodCert NG Medical Fitness Certificate")
        pdf.setFont("Helvetica", 11)
        lines = [
            ("Certificate Number", certificate.certificate_number),
            ("Food Handler", certificate.food_handler.full_name),
            ("Masked NIN", certificate.food_handler.masked_nin),
            ("Facility", certificate.facility.facility_name),
            ("Doctor", certificate.doctor.get_full_name() or certificate.doctor.email),
            ("Issuing State", certificate.issuing_state.name),
            ("Issue Date", str(certificate.issue_date)),
            ("Expiry Date", str(certificate.expiry_date)),
            ("Fitness Status", certificate.assessment.final_decision),
            ("Verification URL", certificate.verification_url),
            ("Digital Hash", certificate.digital_signature_hash),
        ]
        y = 740
        for label, value in lines:
            pdf.drawString(72, y, f"{label}: {value}")
            y -= 24
        pdf.showPage()
        pdf.save()
        output_path.write_bytes(buffer.getvalue())
        return _absolute_media_url(relative_path)

    @classmethod
    @transaction.atomic
    def issue_certificate(cls, *, assessment, actor=None):
        cls.validate_assessment_eligible(assessment)
        policy = cls.policy_for_state(assessment.facility.state)
        request = getattr(assessment, "certificate_request", None)
        if policy.requires_state_certificate_validation:
            if not request or request.status != CertificateRequestStatus.APPROVED:
                raise ValidationError("State ministry validation is required before certificate issuance.")
            issued_by = request.reviewed_by
        else:
            issued_by = actor if getattr(actor, "role", None) in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN} else None
        certificate = getattr(assessment, "certificate", None)
        if certificate:
            return certificate
        issue_date = timezone.localdate()
        expiry_date = issue_date + timezone.timedelta(days=30 * policy.certificate_validity_months)
        number = cls.certificate_number(assessment.facility.state.code)
        verification_url = cls.build_verification_url(number)
        signature = cls.signature_hash(
            certificate_number=number,
            assessment_id=assessment.id,
            food_handler_id=assessment.food_handler_id,
            issue_date=issue_date,
            expiry_date=expiry_date,
        )
        certificate = Certificate.objects.create(
            certificate_number=number,
            food_handler=assessment.food_handler,
            assessment=assessment,
            employer=assessment.employer,
            facility=assessment.facility,
            doctor=assessment.doctor,
            issuing_state=assessment.facility.state,
            issued_by_state_user=issued_by,
            issue_date=issue_date,
            expiry_date=expiry_date,
            verification_url=verification_url,
            digital_signature_hash=signature,
        )
        certificate.qr_code_url = cls.write_qr_code(certificate_number=number, verification_url=verification_url)
        certificate.pdf_url = cls.write_pdf(certificate=certificate)
        certificate.save(update_fields=["qr_code_url", "pdf_url", "updated_at"])
        assessment.status = AssessmentStatus.CERTIFICATE_ISSUED
        assessment.save(update_fields=["status", "updated_at"])
        assessment.food_handler.current_status = FoodHandlerStatus.FIT
        assessment.food_handler.save(update_fields=["current_status", "updated_at"])
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=actor or issued_by, target=certificate, metadata={"event": "certificate_issued"})
        return certificate

    @classmethod
    @transaction.atomic
    def revoke(cls, *, certificate, actor, reason=""):
        certificate.status = CertificateStatus.REVOKED
        certificate.revoked_by = actor
        certificate.revoked_at = timezone.now()
        certificate.revocation_reason = reason
        certificate.save(update_fields=["status", "revoked_by", "revoked_at", "revocation_reason", "updated_at"])
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=actor, target=certificate, metadata={"event": "certificate_revoked"})
        return certificate

    @classmethod
    @transaction.atomic
    def suspend(cls, *, certificate, actor, reason=""):
        certificate.status = CertificateStatus.SUSPENDED
        certificate.revoked_by = actor
        certificate.revoked_at = timezone.now()
        certificate.revocation_reason = reason
        certificate.save(update_fields=["status", "revoked_by", "revoked_at", "revocation_reason", "updated_at"])
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=actor, target=certificate, metadata={"event": "certificate_suspended"})
        return certificate

    @classmethod
    def verification_result_for(cls, certificate):
        expected_hash = cls.signature_hash(
            certificate_number=certificate.certificate_number,
            assessment_id=certificate.assessment_id,
            food_handler_id=certificate.food_handler_id,
            issue_date=certificate.issue_date,
            expiry_date=certificate.expiry_date,
        )
        if expected_hash != certificate.digital_signature_hash:
            return VerificationResult.INVALID
        if certificate.status == CertificateStatus.REVOKED:
            return VerificationResult.REVOKED
        if certificate.status == CertificateStatus.SUSPENDED:
            return VerificationResult.SUSPENDED
        if certificate.status != CertificateStatus.ACTIVE:
            return VerificationResult.INVALID
        if certificate.is_expired:
            return VerificationResult.EXPIRED
        return VerificationResult.VALID
