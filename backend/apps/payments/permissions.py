from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied

from apps.accounts.models import EmployerStaffRole, UserRole
from apps.facilities.models import FacilityStaffType
from apps.ministries.permissions import can_manage_state_fees, can_view_federal_aggregate_data, effective_state_id, ministry_sub_role
from apps.ministries.models import MinistryStaffRole


FINANCE_PRIVATE_METADATA_KEYS = {
    "diagnosis",
    "doctor_note",
    "doctor_notes",
    "lab_result",
    "lab_results",
    "medical_result",
    "medical_results",
    "declaration_answer",
    "declaration_answers",
    "treatment",
    "treatment_note",
    "treatment_notes",
    "nin",
    "full_nin",
}

STATE_FINANCE_ROLES = {
    MinistryStaffRole.STATE_SUPER_ADMIN,
    MinistryStaffRole.POLICY_FINANCE_OFFICER,
}

FEDERAL_FINANCE_ROLES = {
    MinistryStaffRole.FEDERAL_SUPER_ADMIN,
    MinistryStaffRole.NATIONAL_FINANCE_OFFICER,
}


def is_platform_finance_user(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.role == UserRole.SUPER_ADMIN:
        return True
    if user.role != UserRole.FEDERAL_ADMIN:
        return False
    sub_role = ministry_sub_role(user)
    return not sub_role or sub_role in FEDERAL_FINANCE_ROLES


def is_state_finance_user(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.role == UserRole.SUPER_ADMIN:
        return True
    if user.role != UserRole.STATE_ADMIN:
        return False
    sub_role = ministry_sub_role(user)
    return not sub_role or sub_role in STATE_FINANCE_ROLES


def can_manage_financial_policy(user) -> bool:
    return is_platform_finance_user(user) or can_manage_state_fees(user)


def can_view_national_finance(user) -> bool:
    return is_platform_finance_user(user) or can_view_federal_aggregate_data(user)


def facility_for_finance_user(user):
    try:
        profile = getattr(user, "facility_staff_profile", None)
    except ObjectDoesNotExist:
        profile = None
    if profile and profile.is_active and profile.staff_type in {FacilityStaffType.FACILITY_ADMIN, FacilityStaffType.FINANCE_USER}:
        return profile.facility
    organization = getattr(user, "organization", None)
    if user.role == UserRole.FACILITY_ADMIN and organization:
        try:
            return getattr(organization, "medical_facility", None)
        except ObjectDoesNotExist:
            return None
    return None


def has_facility_finance_access(user, facility) -> bool:
    if is_platform_finance_user(user):
        return True
    if is_state_finance_user(user) and getattr(facility, "state_id", None) == effective_state_id(user):
        return True
    user_facility = facility_for_finance_user(user)
    return bool(user_facility and user_facility.id == facility.id)


def ensure_facility_finance_access(user, facility):
    if not has_facility_finance_access(user, facility):
        raise PermissionDenied("You cannot view settlements for this facility.")


def has_employer_billing_access(user, employer, *, manage=False) -> bool:
    if is_platform_finance_user(user):
        return True
    if user.role == UserRole.STATE_ADMIN:
        return not manage and employer.state_id == effective_state_id(user)
    if user.role != UserRole.EMPLOYER:
        return False
    same_owner = employer.user_id == user.id
    same_org = bool(user.organization_id and employer.organization_id == user.organization_id)
    if not same_owner and not same_org:
        return False
    if not manage:
        return True
    return user.employer_staff_role in {"", EmployerStaffRole.EMPLOYER_ADMIN, EmployerStaffRole.FINANCE_USER}


def ensure_employer_billing_access(user, employer, *, manage=False):
    if not has_employer_billing_access(user, employer, manage=manage):
        raise PermissionDenied("You cannot access billing for this employer.")


def scope_payment_transactions_for_user(queryset, user):
    if is_platform_finance_user(user):
        return queryset
    if user.role == UserRole.FEDERAL_ADMIN:
        return queryset
    if user.role == UserRole.STATE_ADMIN:
        state_id = effective_state_id(user)
        return queryset.filter(metadata__state_id=str(state_id)) if state_id else queryset.none()
    if user.role == UserRole.FACILITY_ADMIN:
        facility = facility_for_finance_user(user)
        return queryset.filter(metadata__facility_id=str(facility.id)) if facility else queryset.none()
    if user.role == UserRole.EMPLOYER:
        filters = Q(payer_user=user)
        if user.organization_id:
            filters |= Q(payer_user__organization_id=user.organization_id, payer_type="employer")
        return queryset.filter(filters)
    return queryset.filter(payer_user=user)


def redacted_finance_metadata(metadata):
    if not isinstance(metadata, dict):
        return {}
    return {
        key: value
        for key, value in metadata.items()
        if key not in FINANCE_PRIVATE_METADATA_KEYS
    }
