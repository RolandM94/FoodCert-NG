import csv
import ast
import operator
import re
from decimal import Decimal
from io import StringIO
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from rest_framework.exceptions import PermissionDenied

from apps.accounts.models import User, UserRole, UserStatus
from apps.assessments.models import FitnessDecision, MedicalAssessment, StepStatus
from apps.certificates.models import Certificate, CertificateRequest, CertificateRequestStatus, CertificateStatus, CertificateVerificationLog
from apps.employers.models import Employer
from apps.facilities.models import AccreditationStatus, FacilityAccreditationApplication, MedicalFacility
from apps.food_handlers.models import FoodHandlerProfile, FoodHandlerStatus
from apps.illness.models import IllnessReport
from apps.inspections.models import CorrectiveActionResponse, EnforcementAction, EnforcementCase, EnforcementNotice, Inspection, InspectionFinding, InspectionPriority, InspectionStatus
from apps.lab_tests.models import LabTest, LabTestStatus
from apps.locations.models import LGA, State
from apps.ministries.models import StateReport, StateReportStatus
from apps.organizations.models import Organization, OrganizationStatus, OrganizationUnitType
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.reports.models import DataQualityIssue, DataQualityIssueSeverity, GeneratedReport, GeneratedReportStatus, MEIndicator, MEIndicatorValue, ReportFormat, ReportType
from apps.settlements.models import Settlement, SettlementStatus
from apps.vaccinations.models import VaccinationRecord, VaccinationStatus, VaccineType


def percent(numerator, denominator):
    if not denominator:
        return 0
    return round((numerator / denominator) * 100, 2)


def decimal_string(value):
    return format(Decimal(value or 0).normalize(), "f")


def media_url(relative_path):
    return f"http://localhost:8000{settings.MEDIA_URL}{relative_path}"


