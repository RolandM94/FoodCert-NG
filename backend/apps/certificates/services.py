import hashlib
from io import BytesIO
from pathlib import Path
import secrets
from textwrap import wrap
from typing import Optional
from uuid import uuid4

import qrcode
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import UserRole
from apps.assessments.models import AssessmentStatus, FitnessDecision, StepStatus
from apps.assessments.services import AssessmentService
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.certificates.models import (
    AccreditationCertificate,
    AccreditationCertificateType,
    Certificate,
    CertificateRequest,
    CertificateRequestStatus,
    CertificateStatus,
    CertificateTemplate,
    CertificateTemplateScope,
    VerificationResult,
)
from apps.employers.models import ComplianceStatus
from apps.facilities.models import AccreditationStatus
from apps.food_handlers.models import FoodHandlerStatus
from apps.illness.models import ClearanceStatus, IllnessReport
from apps.policy.models import StatePolicyConfig
from apps.payments.models import PaymentStatus
from apps.reports.models import GeneratedReport, ReportType
from apps.notifications.models import Notification, NotificationCategory
from apps.notifications.services import NotificationService

User = get_user_model()


def _absolute_media_url(path: str) -> str:
    return f"http://localhost:8000{settings.MEDIA_URL}{path}"


def _media_path_from_url(url: str) -> Optional[Path]:
    if not url:
        return None
    media_prefix = f"http://localhost:8000{settings.MEDIA_URL}"
    if url.startswith(media_prefix):
        return Path(settings.MEDIA_ROOT) / url.replace(media_prefix, "")
    if url.startswith(settings.MEDIA_URL):
        return Path(settings.MEDIA_ROOT) / url.replace(settings.MEDIA_URL, "", 1)
    return None


