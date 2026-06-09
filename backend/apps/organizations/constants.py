from apps.organizations.models import OrganizationType


UNIT_LABELS = {
    OrganizationType.FEDERAL_MINISTRY: {"plural": "Departments & Directorates", "singular": "Department"},
    OrganizationType.STATE_MINISTRY: {"plural": "Units & Offices", "singular": "Unit"},
    OrganizationType.MEDICAL_FACILITY: {"plural": "Departments", "singular": "Department"},
    OrganizationType.EMPLOYER: {"plural": "Branches", "singular": "Branch"},
    OrganizationType.PLATFORM_OPERATOR: {"plural": "Teams", "singular": "Team"},
}