class MEIndicatorService:
    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
    }

    @classmethod
    def calculate_indicator(cls, indicator, state=None, lga=None, period_start=None, period_end=None):
        period_start, period_end = cls.normalized_period(period_start, period_end)
        metrics = cls.metric_context(state=state, lga=lga, period_start=period_start, period_end=period_end)
        calculated = cls.evaluate_formula(indicator.formula, metrics)
        numerator, denominator = cls.indicator_components(indicator.code, metrics)
        value, _created = MEIndicatorValue.objects.update_or_create(
            indicator=indicator,
            state=state,
            lga=lga,
            organization=None,
            period_start=period_start,
            period_end=period_end,
            defaults={
                "numerator_value": numerator,
                "denominator_value": denominator,
                "calculated_value": calculated,
                "disaggregation": {"category": indicator.category, "formula": indicator.formula},
            },
        )
        return value

    @classmethod
    def calculate_all_indicators(cls, state=None, period_start=None, period_end=None):
        return [
            cls.calculate_indicator(indicator, state=state, period_start=period_start, period_end=period_end)
            for indicator in MEIndicator.objects.filter(is_active=True).order_by("category", "code")
        ]

    @classmethod
    def calculate_category(cls, category, state=None, period_start=None, period_end=None):
        return [
            cls.calculate_indicator(indicator, state=state, period_start=period_start, period_end=period_end)
            for indicator in MEIndicator.objects.filter(is_active=True, category=category).order_by("code")
        ]

    @classmethod
    def get_indicator_history(cls, indicator_id, periods=12):
        return MEIndicatorValue.objects.filter(indicator_id=indicator_id).select_related("indicator", "state", "lga", "organization").order_by("-period_end")[:periods]

    @classmethod
    def get_state_performance(cls, state_id):
        state = State.objects.get(id=state_id)
        today = timezone.localdate()
        context = cls.metric_context(state=state, period_start=today.replace(day=1), period_end=today)
        compliance_summary = ComplianceStatusService.get_state_compliance_summary(state_id)
        compliance = compliance_summary["compliance_percentage"]
        vaccination = compliance_summary["vaccination_coverage_rate"]
        quality = DashboardService.state_data_quality_score(
            state,
            FoodHandlerProfile.objects.filter(state=state),
            Employer.objects.filter(state=state),
            MedicalFacility.objects.filter(state=state),
        )
        return {
            "state": {"id": str(state.id), "name": state.name, "code": state.code},
            "cards": {
                "registered_food_handlers": int(context["registered_food_handlers"]),
                "certified_food_handlers": int(context["active_certified_handlers"]),
                "compliance_score": compliance,
                "vaccination_score": vaccination,
                "data_quality_score": quality,
                "performance_rating": DashboardService.state_performance_rating(
                    compliance_percentage=compliance,
                    vaccination_coverage_rate=vaccination,
                    inspections_count=int(context["inspections_conducted"]),
                    enforcement_count=int(context["enforcement_notices_issued"]),
                    data_quality_score=quality,
                ),
            },
        }

    @classmethod
    def get_national_summary(cls):
        today = timezone.localdate()
        rows = [DashboardService.federal_state_dashboard_row(state, today) for state in State.objects.order_by("name")]
        totals = {
            "states": len(rows),
            "registered_handlers": sum(row["registered_handlers"] for row in rows),
            "certified_handlers": sum(row["certified_handlers"] for row in rows),
            "approved_facilities": sum(row["approved_facilities"] for row in rows),
            "inspection_count": sum(row["inspection_count"] for row in rows),
            "illness_reports": sum(row["illness_reports"] for row in rows),
        }
        totals["certification_coverage"] = percent(totals["certified_handlers"], totals["registered_handlers"])
        return {"totals": totals, "states": rows}

    @classmethod
    def normalized_period(cls, period_start=None, period_end=None):
        period_end = period_end or timezone.localdate()
        period_start = period_start or period_end.replace(day=1)
        return period_start, period_end

    @classmethod
    def metric_context(cls, state=None, lga=None, period_start=None, period_end=None):
        handlers = FoodHandlerProfile.objects.all()
        employers = Employer.objects.all()
        facilities = MedicalFacility.objects.all()
        certificates = Certificate.objects.all()
        assessments = MedicalAssessment.objects.all()
        inspections = Inspection.objects.all()
        illness = IllnessReport.objects.all()
        payments = PaymentTransaction.objects.all()
        settlements = Settlement.objects.all()
        if state:
            handlers = handlers.filter(state=state)
            employers = employers.filter(state=state)
            facilities = facilities.filter(state=state)
            certificates = certificates.filter(issuing_state=state)
            assessments = assessments.filter(facility__state=state)
            inspections = inspections.filter(employer__state=state)
            illness = illness.filter(food_handler__state=state)
            payments = payments.filter(payer_user__state=state)
            settlements = settlements.filter(state=state)
        if lga:
            handlers = handlers.filter(lga=lga)
            employers = employers.filter(lga=lga)
            facilities = facilities.filter(lga=lga)
            certificates = certificates.filter(food_handler__lga=lga)
            assessments = assessments.filter(food_handler__lga=lga)
            inspections = inspections.filter(employer__lga=lga)
            illness = illness.filter(food_handler__lga=lga)
        if period_start:
            certificates = certificates.filter(issue_date__gte=period_start)
            assessments = assessments.filter(created_at__date__gte=period_start)
            inspections = inspections.filter(inspection_date__date__gte=period_start)
            illness = illness.filter(created_at__date__gte=period_start)
            payments = payments.filter(created_at__date__gte=period_start)
            settlements = settlements.filter(created_at__date__gte=period_start)
        if period_end:
            certificates = certificates.filter(issue_date__lte=period_end)
            assessments = assessments.filter(created_at__date__lte=period_end)
            inspections = inspections.filter(inspection_date__date__lte=period_end)
            illness = illness.filter(created_at__date__lte=period_end)
            payments = payments.filter(created_at__date__lte=period_end)
            settlements = settlements.filter(created_at__date__lte=period_end)
        all_handlers = FoodHandlerProfile.objects.filter(state=state) if state else FoodHandlerProfile.objects.all()
        if lga:
            all_handlers = all_handlers.filter(lga=lga)
        today = timezone.localdate()
        successful_payments = payments.filter(status=PaymentStatus.SUCCESS)
        paid_settlements = settlements.filter(settlement_status=SettlementStatus.PAID)
        return {
            "registered_food_handlers": Decimal(all_handlers.count()),
            "registered_employers": Decimal(employers.count()),
            "registered_medical_facilities": Decimal(facilities.count()),
            "approved_medical_facilities": Decimal(facilities.filter(accreditation_status=AccreditationStatus.APPROVED).count()),
            "certificates_issued": Decimal(certificates.count()),
            "active_certified_handlers": Decimal(all_handlers.filter(certificates__status=CertificateStatus.ACTIVE, certificates__expiry_date__gte=today).distinct().count()),
            "active_certificates": Decimal(certificates.filter(status=CertificateStatus.ACTIVE, expiry_date__gte=today).count()),
            "expired_certificates": Decimal(certificates.filter(expiry_date__lt=today).count()),
            "revoked_certificates": Decimal(certificates.filter(status=CertificateStatus.REVOKED).count()),
            "suspended_certificates": Decimal(certificates.filter(status=CertificateStatus.SUSPENDED).count()),
            "assessments_initiated": Decimal(assessments.count()),
            "assessments_completed": Decimal(assessments.exclude(signed_at__isnull=True).count()),
            "fit_decisions": Decimal(assessments.filter(final_decision=FitnessDecision.FIT).count()),
            "temporarily_not_fit_decisions": Decimal(assessments.filter(final_decision=FitnessDecision.TEMPORARILY_NOT_FIT).count()),
            "valid_typhoid": Decimal(all_handlers.filter(vaccinations__vaccine_type=VaccineType.TYPHOID, vaccinations__status=VaccinationStatus.VALID).distinct().count()),
            "valid_vaccinated_handlers": Decimal(all_handlers.filter(vaccinations__status=VaccinationStatus.VALID).distinct().count()),
            "inspections_conducted": Decimal(inspections.count()),
            "enforcement_notices_issued": Decimal(inspections.exclude(enforcement_action=EnforcementAction.NONE).count()),
            "illness_reports": Decimal(illness.count()),
            "return_to_work_pending": Decimal(illness.filter(clearance_status__in=["pending", "under_review", "clearance_required"]).count()),
            "assessment_revenue": Decimal(successful_payments.aggregate(total=Sum("amount"))["total"] or 0),
            "state_revenue_share": Decimal(paid_settlements.aggregate(total=Sum("state_amount"))["total"] or 0),
            "facility_settlement_amount": Decimal(paid_settlements.aggregate(total=Sum("facility_amount"))["total"] or 0),
            "failed_payments": Decimal(payments.filter(status=PaymentStatus.FAILED).count()),
            "total_payments": Decimal(payments.count()),
        }

    @classmethod
    def indicator_components(cls, code, metrics):
        if code.endswith("certification_coverage_rate"):
            return metrics.get("active_certified_handlers"), metrics.get("registered_food_handlers")
        if code.endswith("vaccination_coverage"):
            return metrics.get("valid_typhoid"), metrics.get("registered_food_handlers")
        component_map = {
            "certification_coverage_rate": ("active_certified_handlers", "registered_food_handlers"),
            "typhoid_vaccination_coverage": ("valid_typhoid", "registered_food_handlers"),
            "employer_compliance_rate": ("active_certified_handlers", "registered_food_handlers"),
            "inspection_coverage_rate": ("inspections_conducted", "registered_employers"),
            "failed_payment_rate": ("failed_payments", "total_payments"),
            "assessment_revenue": ("assessment_revenue", None),
            "state_revenue_share": ("state_revenue_share", None),
            "facility_settlement_amount": ("facility_settlement_amount", None),
        }
        numerator_key, denominator_key = component_map.get(code, (None, None))
        return metrics.get(numerator_key) if numerator_key else None, metrics.get(denominator_key) if denominator_key else None

    @classmethod
    def evaluate_formula(cls, formula, metrics):
        expression = formula.strip().lower()
        function_match = re.fullmatch(r"(count|sum|avg)\(([^)]+)\)", expression)
        if function_match:
            key = cls.metric_key(function_match.group(2))
            return metrics.get(key, Decimal("0"))
        expression = re.sub(r"\bcount\(([^)]+)\)", lambda match: str(metrics.get(cls.metric_key(match.group(1)), Decimal("0"))), expression)
        expression = re.sub(r"\bsum\(([^)]+)\)", lambda match: str(metrics.get(cls.metric_key(match.group(1)), Decimal("0"))), expression)
        expression = re.sub(r"\bavg\(([^)]+)\)", lambda match: str(metrics.get(cls.metric_key(match.group(1)), Decimal("0"))), expression)
        for key, value in sorted(metrics.items(), key=lambda item: len(item[0]), reverse=True):
            expression = re.sub(rf"\b{re.escape(key)}\b", str(value), expression)
        if re.search(r"[A-Za-z_]", expression):
            return Decimal("0")
        try:
            return Decimal(str(round(cls.safe_eval(expression), 4)))
        except (ArithmeticError, SyntaxError, ValueError, ZeroDivisionError):
            return Decimal("0")

    @classmethod
    def metric_key(cls, raw):
        return re.sub(r"[^a-z0-9]+", "_", raw.strip().lower()).strip("_")

    @classmethod
    def safe_eval(cls, expression):
        node = ast.parse(expression, mode="eval").body
        return cls.eval_node(node)

    @classmethod
    def eval_node(cls, node):
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in cls.ALLOWED_OPERATORS:
            return cls.ALLOWED_OPERATORS[type(node.op)](cls.eval_node(node.left), cls.eval_node(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in cls.ALLOWED_OPERATORS:
            return cls.ALLOWED_OPERATORS[type(node.op)](cls.eval_node(node.operand))
        raise ValueError("Unsupported formula expression.")


class ComplianceStatusService:
    @classmethod
    def get_food_handler_operational_status(cls, food_handler_id):
        handler = FoodHandlerProfile.objects.select_related("employer", "business_branch", "state").get(id=food_handler_id)
        today = timezone.localdate()
        certificate = handler.certificates.order_by("-expiry_date", "-created_at").first()
        active_certificate = handler.certificates.filter(status=CertificateStatus.ACTIVE, expiry_date__gte=today).order_by("-expiry_date").first()
        illness = IllnessReport.objects.filter(food_handler=handler).order_by("-created_at").first()
        typhoid_valid = handler.vaccinations.filter(vaccine_type=VaccineType.TYPHOID, status=VaccinationStatus.VALID).exists()
        metrics = {
            "has_active_certificate": bool(active_certificate),
            "certificate_status": active_certificate.effective_status if active_certificate else certificate.effective_status if certificate else "not_issued",
            "certificate_expiry_date": active_certificate.expiry_date.isoformat() if active_certificate else certificate.expiry_date.isoformat() if certificate else "",
            "days_to_expiry": (active_certificate.expiry_date - today).days if active_certificate else None,
            "typhoid_valid": typhoid_valid,
            "return_to_work_status": illness.clearance_status if illness else "not_applicable",
            "current_status": handler.current_status,
        }
        metrics["overall_status"] = cls.get_overall_compliance_status(metrics)
        metrics["overall_compliance_status"] = metrics["overall_status"]
        return metrics

    @classmethod
    def get_branch_compliance_summary(cls, branch_id):
        handlers = FoodHandlerProfile.objects.filter(business_branch_id=branch_id)
        summary = cls.handler_queryset_summary(handlers)
        summary["branch_id"] = str(branch_id)
        return summary

    @classmethod
    def get_employer_compliance_summary(cls, employer_id):
        handlers = FoodHandlerProfile.objects.filter(employer_id=employer_id)
        summary = cls.handler_queryset_summary(handlers)
        summary["employer_id"] = str(employer_id)
        summary["open_inspections"] = Inspection.objects.filter(employer_id=employer_id).exclude(status__in=[InspectionStatus.CLOSED, InspectionStatus.CANCELLED]).count()
        return summary

    @classmethod
    def get_state_compliance_summary(cls, state_id):
        handlers = FoodHandlerProfile.objects.filter(state_id=state_id)
        summary = cls.handler_queryset_summary(handlers)
        summary["state_id"] = str(state_id)
        summary["registered_employers"] = Employer.objects.filter(state_id=state_id).count()
        summary["approved_facilities"] = MedicalFacility.objects.filter(state_id=state_id, accreditation_status=AccreditationStatus.APPROVED).count()
        summary["inspections_conducted"] = Inspection.objects.filter(employer__state_id=state_id).count()
        summary["enforcement_notices"] = Inspection.objects.filter(employer__state_id=state_id).exclude(enforcement_action=EnforcementAction.NONE).count()
        return summary

    @classmethod
    def get_national_compliance_summary(cls):
        handlers = FoodHandlerProfile.objects.all()
        summary = cls.handler_queryset_summary(handlers)
        summary["registered_employers"] = Employer.objects.count()
        summary["approved_facilities"] = MedicalFacility.objects.filter(accreditation_status=AccreditationStatus.APPROVED).count()
        summary["inspections_conducted"] = Inspection.objects.count()
        summary["enforcement_notices"] = Inspection.objects.exclude(enforcement_action=EnforcementAction.NONE).count()
        return summary

    @classmethod
    def handler_queryset_summary(cls, handlers):
        today = timezone.localdate()
        total = handlers.count()
        active_certified = handlers.filter(certificates__status=CertificateStatus.ACTIVE, certificates__expiry_date__gte=today).distinct().count()
        expired = handlers.filter(certificates__expiry_date__lt=today).distinct().count()
        expiring_soon = handlers.filter(certificates__status=CertificateStatus.ACTIVE, certificates__expiry_date__range=(today, today + timezone.timedelta(days=30))).distinct().count()
        typhoid_valid = handlers.filter(vaccinations__vaccine_type=VaccineType.TYPHOID, vaccinations__status=VaccinationStatus.VALID).distinct().count()
        temporarily_not_fit = handlers.filter(current_status__in=[FoodHandlerStatus.TEMPORARILY_NOT_FIT, FoodHandlerStatus.TEMPORARILY_EXCLUDED]).count()
        return_to_work_pending = IllnessReport.objects.filter(food_handler__in=handlers, clearance_status__in=["pending", "under_review", "clearance_required"]).count()
        metrics = {
            "registered_food_handlers": total,
            "total_food_handlers": total,
            "valid_certificates": active_certified,
            "certified_food_handlers": active_certified,
            "expired_certificates": expired,
            "expiring_soon": expiring_soon,
            "not_certified": max(total - active_certified, 0),
            "typhoid_vaccination_valid": typhoid_valid,
            "vaccination_coverage_rate": percent(typhoid_valid, total),
            "temporarily_not_fit": temporarily_not_fit,
            "return_to_work_pending": return_to_work_pending,
            "compliance_percentage": percent(active_certified, total),
        }
        metrics["overall_status"] = cls.get_overall_compliance_status(metrics)
        metrics["overall_compliance_status"] = metrics["overall_status"]
        return metrics

    @classmethod
    def get_overall_compliance_status(cls, metrics):
        if metrics.get("current_status") in {FoodHandlerStatus.EXCLUDED, FoodHandlerStatus.TEMPORARILY_EXCLUDED, FoodHandlerStatus.TEMPORARILY_NOT_FIT}:
            return "high_risk"
        if metrics.get("return_to_work_status") in {"pending", "under_review", "clearance_required"}:
            return "high_risk"
        if metrics.get("has_active_certificate") is False:
            return "non_compliant"
        compliance = metrics.get("compliance_percentage")
        if compliance is None and "valid_certificates" in metrics and "total_food_handlers" in metrics:
            compliance = percent(metrics["valid_certificates"], metrics["total_food_handlers"])
        if compliance is not None:
            if compliance >= 90:
                return "compliant"
            if compliance >= 50:
                return "partially_compliant"
            return "non_compliant"
        if metrics.get("has_active_certificate") and metrics.get("typhoid_valid", True):
            return "compliant"
        return "partially_compliant"


class AnalyticsService:
    @classmethod
    def filters_from_request(cls, validated_data, user=None):
        filters = dict(validated_data)
        if user and user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR} and user.state_id:
            filters["state"] = user.state_id
        return filters

    @classmethod
    def apply_common_filters(cls, queryset, filters, paths, date_field="created_at"):
        state = filters.get("state")
        lga = filters.get("lga")
        employer_category = filters.get("employer_category")
        facility_type = filters.get("facility_type")
        date_from = filters.get("date_from")
        date_to = filters.get("date_to")
        if state and paths.get("state"):
            queryset = queryset.filter(**{paths["state"]: state})
        if lga and paths.get("lga"):
            queryset = queryset.filter(**{paths["lga"]: lga})
        if employer_category and paths.get("employer_category"):
            queryset = queryset.filter(**{paths["employer_category"]: employer_category})
        if facility_type and paths.get("facility_type"):
            queryset = queryset.filter(**{paths["facility_type"]: facility_type})
        model_field = queryset.model._meta.get_field(date_field.split("__", 1)[0])
        lookup = f"{date_field}__date" if isinstance(model_field, models.DateTimeField) else date_field
        if date_from:
            queryset = queryset.filter(**{f"{lookup}__gte": date_from})
        if date_to:
            queryset = queryset.filter(**{f"{lookup}__lte": date_to})
        return queryset

    @classmethod
    def by_month(cls, queryset, date_field, count_field="id", total_field=None):
        rows = queryset.annotate(month=TruncMonth(date_field)).values("month").annotate(total=Count(count_field))
        if total_field:
            rows = rows.annotate(amount=Sum(total_field))
        return [
            {
                "month": row["month"].date().isoformat() if hasattr(row["month"], "date") else row["month"].isoformat() if hasattr(row["month"], "isoformat") else str(row["month"]),
                "total": row["total"],
                **({"amount": str(row["amount"] or 0)} if total_field else {}),
            }
            for row in rows.order_by("month")
            if row["month"]
        ]

    @classmethod
    def grouped_counts(cls, queryset, field):
        return list(queryset.values(field).annotate(total=Count("id")).order_by(field))

    @classmethod
    def certificate_analytics(cls, filters):
        certs = cls.apply_common_filters(
            Certificate.objects.select_related("issuing_state", "food_handler", "employer", "facility"),
            filters,
            {
                "state": "issuing_state_id",
                "lga": "food_handler__lga_id",
                "employer_category": "employer__establishment_category",
                "facility_type": "facility__facility_type",
            },
            "issue_date",
        )
        verification_logs = cls.apply_common_filters(
            CertificateVerificationLog.objects.select_related("certificate", "certificate__issuing_state"),
            filters,
            {"state": "certificate__issuing_state_id", "lga": "certificate__food_handler__lga_id"},
            "verified_at",
        )
        today = timezone.localdate()
        return {
            "cards": {
                "issued": certs.count(),
                "active": certs.filter(status=CertificateStatus.ACTIVE, expiry_date__gte=today).count(),
                "expired": certs.filter(expiry_date__lt=today).count(),
                "expiring_soon": certs.filter(status=CertificateStatus.ACTIVE, expiry_date__gte=today, expiry_date__lte=today + timezone.timedelta(days=30)).count(),
                "verification_attempts": verification_logs.count(),
            },
            "charts": {
                "issuance_trend": cls.by_month(certs, "issue_date"),
                "expiry_trend": cls.by_month(certs, "expiry_date"),
                "status": cls.grouped_counts(certs, "status"),
                "verification_results": cls.grouped_counts(verification_logs, "result"),
                "by_state": list(certs.values("issuing_state__name").annotate(total=Count("id")).order_by("issuing_state__name")),
            },
        }

    @classmethod
    def assessment_analytics(cls, filters):
        assessments = cls.apply_common_filters(
            MedicalAssessment.objects.select_related("facility", "employer"),
            filters,
            {
                "state": "facility__state_id",
                "lga": "facility__lga_id",
                "employer_category": "employer__establishment_category",
                "facility_type": "facility__facility_type",
            },
            "created_at",
        )
        return {
            "cards": {
                "total_assessments": assessments.count(),
                "completed_assessments": assessments.exclude(signed_at__isnull=True).count(),
                "fit_decisions": assessments.filter(final_decision=FitnessDecision.FIT).count(),
                "temporarily_not_fit": assessments.filter(final_decision=FitnessDecision.TEMPORARILY_NOT_FIT).count(),
                "average_turnaround_hours": DashboardService.average_turnaround_hours(assessments),
            },
            "charts": {
                "volume_trend": cls.by_month(assessments, "created_at"),
                "decision_distribution": cls.grouped_counts(assessments, "final_decision"),
                "status_distribution": cls.grouped_counts(assessments, "status"),
                "by_facility": list(assessments.values("facility__facility_name").annotate(total=Count("id")).order_by("facility__facility_name")),
            },
        }

    @classmethod
    def vaccination_analytics(cls, filters):
        records = cls.apply_common_filters(
            VaccinationRecord.objects.select_related("food_handler", "food_handler__employer"),
            filters,
            {
                "state": "food_handler__state_id",
                "lga": "food_handler__lga_id",
                "employer_category": "food_handler__employer__establishment_category",
            },
            "date_administered",
        )
        handlers = cls.apply_common_filters(
            FoodHandlerProfile.objects.select_related("employer"),
            filters,
            {"state": "state_id", "lga": "lga_id", "employer_category": "employer__establishment_category"},
            "created_at",
        )
        valid_typhoid = handlers.filter(vaccinations__vaccine_type=VaccineType.TYPHOID, vaccinations__status=VaccinationStatus.VALID).distinct().count()
        return {
            "cards": {
                "records": records.count(),
                "valid_typhoid_handlers": valid_typhoid,
                "registered_food_handlers": handlers.count(),
                "coverage_rate": percent(valid_typhoid, handlers.count()),
                "second_dose_due": records.filter(status=VaccinationStatus.SECOND_DOSE_DUE).count(),
            },
            "charts": {
                "coverage_by_lga": list(handlers.values("lga__name").annotate(total=Count("id"), valid=Count("vaccinations", filter=Q(vaccinations__vaccine_type=VaccineType.TYPHOID, vaccinations__status=VaccinationStatus.VALID), distinct=True)).order_by("lga__name")),
                "status_distribution": cls.grouped_counts(records, "status"),
                "vaccine_type_distribution": cls.grouped_counts(records, "vaccine_type"),
                "administration_trend": cls.by_month(records, "date_administered"),
            },
        }

    @classmethod
    def facility_analytics(cls, filters):
        facilities = cls.apply_common_filters(
            MedicalFacility.objects.all(),
            filters,
            {"state": "state_id", "lga": "lga_id", "facility_type": "facility_type"},
            "created_at",
        )
        today = timezone.localdate()
        return {
            "cards": {
                "facilities": facilities.count(),
                "approved": facilities.filter(accreditation_status=AccreditationStatus.APPROVED).count(),
                "suspended": facilities.filter(accreditation_status=AccreditationStatus.SUSPENDED).count(),
                "renewal_due_60_days": facilities.filter(accreditation_expiry_date__gte=today, accreditation_expiry_date__lte=today + timezone.timedelta(days=60)).count(),
            },
            "charts": {
                "accreditation_status": cls.grouped_counts(facilities, "accreditation_status"),
                "facility_type": cls.grouped_counts(facilities, "facility_type"),
                "registration_trend": cls.by_month(facilities, "created_at"),
                "renewal_trend": cls.by_month(facilities.exclude(accreditation_expiry_date__isnull=True), "accreditation_expiry_date"),
            },
        }

    @classmethod
    def employer_analytics(cls, filters):
        employers = cls.apply_common_filters(
            Employer.objects.all(),
            filters,
            {"state": "state_id", "lga": "lga_id", "employer_category": "establishment_category"},
            "created_at",
        )
        return {
            "cards": {
                "employers": employers.count(),
                "compliant": employers.filter(compliance_status="compliant").count(),
                "active_subscriptions": employers.filter(subscription_status="active").count(),
                "linked_handlers": FoodHandlerProfile.objects.filter(employer__in=employers).count(),
            },
            "charts": {
                "compliance_status": cls.grouped_counts(employers, "compliance_status"),
                "subscription_status": cls.grouped_counts(employers, "subscription_status"),
                "establishment_category": cls.grouped_counts(employers, "establishment_category"),
                "branch_by_state": list(
                    employers.values("state__name")
                    .annotate(
                        total=Count(
                            "organization__units",
                            filter=Q(organization__units__unit_type=OrganizationUnitType.BRANCH),
                            distinct=True,
                        )
                    )
                    .order_by("state__name")
                ),
            },
        }

    @classmethod
    def inspection_analytics(cls, filters):
        inspections = cls.apply_common_filters(
            Inspection.objects.select_related("employer"),
            filters,
            {"state": "employer__state_id", "lga": "employer__lga_id", "employer_category": "employer__establishment_category"},
            "inspection_date",
        )
        findings = InspectionFinding.objects.filter(inspection__in=inspections)
        return {
            "cards": {
                "inspections": inspections.count(),
                "completed": inspections.filter(status=InspectionStatus.CLOSED).count(),
                "enforcement_actions": inspections.exclude(enforcement_action=EnforcementAction.NONE).count(),
                "average_compliance_score": float(inspections.aggregate(avg=Avg("compliance_score"))["avg"] or 0),
            },
            "charts": {
                "inspection_trend": cls.by_month(inspections, "inspection_date"),
                "outcomes": cls.grouped_counts(inspections, "enforcement_action"),
                "status_distribution": cls.grouped_counts(inspections, "status"),
                "findings_by_severity": cls.grouped_counts(findings, "severity"),
            },
        }

    @classmethod
    def enforcement_analytics(cls, filters):
        notices = cls.apply_common_filters(
            EnforcementNotice.objects.select_related("employer"),
            filters,
            {"state": "employer__state_id", "lga": "employer__lga_id", "employer_category": "employer__establishment_category"},
            "created_at",
        )
        actions = CorrectiveActionResponse.objects.filter(notice__in=notices)
        cases = cls.apply_common_filters(
            EnforcementCase.objects.select_related("state", "employer"),
            filters,
            {"state": "state_id", "lga": "employer__lga_id", "employer_category": "employer__establishment_category"},
            "created_at",
        )
        return {
            "cards": {
                "notices": notices.count(),
                "corrective_actions": actions.count(),
                "open_cases": cases.exclude(status__in=["resolved", "closed"]).count(),
                "escalated_cases": cases.filter(status="escalated").count(),
            },
            "charts": {
                "notice_type": cls.grouped_counts(notices, "notice_type"),
                "notice_status": cls.grouped_counts(notices, "status"),
                "corrective_action_status": cls.grouped_counts(actions, "status"),
                "case_severity": cls.grouped_counts(cases, "severity"),
            },
        }

    @classmethod
    def illness_analytics(cls, filters):
        illness = cls.apply_common_filters(
            IllnessReport.objects.select_related("food_handler", "employer"),
            filters,
            {"state": "food_handler__state_id", "lga": "food_handler__lga_id", "employer_category": "employer__establishment_category"},
            "created_at",
        )
        return {
            "cards": {
                "illness_reports": illness.count(),
                "active_exclusions": illness.exclude(clearance_status__in=["cleared", "rejected"]).count(),
                "return_to_work_pending": illness.filter(clearance_status__in=["pending", "under_review", "clearance_required"]).count(),
                "cleared": illness.filter(clearance_status="cleared").count(),
            },
            "charts": {
                "trend": cls.by_month(illness, "created_at"),
                "clearance_status": cls.grouped_counts(illness, "clearance_status"),
                "by_state": list(illness.values("food_handler__state__name").annotate(total=Count("id")).order_by("food_handler__state__name")),
            },
        }

    @classmethod
    def payment_analytics(cls, filters):
        payments = cls.apply_common_filters(
            PaymentTransaction.objects.select_related("payer_user"),
            filters,
            {"state": "payer_user__state_id"},
            "created_at",
        )
        return {
            "cards": {
                "transactions": payments.count(),
                "successful": payments.filter(status=PaymentStatus.SUCCESS).count(),
                "failed": payments.filter(status=PaymentStatus.FAILED).count(),
                "revenue": str(payments.filter(status=PaymentStatus.SUCCESS).aggregate(total=Sum("amount"))["total"] or 0),
            },
            "charts": {
                "status_distribution": cls.grouped_counts(payments, "status"),
                "provider_distribution": cls.grouped_counts(payments, "payment_provider"),
                "revenue_trend": cls.by_month(payments.filter(status=PaymentStatus.SUCCESS), "created_at", total_field="amount"),
            },
        }

    @classmethod
    def settlement_analytics(cls, filters):
        settlements = cls.apply_common_filters(
            Settlement.objects.select_related("state", "facility"),
            filters,
            {"state": "state_id", "facility_type": "facility__facility_type"},
            "created_at",
        )
        return {
            "cards": {
                "settlements": settlements.count(),
                "paid": settlements.filter(settlement_status=SettlementStatus.PAID).count(),
                "pending": settlements.filter(settlement_status=SettlementStatus.PENDING).count(),
                "gross_amount": str(settlements.aggregate(total=Sum("gross_amount"))["total"] or 0),
                "state_amount": str(settlements.aggregate(total=Sum("state_amount"))["total"] or 0),
            },
            "charts": {
                "status_distribution": cls.grouped_counts(settlements, "settlement_status"),
                "dispute_status": cls.grouped_counts(settlements, "dispute_status"),
                "amount_trend": cls.by_month(settlements, "created_at", total_field="gross_amount"),
                "by_state": list(settlements.values("state__name").annotate(total=Count("id"), amount=Sum("gross_amount")).order_by("state__name")),
            },
        }

    @classmethod
    def data_quality_analytics(cls, filters):
        issues = cls.apply_common_filters(
            DataQualityIssue.objects.select_related("state", "organization"),
            filters,
            {"state": "state_id"},
            "created_at",
        )
        return {
            "cards": {
                "issues": issues.count(),
                "open": issues.filter(status="open").count(),
                "high_or_critical": issues.filter(severity__in=[DataQualityIssueSeverity.HIGH, DataQualityIssueSeverity.CRITICAL]).count(),
                "resolved": issues.filter(status="resolved").count(),
            },
            "charts": {
                "issue_type": cls.grouped_counts(issues, "issue_type"),
                "severity": cls.grouped_counts(issues, "severity"),
                "status": cls.grouped_counts(issues, "status"),
                "module": cls.grouped_counts(issues, "module"),
            },
        }


class DashboardService:
    @classmethod
    def food_handler_for_user(cls, user):
        if user.role != UserRole.FOOD_HANDLER:
            raise PermissionDenied("You cannot access food handler dashboards.")
        profile = getattr(user, "food_handler_profile", None)
        if not profile:
            return None
        return profile

    @classmethod
    def food_handler_dashboard(cls, user):
        food_handler = cls.food_handler_for_user(user)
        if not food_handler:
            return {"food_handler": None, "cards": {}, "sections": {}}
        today = timezone.localdate()
        renewal_window = today + timezone.timedelta(days=90)
        certificate = (
            Certificate.objects.select_related("facility", "issuing_state")
            .filter(food_handler=food_handler)
            .order_by("-issue_date", "-created_at")
            .first()
        )
        latest_assessment = (
            MedicalAssessment.objects.select_related("facility", "doctor", "employer")
            .filter(food_handler=food_handler)
            .order_by("-created_at")
            .first()
        )
        vaccinations = VaccinationRecord.objects.filter(food_handler=food_handler).order_by("vaccine_type", "dose_number", "-date_administered")
        latest_illness = IllnessReport.objects.filter(food_handler=food_handler).order_by("-created_at").first()
        certificate_status = certificate.effective_status if certificate else "not_issued"
        certificate_expiry_date = certificate.expiry_date if certificate else None
        days_to_expiry = (certificate_expiry_date - today).days if certificate_expiry_date else None
        if not certificate:
            renewal_status = "not_available"
        elif certificate.effective_status != CertificateStatus.ACTIVE:
            renewal_status = "renewal_required"
        elif certificate.expiry_date <= renewal_window:
            renewal_status = "renewal_due"
        else:
            renewal_status = "current"
        vaccination_status = cls.food_handler_vaccination_status(vaccinations)
        return_to_work_status = latest_illness.clearance_status if latest_illness else "not_applicable"
        compliance = ComplianceStatusService.get_food_handler_operational_status(food_handler.id)
        return {
            "food_handler": {
                "id": str(food_handler.id),
                "system_identifier": food_handler.system_identifier,
                "full_name": food_handler.full_name,
                "current_status": food_handler.current_status,
                "state": food_handler.state.name if food_handler.state else "",
                "employer": food_handler.employer.business_name if food_handler.employer else "",
            },
            "cards": {
                "certificate_status": certificate_status,
                "certificate_expiry_date": certificate_expiry_date.isoformat() if certificate_expiry_date else "",
                "days_to_expiry": days_to_expiry,
                "assessment_status": latest_assessment.status if latest_assessment else "not_started",
                "vaccination_status": vaccination_status,
                "renewal_status": renewal_status,
                "return_to_work_status": return_to_work_status,
                "overall_compliance_status": compliance["overall_status"],
            },
            "sections": {
                "my_certificate": cls.food_handler_certificate_payload(certificate, today),
                "my_assessment": cls.food_handler_assessment_payload(latest_assessment),
                "vaccination_records": [
                    {
                        "id": str(record.id),
                        "vaccine_type": record.vaccine_type,
                        "dose_number": record.dose_number,
                        "date_administered": record.date_administered.isoformat() if record.date_administered else "",
                        "expiry_date": record.expiry_date.isoformat() if record.expiry_date else "",
                        "next_due": record.next_dose_date.isoformat() if record.next_dose_date else "",
                        "reminder_date": record.reminder_date.isoformat() if record.reminder_date else "",
                        "status": record.status,
                        "compliance_status": record.compliance_status,
                    }
                    for record in vaccinations[:12]
                ],
                "renewal_reminders": cls.food_handler_renewal_reminders(certificate, today, renewal_window),
                "illness_return_to_work": cls.food_handler_illness_payload(latest_illness),
            },
        }

    @classmethod
    def food_handler_vaccination_status(cls, vaccinations):
        records = list(vaccinations)
        if not records:
            return "missing"
        if any(record.status in {VaccinationStatus.EXPIRED, VaccinationStatus.MISSING, VaccinationStatus.INCOMPLETE} for record in records):
            return "attention_required"
        if any(record.status == VaccinationStatus.SECOND_DOSE_DUE for record in records):
            return "second_dose_due"
        return "current"

    @classmethod
    def food_handler_certificate_payload(cls, certificate, today):
        if not certificate:
            return None
        return {
            "id": str(certificate.id),
            "certificate_number": certificate.certificate_number,
            "issue_date": certificate.issue_date.isoformat(),
            "expiry_date": certificate.expiry_date.isoformat(),
            "status": certificate.effective_status,
            "days_to_expiry": (certificate.expiry_date - today).days,
            "facility": certificate.facility.facility_name,
            "issuing_state": certificate.issuing_state.name,
            "verification_url": certificate.verification_url,
            "pdf_url": certificate.pdf_url,
        }

    @classmethod
    def food_handler_assessment_payload(cls, assessment):
        if not assessment:
            return None
        return {
            "id": str(assessment.id),
            "status": assessment.status,
            "facility": assessment.facility.facility_name if assessment.facility else "",
            "doctor": assessment.doctor.get_full_name() if assessment.doctor else "",
            "decision": assessment.final_decision,
            "return_to_work_date": assessment.return_to_work_date.isoformat() if assessment.return_to_work_date else "",
            "declaration_status": assessment.declaration_status,
            "physical_exam_status": assessment.physical_exam_status,
            "lab_status": assessment.lab_status,
            "vaccination_status": assessment.vaccination_status,
            "signed_at": assessment.signed_at.isoformat() if assessment.signed_at else "",
        }

    @classmethod
    def food_handler_renewal_reminders(cls, certificate, today, renewal_window):
        if not certificate:
            return [{"type": "certificate", "status": "not_issued", "message": "Start a medical assessment to obtain a certificate."}]
        if certificate.effective_status != CertificateStatus.ACTIVE:
            return [{"type": "certificate", "status": certificate.effective_status, "message": "Renewal is required before food handling clearance can be current."}]
        if certificate.expiry_date <= renewal_window:
            return [
                {
                    "type": "certificate",
                    "status": "due",
                    "expiry_date": certificate.expiry_date.isoformat(),
                    "days_to_expiry": (certificate.expiry_date - today).days,
                    "message": "Certificate renewal is due within 90 days.",
                }
            ]
        return []

    @classmethod
    def food_handler_illness_payload(cls, illness):
        if not illness:
            return None
        return {
            "id": str(illness.id),
            "clearance_status": illness.clearance_status,
            "suspected_condition": illness.suspected_condition,
            "exclusion_start_date": illness.exclusion_start_date.isoformat() if illness.exclusion_start_date else "",
            "earliest_return_date": illness.earliest_return_date.isoformat() if illness.earliest_return_date else "",
            "cleared_at": illness.cleared_at.isoformat() if illness.cleared_at else "",
            "return_to_work_certificate_number": illness.return_to_work_certificate_number,
        }

    @classmethod
    def employer_for_user(cls, user, employer_id=None):
        queryset = Employer.objects.all()
        if user.role == UserRole.EMPLOYER:
            own = getattr(user, "employer", None)
            if own:
                return own
            if user.organization_id:
                return queryset.filter(organization=user.organization).first()
            return None
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return queryset.filter(id=employer_id).first() if employer_id else queryset.first()
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return queryset.filter(state=user.state, id=employer_id).first() if employer_id else queryset.filter(state=user.state).first()
        raise PermissionDenied("You cannot access employer dashboards.")

    @classmethod
    def facility_for_user(cls, user, facility_id=None):
        queryset = MedicalFacility.objects.all()
        if user.organization_id:
            own = queryset.filter(organization=user.organization).first()
            if own:
                return own
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return queryset.filter(id=facility_id).first() if facility_id else queryset.first()
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return queryset.filter(state=user.state, id=facility_id).first() if facility_id else queryset.filter(state=user.state).first()
        raise PermissionDenied("You cannot access facility dashboards.")

    @classmethod
    def doctor_dashboard(cls, user, facility_id=None):
        if user.role != UserRole.DOCTOR:
            raise PermissionDenied("You cannot access doctor dashboards.")
        assessments = MedicalAssessment.objects.select_related("food_handler", "facility", "employer").filter(doctor=user)
        if facility_id:
            assessments = assessments.filter(facility_id=facility_id)
        elif user.organization_id:
            assessments = assessments.filter(facility__organization=user.organization)
        handler_ids = assessments.values_list("food_handler_id", flat=True)
        lab_tests = LabTest.objects.select_related("assessment", "assessment__food_handler").filter(assessment__in=assessments)
        return_to_work_reports = IllnessReport.objects.select_related("food_handler").filter(
            food_handler_id__in=handler_ids,
            clearance_status__in=["pending", "under_review", "clearance_required"],
        )
        pending_queue = cls.doctor_pending_queue(assessments, lab_tests)
        recent_decisions = assessments.exclude(final_decision=FitnessDecision.PENDING).order_by("-signed_at", "-updated_at")[:8]
        return {
            "doctor": {
                "id": str(user.id),
                "name": user.get_full_name() or user.username,
                "facility": user.organization.name if user.organization else "",
            },
            "filters": {"facility": str(facility_id) if facility_id else ""},
            "cards": {
                "assigned_assessments": assessments.count(),
                "declaration_reviews_pending": assessments.filter(declaration_status=StepStatus.SUBMITTED).count(),
                "physical_exams_pending": assessments.filter(physical_exam_status=StepStatus.PENDING).count(),
                "lab_results_pending_review": lab_tests.filter(status__in=[LabTestStatus.RESULT_UPLOADED, LabTestStatus.SUBMITTED_TO_DOCTOR]).count()
                + assessments.filter(lab_status=StepStatus.SUBMITTED).count(),
                "vaccination_reviews_pending": assessments.exclude(vaccination_status=StepStatus.REVIEWED).count(),
                "decisions_pending": assessments.filter(final_decision=FitnessDecision.PENDING).count(),
                "temporarily_not_fit_cases": assessments.filter(final_decision=FitnessDecision.TEMPORARILY_NOT_FIT).count(),
                "return_to_work_reviews_pending": return_to_work_reports.count(),
            },
            "sections": {
                "pending_queue": pending_queue,
                "recent_decisions": [
                    {
                        "id": str(item.id),
                        "food_handler": item.food_handler.full_name,
                        "facility": item.facility.facility_name if item.facility else "",
                        "decision": item.final_decision,
                        "status": item.status,
                        "return_to_work_date": item.return_to_work_date.isoformat() if item.return_to_work_date else "",
                        "signed_at": item.signed_at.isoformat() if item.signed_at else "",
                    }
                    for item in recent_decisions
                ],
                "workload_summary": list(assessments.values("status").annotate(total=Count("id")).order_by("status")),
                "return_to_work_reviews": [
                    {
                        "id": str(report.id),
                        "food_handler": report.food_handler.full_name,
                        "clearance_status": report.clearance_status,
                        "earliest_return_date": report.earliest_return_date.isoformat() if report.earliest_return_date else "",
                        "created_at": report.created_at.isoformat(),
                    }
                    for report in return_to_work_reports.order_by("-created_at")[:8]
                ],
            },
        }

    @classmethod
    def doctor_pending_queue(cls, assessments, lab_tests):
        queue = []
        for assessment in assessments.order_by("created_at")[:100]:
            queue.extend(cls.doctor_assessment_pending_tasks(assessment))
        for lab_test in lab_tests.filter(status__in=[LabTestStatus.RESULT_UPLOADED, LabTestStatus.SUBMITTED_TO_DOCTOR]).order_by("submitted_to_doctor_at", "created_at")[:50]:
            queue.append(
                {
                    "assessment_id": str(lab_test.assessment_id),
                    "food_handler": lab_test.assessment.food_handler.full_name,
                    "queue_type": "lab_review",
                    "status": lab_test.status,
                    "created_at": lab_test.created_at.isoformat(),
                }
            )
        return queue[:50]

    @classmethod
    def doctor_assessment_pending_tasks(cls, assessment):
        tasks = []
        base = {
            "assessment_id": str(assessment.id),
            "food_handler": assessment.food_handler.full_name,
            "status": assessment.status,
            "created_at": assessment.created_at.isoformat(),
        }
        if assessment.declaration_status == StepStatus.SUBMITTED:
            tasks.append({**base, "queue_type": "declaration_review"})
        if assessment.physical_exam_status == StepStatus.PENDING:
            tasks.append({**base, "queue_type": "physical_exam"})
        if assessment.lab_status == StepStatus.SUBMITTED:
            tasks.append({**base, "queue_type": "lab_review"})
        if assessment.vaccination_status != StepStatus.REVIEWED:
            tasks.append({**base, "queue_type": "vaccination_review"})
        if assessment.final_decision == FitnessDecision.PENDING:
            tasks.append({**base, "queue_type": "decision"})
        return tasks

    @classmethod
    def lab_dashboard(cls, user, facility_id=None):
        if user.role != UserRole.LAB_STAFF:
            raise PermissionDenied("You cannot access lab dashboards.")
        lab_tests = LabTest.objects.select_related("assessment", "assessment__food_handler", "assessment__facility")
        if facility_id:
            lab_tests = lab_tests.filter(assessment__facility_id=facility_id)
        elif user.organization_id:
            lab_tests = lab_tests.filter(assessment__facility__organization=user.organization)
        today = timezone.localdate()
        sample_pending = lab_tests.filter(status__in=[LabTestStatus.REQUESTED, LabTestStatus.SAMPLE_COLLECTION_PENDING])
        result_pending = lab_tests.filter(status__in=[LabTestStatus.SAMPLE_COLLECTED, LabTestStatus.IN_PROGRESS])
        submitted_today = lab_tests.filter(submitted_to_doctor_at__date=today)
        repeat_required = lab_tests.filter(Q(repeat_required=True) | Q(status=LabTestStatus.REPEAT_REQUIRED))
        return {
            "lab": {
                "user_id": str(user.id),
                "name": user.get_full_name() or user.username,
                "facility": user.organization.name if user.organization else "",
            },
            "filters": {"facility": str(facility_id) if facility_id else ""},
            "cards": {
                "lab_requests_pending": lab_tests.filter(status__in=[LabTestStatus.REQUESTED, LabTestStatus.SAMPLE_COLLECTION_PENDING, LabTestStatus.SAMPLE_COLLECTED, LabTestStatus.IN_PROGRESS]).count(),
                "samples_pending_collection": sample_pending.count(),
                "results_pending_upload": result_pending.count(),
                "results_submitted_today": submitted_today.count(),
                "repeat_tests_required": repeat_required.count(),
                "average_turnaround_time": cls.lab_average_turnaround_hours(lab_tests),
            },
            "sections": {
                "pending_sample_collection": cls.lab_queue_payload(sample_pending.order_by("requested_at", "created_at")[:12]),
                "pending_result_upload": cls.lab_queue_payload(result_pending.order_by("sample_collected_at", "created_at")[:12]),
                "recent_lab_results": cls.lab_queue_payload(lab_tests.filter(status__in=[LabTestStatus.RESULT_UPLOADED, LabTestStatus.SUBMITTED_TO_DOCTOR, LabTestStatus.REVIEWED]).order_by("-resulted_at", "-updated_at")[:12]),
                "turnaround_time_chart": list(
                    lab_tests.exclude(resulted_at__isnull=True)
                    .extra(select={"day": "date(resulted_at)"})
                    .values("day")
                    .annotate(total=Count("id"))
                    .order_by("day")[:30]
                ),
            },
        }

    @classmethod
    def lab_queue_payload(cls, lab_tests):
        return [
            {
                "id": str(test.id),
                "assessment_id": str(test.assessment_id),
                "food_handler": test.assessment.food_handler.full_name,
                "facility": test.assessment.facility.facility_name if test.assessment.facility else "",
                "test_type": test.test_type,
                "test_name": test.test_name,
                "status": test.status,
                "repeat_required": test.repeat_required,
                "requested_at": test.requested_at.isoformat() if test.requested_at else "",
                "sample_collected_at": test.sample_collected_at.isoformat() if test.sample_collected_at else "",
                "resulted_at": test.resulted_at.isoformat() if test.resulted_at else "",
            }
            for test in lab_tests
        ]

    @classmethod
    def lab_average_turnaround_hours(cls, lab_tests):
        total = 0
        count = 0
        for item in lab_tests.exclude(resulted_at__isnull=True).values("requested_at", "resulted_at"):
            requested_at = item["requested_at"]
            resulted_at = item["resulted_at"]
            if not requested_at or not resulted_at:
                continue
            total += (resulted_at - requested_at).total_seconds() / 3600
            count += 1
        return round(total / count, 2) if count else 0

    @classmethod
    def inspector_dashboard(cls, user):
        if user.role != UserRole.INSPECTOR:
            raise PermissionDenied("You cannot access inspector dashboards.")
        inspections = Inspection.objects.select_related("employer", "branch").filter(inspector=user)
        today = timezone.localdate()
        month_start = today.replace(day=1)
        due_today = inspections.filter(
            Q(scheduled_at__date=today) | Q(inspection_date__date=today),
            status__in=[InspectionStatus.ASSIGNED, InspectionStatus.ACCEPTED, InspectionStatus.SCHEDULED, InspectionStatus.IN_PROGRESS],
        )
        overdue = inspections.filter(
            Q(scheduled_at__date__lt=today) | Q(inspection_date__date__lt=today),
            status__in=[InspectionStatus.ASSIGNED, InspectionStatus.ACCEPTED, InspectionStatus.SCHEDULED, InspectionStatus.IN_PROGRESS, InspectionStatus.RETURNED_FOR_CORRECTION],
        )
        follow_ups_due = inspections.filter(
            status__in=[InspectionStatus.FOLLOW_UP_REQUIRED, InspectionStatus.FOLLOW_UP_SCHEDULED],
            inspection_date__date__lte=today,
        )
        open_statuses = [
            InspectionStatus.ASSIGNED,
            InspectionStatus.ACCEPTED,
            InspectionStatus.SCHEDULED,
            InspectionStatus.IN_PROGRESS,
            InspectionStatus.RETURNED_FOR_CORRECTION,
            InspectionStatus.NOTICE_ISSUED,
            InspectionStatus.CORRECTIVE_ACTION_PENDING,
            InspectionStatus.CORRECTIVE_ACTION_SUBMITTED,
            InspectionStatus.FOLLOW_UP_REQUIRED,
            InspectionStatus.FOLLOW_UP_SCHEDULED,
        ]
        task_list = inspections.filter(status__in=open_statuses).order_by("scheduled_at", "inspection_date", "-priority", "-created_at")[:25]
        return {
            "inspector": {
                "id": str(user.id),
                "name": user.get_full_name() or user.username,
                "state": user.state.name if user.state else "",
            },
            "cards": {
                "assigned_inspections": inspections.count(),
                "due_today": due_today.count(),
                "overdue": overdue.count(),
                "in_progress": inspections.filter(status=InspectionStatus.IN_PROGRESS).count(),
                "submitted": inspections.filter(status=InspectionStatus.SUBMITTED).count(),
                "notices_issued": inspections.filter(Q(status=InspectionStatus.NOTICE_ISSUED) | ~Q(enforcement_action=EnforcementAction.NONE)).count(),
                "corrective_actions_pending": inspections.filter(status=InspectionStatus.CORRECTIVE_ACTION_PENDING).count(),
                "follow_ups_due": follow_ups_due.count(),
                "high_priority": inspections.filter(priority__in=[InspectionPriority.HIGH, InspectionPriority.CRITICAL]).exclude(status__in=[InspectionStatus.CLOSED, InspectionStatus.CANCELLED]).count(),
                "closed_this_month": inspections.filter(status=InspectionStatus.CLOSED, closed_at__date__gte=month_start).count(),
            },
            "sections": {
                "task_list": [
                    {
                        "id": str(item.id),
                        "reference": item.reference,
                        "inspection_type": item.inspection_type,
                        "priority": item.priority,
                        "status": item.status,
                        "employer": item.employer.business_name,
                        "branch": item.branch.name if item.branch else "",
                        "inspection_date": item.inspection_date.isoformat() if item.inspection_date else "",
                        "scheduled_at": item.scheduled_at.isoformat() if item.scheduled_at else "",
                        "enforcement_action": item.enforcement_action,
                    }
                    for item in task_list
                ],
                "performance_summary": {
                    "open": inspections.filter(status__in=open_statuses).count(),
                    "closed": inspections.filter(status=InspectionStatus.CLOSED).count(),
                    "submitted": inspections.filter(status=InspectionStatus.SUBMITTED).count(),
                    "escalated": inspections.filter(status=InspectionStatus.ESCALATED).count(),
                    "average_compliance_score": decimal_string(inspections.exclude(compliance_score__isnull=True).aggregate(score=Avg("compliance_score"))["score"]),
                },
                "status_breakdown": list(inspections.values("status").annotate(total=Count("id")).order_by("status")),
                "priority_breakdown": list(inspections.values("priority").annotate(total=Count("id")).order_by("priority")),
            },
        }

    @classmethod
    def admin_dashboard(cls, user):
        if user.role != UserRole.SUPER_ADMIN:
            raise PermissionDenied("Only super admins can access the platform dashboard.")
        recent_cutoff = timezone.now() - timezone.timedelta(days=7)
        failed_reports = GeneratedReport.objects.filter(status=GeneratedReportStatus.FAILED)
        failed_payments = PaymentTransaction.objects.filter(status=PaymentStatus.FAILED)
        failed_certificate_requests = CertificateRequest.objects.filter(status=CertificateRequestStatus.REJECTED)
        recent_api_errors = DataQualityIssue.objects.filter(
            severity__in=[DataQualityIssueSeverity.HIGH, DataQualityIssueSeverity.CRITICAL],
            created_at__gte=recent_cutoff,
        )
        return {
            "cards": {
                "total_users": User.objects.count(),
                "active_organizations": Organization.objects.filter(status=OrganizationStatus.ACTIVE).count(),
                "active_employers": Employer.objects.count(),
                "active_facilities": MedicalFacility.objects.filter(accreditation_status=AccreditationStatus.APPROVED).count(),
                "active_state_ministry_accounts": User.objects.filter(role=UserRole.STATE_ADMIN, status=UserStatus.ACTIVE).count(),
                "active_federal_users": User.objects.filter(role=UserRole.FEDERAL_ADMIN, status=UserStatus.ACTIVE).count(),
                "api_errors": recent_api_errors.count(),
                "failed_payments": failed_payments.count(),
                "failed_certificate_generation": failed_certificate_requests.count(),
                "failed_report_jobs": failed_reports.count(),
                "background_job_health": "attention_required" if failed_reports.filter(created_at__gte=recent_cutoff).exists() else "healthy",
                "storage_usage": cls.storage_usage_summary(),
            },
            "charts": {
                "users_by_role": list(User.objects.values("role").annotate(total=Count("id")).order_by("role")),
                "organizations_by_type": list(Organization.objects.values("organization_type").annotate(total=Count("id")).order_by("organization_type")),
                "payments_by_status": list(PaymentTransaction.objects.values("status").annotate(total=Count("id"), amount=Sum("amount")).order_by("status")),
                "reports_by_status": list(GeneratedReport.objects.values("status").annotate(total=Count("id")).order_by("status")),
            },
            "sections": {
                "system_health": [
                    {"name": "Background jobs", "status": "attention_required" if failed_reports.filter(created_at__gte=recent_cutoff).exists() else "healthy", "count": failed_reports.count()},
                    {"name": "Payments", "status": "attention_required" if failed_payments.exists() else "healthy", "count": failed_payments.count()},
                    {"name": "Certificate generation", "status": "attention_required" if failed_certificate_requests.exists() else "healthy", "count": failed_certificate_requests.count()},
                    {"name": "Recent data quality alerts", "status": "attention_required" if recent_api_errors.exists() else "healthy", "count": recent_api_errors.count()},
                ],
                "recent_failed_payments": [
                    {
                        "id": str(payment.id),
                        "internal_reference": payment.internal_reference,
                        "payer_type": payment.payer_type,
                        "amount": str(payment.amount),
                        "currency": payment.currency,
                        "created_at": payment.created_at.isoformat(),
                    }
                    for payment in failed_payments.order_by("-created_at")[:8]
                ],
                "recent_failed_reports": [
                    {
                        "id": str(report.id),
                        "report_type": report.report_type,
                        "title": report.title,
                        "error_message": report.error_message,
                        "created_at": report.created_at.isoformat(),
                    }
                    for report in failed_reports.order_by("-created_at")[:8]
                ],
            },
        }

    @classmethod
    def storage_usage_summary(cls):
        media_root = Path(settings.MEDIA_ROOT)
        total_bytes = 0
        file_count = 0
        if media_root.exists():
            for path in media_root.rglob("*"):
                if path.is_file():
                    file_count += 1
                    total_bytes += path.stat().st_size
        return {
            "bytes": total_bytes,
            "megabytes": round(total_bytes / (1024 * 1024), 2),
            "files": file_count,
        }

    @classmethod
    def employer_dashboard(cls, user, employer_id=None, branch_id=None):
        employer = cls.employer_for_user(user, employer_id)
        if not employer:
            return {"employer": None, "cards": {}}
        handlers = FoodHandlerProfile.objects.filter(employer=employer)
        branch = None
        if user.role == UserRole.EMPLOYER and user.unit_restricted and user.unit_id:
            branch = user.unit
            handlers = handlers.filter(business_branch=user.unit)
        elif branch_id:
            handlers = handlers.filter(business_branch_id=branch_id)
            branch = handlers.first().business_branch if handlers.exists() else None
        elif user.role == UserRole.EMPLOYER and user.unit_id:
            branch = user.unit
            handlers = handlers.filter(business_branch=user.unit)
        total = handlers.count()
        compliance = ComplianceStatusService.handler_queryset_summary(handlers)
        typhoid_valid = handlers.filter(vaccinations__vaccine_type=VaccineType.TYPHOID, vaccinations__status=VaccinationStatus.VALID).distinct().count()
        typhoid_expired = handlers.filter(vaccinations__vaccine_type=VaccineType.TYPHOID, vaccinations__status=VaccinationStatus.EXPIRED).distinct().count()
        hep_a_dose_1 = handlers.filter(vaccinations__vaccine_type=VaccineType.HEPATITIS_A, vaccinations__dose_number=1).distinct().count()
        hep_a_dose_2_pending = handlers.filter(vaccinations__vaccine_type=VaccineType.HEPATITIS_A, vaccinations__status=VaccinationStatus.SECOND_DOSE_DUE).distinct().count()
        return {
            "employer": {"id": str(employer.id), "business_name": employer.business_name},
            "branch": {"id": str(branch.id), "name": branch.name} if branch else None,
            "cards": {
                "total_food_handlers": total,
                "valid_certificates": compliance["valid_certificates"],
                "expired_certificates": compliance["expired_certificates"],
                "expiring_soon": compliance["expiring_soon"],
                "not_certified": compliance["not_certified"],
                "temporarily_not_fit": compliance["temporarily_not_fit"],
                "cleared_to_return": IllnessReport.objects.filter(employer=employer, food_handler__in=handlers, clearance_status="cleared").count(),
                "typhoid_vaccination_valid": typhoid_valid,
                "typhoid_vaccination_expired": typhoid_expired,
                "hepatitis_a_dose_1_completed": hep_a_dose_1,
                "hepatitis_a_dose_2_pending": hep_a_dose_2_pending,
                "compliance_percentage": compliance["compliance_percentage"],
                "overall_compliance_status": compliance["overall_status"],
            },
        }

    @classmethod
    def facility_dashboard(
        cls,
        user,
        facility_id=None,
        department_id=None,
        date_from=None,
        date_to=None,
        doctor_id=None,
        lab_status="",
        assessment_status="",
        employer_category="",
    ):
        facility = cls.facility_for_user(user, facility_id)
        if not facility:
            return {"facility": None, "cards": {}}
        assessments = MedicalAssessment.objects.filter(facility=facility).select_related("doctor", "employer", "appointment")
        if user.unit_id:
            if getattr(user.unit, "unit_type", "") == "lab_department":
                assessments = assessments.filter(lab_tests__isnull=False).distinct()
        if department_id:
            # Department filtering is advisory until assessment records carry department IDs.
            assessments = assessments
        if date_from:
            assessments = assessments.filter(created_at__date__gte=date_from)
        if date_to:
            assessments = assessments.filter(created_at__date__lte=date_to)
        if doctor_id:
            assessments = assessments.filter(doctor_id=doctor_id)
        if lab_status:
            assessments = assessments.filter(lab_status=lab_status)
        if assessment_status:
            assessments = assessments.filter(status=assessment_status)
        if employer_category:
            assessments = assessments.filter(employer__establishment_category=employer_category)
        today = timezone.localdate()
        tomorrow = today + timezone.timedelta(days=1)
        expiry_countdown = (facility.accreditation_expiry_date - today).days if facility.accreditation_expiry_date else None
        pending_settlements = Settlement.objects.filter(facility=facility, settlement_status=SettlementStatus.PENDING)
        settled = Settlement.objects.filter(facility=facility, settlement_status=SettlementStatus.PAID)
        appointments = facility.appointments.all()
        if date_from:
            appointments = appointments.filter(appointment_date__date__gte=date_from)
        if date_to:
            appointments = appointments.filter(appointment_date__date__lte=date_to)
        certificate_requests = CertificateRequest.objects.filter(assessment__facility=facility)
        return {
            "facility": {"id": str(facility.id), "facility_name": facility.facility_name},
            "filters": {
                "date_from": str(date_from) if date_from else "",
                "date_to": str(date_to) if date_to else "",
                "department": str(department_id) if department_id else "",
                "doctor": str(doctor_id) if doctor_id else "",
                "lab_status": lab_status or "",
                "assessment_status": assessment_status or "",
                "employer_category": employer_category or "",
            },
            "cards": {
                "accreditation_status": facility.accreditation_status,
                "reaccreditation_countdown_days": expiry_countdown,
                "appointments_today": appointments.filter(appointment_date__date=today).count(),
                "pending_appointments": appointments.filter(status__in=["pending", "rescheduled"], appointment_date__date__gte=today).count(),
                "appointments_tomorrow": appointments.filter(appointment_date__date=tomorrow).count(),
                "assessments_in_progress": assessments.exclude(signed_at__isnull=False).count(),
                "assessments_conducted": assessments.count(),
                "lab_requests_pending": assessments.filter(lab_status__in=[StepStatus.PENDING, StepStatus.SUBMITTED]).count(),
                "lab_results_pending_doctor_review": assessments.filter(lab_status=StepStatus.SUBMITTED).count(),
                "vaccination_reviews_pending": assessments.exclude(vaccination_status=StepStatus.REVIEWED).count(),
                "doctor_decisions_pending": assessments.filter(final_decision=FitnessDecision.PENDING).count(),
                "submitted_to_state": certificate_requests.filter(status=CertificateRequestStatus.PENDING_VALIDATION).count(),
                "state_clarifications": certificate_requests.filter(status=CertificateRequestStatus.CORRECTION_REQUESTED).count(),
                "certificates_issued": Certificate.objects.filter(facility=facility).count(),
                "not_fit_reports": assessments.filter(final_decision__in=[FitnessDecision.NOT_FIT, FitnessDecision.TEMPORARILY_NOT_FIT]).count(),
                "pending_lab_results": assessments.exclude(lab_status=StepStatus.REVIEWED).filter(lab_tests__status__in=[LabTestStatus.REQUESTED, LabTestStatus.IN_PROGRESS, LabTestStatus.SAMPLE_COLLECTED]).distinct().count(),
                "pending_doctor_review": assessments.filter(Q(final_decision=FitnessDecision.PENDING) | Q(declaration_status=StepStatus.SUBMITTED)).count(),
                "average_turnaround_hours": cls.average_turnaround_hours(assessments),
                "pending_settlements": pending_settlements.count(),
                "settled_amount": decimal_string(settled.aggregate(total=Sum("facility_amount"))["total"]),
            },
            "charts": {
                "assessment_status": list(assessments.values("status").annotate(total=Count("id")).order_by("status")),
                "lab_status": list(assessments.values("lab_status").annotate(total=Count("id")).order_by("lab_status")),
                "decision_distribution": list(assessments.values("final_decision").annotate(total=Count("id")).order_by("final_decision")),
                "settlement_status": list(Settlement.objects.filter(facility=facility).values("settlement_status").annotate(total=Count("id")).order_by("settlement_status")),
            },
            "sections": {
                "queue_summary": [
                    {"name": "Appointments today", "count": appointments.filter(appointment_date__date=today).count(), "href": "/facility/appointments"},
                    {"name": "Lab pending", "count": assessments.exclude(lab_status=StepStatus.REVIEWED).count(), "href": "/facility/lab-tests"},
                    {"name": "State clarifications", "count": certificate_requests.filter(status=CertificateRequestStatus.CORRECTION_REQUESTED).count(), "href": "/facility/certificates"},
                    {"name": "Pending settlements", "count": pending_settlements.count(), "href": "/facility/settlements"},
                ],
                "recent_assessments": [
                    {
                        "id": str(item.id),
                        "food_handler": item.food_handler.full_name,
                        "status": item.status,
                        "decision": item.final_decision,
                        "doctor": item.doctor.get_full_name() if item.doctor else "",
                    }
                    for item in assessments.select_related("food_handler", "doctor").order_by("-created_at")[:8]
                ],
            },
        }

    @classmethod
    def average_turnaround_hours(cls, assessments):
        completed = assessments.exclude(signed_at__isnull=True)
        total = 0
        count = 0
        for assessment in completed.values("created_at", "signed_at"):
            if not assessment["signed_at"]:
                continue
            total += (assessment["signed_at"] - assessment["created_at"]).total_seconds() / 3600
            count += 1
        return round(total / count, 2) if count else 0

    @classmethod
    def state_dashboard(
        cls,
        user,
        state_id=None,
        lga_id=None,
        date_from=None,
        date_to=None,
        employer_category="",
        certificate_status="",
    ):
        if user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            raise PermissionDenied("You cannot access state dashboards.")
        state = user.state if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR} else None
        if not state and state_id:
            state = State.objects.filter(id=state_id).first()
        handlers = FoodHandlerProfile.objects.filter(state=state) if state else FoodHandlerProfile.objects.all()
        employers = Employer.objects.filter(state=state) if state else Employer.objects.all()
        facilities = MedicalFacility.objects.filter(state=state) if state else MedicalFacility.objects.all()
        certs = Certificate.objects.filter(issuing_state=state) if state else Certificate.objects.all()
        inspections = Inspection.objects.filter(employer__state=state) if state else Inspection.objects.all()
        illness = IllnessReport.objects.filter(food_handler__state=state) if state else IllnessReport.objects.all()
        certificate_requests = CertificateRequest.objects.select_related(
            "assessment",
            "assessment__food_handler",
            "assessment__facility",
            "assessment__employer",
        )
        facility_applications = FacilityAccreditationApplication.objects.select_related("facility")
        settlements = Settlement.objects.all()
        if state:
            certificate_requests = certificate_requests.filter(assessment__facility__state=state)
            facility_applications = facility_applications.filter(facility__state=state)
            settlements = settlements.filter(state=state)
        if user.unit_id and getattr(user.unit, "lga_id", None):
            lga_id = user.unit.lga_id
        if lga_id:
            handlers = handlers.filter(lga_id=lga_id)
            employers = employers.filter(lga_id=lga_id)
            facilities = facilities.filter(lga_id=lga_id)
            inspections = inspections.filter(employer__lga_id=lga_id)
            illness = illness.filter(food_handler__lga_id=lga_id)
            certificate_requests = certificate_requests.filter(assessment__food_handler__lga_id=lga_id)
            facility_applications = facility_applications.filter(facility__lga_id=lga_id)
        if employer_category:
            employers = employers.filter(establishment_category=employer_category)
            handlers = handlers.filter(employer__establishment_category=employer_category)
            certs = certs.filter(employer__establishment_category=employer_category)
            inspections = inspections.filter(employer__establishment_category=employer_category)
            illness = illness.filter(employer__establishment_category=employer_category)
            certificate_requests = certificate_requests.filter(assessment__employer__establishment_category=employer_category)
        if certificate_status:
            certs = certs.filter(status=certificate_status)
            handlers = handlers.filter(certificates__status=certificate_status).distinct()
        if date_from:
            certs = certs.filter(issue_date__gte=date_from)
            inspections = inspections.filter(inspection_date__date__gte=date_from)
            illness = illness.filter(created_at__date__gte=date_from)
            certificate_requests = certificate_requests.filter(created_at__date__gte=date_from)
            facility_applications = facility_applications.filter(created_at__date__gte=date_from)
            settlements = settlements.filter(created_at__date__gte=date_from)
        if date_to:
            certs = certs.filter(issue_date__lte=date_to)
            inspections = inspections.filter(inspection_date__date__lte=date_to)
            illness = illness.filter(created_at__date__lte=date_to)
            certificate_requests = certificate_requests.filter(created_at__date__lte=date_to)
            facility_applications = facility_applications.filter(created_at__date__lte=date_to)
            settlements = settlements.filter(created_at__date__lte=date_to)
        today = timezone.localdate()
        month_start = today.replace(day=1)
        pending_facility_applications = facility_applications.filter(
            application_status__in=[AccreditationStatus.SUBMITTED, AccreditationStatus.UNDER_REVIEW]
        )
        pending_certificate_requests = certificate_requests.filter(status=CertificateRequestStatus.PENDING_VALIDATION)
        active_illness_exclusions = illness.exclude(clearance_status__in=["cleared", "rejected"])
        enforcement_notices = inspections.exclude(enforcement_action="none")
        settled_total = settlements.filter(settlement_status=SettlementStatus.PAID).aggregate(total=Sum("state_amount"))["total"] or 0
        compliance_summary = ComplianceStatusService.handler_queryset_summary(handlers)
        active_certified_handlers = compliance_summary["certified_food_handlers"]
        vaccination_coverage = cls.vaccination_coverage_queryset(handlers)
        vaccination_coverage_rate = compliance_summary["vaccination_coverage_rate"]
        state_compliance_percentage = compliance_summary["compliance_percentage"]
        return_to_work_pending = compliance_summary["return_to_work_pending"]
        certificates_expiring_soon = certs.filter(status=CertificateStatus.ACTIVE, expiry_date__gte=today, expiry_date__lte=today + timezone.timedelta(days=30)).count()
        performance_rating = cls.state_performance_rating(
            compliance_percentage=state_compliance_percentage,
            vaccination_coverage_rate=vaccination_coverage_rate,
            inspections_count=inspections.count(),
            enforcement_count=enforcement_notices.count(),
            data_quality_score=cls.state_data_quality_score(state, handlers, employers, facilities),
        )
        return {
            "state": {"id": str(state.id), "name": state.name} if state else None,
            "filters": {
                "lga": str(lga_id) if lga_id else "",
                "date_from": str(date_from) if date_from else "",
                "date_to": str(date_to) if date_to else "",
                "employer_category": employer_category or "",
                "certificate_status": certificate_status or "",
            },
            "cards": {
                "registered_food_handlers": handlers.count(),
                "certified_food_handlers": active_certified_handlers,
                "food_businesses_registered": employers.count(),
                "approved_facilities": facilities.filter(accreditation_status=AccreditationStatus.APPROVED).count(),
                "pending_facility_applications": pending_facility_applications.count(),
                "pending_certificate_validations": pending_certificate_requests.count(),
                "suspended_facilities": facilities.filter(accreditation_status=AccreditationStatus.SUSPENDED).count(),
                "facilities_due_for_reaccreditation": facilities.filter(accreditation_expiry_date__lte=today + timezone.timedelta(days=60), accreditation_expiry_date__gte=today).count(),
                "certificates_issued_this_month": certs.filter(issue_date__gte=month_start).count(),
                "expired_certificates": certs.filter(expiry_date__lt=today).count(),
                "illness_reports": illness.count(),
                "active_illness_exclusions": active_illness_exclusions.count(),
                "inspections_conducted": inspections.count(),
                "enforcement_notices": enforcement_notices.count(),
                "state_revenue_collected": str(settled_total),
                "vaccination_coverage_rate": vaccination_coverage_rate,
                "state_compliance_percentage": state_compliance_percentage,
                "return_to_work_pending": return_to_work_pending,
                "certificates_expiring_soon": certificates_expiring_soon,
                "overall_compliance_status": compliance_summary["overall_compliance_status"],
                "performance_rating": performance_rating,
            },
            "charts": {
                "compliance_by_lga": list(handlers.values("lga__name").annotate(total=Count("id")).order_by("lga__name")),
                "lga_drill_down": cls.lga_drill_down(handlers),
                "inspection_outcomes": list(inspections.values("enforcement_action").annotate(total=Count("id")).order_by("enforcement_action")),
                "enforcement_notices_by_status": list(inspections.exclude(enforcement_action=EnforcementAction.NONE).values("status").annotate(total=Count("id")).order_by("status")),
                "certificate_status": list(certs.values("status").annotate(total=Count("id")).order_by("status")),
                "facility_accreditation_status": list(facilities.values("accreditation_status").annotate(total=Count("id")).order_by("accreditation_status")),
                "vaccination_coverage": vaccination_coverage,
                "illness_trends": cls.monthly_trend(illness, "created_at"),
                "assessment_volume_by_facility": list(
                    MedicalAssessment.objects.filter(facility__in=facilities)
                    .values("facility__facility_name")
                    .annotate(total=Count("id"))
                    .order_by("facility__facility_name")
                ),
                "revenue_trend": cls.monthly_revenue_trend(settlements) if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN} else [],
            },
            "sections": {
                "operational_queues": [
                    {
                        "name": "Facility accreditation",
                        "status": "pending",
                        "count": pending_facility_applications.count(),
                        "href": "/state/facilities/accreditation",
                    },
                    {
                        "name": "Certificate validation",
                        "status": "pending",
                        "count": pending_certificate_requests.count(),
                        "href": "/state/certificate-requests",
                    },
                    {
                        "name": "Illness exclusions",
                        "status": "active",
                        "count": active_illness_exclusions.count(),
                        "href": "/state/illness-reports",
                    },
                    {
                        "name": "Enforcement notices",
                        "status": "attention",
                        "count": enforcement_notices.count(),
                        "href": "/state/inspections",
                    },
                ],
                "recent_certificate_requests": [
                    {
                        "id": str(item.id),
                        "handler": item.assessment.food_handler.full_name if item.assessment and item.assessment.food_handler else "",
                        "facility": item.assessment.facility.facility_name if item.assessment and item.assessment.facility else "",
                        "status": item.status,
                        "created_at": item.created_at.isoformat(),
                    }
                    for item in pending_certificate_requests.order_by("-created_at")[:5]
                ],
                "recent_facility_applications": [
                    {
                        "id": str(item.id),
                        "facility": item.facility.facility_name,
                        "status": item.application_status,
                        "created_at": item.created_at.isoformat(),
                    }
                    for item in pending_facility_applications.order_by("-created_at")[:5]
                ],
            },
        }

    @classmethod
    def federal_dashboard(cls, user):
        if user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only federal users can access the national dashboard.")
        handlers = FoodHandlerProfile.objects.all()
        today = timezone.localdate()
        compliance_summary = ComplianceStatusService.get_national_compliance_summary()
        states = State.objects.order_by("name")
        state_rows = [cls.federal_state_dashboard_row(state, today) for state in states]
        states_with_active_implementation = sum(1 for row in state_rows if row["registered_handlers"] or row["registered_employers"] or row["approved_facilities"])
        states_with_overdue_reports = sum(1 for row in state_rows if row["latest_report_status"] in {"missing", "overdue"})
        national_vaccination_coverage = compliance_summary["vaccination_coverage_rate"]
        national_return_to_work_pending = compliance_summary["return_to_work_pending"]
        return {
            "cards": {
                "national_certification_coverage": compliance_summary["compliance_percentage"],
                "registered_food_handlers": compliance_summary["registered_food_handlers"],
                "certified_food_handlers": compliance_summary["certified_food_handlers"],
                "approved_facilities": compliance_summary["approved_facilities"],
                "illness_reports": IllnessReport.objects.count(),
                "inspections": compliance_summary["inspections_conducted"],
                "states_with_active_implementation": states_with_active_implementation,
                "states_with_overdue_reports": states_with_overdue_reports,
                "national_vaccination_coverage": national_vaccination_coverage,
                "national_inspection_count": compliance_summary["inspections_conducted"],
                "national_illness_reports": IllnessReport.objects.count(),
                "national_return_to_work_pending": national_return_to_work_pending,
                "overall_compliance_status": compliance_summary["overall_compliance_status"],
            },
            "charts": {
                "compliance_by_state": list(handlers.values("state__name").annotate(total=Count("id"), certified=Count("certificates", filter=Q(certificates__status=CertificateStatus.ACTIVE, certificates__expiry_date__gte=today))).order_by("state__name")),
                "state_comparison_table": state_rows,
                "certification_coverage_by_state": [
                    {"state_name": row["state_name"], "state_code": row["state_code"], "coverage": row["certification_coverage"]}
                    for row in state_rows
                ],
                "facility_accreditation_by_state": [
                    {"state_name": row["state_name"], "state_code": row["state_code"], "approved_facilities": row["approved_facilities"]}
                    for row in state_rows
                ],
                "vaccination_coverage_by_state": [
                    {"state_name": row["state_name"], "state_code": row["state_code"], "coverage": row["vaccination_coverage"]}
                    for row in state_rows
                ],
                "state_report_submission_status": cls.state_report_submission_status(state_rows),
                "approved_facilities_by_state": list(MedicalFacility.objects.filter(accreditation_status=AccreditationStatus.APPROVED).values("state__name").annotate(total=Count("id")).order_by("state__name")),
                "food_handler_categories": list(handlers.values("food_handler_category").annotate(total=Count("id")).order_by("food_handler_category")),
                "establishment_categories": list(Employer.objects.values("establishment_category").annotate(total=Count("id")).order_by("establishment_category")),
                "vaccination_coverage": cls.vaccination_coverage_queryset(handlers),
                "illness_trends": cls.monthly_trend(IllnessReport.objects.all(), "created_at"),
                "inspection_trends": cls.monthly_trend(Inspection.objects.all(), "inspection_date"),
            },
        }

    @classmethod
    def lga_drill_down(cls, handlers):
        rows = (
            handlers.values("lga_id", "lga__name")
            .annotate(
                registered_handlers=Count("id"),
                certified_handlers=Count(
                    "certificates",
                    filter=Q(certificates__status=CertificateStatus.ACTIVE, certificates__expiry_date__gte=timezone.localdate()),
                    distinct=True,
                ),
                typhoid_valid=Count(
                    "vaccinations",
                    filter=Q(vaccinations__vaccine_type=VaccineType.TYPHOID, vaccinations__status=VaccinationStatus.VALID),
                    distinct=True,
                ),
            )
            .order_by("lga__name")
        )
        return [
            {
                "lga_id": str(row["lga_id"]) if row["lga_id"] else "",
                "lga_name": row["lga__name"] or "Unassigned",
                "registered_handlers": row["registered_handlers"],
                "certified_handlers": row["certified_handlers"],
                "certification_coverage": percent(row["certified_handlers"], row["registered_handlers"]),
                "vaccination_coverage": percent(row["typhoid_valid"], row["registered_handlers"]),
            }
            for row in rows
        ]

    @classmethod
    def monthly_trend(cls, queryset, date_field):
        rows = (
            queryset.annotate(month=TruncMonth(date_field))
            .values("month")
            .annotate(total=Count("id"))
            .order_by("month")[:12]
        )
        return [
            {"month": row["month"].strftime("%Y-%m") if row["month"] else "", "total": row["total"]}
            for row in rows
        ]

    @classmethod
    def monthly_revenue_trend(cls, settlements):
        return [
            {"month": row["month"].strftime("%Y-%m") if row["month"] else "", "amount": str(row["amount"] or 0)}
            for row in settlements.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(amount=Sum("state_amount"))
            .order_by("month")[:12]
        ]

    @classmethod
    def state_data_quality_score(cls, state, handlers, employers, facilities):
        latest_report = StateReport.objects.filter(state=state).order_by("-reporting_period_end", "-created_at").first() if state else None
        inputs = [
            handlers.exclude(lga__isnull=True).count() / handlers.count() if handlers.count() else 1,
            employers.exclude(lga__isnull=True).count() / employers.count() if employers.count() else 1,
            facilities.exclude(lga__isnull=True).count() / facilities.count() if facilities.count() else 1,
            1 if latest_report and latest_report.status in {StateReportStatus.SUBMITTED, StateReportStatus.ACCEPTED} else 0,
        ]
        return round((sum(inputs) / len(inputs)) * 100, 2)

    @classmethod
    def state_performance_rating(cls, *, compliance_percentage, vaccination_coverage_rate, inspections_count, enforcement_count, data_quality_score):
        compliance_percentage = float(compliance_percentage)
        vaccination_coverage_rate = float(vaccination_coverage_rate)
        data_quality_score = float(data_quality_score)
        inspection_score = 100 if inspections_count else 0
        enforcement_score = 100 if inspections_count and enforcement_count <= inspections_count else 75 if enforcement_count else 100
        score = round((compliance_percentage * 0.35) + (vaccination_coverage_rate * 0.25) + (data_quality_score * 0.25) + (inspection_score * 0.1) + (enforcement_score * 0.05), 2)
        if score >= 80:
            band = "strong"
        elif score >= 60:
            band = "moderate"
        else:
            band = "needs_attention"
        return {"score": score, "band": band}

    @classmethod
    def federal_state_dashboard_row(cls, state, today):
        handlers = FoodHandlerProfile.objects.filter(state=state)
        employers = Employer.objects.filter(state=state)
        facilities = MedicalFacility.objects.filter(state=state)
        inspections = Inspection.objects.filter(employer__state=state)
        illness = IllnessReport.objects.filter(food_handler__state=state)
        total_handlers = handlers.count()
        certified_handlers = handlers.filter(certificates__status=CertificateStatus.ACTIVE, certificates__expiry_date__gte=today).distinct().count()
        latest_report = StateReport.objects.filter(state=state).order_by("-reporting_period_end", "-created_at").first()
        latest_status = "missing"
        latest_period_end = ""
        if latest_report:
            latest_period_end = latest_report.reporting_period_end.isoformat()
            latest_status = latest_report.status
            if latest_report.status not in {StateReportStatus.SUBMITTED, StateReportStatus.ACCEPTED} and latest_report.reporting_period_end < today - timezone.timedelta(days=45):
                latest_status = "overdue"
        vaccination_coverage = cls.vaccination_coverage_queryset(handlers)["typhoid_valid_percentage"]
        data_quality_score = cls.state_data_quality_score(state, handlers, employers, facilities)
        return {
            "state_id": str(state.id),
            "state_name": state.name,
            "state_code": state.code,
            "registered_handlers": total_handlers,
            "certified_handlers": certified_handlers,
            "certification_coverage": percent(certified_handlers, total_handlers),
            "vaccination_coverage": vaccination_coverage,
            "registered_employers": employers.count(),
            "approved_facilities": facilities.filter(accreditation_status=AccreditationStatus.APPROVED).count(),
            "inspection_count": inspections.count(),
            "illness_reports": illness.count(),
            "return_to_work_pending": illness.filter(clearance_status__in=["pending", "under_review", "clearance_required"]).count(),
            "latest_report_status": latest_status,
            "latest_report_period_end": latest_period_end,
            "data_quality_score": data_quality_score,
        }

    @classmethod
    def state_report_submission_status(cls, state_rows):
        counts = {}
        for row in state_rows:
            counts[row["latest_report_status"]] = counts.get(row["latest_report_status"], 0) + 1
        return [{"status": status, "total": total} for status, total in sorted(counts.items())]

    @classmethod
    def vaccination_coverage_queryset(cls, handlers):
        total = handlers.count()
        typhoid = handlers.filter(vaccinations__vaccine_type=VaccineType.TYPHOID, vaccinations__status=VaccinationStatus.VALID).distinct().count()
        hepatitis = handlers.filter(vaccinations__vaccine_type=VaccineType.HEPATITIS_A, vaccinations__status__in=[VaccinationStatus.VALID, VaccinationStatus.SECOND_DOSE_DUE]).distinct().count()
        return {
            "typhoid_valid_percentage": percent(typhoid, total),
            "hepatitis_a_recorded_percentage": percent(hepatitis, total),
        }


