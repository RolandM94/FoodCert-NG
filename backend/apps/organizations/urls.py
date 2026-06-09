from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.organizations.views import OrganizationUnitViewSet, OrganizationViewSet

router = DefaultRouter()
router.register("organizations", OrganizationViewSet, basename="organizations")

unit_list = OrganizationUnitViewSet.as_view({"get": "list", "post": "create"})
unit_detail = OrganizationUnitViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})
unit_tree = OrganizationUnitViewSet.as_view({"get": "tree"})
unit_members = OrganizationUnitViewSet.as_view({"get": "members"})
unit_assign_user = OrganizationUnitViewSet.as_view({"post": "assign_user"})
unit_deactivate = OrganizationUnitViewSet.as_view({"post": "deactivate"})
unit_reactivate = OrganizationUnitViewSet.as_view({"post": "reactivate"})
unit_archive = OrganizationUnitViewSet.as_view({"post": "archive"})

urlpatterns = [
    path("organizations/<uuid:organization_id>/units/", unit_list, name="organization-units"),
    path("organizations/<uuid:organization_id>/units/tree/", unit_tree, name="organization-unit-tree"),
    path("organizations/<uuid:organization_id>/units/<uuid:pk>/", unit_detail, name="organization-unit-detail"),
    path("organizations/<uuid:organization_id>/units/<uuid:pk>/members/", unit_members, name="organization-unit-members"),
    path("organizations/<uuid:organization_id>/units/<uuid:pk>/assign-user/", unit_assign_user, name="organization-unit-assign-user"),
    path("organizations/<uuid:organization_id>/units/<uuid:pk>/deactivate/", unit_deactivate, name="organization-unit-deactivate"),
    path("organizations/<uuid:organization_id>/units/<uuid:pk>/reactivate/", unit_reactivate, name="organization-unit-reactivate"),
    path("organizations/<uuid:organization_id>/units/<uuid:pk>/archive/", unit_archive, name="organization-unit-archive"),
    *router.urls,
]
