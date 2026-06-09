from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError, transaction
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
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
