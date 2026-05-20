from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.employers.models import Employer, EstablishmentCategory
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, FoodHandlerStatus, Gender
from apps.illness.models import ClearanceStatus
from apps.locations.models import State
from apps.notifications.models import Notification, NotificationType
from apps.organizations.models import Organization, OrganizationType

User = get_user_model()


def data(response):
    return response.data.get("data", response.data)


class IllnessWorkflowTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.employer_org = Organization.objects.create(name="Clean Foods", organization_type=OrganizationType.EMPLOYER, state=self.state)
        self.facility_org = Organization.objects.create(name="Clinic", organization_type=OrganizationType.MEDICAL_FACILITY, state=self.state)
        self.handler_user = User.objects.create_user("handler", "handler@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.state)
        self.employer_user = User.objects.create_user(
            "employer",
            "employer@example.com",
            "StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
            state=self.state,
        )
        self.doctor = User.objects.create_user(
            "doctor",
            "doctor@example.com",
            "StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.state,
        )
        self.employer = Employer.objects.create(
            user=self.employer_user,
            organization=self.employer_org,
            business_name="Clean Foods",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Ada",
            contact_person_phone="08030000000",
            contact_person_email="ada@example.com",
            address="1 Food Road",
            state=self.state,
        )
        self.food_handler = FoodHandlerProfile.objects.create(
            user=self.handler_user,
            full_name="Ada Okafor",
            date_of_birth="1992-04-12",
            gender=Gender.FEMALE,
            nin="12345678901",
            phone="08030000003",
            email="ada@example.com",
            home_address="3 Allen Avenue",
            state=self.state,
            employer=self.employer,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-ILL001",
            current_status=FoodHandlerStatus.FIT,
        )

    def test_illness_report_excludes_handler_and_notifies_employer(self):
        self.client.force_authenticate(self.handler_user)
        symptom_end = timezone.localdate()

        response = self.client.post(
            "/api/illness-reports/",
            {
                "food_handler": str(self.food_handler.id),
                "symptoms": {"diarrhoea": True, "vomiting": True},
                "suspected_condition": "general_diarrhoea_vomiting",
                "symptom_end_date": str(symptom_end),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data(response)["earliest_return_date"], str(symptom_end + timezone.timedelta(days=2)))
        self.food_handler.refresh_from_db()
        self.assertEqual(self.food_handler.current_status, FoodHandlerStatus.TEMPORARILY_EXCLUDED)
        self.assertTrue(Notification.objects.filter(recipient=self.employer_user, notification_type=NotificationType.ILLNESS_REPORTED).exists())

    def test_doctor_can_clear_after_earliest_return_date(self):
        self.client.force_authenticate(self.handler_user)
        report_response = self.client.post(
            "/api/illness-reports/",
            {
                "food_handler": str(self.food_handler.id),
                "symptoms": {"diarrhoea": True},
                "suspected_condition": "general_diarrhoea_vomiting",
                "symptom_end_date": str(timezone.localdate() - timezone.timedelta(days=2)),
            },
            format="json",
        )
        report_id = data(report_response)["id"]

        self.client.force_authenticate(self.doctor)
        review_response = self.client.patch(f"/api/illness-reports/{report_id}/review/", {"notes": "Symptoms resolved."}, format="json")
        self.assertEqual(review_response.status_code, 200)
        clearance_response = self.client.patch(
            f"/api/illness-reports/{report_id}/clearance/",
            {"cleared": True, "notes": "Cleared for duty."},
            format="json",
        )

        self.assertEqual(clearance_response.status_code, 200)
        self.assertEqual(data(clearance_response)["clearance_status"], ClearanceStatus.CLEARED)
        self.assertTrue(data(clearance_response)["return_to_work_certificate_number"].startswith("RTW-"))
        self.food_handler.refresh_from_db()
        self.assertEqual(self.food_handler.current_status, FoodHandlerStatus.FIT)

    def test_employer_sees_operational_illness_status(self):
        self.client.force_authenticate(self.handler_user)
        self.client.post(
            "/api/illness-reports/",
            {"food_handler": str(self.food_handler.id), "symptoms": {"fever": True}, "suspected_condition": "other"},
            format="json",
        )

        self.client.force_authenticate(self.employer_user)
        response = self.client.get("/api/illness-reports/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data(response)), 1)
        self.assertEqual(data(response)[0]["clearance_status"], ClearanceStatus.PENDING)
