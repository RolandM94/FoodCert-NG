from django.db import IntegrityError

from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import UserRole
from apps.accounts.permissions import is_super_admin, is_federal_admin, is_state_admin
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.organizations.models import Organization, OrganizationUnit


MAX_NESTING_DEPTH = 3


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
    parent = data.get("parent")
    if parent:
        validate_nesting_depth(parent)
        if parent.organization_id != organization.id:
            raise ValidationError("Parent unit must belong to the same organization.")
    try:
        unit = OrganizationUnit.objects.create(organization=organization, **data)
    except IntegrityError:
        raise ValidationError("A unit with this name already exists in this organization.")
    log_action(action=AuditAction.CREATE, actor=actor, target=unit)
    return unit


def update_unit(*, actor, unit, **data):
    ensure_can_manage_units(actor, unit.organization)
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
    unit.save()
    log_action(action=AuditAction.UPDATE, actor=actor, target=unit)
    return unit


def deactivate_unit(*, actor, unit):
    ensure_can_manage_units(actor, unit.organization)
    unit.is_active = False
    unit.save(update_fields=["is_active", "updated_at"])
    unit.members.update(unit=None, unit_restricted=False)
    unit.food_handlers.update(business_branch=None)
    unit.children.filter(is_active=True).update(is_active=False)
    log_action(action=AuditAction.UPDATE, actor=actor, target=unit, metadata={"event": "unit_soft_deleted"})
    return unit
