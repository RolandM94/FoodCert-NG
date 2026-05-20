from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.organizations.views import OrganizationUnitViewSet, OrganizationViewSet

router = DefaultRouter()
router.register("organizations", OrganizationViewSet, basename="organizations")

unit_list = OrganizationUnitViewSet.as_view({"get": "list", "post": "create"})
unit_detail = OrganizationUnitViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})

urlpatterns = [
    path("organizations/<uuid:organization_id>/units/", unit_list, name="organization-units"),
    path("organizations/<uuid:organization_id>/units/<uuid:pk>/", unit_detail, name="organization-unit-detail"),
    *router.urls,
]
