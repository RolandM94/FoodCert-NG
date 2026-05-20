from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.reports.views import (
    EmployerComplianceReportView,
    EmployerDashboardView,
    FacilityDashboardView,
    FacilityPerformanceReportView,
    FederalDashboardView,
    GeneratedReportViewSet,
    IllnessTrendsReportView,
    InspectionOutcomesReportView,
    NationalReportView,
    ReportScheduleViewSet,
    StateDashboardView,
    StateMonthlyReportView,
    VaccinationCoverageReportView,
)


router = DefaultRouter()
router.register("reports/schedule", ReportScheduleViewSet, basename="report-schedule")
router.register("reports/generated", GeneratedReportViewSet, basename="generated-reports")

urlpatterns = [
    path("dashboard/employer/", EmployerDashboardView.as_view(), name="dashboard-employer"),
    path("dashboard/facility/", FacilityDashboardView.as_view(), name="dashboard-facility"),
    path("dashboard/state/", StateDashboardView.as_view(), name="dashboard-state"),
    path("dashboard/federal/", FederalDashboardView.as_view(), name="dashboard-federal"),
    path("reports/employer-compliance/", EmployerComplianceReportView.as_view(), name="report-employer-compliance"),
    path("reports/facility-performance/", FacilityPerformanceReportView.as_view(), name="report-facility-performance"),
    path("reports/state-monthly/", StateMonthlyReportView.as_view(), name="report-state-monthly"),
    path("reports/national/", NationalReportView.as_view(), name="report-national"),
    path("reports/vaccination-coverage/", VaccinationCoverageReportView.as_view(), name="report-vaccination-coverage"),
    path("reports/illness-trends/", IllnessTrendsReportView.as_view(), name="report-illness-trends"),
    path("reports/inspection-outcomes/", InspectionOutcomesReportView.as_view(), name="report-inspection-outcomes"),
    *router.urls,
]
