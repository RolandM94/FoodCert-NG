import csv
from io import StringIO
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from rest_framework.exceptions import PermissionDenied

from apps.accounts.models import UserRole
from apps.assessments.models import FitnessDecision, MedicalAssessment, StepStatus
from apps.certificates.models import Certificate, CertificateRequest, CertificateRequestStatus, CertificateStatus
from apps.employers.models import Employer
from apps.facilities.models import AccreditationStatus, FacilityAccreditationApplication, MedicalFacility
from apps.food_handlers.models import FoodHandlerProfile, FoodHandlerStatus
from apps.illness.models import IllnessReport
from apps.inspections.models import Inspection
from apps.lab_tests.models import LabTestStatus
from apps.reports.models import GeneratedReport, GeneratedReportStatus, ReportFormat, ReportType
from apps.settlements.models import Settlement, SettlementStatus
from apps.vaccinations.models import VaccinationRecord, VaccinationStatus, VaccineType


def percent(numerator, denominator):
    if not denominator:
        return 0
    return round((numerator / denominator) * 100, 2)


def media_url(relative_path):
    return f"http://localhost:8000{settings.MEDIA_URL}{relative_path}"


class DashboardService:
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
        today = timezone.localdate()
        soon = today + timezone.timedelta(days=30)
        valid_certified = handlers.filter(certificates__status=CertificateStatus.ACTIVE, certificates__expiry_date__gte=today).distinct().count()
        expired = handlers.filter(certificates__expiry_date__lt=today).distinct().count()
        expiring_soon = handlers.filter(certificates__status=CertificateStatus.ACTIVE, certificates__expiry_date__range=(today, soon)).distinct().count()
        typhoid_valid = handlers.filter(vaccinations__vaccine_type=VaccineType.TYPHOID, vaccinations__status=VaccinationStatus.VALID).distinct().count()
        typhoid_expired = handlers.filter(vaccinations__vaccine_type=VaccineType.TYPHOID, vaccinations__status=VaccinationStatus.EXPIRED).distinct().count()
        hep_a_dose_1 = handlers.filter(vaccinations__vaccine_type=VaccineType.HEPATITIS_A, vaccinations__dose_number=1).distinct().count()
        hep_a_dose_2_pending = handlers.filter(vaccinations__vaccine_type=VaccineType.HEPATITIS_A, vaccinations__status=VaccinationStatus.SECOND_DOSE_DUE).distinct().count()
        return {
            "employer": {"id": str(employer.id), "business_name": employer.business_name},
            "branch": {"id": str(branch.id), "name": branch.name} if branch else None,
            "cards": {
                "total_food_handlers": total,
                "valid_certificates": valid_certified,
                "expired_certificates": expired,
                "expiring_soon": expiring_soon,
                "not_certified": max(total - valid_certified, 0),
                "temporarily_not_fit": handlers.filter(current_status__in=[FoodHandlerStatus.TEMPORARILY_NOT_FIT, FoodHandlerStatus.TEMPORARILY_EXCLUDED]).count(),
                "cleared_to_return": IllnessReport.objects.filter(employer=employer, food_handler__in=handlers, clearance_status="cleared").count(),
                "typhoid_vaccination_valid": typhoid_valid,
                "typhoid_vaccination_expired": typhoid_expired,
                "hepatitis_a_dose_1_completed": hep_a_dose_1,
                "hepatitis_a_dose_2_pending": hep_a_dose_2_pending,
                "compliance_percentage": percent(valid_certified, total),
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
                "settled_amount": str(settled.aggregate(total=Sum("facility_amount"))["total"] or 0),
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
            from apps.locations.models import State

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
                "certified_food_handlers": handlers.filter(certificates__status=CertificateStatus.ACTIVE, certificates__expiry_date__gte=today).distinct().count(),
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
            },
            "charts": {
                "compliance_by_lga": list(handlers.values("lga__name").annotate(total=Count("id")).order_by("lga__name")),
                "inspection_outcomes": list(inspections.values("enforcement_action").annotate(total=Count("id")).order_by("enforcement_action")),
                "certificate_status": list(certs.values("status").annotate(total=Count("id")).order_by("status")),
                "facility_accreditation_status": list(facilities.values("accreditation_status").annotate(total=Count("id")).order_by("accreditation_status")),
                "vaccination_coverage": cls.vaccination_coverage_queryset(handlers),
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
        total = handlers.count()
        today = timezone.localdate()
        valid = handlers.filter(certificates__status=CertificateStatus.ACTIVE, certificates__expiry_date__gte=today).distinct().count()
        return {
            "cards": {
                "national_certification_coverage": percent(valid, total),
                "registered_food_handlers": total,
                "certified_food_handlers": valid,
                "approved_facilities": MedicalFacility.objects.filter(accreditation_status=AccreditationStatus.APPROVED).count(),
                "illness_reports": IllnessReport.objects.count(),
                "inspections": Inspection.objects.count(),
            },
            "charts": {
                "compliance_by_state": list(handlers.values("state__name").annotate(total=Count("id"), certified=Count("certificates", filter=Q(certificates__status=CertificateStatus.ACTIVE, certificates__expiry_date__gte=today))).order_by("state__name")),
                "approved_facilities_by_state": list(MedicalFacility.objects.filter(accreditation_status=AccreditationStatus.APPROVED).values("state__name").annotate(total=Count("id")).order_by("state__name")),
                "food_handler_categories": list(handlers.values("food_handler_category").annotate(total=Count("id")).order_by("food_handler_category")),
                "establishment_categories": list(Employer.objects.values("establishment_category").annotate(total=Count("id")).order_by("establishment_category")),
                "vaccination_coverage": cls.vaccination_coverage_queryset(handlers),
                "illness_trends": list(IllnessReport.objects.extra(select={"month": "strftime('%%Y-%%m', created_at)"}).values("month").annotate(total=Count("id")).order_by("month")),
                "inspection_trends": list(Inspection.objects.extra(select={"month": "strftime('%%Y-%%m', inspection_date)"}).values("month").annotate(total=Count("id")).order_by("month")),
            },
        }

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
            report_type=report_type,
            file_format=file_format,
            filters=filters,
            summary=summary,
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
            report_type=report_type,
            file_format=cls.normalized_format(file_format),
            filters=summary.get("filters", {}),
            summary=summary,
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
