from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.certificates.views import (
    AccreditationCertificateViewSet,
    CertificateRequestViewSet,
    CertificateTemplateViewSet,
    CertificateViewSet,
    GenerateCertificateView,
    RequestCertificateView,
    public_report_suspicious_certificate,
    public_verify_certificate,
    public_verify_certificate_by_number,
)


router = DefaultRouter()
router.register("certificate-requests", CertificateRequestViewSet, basename="certificate-requests")
router.register("certificates", CertificateViewSet, basename="certificates")
router.register("accreditation-certificates", AccreditationCertificateViewSet, basename="accreditation-certificates")
router.register("certificate-templates", CertificateTemplateViewSet, basename="certificate-templates")

urlpatterns = [
    path("assessments/<uuid:assessment_id>/request-certificate/", RequestCertificateView.as_view(), name="request-certificate"),
    path("certificates/generate/", GenerateCertificateView.as_view(), name="generate-certificate"),
    path("public/certificates/verify/<str:certificate_number>/", public_verify_certificate, name="public-certificate-verify"),
    path("public/certificates/verify-by-number/", public_verify_certificate_by_number, name="public-certificate-verify-by-number"),
    path("public/certificates/report-suspicious/", public_report_suspicious_certificate, name="public-certificate-report-suspicious"),
    *router.urls,
]
