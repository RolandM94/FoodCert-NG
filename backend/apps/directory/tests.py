from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.employers.models import Employer, EstablishmentCategory
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, FoodHandlerStatus, Gender
from apps.illness.models import ClearanceStatus, IllnessReport
from apps.locations.models import State
from apps.organizations.models import Organization, OrganizationType

User = get_user_model()


def rows(response):
    payload = response.data.get("data", response.data)
    return payload.get("results", payload) if isinstance(payload, dict) else payload


class DirectoryIllnessFilterTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.org = Organization.objects.create(name="Clean Foods", organization_type=OrganizationType.EMPLOYER, state=self.state)
        self.state_admin = User.objects.create_user(
            "state-admin",
            "state@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.state,
        )
        self.employer_user = User.objects.create_user(
            "employer",
            "employer@example.com",
            "StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.org,
            state=self.state,
        )
        self.employer = Employer.objects.create(
            user=self.employer_user,
            organization=self.org,
            business_name="Clean Foods",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Ada",
            contact_person_phone="08030000000",
            contact_person_email="ada@example.com",
            address="1 Food Road",
            state=self.state,
        )
        self.excluded_user = User.objects.create_user("excluded", "excluded@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.state)
        self.fit_user = User.objects.create_user("fit", "fit@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.state)
        self.excluded_handler = FoodHandlerProfile.objects.create(
            user=self.excluded_user,
            full_name="Excluded Handler",
            date_of_birth="1992-04-12",
            gender=Gender.FEMALE,
            nin="12345678901",
            phone="08030000003",
            email="excluded@example.com",
            home_address="3 Allen Avenue",
            state=self.state,
            employer=self.employer,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-DIR001",
            current_status=FoodHandlerStatus.TEMPORARILY_EXCLUDED,
        )
        self.fit_handler = FoodHandlerProfile.objects.create(
            user=self.fit_user,
            full_name="Fit Handler",
            date_of_birth="1993-04-12",
            gender=Gender.MALE,
            nin="12345678902",
            phone="08030000004",
            email="fit@example.com",
            home_address="4 Allen Avenue",
            state=self.state,
            employer=self.employer,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-DIR002",
            current_status=FoodHandlerStatus.FIT,
        )
        IllnessReport.objects.create(
            food_handler=self.excluded_handler,
            employer=self.employer,
            reported_by=self.employer_user,
            symptoms={"fever": True},
            clearance_status=ClearanceStatus.CLEARANCE_REQUIRED,
            earliest_return_date=timezone.localdate() + timezone.timedelta(days=2),
        )

    def test_directory_filters_food_handlers_by_operational_fitness_status(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/directory/food-handlers/?operational_fitness_status=temporarily_excluded")

        self.assertEqual(response.status_code, 200)
        payload = rows(response)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["id"], str(self.excluded_handler.id))

    def test_directory_filters_food_handlers_by_illness_and_rtw_status(self):
        self.client.force_authenticate(self.state_admin)

        exclusion_response = self.client.get("/api/directory/food-handlers/?illness_exclusion_status=clearance_required")
        rtw_response = self.client.get("/api/directory/food-handlers/?return_to_work_status=clearance_required")
        none_response = self.client.get("/api/directory/food-handlers/?return_to_work_status=not_required")

        self.assertEqual(exclusion_response.status_code, 200)
        self.assertEqual(rtw_response.status_code, 200)
        self.assertEqual(none_response.status_code, 200)
        self.assertEqual([row["id"] for row in rows(exclusion_response)], [str(self.excluded_handler.id)])
        self.assertEqual([row["id"] for row in rows(rtw_response)], [str(self.excluded_handler.id)])
        self.assertEqual([row["id"] for row in rows(none_response)], [str(self.fit_handler.id)])
