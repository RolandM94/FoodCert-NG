from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import InviteStatus, UserInvite, UserRole, UserStatus
from apps.audit.models import AuditAction, AuditLog
from apps.facilities.models import FacilityStaffProfile, FacilityStaffType, FacilityType, MedicalFacility, OwnershipType
from apps.locations.models import State
from apps.organizations.models import MembershipStatus, Organization, OrganizationMembership, OrganizationType, OrganizationUnit, OrganizationUnitType

User = get_user_model()


def data(response):
    return response.data.get("data", response.data)


class AuthenticationApiTests(APITestCase):
    def test_user_can_register_and_login(self):
        register_response = self.client.post(
            "/api/auth/register/",
            {
                "username": "handler1",
                "email": "handler@example.com",
                "password": "StrongPass123!",
                "first_name": "Ada",
                "last_name": "Okafor",
                "phone": "08030000000",
                "role": UserRole.FOOD_HANDLER,
            },
            format="json",
        )

        self.assertEqual(register_response.status_code, 201)
        self.assertEqual(data(register_response)["role"], UserRole.FOOD_HANDLER)

        login_response = self.client.post(
            "/api/auth/login/",
            {"username": "handler1", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access", data(login_response))
        self.assertEqual(data(login_response)["user"]["email"], "handler@example.com")

    def test_suspended_user_cannot_login(self):
        User.objects.create_user(
            username="suspended",
            email="suspended@example.com",
            password="StrongPass123!",
            status=UserStatus.SUSPENDED,
        )

        response = self.client.post(
            "/api/auth/login/",
            {"username": "suspended", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        if "success" in response.data:
            self.assertFalse(response.data["success"])

    def test_high_privilege_login_failure_is_audited_with_request_metadata(self):
        admin = User.objects.create_user(
            username="state-admin",
            email="state-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
        )

        response = self.client.post(
            "/api/auth/login/",
            {"username": admin.username, "password": "wrong-password"},
            HTTP_USER_AGENT="FoodCertSecurityTest/1.0",
            REMOTE_ADDR="10.0.0.10",
            format="json",
        )

        self.assertEqual(response.status_code, 401)
        audit = AuditLog.objects.get(action=AuditAction.SECURITY_EVENT)
        self.assertEqual(audit.actor, admin)
        self.assertEqual(audit.ip_address, "10.0.0.10")
        self.assertEqual(audit.user_agent, "FoodCertSecurityTest/1.0")
        self.assertEqual(audit.metadata["event"], "high_privilege_login_failure")


class UserOrganizationScopeTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.lagos_facility = Organization.objects.create(
            name="Lagos Care",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.lagos,
        )
        self.oyo_facility = Organization.objects.create(
            name="Oyo Care",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.oyo,
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
            state=self.lagos,
        )
        self.facility_admin = User.objects.create_user(
            username="facility-admin",
            email="facility-admin@example.com",
            password="StrongPass123!",
            role=UserRole.FACILITY_ADMIN,
            organization=self.lagos_facility,
            state=self.lagos,
        )
        self.oyo_doctor = User.objects.create_user(
            username="oyo-doctor",
            email="oyo-doctor@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.oyo_facility,
            state=self.oyo,
        )

    def test_me_endpoint_returns_current_user(self):
        self.client.force_authenticate(self.facility_admin)

        response = self.client.get("/api/users/me/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data(response)["email"], "facility-admin@example.com")

    def test_state_admin_only_lists_state_users(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/users/")

        self.assertEqual(response.status_code, 200)
        emails = {item["email"] for item in data(response)}
        self.assertIn("facility-admin@example.com", emails)
        self.assertNotIn("oyo-doctor@example.com", emails)

    def test_facility_admin_cannot_access_other_organization_user(self):
        self.client.force_authenticate(self.facility_admin)

        response = self.client.get(f"/api/users/{self.oyo_doctor.id}/")

        self.assertEqual(response.status_code, 404)

    def test_facility_admin_can_invite_user_to_own_organization(self):
        self.client.force_authenticate(self.facility_admin)

        response = self.client.post(
            "/api/users/invite/",
            {
                "username": "new-doctor",
                "email": "new-doctor@example.com",
                "password": "StrongPass123!",
                "role": UserRole.DOCTOR,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        invited = User.objects.get(email="new-doctor@example.com")
        self.assertEqual(invited.organization, self.lagos_facility)

    def test_state_admin_cannot_create_out_of_state_organization(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(
            "/api/organizations/",
            {
                "name": "Out of State Facility",
                "organization_type": OrganizationType.MEDICAL_FACILITY,
                "state": str(self.oyo.id),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        if "code" in response.data:
            self.assertEqual(response.data["code"], "PERMISSION_DENIED")

    def test_super_admin_can_list_all_organizations(self):
        self.client.force_authenticate(self.super_admin)

        response = self.client.get("/api/organizations/")

        self.assertEqual(response.status_code, 200)
        names = {item["name"] for item in data(response)}
        self.assertEqual(names, {"Lagos Care", "Oyo Care"})


class UserInviteUnitWorkflowTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.org = Organization.objects.create(
            name="Tasty Foods",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
        )
        self.branch = OrganizationUnit.objects.create(
            organization=self.org,
            name="Ikeja Branch",
            unit_type=OrganizationUnitType.BRANCH,
            state=self.state,
        )
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.org,
            state=self.state,
        )

    def test_invite_acceptance_assigns_role_organization_and_unit(self):
        self.client.force_authenticate(self.owner)
        invite_response = self.client.post(
            f"/api/organizations/{self.org.id}/invites/",
            {
                "email": "branch.manager@example.com",
                "role": UserRole.EMPLOYER,
                "unit": str(self.branch.id),
                "message": "Join Ikeja branch",
            },
            format="json",
        )
        self.assertEqual(invite_response.status_code, 201)

        token = data(invite_response)["token"]
        self.client.force_authenticate(user=None)
        accept_response = self.client.post(
            f"/api/invites/{token}/accept/",
            {"username": "branch-manager", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(accept_response.status_code, 200)
        invited = User.objects.get(email="branch.manager@example.com")
        self.assertEqual(invited.role, UserRole.EMPLOYER)
        self.assertEqual(invited.organization, self.org)
        self.assertEqual(invited.unit, self.branch)
        self.assertTrue(invited.unit_restricted)
        membership = OrganizationMembership.objects.get(user=invited, organization=self.org)
        self.assertEqual(membership.status, MembershipStatus.ACTIVE)
        self.assertEqual(membership.role.code, UserRole.EMPLOYER)
        self.assertEqual(membership.unit, self.branch)
        self.assertTrue(membership.unit_restricted)
        self.assertEqual(UserInvite.objects.get(token=token).status, InviteStatus.ACCEPTED)

    def test_invite_preview_resend_revoke_and_decline(self):
        self.client.force_authenticate(self.owner)
        invite_response = self.client.post(
            f"/api/organizations/{self.org.id}/invites/",
            {
                "email": "preview@example.com",
                "role": UserRole.EMPLOYER,
                "unit": str(self.branch.id),
                "unit_restricted": True,
                "message": "Join Ikeja branch",
            },
            format="json",
        )
        self.assertEqual(invite_response.status_code, 201, invite_response.data)
        invite_id = data(invite_response)["id"]
        token = data(invite_response)["token"]

        self.client.force_authenticate(user=None)
        preview = self.client.get(f"/api/invites/{token}/preview/")
        self.assertEqual(preview.status_code, 200, preview.data)
        self.assertEqual(data(preview)["organization_name"], "Tasty Foods")
        self.assertEqual(data(preview)["organization_type"], OrganizationType.EMPLOYER)
        self.assertEqual(data(preview)["unit_name"], "Ikeja Branch")
        self.assertTrue(data(preview)["unit_restricted"])

        self.client.force_authenticate(self.owner)
        resent = self.client.post(f"/api/organizations/{self.org.id}/invites/{invite_id}/resend/", format="json")
        self.assertEqual(resent.status_code, 200, resent.data)
        self.assertNotEqual(data(resent)["token"], token)

        declined_token = data(resent)["token"]
        self.client.force_authenticate(user=None)
        declined = self.client.post(f"/api/invites/{declined_token}/decline/", format="json")
        self.assertEqual(declined.status_code, 200, declined.data)
        self.assertEqual(data(declined)["status"], InviteStatus.DECLINED)

        self.client.force_authenticate(self.owner)
        second = self.client.post(
            f"/api/organizations/{self.org.id}/invites/",
            {"email": "revoke@example.com", "role": UserRole.EMPLOYER},
            format="json",
        )
        revoked = self.client.post(f"/api/organizations/{self.org.id}/invites/{data(second)['id']}/revoke/", format="json")
        self.assertEqual(revoked.status_code, 200, revoked.data)
        self.assertEqual(data(revoked)["status"], InviteStatus.REVOKED)

    def test_expired_invite_cannot_be_accepted(self):
        invite = UserInvite.objects.create(
            organization=self.org,
            unit=self.branch,
            invited_by=self.owner,
            email="expired@example.com",
            role=UserRole.FOOD_HANDLER,
            token="expired-token",
            expires_at=timezone.now() - timezone.timedelta(minutes=1),
        )

        response = self.client.post(
            f"/api/invites/{invite.token}/accept/",
            {"username": "expired", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        invite.refresh_from_db()
        self.assertEqual(invite.status, InviteStatus.EXPIRED)

    def test_facility_invite_acceptance_creates_staff_profile(self):
        facility_org = Organization.objects.create(
            name="Lagos Diagnostic Centre",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.state,
        )
        facility = MedicalFacility.objects.create(
            organization=facility_org,
            facility_name="Lagos Diagnostic Centre",
            facility_type=FacilityType.DIAGNOSTIC_CENTRE,
            ownership_type=OwnershipType.PRIVATE,
            license_number="LDC-001",
            address="1 Health Road",
            state=self.state,
            contact_person="Medical Director",
            phone="08030000001",
            email="facility@example.com",
        )
        records_department = OrganizationUnit.objects.create(
            organization=facility_org,
            name="Records",
            unit_type=OrganizationUnitType.RECORDS_DEPARTMENT,
            state=self.state,
        )
        facility_admin = User.objects.create_user(
            username="facility-owner",
            email="facility-owner@example.com",
            password="StrongPass123!",
            role=UserRole.FACILITY_ADMIN,
            organization=facility_org,
            state=self.state,
        )
        invite = UserInvite.objects.create(
            organization=facility_org,
            unit=records_department,
            invited_by=facility_admin,
            email="records@example.com",
            role=UserRole.FACILITY_ADMIN,
            facility_staff_type=FacilityStaffType.RECORDS_STAFF,
            token="records-staff-token",
            expires_at=timezone.now() + timezone.timedelta(days=7),
        )

        response = self.client.post(
            f"/api/invites/{invite.token}/accept/",
            {"username": "records-staff", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        invited = User.objects.get(email="records@example.com")
        self.assertEqual(invited.organization, facility_org)
        self.assertEqual(invited.unit, records_department)
        self.assertTrue(invited.unit_restricted)
        membership = OrganizationMembership.objects.get(user=invited, organization=facility_org)
        self.assertEqual(membership.role.code, UserRole.FACILITY_ADMIN)
        self.assertEqual(membership.unit, records_department)
        profile = FacilityStaffProfile.objects.get(user=invited)
        self.assertEqual(profile.facility, facility)
        self.assertEqual(profile.department, records_department)
        self.assertEqual(profile.staff_type, FacilityStaffType.RECORDS_STAFF)
        self.assertTrue(profile.is_active)
