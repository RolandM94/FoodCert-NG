from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.accounts.models import UserRole
from apps.accounts.permissions import is_super_admin, is_federal_admin, is_state_admin
from apps.organizations.services_access import EffectiveAccessService


def can_manage_unit(actor, unit_or_org):
    from apps.organizations.models import Organization, OrganizationUnit

    if is_super_admin(actor):
        return True
    if is_federal_admin(actor):
        return True
    if isinstance(unit_or_org, OrganizationUnit):
        org = unit_or_org.organization
        if is_state_admin(actor):
            return org.state_id == actor.state_id
        return org.id == getattr(actor, "organization_id", None)
    if isinstance(unit_or_org, Organization):
        if is_state_admin(actor):
            return unit_or_org.state_id == actor.state_id
        return unit_or_org.id == getattr(actor, "organization_id", None)
    return False


class CanManageOrganizationUnit(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        return can_manage_unit(request.user, obj)


class HasStakeholderPermission(BasePermission):
    permission_code = None

    def has_permission(self, request, view):
        permission_code = self._get_permission_code(view)
        if not permission_code:
            return False
        organization = self._get_organization(view)
        result = EffectiveAccessService().check(request.user, permission_code, organization=organization)
        view.access_result = result
        return result.allowed

    def has_object_permission(self, request, view, obj):
        permission_code = self._get_permission_code(view)
        if not permission_code:
            return False
        result = EffectiveAccessService().check(request.user, permission_code, resource=obj)
        view.access_result = result
        return result.allowed

    def _get_permission_code(self, view):
        return getattr(view, "permission_code", None) or getattr(view, "stakeholder_permission_code", None) or self.permission_code

    def _get_organization(self, view):
        get_organization = getattr(view, "get_organization", None)
        if callable(get_organization):
            return get_organization()
        return None
