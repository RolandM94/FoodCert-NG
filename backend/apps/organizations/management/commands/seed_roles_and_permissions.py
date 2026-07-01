from django.core.management.base import BaseCommand
from django.db import transaction

from apps.organizations.models import OrganizationType, Permission, Role, RolePermission, RoleStatus
from apps.organizations.permission_codes import PERMISSIONS


ADMIN_PERMISSIONS = [
    "organization.view", "organization.update", "unit.view", "unit.create", "unit.update",
    "unit.deactivate", "unit.assign_user", "unit.view_members", "user.view", "user.invite",
    "user.update", "user.suspend", "user.reactivate", "user.remove", "invite.view",
    "invite.create", "invite.resend", "invite.revoke", "role.view", "role.assign",
    "permission.view",
]
VIEWER_PERMISSIONS = ["organization.view", "unit.view", "unit.view_members", "user.view", "role.view", "permission.view"]
FEDERAL_INDICATOR_PERMISSIONS = [
    "indicators.view_federal", "indicators.create_federal", "indicators.update_federal",
    "indicators.publish_federal", "indicators.share_to_states", "indicators.set_national_targets",
    "indicators.manage_thresholds", "indicators.view_cross_state_results",
    "indicators.export_federal_results", "indicators.ai_use_federal",
]
STATE_INDICATOR_PERMISSIONS = [
    "indicators.view_state", "indicators.create_state", "indicators.update_state",
    "indicators.adopt_federal", "indicators.clone_federal", "indicators.set_state_targets",
    "indicators.manage_state_thresholds", "indicators.view_state_results",
    "indicators.export_state_results", "indicators.ai_use_state",
]
EMPLOYER_INDICATOR_PERMISSIONS = [
    "indicators.view_employer", "indicators.view_branch_indicators",
    "indicators.export_employer_indicators", "indicators.ai_use_employer",
]
FACILITY_INDICATOR_PERMISSIONS = [
    "indicators.view_facility", "indicators.view_assessment_indicators",
    "indicators.export_facility_indicators", "indicators.ai_use_facility",
]
FINANCE_PERMISSIONS = ["payment.view", "settlement.view", "report.export", "organization.view"]
REPORTING_PERMISSIONS = ["report.export", "organization.view", "unit.view", "user.view"]


