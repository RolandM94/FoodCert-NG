from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.certificates.views import (
    CertificateRequestViewSet,
    CertificateViewSet,
    GenerateCertificateView,
    RequestCertificateView,
    public_verify_certificate,
)


router = DefaultRouter()
router.register("certificate-requests", CertificateRequestViewSet, basename="certificate-requests")
router.register("certificates", CertificateViewSet, basename="certificates")

urlpatterns = [
    path("assessments/<uuid:assessment_id>/request-certificate/", RequestCertificateView.as_view(), name="request-certificate"),
    path("certificates/generate/", GenerateCertificateView.as_view(), name="generate-certificate"),
    path("public/certificates/verify/<str:certificate_number>/", public_verify_certificate, name="public-certificate-verify"),
    *router.urls,
]
