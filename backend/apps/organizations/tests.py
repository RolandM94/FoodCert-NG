from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError, transaction
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.audit.models import AuditLog
from apps.locations.models import State, LGA
from apps.organizations.models import (
    MembershipStatus,
    Organization,
    OrganizationMembership,
    OrganizationStatus,
    OrganizationType,
    OrganizationUnit,
    OrganizationUnitStatus,
    OrganizationUnitType,
    Permission,
    PermissionOverride,
    PermissionOverrideEffect,
    Role,
    RolePermission,
)
from apps.organizations.permission_codes import PERMISSION_CODES
from apps.organizations.services_access import EffectiveAccessService

User = get_user_model()


def data(response):
    return response.data.get("data", response.data)


class StakeholderFoundationModelTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.creator = User.objects.create_user(
            username="creator",
            email="creator@example.com",
            password="StrongPass123!",
            role=UserRole.SUPER_ADMIN,
        )
        self.parent_org = Organization.objects.create(
            name="Federal MOH",
            organization_type=OrganizationType.FEDERAL_MINISTRY,
            status=OrganizationStatus.ACTIVE,
            created_by=self.creator,
        )
        self.org = Organization.objects.create(
            parent=self.parent_org,
            name="Lagos MOH",
            organization_type=OrganizationType.STATE_MINISTRY,
            status=OrganizationStatus.DRAFT,
            state=self.state,
            contact_person_name="State Coordinator",
            website="https://lagosmoh.example.com",
            created_by=self.creator,
        )
        self.unit = OrganizationUnit.objects.create(
            organization=self.org,
            name="Food Safety Desk",
            unit_type=OrganizationUnitType.DESK,
            status=OrganizationUnitStatus.ACTIVE,
            manager=self.creator,
            created_by=self.creator,
        )
        self.member_user = User.objects.create_user(
            username="member",
            email="member@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            organization=self.org,
            unit=self.unit,
            unit_restricted=True,
        )

    def test_organization_and_unit_prd_foundation_fields_are_available(self):
        self.assertEqual(self.org.parent, self.parent_org)
        self.assertEqual(self.org.status, OrganizationStatus.DRAFT)
        self.assertEqual(self.org.contact_person_name, "State Coordinator")
        self.assertEqual(self.org.website, "https://lagosmoh.example.com")
        self.assertEqual(self.org.created_by, self.creator)
        self.assertEqual(self.unit.status, OrganizationUnitStatus.ACTIVE)
        self.assertEqual(self.unit.manager, self.creator)
        self.assertEqual(self.unit.created_by, self.creator)

    def test_role_permission_and_override_constraints(self):
        role = Role.objects.create(
            name="State Viewer",
            code="state_viewer_test",
            organization_type=OrganizationType.STATE_MINISTRY,
        )
        permission = Permission.objects.create(
            code="organization.view.test",
            name="View Organization",
            module="organization",
        )
        RolePermission.objects.create(role=role, permission=permission)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                RolePermission.objects.create(role=role, permission=permission)

        membership = OrganizationMembership.objects.create(
            user=self.member_user,
            organization=self.org,
            role=role,
            unit=self.unit,
            unit_restricted=True,
            status=MembershipStatus.ACTIVE,
        )
        override = PermissionOverride.objects.create(
            membership=membership,
            permission=permission,
            effect=PermissionOverrideEffect.ALLOW,
            reason="Temporary support coverage.",
            granted_by=self.creator,
        )
        self.assertEqual(override.effect, PermissionOverrideEffect.ALLOW)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PermissionOverride.objects.create(
                    membership=membership,
                    permission=permission,
                    effect=PermissionOverrideEffect.DENY,
                )

    def test_only_one_active_membership_per_user_and_organization(self):
        role = Role.objects.get(code=UserRole.STATE_ADMIN)
        OrganizationMembership.objects.create(
            user=self.member_user,
            organization=self.org,
            role=role,
            status=MembershipStatus.ACTIVE,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                OrganizationMembership.objects.create(
                    user=self.member_user,
                    organization=self.org,
                    role=role,
                    status=MembershipStatus.ACTIVE,
                )
        suspended = OrganizationMembership.objects.create(
            user=self.member_user,
            organization=self.org,
            role=role,
            status=MembershipStatus.SUSPENDED,
        )
        self.assertEqual(suspended.status, MembershipStatus.SUSPENDED)

    def test_user_compatibility_properties_prefer_active_membership(self):
        role = Role.objects.get(code=UserRole.STATE_ADMIN)
        membership = OrganizationMembership.objects.create(
            user=self.member_user,
            organization=self.org,
            role=role,
            unit=self.unit,
            unit_restricted=True,
            status=MembershipStatus.ACTIVE,
        )
        self.assertEqual(self.member_user.current_membership, membership)
        self.assertEqual(self.member_user.current_organization, self.org)
        self.assertEqual(self.member_user.current_role, role)
        self.assertEqual(self.member_user.current_unit, self.unit)
        self.assertTrue(self.member_user.is_unit_restricted)

    def test_user_without_org_does_not_get_membership(self):
        user = User.objects.create_user(
            username="floating",
            email="floating@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
        )
        self.assertFalse(user.memberships.exists())
        self.assertIsNone(user.current_membership)

    def test_legacy_roles_are_seeded_for_compatibility(self):
        for role_code in UserRole.values:
            self.assertTrue(Role.objects.filter(code=role_code, status="active", is_system_role=True).exists())


class StakeholderRoleSeedCommandTests(APITestCase):
    def test_seed_command_creates_permissions_role_templates_and_links(self):
        call_command("seed_roles_and_permissions", verbosity=0)

        self.assertEqual(Permission.objects.count(), len(PERMISSION_CODES))
        self.assertTrue(Permission.objects.filter(code="permission.override", is_sensitive=True).exists())
        self.assertEqual(Role.objects.filter(is_system_role=True, status="active").count(), 35)
        self.assertTrue(Role.objects.filter(code="federal_admin", organization_type=OrganizationType.FEDERAL_MINISTRY).exists())
        self.assertTrue(Role.objects.filter(code="state_admin", organization_type=OrganizationType.STATE_MINISTRY).exists())
        self.assertTrue(Role.objects.filter(code="facility_admin", organization_type=OrganizationType.MEDICAL_FACILITY).exists())
        self.assertTrue(Role.objects.filter(code="employer", organization_type=OrganizationType.EMPLOYER).exists())
        self.assertTrue(Role.objects.filter(code="super_admin", organization_type=OrganizationType.PLATFORM_OPERATOR).exists())

        super_admin = Role.objects.get(code="super_admin")
        state_admin = Role.objects.get(code="state_admin")
        branch_manager = Role.objects.get(code="branch_manager")
        self.assertEqual(super_admin.role_permissions.count(), len(PERMISSION_CODES))
        self.assertTrue(state_admin.role_permissions.filter(permission__code="facility.accredit").exists())
        self.assertTrue(branch_manager.role_permissions.filter(permission__code="employer.view_compliance").exists())
        self.assertFalse(branch_manager.role_permissions.filter(permission__code="permission.override").exists())

    def test_seed_command_is_idempotent(self):
        call_command("seed_roles_and_permissions", verbosity=0)
        counts = {
            "permissions": Permission.objects.count(),
            "roles": Role.objects.count(),
            "role_permissions": RolePermission.objects.count(),
        }

        call_command("seed_roles_and_permissions", verbosity=0)

        self.assertEqual(Permission.objects.count(), counts["permissions"])
        self.assertEqual(Role.objects.count(), counts["roles"])
        self.assertEqual(RolePermission.objects.count(), counts["role_permissions"])


class OrganizationMembershipApiTests(APITestCase):
    def setUp(self):
        call_command("seed_roles_and_permissions", verbosity=0)
        self.state = State.objects.create(name="Lagos", code="LA")
        self.org = Organization.objects.create(
            name="MegaChow",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
        )
        self.branch = OrganizationUnit.objects.create(
            organization=self.org,
            name="Ikeja Branch",
            unit_type=OrganizationUnitType.BRANCH,
        )
        self.other_branch = OrganizationUnit.objects.create(
            organization=self.org,
            name="Surulere Branch",
            unit_type=OrganizationUnitType.BRANCH,
        )
        self.super_admin = User.objects.create_user(
            username="membership-super",
            email="membership-super@example.com",
            password="StrongPass123!",
            role=UserRole.SUPER_ADMIN,
        )
        self.target_user = User.objects.create_user(
            username="membership-user",
            email="membership-user@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
        )
        self.employer_role = Role.objects.get(code="employer")
        self.branch_manager_role = Role.objects.get(code="branch_manager")

    def create_membership(self):
        self.client.force_authenticate(self.super_admin)
        response = self.client.post(
            f"/api/organizations/{self.org.id}/memberships/",
            {
                "user": str(self.target_user.id),
                "role": str(self.employer_role.id),
                "unit": str(self.branch.id),
                "unit_restricted": False,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        return OrganizationMembership.objects.get(id=data(response)["id"])

    def test_create_list_detail_and_me_include_membership_and_permissions(self):
        membership = self.create_membership()
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.organization, self.org)
        self.assertEqual(self.target_user.unit, self.branch)
        self.assertEqual(self.target_user.role, UserRole.EMPLOYER)

        list_response = self.client.get(f"/api/organizations/{self.org.id}/memberships/")
        self.assertEqual(list_response.status_code, 200, list_response.data)
        self.assertEqual(data(list_response)[0]["user_email"], "membership-user@example.com")
        self.assertEqual(data(list_response)[0]["role_code"], "employer")

        detail = self.client.get(f"/api/organizations/{self.org.id}/memberships/{membership.id}/")
        self.assertEqual(detail.status_code, 200, detail.data)
        self.assertIn("employer.manage_branch", data(detail)["permissions"])
        self.assertTrue(data(detail)["audit_log"])

        self.client.force_authenticate(self.target_user)
        me = self.client.get("/api/users/me/")
        self.assertEqual(me.status_code, 200, me.data)
        self.assertEqual(data(me)["current_membership"]["role_code"], "employer")
        self.assertIn("employer.manage_branch", data(me)["effective_permissions"])

    def test_membership_lifecycle_actions_sync_compat_user_fields_and_audit(self):
        membership = self.create_membership()

        changed_role = self.client.patch(
            f"/api/organizations/{self.org.id}/memberships/{membership.id}/change-role/",
            {"role": str(self.branch_manager_role.id)},
            format="json",
        )
        self.assertEqual(changed_role.status_code, 200, changed_role.data)
        self.assertEqual(data(changed_role)["role_code"], "branch_manager")

        changed_unit = self.client.patch(
            f"/api/organizations/{self.org.id}/memberships/{membership.id}/change-unit/",
            {"unit": str(self.other_branch.id), "unit_restricted": True},
            format="json",
        )
        self.assertEqual(changed_unit.status_code, 200, changed_unit.data)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.unit, self.other_branch)
        self.assertTrue(self.target_user.unit_restricted)

        toggled = self.client.patch(f"/api/organizations/{self.org.id}/memberships/{membership.id}/toggle-unit-restriction/", format="json")
        self.assertEqual(toggled.status_code, 200, toggled.data)
        self.assertFalse(data(toggled)["unit_restricted"])

        suspended = self.client.patch(f"/api/organizations/{self.org.id}/memberships/{membership.id}/suspend/", format="json")
        self.assertEqual(suspended.status_code, 200, suspended.data)
        self.assertEqual(data(suspended)["status"], MembershipStatus.SUSPENDED)
        self.target_user.refresh_from_db()
        self.assertIsNone(self.target_user.organization)

        reactivated = self.client.patch(f"/api/organizations/{self.org.id}/memberships/{membership.id}/reactivate/", format="json")
        self.assertEqual(reactivated.status_code, 200, reactivated.data)
        self.assertEqual(data(reactivated)["status"], MembershipStatus.ACTIVE)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.organization, self.org)

        removed = self.client.patch(f"/api/organizations/{self.org.id}/memberships/{membership.id}/remove/", format="json")
        self.assertEqual(removed.status_code, 200, removed.data)
        self.assertEqual(data(removed)["status"], MembershipStatus.REMOVED)
        self.assertTrue(
            AuditLog.objects.filter(
                target_id=str(membership.id),
                metadata__event="membership_removed",
            ).exists()
        )

    def test_rejects_duplicate_active_membership_and_wrong_org_unit(self):
        membership = self.create_membership()
        duplicate = self.client.post(
            f"/api/organizations/{self.org.id}/memberships/",
            {"user": str(self.target_user.id), "role": str(self.employer_role.id)},
            format="json",
        )
        self.assertEqual(duplicate.status_code, 400)

        other_org = Organization.objects.create(name="Other Employer", organization_type=OrganizationType.EMPLOYER, state=self.state)
        other_unit = OrganizationUnit.objects.create(organization=other_org, name="Other Branch", unit_type=OrganizationUnitType.BRANCH)
        invalid_unit = self.client.patch(
            f"/api/organizations/{self.org.id}/memberships/{membership.id}/change-unit/",
            {"unit": str(other_unit.id), "unit_restricted": True},
            format="json",
        )
        self.assertEqual(invalid_unit.status_code, 400)


