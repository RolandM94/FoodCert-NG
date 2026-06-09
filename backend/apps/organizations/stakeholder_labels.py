from apps.organizations.models import OrganizationType

STAKEHOLDER_LABELS = {
    OrganizationType.FEDERAL_MINISTRY: {
        "stakeholders": "Federal Users",
        "units": "Departments / Directorates",
        "unit": "Department / Directorate",
        "invite_button": "Invite Federal User",
    },
    OrganizationType.STATE_MINISTRY: {
        "stakeholders": "Officers",
        "units": "Units & Offices",
        "unit": "Unit / Office",
        "invite_button": "Invite Officer",
    },
    OrganizationType.MEDICAL_FACILITY: {
        "stakeholders": "Staff",
        "units": "Departments",
        "unit": "Department",
        "invite_button": "Invite Staff",
    },
    OrganizationType.EMPLOYER: {
        "stakeholders": "Team Members",
        "units": "Branches / Outlets",
        "unit": "Branch / Outlet",
        "invite_button": "Invite Team Member",
    },
    OrganizationType.PLATFORM_OPERATOR: {
        "stakeholders": "Platform Users",
        "units": "Teams / Units",
        "unit": "Team / Unit",
        "invite_button": "Invite Platform User",
    },
}