ROLE_TEMPLATES = [
    {
        "code": "federal_admin",
        "name": "Federal Admin",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": ADMIN_PERMISSIONS + ["organization.suspend", "report.export", "certificate.verify", "certificate.validate"] + FEDERAL_INDICATOR_PERMISSIONS,
    },
    {
        "code": "national_food_safety_programme_officer",
        "name": "National Food Safety Programme Officer",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": ["organization.view", "unit.view", "user.view", "certificate.verify", "inspection.assign", "report.export"],
    },
    {
        "code": "national_me_officer",
        "name": "National M&E Officer",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": REPORTING_PERMISSIONS + ["employer.view_compliance"] + FEDERAL_INDICATOR_PERMISSIONS,
    },
    {
        "code": "national_policy_officer",
        "name": "National Policy Officer",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": ["organization.view", "unit.view", "report.export"] + FEDERAL_INDICATOR_PERMISSIONS,
    },
    {
        "code": "national_finance_officer",
        "name": "National Finance/Oversight Officer",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": FINANCE_PERMISSIONS + ["user.view"],
    },
    {
        "code": "federal_viewer",
        "name": "Federal Viewer",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": VIEWER_PERMISSIONS + ["report.export"],
    },
    {
        "code": "executive_viewer",
        "name": "Executive Viewer",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": ["organization.view", "unit.view", "report.export", "employer.view_compliance"],
    },
    {
        "code": "national_programme_manager",
        "name": "National Programme Manager",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": [
            "organization.view", "unit.view", "user.view", "report.export",
            "certificate.verify", "employer.view_compliance", "audit_logs.view",
        ],
    },
    {
        "code": "director_department_head",
        "name": "Director / Department Head",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": [
            "organization.view", "unit.view", "user.view", "report.export",
            "certificate.verify", "employer.view_compliance", "audit_logs.view",
        ],
    },
    {
        "code": "policy_configuration_officer",
        "name": "Policy Configuration Officer",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": ["organization.view", "unit.view", "report.export"],
    },
    {
        "code": "standards_officer",
        "name": "Standards Officer",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": ["organization.view", "unit.view", "report.export"],
    },
    {
        "code": "legal_regulatory_reviewer",
        "name": "Legal / Regulatory Reviewer",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": ["organization.view", "unit.view", "report.export"],
    },
    {
        "code": "medical_clinical_reviewer",
        "name": "Medical / Clinical Reviewer",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": ["organization.view", "unit.view", "report.export", "medical_data.restricted_view"],
    },
    {
        "code": "data_analyst",
        "name": "Data Analyst",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": ["organization.view", "unit.view", "report.export", "employer.view_compliance", "indicators.view_federal", "indicators.view_cross_state_results", "indicators.ai_use_federal", "indicators.export_federal_results"],
    },
    {
        "code": "state_coordination_officer",
        "name": "State Coordination Officer",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": ["organization.view", "unit.view", "user.view", "report.export"],
    },
    {
        "code": "facility_oversight_officer",
        "name": "Facility Oversight Officer",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": ["organization.view", "unit.view", "report.export", "employer.view_compliance"],
    },
    {
        "code": "certificate_registry_officer",
        "name": "Certificate Registry Officer",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": ["organization.view", "unit.view", "certificate.verify", "certificate.validate", "report.export"],
    },
    {
        "code": "public_awareness_officer",
        "name": "Public Awareness Officer",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": ["organization.view", "unit.view", "report.export"],
    },
    {
        "code": "compliance_enforcement_officer",
        "name": "Compliance / Enforcement Officer",
        "organization_type": OrganizationType.FEDERAL_MINISTRY,
        "permissions": [
            "organization.view", "unit.view", "employer.view_compliance",
            "audit_logs.view", "certificate.verify", "report.export",
        ],
    },
    {
        "code": "state_admin",
        "name": "State Admin",
        "organization_type": OrganizationType.STATE_MINISTRY,
        "permissions": ADMIN_PERMISSIONS + [
            "facility.accredit",
            "certificate.verify",
            "certificate.validate",
            "inspection.assign",
            "state.fee.manage",
            "state.report.manage",
            "medical_data.restricted_view",
            "audit_logs.view",
            "report.export",
        ] + STATE_INDICATOR_PERMISSIONS,
    },
    {
        "code": "food_safety_directorate_officer",
        "name": "Food Safety Directorate Officer",
        "organization_type": OrganizationType.STATE_MINISTRY,
        "permissions": ["organization.view", "unit.view", "user.view", "employer.view_compliance", "inspection.assign", "report.export"],
    },
    {
        "code": "certificate_verification_officer",
        "name": "Certificate Verification Officer",
        "organization_type": OrganizationType.STATE_MINISTRY,
        "permissions": ["organization.view", "unit.view", "certificate.verify", "certificate.validate", "medical_data.restricted_view", "report.export"],
    },
    {
        "code": "facility_accreditation_officer",
        "name": "Facility Accreditation Officer",
        "organization_type": OrganizationType.STATE_MINISTRY,
        "permissions": ["organization.view", "unit.view", "facility.accredit", "facility.manage_department", "report.export"],
    },
    {
        "code": "policy_and_finance_officer",
        "name": "Policy and Finance Officer",
        "organization_type": OrganizationType.STATE_MINISTRY,
        "permissions": FINANCE_PERMISSIONS + ["organization.view", "unit.view", "state.fee.manage", "state.report.manage"],
    },
    {
        "code": "inspectorate_coordinator",
        "name": "Inspectorate Coordinator",
        "organization_type": OrganizationType.STATE_MINISTRY,
        "permissions": ["organization.view", "unit.view", "user.view", "inspection.assign", "inspection.conduct", "report.export"],
    },
    {
        "code": "inspector",
        "name": "Inspector / Environmental Health Officer",
        "organization_type": OrganizationType.STATE_MINISTRY,
        "permissions": ["organization.view", "unit.view", "inspection.conduct", "certificate.verify"],
    },
    {
        "code": "lga_office_officer",
        "name": "LGA Office Officer",
        "organization_type": OrganizationType.STATE_MINISTRY,
        "permissions": ["organization.view", "unit.view", "user.view", "certificate.verify", "inspection.conduct"],
    },
    {
        "code": "state_viewer",
        "name": "State Viewer",
        "organization_type": OrganizationType.STATE_MINISTRY,
        "permissions": VIEWER_PERMISSIONS + ["certificate.verify", "report.export"],
    },
    {
        "code": "facility_admin",
        "name": "Facility Admin",
        "organization_type": OrganizationType.MEDICAL_FACILITY,
        "permissions": ADMIN_PERMISSIONS + ["facility.manage_department", "facility.invite_staff", "certificate.verify", "report.export"] + FACILITY_INDICATOR_PERMISSIONS,
    },
    {
        "code": "doctor",
        "name": "Doctor",
        "organization_type": OrganizationType.MEDICAL_FACILITY,
        "permissions": ["organization.view", "unit.view", "certificate.verify", "report.export"],
    },
    {
        "code": "lab_staff",
        "name": "Lab Staff",
        "organization_type": OrganizationType.MEDICAL_FACILITY,
        "permissions": ["organization.view", "unit.view", "certificate.verify"],
    },
    {
        "code": "medical_records_staff",
        "name": "Medical Records Staff",
        "organization_type": OrganizationType.MEDICAL_FACILITY,
        "permissions": ["organization.view", "unit.view", "certificate.verify", "report.export"],
    },
    {
        "code": "medical_facility_finance_user",
        "name": "Finance / Settlement User",
        "organization_type": OrganizationType.MEDICAL_FACILITY,
        "permissions": FINANCE_PERMISSIONS,
    },
    {
        "code": "facility_viewer",
        "name": "Facility Viewer",
        "organization_type": OrganizationType.MEDICAL_FACILITY,
        "permissions": VIEWER_PERMISSIONS + ["certificate.verify"],
    },
    {
        "code": "employer",
        "name": "Employer Admin / Business Owner",
        "organization_type": OrganizationType.EMPLOYER,
        "permissions": ADMIN_PERMISSIONS + ["employer.manage_branch", "employer.view_compliance", "certificate.verify", "report.export"] + EMPLOYER_INDICATOR_PERMISSIONS,
    },
    {
        "code": "compliance_officer",
        "name": "Compliance Officer",
        "organization_type": OrganizationType.EMPLOYER,
        "permissions": ["organization.view", "unit.view", "user.view", "employer.view_compliance", "certificate.verify", "report.export"],
    },
    {
        "code": "branch_manager",
        "name": "Branch Manager",
        "organization_type": OrganizationType.EMPLOYER,
        "permissions": ["organization.view", "unit.view", "unit.view_members", "user.view", "user.invite", "employer.view_compliance", "certificate.verify"],
    },
    {
        "code": "employer_finance_user",
        "name": "Finance User",
        "organization_type": OrganizationType.EMPLOYER,
        "permissions": FINANCE_PERMISSIONS,
    },
    {
        "code": "employer_viewer",
        "name": "Employer Viewer",
        "organization_type": OrganizationType.EMPLOYER,
        "permissions": VIEWER_PERMISSIONS + ["employer.view_compliance", "certificate.verify"],
    },
    {
        "code": "super_admin",
        "name": "Super Admin",
        "organization_type": OrganizationType.PLATFORM_OPERATOR,
        "permissions": [permission["code"] for permission in PERMISSIONS],
    },
    {
        "code": "platform_admin",
        "name": "Platform Admin",
        "organization_type": OrganizationType.PLATFORM_OPERATOR,
        "permissions": [permission["code"] for permission in PERMISSIONS if permission["code"] != "permission.override"],
    },
    {
        "code": "support_agent",
        "name": "Support Agent",
        "organization_type": OrganizationType.PLATFORM_OPERATOR,
        "permissions": ["organization.view", "unit.view", "user.view", "invite.view", "certificate.verify"],
    },
    {
        "code": "finance_operator",
        "name": "Finance Operator",
        "organization_type": OrganizationType.PLATFORM_OPERATOR,
        "permissions": FINANCE_PERMISSIONS + ["organization.view", "user.view"],
    },
    {
        "code": "compliance_operator",
        "name": "Compliance Operator",
        "organization_type": OrganizationType.PLATFORM_OPERATOR,
        "permissions": ["organization.view", "unit.view", "user.view", "employer.view_compliance", "inspection.assign", "inspection.conduct", "report.export"],
    },
    {
        "code": "technical_operator",
        "name": "Technical Operator",
        "organization_type": OrganizationType.PLATFORM_OPERATOR,
        "permissions": ["organization.view", "unit.view", "user.view", "role.view", "permission.view"],
    },
    {
        "code": "auditor",
        "name": "Auditor",
        "organization_type": OrganizationType.PLATFORM_OPERATOR,
        "permissions": ["organization.view", "unit.view", "user.view", "invite.view", "role.view", "permission.view", "report.export"],
    },
]


