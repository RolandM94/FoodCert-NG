from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.settlements.views import FacilitySettlementDetailView, FacilitySettlementDisputeView, FacilitySettlementReportView, FacilitySettlementsView, SettlementBatchViewSet, SettlementViewSet


router = DefaultRouter()
router.register("settlements", SettlementViewSet, basename="settlements")
router.register("admin/settlement-batches", SettlementBatchViewSet, basename="settlement-batches")

urlpatterns = [
    path("facilities/<uuid:facility_id>/reports/settlements/", FacilitySettlementReportView.as_view(), name="facility-settlement-report"),
    path("facilities/<uuid:facility_id>/settlements/", FacilitySettlementsView.as_view(), name="facility-settlements"),
    path("facilities/<uuid:facility_id>/settlements/<uuid:settlement_id>/", FacilitySettlementDetailView.as_view(), name="facility-settlement-detail"),
    path("facilities/<uuid:facility_id>/settlements/<uuid:settlement_id>/dispute/", FacilitySettlementDisputeView.as_view(), name="facility-settlement-dispute"),
    *router.urls,
]
