from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.accounts.models import UserRole
from apps.accounts.permissions import is_super_admin, is_federal_admin, is_state_admin


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
