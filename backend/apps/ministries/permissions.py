from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import BasePermission

from apps.accounts.models import UserRole
from apps.ministries.models import MinistryStaffRole, MinistryType


STATE_MANAGEMENT_ROLES = {
    MinistryStaffRole.STATE_SUPER_ADMIN,
}

FACILITY_ACCREDITATION_ROLES = {
    MinistryStaffRole.STATE_SUPER_ADMIN,
    MinistryStaffRole.FACILITY_ACCREDITATION_OFFICER,
}

CERTIFICATE_VALIDATION_ROLES = {
    MinistryStaffRole.STATE_SUPER_ADMIN,
    MinistryStaffRole.CERTIFICATE_VERIFICATION_OFFICER,
}

STATE_FEE_ROLES = {
    MinistryStaffRole.STATE_SUPER_ADMIN,
    MinistryStaffRole.POLICY_FINANCE_OFFICER,
}

INSPECTION_COORDINATION_ROLES = {
    MinistryStaffRole.STATE_SUPER_ADMIN,
    MinistryStaffRole.INSPECTORATE_COORDINATOR,
}

STATE_REPORT_ROLES = {
    MinistryStaffRole.STATE_SUPER_ADMIN,
    MinistryStaffRole.FOOD_SAFETY_OFFICER,
    MinistryStaffRole.POLICY_FINANCE_OFFICER,
}

NATIONAL_POLICY_ROLES = {
    MinistryStaffRole.FEDERAL_SUPER_ADMIN,
    MinistryStaffRole.NATIONAL_POLICY_OFFICER,
}

FEDERAL_REPORT_REVIEW_ROLES = {
    MinistryStaffRole.FEDERAL_SUPER_ADMIN,
    MinistryStaffRole.NATIONAL_FOOD_SAFETY_OFFICER,
    MinistryStaffRole.NATIONAL_ME_OFFICER,
}

FEDERAL_QUERY_ROLES = {
    MinistryStaffRole.FEDERAL_SUPER_ADMIN,
    MinistryStaffRole.NATIONAL_FOOD_SAFETY_OFFICER,
    MinistryStaffRole.NATIONAL_ME_OFFICER,
}


def ministry_profile(user):
    try:
        return getattr(user, "ministry_profile", None)
    except ObjectDoesNotExist:
        return None


def ministry_sub_role(user):
    profile = ministry_profile(user)
    if profile and profile.is_active:
        return profile.sub_role
    return ""


def ministry_type(user):
    profile = ministry_profile(user)
    if profile and profile.is_active:
        return profile.ministry_type
    if getattr(user, "role", None) == UserRole.STATE_ADMIN:
        return MinistryType.STATE
    if getattr(user, "role", None) == UserRole.FEDERAL_ADMIN:
        return MinistryType.FEDERAL
    return ""


def effective_state_id(user):
    profile = ministry_profile(user)
    if profile and profile.is_active and profile.state_id:
        return profile.state_id
    return getattr(user, "state_id", None)


def effective_lga_id(user):
    profile = ministry_profile(user)
    if profile and profile.is_active and profile.lga_id:
        return profile.lga_id
    unit = getattr(user, "unit", None)
    if getattr(user, "unit_restricted", False) and unit and getattr(unit, "lga_id", None):
        return unit.lga_id
    return None


def is_state_ministry_user(user):
    return bool(
        user
        and user.is_authenticated
        and user.role in {UserRole.SUPER_ADMIN, UserRole.STATE_ADMIN, UserRole.INSPECTOR}
    )


def is_federal_ministry_user(user):
    return bool(
        user
        and user.is_authenticated
        and user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}
    )


def _state_role_allowed(user, allowed_roles):
    if getattr(user, "role", None) == UserRole.SUPER_ADMIN:
        return True
    if getattr(user, "role", None) != UserRole.STATE_ADMIN:
        return False
    sub_role = ministry_sub_role(user)
    return not sub_role or sub_role in allowed_roles


def _federal_role_allowed(user, allowed_roles):
    if getattr(user, "role", None) == UserRole.SUPER_ADMIN:
        return True
    if getattr(user, "role", None) != UserRole.FEDERAL_ADMIN:
        return False
    sub_role = ministry_sub_role(user)
    return not sub_role or sub_role in allowed_roles


def can_manage_state_users(user):
    return _state_role_allowed(user, STATE_MANAGEMENT_ROLES)


def can_review_facility_accreditation(user):
    return _state_role_allowed(user, FACILITY_ACCREDITATION_ROLES)


def can_validate_certificates(user):
    return _state_role_allowed(user, CERTIFICATE_VALIDATION_ROLES)


def can_manage_state_fees(user):
    return _state_role_allowed(user, STATE_FEE_ROLES)


def can_assign_inspections(user):
    return _state_role_allowed(user, INSPECTION_COORDINATION_ROLES)


def can_submit_state_reports(user):
    return _state_role_allowed(user, STATE_REPORT_ROLES)


def can_view_federal_aggregate_data(user):
    if getattr(user, "role", None) == UserRole.SUPER_ADMIN:
        return True
    return getattr(user, "role", None) == UserRole.FEDERAL_ADMIN


def can_manage_national_policy(user):
    return _federal_role_allowed(user, NATIONAL_POLICY_ROLES)


def can_review_state_reports(user):
    return _federal_role_allowed(user, FEDERAL_REPORT_REVIEW_ROLES)


def can_manage_federal_queries(user):
    return _federal_role_allowed(user, FEDERAL_QUERY_ROLES)


def can_access_state_scope(user, state_id=None, lga_id=None):
    if getattr(user, "role", None) in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
        return True
    if not is_state_ministry_user(user):
        return False
    user_state_id = effective_state_id(user)
    if state_id and str(user_state_id) != str(state_id):
        return False
    user_lga_id = effective_lga_id(user)
    if user_lga_id and lga_id and str(user_lga_id) != str(lga_id):
        return False
    return bool(user_state_id)


class IsStateMinistryUser(BasePermission):
    message = "Only state ministry users can access this endpoint."

    def has_permission(self, request, view):
        return is_state_ministry_user(request.user)


class IsFederalMinistryUser(BasePermission):
    message = "Only federal ministry users can access this endpoint."

    def has_permission(self, request, view):
        return is_federal_ministry_user(request.user)