class EffectiveAccessServiceTests(APITestCase):
    def setUp(self):
        call_command("seed_roles_and_permissions", verbosity=0)
        self.state = State.objects.create(name="Lagos", code="LA")
        self.org = Organization.objects.create(
            name="MegaChow",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
        )
        self.branch = OrganizationUnit.objects.create(
            organization=self.org,
            name="Ikeja Branch",
            unit_type=OrganizationUnitType.BRANCH,
        )
        self.user = User.objects.create_user(
            username="access-user",
            email="access-user@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
        )
        self.super_admin = User.objects.create_user(
            username="access-super",
            email="access-super@example.com",
            password="StrongPass123!",
            role=UserRole.SUPER_ADMIN,
        )
        self.role = Role.objects.get(code="branch_manager")
        self.membership = OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org,
            role=self.role,
            unit=self.branch,
            unit_restricted=True,
            status=MembershipStatus.ACTIVE,
        )
        self.service = EffectiveAccessService()

    def test_role_permissions_and_scope_are_resolved_from_active_membership(self):
        result = self.service.check(self.user, "employer.view_compliance", organization=self.org)

        self.assertTrue(result.allowed)
        self.assertEqual(result.scope, "unit")
        self.assertEqual(result.unit_id, str(self.branch.id))
        self.assertEqual(result.filters["unit_id"], str(self.branch.id))
        self.assertEqual(result.role_code, "branch_manager")

    def test_permission_override_can_deny_or_allow(self):
        permission = Permission.objects.get(code="employer.view_compliance")
        PermissionOverride.objects.create(
            membership=self.membership,
            permission=permission,
            effect=PermissionOverrideEffect.DENY,
            granted_by=self.super_admin,
        )

        denied = self.service.check(self.user, "employer.view_compliance", organization=self.org)

        self.assertFalse(denied.allowed)
        self.assertEqual(denied.reason, "Denied by permission override.")

        PermissionOverride.objects.filter(membership=self.membership, permission=permission).update(effect=PermissionOverrideEffect.ALLOW)
        allowed = self.service.check(self.user, "employer.view_compliance", organization=self.org)

        self.assertTrue(allowed.allowed)
        self.assertEqual(allowed.reason, "Allowed by permission override.")

    def test_missing_membership_and_missing_permission_are_denied(self):
        no_membership_user = User.objects.create_user(
            username="no-membership",
            email="no-membership@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
        )

        no_membership = self.service.check(no_membership_user, "employer.view_compliance", organization=self.org)
        missing_permission = self.service.check(self.user, "permission.override", organization=self.org)

        self.assertFalse(no_membership.allowed)
        self.assertEqual(no_membership.reason, "No active organization membership found.")
        self.assertFalse(missing_permission.allowed)
        self.assertEqual(missing_permission.reason, "Role does not include this permission.")

    def test_super_admin_gets_global_access(self):
        result = self.service.check(self.super_admin, "permission.override")

        self.assertTrue(result.allowed)
        self.assertEqual(result.scope, "global")

    def test_effective_access_endpoints(self):
        self.client.force_authenticate(self.user)

        memberships = self.client.get("/api/me/memberships/")
        self.assertEqual(memberships.status_code, 200, memberships.data)
        self.assertEqual(memberships.data[0]["role_code"], "branch_manager")

        permissions = self.client.get(f"/api/me/effective-permissions/?organization_id={self.org.id}")
        self.assertEqual(permissions.status_code, 200, permissions.data)
        self.assertIn("employer.view_compliance", data(permissions)["permissions"])

        check = self.client.post(
            "/api/permissions/check/",
            {"permission_code": "employer.view_compliance", "organization_id": str(self.org.id)},
            format="json",
        )
        self.assertEqual(check.status_code, 200, check.data)
        self.assertTrue(data(check)["allowed"])
        self.assertEqual(data(check)["scope"], "unit")


