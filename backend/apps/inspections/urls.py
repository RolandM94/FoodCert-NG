from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.inspections.views import (
    EnforcementCaseViewSet,
    EnforcementNoticeViewSet,
    FederalEnforcementDashboardView,
    FederalEnforcementReportsView,
    InspectionChecklistItemViewSet,
    InspectionComplianceSummaryView,
    InspectionEmployerContextView,
    InspectionFoodHandlersView,
    InspectionViewSet,
    InspectorDashboardView,
    InspectorTasksView,
    StateEnforcementDashboardView,
    StateEnforcementReportsView,
    inspector_flag_certificate,
    inspector_save_certificate_to_inspection,
    inspector_verify_certificate,
    inspector_verify_certificate_by_number,
)


router = DefaultRouter()
router.register("inspections", InspectionViewSet, basename="inspections")
router.register("inspection-checklist-items", InspectionChecklistItemViewSet, basename="inspection-checklist-items")
router.register("enforcement-notices", EnforcementNoticeViewSet, basename="enforcement-notices")
router.register("enforcement-cases", EnforcementCaseViewSet, basename="enforcement-cases")

urlpatterns = router.urls

urlpatterns += [
    path("inspector/certificates/verify/<str:verification_code>/", inspector_verify_certificate, name="inspector-certificate-verify"),
    path("inspector/certificates/verify-by-number/", inspector_verify_certificate_by_number, name="inspector-certificate-verify-by-number"),
    path("inspector/certificates/<uuid:certificate_id>/save-to-inspection/", inspector_save_certificate_to_inspection, name="inspector-certificate-save"),
    path("inspector/certificates/<uuid:certificate_id>/flag/", inspector_flag_certificate, name="inspector-certificate-flag"),

    path("inspector/dashboard/", InspectorDashboardView.as_view(), name="inspector-dashboard"),
    path("inspector/tasks/", InspectorTasksView.as_view(), name="inspector-tasks"),

    path("inspections/<uuid:pk>/employer-context/", InspectionEmployerContextView.as_view(), name="inspection-employer-context"),
    path("inspections/<uuid:pk>/compliance-summary/", InspectionComplianceSummaryView.as_view(), name="inspection-compliance-summary"),
    path("inspections/<uuid:pk>/food-handlers/", InspectionFoodHandlersView.as_view(), name="inspection-food-handlers"),

    path("state/enforcement/dashboard/", StateEnforcementDashboardView.as_view(), name="state-enforcement-dashboard"),
    path("state/enforcement/reports/<str:report_type>/", StateEnforcementReportsView.as_view(), name="state-enforcement-reports"),

    path("federal/enforcement/dashboard/", FederalEnforcementDashboardView.as_view(), name="federal-enforcement-dashboard"),
    path("federal/enforcement/reports/", FederalEnforcementReportsView.as_view(), name="federal-enforcement-reports"),
]
