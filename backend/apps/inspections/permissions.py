from django.db.models import Q
from rest_framework.exceptions import PermissionDenied

from apps.accounts.models import UserRole

INSPECTOR_ROLES = {
    UserRole.INSPECTOR,
    UserRole.STATE_ADMIN,
    UserRole.SUPER_ADMIN,
    UserRole.FEDERAL_ADMIN,
}

COORDINATOR_ROLES = {
    UserRole.STATE_ADMIN,
    UserRole.SUPER_ADMIN,
    UserRole.FEDERAL_ADMIN,
}

ADMIN_ROLES = {
    UserRole.STATE_ADMIN,
    UserRole.SUPER_ADMIN,
}

FEDERAL_ROLES = {
    UserRole.FEDERAL_ADMIN,
    UserRole.SUPER_ADMIN,
}

INSPECTOR_PRIVATE_METADATA_KEYS = {
    "lab_results",
    "diagnosis",
    "doctor_notes",
    "declaration_answers",
    "full_nin",
    "medical_history",
    "vaccination_medical_data",
}


def is_inspector_role(user):
    return user.role in INSPECTOR_ROLES


def is_coordinator_role(user):
    return user.role in COORDINATOR_ROLES


def is_admin_role(user):
    return user.role in ADMIN_ROLES


def is_federal_admin_role(user):
    return user.role in FEDERAL_ROLES


def ensure_inspector_role(user):
    if not is_inspector_role(user):
        raise PermissionDenied("Only inspectors and regulators can perform this action.")


def ensure_coordinator_role(user):
    if not is_coordinator_role(user):
        raise PermissionDenied("Only coordinators and administrators can perform this action.")


def ensure_admin_role(user):
    if not is_admin_role(user):
        raise PermissionDenied("Only state administrators can perform this action.")


def ensure_federal_role(user):
    if not is_federal_admin_role(user):
        raise PermissionDenied("Only federal administrators can access this data.")


def ensures_state_match(user, target_state_id):
    if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
        return
    if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
        if user.state_id != target_state_id:
            raise PermissionDenied("You can only access inspections in your own state.")


def ensure_inspection_owner(user, inspection):
    if user.role == UserRole.INSPECTOR and inspection.inspector_id != user.id:
        raise PermissionDenied("Only the assigned inspector can perform this action.")


def ensure_employer_scope(user, employer):
    if user.role == UserRole.EMPLOYER:
        if hasattr(user, "employer") and user.employer_id == employer.id:
            return
        if user.organization_id == employer.organization_id:
            return
        raise PermissionDenied("You can only access notices for your own organization.")
