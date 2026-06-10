from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.employers.models import Employer, EstablishmentCategory
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, FoodHandlerStatus, Gender
from apps.illness.models import ClearanceStatus, IllnessReport
from apps.locations.models import State
from apps.notifications.models import Notification, NotificationCategory
from apps.organizations.models import Organization, OrganizationType

User = get_user_model()


def data(response):
    if isinstance(response.data, list):
        return response.data
    return response.data.get("data", response.data)


class IllnessWorkflowTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.other_state = State.objects.create(name="Oyo", code="OY")
        self.employer_org = Organization.objects.create(name="Clean Foods", organization_type=OrganizationType.EMPLOYER, state=self.state)
        self.facility_org = Organization.objects.create(name="Clinic", organization_type=OrganizationType.MEDICAL_FACILITY, state=self.state)
        self.handler_user = User.objects.create_user("handler", "handler@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.state)
        self.other_handler_user = User.objects.create_user("other-handler", "other-handler@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.state)
        self.other_state_handler_user = User.objects.create_user("oyo-handler", "oyo-handler@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.other_state)
        self.state_admin = User.objects.create_user("state-admin", "state@example.com", "StrongPass123!", role=UserRole.STATE_ADMIN, state=self.state)
        self.other_state_admin = User.objects.create_user("oyo-admin", "oyo@example.com", "StrongPass123!", role=UserRole.STATE_ADMIN, state=self.other_state)
        self.inspector = User.objects.create_user("inspector", "inspector@example.com", "StrongPass123!", role=UserRole.INSPECTOR, state=self.state)
        self.employer_user = User.objects.create_user(
            "employer",
            "employer@example.com",
            "StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
            state=self.state,
        )
        self.other_employer_org = Organization.objects.create(name="Other Foods", organization_type=OrganizationType.EMPLOYER, state=self.state)
        self.other_employer_user = User.objects.create_user(
            "other-employer",
            "other-employer@example.com",
            "StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.other_employer_org,
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
        self.facility_admin = User.objects.create_user(
            "facility-admin",
            "facility-admin@example.com",
            "StrongPass123!",
            role=UserRole.FACILITY_ADMIN,
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
        self.other_employer = Employer.objects.create(
            user=self.other_employer_user,
            organization=self.other_employer_org,
            business_name="Other Foods",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Bola",
            contact_person_phone="08030000010",
            contact_person_email="bola@example.com",
            address="2 Food Road",
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
        self.other_food_handler = FoodHandlerProfile.objects.create(
            user=self.other_handler_user,
            full_name="Bola Musa",
            date_of_birth="1991-05-20",
            gender=Gender.MALE,
            nin="12345678902",
            phone="08030000004",
            email="bola-handler@example.com",
            home_address="4 Allen Avenue",
            state=self.state,
            employer=self.other_employer,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-ILL002",
            current_status=FoodHandlerStatus.FIT,
        )
        self.other_state_food_handler = FoodHandlerProfile.objects.create(
            user=self.other_state_handler_user,
            full_name="Tunde Ade",
            date_of_birth="1990-08-10",
            gender=Gender.MALE,
            nin="12345678903",
            phone="08030000005",
            email="tunde@example.com",
            home_address="5 Ring Road",
            state=self.other_state,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-ILL003",
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
        self.assertTrue(Notification.objects.filter(recipient=self.employer_user, category=NotificationCategory.ASSESSMENT).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.handler_user, title="Illness exclusion recorded").exists())

    def test_clearance_required_report_notifies_doctor_and_state_exception_users(self):
        self.client.force_authenticate(self.handler_user)

        response = self.client.post(
            "/api/illness-reports/",
            {
                "food_handler": str(self.food_handler.id),
                "symptoms": {"diarrhoea": True},
                "suspected_condition": "cholera",
                "notes": "Private note that must not be in notifications",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Notification.objects.filter(recipient=self.doctor, title="Return-to-work review required").exists())
        state_notice = Notification.objects.get(recipient=self.state_admin, title="Illness exclusion exception")
        self.assertNotIn("Private note", state_notice.message)
        self.assertFalse(Notification.objects.filter(recipient=self.other_state_admin, title="Illness exclusion exception").exists())

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
        self.assertTrue(Notification.objects.filter(recipient=self.handler_user, title="Return to work cleared").exists())
        self.assertTrue(Notification.objects.filter(recipient=self.employer_user, title="Return to work cleared").exists())

    def test_doctor_rejection_notifies_handler_and_employer(self):
        self.client.force_authenticate(self.handler_user)
        report_response = self.client.post(
            "/api/illness-reports/",
            {
                "food_handler": str(self.food_handler.id),
                "symptoms": {"diarrhoea": True},
                "suspected_condition": "cholera",
            },
            format="json",
        )
        report_id = data(report_response)["id"]

        self.client.force_authenticate(self.doctor)
        clearance_response = self.client.patch(
            f"/api/illness-reports/{report_id}/clearance/",
            {"cleared": False, "notes": "Not safe to return."},
            format="json",
        )

        self.assertEqual(clearance_response.status_code, 200)
        self.assertEqual(data(clearance_response)["clearance_status"], ClearanceStatus.REJECTED)
        self.assertTrue(Notification.objects.filter(recipient=self.handler_user, title="Return to work not cleared").exists())
        self.assertTrue(Notification.objects.filter(recipient=self.employer_user, title="Return to work not cleared").exists())

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
        self.assertNotIn("symptoms", data(response)[0])
        self.assertNotIn("notes", data(response)[0])

    def test_employer_specific_illness_endpoint_omits_private_medical_details(self):
        self.client.force_authenticate(self.employer_user)
        response = self.client.post(
            f"/api/employers/{self.employer.id}/illness-reports/",
            {
                "food_handler": str(self.food_handler.id),
                "symptoms": {"fever": True},
                "suspected_condition": "other",
                "notes": "Internal employer note",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertNotIn("symptoms", data(response))
        self.assertNotIn("notes", data(response))

        list_response = self.client.get(f"/api/employers/{self.employer.id}/illness-reports/")
        self.assertEqual(list_response.status_code, 200)
        self.assertNotIn("symptoms", data(list_response)[0])
        self.assertNotIn("notes", data(list_response)[0])

    def test_employer_only_sees_linked_food_handler_illness_cases(self):
        IllnessReport.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            reported_by=self.handler_user,
            symptoms={"fever": True},
            notes="Own employer private note",
        )
        IllnessReport.objects.create(
            food_handler=self.other_food_handler,
            employer=self.other_employer,
            reported_by=self.other_handler_user,
            symptoms={"vomiting": True},
            notes="Other employer private note",
        )
        self.client.force_authenticate(self.employer_user)

        response = self.client.get("/api/illness-reports/")

        self.assertEqual(response.status_code, 200)
        rows = data(response)
        self.assertEqual(len(rows), 1)
        self.assertEqual(str(rows[0]["food_handler"]), str(self.food_handler.id))
        self.assertNotIn("symptoms", rows[0])
        self.assertNotIn("notes", rows[0])

    def test_state_user_sees_only_state_scoped_operational_illness_cases(self):
        IllnessReport.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            reported_by=self.handler_user,
            symptoms={"fever": True},
            notes="Lagos private note",
        )
        other_state_report = IllnessReport.objects.create(
            food_handler=self.other_state_food_handler,
            reported_by=self.other_state_handler_user,
            symptoms={"vomiting": True},
            notes="Oyo private note",
        )
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/illness-reports/")
        detail_response = self.client.get(f"/api/illness-reports/{other_state_report.id}/")

        self.assertEqual(response.status_code, 200)
        rows = data(response)
        self.assertEqual(len(rows), 1)
        self.assertEqual(str(rows[0]["food_handler"]), str(self.food_handler.id))
        self.assertNotIn("symptoms", rows[0])
        self.assertNotIn("notes", rows[0])
        self.assertEqual(detail_response.status_code, 404)

    def test_inspector_sees_operational_illness_fields_without_medical_details(self):
        IllnessReport.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            reported_by=self.handler_user,
            symptoms={"diarrhoea": True},
            notes="Clinical note for doctor only",
            clearance_status=ClearanceStatus.PENDING,
        )
        self.client.force_authenticate(self.inspector)

        response = self.client.get("/api/illness-reports/")

        self.assertEqual(response.status_code, 200)
        rows = data(response)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["clearance_status"], ClearanceStatus.PENDING)
        self.assertNotIn("symptoms", rows[0])
        self.assertNotIn("notes", rows[0])

    def test_facility_admin_cannot_browse_unassigned_illness_cases(self):
        IllnessReport.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            reported_by=self.handler_user,
            symptoms={"fever": True},
            notes="Private clinical note",
        )
        self.client.force_authenticate(self.facility_admin)

        response = self.client.get("/api/illness-reports/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data(response), [])
