from dataclasses import asdict, dataclass, field

from django.utils import timezone

from apps.accounts.models import UserRole
from apps.organizations.models import MembershipStatus, Organization, OrganizationMembership, OrganizationType, PermissionOverrideEffect


@dataclass(frozen=True)
class AccessResult:
    allowed: bool
    reason: str
    scope: str = "none"
    organization_id: str | None = None
    unit_id: str | None = None
    membership_id: str | None = None
    role_code: str = ""
    permission_code: str = ""
    filters: dict = field(default_factory=dict)

    def as_dict(self):
        return asdict(self)


class EffectiveAccessService:
    def check(self, user, permission_code, organization=None, resource=None):
        if not user or not user.is_authenticated:
            return AccessResult(False, "Authentication is required.", permission_code=permission_code)

        if getattr(user, "role", None) == UserRole.SUPER_ADMIN:
            return AccessResult(
                True,
                "Super admin has global access.",
                scope="global",
                permission_code=permission_code,
                filters={},
            )

        membership = self._resolve_membership(user, organization=organization, resource=resource)
        if not membership:
            return AccessResult(False, "No active organization membership found.", permission_code=permission_code)

        role_permission_codes = set(membership.role.role_permissions.values_list("permission__code", flat=True))
        allowed = permission_code in role_permission_codes
        reason = "Allowed by role permission." if allowed else "Role does not include this permission."

        override = self._get_active_override(membership, permission_code)
        if override:
            allowed = override.effect == PermissionOverrideEffect.ALLOW
            reason = "Allowed by permission override." if allowed else "Denied by permission override."

        scope = self._scope_for(membership)
        filters = self._filters_for(membership, scope)

        return AccessResult(
            allowed=allowed,
            reason=reason,
            scope=scope if allowed else "none",
            organization_id=str(membership.organization_id),
            unit_id=str(membership.unit_id) if membership.unit_id else None,
            membership_id=str(membership.id),
            role_code=membership.role.code,
            permission_code=permission_code,
            filters=filters if allowed else {},
        )

    def list_permissions(self, user, organization=None):
        if not user or not user.is_authenticated:
            return []
        if getattr(user, "role", None) == UserRole.SUPER_ADMIN:
            from apps.organizations.models import Permission

            return sorted(Permission.objects.values_list("code", flat=True))

        memberships = user.memberships.select_related("organization", "role").filter(status=MembershipStatus.ACTIVE)
        if organization is not None:
            memberships = memberships.filter(organization=organization)

        allowed = set()
        now = timezone.now()
        for membership in memberships.prefetch_related("role__role_permissions__permission", "permission_overrides__permission"):
            allowed.update(membership.role.role_permissions.values_list("permission__code", flat=True))
            for override in membership.permission_overrides.select_related("permission"):
                if override.expires_at and override.expires_at <= now:
                    continue
                if override.effect == PermissionOverrideEffect.DENY:
                    allowed.discard(override.permission.code)
                elif override.effect == PermissionOverrideEffect.ALLOW:
                    allowed.add(override.permission.code)
        return sorted(allowed)

    def _resolve_membership(self, user, organization=None, resource=None):
        organization_id = self._organization_id_for(organization) or self._organization_id_for_resource(resource)
        queryset = (
            OrganizationMembership.objects.select_related("organization", "role", "unit")
            .prefetch_related("permission_overrides__permission")
            .filter(user=user, status=MembershipStatus.ACTIVE)
        )
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset.first()

    def _get_active_override(self, membership, permission_code):
        now = timezone.now()
        return (
            membership.permission_overrides.select_related("permission")
            .filter(permission__code=permission_code)
            .filter(expires_at__isnull=True)
            .first()
            or membership.permission_overrides.select_related("permission")
            .filter(permission__code=permission_code, expires_at__gt=now)
            .first()
        )

    def _scope_for(self, membership):
        if membership.unit_restricted and membership.unit_id:
            return "unit"
        if membership.organization.organization_type == OrganizationType.STATE_MINISTRY:
            return "state"
        if membership.organization.state_id and membership.role.code == UserRole.STATE_ADMIN:
            return "state"
        return "organization"

    def _filters_for(self, membership, scope):
        if scope == "unit":
            return {"organization_id": str(membership.organization_id), "unit_id": str(membership.unit_id)}
        if scope == "state":
            return {"state_id": str(membership.organization.state_id) if membership.organization.state_id else None}
        if scope == "organization":
            return {"organization_id": str(membership.organization_id)}
        return {}

    def _organization_id_for(self, organization):
        if organization is None:
            return None
        if isinstance(organization, Organization):
            return organization.id
        return organization

    def _organization_id_for_resource(self, resource):
        if resource is None:
            return None
        organization_id = getattr(resource, "organization_id", None)
        if organization_id:
            return organization_id
        organization = getattr(resource, "organization", None)
        return getattr(organization, "id", None)
