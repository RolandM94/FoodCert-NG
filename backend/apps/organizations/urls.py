from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.organizations.views import OrganizationUnitViewSet, OrganizationViewSet
from apps.organizations.views_membership import OrganizationMembershipViewSet
from apps.organizations.views_permissions import PermissionViewSet
from apps.organizations.views_roles import RoleViewSet
from apps.organizations.views_stakeholder import StakeholderContextView, StakeholderSummaryView

router = DefaultRouter()
router.register("organizations", OrganizationViewSet, basename="organizations")
router.register("roles", RoleViewSet, basename="roles")
router.register("permissions", PermissionViewSet, basename="permissions")

unit_list = OrganizationUnitViewSet.as_view({"get": "list", "post": "create"})
unit_detail = OrganizationUnitViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})
unit_tree = OrganizationUnitViewSet.as_view({"get": "tree"})
unit_members = OrganizationUnitViewSet.as_view({"get": "members"})
unit_assign_user = OrganizationUnitViewSet.as_view({"post": "assign_user"})
unit_deactivate = OrganizationUnitViewSet.as_view({"post": "deactivate"})
unit_reactivate = OrganizationUnitViewSet.as_view({"post": "reactivate"})
unit_archive = OrganizationUnitViewSet.as_view({"post": "archive"})
membership_list = OrganizationMembershipViewSet.as_view({"get": "list", "post": "create"})
membership_detail = OrganizationMembershipViewSet.as_view({"get": "retrieve", "patch": "partial_update"})
membership_suspend = OrganizationMembershipViewSet.as_view({"patch": "suspend"})
membership_reactivate = OrganizationMembershipViewSet.as_view({"patch": "reactivate"})
membership_remove = OrganizationMembershipViewSet.as_view({"patch": "remove"})
membership_change_role = OrganizationMembershipViewSet.as_view({"patch": "change_role"})
membership_change_unit = OrganizationMembershipViewSet.as_view({"patch": "change_unit"})
membership_toggle_unit_restriction = OrganizationMembershipViewSet.as_view({"patch": "toggle_unit_restriction"})
roles_by_organization_type = RoleViewSet.as_view({"get": "list"})

urlpatterns = [
    path("stakeholder-management/context/", StakeholderContextView.as_view(), name="stakeholder-context"),
    path("stakeholder-management/summary/", StakeholderSummaryView.as_view(), name="stakeholder-summary"),
    path("organization-types/<str:organization_type>/roles/", roles_by_organization_type, name="organization-type-roles"),
    path("organizations/<uuid:organization_id>/units/", unit_list, name="organization-units"),
    path("organizations/<uuid:organization_id>/units/tree/", unit_tree, name="organization-unit-tree"),
    path("organizations/<uuid:organization_id>/units/<uuid:pk>/", unit_detail, name="organization-unit-detail"),
    path("organizations/<uuid:organization_id>/units/<uuid:pk>/members/", unit_members, name="organization-unit-members"),
    path("organizations/<uuid:organization_id>/units/<uuid:pk>/assign-user/", unit_assign_user, name="organization-unit-assign-user"),
    path("organizations/<uuid:organization_id>/units/<uuid:pk>/deactivate/", unit_deactivate, name="organization-unit-deactivate"),
    path("organizations/<uuid:organization_id>/units/<uuid:pk>/reactivate/", unit_reactivate, name="organization-unit-reactivate"),
    path("organizations/<uuid:organization_id>/units/<uuid:pk>/archive/", unit_archive, name="organization-unit-archive"),
    path("organizations/<uuid:organization_id>/memberships/", membership_list, name="organization-memberships"),
    path("organizations/<uuid:organization_id>/memberships/<uuid:pk>/", membership_detail, name="organization-membership-detail"),
    path("organizations/<uuid:organization_id>/memberships/<uuid:pk>/suspend/", membership_suspend, name="organization-membership-suspend"),
    path("organizations/<uuid:organization_id>/memberships/<uuid:pk>/reactivate/", membership_reactivate, name="organization-membership-reactivate"),
    path("organizations/<uuid:organization_id>/memberships/<uuid:pk>/remove/", membership_remove, name="organization-membership-remove"),
    path("organizations/<uuid:organization_id>/memberships/<uuid:pk>/change-role/", membership_change_role, name="organization-membership-change-role"),
    path("organizations/<uuid:organization_id>/memberships/<uuid:pk>/change-unit/", membership_change_unit, name="organization-membership-change-unit"),
    path("organizations/<uuid:organization_id>/memberships/<uuid:pk>/toggle-unit-restriction/", membership_toggle_unit_restriction, name="organization-membership-toggle-unit-restriction"),
    *router.urls,
]
