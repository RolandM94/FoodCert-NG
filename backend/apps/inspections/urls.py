from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.inspections.views import (
    InspectionViewSet,
    inspector_flag_certificate,
    inspector_save_certificate_to_inspection,
    inspector_verify_certificate,
    inspector_verify_certificate_by_number,
)


router = DefaultRouter()
router.register("inspections", InspectionViewSet, basename="inspections")

urlpatterns = router.urls

urlpatterns += [
    path("inspector/certificates/verify/<str:verification_code>/", inspector_verify_certificate, name="inspector-certificate-verify"),
    path("inspector/certificates/verify-by-number/", inspector_verify_certificate_by_number, name="inspector-certificate-verify-by-number"),
    path("inspector/certificates/<uuid:certificate_id>/save-to-inspection/", inspector_save_certificate_to_inspection, name="inspector-certificate-save"),
    path("inspector/certificates/<uuid:certificate_id>/flag/", inspector_flag_certificate, name="inspector-certificate-flag"),
]
