from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.accounts.models import UserRole


REGULATORY_ROLES = {
    UserRole.SUPER_ADMIN,
    UserRole.FEDERAL_ADMIN,
    UserRole.STATE_ADMIN,
    UserRole.INSPECTOR,
}

ORG_ROLES = {
    UserRole.FACILITY_ADMIN,
    UserRole.DOCTOR,
    UserRole.LAB_STAFF,
    UserRole.EMPLOYER,
}


def is_super_admin(user) -> bool:
    return bool(user and user.is_authenticated and user.role == UserRole.SUPER_ADMIN)


def is_federal_admin(user) -> bool:
    return bool(user and user.is_authenticated and user.role == UserRole.FEDERAL_ADMIN)


def is_state_admin(user) -> bool:
    return bool(user and user.is_authenticated and user.role == UserRole.STATE_ADMIN)


def shares_organization(user, obj) -> bool:
    return bool(
        getattr(user, "organization_id", None)
        and getattr(obj, "organization_id", None) == user.organization_id
    )


def shares_state(user, obj) -> bool:
    obj_state_id = getattr(obj, "state_id", None)
    if obj_state_id is None and getattr(obj, "organization", None):
        obj_state_id = getattr(obj.organization, "state_id", None)
    return bool(getattr(user, "state_id", None) and obj_state_id == user.state_id)


class IsActiveUser(BasePermission):
    message = "Your account is not active."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "status", None) == "active"
        )


class IsSelfOrScopedAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if is_super_admin(user):
            return True
        if obj.pk == user.pk:
            return True
        if is_federal_admin(user):
            return request.method in SAFE_METHODS
        if is_state_admin(user):
            return shares_state(user, obj)
        return shares_organization(user, obj)


class CanManageOrganization(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if is_super_admin(user):
            return True
        if is_federal_admin(user):
            return request.method in SAFE_METHODS
        if is_state_admin(user):
            return obj.state_id == user.state_id
        return obj.pk == getattr(user, "organization_id", None)
