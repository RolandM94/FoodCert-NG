from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.reports.views import (
    AdminDashboardView,
    AnalyticsDatasetViewSet,
    KpiCardDefinitionViewSet,
    AnalyticsWidgetViewSet,
    AnalyticsWorksheetViewSet,
    DashboardAlertEventViewSet,
    DashboardAlertRuleViewSet,
    DashboardExportJobViewSet,
    AssessmentAnalyticsView,
    CertificateAnalyticsView,
    DashboardCanvasBlockViewSet,
    DashboardCanvasViewSet,
    DashboardTemplateViewSet,
    DashboardWidgetViewSet,
    DataQualityAnalyticsView,
    DataQualityIssueViewSet,
    DoctorDashboardView,
    EmployerComplianceReportView,
    EmployerAnalyticsView,
    EmployerDashboardView,
    EnforcementAnalyticsView,
    FacilityAnalyticsView,
    FacilityDashboardView,
    FacilityPerformanceReportView,
    FederalStateReportViewSet,
    FederalDashboardView,
    FoodHandlerDashboardView,
    GeneratedReportViewSet,
    IllnessTrendsReportView,
    IllnessAnalyticsView,
    InspectionOutcomesReportView,
    InspectionAnalyticsView,
    InspectorDashboardView,
    LabDashboardView,
    MECalculateView,
    MEDashboardView,
    MEIndicatorViewSet,
    MENationalSummaryView,
    MEStatePerformanceView,
    NationalReportView,
    PaymentAnalyticsView,
    PublishedDashboardViewSet,
    ReportScheduleViewSet,
    ReportTemplateViewSet,
    ScheduledReportViewSet,
    SettlementAnalyticsView,
    StateDashboardView,
    StateMonthlyReportView,
    VaccinationAnalyticsView,
    VaccinationCoverageReportView,
)


router = DefaultRouter()
router.register("report-templates", ReportTemplateViewSet, basename="report-templates")
router.register("m-and-e/indicators", MEIndicatorViewSet, basename="me-indicators")
router.register("reports/schedule", ReportScheduleViewSet, basename="report-schedule")
router.register("reports/generated", GeneratedReportViewSet, basename="generated-reports")
router.register("federal/state-reports", FederalStateReportViewSet, basename="federal-state-reports")
router.register("dashboard-widgets", DashboardWidgetViewSet, basename="dashboard-widgets")
router.register("analytics/datasets", AnalyticsDatasetViewSet, basename="analytics-datasets")
router.register("analytics/kpi-cards", KpiCardDefinitionViewSet, basename="kpi-cards")
router.register("analytics/worksheets", AnalyticsWorksheetViewSet, basename="analytics-worksheets")
router.register("analytics/widgets", AnalyticsWidgetViewSet, basename="analytics-widgets")
router.register("analytics/dashboard-alerts", DashboardAlertRuleViewSet, basename="analytics-dashboard-alerts")
router.register("analytics/dashboard-alert-events", DashboardAlertEventViewSet, basename="analytics-dashboard-alert-events")
router.register("analytics/dashboard-export-jobs", DashboardExportJobViewSet, basename="analytics-dashboard-export-jobs")
router.register("analytics/dashboard-canvases", DashboardCanvasViewSet, basename="analytics-dashboard-canvases")
router.register("analytics/dashboard-blocks", DashboardCanvasBlockViewSet, basename="analytics-dashboard-blocks")
router.register("analytics/published-dashboards", PublishedDashboardViewSet, basename="analytics-published-dashboards")
router.register("analytics/dashboard-templates", DashboardTemplateViewSet, basename="analytics-dashboard-templates")
router.register("data-quality/issues", DataQualityIssueViewSet, basename="data-quality-issues")
router.register("scheduled-reports", ScheduledReportViewSet, basename="scheduled-reports")

urlpatterns = [
    path("dashboard/food-handler/", FoodHandlerDashboardView.as_view(), name="dashboard-food-handler"),
    path("dashboard/doctor/", DoctorDashboardView.as_view(), name="dashboard-doctor"),
    path("dashboard/lab/", LabDashboardView.as_view(), name="dashboard-lab"),
    path("dashboard/inspector/", InspectorDashboardView.as_view(), name="dashboard-inspector"),
    path("dashboard/admin/", AdminDashboardView.as_view(), name="dashboard-admin"),
    path("dashboard/employer/", EmployerDashboardView.as_view(), name="dashboard-employer"),
    path("dashboard/facility/", FacilityDashboardView.as_view(), name="dashboard-facility"),
    path("dashboard/state/", StateDashboardView.as_view(), name="dashboard-state"),
    path("dashboard/federal/", FederalDashboardView.as_view(), name="dashboard-federal"),
    path("analytics/certificates/", CertificateAnalyticsView.as_view(), name="analytics-certificates"),
    path("analytics/assessments/", AssessmentAnalyticsView.as_view(), name="analytics-assessments"),
    path("analytics/vaccinations/", VaccinationAnalyticsView.as_view(), name="analytics-vaccinations"),
    path("analytics/facilities/", FacilityAnalyticsView.as_view(), name="analytics-facilities"),
    path("analytics/employers/", EmployerAnalyticsView.as_view(), name="analytics-employers"),
    path("analytics/inspections/", InspectionAnalyticsView.as_view(), name="analytics-inspections"),
    path("analytics/enforcement/", EnforcementAnalyticsView.as_view(), name="analytics-enforcement"),
    path("analytics/illness/", IllnessAnalyticsView.as_view(), name="analytics-illness"),
    path("analytics/payments/", PaymentAnalyticsView.as_view(), name="analytics-payments"),
    path("analytics/settlements/", SettlementAnalyticsView.as_view(), name="analytics-settlements"),
    path("analytics/data-quality/", DataQualityAnalyticsView.as_view(), name="analytics-data-quality"),
    path("reports/employer-compliance/", EmployerComplianceReportView.as_view(), name="report-employer-compliance"),
    path("reports/facility-performance/", FacilityPerformanceReportView.as_view(), name="report-facility-performance"),
    path("reports/state-monthly/", StateMonthlyReportView.as_view(), name="report-state-monthly"),
    path("reports/national/", NationalReportView.as_view(), name="report-national"),
    path("reports/vaccination-coverage/", VaccinationCoverageReportView.as_view(), name="report-vaccination-coverage"),
    path("reports/illness-trends/", IllnessTrendsReportView.as_view(), name="report-illness-trends"),
    path("reports/inspection-outcomes/", InspectionOutcomesReportView.as_view(), name="report-inspection-outcomes"),
    path("m-and-e/calculate/", MECalculateView.as_view(), name="me-calculate"),
    path("m-and-e/dashboard/", MEDashboardView.as_view(), name="me-dashboard"),
    path("m-and-e/state-performance/", MEStatePerformanceView.as_view(), name="me-state-performance"),
    path("m-and-e/national-summary/", MENationalSummaryView.as_view(), name="me-national-summary"),
    *router.urls,
]