class CertificateService:
    @classmethod
    def _notify_assessment_people(cls, *, assessment, category, title, message):
        recipients = []
        if assessment.doctor_id:
            recipients.append({
                "user_id": str(assessment.doctor_id),
                "email": assessment.doctor.email or "",
                "recipient_type": "doctor",
            })
        if assessment.food_handler.user_id:
            recipients.append({
                "user_id": str(assessment.food_handler.user_id),
                "email": assessment.food_handler.user.email or "",
                "recipient_type": "food_handler",
            })
        facility_admins = User.objects.filter(
            role=UserRole.FACILITY_ADMIN,
            organization_id=assessment.facility.organization_id,
            is_active=True,
        )
        for admin in facility_admins:
            recipients.append({
                "user_id": str(admin.id),
                "email": admin.email or "",
                "recipient_type": "facility_admin",
                "organization_id": str(admin.organization_id) if admin.organization_id else "",
            })
        NotificationService.send(
            category=category,
            title=title,
            message=message,
            recipients=recipients,
        )

    @classmethod
    def policy_for_state(cls, state):
        config, _ = StatePolicyConfig.objects.get_or_create(state=state)
        return config

    @classmethod
    def validate_assessment_eligible(cls, assessment):
        if not AssessmentService.profile_complete(assessment):
            raise ValidationError("Food handler profile must be complete before certificate issuance.")
        if not AssessmentService.has_verified_identity(assessment):
            raise ValidationError("Food handler NIN must be verified or override-approved before certificate issuance.")
        if not assessment.payment_transaction or assessment.payment_transaction.status != PaymentStatus.SUCCESS:
            raise ValidationError("Assessment payment must be successful before certificate issuance.")
        if not assessment.facility.can_conduct_assessments:
            raise ValidationError("Certificate cannot be issued for an inactive or unapproved facility.")
        if not AssessmentService.has_verified_identity(assessment):
            raise ValidationError("Identity must be verified before certificate issuance or State submission.")
        assessment_date = timezone.localtime(assessment.created_at).date() if assessment.created_at else timezone.localdate()
        if (
            not assessment.facility.accreditation_start_date
            or assessment.facility.accreditation_start_date > assessment_date
            or not assessment.facility.accreditation_expiry_date
            or assessment.facility.accreditation_expiry_date < assessment_date
        ):
            raise ValidationError("Facility accreditation must have been valid when the assessment was conducted.")
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
        if assessment.food_handler.current_status in {FoodHandlerStatus.EXCLUDED, FoodHandlerStatus.TEMPORARILY_EXCLUDED}:
            raise ValidationError("Food handler has an unresolved exclusion and cannot receive a certificate.")
        unresolved_illness = IllnessReport.objects.filter(
            food_handler=assessment.food_handler,
            clearance_required=True,
            clearance_status__in=[
                ClearanceStatus.PENDING,
                ClearanceStatus.UNDER_REVIEW,
                ClearanceStatus.CLEARANCE_REQUIRED,
            ],
        ).exists()
        if unresolved_illness:
            raise ValidationError("Food handler has an unresolved illness or return-to-work clearance block.")

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
            category=NotificationCategory.ENFORCEMENT,
            title="Assessment submitted to State",
            message="A fit assessment has been submitted for State certificate validation.",
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
                category=NotificationCategory.SYSTEM,
                title="Certificate clarification response received",
                message="A facility has responded to a State certificate validation clarification request.",
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
                category=NotificationCategory.SYSTEM,
                title="State clarification requested",
                message="State validation requested clarification on a certificate submission.",
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
            category=NotificationCategory.ENFORCEMENT,
            title="Assessment approved by State",
            message="State validation approved the certificate request.",
        )
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=reviewer, target=request, metadata={"event": "certificate_request_approved"})
        return request

    @classmethod
    @transaction.atomic
    def approve_and_generate(cls, *, request, reviewer, notes=""):
        certificate_request = cls.approve_request(request=request, reviewer=reviewer, notes=notes)
        certificate = cls.issue_certificate(assessment=certificate_request.assessment, actor=reviewer)
        log_action(
            action=AuditAction.CERTIFICATE_EVENT,
            actor=reviewer,
            target=certificate,
            metadata={
                "event": "certificate_request_approved_and_generated",
                "certificate_request_id": str(certificate_request.id),
            },
        )
        return certificate_request, certificate

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
            category=NotificationCategory.ENFORCEMENT,
            title="Assessment rejected by State",
            message="State validation rejected the certificate request.",
        )
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=reviewer, target=request, metadata={"event": "certificate_request_rejected"})
        return request

    @classmethod
    def certificate_number(cls, state_code):
        today = timezone.localdate()
        prefix = f"FCNG-{state_code}-{today:%Y}"
        sequence = Certificate.objects.filter(certificate_number__startswith=f"{prefix}-").count() + 1
        while True:
            sequence_part = f"{sequence:06d}"
            check = secrets.token_hex(1).upper()
            number = f"{prefix}-{sequence_part}-{check}"
            if not Certificate.objects.filter(certificate_number=number).exists():
                return number
            sequence += 1

    @classmethod
    def verification_token(cls):
        while True:
            token = secrets.token_urlsafe(32)
            if not Certificate.objects.filter(verification_token=token).exists() and not AccreditationCertificate.objects.filter(verification_token=token).exists():
                return token

    @classmethod
    def accreditation_certificate_number(cls, state_code, certificate_type):
        today = timezone.localdate()
        type_part = "EMP" if certificate_type == AccreditationCertificateType.EMPLOYER else "FAC"
        prefix = f"FCNG-{state_code}-{today:%Y}-{type_part}"
        sequence = AccreditationCertificate.objects.filter(certificate_number__startswith=f"{prefix}-").count() + 1
        while True:
            number = f"{prefix}-{sequence:06d}-{secrets.token_hex(1).upper()}"
            if not AccreditationCertificate.objects.filter(certificate_number=number).exists():
                return number
            sequence += 1

    @classmethod
    def signature_hash(
        cls,
        *,
        certificate_number,
        assessment_id,
        food_handler_id,
        issue_date,
        expiry_date,
        facility_id=None,
        issuing_state_id=None,
        doctor_id=None,
        verification_token="",
    ):
        payload = ":".join(
            [
                str(certificate_number),
                str(assessment_id),
                str(food_handler_id),
                str(facility_id or ""),
                str(issuing_state_id or ""),
                str(doctor_id or ""),
                str(issue_date),
                str(expiry_date),
                str(verification_token or ""),
                settings.SECRET_KEY,
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def accreditation_signature_hash(
        cls,
        *,
        certificate_number,
        certificate_type,
        owner_id,
        issue_date,
        expiry_date,
        issuing_state_id=None,
        verification_token="",
    ):
        payload = ":".join(
            [
                str(certificate_number),
                str(certificate_type),
                str(owner_id),
                str(issuing_state_id or ""),
                str(issue_date),
                str(expiry_date),
                str(verification_token or ""),
                settings.SECRET_KEY,
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def build_verification_url(cls, verification_token):
        return f"http://localhost:3000/verify/{verification_token}"

    @classmethod
    def active_national_policy(cls):
        from apps.policy.models import NationalPolicyConfig

        policy = NationalPolicyConfig.objects.order_by("-updated_at").first()
        if not policy:
            policy = NationalPolicyConfig.objects.create()
        return policy

    @classmethod
    def default_template_for_state(cls, state):
        policy = cls.active_national_policy()
        if getattr(policy, "state_certificate_template_overrides_enabled", True):
            state_templates = CertificateTemplate.objects.filter(
                scope=CertificateTemplateScope.STATE,
                state=state,
            )
            state_template = state_templates.filter(
                scope=CertificateTemplateScope.STATE,
                state=state,
                is_active=True,
                is_default=True,
            ).first()
            if state_template:
                return state_template
            if state_templates.exists():
                return None
        national_templates = CertificateTemplate.objects.filter(
            scope=CertificateTemplateScope.NATIONAL,
        )
        national_template = national_templates.filter(
            scope=CertificateTemplateScope.NATIONAL,
            is_active=True,
            is_default=True,
        ).first()
        if national_template:
            return national_template
        if national_templates.exists():
            return None
        return CertificateTemplate.objects.create(
            name="FoodCert NG Default",
            scope=CertificateTemplateScope.NATIONAL,
            ministry_name="FoodCert NG",
            is_default=True,
            created_by=None,
        )

    @classmethod
    def active_template_for_state(cls, state):
        template = cls.default_template_for_state(state)
        if not template or not template.is_active:
            raise ValidationError("An active certificate template is required before certificate issuance.")
        return template

    @classmethod
    def write_qr_code(cls, *, certificate_number, verification_url):
        relative_path = f"certificates/qr/{certificate_number}.png"
        output_path = Path(settings.MEDIA_ROOT) / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
        qr.add_data(verification_url)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")
        image.save(output_path)
        return _absolute_media_url(relative_path)

    @classmethod
    def write_pdf(cls, *, certificate):
        template = certificate.template or cls.default_template_for_state(certificate.issuing_state)
        relative_path = f"certificates/pdf/{certificate.certificate_number}.pdf"
        output_path = Path(settings.MEDIA_ROOT) / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        pdf.setTitle(certificate.certificate_number)

        accent_color = template.accent_color if template and template.accent_color else "#0f5132"
        deep_green = colors.HexColor(accent_color)
        pale_green = colors.HexColor("#edf7ef")
        ink = colors.HexColor("#17201b")
        muted = colors.HexColor("#52645a")

        # A restrained security pattern keeps the document formal without
        # competing with the certificate text when printed in grayscale.
        pdf.setFillColor(colors.white)
        pdf.rect(0, 0, width, height, stroke=0, fill=1)
        pdf.setStrokeColor(colors.HexColor("#e2efe5"))
        pdf.setLineWidth(0.35)
        for offset in range(-260, 760, 18):
            pdf.line(26, offset, width - 26, offset + 420)
            pdf.line(26, offset + 420, width - 26, offset)

        pdf.setStrokeColor(deep_green)
        pdf.setLineWidth(3)
        pdf.rect(22, 22, width - 44, height - 44, stroke=1, fill=0)
        pdf.setLineWidth(0.9)
        pdf.rect(30, 30, width - 60, height - 60, stroke=1, fill=0)
        pdf.setLineWidth(0.45)
        pdf.rect(36, 36, width - 72, height - 72, stroke=1, fill=0)

        for x, y in [(36, 36), (width - 36, 36), (36, height - 36), (width - 36, height - 36)]:
            pdf.setFillColor(deep_green)
            pdf.circle(x, y, 3.5, stroke=0, fill=1)

        coat_of_arms = Path(__file__).resolve().parent / "assets" / "nigeria-coat-of-arms.png"
        if coat_of_arms.exists():
            pdf.drawImage(
                ImageReader(str(coat_of_arms)),
                width / 2 - 36,
                height - 129,
                width=72,
                height=62,
                preserveAspectRatio=True,
                mask="auto",
                anchor="c",
            )

        pdf.setFillColor(ink)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawCentredString(width / 2, height - 148, "FEDERAL REPUBLIC OF NIGERIA")
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawCentredString(width / 2, height - 164, f"{certificate.issuing_state.name.upper()} STATE MINISTRY OF HEALTH")
        pdf.setStrokeColor(deep_green)
        pdf.setLineWidth(0.8)
        pdf.line(104, height - 178, width - 104, height - 178)

        pdf.setFillColor(deep_green)
        pdf.setFont("Times-BoldItalic", 24)
        pdf.drawCentredString(width / 2, height - 215, "Food Handler Certificate")
        pdf.setFillColor(ink)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawCentredString(width / 2, height - 237, "MEDICAL FITNESS TO HANDLE FOOD")
        pdf.setFillColor(muted)
        pdf.setFont("Helvetica", 8.5)
        pdf.drawCentredString(width / 2, height - 253, "Issued under the FoodCert NG national food handler certification programme")

        qr_path = _media_path_from_url(certificate.qr_code_url)
        if qr_path and qr_path.exists():
            pdf.drawImage(ImageReader(str(qr_path)), 72, 91, width=86, height=86, preserveAspectRatio=True, mask="auto")
        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.setFillColor(muted)
        pdf.drawCentredString(115, 82, "SCAN TO VERIFY")

        branch_name = certificate.business_branch.name if certificate.business_branch_id else "Not linked"
        employer_name = certificate.employer.business_name if certificate.employer_id else "Not linked"
        pdf.setFillColor(ink)
        pdf.setFont("Times-Roman", 12)
        pdf.drawCentredString(width / 2, height - 292, "This is to certify that")
        pdf.setFillColor(deep_green)
        pdf.setFont("Times-Bold", 22)
        pdf.drawCentredString(width / 2, height - 324, certificate.food_handler.full_name.upper()[:52])
        pdf.setStrokeColor(deep_green)
        pdf.setLineWidth(0.6)
        pdf.line(116, height - 334, width - 116, height - 334)
        pdf.setFillColor(ink)
        pdf.setFont("Times-Roman", 11)
        pdf.drawCentredString(width / 2, height - 358, "has completed the required medical assessment and is certified")
        pdf.drawCentredString(width / 2, height - 375, "fit to handle food within the validity period stated below.")

        pdf.setFillColor(pale_green)
        pdf.roundRect(72, height - 524, width - 144, 112, 4, stroke=0, fill=1)
        details = [
            ("Certificate No.", certificate.certificate_number),
            ("Food Handler ID", certificate.food_handler.system_identifier),
            ("Employer", employer_name),
            ("Business Branch", branch_name),
            ("Medical Facility", certificate.facility.facility_name),
            ("Issuing State", certificate.issuing_state.name),
            ("Issue Date", certificate.issue_date.strftime("%d %b %Y")),
            ("Expiry Date", certificate.expiry_date.strftime("%d %b %Y")),
        ]
        for index, (label, value) in enumerate(details):
            column = index % 2
            row = index // 2
            x = 88 + column * 225
            y = height - 434 - row * 24
            pdf.setFillColor(muted)
            pdf.setFont("Helvetica-Bold", 7)
            pdf.drawString(x, y, label.upper())
            pdf.setFillColor(ink)
            pdf.setFont("Helvetica-Bold", 8.6)
            pdf.drawString(x, y - 11, str(value or "Not provided")[:42])

        status_label = certificate.effective_status.replace("_", " ").upper()
        status_fill = colors.HexColor("#dff5e7") if certificate.effective_status == CertificateStatus.ACTIVE else colors.HexColor("#fee2e2")
        status_ink = colors.HexColor("#0f5132") if certificate.effective_status == CertificateStatus.ACTIVE else colors.HexColor("#991b1b")
        pdf.setFillColor(status_fill)
        pdf.roundRect(width - 172, height - 567, 100, 21, 3, stroke=0, fill=1)
        pdf.setFillColor(status_ink)
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawCentredString(width - 122, height - 560, status_label)

        signature_name = template.signatory_name or f"{certificate.issuing_state.name} State Ministry of Health"
        pdf.setStrokeColor(ink)
        pdf.setLineWidth(0.7)
        pdf.line(width - 286, 148, width - 74, 148)
        pdf.setFillColor(ink)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawCentredString(width - 180, 134, signature_name[:42])
        pdf.setFont("Helvetica", 8)
        pdf.drawCentredString(width - 180, 122, (template.signatory_title or "Authorized Issuing Authority")[:48])

        pdf.setFont("Helvetica", 7.2)
        pdf.setFillColor(muted)
        footer_lines = wrap(template.footer_note or "This certificate confirms fitness status only.", width=112)[:2]
        for index, line in enumerate(footer_lines):
            pdf.drawString(72, 70 - index * 10, line)
        pdf.drawString(72, 48, "Verify authenticity using the QR code or public verification URL. Alteration renders this certificate invalid.")
        pdf.drawRightString(width - 72, 40, f"Serial: {certificate.certificate_number}")
        pdf.showPage()
        pdf.save()
        output_path.write_bytes(buffer.getvalue())
        return _absolute_media_url(relative_path)

    @classmethod
    def write_accreditation_pdf(cls, *, certificate):
        relative_path = f"certificates/pdf/{certificate.certificate_number}.pdf"
        output_path = Path(settings.MEDIA_ROOT) / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        pdf.setTitle(certificate.certificate_number)
        deep_green = colors.HexColor("#0f5132")
        pale_green = colors.HexColor("#edf7ef")
        ink = colors.HexColor("#17201b")
        muted = colors.HexColor("#52645a")

        pdf.setFillColor(colors.white)
        pdf.rect(0, 0, width, height, stroke=0, fill=1)
        pdf.setStrokeColor(deep_green)
        pdf.setLineWidth(3)
        pdf.rect(22, 22, width - 44, height - 44, stroke=1, fill=0)
        pdf.setLineWidth(0.9)
        pdf.rect(32, 32, width - 64, height - 64, stroke=1, fill=0)

        coat_of_arms = Path(__file__).resolve().parent / "assets" / "nigeria-coat-of-arms.png"
        if coat_of_arms.exists():
            pdf.drawImage(ImageReader(str(coat_of_arms)), width / 2 - 36, height - 128, width=72, height=62, preserveAspectRatio=True, mask="auto")

        pdf.setFillColor(ink)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawCentredString(width / 2, height - 148, "FEDERAL REPUBLIC OF NIGERIA")
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawCentredString(width / 2, height - 164, f"{certificate.issuing_state.name.upper()} STATE MINISTRY OF HEALTH")
        pdf.setStrokeColor(deep_green)
        pdf.line(104, height - 178, width - 104, height - 178)

        title = "Employer Accreditation Certificate" if certificate.certificate_type == AccreditationCertificateType.EMPLOYER else "Medical Facility Accreditation Certificate"
        pdf.setFillColor(deep_green)
        pdf.setFont("Times-BoldItalic", 23)
        pdf.drawCentredString(width / 2, height - 218, title)
        pdf.setFillColor(ink)
        pdf.setFont("Times-Roman", 12)
        pdf.drawCentredString(width / 2, height - 266, "This is to certify that")
        pdf.setFillColor(deep_green)
        pdf.setFont("Times-Bold", 22)
        pdf.drawCentredString(width / 2, height - 300, certificate.owner_name.upper()[:54])
        pdf.setStrokeColor(deep_green)
        pdf.line(116, height - 311, width - 116, height - 311)
        pdf.setFillColor(ink)
        pdf.setFont("Times-Roman", 11)
        pdf.drawCentredString(width / 2, height - 340, "has met the applicable FoodCert NG accreditation requirements")
        pdf.drawCentredString(width / 2, height - 357, "and is recognised for the validity period stated below.")

        pdf.setFillColor(pale_green)
        pdf.roundRect(72, height - 508, width - 144, 102, 4, stroke=0, fill=1)
        details = [
            ("Certificate No.", certificate.certificate_number),
            ("Certificate Type", certificate.get_certificate_type_display()),
            ("Owner Type", certificate.owner_type.title()),
            ("Issuing State", certificate.issuing_state.name),
            ("Issue Date", certificate.issue_date.strftime("%d %b %Y")),
            ("Expiry Date", certificate.expiry_date.strftime("%d %b %Y")),
        ]
        for index, (label, value) in enumerate(details):
            column = index % 2
            row = index // 2
            x = 88 + column * 225
            y = height - 430 - row * 26
            pdf.setFillColor(muted)
            pdf.setFont("Helvetica-Bold", 7)
            pdf.drawString(x, y, label.upper())
            pdf.setFillColor(ink)
            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawString(x, y - 12, str(value or "Not provided")[:42])

        qr_path = _media_path_from_url(certificate.qr_code_url)
        if qr_path and qr_path.exists():
            pdf.drawImage(ImageReader(str(qr_path)), 72, 91, width=86, height=86, preserveAspectRatio=True, mask="auto")
        pdf.setFillColor(muted)
        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawCentredString(115, 82, "SCAN TO VERIFY")

        pdf.setStrokeColor(ink)
        pdf.line(width - 286, 148, width - 74, 148)
        pdf.setFillColor(ink)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawCentredString(width - 180, 134, f"{certificate.issuing_state.name} State Ministry of Health"[:42])
        pdf.setFont("Helvetica", 8)
        pdf.drawCentredString(width - 180, 122, "Authorized Issuing Authority")

        pdf.setFont("Helvetica", 7.2)
        pdf.setFillColor(muted)
        pdf.drawString(72, 56, "Verify authenticity using the QR code or public verification URL. Alteration renders this certificate invalid.")
        pdf.drawRightString(width - 72, 40, f"Serial: {certificate.certificate_number}")
        pdf.showPage()
        pdf.save()
        output_path.write_bytes(buffer.getvalue())
        return _absolute_media_url(relative_path)

    @classmethod
    @transaction.atomic
    def issue_facility_accreditation_certificate(cls, *, application, actor=None):
        facility = application.facility
        if application.application_status != AccreditationStatus.APPROVED or facility.accreditation_status != AccreditationStatus.APPROVED:
            raise ValidationError("Facility accreditation must be approved before certificate issuance.")
        issue_date = facility.accreditation_start_date or timezone.localdate()
        expiry_date = facility.accreditation_expiry_date or facility.default_expiry_date(issue_date)
        certificate = AccreditationCertificate.objects.filter(
            certificate_type=AccreditationCertificateType.FACILITY,
            facility=facility,
            status=CertificateStatus.ACTIVE,
        ).order_by("-issue_date", "-created_at").first()
        if certificate:
            return certificate
        return cls._issue_accreditation_certificate(
            certificate_type=AccreditationCertificateType.FACILITY,
            owner=facility,
            issuing_state=facility.state,
            issue_date=issue_date,
            expiry_date=expiry_date,
            actor=actor,
            facility_application=application,
        )

    @classmethod
    @transaction.atomic
    def issue_employer_accreditation_certificate(cls, *, employer, actor=None):
        if employer.compliance_status != ComplianceStatus.COMPLIANT:
            raise ValidationError("Employer must be compliant before accreditation certificate issuance.")
        certificate = AccreditationCertificate.objects.filter(
            certificate_type=AccreditationCertificateType.EMPLOYER,
            employer=employer,
            status=CertificateStatus.ACTIVE,
            expiry_date__gte=timezone.localdate(),
        ).order_by("-issue_date", "-created_at").first()
        if certificate:
            return certificate
        issue_date = timezone.localdate()
        expiry_date = issue_date + timezone.timedelta(days=365)
        return cls._issue_accreditation_certificate(
            certificate_type=AccreditationCertificateType.EMPLOYER,
            owner=employer,
            issuing_state=employer.state,
            issue_date=issue_date,
            expiry_date=expiry_date,
            actor=actor,
        )

    @classmethod
    def _issue_accreditation_certificate(cls, *, certificate_type, owner, issuing_state, issue_date, expiry_date, actor=None, facility_application=None):
        number = cls.accreditation_certificate_number(issuing_state.code, certificate_type)
        token = cls.verification_token()
        verification_url = cls.build_verification_url(token)
        owner_id = owner.id
        signature = cls.accreditation_signature_hash(
            certificate_number=number,
            certificate_type=certificate_type,
            owner_id=owner_id,
            issue_date=issue_date,
            expiry_date=expiry_date,
            issuing_state_id=issuing_state.id,
            verification_token=token,
        )
        certificate = AccreditationCertificate.objects.create(
            certificate_number=number,
            certificate_type=certificate_type,
            public_id=uuid4(),
            verification_token=token,
            employer=owner if certificate_type == AccreditationCertificateType.EMPLOYER else None,
            facility=owner if certificate_type == AccreditationCertificateType.FACILITY else None,
            facility_application=facility_application,
            issuing_state=issuing_state,
            issued_by_state_user=actor if getattr(actor, "role", None) in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN} else None,
            issue_date=issue_date,
            expiry_date=expiry_date,
            verification_url=verification_url,
            digital_signature_hash=signature,
        )
        certificate.qr_code_url = cls.write_qr_code(certificate_number=number, verification_url=verification_url)
        certificate.pdf_url = cls.write_accreditation_pdf(certificate=certificate)
        certificate.save(update_fields=["qr_code_url", "pdf_url", "updated_at"])
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=actor, target=certificate, metadata={"event": "accreditation_certificate_issued"})
        return certificate

    @classmethod
    def accreditation_verification_result_for(cls, certificate):
        owner_id = certificate.employer_id or certificate.facility_id
        expected_hash = cls.accreditation_signature_hash(
            certificate_number=certificate.certificate_number,
            certificate_type=certificate.certificate_type,
            owner_id=owner_id,
            issue_date=certificate.issue_date,
            expiry_date=certificate.expiry_date,
            issuing_state_id=certificate.issuing_state_id,
            verification_token=certificate.verification_token,
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

    @classmethod
    @transaction.atomic
    def issue_certificate(cls, *, assessment, actor=None):
        cls.validate_assessment_eligible(assessment)
        policy = cls.policy_for_state(assessment.facility.state)
        if not policy.certificate_validity_months or policy.certificate_validity_months <= 0:
            raise ValidationError("Certificate validity policy is missing or invalid.")
        template = cls.active_template_for_state(assessment.facility.state)
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
        token = cls.verification_token()
        verification_url = cls.build_verification_url(token)
        signature = cls.signature_hash(
            certificate_number=number,
            assessment_id=assessment.id,
            food_handler_id=assessment.food_handler_id,
            issue_date=issue_date,
            expiry_date=expiry_date,
            facility_id=assessment.facility_id,
            issuing_state_id=assessment.facility.state_id,
            doctor_id=assessment.doctor_id,
            verification_token=token,
        )
        certificate = Certificate.objects.create(
            certificate_number=number,
            public_id=uuid4(),
            verification_token=token,
            food_handler=assessment.food_handler,
            assessment=assessment,
            employer=assessment.employer,
            business_branch=assessment.food_handler.business_branch,
            facility=assessment.facility,
            doctor=assessment.doctor,
            issuing_state=assessment.facility.state,
            issued_by_state_user=issued_by,
            template=template,
            issue_date=issue_date,
            expiry_date=expiry_date,
            verification_url=verification_url,
            digital_signature_hash=signature,
        )
        certificate.qr_code_url = cls.write_qr_code(certificate_number=number, verification_url=verification_url)
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=actor or issued_by, target=certificate, metadata={"event": "certificate_qr_generated"})
        certificate.pdf_url = cls.write_pdf(certificate=certificate)
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=actor or issued_by, target=certificate, metadata={"event": "certificate_pdf_generated", "template_id": str(certificate.template_id) if certificate.template_id else ""})
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
        certificate.suspended_by = actor
        certificate.suspended_at = timezone.now()
        certificate.suspension_reason = reason
        certificate.save(update_fields=["status", "suspended_by", "suspended_at", "suspension_reason", "updated_at"])
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=actor, target=certificate, metadata={"event": "certificate_suspended"})
        return certificate

    @classmethod
    @transaction.atomic
    def reinstate(cls, *, certificate, actor, reason=""):
        if certificate.status != CertificateStatus.SUSPENDED:
            raise ValidationError("Only suspended certificates can be reinstated.")
        certificate.status = CertificateStatus.ACTIVE
        certificate.suspended_by = None
        certificate.suspended_at = None
        certificate.suspension_reason = ""
        certificate.save(update_fields=["status", "suspended_by", "suspended_at", "suspension_reason", "updated_at"])
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=actor, target=certificate, metadata={"event": "certificate_reinstated", "reason": reason})
        return certificate

    @classmethod
    @transaction.atomic
    def replace(cls, *, certificate, actor, reason=""):
        if certificate.status == CertificateStatus.REVOKED:
            raise ValidationError("Revoked certificates cannot be replaced.")
        certificate.status = CertificateStatus.REPLACED
        certificate.replacement_reason = reason
        certificate.save(update_fields=["status", "replacement_reason", "updated_at"])
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=actor, target=certificate, metadata={"event": "certificate_marked_replaced", "reason": reason})
        return certificate

    @classmethod
    def verification_result_for(cls, certificate):
        expected_hash = cls.signature_hash(
            certificate_number=certificate.certificate_number,
            assessment_id=certificate.assessment_id,
            food_handler_id=certificate.food_handler_id,
            issue_date=certificate.issue_date,
            expiry_date=certificate.expiry_date,
            facility_id=certificate.facility_id,
            issuing_state_id=certificate.issuing_state_id,
            doctor_id=certificate.doctor_id,
            verification_token=certificate.verification_token,
        )
        if expected_hash != certificate.digital_signature_hash:
            log_action(
                action=AuditAction.SECURITY_EVENT,
                target=certificate,
                metadata={"event": "certificate_hash_mismatch", "certificate_number": certificate.certificate_number},
            )
            return VerificationResult.INVALID
        if certificate.status == CertificateStatus.REVOKED:
            return VerificationResult.REVOKED
        if certificate.status == CertificateStatus.SUSPENDED:
            return VerificationResult.SUSPENDED
        if certificate.status == CertificateStatus.REPLACED:
            return VerificationResult.REPLACED
        if certificate.status != CertificateStatus.ACTIVE:
            return VerificationResult.INVALID
        if certificate.is_expired:
            return VerificationResult.EXPIRED
        return VerificationResult.VALID


