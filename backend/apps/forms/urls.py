from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.forms.views import (
    EmployerAssignedFormsView,
    EmployerAssignedFormDetailView,
    EmployerAssignedFormResponseView,
    FacilityAssignedFormsView,
    FacilityAssignedFormDetailView,
    FacilityAssignedFormResponseView,
    FoodHandlerAssignedFormsView,
    FoodHandlerAssignedFormDetailView,
    FoodHandlerAssignedFormResponseView,
    FormAssignmentViewSet,
    FormAttachmentExportView,
    FormResponseExportView,
    FormResponseViewSet,
    FormTemplateViewSet,
    FormsAnalyticsView,
    FormsPermissionsView,
    OfflineAssignmentPackageView,
    OfflineAssignmentsView,
    OfflineSyncStatusView,
    OfflineSyncView,
)

router = DefaultRouter()
router.register("forms/templates", FormTemplateViewSet, basename="form-templates")
router.register("forms/assignments", FormAssignmentViewSet, basename="form-assignments")
router.register("forms/responses", FormResponseViewSet, basename="form-responses")

urlpatterns = router.urls
urlpatterns += [
    path("forms/permissions/", FormsPermissionsView.as_view(), name="forms-permissions"),
    path("forms/reports/analytics/", FormsAnalyticsView.as_view(), name="forms-analytics"),
    path("forms/exports/responses/", FormResponseExportView.as_view(), name="forms-export-responses"),
    path("forms/exports/attachments/", FormAttachmentExportView.as_view(), name="forms-export-attachments"),
    path("forms/offline/assignments/", OfflineAssignmentsView.as_view(), name="forms-offline-assignments"),
    path("forms/offline/assignments/<uuid:assignment_id>/package/", OfflineAssignmentPackageView.as_view(), name="forms-offline-assignment-package"),
    path("forms/offline/sync/", OfflineSyncView.as_view(), name="forms-offline-sync"),
    path("forms/offline/sync/<uuid:sync_job_id>/status/", OfflineSyncStatusView.as_view(), name="forms-offline-sync-status"),

    path("employer/assigned-forms/", EmployerAssignedFormsView.as_view(), name="employer-assigned-forms"),
    path("employer/assigned-forms/<uuid:assignment_id>/", EmployerAssignedFormDetailView.as_view(), name="employer-assigned-form-detail"),
    path("employer/assigned-forms/<uuid:assignment_id>/response/", EmployerAssignedFormResponseView.as_view(), name="employer-assigned-form-response"),

    path("facility/assigned-forms/", FacilityAssignedFormsView.as_view(), name="facility-assigned-forms"),
    path("facility/assigned-forms/<uuid:assignment_id>/", FacilityAssignedFormDetailView.as_view(), name="facility-assigned-form-detail"),
    path("facility/assigned-forms/<uuid:assignment_id>/response/", FacilityAssignedFormResponseView.as_view(), name="facility-assigned-form-response"),

    path("food-handler/assigned-forms/", FoodHandlerAssignedFormsView.as_view(), name="food-handler-assigned-forms"),
    path("food-handler/assigned-forms/<uuid:assignment_id>/", FoodHandlerAssignedFormDetailView.as_view(), name="food-handler-assigned-form-detail"),
    path("food-handler/assigned-forms/<uuid:assignment_id>/response/", FoodHandlerAssignedFormResponseView.as_view(), name="food-handler-assigned-form-response"),
]