class RolePermissionManagementApiTests(APITestCase):
    def setUp(self):
        call_command("seed_roles_and_permissions", verbosity=0)
        self.super_admin = User.objects.create_user(
            username="role-super",
            email="role-super@example.com",
            password="StrongPass123!",
            role=UserRole.SUPER_ADMIN,
        )
        self.state_admin = User.objects.create_user(
            username="role-state",
            email="role-state@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
        )
        self.permission = Permission.objects.get(code="organization.view")

    def test_roles_permissions_and_org_type_role_lists_are_available(self):
        self.client.force_authenticate(self.super_admin)

        roles = self.client.get("/api/roles/?organization_type=state_ministry")
        self.assertEqual(roles.status_code, 200, roles.data)
        self.assertTrue(any(role["code"] == "state_admin" for role in data(roles)))
        self.assertIn("permission_count", data(roles)[0])

        type_roles = self.client.get("/api/organization-types/state_ministry/roles/")
        self.assertEqual(type_roles.status_code, 200, type_roles.data)
        self.assertTrue(all(role["organization_type"] == OrganizationType.STATE_MINISTRY for role in data(type_roles)))

        permissions = self.client.get("/api/permissions/?module=organization")
        self.assertEqual(permissions.status_code, 200, permissions.data)
        self.assertTrue(any(permission["code"] == "organization.view" for permission in data(permissions)))

    def test_super_admin_can_create_update_and_manage_custom_role_permissions(self):
        self.client.force_authenticate(self.super_admin)

        created = self.client.post(
            "/api/roles/",
            {
                "name": "State Custom Reviewer",
                "code": "state_custom_reviewer",
                "organization_type": OrganizationType.STATE_MINISTRY,
                "description": "Reviews state submissions.",
                "status": "active",
            },
            format="json",
        )
        self.assertEqual(created.status_code, 201, created.data)
        role_id = data(created)["id"]
        self.assertTrue(data(created)["is_custom_role"])

        updated = self.client.patch(
            f"/api/roles/{role_id}/",
            {"name": "State Submission Reviewer", "description": "Reviews submitted state records."},
            format="json",
        )
        self.assertEqual(updated.status_code, 200, updated.data)
        self.assertEqual(data(updated)["name"], "State Submission Reviewer")

        added = self.client.post(
            f"/api/roles/{role_id}/permissions/",
            {"permission": str(self.permission.id)},
            format="json",
        )
        self.assertEqual(added.status_code, 201, added.data)
        self.assertTrue(any(permission["code"] == "organization.view" for permission in data(added)["permissions"]))

        listed = self.client.get(f"/api/roles/{role_id}/permissions/")
        self.assertEqual(listed.status_code, 200, listed.data)
        self.assertTrue(any(permission["code"] == "organization.view" for permission in listed.data))

        removed = self.client.delete(f"/api/roles/{role_id}/permissions/{self.permission.id}/")
        self.assertEqual(removed.status_code, 204, removed.data)
        self.assertFalse(RolePermission.objects.filter(role_id=role_id, permission=self.permission).exists())

    def test_non_super_admin_cannot_create_custom_roles(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(
            "/api/roles/",
            {
                "name": "Blocked Role",
                "code": "blocked_role",
                "organization_type": OrganizationType.STATE_MINISTRY,
                "status": "active",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)


class OrganizationUnitCRUDTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.lga = LGA.objects.create(name="Ikeja", state=self.state)
        self.org = Organization.objects.create(
            name="Lagos MOH",
            organization_type=OrganizationType.STATE_MINISTRY,
            state=self.state,
        )
        self.super_admin = User.objects.create_user(
            username="super",
            email="super@example.com",
            password="StrongPass123!",
            role=UserRole.SUPER_ADMIN,
        )
        self.state_admin = User.objects.create_user(
            username="lagos-admin",
            email="lagos-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.state,
            organization=self.org,
        )
        self.other_state = State.objects.create(name="Oyo", code="OY")
        self.other_admin = User.objects.create_user(
            username="oyo-admin",
            email="oyo-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.other_state,
        )

    def test_state_admin_can_create_unit_in_own_state_org(self):
        self.client.force_authenticate(self.state_admin)
        response = self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {"name": "Food Safety Directorate", "unit_type": OrganizationUnitType.DIRECTORATE},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data(response)["name"], "Food Safety Directorate")
        self.assertEqual(data(response)["status"], OrganizationUnitStatus.ACTIVE)

    def test_state_admin_cannot_create_unit_in_other_state_org(self):
        self.client.force_authenticate(self.other_admin)
        response = self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {"name": "Bad Unit", "unit_type": OrganizationUnitType.UNIT},
            format="json",
        )
        code = response.data.get("code", response.data.get("detail", ""))
        self.assertIn(response.status_code, [403, 404])
        self.assertTrue(
            "PERMISSION_DENIED" in str(code) or "not found" in str(code).lower() or "403" in str(response.status_code)
        )

    def test_super_admin_can_create_unit_anywhere(self):
        self.client.force_authenticate(self.super_admin)
        response = self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {"name": "Verification Desk", "unit_type": OrganizationUnitType.UNIT},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_other_state_admin_sees_empty_unit_list(self):
        unit = OrganizationUnit.objects.create(
            organization=self.org,
            name="Food Safety",
            unit_type=OrganizationUnitType.DIRECTORATE,
        )
        self.client.force_authenticate(self.other_admin)
        response = self.client.get(f"/api/organizations/{self.org.id}/units/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data(response)), 0)

    def test_state_admin_sees_units_in_own_state(self):
        OrganizationUnit.objects.create(
            organization=self.org,
            name="Food Safety",
            unit_type=OrganizationUnitType.DIRECTORATE,
        )
        self.client.force_authenticate(self.state_admin)
        response = self.client.get(f"/api/organizations/{self.org.id}/units/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data(response)), 1)


class OrganizationUnitNestingTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.org = Organization.objects.create(
            name="Lagos MOH",
            organization_type=OrganizationType.STATE_MINISTRY,
            state=self.state,
        )
        self.super_admin = User.objects.create_user(
            username="super",
            email="super@example.com",
            password="StrongPass123!",
            role=UserRole.SUPER_ADMIN,
        )
        self.state_admin = User.objects.create_user(
            username="lagos-admin",
            email="lagos-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.state,
            organization=self.org,
        )

    def test_create_nested_unit_tree(self):
        self.client.force_authenticate(self.state_admin)
        d1 = self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {"name": "Food Safety Directorate", "unit_type": OrganizationUnitType.DIRECTORATE},
            format="json",
        )
        self.assertEqual(d1.status_code, 201)
        unit1_id = data(d1)["id"]

        d2 = self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {"name": "Inspectorate", "unit_type": OrganizationUnitType.DEPARTMENT, "parent": unit1_id},
            format="json",
        )
        self.assertEqual(d2.status_code, 201)
        unit2_id = data(d2)["id"]

        d3 = self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {"name": "Ikeja LGA Office", "unit_type": OrganizationUnitType.UNIT, "parent": unit2_id},
            format="json",
        )
        self.assertEqual(d3.status_code, 201)
        self.assertEqual(f"{data(d3)['parent']}", f"{unit2_id}")
        self.assertEqual(data(d3)["parent_name"], "Inspectorate")

    def test_nesting_exceeds_max_depth_rejected(self):
        self.client.force_authenticate(self.state_admin)
        r1 = self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {"name": "Level 1", "unit_type": OrganizationUnitType.DIRECTORATE},
            format="json",
        )
        self.assertEqual(r1.status_code, 201)
        id1 = data(r1)["id"]

        r2 = self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {"name": "Level 2", "unit_type": OrganizationUnitType.DEPARTMENT, "parent": id1},
            format="json",
        )
        self.assertEqual(r2.status_code, 201)
        id2 = data(r2)["id"]

        # Level 3 (depth 3) is the max allowed
        r3 = self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {"name": "Level 3", "unit_type": OrganizationUnitType.UNIT, "parent": id2},
            format="json",
        )
        self.assertEqual(r3.status_code, 201)
        id3 = data(r3)["id"]

        # Level 4 should be rejected (exceeds max 3)
        r4 = self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {"name": "Level 4 Should Fail", "unit_type": OrganizationUnitType.UNIT, "parent": id3},
            format="json",
        )
        self.assertEqual(r4.status_code, 400)

    def test_parent_must_belong_to_same_organization(self):
        self.client.force_authenticate(self.state_admin)
        other_org = Organization.objects.create(
            name="Other Org",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
        )
        other_unit = OrganizationUnit.objects.create(
            organization=other_org,
            name="Other Unit",
            unit_type=OrganizationUnitType.UNIT,
        )
        response = self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {"name": "Bad Parent", "unit_type": OrganizationUnitType.UNIT, "parent": str(other_unit.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 400)


class OrganizationApiRefactorTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.other_state = State.objects.create(name="Oyo", code="OY")
        self.parent = Organization.objects.create(
            name="Federal MOH",
            organization_type=OrganizationType.FEDERAL_MINISTRY,
            status=OrganizationStatus.ACTIVE,
        )
        self.org = Organization.objects.create(
            parent=self.parent,
            name="Lagos MOH",
            organization_type=OrganizationType.STATE_MINISTRY,
            status=OrganizationStatus.ACTIVE,
            state=self.state,
            contact_person_name="State Coordinator",
            website="https://lagos.example.com",
        )
        Organization.objects.create(
            name="Oyo MOH",
            organization_type=OrganizationType.STATE_MINISTRY,
            status=OrganizationStatus.SUSPENDED,
            state=self.other_state,
        )
        self.super_admin = User.objects.create_user(
            username="super-org",
            email="super-org@example.com",
            password="StrongPass123!",
            role=UserRole.SUPER_ADMIN,
        )
        self.state_admin = User.objects.create_user(
            username="lagos-org-admin",
            email="lagos-org-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.state,
            organization=self.org,
        )

    def test_organization_list_filters_and_counts(self):
        OrganizationUnit.objects.create(organization=self.org, name="Food Safety", unit_type=OrganizationUnitType.DIRECTORATE)
        role = Role.objects.get(code=UserRole.STATE_ADMIN)
        OrganizationMembership.objects.create(user=self.state_admin, organization=self.org, role=role, status=MembershipStatus.ACTIVE)
        self.client.force_authenticate(self.super_admin)

        response = self.client.get(f"/api/organizations/?status=active&organization_type={OrganizationType.STATE_MINISTRY}&state={self.state.id}")

        self.assertEqual(response.status_code, 200, response.data)
        items = data(response)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["parent_name"], "Federal MOH")
        self.assertEqual(items[0]["contact_person_name"], "State Coordinator")
        self.assertEqual(items[0]["website"], "https://lagos.example.com")
        self.assertEqual(items[0]["unit_count"], 1)
        self.assertEqual(items[0]["membership_count"], 1)

    def test_suspend_and_reactivate_organization_actions(self):
        self.client.force_authenticate(self.super_admin)
        suspended = self.client.post(f"/api/organizations/{self.org.id}/suspend/", format="json")
        self.assertEqual(suspended.status_code, 200, suspended.data)
        self.assertEqual(data(suspended)["status"], OrganizationStatus.SUSPENDED)

        reactivated = self.client.post(f"/api/organizations/{self.org.id}/reactivate/", format="json")
        self.assertEqual(reactivated.status_code, 200, reactivated.data)
        self.assertEqual(data(reactivated)["status"], OrganizationStatus.ACTIVE)

    def test_archived_organization_cannot_patch_directly_to_active(self):
        self.org.status = OrganizationStatus.ARCHIVED
        self.org.save(update_fields=["status", "updated_at"])
        self.client.force_authenticate(self.super_admin)

        response = self.client.patch(f"/api/organizations/{self.org.id}/", {"status": OrganizationStatus.ACTIVE}, format="json")

        self.assertEqual(response.status_code, 400)


class OrganizationUnitApiRefactorTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.state_org = Organization.objects.create(
            name="Lagos MOH",
            organization_type=OrganizationType.STATE_MINISTRY,
            state=self.state,
        )
        self.employer_org = Organization.objects.create(
            name="MegaChow",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
        )
        self.admin = User.objects.create_user(
            username="unit-admin",
            email="unit-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.state,
            organization=self.state_org,
        )
        self.employer = User.objects.create_user(
            username="unit-employer",
            email="unit-employer@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
        )

    def test_unit_type_compatibility_is_enforced(self):
        self.client.force_authenticate(self.employer)
        invalid = self.client.post(
            f"/api/organizations/{self.employer_org.id}/units/",
            {"name": "Ikeja LGA", "unit_type": OrganizationUnitType.LGA_OFFICE},
            format="json",
        )
        self.assertEqual(invalid.status_code, 400)

        valid = self.client.post(
            f"/api/organizations/{self.employer_org.id}/units/",
            {"name": "Ikeja Branch", "unit_type": OrganizationUnitType.BRANCH},
            format="json",
        )
        self.assertEqual(valid.status_code, 201, valid.data)

    def test_unit_tree_members_assign_and_status_actions(self):
        role = Role.objects.get(code=UserRole.STATE_ADMIN)
        parent = OrganizationUnit.objects.create(
            organization=self.state_org,
            name="Food Safety Directorate",
            unit_type=OrganizationUnitType.DIRECTORATE,
        )
        child = OrganizationUnit.objects.create(
            organization=self.state_org,
            name="Verification Desk",
            unit_type=OrganizationUnitType.DESK,
            parent=parent,
        )
        member = User.objects.create_user(
            username="desk-member",
            email="desk-member@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            organization=self.state_org,
        )
        OrganizationMembership.objects.create(
            user=member,
            organization=self.state_org,
            role=role,
            status=MembershipStatus.ACTIVE,
        )
        self.client.force_authenticate(self.admin)

        assigned = self.client.post(
            f"/api/organizations/{self.state_org.id}/units/{child.id}/assign-user/",
            {"user": str(member.id), "unit_restricted": True},
            format="json",
        )
        self.assertEqual(assigned.status_code, 200, assigned.data)
        member.refresh_from_db()
        self.assertEqual(member.unit, child)
        self.assertTrue(member.unit_restricted)
        self.assertEqual(member.current_membership.unit, child)

        members = self.client.get(f"/api/organizations/{self.state_org.id}/units/{child.id}/members/")
        self.assertEqual(members.status_code, 200, members.data)
        self.assertEqual(len(members.data), 1)
        self.assertEqual(members.data[0]["email"], "desk-member@example.com")

        tree = self.client.get(f"/api/organizations/{self.state_org.id}/units/tree/")
        self.assertEqual(tree.status_code, 200, tree.data)
        self.assertEqual(tree.data[0]["children"][0]["name"], "Verification Desk")

        deactivated = self.client.post(f"/api/organizations/{self.state_org.id}/units/{child.id}/deactivate/", format="json")
        self.assertEqual(deactivated.status_code, 200, deactivated.data)
        self.assertEqual(data(deactivated)["status"], OrganizationUnitStatus.INACTIVE)
        self.assertFalse(data(deactivated)["is_active"])

        reactivated = self.client.post(f"/api/organizations/{self.state_org.id}/units/{child.id}/reactivate/", format="json")
        self.assertEqual(reactivated.status_code, 200, reactivated.data)
        self.assertEqual(data(reactivated)["status"], OrganizationUnitStatus.ACTIVE)
        self.assertTrue(data(reactivated)["is_active"])

        archived = self.client.post(f"/api/organizations/{self.state_org.id}/units/{child.id}/archive/", format="json")
        self.assertEqual(archived.status_code, 200, archived.data)
        self.assertEqual(data(archived)["status"], OrganizationUnitStatus.ARCHIVED)
        self.assertFalse(data(archived)["is_active"])

    def test_unit_cannot_be_its_own_parent(self):
        unit = OrganizationUnit.objects.create(
            organization=self.state_org,
            name="Verification Desk",
            unit_type=OrganizationUnitType.UNIT,
        )
        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            f"/api/organizations/{self.state_org.id}/units/{unit.id}/",
            {"parent": str(unit.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_unit_cannot_be_reparented_under_descendant(self):
        parent = OrganizationUnit.objects.create(
            organization=self.state_org,
            name="Directorate",
            unit_type=OrganizationUnitType.DIRECTORATE,
        )
        child = OrganizationUnit.objects.create(
            organization=self.state_org,
            name="Desk",
            unit_type=OrganizationUnitType.UNIT,
            parent=parent,
        )
        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            f"/api/organizations/{self.state_org.id}/units/{parent.id}/",
            {"parent": str(child.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 400)


class OrganizationUnitSoftDeleteTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.org = Organization.objects.create(
            name="Lagos MOH",
            organization_type=OrganizationType.STATE_MINISTRY,
            state=self.state,
        )
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.state,
            organization=self.org,
        )
        self.unit = OrganizationUnit.objects.create(
            organization=self.org,
            name="Verification Desk",
            unit_type=OrganizationUnitType.UNIT,
        )
        self.member = User.objects.create_user(
            username="officer",
            email="officer@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.state,
            organization=self.org,
            unit=self.unit,
            unit_restricted=True,
        )

    def test_soft_delete_deactivates_unit(self):
        self.client.force_authenticate(self.admin)
        response = self.client.delete(f"/api/organizations/{self.org.id}/units/{self.unit.id}/")
        self.assertEqual(response.status_code, 204)
        self.unit.refresh_from_db()
        self.assertFalse(self.unit.is_active)

    def test_soft_delete_unassigns_members(self):
        self.client.force_authenticate(self.admin)
        self.client.delete(f"/api/organizations/{self.org.id}/units/{self.unit.id}/")
        self.member.refresh_from_db()
        self.assertIsNone(self.member.unit)
        self.assertFalse(self.member.unit_restricted)

    def test_soft_delete_deactivates_child_units(self):
        child = OrganizationUnit.objects.create(
            organization=self.org,
            name="Child Unit",
            unit_type=OrganizationUnitType.UNIT,
            parent=self.unit,
        )
        self.client.force_authenticate(self.admin)
        self.client.delete(f"/api/organizations/{self.org.id}/units/{self.unit.id}/")
        child.refresh_from_db()
        self.assertFalse(child.is_active)


class OrganizationUnitScopingTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.lagos_org = Organization.objects.create(
            name="Lagos MOH",
            organization_type=OrganizationType.STATE_MINISTRY,
            state=self.state,
        )
        self.emp_org = Organization.objects.create(
            name="MegaChow Ltd",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
        )
        self.lagos_unit = OrganizationUnit.objects.create(
            organization=self.lagos_org,
            name="Food Safety",
            unit_type=OrganizationUnitType.DIRECTORATE,
        )
        self.emp_unit = OrganizationUnit.objects.create(
            organization=self.emp_org,
            name="Branch - Ikeja",
            unit_type=OrganizationUnitType.BRANCH,
        )
        self.state_admin = User.objects.create_user(
            username="lagos-admin",
            email="lagos-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.state,
        )
        self.employer = User.objects.create_user(
            username="employer",
            email="employer@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.emp_org,
        )

    def test_state_admin_sees_all_state_org_units(self):
        self.client.force_authenticate(self.state_admin)
        r1 = self.client.get(f"/api/organizations/{self.lagos_org.id}/units/")
        r2 = self.client.get(f"/api/organizations/{self.emp_org.id}/units/")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(len(data(r1)), 1)
        self.assertEqual(len(data(r2)), 1)

    def test_employer_sees_own_org_units_only(self):
        self.client.force_authenticate(self.employer)
        r1 = self.client.get(f"/api/organizations/{self.emp_org.id}/units/")
        r2 = self.client.get(f"/api/organizations/{self.lagos_org.id}/units/")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(len(data(r1)), 1)
        self.assertEqual(len(data(r2)), 0)

    def test_employer_cannot_edit_other_org_unit(self):
        self.client.force_authenticate(self.employer)
        response = self.client.patch(
            f"/api/organizations/{self.lagos_org.id}/units/{self.lagos_unit.id}/",
            {"name": "Hacked"},
            format="json",
        )
        self.assertIn(response.status_code, [403, 404])


class OrganizationUnitBranchTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.org = Organization.objects.create(
            name="MegaChow Ltd",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
        )
        self.employer = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.org,
        )

    def test_create_branch_unit(self):
        self.client.force_authenticate(self.employer)
        response = self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {
                "name": "Branch - Surulere",
                "unit_type": OrganizationUnitType.BRANCH,
                "state": str(self.state.id),
                "address": "123 Surulere Road",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(f"{data(response)['unit_type']}", OrganizationUnitType.BRANCH)
        self.assertEqual(f"{data(response)['state']}", f"{self.state.id}")

    def test_branch_name_unique_per_org(self):
        self.client.force_authenticate(self.employer)
        self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {"name": "Branch - VI", "unit_type": OrganizationUnitType.BRANCH},
            format="json",
        )
        response = self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {"name": "Branch - VI", "unit_type": OrganizationUnitType.BRANCH},
            format="json",
        )
        self.assertEqual(response.status_code, 400)