class CertificateLifecycleJobService:
    @classmethod
    def process_expiry_and_reminders(cls, *, actor=None, today=None):
        today = today or timezone.localdate()
        expired = cls.mark_expired(actor=actor, today=today)
        reminders = cls.send_expiry_reminders(today=today)
        return {"expired_marked": expired, "reminders_sent": reminders}

    @classmethod
    def mark_expired(cls, *, actor=None, today=None):
        today = today or timezone.localdate()
        queryset = Certificate.objects.filter(status=CertificateStatus.ACTIVE, expiry_date__lt=today)
        count = 0
        for certificate in queryset:
            certificate.status = CertificateStatus.EXPIRED
            certificate.save(update_fields=["status", "updated_at"])
            count += 1
            log_action(
                action=AuditAction.CERTIFICATE_EVENT,
                actor=actor,
                target=certificate,
                metadata={"event": "certificate_marked_expired", "expiry_date": certificate.expiry_date.isoformat()},
            )
            cls._notify_certificate_people(
                certificate=certificate,
                subject="Certificate expired",
                body="A FoodCert NG certificate has expired and is no longer valid for food handling.",
                reminder_key="expired",
            )
        return count

    @classmethod
    def send_expiry_reminders(cls, *, today=None, reminder_days=(30, 7)):
        today = today or timezone.localdate()
        sent = 0
        for days in reminder_days:
            target_date = today + timezone.timedelta(days=days)
            certificates = Certificate.objects.select_related("food_handler", "food_handler__user", "employer").filter(
                status=CertificateStatus.ACTIVE,
                expiry_date=target_date,
            )
            for certificate in certificates:
                sent += cls._notify_certificate_people(
                    certificate=certificate,
                    subject=f"Certificate expires in {days} days",
                    body=f"FoodCert NG certificate {certificate.certificate_number} expires in {days} days.",
                    reminder_key=f"expiry_{days}",
                    days=days,
                )
        return sent

    @classmethod
    def _notify_certificate_people(cls, *, certificate, subject, body, reminder_key, days=None):
        recipients = []
        if certificate.food_handler.user_id:
            recipients.append(certificate.food_handler.user)
        if certificate.employer_id and getattr(certificate.employer, "user_id", None):
            recipients.append(certificate.employer.user)
        sent = 0
        for recipient in recipients:
            exists = Notification.objects.filter(
                recipient=recipient,
                category=NotificationCategory.CERTIFICATE,
                related_object_type="certificate",
                related_object_id=str(certificate.id),
                title=subject,
            ).exists()
            if exists:
                continue
            Notification.objects.create(
                recipient=recipient,
                category=NotificationCategory.CERTIFICATE,
                title=subject,
                message=body,
                related_object_type="certificate",
                related_object_id=certificate.id,
            )
            sent += 1
        return sent
