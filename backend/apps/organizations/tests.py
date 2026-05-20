from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.locations.models import State, LGA
from apps.organizations.models import Organization, OrganizationType, OrganizationUnit, OrganizationUnitType

User = get_user_model()


def data(response):
    return response.data.get("data", response.data)


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

    def test_unit_cannot_be_its_own_parent(self):
        unit = OrganizationUnit.objects.create(
            organization=self.org,
            name="Verification Desk",
            unit_type=OrganizationUnitType.UNIT,
        )
        self.client.force_authenticate(self.state_admin)
        response = self.client.patch(
            f"/api/organizations/{self.org.id}/units/{unit.id}/",
            {"parent": str(unit.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_unit_cannot_be_reparented_under_descendant(self):
        parent = OrganizationUnit.objects.create(
            organization=self.org,
            name="Directorate",
            unit_type=OrganizationUnitType.DIRECTORATE,
        )
        child = OrganizationUnit.objects.create(
            organization=self.org,
            name="Desk",
            unit_type=OrganizationUnitType.UNIT,
            parent=parent,
        )
        self.client.force_authenticate(self.state_admin)
        response = self.client.patch(
            f"/api/organizations/{self.org.id}/units/{parent.id}/",
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