class ReportService:
    TYPE_TO_DASHBOARD = {
        ReportType.EMPLOYER_COMPLIANCE: DashboardService.employer_dashboard,
        ReportType.FACILITY_PERFORMANCE: DashboardService.facility_dashboard,
        ReportType.STATE_MONTHLY: DashboardService.state_dashboard,
        ReportType.NATIONAL: lambda user, **filters: DashboardService.federal_dashboard(user),
        ReportType.VACCINATION_COVERAGE: DashboardService.state_dashboard,
        ReportType.ILLNESS_TRENDS: DashboardService.state_dashboard,
        ReportType.INSPECTION_OUTCOMES: DashboardService.state_dashboard,
    }

    @classmethod
    def build_summary(cls, *, report_type, user, filters):
        builder = cls.TYPE_TO_DASHBOARD.get(report_type)
        if not builder:
            raise PermissionDenied("Unsupported report type.")
        if report_type == ReportType.EMPLOYER_COMPLIANCE:
            return builder(user, employer_id=filters.get("employer"), branch_id=filters.get("branch"))
        if report_type == ReportType.FACILITY_PERFORMANCE:
            return builder(
                user,
                facility_id=filters.get("facility"),
                department_id=filters.get("department"),
                date_from=filters.get("date_from"),
                date_to=filters.get("date_to"),
                doctor_id=filters.get("doctor"),
                lab_status=filters.get("lab_status", ""),
                assessment_status=filters.get("assessment_status", ""),
                employer_category=filters.get("employer_category", ""),
            )
        if report_type in {ReportType.STATE_MONTHLY, ReportType.VACCINATION_COVERAGE, ReportType.ILLNESS_TRENDS, ReportType.INSPECTION_OUTCOMES}:
            return builder(user, state_id=filters.get("state"), lga_id=filters.get("lga"))
        return builder(user)

    @classmethod
    def generate(cls, *, report_type, user, file_format=ReportFormat.JSON, filters=None, schedule=None):
        filters = filters or {}
        summary = cls.build_summary(report_type=report_type, user=user, filters=filters)
        report = GeneratedReport.objects.create(
            title=f"{ReportType(report_type).label} - {timezone.localdate().isoformat()}",
            report_type=report_type,
            organization=getattr(user, "organization", None),
            state=getattr(user, "state", None),
            reporting_period_start=filters.get("date_from"),
            reporting_period_end=filters.get("date_to"),
            file_format=file_format,
            filters=filters,
            summary=summary,
            data_snapshot=summary,
            generated_by=user,
            schedule=schedule,
            status=GeneratedReportStatus.GENERATED,
        )
        if file_format == ReportFormat.CSV:
            report.file_url = cls.write_csv(report)
        elif file_format == ReportFormat.PDF:
            report.file_url = cls.write_pdf(report)
        elif file_format == ReportFormat.EXCEL:
            report.file_url = cls.write_excel(report)
        report.save(update_fields=["file_url", "updated_at"])
        return report

    @classmethod
    def submit_to_federal(cls, *, report, actor):
        if actor.role != UserRole.STATE_ADMIN:
            raise PermissionDenied("Only state users can submit reports to federal.")
        if report.generated_by_id != actor.id and report.state_id != actor.state_id:
            raise PermissionDenied("You cannot submit this report.")
        if report.report_type not in {ReportType.STATE_MONTHLY, ReportType.VACCINATION_COVERAGE, ReportType.ILLNESS_TRENDS, ReportType.INSPECTION_OUTCOMES}:
            raise PermissionDenied("Only state regulatory reports can be submitted to federal.")
        if report.status not in {GeneratedReportStatus.GENERATED, GeneratedReportStatus.RETURNED_FOR_CORRECTION}:
            raise PermissionDenied("Only generated or returned reports can be submitted.")
        report.status = GeneratedReportStatus.SUBMITTED
        report.submitted_to_federal_at = timezone.now()
        report.review_status = ""
        report.review_comment = ""
        report.save(update_fields=["status", "submitted_to_federal_at", "review_status", "review_comment", "updated_at"])
        return report

    @classmethod
    def archive(cls, *, report, actor):
        if actor.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("You cannot archive reports.")
        if actor.role == UserRole.STATE_ADMIN and report.state_id != actor.state_id:
            raise PermissionDenied("State users can only archive reports from their state.")
        report.status = GeneratedReportStatus.ARCHIVED
        report.save(update_fields=["status", "updated_at"])
        return report

    @classmethod
    def regenerate(cls, *, report, actor):
        if actor.role == UserRole.STATE_ADMIN and report.state_id != actor.state_id:
            raise PermissionDenied("State users can only regenerate reports from their state.")
        return cls.generate(
            report_type=report.report_type,
            user=actor,
            file_format=report.file_format,
            filters=report.filters,
            schedule=report.schedule,
        )

    @classmethod
    def accept_federal_report(cls, *, report, actor, comment=""):
        cls.ensure_federal_reviewer(actor)
        cls.ensure_submitted_state_report(report)
        report.status = GeneratedReportStatus.ACCEPTED
        report.review_status = GeneratedReportStatus.ACCEPTED
        report.review_comment = comment
        report.reviewed_by = actor
        report.reviewed_at = timezone.now()
        report.save(update_fields=["status", "review_status", "review_comment", "reviewed_by", "reviewed_at", "updated_at"])
        return report

    @classmethod
    def return_for_correction(cls, *, report, actor, comment=""):
        cls.ensure_federal_reviewer(actor)
        cls.ensure_submitted_state_report(report)
        report.status = GeneratedReportStatus.RETURNED_FOR_CORRECTION
        report.review_status = GeneratedReportStatus.RETURNED_FOR_CORRECTION
        report.review_comment = comment
        report.reviewed_by = actor
        report.reviewed_at = timezone.now()
        report.save(update_fields=["status", "review_status", "review_comment", "reviewed_by", "reviewed_at", "updated_at"])
        return report

    @classmethod
    def escalate_federal_report(cls, *, report, actor, comment=""):
        cls.ensure_federal_reviewer(actor)
        cls.ensure_submitted_state_report(report)
        report.review_status = "escalated"
        report.review_comment = comment
        report.reviewed_by = actor
        report.reviewed_at = timezone.now()
        report.save(update_fields=["review_status", "review_comment", "reviewed_by", "reviewed_at", "updated_at"])
        return report

    @classmethod
    def ensure_federal_reviewer(cls, actor):
        if actor.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only federal users can review submitted state reports.")

    @classmethod
    def ensure_submitted_state_report(cls, report):
        if report.state_id is None:
            raise PermissionDenied("Only state reports can be reviewed.")
        if report.status != GeneratedReportStatus.SUBMITTED:
            raise PermissionDenied("Only submitted reports can be reviewed.")

    @classmethod
    def write_csv(cls, report):
        relative_path = f"reports/{report.report_type}-{report.id}.csv"
        output_path = Path(settings.MEDIA_ROOT) / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        buffer = StringIO()
        writer = csv.writer(buffer)
        cls.write_summary_to_csv(writer, report.summary)
        output_path.write_text(buffer.getvalue())
        return media_url(relative_path)

    @classmethod
    def write_summary_to_csv(cls, writer, summary):
        writer.writerow(["metric", "value"])
        for key, value in (summary.get("cards") or {}).items():
            writer.writerow([key, value])
        for section_name, rows in (summary.get("sections") or {}).items():
            writer.writerow([])
            writer.writerow([section_name])
            if not rows:
                continue
            headers = sorted({key for row in rows for key in row.keys()})
            writer.writerow(headers)
            for row in rows:
                writer.writerow([row.get(header, "") for header in headers])

    @classmethod
    def write_pdf(cls, report):
        relative_path = f"reports/{report.report_type}-{report.id}.pdf"
        output_path = Path(settings.MEDIA_ROOT) / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pdf = canvas.Canvas(str(output_path), pagesize=A4)
        pdf.setTitle(report.get_report_type_display())
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(72, 780, report.get_report_type_display())
        pdf.setFont("Helvetica", 10)
        y = 740
        for key, value in (report.summary.get("cards") or {}).items():
            pdf.drawString(72, y, f"{key}: {value}")
            y -= 20
            if y < 72:
                pdf.showPage()
                y = 780
        for section_name, rows in (report.summary.get("sections") or {}).items():
            y -= 10
            if y < 96:
                pdf.showPage()
                y = 780
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(72, y, section_name.replace("_", " ").title())
            y -= 18
            pdf.setFont("Helvetica", 9)
            for row in rows[:25]:
                text = " | ".join(f"{key}: {value}" for key, value in row.items() if value not in ("", None))
                pdf.drawString(72, y, text[:110])
                y -= 16
                if y < 72:
                    pdf.showPage()
                    y = 780
        pdf.save()
        return media_url(relative_path)

    @classmethod
    def write_excel(cls, report):
        relative_path = f"reports/{report.report_type}-{report.id}.xls"
        output_path = Path(settings.MEDIA_ROOT) / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        buffer = StringIO()
        writer = csv.writer(buffer, delimiter="\t")
        cls.write_summary_to_csv(writer, report.summary)
        output_path.write_text(buffer.getvalue())
        return media_url(relative_path)


