from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.forms.views import (
    EmployerAssignedFormsView,
    EmployerAssignedFormDetailView,
    EmployerAssignedFormResponseView,
    FacilityAssignedFormsView,
    FacilityAssignedFormDetailView,
    FacilityAssignedFormResponseView,
    FederalFormAssignmentDetailView,
    FederalFormAssignmentListCreateView,
    FederalFormAssignmentRecipientsView,
    FederalFormAssignmentResponseSummaryView,
    FederalFormAssignmentStateResponseMatrixView,
    FederalFormResponseDetailView,
    FederalFormResponseListView,
    FederalFormsExportCreateView,
    FederalFormsExportDownloadView,
    FederalFormsReportDetailView,
    FederalFormsReportListView,
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
    StateFederalTemplateAdoptView,
    StateFederalTemplateCloneView,
    StateFederalTemplateListView,
    StateFederalAssignmentDetailView,
    StateFederalAssignmentListView,
    StateFederalAssignmentResponseView,
    OfflineAssignmentPackageView,
    OfflineAssignmentsView,
    OfflineSyncStatusView,
    OfflineSyncView,
)

router = DefaultRouter()
router.register("forms/templates", FormTemplateViewSet, basename="form-templates")
router.register("forms/assignments", FormAssignmentViewSet, basename="form-assignments")
router.register("forms/responses", FormResponseViewSet, basename="form-responses")

federal_template_list = FormTemplateViewSet.as_view({"get": "list", "post": "create"})
federal_template_detail = FormTemplateViewSet.as_view({"get": "retrieve", "patch": "partial_update"})
federal_template_publish = FormTemplateViewSet.as_view({"post": "publish"})
federal_template_share_to_states = FormTemplateViewSet.as_view({"post": "share_to_states"})
federal_template_unshare_states = FormTemplateViewSet.as_view({"post": "unshare_states"})
federal_template_mark_standard = FormTemplateViewSet.as_view({"post": "mark_standard"})

urlpatterns = router.urls
urlpatterns += [
    path("forms/permissions/", FormsPermissionsView.as_view(), name="forms-permissions"),
    path("forms/reports/analytics/", FormsAnalyticsView.as_view(), name="forms-analytics"),
    path("forms/exports/responses/", FormResponseExportView.as_view(), name="forms-export-responses"),
    path("forms/exports/attachments/", FormAttachmentExportView.as_view(), name="forms-export-attachments"),
    path("federal/forms/templates/", federal_template_list, name="federal-form-templates"),
    path("federal/forms/templates/<uuid:pk>/", federal_template_detail, name="federal-form-template-detail"),
    path("federal/forms/templates/<uuid:pk>/publish/", federal_template_publish, name="federal-form-template-publish"),
    path("federal/forms/templates/<uuid:pk>/share-to-states/", federal_template_share_to_states, name="federal-form-template-share-to-states"),
    path("federal/forms/templates/<uuid:pk>/unshare-states/", federal_template_unshare_states, name="federal-form-template-unshare-states"),
    path("federal/forms/templates/<uuid:pk>/mark-standard/", federal_template_mark_standard, name="federal-form-template-mark-standard"),
    path("federal/forms/assignments/", FederalFormAssignmentListCreateView.as_view(), name="federal-form-assignments"),
    path("federal/forms/assignments/<uuid:assignment_id>/", FederalFormAssignmentDetailView.as_view(), name="federal-form-assignment-detail"),
    path("federal/forms/assignments/<uuid:assignment_id>/recipients/", FederalFormAssignmentRecipientsView.as_view(), name="federal-form-assignment-recipients"),
    path("federal/forms/assignments/<uuid:assignment_id>/response-summary/", FederalFormAssignmentResponseSummaryView.as_view(), name="federal-form-assignment-response-summary"),
    path("federal/forms/assignments/<uuid:assignment_id>/state-response-matrix/", FederalFormAssignmentStateResponseMatrixView.as_view(), name="federal-form-assignment-state-response-matrix"),
    path("federal/forms/responses/", FederalFormResponseListView.as_view(), name="federal-form-responses"),
    path("federal/forms/responses/<uuid:response_id>/", FederalFormResponseDetailView.as_view(), name="federal-form-response-detail"),
    path("federal/forms/reports/", FederalFormsReportListView.as_view(), name="federal-form-reports"),
    path("federal/forms/reports/<str:report_key>/", FederalFormsReportDetailView.as_view(), name="federal-form-report-detail"),
    path("federal/forms/exports/", FederalFormsExportCreateView.as_view(), name="federal-form-exports"),
    path("federal/forms/exports/<path:export_id>/download/", FederalFormsExportDownloadView.as_view(), name="federal-form-export-download"),
    path("state/forms/federal-assignments/", StateFederalAssignmentListView.as_view(), name="state-federal-form-assignments"),
    path("state/forms/federal-assignments/<uuid:assignment_id>/", StateFederalAssignmentDetailView.as_view(), name="state-federal-form-assignment-detail"),
    path("state/forms/federal-assignments/<uuid:assignment_id>/response/", StateFederalAssignmentResponseView.as_view(), name="state-federal-form-assignment-response"),
    path("state/forms/federal-templates/", StateFederalTemplateListView.as_view(), name="state-federal-form-templates"),
    path("state/forms/federal-templates/<uuid:template_id>/adopt/", StateFederalTemplateAdoptView.as_view(), name="state-federal-form-template-adopt"),
    path("state/forms/federal-templates/<uuid:template_id>/clone/", StateFederalTemplateCloneView.as_view(), name="state-federal-form-template-clone"),
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