class Command(BaseCommand):
    help = "Seed stakeholder role templates, permissions, and role-permission mappings."

    @transaction.atomic
    def handle(self, *args, **options):
        permissions_by_code = {}
        created_permissions = 0
        updated_permissions = 0
        for definition in PERMISSIONS:
            permission, created = Permission.objects.update_or_create(
                code=definition["code"],
                defaults={
                    "name": definition["name"],
                    "module": definition["module"],
                    "description": definition.get("description", ""),
                    "is_sensitive": definition.get("is_sensitive", False),
                },
            )
            permissions_by_code[permission.code] = permission
            created_permissions += int(created)
            updated_permissions += int(not created)

        created_roles = 0
        updated_roles = 0
        role_permission_count = 0
        for definition in ROLE_TEMPLATES:
            role, created = Role.objects.update_or_create(
                code=definition["code"],
                defaults={
                    "name": definition["name"],
                    "organization_type": definition["organization_type"],
                    "description": definition.get("description", f"System role template for {definition['name']}."),
                    "is_system_role": True,
                    "is_custom_role": False,
                    "status": RoleStatus.ACTIVE,
                },
            )
            created_roles += int(created)
            updated_roles += int(not created)
            for permission_code in definition["permissions"]:
                RolePermission.objects.get_or_create(
                    role=role,
                    permission=permissions_by_code[permission_code],
                )
            role_permission_count += role.role_permissions.count()

        if options.get("verbosity", 1) > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "Seeded stakeholder roles and permissions: "
                    f"{created_permissions} permissions created, {updated_permissions} permissions updated, "
                    f"{created_roles} roles created, {updated_roles} roles updated, "
                    f"{role_permission_count} role-permission links active."
                )
            )