class OrganizationUnitPermittedRolesTests(APITestCase):
    """Tests from Chunk 00c acceptance criteria: role-based unit management access."""

    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.org = Organization.objects.create(
            name="Lagos MOH",
            organization_type=OrganizationType.STATE_MINISTRY,
            state=self.state,
        )
        self.fac_org = Organization.objects.create(
            name="Lagos Care",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.state,
        )
        self.super_admin = User.objects.create_user(
            username="super", email="super@example.com",
            password="pass", role=UserRole.SUPER_ADMIN,
        )
        self.state_admin = User.objects.create_user(
            username="state", email="state@example.com",
            password="pass", role=UserRole.STATE_ADMIN, state=self.state,
        )
        self.facility_admin = User.objects.create_user(
            username="facility", email="fac@example.com",
            password="pass", role=UserRole.FACILITY_ADMIN, organization=self.fac_org, state=self.state,
        )
        self.employer = User.objects.create_user(
            username="emp", email="emp@example.com",
            password="pass", role=UserRole.EMPLOYER,
            organization=self.fac_org, state=self.state,
        )
        self.food_handler = User.objects.create_user(
            username="handler", email="handler@example.com",
            password="pass", role=UserRole.FOOD_HANDLER,
        )

    def test_state_admin_can_create_unit_in_own_state_org(self):
        self.client.force_authenticate(self.state_admin)
        response = self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {"name": "Unit A", "unit_type": OrganizationUnitType.UNIT},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_food_handler_cannot_create_unit(self):
        self.client.force_authenticate(self.food_handler)
        response = self.client.post(
            f"/api/organizations/{self.fac_org.id}/units/",
            {"name": "Should Fail", "unit_type": OrganizationUnitType.UNIT},
            format="json",
        )
        self.assertIn(response.status_code, [403, 404])

    def test_facility_admin_can_manage_own_org_units(self):
        self.client.force_authenticate(self.facility_admin)
        response = self.client.post(
            f"/api/organizations/{self.fac_org.id}/units/",
            {"name": "Lab Dept", "unit_type": OrganizationUnitType.LAB_DEPARTMENT},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_facility_admin_cannot_manage_state_ministry_units(self):
        self.client.force_authenticate(self.facility_admin)
        response = self.client.post(
            f"/api/organizations/{self.org.id}/units/",
            {"name": "Bad Access", "unit_type": OrganizationUnitType.UNIT},
            format="json",
        )
        self.assertIn(response.status_code, [403, 404])


class CrossModuleScopeEnforcementTests(APITestCase):
    """Chunk 9: Verify membership-based scoping across organization units and user types."""

    def setUp(self):
        call_command("seed_roles_and_permissions", stdout=open("/dev/null", "w"))

        self.state = State.objects.create(name="Lagos", code="LA")
        self.other_state = State.objects.create(name="Abuja", code="FC")

        self.employer_org = Organization.objects.create(
            name="MegaChow Ltd",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
        )
        self.ikeja_branch = OrganizationUnit.objects.create(
            organization=self.employer_org,
            name="Ikeja Branch",
            unit_type=OrganizationUnitType.BRANCH,
        )
        self.lekki_branch = OrganizationUnit.objects.create(
            organization=self.employer_org,
            name="Lekki Branch",
            unit_type=OrganizationUnitType.BRANCH,
        )

        self.facility_org = Organization.objects.create(
            name="Excel Diagnostics",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.state,
        )
        self.clinical_dept = OrganizationUnit.objects.create(
            organization=self.facility_org,
            name="Clinical Department",
            unit_type=OrganizationUnitType.CLINICAL_DEPARTMENT,
        )
        self.lab_dept = OrganizationUnit.objects.create(
            organization=self.facility_org,
            name="Lab Department",
            unit_type=OrganizationUnitType.LAB_DEPARTMENT,
        )

        self.super_admin = User.objects.create_user(
            username="super-scope", email="super@test.com", password="pass",
            role=UserRole.SUPER_ADMIN,
        )
        self.branch_manager = User.objects.create_user(
            username="branch-mgr", email="bmgr@test.com", password="pass",
            role=UserRole.EMPLOYER, organization=self.employer_org,
        )
        self.lab_staff = User.objects.create_user(
            username="lab-tech", email="lab@test.com", password="pass",
            role=UserRole.LAB_STAFF, organization=self.facility_org,
        )

        self.branch_mgr_role = Role.objects.get(code="branch_manager")
        self.lab_staff_role = Role.objects.get(code="lab_staff")
        self.facility_admin_role = Role.objects.get(code="facility_admin")
        self.employer_admin_role = Role.objects.get(code="employer")

        self.bm_membership = OrganizationMembership.objects.create(
            user=self.branch_manager,
            organization=self.employer_org,
            role=self.branch_mgr_role,
            unit=self.ikeja_branch,
            unit_restricted=True,
            status=MembershipStatus.ACTIVE,
        )
        self.lab_membership = OrganizationMembership.objects.create(
            user=self.lab_staff,
            organization=self.facility_org,
            role=self.lab_staff_role,
            unit=self.lab_dept,
            unit_restricted=True,
            status=MembershipStatus.ACTIVE,
        )

    def test_membership_properties_are_correct(self):
        self.assertEqual(self.branch_manager.current_organization, self.employer_org)
        self.assertEqual(self.branch_manager.current_role, self.branch_mgr_role)
        self.assertEqual(self.branch_manager.current_unit, self.ikeja_branch)
        self.assertTrue(self.branch_manager.is_unit_restricted)

    def test_effective_access_branch_manager_restricted(self):
        result = EffectiveAccessService().check(
            self.branch_manager, PERMISSION_CODES["organization.view"],
            organization=self.employer_org,
        )
        self.assertTrue(result.allowed)
        self.assertEqual(result.scope, "unit")
        self.assertEqual(result.unit_id, str(self.ikeja_branch.id))

    def test_branch_manager_cannot_access_other_branch(self):
        result = EffectiveAccessService().check(
            self.branch_manager, PERMISSION_CODES["organization.view"],
            organization=self.employer_org,
        )
        self.assertTrue(result.allowed)
        self.assertEqual(result.scope, "unit")
        self.assertNotEqual(str(result.unit_id), str(self.lekki_branch.id))

    def test_lab_staff_sees_only_lab_department(self):
        result = EffectiveAccessService().check(
            self.lab_staff, PERMISSION_CODES["unit.view"],
            organization=self.facility_org,
        )
        self.assertTrue(result.allowed)
        self.assertEqual(result.scope, "unit")
        self.assertEqual(result.unit_id, str(self.lab_dept.id))

    def test_lab_staff_cannot_access_clinical_department(self):
        result = EffectiveAccessService().check(
            self.lab_staff, PERMISSION_CODES["unit.view"],
            organization=self.facility_org,
        )
        self.assertEqual(str(result.unit_id), str(self.lab_dept.id))
        self.assertNotEqual(result.unit_id, str(self.clinical_dept.id))

    def test_branch_manager_cannot_access_facility(self):
        result = EffectiveAccessService().check(
            self.branch_manager, PERMISSION_CODES["unit.view"],
            organization=self.facility_org,
        )
        self.assertFalse(result.allowed)

    def test_food_handler_cannot_access_employer_management(self):
        handler = User.objects.create_user(
            username="handler-scope", email="handler@test.com", password="pass",
            role=UserRole.FOOD_HANDLER, organization=self.employer_org,
        )
        result = EffectiveAccessService().check(
            handler, PERMISSION_CODES["organization.view"],
            organization=self.employer_org,
        )
        self.assertFalse(result.allowed)

    def test_super_admin_has_global_scope(self):
        self.client.force_authenticate(self.super_admin)
        result = EffectiveAccessService().check(
            self.super_admin, PERMISSION_CODES["organization.view"],
            organization=self.employer_org,
        )
        self.assertTrue(result.allowed)
        self.assertEqual(result.scope, "global")

    def test_unit_restricted_api_access_restricted_for_other_org(self):
        """Branch manager cannot see another org's units."""
        self.client.force_authenticate(self.branch_manager)
        response = self.client.get(f"/api/organizations/{self.facility_org.id}/units/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data(response)), 0)

    def test_permission_override_denies_access(self):
        override = PermissionOverride.objects.create(
            membership=self.bm_membership,
            permission=Permission.objects.get(code=PERMISSION_CODES["organization.view"]),
            effect=PermissionOverrideEffect.DENY,
        )
        result = EffectiveAccessService().check(
            self.branch_manager, PERMISSION_CODES["organization.view"],
            organization=self.employer_org,
        )
        self.assertFalse(result.allowed)


class MembershipAPIScopeEnforcementTests(APITestCase):
    """Chunk 9: Cross-org membership API scope enforcement."""

    def setUp(self):
        call_command("seed_roles_and_permissions", stdout=open("/dev/null", "w"))

        self.state = State.objects.create(name="Lagos", code="LA")

        self.org1 = Organization.objects.create(
            name="Org 1", organization_type=OrganizationType.EMPLOYER, state=self.state,
        )
        self.org2 = Organization.objects.create(
            name="Org 2", organization_type=OrganizationType.EMPLOYER, state=self.state,
        )

        self.admin = User.objects.create_user(
            username="api-scope-admin", email="admin@test.com", password="pass",
            role=UserRole.SUPER_ADMIN,
        )
        self.org1_user = User.objects.create_user(
            username="org1-user", email="u1@test.com", password="pass",
            role=UserRole.EMPLOYER, organization=self.org1,
        )
        self.org2_user = User.objects.create_user(
            username="org2-user", email="u2@test.com", password="pass",
            role=UserRole.EMPLOYER, organization=self.org2,
        )

        self.role = Role.objects.get(code="employer")
        OrganizationMembership.objects.create(
            user=self.org1_user, organization=self.org1,
            role=self.role, status=MembershipStatus.ACTIVE,
        )
        OrganizationMembership.objects.create(
            user=self.org2_user, organization=self.org2,
            role=self.role, status=MembershipStatus.ACTIVE,
        )

    def test_org1_user_sees_only_org1_memberships(self):
        self.client.force_authenticate(self.org1_user)
        response = self.client.get(f"/api/organizations/{self.org1.id}/memberships/")
        self.assertEqual(response.status_code, 200)

    def test_org1_user_cannot_see_org2_memberships(self):
        self.client.force_authenticate(self.org1_user)
        response = self.client.get(f"/api/organizations/{self.org2.id}/memberships/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data(response)), 0)

    def test_org2_user_cannot_see_org1_memberships(self):
        self.client.force_authenticate(self.org2_user)
        response = self.client.get(f"/api/organizations/{self.org1.id}/memberships/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data(response)), 0)

    def test_super_admin_sees_all_orgs(self):
        self.client.force_authenticate(self.admin)
        r1 = self.client.get(f"/api/organizations/{self.org1.id}/memberships/")
        r2 = self.client.get(f"/api/organizations/{self.org2.id}/memberships/")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)
