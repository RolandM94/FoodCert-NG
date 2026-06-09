from django.db import IntegrityError

from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import UserRole
from apps.accounts.permissions import is_super_admin, is_federal_admin, is_state_admin
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.organizations.models import MembershipStatus, Organization, OrganizationUnit, OrganizationUnitStatus, OrganizationUnitType


MAX_NESTING_DEPTH = 3

COMMON_UNIT_TYPES = {
    OrganizationUnitType.HEADQUARTERS,
    OrganizationUnitType.DEPARTMENT,
    OrganizationUnitType.UNIT,
    OrganizationUnitType.OFFICE,
    OrganizationUnitType.FINANCE_UNIT,
    OrganizationUnitType.ADMINISTRATION_UNIT,
    OrganizationUnitType.SUPPORT_UNIT,
    OrganizationUnitType.TECHNICAL_UNIT,
    OrganizationUnitType.OTHER,
}
UNIT_TYPES_BY_ORGANIZATION_TYPE = {
    "platform_operator": COMMON_UNIT_TYPES,
    "federal_ministry": COMMON_UNIT_TYPES | {OrganizationUnitType.DIRECTORATE},
    "state_ministry": COMMON_UNIT_TYPES | {
        OrganizationUnitType.DIRECTORATE,
        OrganizationUnitType.DESK,
        OrganizationUnitType.LGA_OFFICE,
        OrganizationUnitType.INSPECTORATE,
    },
    "medical_facility": COMMON_UNIT_TYPES | {
        OrganizationUnitType.CLINICAL_DEPARTMENT,
        OrganizationUnitType.LAB_DEPARTMENT,
        OrganizationUnitType.MEDICAL_RECORDS_DEPARTMENT,
        OrganizationUnitType.RECORDS_DEPARTMENT,
    },
    "employer": COMMON_UNIT_TYPES | {
        OrganizationUnitType.BRANCH,
        OrganizationUnitType.REGIONAL_OFFICE,
        OrganizationUnitType.SITE,
        OrganizationUnitType.OUTLET,
        OrganizationUnitType.STORE,
    },
}


def _nesting_depth(unit):
    depth = 1
    current = unit
    while current.parent_id:
        depth += 1
        if depth > MAX_NESTING_DEPTH:
            return depth
        current = current.parent
    return depth


def _is_descendant(*, candidate_parent, unit):
    current = candidate_parent
    while current:
        if current.id == unit.id:
            return True
        current = current.parent
    return False


def _subtree_depth(unit):
    child_depths = [_subtree_depth(child) for child in unit.children.all()]
    return 1 + (max(child_depths) if child_depths else 0)


def validate_nesting_depth(parent):
    if _nesting_depth(parent) >= MAX_NESTING_DEPTH:
        raise ValidationError(f"Unit nesting depth cannot exceed {MAX_NESTING_DEPTH} levels.")


def validate_reparenting_depth(*, unit, parent):
    if parent is None:
        return
    if parent.id == unit.id:
        raise ValidationError("A unit cannot be its own parent.")
    if _is_descendant(candidate_parent=parent, unit=unit):
        raise ValidationError("A unit cannot be moved under one of its own child units.")
    parent_depth = _nesting_depth(parent)
    if parent_depth + _subtree_depth(unit) > MAX_NESTING_DEPTH:
        raise ValidationError(f"Unit nesting depth cannot exceed {MAX_NESTING_DEPTH} levels.")


def validate_unit_type_for_organization(*, organization, unit_type):
    allowed = UNIT_TYPES_BY_ORGANIZATION_TYPE.get(organization.organization_type, COMMON_UNIT_TYPES)
    if unit_type not in allowed:
        raise ValidationError(f"{unit_type} is not a valid unit type for {organization.get_organization_type_display()}.")


def ensure_can_manage_units(actor, organization):
    if is_super_admin(actor) or is_federal_admin(actor):
        return
    if is_state_admin(actor) and organization.state_id == actor.state_id:
        return
    if actor.role in {UserRole.FACILITY_ADMIN, UserRole.EMPLOYER} and organization.id == actor.organization_id:
        return
    raise PermissionDenied("You cannot manage units for this organization.")