class EmployerReportService:
    @classmethod
    def normalized_format(cls, value):
        if value == "xlsx":
            return ReportFormat.EXCEL
        return value or ReportFormat.JSON

    @classmethod
    def scoped_handlers(cls, *, employer, actor, filters):
        handlers = FoodHandlerProfile.objects.select_related("business_branch", "state", "lga").filter(employer=employer)
        if actor.role == UserRole.EMPLOYER and actor.unit_restricted and actor.unit_id:
            handlers = handlers.filter(business_branch=actor.unit)
        elif filters.get("branch"):
            handlers = handlers.filter(business_branch_id=filters["branch"])
        if filters.get("state"):
            handlers = handlers.filter(state_id=filters["state"])
        if filters.get("lga"):
            handlers = handlers.filter(lga_id=filters["lga"])
        if filters.get("category"):
            handlers = handlers.filter(food_handler_category=filters["category"])
        if filters.get("fitness_status"):
            handlers = handlers.filter(current_status=filters["fitness_status"])
        return handlers

    @classmethod
    def base_payload(cls, *, employer, actor, filters):
        branch = None
        if actor.role == UserRole.EMPLOYER and actor.unit_restricted and actor.unit_id:
            branch = actor.unit
        return {
            "employer": {"id": str(employer.id), "business_name": employer.business_name},
            "branch": {"id": str(branch.id), "name": branch.name} if branch else None,
            "filters": {key: str(value) for key, value in filters.items() if value not in ("", None)},
            "generated_at": timezone.now().isoformat(),
        }

    @classmethod
    def compliance_summary(cls, *, employer, actor, filters):
        handlers = cls.scoped_handlers(employer=employer, actor=actor, filters=filters)
        today = timezone.localdate()
        total = handlers.count()
        certified = handlers.filter(certificates__status=CertificateStatus.ACTIVE, certificates__expiry_date__gte=today).distinct().count()
        expired = handlers.filter(certificates__expiry_date__lt=today).distinct().count()
        typhoid_valid = handlers.filter(vaccinations__vaccine_type=VaccineType.TYPHOID, vaccinations__status=VaccinationStatus.VALID).distinct().count()
        hepatitis_recorded = handlers.filter(vaccinations__vaccine_type=VaccineType.HEPATITIS_A).distinct().count()
        open_inspections = Inspection.objects.filter(employer=employer).exclude(status="closed")
        if actor.role == UserRole.EMPLOYER and actor.unit_restricted and actor.unit_id:
            open_inspections = open_inspections.filter(branch=actor.unit)
        elif filters.get("branch"):
            open_inspections = open_inspections.filter(branch_id=filters["branch"])

        payload = cls.base_payload(employer=employer, actor=actor, filters=filters)
        payload.update({
            "cards": {
                "handler_count": total,
                "certified_count": certified,
                "expired_count": expired,
                "compliance_percentage": percent(certified, total),
                "vaccination_coverage_percentage": percent(typhoid_valid + hepatitis_recorded, total * 2),
                "typhoid_valid": typhoid_valid,
                "hepatitis_a_recorded": hepatitis_recorded,
                "open_inspections": open_inspections.count(),
                "excluded_handlers": handlers.filter(current_status__in=[FoodHandlerStatus.TEMPORARILY_EXCLUDED, FoodHandlerStatus.EXCLUDED]).count(),
            },
            "sections": {
                "branch_breakdown": list(
                    handlers.values("business_branch__name")
                    .annotate(total=Count("id"), certified=Count("certificates", filter=Q(certificates__status=CertificateStatus.ACTIVE, certificates__expiry_date__gte=today)))
                    .order_by("business_branch__name")
                ),
                "certificate_status": list(handlers.values("certificates__status").annotate(total=Count("certificates")).order_by("certificates__status")),
                "fitness_status": list(handlers.values("current_status").annotate(total=Count("id")).order_by("current_status")),
            },
        })
        return payload

    @classmethod
    def certificate_expiry_summary(cls, *, employer, actor, filters):
        handlers = cls.scoped_handlers(employer=employer, actor=actor, filters=filters)
        certificates = Certificate.objects.select_related("food_handler", "food_handler__business_branch", "facility", "issuing_state").filter(food_handler__in=handlers)
        if filters.get("certificate_status"):
            certificates = certificates.filter(status=filters["certificate_status"])
        if filters.get("date_from"):
            certificates = certificates.filter(expiry_date__gte=filters["date_from"])
        if filters.get("date_to"):
            certificates = certificates.filter(expiry_date__lte=filters["date_to"])
        today = timezone.localdate()
        payload = cls.base_payload(employer=employer, actor=actor, filters=filters)
        payload.update({
            "cards": {
                "total_certificates": certificates.count(),
                "active": certificates.filter(status=CertificateStatus.ACTIVE, expiry_date__gte=today).count(),
                "expired": certificates.filter(Q(status=CertificateStatus.EXPIRED) | Q(expiry_date__lt=today)).count(),
                "expiring_30d": certificates.filter(status=CertificateStatus.ACTIVE, expiry_date__gte=today, expiry_date__lte=today + timezone.timedelta(days=30)).count(),
                "expiring_7d": certificates.filter(status=CertificateStatus.ACTIVE, expiry_date__gte=today, expiry_date__lte=today + timezone.timedelta(days=7)).count(),
                "revoked_or_suspended": certificates.filter(status__in=[CertificateStatus.REVOKED, CertificateStatus.SUSPENDED]).count(),
            },
            "sections": {
                "certificates": [
                    {
                        "handler_name": cert.food_handler.full_name,
                        "branch_name": cert.food_handler.business_branch.name if cert.food_handler.business_branch else "",
                        "certificate_number": cert.certificate_number,
                        "facility_name": cert.facility.facility_name,
                        "issuing_state": cert.issuing_state.name,
                        "issue_date": cert.issue_date.isoformat(),
                        "expiry_date": cert.expiry_date.isoformat(),
                        "status": cert.effective_status,
                    }
                    for cert in certificates.order_by("expiry_date")[:500]
                ]
            },
        })
        return payload

    @classmethod
    def vaccination_summary(cls, *, employer, actor, filters):
        handlers = cls.scoped_handlers(employer=employer, actor=actor, filters=filters)
        vaccinations = VaccinationRecord.objects.select_related("food_handler", "food_handler__business_branch").filter(food_handler__in=handlers)
        if filters.get("vaccine_type"):
            vaccinations = vaccinations.filter(vaccine_type=filters["vaccine_type"])
        if filters.get("date_from"):
            vaccinations = vaccinations.filter(date_administered__gte=filters["date_from"])
        if filters.get("date_to"):
            vaccinations = vaccinations.filter(date_administered__lte=filters["date_to"])
        payload = cls.base_payload(employer=employer, actor=actor, filters=filters)
        payload.update({
            "cards": {
                "total_handlers": handlers.count(),
                "vaccination_records": vaccinations.count(),
                "typhoid_valid": handlers.filter(vaccinations__vaccine_type=VaccineType.TYPHOID, vaccinations__status=VaccinationStatus.VALID).distinct().count(),
                "typhoid_expired": handlers.filter(vaccinations__vaccine_type=VaccineType.TYPHOID, vaccinations__status=VaccinationStatus.EXPIRED).distinct().count(),
                "hepatitis_a_dose_1": handlers.filter(vaccinations__vaccine_type=VaccineType.HEPATITIS_A, vaccinations__dose_number=1).distinct().count(),
                "hepatitis_a_dose_2_pending": handlers.filter(vaccinations__vaccine_type=VaccineType.HEPATITIS_A, vaccinations__status=VaccinationStatus.SECOND_DOSE_DUE).distinct().count(),
                "missing_records": max(handlers.count() - handlers.filter(vaccinations__isnull=False).distinct().count(), 0),
            },
            "sections": {
                "vaccinations": [
                    {
                        "handler_name": record.food_handler.full_name,
                        "branch_name": record.food_handler.business_branch.name if record.food_handler.business_branch else "",
                        "vaccine_type": record.vaccine_type,
                        "dose_number": record.dose_number,
                        "date_administered": record.date_administered.isoformat() if record.date_administered else "",
                        "expiry_date": record.expiry_date.isoformat() if record.expiry_date else "",
                        "next_due": record.reminder_date.isoformat() if record.reminder_date else "",
                        "status": record.status,
                    }
                    for record in vaccinations.order_by("food_handler__full_name", "vaccine_type", "dose_number")[:500]
                ]
            },
        })
        return payload

    @classmethod
    def generate(cls, *, report_type, employer, actor, file_format, filters):
        builders = {
            ReportType.EMPLOYER_COMPLIANCE: cls.compliance_summary,
            ReportType.EMPLOYER_CERTIFICATES: cls.certificate_expiry_summary,
            ReportType.EMPLOYER_VACCINATIONS: cls.vaccination_summary,
        }
        summary = builders[report_type](employer=employer, actor=actor, filters=filters)
        report = GeneratedReport.objects.create(
            title=f"{ReportType(report_type).label} - {timezone.localdate().isoformat()}",
            report_type=report_type,
            organization=getattr(actor, "organization", None),
            state=getattr(actor, "state", None),
            reporting_period_start=summary.get("filters", {}).get("date_from") or filters.get("date_from"),
            reporting_period_end=summary.get("filters", {}).get("date_to") or filters.get("date_to"),
            file_format=cls.normalized_format(file_format),
            filters=summary.get("filters", {}),
            summary=summary,
            data_snapshot=summary,
            generated_by=actor,
            status=GeneratedReportStatus.GENERATED,
        )
        if report.file_format == ReportFormat.CSV:
            report.file_url = ReportService.write_csv(report)
        elif report.file_format == ReportFormat.PDF:
            report.file_url = ReportService.write_pdf(report)
        elif report.file_format == ReportFormat.EXCEL:
            report.file_url = ReportService.write_excel(report)
        report.save(update_fields=["file_url", "updated_at"])
        return report
