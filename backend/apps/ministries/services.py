from django.db.models import Count, Q, Sum
from django.utils import timezone

from apps.audit.models import AuditAction, AuditLog
from apps.audit.services import log_action
from apps.certificates.models import Certificate, CertificateRequest, CertificateRequestStatus, CertificateStatus
from apps.employers.models import Employer
from apps.facilities.models import AccreditationStatus, FacilityAccreditationApplication, MedicalFacility
from apps.food_handlers.models import FoodHandlerProfile
from apps.illness.models import IllnessReport
from apps.inspections.models import Inspection
from apps.locations.models import State
from apps.ministries.models import FederalStateQueryStatus, StateReport, StateReportStatus
from apps.organizations.models import Organization, OrganizationType
from apps.reports.services import DashboardService
from apps.settlements.models import Settlement, SettlementStatus


class MinistryDashboardService:
    @classmethod
    def state_dashboard(cls, user, **filters):
        return DashboardService.state_dashboard(user, **filters)

    @classmethod
    def federal_dashboard(cls, user):
        return DashboardService.federal_dashboard(user)


class StateReportService:
    @classmethod
    def scoped_state(cls, user):
        if not getattr(user, "state_id", None):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Your account is not assigned to a state.")
        return user.state

    @classmethod
    def scoped_settlements(cls, *, state, date_from=None, date_to=None):
        queryset = Settlement.objects.select_related("facility", "state", "payment_transaction").filter(state=state)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        return queryset

    @classmethod
    def finance_snapshot(cls, *, state, date_from=None, date_to=None):
        settlements = cls.scoped_settlements(state=state, date_from=date_from, date_to=date_to)
        totals = settlements.aggregate(
            gross_amount=Sum("gross_amount"),
            facility_amount=Sum("facility_amount"),
            state_amount=Sum("state_amount"),
            platform_amount=Sum("platform_amount"),
        )
        paid = settlements.filter(settlement_status=SettlementStatus.PAID)
        pending = settlements.exclude(settlement_status=SettlementStatus.PAID)
        return {
            "state": {"id": str(state.id), "name": state.name},
            "filters": {
                "date_from": str(date_from) if date_from else "",
                "date_to": str(date_to) if date_to else "",
            },
            "cards": {
                "settlement_count": settlements.count(),
                "paid_settlement_count": paid.count(),
                "pending_settlement_count": pending.count(),
                "gross_amount": str(totals["gross_amount"] or 0),
                "facility_amount": str(totals["facility_amount"] or 0),
                "state_amount": str(totals["state_amount"] or 0),
                "platform_amount": str(totals["platform_amount"] or 0),
            },
            "charts": {
                "settlement_status": list(settlements.values("settlement_status").annotate(total=Count("id")).order_by("settlement_status")),
                "facility_revenue": [
                    {
                        "facility__facility_name": row["facility__facility_name"],
                        "gross_amount": str(row["gross_amount"] or 0),
                        "state_amount": str(row["state_amount"] or 0),
                        "total": row["total"],
                    }
                    for row in settlements.values("facility__facility_name")
                    .annotate(gross_amount=Sum("gross_amount"), state_amount=Sum("state_amount"), total=Count("id"))
                    .order_by("facility__facility_name")
                ],
            },
            "sections": {
                "recent_settlements": [
                    {
                        "id": str(item.id),
                        "facility_name": item.facility.facility_name,
                        "gross_amount": str(item.gross_amount),
                        "facility_amount": str(item.facility_amount),
                        "state_amount": str(item.state_amount),
                        "platform_amount": str(item.platform_amount),
                        "settlement_status": item.settlement_status,
                        "settlement_reference": item.settlement_reference,
                        "settled_at": item.settled_at.isoformat() if item.settled_at else "",
                        "created_at": item.created_at.isoformat(),
                    }
                    for item in settlements.order_by("-created_at")[:50]
                ]
            },
        }

    @classmethod
    def build_snapshot(cls, *, actor, report_type, period_start, period_end):
        state = cls.scoped_state(actor)
        dashboard = DashboardService.state_dashboard(actor, date_from=period_start, date_to=period_end)
        finance = cls.finance_snapshot(state=state, date_from=period_start, date_to=period_end)
        return {
            "report_type": report_type,
            "state": {"id": str(state.id), "name": state.name},
            "reporting_period_start": period_start.isoformat(),
            "reporting_period_end": period_end.isoformat(),
            "generated_at": timezone.now().isoformat(),
            "dashboard": dashboard,
            "finance": finance,
        }

    @classmethod
    def generate(cls, *, actor, report_type, period_start, period_end):
        state = cls.scoped_state(actor)
        report = StateReport.objects.create(
            state=state,
            report_type=report_type,
            reporting_period_start=period_start,
            reporting_period_end=period_end,
            status=StateReportStatus.GENERATED,
            generated_by=actor,
            data_snapshot=cls.build_snapshot(
                actor=actor,
                report_type=report_type,
                period_start=period_start,
                period_end=period_end,
            ),
        )
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=report, metadata={"event": "state_report_generated"})
        return report

    @classmethod
    def submit(cls, *, report, actor):
        if report.state_id != actor.state_id:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You can only submit reports for your state.")
        if report.status not in {StateReportStatus.DRAFT, StateReportStatus.GENERATED, StateReportStatus.RETURNED}:
            from rest_framework.exceptions import ValidationError

            raise ValidationError("Only draft, generated, or returned reports can be submitted.")
        report.status = StateReportStatus.SUBMITTED
        report.submitted_by = actor
        report.submitted_at = timezone.now()
        report.save(update_fields=["status", "submitted_by", "submitted_at", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=report, metadata={"event": "state_report_submitted"})
        return report


class FederalPerformanceService:
    @classmethod
    def state_metrics(cls, state):
        today = timezone.localdate()
        handlers = FoodHandlerProfile.objects.filter(state=state)
        facilities = MedicalFacility.objects.filter(state=state)
        certificates = Certificate.objects.filter(issuing_state=state)
        employers = Employer.objects.filter(state=state)
        latest_report = StateReport.objects.filter(state=state).order_by("-reporting_period_end", "-created_at").first()
        total_handlers = handlers.count()
        certified_handlers = handlers.filter(
            certificates__status=CertificateStatus.ACTIVE,
            certificates__expiry_date__gte=today,
        ).distinct().count()
        pending_facility_applications = FacilityAccreditationApplication.objects.filter(
            facility__state=state,
            application_status__in=[AccreditationStatus.SUBMITTED, AccreditationStatus.UNDER_REVIEW],
        ).count()
        pending_certificate_validations = CertificateRequest.objects.filter(
            assessment__facility__state=state,
            status=CertificateRequestStatus.PENDING_VALIDATION,
        ).count()
        approved_facilities = facilities.filter(accreditation_status=AccreditationStatus.APPROVED).count()
        inspection_count = Inspection.objects.filter(employer__state=state).count()
        illness_reports = IllnessReport.objects.filter(food_handler__state=state).count()
        data_quality_inputs = [
            employers.exclude(lga__isnull=True).count() / employers.count() if employers.count() else 1,
            handlers.exclude(lga__isnull=True).count() / total_handlers if total_handlers else 1,
            facilities.exclude(lga__isnull=True).count() / facilities.count() if facilities.count() else 1,
            1 if latest_report and latest_report.status in {StateReportStatus.SUBMITTED, StateReportStatus.ACCEPTED} else 0,
        ]
        data_quality_score = round((sum(data_quality_inputs) / len(data_quality_inputs)) * 100, 2)
        return {
            "state_id": str(state.id),
            "state_name": state.name,
            "state_code": state.code,
            "is_fct": state.is_fct,
            "registered_handlers": total_handlers,
            "certified_handlers": certified_handlers,
            "certification_coverage": round((certified_handlers / total_handlers) * 100, 2) if total_handlers else 0,
            "registered_employers": employers.count(),
            "approved_facilities": approved_facilities,
            "pending_facility_applications": pending_facility_applications,
            "pending_certificate_validations": pending_certificate_validations,
            "inspection_count": inspection_count,
            "illness_reports": illness_reports,
            "latest_report_status": latest_report.status if latest_report else "missing",
            "latest_report_period_end": latest_report.reporting_period_end.isoformat() if latest_report else "",
            "data_quality_score": data_quality_score,
        }

    @classmethod
    def state_performance(cls):
        rows = [cls.state_metrics(state) for state in State.objects.order_by("name")]
        totals = {
            "states": len(rows),
            "registered_handlers": sum(row["registered_handlers"] for row in rows),
            "certified_handlers": sum(row["certified_handlers"] for row in rows),
            "approved_facilities": sum(row["approved_facilities"] for row in rows),
            "pending_facility_applications": sum(row["pending_facility_applications"] for row in rows),
            "pending_certificate_validations": sum(row["pending_certificate_validations"] for row in rows),
            "inspection_count": sum(row["inspection_count"] for row in rows),
            "illness_reports": sum(row["illness_reports"] for row in rows),
        }
        totals["certification_coverage"] = round((totals["certified_handlers"] / totals["registered_handlers"]) * 100, 2) if totals["registered_handlers"] else 0
        return {"totals": totals, "states": rows}

    @classmethod
    def state_summary(cls, state_id):
        state = State.objects.get(id=state_id)
        metrics = cls.state_metrics(state)
        reports = StateReport.objects.filter(state=state).order_by("-reporting_period_end", "-created_at")[:6]
        return {
            "state": metrics,
            "reports": [
                {
                    "id": str(report.id),
                    "report_type": report.report_type,
                    "status": report.status,
                    "reporting_period_start": report.reporting_period_start.isoformat(),
                    "reporting_period_end": report.reporting_period_end.isoformat(),
                    "submitted_at": report.submitted_at.isoformat() if report.submitted_at else "",
                }
                for report in reports
            ],
        }


class FederalOversightService:
    @classmethod
    def indicators(cls):
        performance = FederalPerformanceService.state_performance()
        states = performance["states"]
        low_coverage = [row for row in states if row["registered_handlers"] > 0 and row["certification_coverage"] < 50]
        missing_reports = [row for row in states if row["latest_report_status"] == "missing"]
        return {
            "cards": {
                "states_monitored": performance["totals"]["states"],
                "national_certification_coverage": performance["totals"]["certification_coverage"],
                "low_coverage_states": len(low_coverage),
                "missing_reports": len(missing_reports),
                "open_certificate_validations": performance["totals"]["pending_certificate_validations"],
                "open_facility_applications": performance["totals"]["pending_facility_applications"],
            },
            "sections": {
                "low_coverage_states": low_coverage,
                "missing_report_states": missing_reports,
                "top_data_quality_risks": sorted(states, key=lambda row: row["data_quality_score"])[:10],
            },
        }

    @classmethod
    def data_quality(cls):
        risks = []
        for row in FederalPerformanceService.state_performance()["states"]:
            if row["latest_report_status"] == "missing":
                risks.append({"state_id": row["state_id"], "state_name": row["state_name"], "risk": "missing_state_report", "severity": "high", "detail": "No submitted state report found."})
            if row["registered_handlers"] > 0 and row["certification_coverage"] < 50:
                risks.append({"state_id": row["state_id"], "state_name": row["state_name"], "risk": "low_certification_coverage", "severity": "medium", "detail": f"Certification coverage is {row['certification_coverage']}%."})
            if row["pending_certificate_validations"] > 25:
                risks.append({"state_id": row["state_id"], "state_name": row["state_name"], "risk": "stale_certificate_queue", "severity": "medium", "detail": f"{row['pending_certificate_validations']} certificate validations are pending."})
            if row["data_quality_score"] < 75:
                risks.append({"state_id": row["state_id"], "state_name": row["state_name"], "risk": "metadata_completeness", "severity": "medium", "detail": f"Data quality score is {row['data_quality_score']}%."})
        return {"cards": {"risk_count": len(risks)}, "risks": risks}

    @classmethod
    def audit_logs(cls, *, action="", state="", search=""):
        queryset = AuditLog.objects.select_related("actor", "state").order_by("-created_at")
        if action:
            queryset = queryset.filter(action=action)
        if state:
            queryset = queryset.filter(state_id=state)
        if search:
            queryset = queryset.filter(Q(target_type__icontains=search) | Q(target_id__icontains=search) | Q(metadata__icontains=search))
        rows = []
        for log in queryset[:100]:
            risk_level = "low"
            if log.action in {AuditAction.SECURITY_EVENT, AuditAction.MEDICAL_RECORD_ACCESS}:
                risk_level = "high"
            elif log.action in {AuditAction.DELETE, AuditAction.ROLE_CHANGE, AuditAction.PAYMENT_EVENT}:
                risk_level = "medium"
            rows.append(
                {
                    "id": str(log.id),
                    "actor_name": log.actor.get_full_name() if log.actor else "",
                    "actor_email": log.actor.email if log.actor else "",
                    "action": log.action,
                    "target_type": log.target_type,
                    "target_id": log.target_id,
                    "state_name": log.state.name if log.state else "",
                    "metadata": log.metadata,
                    "risk_level": risk_level,
                    "created_at": log.created_at.isoformat(),
                }
            )
        return rows

    @classmethod
    def respond_query(cls, *, query, actor, response):
        query.response = response
        query.responded_by = actor
        query.responded_at = timezone.now()
        query.status = FederalStateQueryStatus.RESPONDED
        query.save(update_fields=["response", "responded_by", "responded_at", "status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=query, state=query.state, metadata={"event": "federal_state_query_responded"})
        return query

    @classmethod
    def close_query(cls, *, query, actor):
        query.status = FederalStateQueryStatus.CLOSED
        query.closed_at = timezone.now()
        query.save(update_fields=["status", "closed_at", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=actor, target=query, state=query.state, metadata={"event": "federal_state_query_closed"})
        return query


def get_state_ministry_organization(user):
    if getattr(user, "organization_id", None) and user.organization.organization_type == OrganizationType.STATE_MINISTRY:
        return user.organization
    if not getattr(user, "state_id", None):
        return None
    organization, _ = Organization.objects.get_or_create(
        organization_type=OrganizationType.STATE_MINISTRY,
        state=user.state,
        defaults={"name": f"{user.state.name} Ministry of Health"},
    )
    return organization