def create_unit(*, actor, organization, **data):
    ensure_can_manage_units(actor, organization)
    validate_unit_type_for_organization(organization=organization, unit_type=data.get("unit_type", OrganizationUnitType.UNIT))
    parent = data.get("parent")
    if parent:
        validate_nesting_depth(parent)
        if parent.organization_id != organization.id:
            raise ValidationError("Parent unit must belong to the same organization.")
    try:
        if "status" not in data:
            data["status"] = OrganizationUnitStatus.ACTIVE
        data.setdefault("is_active", data["status"] == OrganizationUnitStatus.ACTIVE)
        unit = OrganizationUnit.objects.create(organization=organization, created_by=actor, **data)
    except IntegrityError:
        raise ValidationError("A unit with this name already exists in this organization.")
    log_action(action=AuditAction.CREATE, actor=actor, target=unit)
    return unit


def update_unit(*, actor, unit, **data):
    ensure_can_manage_units(actor, unit.organization)
    validate_unit_type_for_organization(organization=unit.organization, unit_type=data.get("unit_type", unit.unit_type))
    parent = data.get("parent")
    current_parent = data.get("parent", unit.parent)
    if current_parent:
        validate_reparenting_depth(unit=unit, parent=current_parent)
        if current_parent.organization_id != unit.organization_id:
            raise ValidationError("Parent unit must belong to the same organization.")
    elif "parent" in data:
        validate_reparenting_depth(unit=unit, parent=None)
    for field, value in data.items():
        setattr(unit, field, value)
    if "status" in data:
        unit.is_active = unit.status == OrganizationUnitStatus.ACTIVE
    elif "is_active" in data:
        unit.status = OrganizationUnitStatus.ACTIVE if unit.is_active else OrganizationUnitStatus.INACTIVE
    unit.save()
    log_action(action=AuditAction.UPDATE, actor=actor, target=unit)
    return unit


def deactivate_unit(*, actor, unit):
    ensure_can_manage_units(actor, unit.organization)
    unit.is_active = False
    unit.status = OrganizationUnitStatus.INACTIVE
    unit.save(update_fields=["is_active", "status", "updated_at"])
    unit.members.update(unit=None, unit_restricted=False)
    unit.food_handlers.update(business_branch=None)
    unit.children.filter(is_active=True).update(is_active=False, status=OrganizationUnitStatus.INACTIVE)
    log_action(action=AuditAction.UPDATE, actor=actor, target=unit, metadata={"event": "unit_soft_deleted"})
    return unit


def reactivate_unit(*, actor, unit):
    ensure_can_manage_units(actor, unit.organization)
    unit.status = OrganizationUnitStatus.ACTIVE
    unit.is_active = True
    unit.save(update_fields=["status", "is_active", "updated_at"])
    log_action(action=AuditAction.UPDATE, actor=actor, target=unit, metadata={"event": "unit_reactivated"})
    return unit


def archive_unit(*, actor, unit):
    ensure_can_manage_units(actor, unit.organization)
    unit.status = OrganizationUnitStatus.ARCHIVED
    unit.is_active = False
    unit.save(update_fields=["status", "is_active", "updated_at"])
    log_action(action=AuditAction.UPDATE, actor=actor, target=unit, metadata={"event": "unit_archived"})
    return unit


def assign_user_to_unit(*, actor, unit, user, unit_restricted=False):
    ensure_can_manage_units(actor, unit.organization)
    user.organization = unit.organization
    user.unit = unit
    user.unit_restricted = unit_restricted
    user.save(update_fields=["organization", "unit", "unit_restricted", "updated_at"])
    membership = user.memberships.filter(organization=unit.organization, status=MembershipStatus.ACTIVE).first()
    if membership:
        membership.unit = unit
        membership.unit_restricted = unit_restricted
        membership.save(update_fields=["unit", "unit_restricted", "updated_at"])
    log_action(
        action=AuditAction.UPDATE,
        actor=actor,
        target=unit,
        metadata={"event": "unit_user_assigned", "user_id": str(user.id), "unit_restricted": unit_restricted},
    )
    return user


def get_unit_tree(organization):
    units = list(organization.units.select_related("parent").order_by("name"))
    by_parent = {}
    for unit in units:
        by_parent.setdefault(unit.parent_id, []).append(unit)

    def serialize(unit):
        return {
            "id": str(unit.id),
            "name": unit.name,
            "unit_type": unit.unit_type,
            "status": unit.status,
            "is_active": unit.is_active,
            "children": [serialize(child) for child in by_parent.get(unit.id, [])],
        }

    return [serialize(unit) for unit in by_parent.get(None, [])]
