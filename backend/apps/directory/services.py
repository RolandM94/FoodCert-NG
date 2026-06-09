from apps.accounts.models import User, UserRole
from apps.organizations.models import OrganizationMembership


class DirectoryScopeService:
    """Resolves user scope for directory queries."""

    def __init__(self, user: User):
        self.user = user
        self.membership = user.current_membership

    def state_filter(self):
        if self.user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return {}
        if self.user.role == UserRole.STATE_ADMIN:
            return {"state_id": self.user.state_id}
        if self.membership and self.membership.organization:
            org = self.membership.organization
            if org.state_id:
                return {"state_id": org.state_id}
        return {}

    def organization_filter(self):
        if self.user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return {}
        if self.user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return self.state_filter()
        if self.membership and self.membership.organization:
            return {"organization_id": self.membership.organization_id}
        return {"id__in": []}

    def branch_filter(self, field_name: str = "business_branch_id"):
        if self.user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return {}
        if self.membership and self.membership.unit_restricted and self.membership.unit:
            return {field_name: self.membership.unit_id}
        return {}

    def employer_filter(self):
        if self.user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return {}
        if hasattr(self.user, 'employer') and self.user.employer:
            return {"employer_id": self.user.employer.id}
        if self.membership and self.membership.organization:
            org_type = self.membership.organization.organization_type
            if org_type == "employer" and hasattr(self.membership.organization, 'employer'):
                return {"employer_id": self.membership.organization.employer.id}
        return {}

    def facility_filter(self):
        if self.user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return {}
        if self.user.role == UserRole.FACILITY_ADMIN and self.user.organization_id:
            return {"facility_id": self.user.organization_id}
        return {}
