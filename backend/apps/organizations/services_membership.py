from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.organizations.models import MembershipStatus, OrganizationMembership
from apps.organizations.services import ensure_can_manage_units


def get_user_active_membership(user, organization=None):
    queryset = user.memberships.select_related("organization", "role", "unit").filter(status=MembershipStatus.ACTIVE)
    if organization is not None:
        queryset = queryset.filter(organization=organization)
    return queryset.first()


def _snapshot(membership):
    return {
        "role": str(membership.role_id),
        "role_code": membership.role.code,
        "unit": str(membership.unit_id) if membership.unit_id else "",
        "unit_restricted": membership.unit_restricted,
        "status": membership.status,
    }


def ensure_can_manage_memberships(*, actor, organization):
    ensure_can_manage_units(actor, organization)


@transaction.atomic
def create_membership(*, actor, organization, user, role, unit=None, unit_restricted=False, invited_by=None, status=MembershipStatus.ACTIVE):
    ensure_can_manage_memberships(actor=actor, organization=organization)
    if unit and unit.organization_id != organization.id:
        raise ValidationError("Unit must belong to the membership organization.")
    if role.organization_type and role.organization_type != organization.organization_type:
        raise ValidationError("Role is not valid for this organization type.")
    if status == MembershipStatus.ACTIVE and OrganizationMembership.objects.filter(user=user, organization=organization, status=MembershipStatus.ACTIVE).exists():
        raise ValidationError("User already has an active membership in this organization.")
    membership = OrganizationMembership.objects.create(
        user=user,
        organization=organization,
        role=role,
        unit=unit,
        unit_restricted=unit_restricted,
        status=status,
        invited_by=invited_by or actor,
        joined_at=timezone.now() if status == MembershipStatus.ACTIVE else None,
    )
    if status == MembershipStatus.ACTIVE:
        user.organization = organization
        user.unit = unit
        user.unit_restricted = unit_restricted
        user.role = role.code if role.code in [choice[0] for choice in user._meta.get_field("role").choices] else user.role
        user.save(update_fields=["organization", "unit", "unit_restricted", "role", "updated_at"])
    log_action(action=AuditAction.CREATE, actor=actor, target=membership, metadata={"event": "membership_created"})
    return membership


@transaction.atomic
def update_membership(*, actor, membership, role=None, unit=None, unit_restricted=None):
    ensure_can_manage_memberships(actor=actor, organization=membership.organization)
    old_value = _snapshot(membership)
    if role is not None:
        if role.organization_type and role.organization_type != membership.organization.organization_type:
            raise ValidationError("Role is not valid for this organization type.")
        membership.role = role
    if unit is not None and unit.organization_id != membership.organization_id:
        raise ValidationError("Unit must belong to the membership organization.")
    if unit is not None:
        membership.unit = unit
    if unit_restricted is not None:
        membership.unit_restricted = unit_restricted
    membership.save(update_fields=["role", "unit", "unit_restricted", "updated_at"])
    _sync_user_from_active_membership(membership)
    log_action(
        action=AuditAction.UPDATE,
        actor=actor,
        target=membership,
        old_value=old_value,
        new_value=_snapshot(membership),
        metadata={"event": "membership_updated"},
    )
    return membership


@transaction.atomic
def change_role(*, actor, membership, role):
    old_value = _snapshot(membership)
    membership = update_membership(actor=actor, membership=membership, role=role)
    log_action(
        action=AuditAction.ROLE_CHANGE,
        actor=actor,
        target=membership,
        old_value=old_value,
        new_value=_snapshot(membership),
        metadata={"event": "membership_role_changed"},
    )
    return membership


@transaction.atomic
def change_unit(*, actor, membership, unit=None, unit_restricted=False):
    old_value = _snapshot(membership)
    membership = update_membership(actor=actor, membership=membership, unit=unit, unit_restricted=unit_restricted)
    log_action(
        action=AuditAction.UPDATE,
        actor=actor,
        target=membership,
        old_value=old_value,
        new_value=_snapshot(membership),
        metadata={"event": "membership_unit_changed"},
    )
    return membership


@transaction.atomic
def suspend_membership(*, actor, membership):
    return _transition_membership(actor=actor, membership=membership, status=MembershipStatus.SUSPENDED, event="membership_suspended")


@transaction.atomic
def reactivate_membership(*, actor, membership):
    if OrganizationMembership.objects.filter(
        user=membership.user,
        organization=membership.organization,
        status=MembershipStatus.ACTIVE,
    ).exclude(pk=membership.pk).exists():
        raise ValidationError("Another active membership already exists for this user and organization.")
    membership = _transition_membership(actor=actor, membership=membership, status=MembershipStatus.ACTIVE, event="membership_reactivated")
    membership.joined_at = membership.joined_at or timezone.now()
    membership.save(update_fields=["joined_at", "updated_at"])
    _sync_user_from_active_membership(membership)
    return membership


@transaction.atomic
def remove_membership(*, actor, membership):
    return _transition_membership(actor=actor, membership=membership, status=MembershipStatus.REMOVED, event="membership_removed")


@transaction.atomic
def toggle_unit_restriction(*, actor, membership):
    old_value = _snapshot(membership)
    membership.unit_restricted = not membership.unit_restricted
    membership.save(update_fields=["unit_restricted", "updated_at"])
    _sync_user_from_active_membership(membership)
    log_action(
        action=AuditAction.UPDATE,
        actor=actor,
        target=membership,
        old_value=old_value,
        new_value=_snapshot(membership),
        metadata={"event": "membership_unit_restriction_toggled"},
    )
    return membership


def _transition_membership(*, actor, membership, status, event):
    ensure_can_manage_memberships(actor=actor, organization=membership.organization)
    old_value = _snapshot(membership)
    membership.status = status
    membership.save(update_fields=["status", "updated_at"])
    if status != MembershipStatus.ACTIVE:
        _clear_user_if_current(membership)
    log_action(
        action=AuditAction.UPDATE,
        actor=actor,
        target=membership,
        old_value=old_value,
        new_value=_snapshot(membership),
        metadata={"event": event},
    )
    return membership


def _sync_user_from_active_membership(membership):
    if membership.status != MembershipStatus.ACTIVE:
        return
    user = membership.user
    user.organization = membership.organization
    user.unit = membership.unit
    user.unit_restricted = membership.unit_restricted
    role_values = {choice[0] for choice in user._meta.get_field("role").choices}
    if membership.role.code in role_values:
        user.role = membership.role.code
    user.save(update_fields=["organization", "unit", "unit_restricted", "role", "updated_at"])


def _clear_user_if_current(membership):
    user = membership.user
    if user.organization_id != membership.organization_id:
        return
    replacement = get_user_active_membership(user)
    if replacement and replacement.id != membership.id:
        _sync_user_from_active_membership(replacement)
        return
    user.organization = None
    user.unit = None
    user.unit_restricted = False
    user.save(update_fields=["organization", "unit", "unit_restricted", "updated_at"])
