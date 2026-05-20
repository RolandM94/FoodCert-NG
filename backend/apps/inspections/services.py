from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import UserRole
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.certificates.models import Certificate
from apps.certificates.services import CertificateService
from apps.inspections.models import Inspection, InspectionCertificateScan, InspectionResponse, InspectionStatus
from apps.notifications.models import Notification, NotificationChannel, NotificationType


class InspectionService:
    @classmethod
    def ensure_inspector(cls, user):
        if user.role not in {UserRole.INSPECTOR, UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only inspectors and regulators can perform inspections.")

    @classmethod
    def compliance_score(cls, checklist):
        if not checklist:
            return None
        values = [bool(value) for value in checklist.values()]
        if not values:
            return None
        return Decimal(sum(values) * 100) / Decimal(len(values))

    @classmethod
    @transaction.atomic
    def create(cls, *, inspector, employer, **kwargs):
        cls.ensure_inspector(inspector)
        if inspector.role in {UserRole.INSPECTOR, UserRole.STATE_ADMIN} and employer.state_id != inspector.state_id:
            raise PermissionDenied("Inspectors can only inspect employers in their state.")
        branch = kwargs.get("branch")
        if branch and branch.organization_id != employer.organization_id:
            raise ValidationError("Inspection branch must belong to the employer organization.")
        checklist = kwargs.get("checklist_responses") or {}
        inspection = Inspection.objects.create(
            inspector=inspector,
            employer=employer,
            compliance_score=cls.compliance_score(checklist),
            **kwargs,
        )
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=inspector, target=inspection, metadata={"event": "inspection_created"})
        return inspection

    @classmethod
    @transaction.atomic
    def assign(cls, *, actor, inspector, employer, **kwargs):
        if actor.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN}:
            raise PermissionDenied("Only state ministry coordinators can assign inspections.")
        cls.ensure_inspector(inspector)
        if actor.role == UserRole.STATE_ADMIN and employer.state_id != actor.state_id:
            raise PermissionDenied("State coordinators can only assign inspections in their state.")
        if inspector.role in {UserRole.INSPECTOR, UserRole.STATE_ADMIN} and inspector.state_id != employer.state_id:
            raise PermissionDenied("Assigned inspector must belong to the employer state.")
        branch = kwargs.get("branch")
        if branch and branch.organization_id != employer.organization_id:
            raise ValidationError("Inspection branch must belong to the employer organization.")
        checklist = kwargs.get("checklist_responses") or {}
        inspection = Inspection.objects.create(
            inspector=inspector,
            employer=employer,
            status=kwargs.pop("status", InspectionStatus.DRAFT),
            compliance_score=cls.compliance_score(checklist),
            **kwargs,
        )
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=inspection,
            metadata={"event": "inspection_assigned", "inspector_id": str(inspector.id), "employer_id": str(employer.id)},
        )
        return inspection

    @classmethod
    @transaction.atomic
    def update(cls, *, inspection, actor, **kwargs):
        cls.ensure_inspector(actor)
        branch = kwargs.get("branch")
        if branch and branch.organization_id != inspection.employer.organization_id:
            raise ValidationError("Inspection branch must belong to the employer organization.")
        if "checklist_responses" in kwargs:
            kwargs["compliance_score"] = cls.compliance_score(kwargs["checklist_responses"])
        for field, value in kwargs.items():
            setattr(inspection, field, value)
        inspection.save(update_fields=[*kwargs.keys(), "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=inspection, metadata={"event": "inspection_updated"})
        return inspection

    @classmethod
    @transaction.atomic
    def review(cls, *, inspection, actor, **kwargs):
        if actor.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only ministry reviewers can review inspection reports.")
        if actor.role == UserRole.STATE_ADMIN and inspection.employer.state_id != actor.state_id:
            raise PermissionDenied("State reviewers can only review inspections in their state.")
        if "checklist_responses" in kwargs:
            kwargs["compliance_score"] = cls.compliance_score(kwargs["checklist_responses"])
        for field, value in kwargs.items():
            setattr(inspection, field, value)
        inspection.save(update_fields=[*kwargs.keys(), "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=inspection,
            metadata={"event": "inspection_reviewed", "enforcement_action": inspection.enforcement_action},
        )
        return inspection

    @classmethod
    @transaction.atomic
    def close(cls, *, inspection, actor, closure_notes=""):
        if actor.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only ministry reviewers can close inspection reports.")
        if actor.role == UserRole.STATE_ADMIN and inspection.employer.state_id != actor.state_id:
            raise PermissionDenied("State reviewers can only close inspections in their state.")
        if inspection.inspector_id == actor.id and actor.role != UserRole.SUPER_ADMIN:
            raise PermissionDenied("Inspectors cannot close their own inspection reports.")
        inspection.status = InspectionStatus.CLOSED
        if closure_notes:
            inspection.findings = f"{inspection.findings}\n\nClosure notes: {closure_notes}".strip()
        inspection.save(update_fields=["status", "findings", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=inspection,
            metadata={"event": "inspection_closed", "closure_notes": closure_notes},
        )
        return inspection

    @classmethod
    @transaction.atomic
    def submit(cls, *, inspection, actor):
        cls.ensure_inspector(actor)
        if inspection.status == InspectionStatus.SUBMITTED:
            return inspection
        if not inspection.checklist_responses:
            raise ValidationError("Checklist responses are required before submission.")
        inspection.compliance_score = cls.compliance_score(inspection.checklist_responses)
        inspection.status = InspectionStatus.SUBMITTED
        inspection.submitted_at = timezone.now()
        inspection.save(update_fields=["compliance_score", "status", "submitted_at", "updated_at"])
        if inspection.enforcement_action in {"compliance_notice", "follow_up_required", "sanction_recommended", "escalated_to_state"} and inspection.employer.user:
            Notification.objects.create(
                recipient=inspection.employer.user,
                notification_type=NotificationType.COMPLIANCE_NOTICE,
                channel=NotificationChannel.IN_APP,
                subject="Inspection compliance notice",
                body=inspection.findings or "An inspection requires your attention.",
                context_data={"inspection_id": str(inspection.id), "enforcement_action": inspection.enforcement_action},
            )
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=inspection, metadata={"event": "inspection_submitted"})
        return inspection

    @classmethod
    @transaction.atomic
    def add_evidence(cls, *, inspection, actor, evidence):
        cls.ensure_inspector(actor)
        inspection.evidence_files = [*inspection.evidence_files, evidence]
        inspection.save(update_fields=["evidence_files", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=inspection, metadata={"event": "inspection_evidence_added"})
        return inspection

    @classmethod
    @transaction.atomic
    def scan_certificate(cls, *, inspection, actor, certificate_number):
        cls.ensure_inspector(actor)
        certificate = Certificate.objects.filter(certificate_number=certificate_number).first()
        result = CertificateService.verification_result_for(certificate) if certificate else "not_found"
        scan = InspectionCertificateScan.objects.create(
            inspection=inspection,
            certificate=certificate,
            certificate_number=certificate_number,
            result=result,
        )
        log_action(action=AuditAction.PUBLIC_VERIFICATION, actor=actor, target=scan, metadata={"event": "inspection_certificate_scan", "result": result})
        return scan

    @classmethod
    @transaction.atomic
    def submit_employer_response(cls, *, inspection, actor, response_type, content="", evidence_file_url=""):
        if actor.role != UserRole.EMPLOYER:
            raise PermissionDenied("Only employer users can respond to inspections.")
        if inspection.employer.organization_id != actor.organization_id:
            raise PermissionDenied("You can only respond to inspections for your organization.")
        if actor.unit_restricted and actor.unit_id and inspection.branch_id != actor.unit_id:
            raise PermissionDenied("Branch managers can only respond to inspections for their branch.")
        response = InspectionResponse.objects.create(
            inspection=inspection,
            submitted_by=actor,
            response_type=response_type,
            content=content,
            evidence_file_url=evidence_file_url,
        )
        if inspection.status != InspectionStatus.CLOSED:
            inspection.status = InspectionStatus.EMPLOYER_RESPONSE_SUBMITTED
            inspection.save(update_fields=["status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=response,
            metadata={"event": "inspection_employer_response", "inspection_id": str(inspection.id), "response_type": response_type},
        )
        return response
