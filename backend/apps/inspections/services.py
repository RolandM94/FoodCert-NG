from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import UserRole
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.certificates.models import Certificate
from apps.certificates.services import CertificateService
from apps.inspections.models import (
    CaseStatus,
    CorrectiveActionResponse,
    CorrectiveActionStatus,
    EnforcementCase,
    EnforcementNotice,
    EscalationLevel,
    Inspection,
    InspectionCertificateScan,
    InspectionFinding,
    InspectionResponse,
    InspectionPriority,
    InspectionStatus,
    InspectionType,
    NoticeStatus,
)
from apps.notifications.models import Notification, NotificationCategory


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
            assigned_by=actor,
            status=kwargs.pop("status", InspectionStatus.ASSIGNED),
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
        if inspection.status == InspectionStatus.SUBMITTED:
            inspection.transition_to(InspectionStatus.UNDER_REVIEW)
        inspection.reviewed_at = timezone.now()
        inspection.save(update_fields=[*kwargs.keys(), "status", "reviewed_at", "updated_at"])
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
        inspection.transition_to(InspectionStatus.CLOSED)
        inspection.closed_at = timezone.now()
        if closure_notes:
            inspection.findings = f"{inspection.findings}\n\nClosure notes: {closure_notes}".strip()
        inspection.save(update_fields=["status", "closed_at", "findings", "updated_at"])
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
        inspection.transition_to(InspectionStatus.SUBMITTED)
        inspection.submitted_at = timezone.now()
        inspection.save(update_fields=["compliance_score", "status", "submitted_at", "updated_at"])
        if inspection.enforcement_action in {"compliance_notice", "follow_up_required", "sanction_recommended", "escalated_to_state"} and inspection.employer.user:
            Notification.objects.create(
                recipient=inspection.employer.user,
                category=NotificationCategory.ENFORCEMENT,
                title="Inspection compliance notice",
                message=inspection.findings or "An inspection requires your attention.",
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
        if inspection.status not in {InspectionStatus.CLOSED, InspectionStatus.CANCELLED}:
            inspection.transition_to(InspectionStatus.CORRECTIVE_ACTION_SUBMITTED)
            inspection.save(update_fields=["status", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=response,
            metadata={"event": "inspection_employer_response", "inspection_id": str(inspection.id), "response_type": response_type},
        )
        return response

    @classmethod
    @transaction.atomic
    def accept(cls, *, inspection, actor):
        cls.ensure_inspector(actor)
        if inspection.inspector_id != actor.id and actor.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN}:
            raise PermissionDenied("Only the assigned inspector can accept the assignment.")
        inspection.transition_to(InspectionStatus.ACCEPTED)
        inspection.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=inspection, metadata={"event": "inspection_accepted"})
        return inspection

    @classmethod
    @transaction.atomic
    def start(cls, *, inspection, actor):
        cls.ensure_inspector(actor)
        if inspection.inspector_id != actor.id:
            raise PermissionDenied("Only the assigned inspector can start the inspection.")
        inspection.transition_to(InspectionStatus.IN_PROGRESS)
        inspection.started_at = timezone.now()
        inspection.save(update_fields=["status", "started_at", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=inspection, metadata={"event": "inspection_started"})
        return inspection

    @classmethod
    @transaction.atomic
    def return_for_correction(cls, *, inspection, actor):
        if actor.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only ministry reviewers can return inspection reports for correction.")
        if actor.role == UserRole.STATE_ADMIN and inspection.employer.state_id != actor.state_id:
            raise PermissionDenied("State reviewers can only review inspections in their state.")
        inspection.transition_to(InspectionStatus.RETURNED_FOR_CORRECTION)
        inspection.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=inspection, metadata={"event": "inspection_returned_for_correction"})
        return inspection

    @classmethod
    @transaction.atomic
    def cancel(cls, *, inspection, actor, reason=""):
        if actor.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN}:
            raise PermissionDenied("Only state coordinators can cancel inspections.")
        if actor.role == UserRole.STATE_ADMIN and inspection.employer.state_id != actor.state_id:
            raise PermissionDenied("State coordinators can only cancel inspections in their state.")
        inspection.transition_to(InspectionStatus.CANCELLED)
        inspection.cancellation_reason = reason
        inspection.save(update_fields=["status", "cancellation_reason", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=inspection, metadata={"event": "inspection_cancelled", "reason": reason})
        return inspection

    @classmethod
    @transaction.atomic
    def reschedule_request(cls, *, inspection, actor, reason=""):
        cls.ensure_inspector(actor)
        if inspection.inspector_id != actor.id and actor.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN}:
            raise PermissionDenied("Only the assigned inspector can request a reschedule.")
        if inspection.status not in {InspectionStatus.ASSIGNED, InspectionStatus.ACCEPTED}:
            raise ValidationError("Reschedule can only be requested for assigned or accepted inspections.")
        previous_status = inspection.status
        upsert_fields = ["updated_at", "reason"]
        if inspection.status == InspectionStatus.ACCEPTED:
            if not reason.strip():
                raise ValidationError("A reason is required when requesting a reschedule from accepted status.")
            inspection.transition_to(InspectionStatus.ASSIGNED)
            upsert_fields.append("status")
        else:
            inspection.reason = reason
        inspection.scheduled_at = None
        inspection.save(update_fields=[*upsert_fields, "scheduled_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=inspection,
            metadata={"event": "inspection_reschedule_requested", "previous_status": previous_status, "reason": reason},
        )
        return inspection

    @classmethod
    @transaction.atomic
    def create_follow_up(cls, *, parent_inspection, actor, inspector=None, scheduled_at=None, reason=""):
        if actor.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN}:
            raise PermissionDenied("Only coordinators can create follow-up inspections.")
        if parent_inspection.status in {InspectionStatus.CLOSED, InspectionStatus.CANCELLED}:
            raise ValidationError("Cannot create a follow-up for a closed or cancelled inspection.")

        unresolved_findings = parent_inspection.findings or ""
        existing_checklist = parent_inspection.checklist_responses or {}
        checklist_snapshot = {k: v for k, v in existing_checklist.items() if not v}

        parent_status = parent_inspection.status
        if parent_status == InspectionStatus.CORRECTIVE_ACTION_SUBMITTED:
            parent_inspection.transition_to(InspectionStatus.FOLLOW_UP_REQUIRED)
            parent_inspection.transition_to(InspectionStatus.FOLLOW_UP_SCHEDULED)
        elif parent_status in {
            InspectionStatus.FOLLOW_UP_REQUIRED,
            InspectionStatus.NOTICE_ISSUED,
            InspectionStatus.CORRECTIVE_ACTION_PENDING,
        }:
            parent_inspection.transition_to(InspectionStatus.FOLLOW_UP_SCHEDULED)
        else:
            parent_inspection.status = InspectionStatus.FOLLOW_UP_SCHEDULED
            parent_inspection.save(update_fields=["status", "updated_at"])

        assigned_inspector = inspector or parent_inspection.inspector
        follow_up = Inspection.objects.create(
            parent_inspection=parent_inspection,
            inspection_type=InspectionType.FOLLOW_UP,
            priority=parent_inspection.priority,
            inspector=assigned_inspector,
            employer=parent_inspection.employer,
            branch=parent_inspection.branch,
            status=InspectionStatus.ASSIGNED,
            scheduled_at=scheduled_at,
            reason=reason or f"Follow-up to {parent_inspection.reference}",
            findings=unresolved_findings,
            checklist_responses=checklist_snapshot,
        )
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=follow_up,
            metadata={
                "event": "follow_up_inspection_created",
                "parent_inspection_id": str(parent_inspection.id),
                "parent_reference": parent_inspection.reference,
            },
        )
        return follow_up

    @classmethod
    @transaction.atomic
    def escalate_inspection(cls, *, inspection, actor, severity="medium", summary=""):
        if actor.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only coordinators and administrators can escalate inspections.")
        if inspection.status in {InspectionStatus.CLOSED, InspectionStatus.CANCELLED}:
            raise ValidationError("Cannot escalate a closed or cancelled inspection.")
        summary_text = summary or f"Escalated from inspection {inspection.reference}. Findings: {(inspection.findings or '')[:500]}"
        enforcement_case = EnforcementCase.objects.create(
            state=inspection.employer.state,
            employer=inspection.employer,
            branch=inspection.branch,
            status=CaseStatus.OPEN,
            severity=severity,
            summary=summary_text,
            opened_by=actor,
            assigned_to=actor,
        )
        if inspection.status not in {InspectionStatus.ESCALATED}:
            inspection.transition_to(InspectionStatus.ESCALATED)
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=enforcement_case,
            metadata={
                "event": "inspection_escalated_to_case",
                "inspection_id": str(inspection.id),
                "inspection_reference": inspection.reference,
                "case_reference": enforcement_case.case_reference,
            },
        )
        return enforcement_case

    @classmethod
    @transaction.atomic
    def escalate_case(cls, *, enforcement_case, actor, reason=""):
        if actor.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only coordinators and administrators can escalate enforcement cases.")
        if enforcement_case.status == CaseStatus.CLOSED:
            raise ValidationError("Cannot escalate a closed enforcement case.")
        current_level = enforcement_case.escalated_to or ""
        escalation_order = [
            EscalationLevel.COORDINATOR,
            EscalationLevel.STATE_ADMIN,
            EscalationLevel.FEDERAL,
        ]
        next_level = EscalationLevel.STATE_ADMIN
        if current_level == EscalationLevel.STATE_ADMIN:
            next_level = EscalationLevel.FEDERAL
        elif current_level == EscalationLevel.FEDERAL:
            next_level = EscalationLevel.FEDERAL
        enforcement_case.status = CaseStatus.ESCALATED
        enforcement_case.escalated_to = next_level
        enforcement_case.save(update_fields=["status", "escalated_to", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=actor,
            target=enforcement_case,
            metadata={
                "event": "enforcement_case_escalated",
                "case_reference": enforcement_case.case_reference,
                "from_level": current_level or "none",
                "to_level": next_level,
                "reason": reason,
            },
        )
        return enforcement_case


class InspectionDashboardService:
    @classmethod
    def _base_inspection_queryset(cls, user):
        qs = Inspection.objects.select_related("employer", "employer__state", "branch")
        if user.role == UserRole.SUPER_ADMIN:
            return qs
        if user.role == UserRole.FEDERAL_ADMIN:
            return qs
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            qs = qs.filter(employer__state=user.state)
            if user.unit_id and getattr(user.unit, "lga_id", None):
                qs = qs.filter(employer__lga_id=user.unit.lga_id)
            return qs
        if user.role == UserRole.EMPLOYER:
            if hasattr(user, "employer"):
                return qs.filter(employer=user.employer)
            return qs.none()
        return qs.none()

    @classmethod
    def inspector_dashboard(cls, user):
        inspections = cls._base_inspection_queryset(user)
        if user.role == UserRole.INSPECTOR:
            inspections = inspections.filter(inspector=user)

        today = timezone.now().date()
        month_start = today.replace(day=1)

        cards = {
            "assigned_inspections": inspections.filter(status=InspectionStatus.ASSIGNED).count(),
            "due_today": inspections.filter(scheduled_at__date=today).count(),
            "overdue": inspections.filter(
                scheduled_at__lt=timezone.now(), status__in=[
                    InspectionStatus.ASSIGNED, InspectionStatus.ACCEPTED,
                    InspectionStatus.SCHEDULED, InspectionStatus.IN_PROGRESS,
                ]
            ).count(),
            "in_progress": inspections.filter(status=InspectionStatus.IN_PROGRESS).count(),
            "submitted": inspections.filter(status=InspectionStatus.SUBMITTED).count(),
            "notices_issued": EnforcementNotice.objects.filter(status__in=[
                NoticeStatus.ISSUED, NoticeStatus.ACKNOWLEDGED,
                NoticeStatus.RESPONSE_SUBMITTED,
            ]).filter(employer__state=user.state).count() if user.role != UserRole.EMPLOYER else 0,
            "corrective_actions_pending": CorrectiveActionResponse.objects.filter(
                notice__employer__state=user.state,
                status=CorrectiveActionStatus.SUBMITTED,
            ).count() if user.role != UserRole.EMPLOYER else 0,
            "follow_ups": inspections.filter(
                parent_inspection__isnull=False, status__in=[
                    InspectionStatus.ASSIGNED, InspectionStatus.ACCEPTED,
                    InspectionStatus.IN_PROGRESS,
                ]
            ).count(),
            "high_priority": inspections.filter(
                priority__in=[InspectionPriority.HIGH, InspectionPriority.CRITICAL],
                status__in=[
                    InspectionStatus.ASSIGNED, InspectionStatus.ACCEPTED,
                    InspectionStatus.SCHEDULED, InspectionStatus.IN_PROGRESS,
                ],
            ).count(),
            "closed_this_month": inspections.filter(
                status=InspectionStatus.CLOSED, closed_at__gte=month_start,
            ).count(),
        }
        return {"cards": cards, "filters": {"user_id": str(user.id)}}

    @classmethod
    def inspector_tasks(cls, user, status_filter=None, priority=None, inspection_type=None, scheduled_from=None, scheduled_to=None):
        inspections = cls._base_inspection_queryset(user)
        if user.role == UserRole.INSPECTOR:
            inspections = inspections.filter(inspector=user)

        if status_filter:
            inspections = inspections.filter(status=status_filter)
        else:
            inspections = inspections.exclude(status__in=[InspectionStatus.CLOSED, InspectionStatus.CANCELLED])

        if priority:
            inspections = inspections.filter(priority=priority)
        if inspection_type:
            inspections = inspections.filter(inspection_type=inspection_type)
        if scheduled_from:
            inspections = inspections.filter(scheduled_at__gte=scheduled_from)
        if scheduled_to:
            inspections = inspections.filter(scheduled_at__lte=scheduled_to)

        return inspections

    @classmethod
    def employer_context(cls, inspection):
        employer = inspection.employer
        branch = inspection.branch
        return {
            "employer": {
                "id": str(employer.id),
                "name": employer.organization.name if employer.organization else employer.name,
                "establishment_category": employer.establishment_category,
                "lga": employer.lga.name if employer.lga else None,
                "state": employer.state.name if employer.state else None,
            },
            "branch": {
                "id": str(branch.id), "name": branch.name,
            } if branch else None,
        }

    @classmethod
    def compliance_summary(cls, inspection):
        employer = inspection.employer
        branch = inspection.branch
        from apps.certificates.models import CertificateStatus as CertStatus

        food_handlers = employer.food_handler_profiles.all()
        if branch:
            food_handlers = food_handlers.filter(organization_unit=branch)

        total_fh = food_handlers.count()
        certificates = Certificate.objects.filter(food_handler__in=food_handlers)
        cert_counts = {
            "total_food_handlers": total_fh,
            "active_certificates": certificates.filter(status=CertStatus.ACTIVE).count(),
            "expired_certificates": certificates.filter(status=CertStatus.EXPIRED).count(),
            "suspended_certificates": certificates.filter(status=CertStatus.SUSPENDED).count(),
            "revoked_certificates": certificates.filter(status=CertStatus.REVOKED).count(),
            "uncertified_food_handlers": total_fh - certificates.count(),
            "temporarily_not_fit": food_handlers.filter(is_fit=False).count(),
            "return_to_work_pending": food_handlers.filter(is_fit=False, return_to_work_cleared_at__isnull=True).count(),
            "vaccination_due": food_handlers.filter(vaccination_due_date__lte=timezone.now().date()).count(),
        }

        critical_findings = InspectionFinding.objects.filter(
            inspection__employer=employer,
            severity__in=["major", "critical"],
            status__in=["open", "under_review", "notice_issued"],
        ).count()

        total_inspections = Inspection.objects.filter(employer=employer).count()
        closed_inspections = Inspection.objects.filter(employer=employer, status=InspectionStatus.CLOSED).count()

        if critical_findings > 0:
            compliance_label = "high_risk"
        elif total_inspections > 0 and closed_inspections / total_inspections < 0.5:
            compliance_label = "non_compliant"
        elif total_inspections > 0 and closed_inspections / total_inspections < 0.8:
            compliance_label = "partially_compliant"
        else:
            compliance_label = "compliant"

        cert_counts["overall_compliance_status"] = compliance_label
        cert_counts["subscription_status"] = "active"
        cert_counts["critical_findings"] = critical_findings
        cert_counts["total_inspections"] = total_inspections
        cert_counts["closed_inspections"] = closed_inspections

        return cert_counts

    @classmethod
    def food_handlers_for_inspection(cls, inspection):
        employer = inspection.employer
        branch = inspection.branch
        from apps.food_handlers.models import FoodHandlerProfile

        food_handlers = FoodHandlerProfile.objects.filter(employer=employer).select_related("user")
        if branch:
            food_handlers = food_handlers.filter(organization_unit=branch)

        return [
            {
                "id": str(fh.id),
                "name": fh.user.get_full_name() or fh.user.email if fh.user else fh.id.hex[:8],
                "photo_url": fh.photo.url if fh.photo else None,
                "certificate_status": fh.certificate_status if hasattr(fh, "certificate_status") else None,
                "fitness_status": "fit" if fh.is_fit else "not_fit",
                "certificate_number": fh.certificate.certificate_number if hasattr(fh, "certificate") and fh.certificate else None,
            }
            for fh in food_handlers
        ]

    @classmethod
    def state_enforcement_dashboard(cls, user, lga_id=None, date_from=None, date_to=None):
        inspections = cls._base_inspection_queryset(user)
        state = user.state

        today = timezone.now().date()
        month_start = today.replace(day=1)

        inspections_lga = inspections.values("employer__lga__name").annotate(
            count=Count("id"),
        ).order_by("-count")

        findings_by_severity = InspectionFinding.objects.filter(
            inspection__employer__state=state,
        ).values("severity").annotate(count=Count("id")).order_by("-count")

        notices_by_type = EnforcementNotice.objects.filter(
            employer__state=state,
        ).values("notice_type").annotate(count=Count("id")).order_by("-count")

        cards = {
            "total_inspections": inspections.count(),
            "inspections_this_month": inspections.filter(inspection_date__gte=month_start).count(),
            "inspections_by_lga": list(inspections_lga[:10]),
            "open_cases": EnforcementCase.objects.filter(state=state).exclude(status=CaseStatus.CLOSED).count(),
            "notices_issued": EnforcementNotice.objects.filter(employer__state=state, status__in=[
                NoticeStatus.ISSUED, NoticeStatus.ACKNOWLEDGED,
            ]).count(),
            "overdue_corrective_actions": CorrectiveActionResponse.objects.filter(
                notice__employer__state=state,
                status=CorrectiveActionStatus.SUBMITTED,
            ).count(),
            "critical_findings": InspectionFinding.objects.filter(
                inspection__employer__state=state,
                severity="critical",
                status__in=["open", "under_review"],
            ).count(),
            "suspicious_certs": 0,
            "follow_ups_pending": inspections.filter(
                parent_inspection__isnull=False,
                status__in=[InspectionStatus.ASSIGNED, InspectionStatus.FOLLOW_UP_SCHEDULED],
            ).count(),
            "branches_inspected": inspections.values("branch").distinct().count() if state else 0,
            "employer_compliance_rate": 0,
            "inspectors_active": inspections.filter(
                inspection_date__gte=month_start,
            ).values("inspector").distinct().count(),
        }

        charts = {
            "inspections_over_time": [],
            "findings_by_severity": list(findings_by_severity),
            "notices_by_type": list(notices_by_type),
            "compliance_by_lga": list(inspections_lga),
        }

        return {
            "cards": cards,
            "charts": charts,
            "filters": {"state_id": str(state.id) if state else None, "lga_id": lga_id, "date_from": date_from, "date_to": date_to},
        }

    @classmethod
    def federal_enforcement_dashboard(cls, user):
        today = timezone.now().date()
        month_start = today.replace(day=1)

        inspections_by_state = Inspection.objects.values("employer__state__name").annotate(
            total=Count("id"),
            this_month=Count("id", filter=Q(inspection_date__gte=month_start)),
        ).order_by("-total")

        notices_by_state = EnforcementNotice.objects.values("employer__state__name").annotate(
            total=Count("id"),
            issued=Count("id", filter=Q(status=NoticeStatus.ISSUED)),
        ).order_by("-total")

        critical_findings_by_state = InspectionFinding.objects.filter(
            severity="critical",
            status__in=["open", "under_review"],
        ).values("inspection__employer__state__name").annotate(count=Count("id")).order_by("-count")

        cards = {
            "total_inspections": Inspection.objects.count(),
            "inspections_this_month": Inspection.objects.filter(inspection_date__gte=month_start).count(),
            "open_enforcement_cases": EnforcementCase.objects.exclude(status=CaseStatus.CLOSED).count(),
            "total_notices_issued": EnforcementNotice.objects.filter(status=NoticeStatus.ISSUED).count(),
            "critical_findings_national": InspectionFinding.objects.filter(severity="critical", status__in=["open", "under_review"]).count(),
            "states_with_active_enforcement": EnforcementCase.objects.exclude(status=CaseStatus.CLOSED).values("state").distinct().count(),
            "active_inspectors": Inspection.objects.filter(inspection_date__gte=month_start).values("inspector").distinct().count(),
        }

        charts = {
            "inspections_by_state": list(inspections_by_state),
            "notices_by_state": list(notices_by_state),
            "critical_findings_by_state": list(critical_findings_by_state),
        }

        return {"cards": cards, "charts": charts}


class InspectionJobService:
    _OVERDUE_ESCALATION_DAYS = 7
    _DEADLINE_REMINDER_DAYS = [2, 1]

    @classmethod
    def process_all(cls, *, actor=None, today=None):
        today = today or timezone.now().date()
        reminders = cls.inspection_reminders(today=today)
        notice = cls.notice_deadlines(today=today)
        analytics = cls.follow_up_analytics(today=today)
        return {
            "reminders_sent": reminders,
            "notice_notifications": notice,
            "analytics_results": analytics,
        }

    @classmethod
    def inspection_reminders(cls, *, today=None):
        today = today or timezone.now().date()
        sent = 0

        due_today = Inspection.objects.filter(
            scheduled_at__date=today,
            status__in=[InspectionStatus.ASSIGNED, InspectionStatus.ACCEPTED],
        ).select_related("inspector", "employer")

        for inspection in due_today:
            if inspection.inspector_id:
                Notification.objects.create(
                    recipient=inspection.inspector,
                    category=NotificationCategory.INSPECTION,
                    title="Inspection due today",
                    message=f"Inspection {inspection.reference} at {inspection.employer.name} is scheduled for today.",
                )
                sent += 1

        overdue = Inspection.objects.filter(
            scheduled_at__date__lt=today,
            status__in=[InspectionStatus.ASSIGNED, InspectionStatus.ACCEPTED, InspectionStatus.SCHEDULED],
        ).select_related("inspector", "employer")

        for inspection in overdue:
            if inspection.inspector_id:
                overdue_days = (today - inspection.scheduled_at.date()).days
                Notification.objects.create(
                    recipient=inspection.inspector,
                    category=NotificationCategory.ENFORCEMENT,
                    title="Inspection overdue",
                    message=f"Inspection {inspection.reference} at {inspection.employer.name} is {overdue_days} day(s) overdue.",
                )
                sent += 1

        return sent

    @classmethod
    def notice_deadlines(cls, *, today=None):
        today = today or timezone.now().date()
        sent = 0

        for days_ahead in cls._DEADLINE_REMINDER_DAYS:
            deadline_date = today + timezone.timedelta(days=days_ahead)
            notices = EnforcementNotice.objects.filter(
                deadline=deadline_date,
                status__in=[NoticeStatus.ISSUED, NoticeStatus.ACKNOWLEDGED],
            ).select_related("employer", "employer__user")

            for notice in notices:
                if notice.employer.user_id:
                    exists = Notification.objects.filter(
                        recipient=notice.employer.user,
                        category=NotificationCategory.ENFORCEMENT,
                        related_object_type="enforcement_notice",
                        related_object_id=str(notice.id),
                    ).filter(
                        title__contains=str(days_ahead),
                    ).exists()
                    if exists:
                        continue
                    Notification.objects.create(
                        recipient=notice.employer.user,
                        category=NotificationCategory.ENFORCEMENT,
                        title=f"Corrective action deadline in {days_ahead} day(s)",
                        message=f"Enforcement notice {notice.notice_reference} requires corrective action by {notice.deadline.isoformat()}.",
                    )
                    sent += 1

        overdue_cutoff = today - timezone.timedelta(days=cls._OVERDUE_ESCALATION_DAYS)
        overdue_notices = EnforcementNotice.objects.filter(
            deadline__lt=overdue_cutoff,
            status__in=[NoticeStatus.ISSUED, NoticeStatus.ACKNOWLEDGED],
        ).select_related("employer", "employer__user")

        for notice in overdue_notices:
            if notice.employer.user_id:
                exists = Notification.objects.filter(
                    recipient=notice.employer.user,
                    category=NotificationCategory.ENFORCEMENT,
                    related_object_type="enforcement_notice",
                    related_object_id=str(notice.id),
                    title__icontains="overdue",
                ).exists()
                if exists:
                    continue
                Notification.objects.create(
                    recipient=notice.employer.user,
                    category=NotificationCategory.ENFORCEMENT,
                    title="Corrective action overdue — escalated",
                    message=f"Enforcement notice {notice.notice_reference} is overdue by {cls._OVERDUE_ESCALATION_DAYS}+ days and has been flagged for escalation.",
                )
                sent += 1

        return sent

    @classmethod
    def follow_up_analytics(cls, *, today=None):
        today = today or timezone.now().date()
        sent = 0

        follow_ups = Inspection.objects.filter(
            parent_inspection__isnull=False,
            status__in=[InspectionStatus.FOLLOW_UP_SCHEDULED, InspectionStatus.ASSIGNED],
            scheduled_at__isnull=False,
        ).select_related("inspector", "employer")

        for inspection in follow_ups:
            if inspection.inspector_id and inspection.scheduled_at and inspection.scheduled_at.date() <= today:
                exists = Notification.objects.filter(
                    recipient=inspection.inspector,
                    category=NotificationCategory.INSPECTION,
                    related_object_type="inspection",
                    related_object_id=str(inspection.id),
                    title__icontains="follow-up",
                ).exists()
                if exists:
                    continue
                Notification.objects.create(
                    recipient=inspection.inspector,
                    category=NotificationCategory.INSPECTION,
                    title="Follow-up inspection due",
                    message=f"Follow-up inspection {inspection.reference} at {inspection.employer.name} is due.",
                )
                sent += 1

        repeat_violations = InspectionFinding.objects.filter(
            status__in=["open", "under_review"],
            severity__in=["major", "critical"],
        ).values("inspection__employer", "category").annotate(
            count=Count("id"),
        ).filter(count__gt=2)

        repeat_count = 0
        for violation in repeat_violations:
            repeat_count += 1

        suspicious_cert_flags = 0

        analytics = {
            "repeat_violation_clusters": repeat_count,
            "suspicious_certificate_patterns": suspicious_cert_flags,
            "non_compliant_employers": 0,
        }
        return {"notifications_sent": sent, "analytics": analytics}
