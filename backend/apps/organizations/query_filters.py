from apps.organizations.services_access import EffectiveAccessService


class UnitScopedQuerySetMixin:
    permission_code = None

    def get_scoped_queryset(self, base_queryset, scope_field="unit", organization_field="organization", state_field="state"):
        result = EffectiveAccessService().check(
            self.request.user,
            self.get_permission_code(),
            organization=getattr(self, "get_organization", lambda: None)(),
        )
        if not result.allowed:
            return base_queryset.none()
        if result.scope == "global":
            return base_queryset
        if result.scope == "unit" and result.unit_id:
            return base_queryset.filter(**{f"{scope_field}_id": result.unit_id})
        if result.scope == "state" and result.filters.get("state_id"):
            return base_queryset.filter(**{f"{state_field}_id": result.filters["state_id"]})
        if result.scope == "organization" and result.organization_id:
            return base_queryset.filter(**{f"{organization_field}_id": result.organization_id})
        return base_queryset.none()

    def get_permission_code(self):
        if self.permission_code:
            return self.permission_code
        return getattr(self, "stakeholder_permission_code", "")
