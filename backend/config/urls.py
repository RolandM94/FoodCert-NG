from django.contrib import admin
from django.urls import include, path
from drf_spectacular.utils import inline_serializer, extend_schema
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.certificates.views import public_verify_certificate


@extend_schema(
    methods=["GET"],
    responses=inline_serializer(
        name="HealthCheckResponse",
        fields={
            "status": serializers.CharField(),
            "service": serializers.CharField(),
        },
    ),
)
@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "ok", "service": "foodcert-ng-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/", include("apps.accounts.urls")),
    path("api/", include("apps.organizations.urls")),
    path("api/", include("apps.locations.urls")),
    path("api/", include("apps.policy.urls")),
    path("api/", include("apps.employers.urls")),
    path("api/", include("apps.facilities.urls")),
    path("api/", include("apps.food_handlers.urls")),
    path("api/", include("apps.nin_verification.urls")),
    path("api/", include("apps.payments.urls")),
    path("api/", include("apps.subscriptions.urls")),
    path("api/", include("apps.settlements.urls")),
    path("api/", include("apps.assessments.urls")),
    path("api/", include("apps.lab_tests.urls")),
    path("api/", include("apps.vaccinations.urls")),
    path("api/", include("apps.certificates.urls")),
    path("api/", include("apps.illness.urls")),
    path("api/", include("apps.inspections.urls")),
    path("api/", include("apps.reports.urls")),
    path("api/", include("apps.ministries.urls")),
    path("verify/<str:certificate_number>/", public_verify_certificate, name="public-certificate-verify-page"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
