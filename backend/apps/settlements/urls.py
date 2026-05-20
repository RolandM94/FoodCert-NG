from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.settlements.views import FacilitySettlementsView, SettlementViewSet


router = DefaultRouter()
router.register("settlements", SettlementViewSet, basename="settlements")

urlpatterns = [
    path("facilities/<uuid:facility_id>/settlements/", FacilitySettlementsView.as_view(), name="facility-settlements"),
    *router.urls,
]
