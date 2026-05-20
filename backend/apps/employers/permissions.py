from rest_framework.permissions import BasePermission

from apps.accounts.models import UserRole


def is_employer_owner(user) -> bool:
    return bool(user and user.is_authenticated and user.role == UserRole.EMPLOYER)


def is_branch_manager(user) -> bool:
    return bool(
        user
        and user.is_authenticated
        and user.role == UserRole.EMPLOYER
        and getattr(user, "unit_id", None) is not None
        and getattr(user, "unit_restricted", False)
    )


def is_same_employer(user, employer) -> bool:
    if not user or not user.is_authenticated or not employer:
        return False
    if user.role == UserRole.EMPLOYER:
        return getattr(user, "employer", None) and user.employer.id == employer.id
    if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
        return True
    return user.organization_id == employer.organization_id


class IsEmployerOwner(BasePermission):
    message = "Only the employer business owner can perform this action."

    def has_permission(self, request, view):
        return is_employer_owner(request.user)

    def has_object_permission(self, request, view, obj):
        from apps.employers.models import Employer

        if isinstance(obj, Employer):
            return obj.user_id == request.user.id
        return True


class IsEmployerOrRegulator(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and user.role in {
            UserRole.EMPLOYER, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN,
            UserRole.STATE_ADMIN, UserRole.INSPECTOR,
        }
