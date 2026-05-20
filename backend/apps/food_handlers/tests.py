from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.employers.models import Employer, EstablishmentCategory
from apps.food_handlers.models import FoodHandlerProfile
from apps.locations.models import State
from apps.nin_verification.models import NINVerificationStatus
from apps.organizations.models import Organization, OrganizationType, OrganizationUnit, OrganizationUnitType

User = get_user_model()


def data(response):
    return response.data.get("data", response.data)


class IdentityWorkflowTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.employer_org = Organization.objects.create(
            name="Tasty Foods",
            organization_type=OrganizationType.EMPLOYER,
            state=self.lagos,
        )
        self.employer_user = User.objects.create_user(
            username="employer",
            email="employer@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
            state=self.lagos,
        )
        self.employer = Employer.objects.create(
            user=self.employer_user,
            organization=self.employer_org,
            business_name="Tasty Foods",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Amina Bello",
            contact_person_phone="08030000001",
            contact_person_email="amina@example.com",
            address="12 Marina",
            state=self.lagos,
            number_of_food_handlers=5,
        )
        self.handler_user = User.objects.create_user(
            username="handler",
            email="handler@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.lagos,
        )
        self.state_admin = User.objects.create_user(
            username="state-admin",
            email="state-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )

    def _profile_payload(self, nin="12345678901"):
        return {
            "full_name": "Ada Okafor",
            "date_of_birth": "1992-04-12",
            "gender": "female",
            "nin": nin,
            "phone": "08030000002",
            "email": "ada@example.com",
            "nationality": "Nigerian",
            "home_address": "3 Allen Avenue",
            "state": str(self.lagos.id),
            "ward": "Ward A",
            "employer": str(self.employer.id),
            "work_location": "Tasty Foods Ikeja",
            "food_handler_category": "food_preparer",
            "emergency_contact": "Chika 08030000003",
        }

    def _profile_model_kwargs(self, nin="12345678901"):
        payload = self._profile_payload(nin)
        payload["state"] = self.lagos
        payload["employer"] = self.employer
        return payload

    def test_food_handler_can_create_profile_without_nin_being_returned(self):
        self.client.force_authenticate(self.handler_user)

        response = self.client.post("/api/food-handlers/", self._profile_payload(), format="json")

        self.assertEqual(response.status_code, 201)
        self.assertNotIn("nin", data(response))
        self.assertEqual(data(response)["masked_nin"], "*******8901")
        self.assertTrue(FoodHandlerProfile.objects.filter(user=self.handler_user).exists())

    def test_successful_nin_verification_marks_profile_pending_certification(self):
        self.client.force_authenticate(self.handler_user)
        profile = FoodHandlerProfile.objects.create(
            user=self.handler_user,
            system_identifier="FCN-TEST001",
            **self._profile_model_kwargs(),
        )

        response = self.client.post(f"/api/food-handlers/{profile.id}/verify-nin/")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data(response)["status"], NINVerificationStatus.VERIFIED)
        self.assertEqual(data(response)["masked_nin"], "*******8901")
        self.assertNotIn("nin", data(response))
        profile.refresh_from_db()
        self.assertEqual(profile.current_status, "certification_pending")

    def test_mismatched_nin_requires_manual_review_and_state_override(self):
        self.client.force_authenticate(self.handler_user)
        profile = FoodHandlerProfile.objects.create(
            user=self.handler_user,
            system_identifier="FCN-TEST002",
            **self._profile_model_kwargs(nin="12345670000"),
        )

        verify_response = self.client.post(f"/api/food-handlers/{profile.id}/verify-nin/")

        self.assertEqual(verify_response.status_code, 201)
        self.assertEqual(data(verify_response)["status"], NINVerificationStatus.MANUAL_REVIEW_REQUIRED)

        verification_id = data(verify_response)["id"]
        self.client.force_authenticate(self.state_admin)
        override_response = self.client.patch(
            f"/api/nin-verifications/{verification_id}/approve-override/",
            {"review_notes": "Identity reviewed against official documents."},
            format="json",
        )

        self.assertEqual(override_response.status_code, 200)
        self.assertEqual(data(override_response)["status"], NINVerificationStatus.OVERRIDE_APPROVED)

    def test_employer_food_handler_list_does_not_expose_nin_or_verification_detail(self):
        FoodHandlerProfile.objects.create(
            user=self.handler_user,
            system_identifier="FCN-TEST003",
            **self._profile_model_kwargs(),
        )
        self.client.force_authenticate(self.employer_user)

        list_response = self.client.get("/api/food-handlers/")

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(data(list_response)), 1)
        self.assertNotIn("nin", data(list_response)[0])
        self.assertNotIn("masked_nin", data(list_response)[0])

    def test_employer_cannot_access_nin_verification_detail(self):
        profile = FoodHandlerProfile.objects.create(
            user=self.handler_user,
            system_identifier="FCN-TEST004",
            **self._profile_model_kwargs(),
        )
        self.client.force_authenticate(self.handler_user)
        self.client.post(f"/api/food-handlers/{profile.id}/verify-nin/")

        self.client.force_authenticate(self.employer_user)
        response = self.client.get(f"/api/food-handlers/{profile.id}/nin-verification/")

        self.assertEqual(response.status_code, 403)

    def test_employer_can_invite_food_handler_only(self):
        self.client.force_authenticate(self.employer_user)

        response = self.client.post(
            "/api/users/invite/",
            {
                "username": "new-handler",
                "email": "new-handler@example.com",
                "password": "StrongPass123!",
                "role": UserRole.FOOD_HANDLER,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        invited = User.objects.get(email="new-handler@example.com")
        self.assertEqual(invited.organization, self.employer_org)

        blocked_response = self.client.post(
            "/api/users/invite/",
            {
                "username": "new-doctor",
                "email": "new-doctor@example.com",
                "password": "StrongPass123!",
                "role": UserRole.DOCTOR,
            },
            format="json",
        )

        self.assertEqual(blocked_response.status_code, 400)

    def test_branch_manager_only_sees_branch_food_handlers(self):
        branch = OrganizationUnit.objects.create(
            organization=self.employer_org,
            name="Ikeja Branch",
            unit_type=OrganizationUnitType.BRANCH,
        )
        other_branch = OrganizationUnit.objects.create(
            organization=self.employer_org,
            name="Yaba Branch",
            unit_type=OrganizationUnitType.BRANCH,
        )
        FoodHandlerProfile.objects.create(
            user=self.handler_user,
            system_identifier="FCN-BRANCH001",
            business_branch=branch,
            **self._profile_model_kwargs(),
        )
        FoodHandlerProfile.objects.create(
            user=User.objects.create_user("handler-yaba", "yaba@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER),
            system_identifier="FCN-BRANCH002",
            business_branch=other_branch,
            **self._profile_model_kwargs(nin="12345678909"),
        )
        branch_manager = User.objects.create_user(
            "branch-manager",
            "branch-manager@example.com",
            "StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
            unit=branch,
            unit_restricted=True,
        )

        self.client.force_authenticate(branch_manager)
        response = self.client.get("/api/food-handlers/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data(response)), 1)
        self.assertEqual(str(data(response)[0]["business_branch"]), str(branch.id))

    def test_employer_can_assign_food_handler_business_branch(self):
        branch = OrganizationUnit.objects.create(
            organization=self.employer_org,
            name="Victoria Island Branch",
            unit_type=OrganizationUnitType.BRANCH,
        )
        profile = FoodHandlerProfile.objects.create(
            user=self.handler_user,
            system_identifier="FCN-BRANCH003",
            **self._profile_model_kwargs(),
        )

        self.client.force_authenticate(self.employer_user)
        response = self.client.patch(
            f"/api/food-handlers/{profile.id}/business-branch/",
            {"business_branch": str(branch.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        profile.refresh_from_db()
        self.assertEqual(profile.business_branch, branch)
