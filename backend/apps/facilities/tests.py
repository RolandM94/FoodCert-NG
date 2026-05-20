from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.facilities.models import AccreditationStatus, FacilityAccreditationApplication, MedicalFacility
from apps.locations.models import State
from apps.organizations.models import Organization, OrganizationType

User = get_user_model()


def data(response):
    return response.data.get("data", response.data)


class FacilityAccreditationWorkflowTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.facility_org = Organization.objects.create(
            name="Lagos Diagnostics",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.lagos,
        )
        self.facility_admin = User.objects.create_user(
            username="facility-admin",
            email="facility-admin@example.com",
            password="StrongPass123!",
            role=UserRole.FACILITY_ADMIN,
            organization=self.facility_org,
            state=self.lagos,
        )
        self.lagos_state_admin = User.objects.create_user(
            username="lagos-state-admin",
            email="lagos-state-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )
        self.oyo_state_admin = User.objects.create_user(
            username="oyo-state-admin",
            email="oyo-state-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.oyo,
        )

    def _facility_payload(self):
        return {
            "facility_name": "Lagos Diagnostics",
            "facility_type": "diagnostic_centre",
            "ownership_type": "private",
            "license_number": "LAG-MED-001",
            "registration_number": "RC-001",
            "address": "12 Health Road",
            "state": str(self.lagos.id),
            "contact_person": "Dr Ada",
            "phone": "08030000000",
            "email": "facility@example.com",
            "standard_assessment_price": "15000.00",
        }

    def _checklist_payload(self, facility_id):
        return {
            "facility": str(facility_id),
            "has_reporting_policy": True,
            "has_medical_records_computers": True,
            "has_computer_operators": True,
            "has_standard_forms": True,
            "has_laboratory_request_forms": True,
            "has_patient_files": True,
            "has_qr_certificate_capability": True,
            "has_internet_access": True,
            "has_trained_records_staff": True,
            "has_trained_clinical_staff": True,
            "has_trained_non_clinical_staff": True,
        }

    def _create_facility_and_application(self):
        self.client.force_authenticate(self.facility_admin)
        facility_response = self.client.post("/api/medical-facilities/", self._facility_payload(), format="json")
        self.assertEqual(facility_response.status_code, 201)
        app_response = self.client.post(
            "/api/facility-accreditation/",
            self._checklist_payload(data(facility_response)["id"]),
            format="json",
        )
        self.assertEqual(app_response.status_code, 201)
        return data(facility_response), data(app_response)

    def test_facility_admin_can_register_facility_and_apply(self):
        facility, application = self._create_facility_and_application()

        self.assertEqual(facility["accreditation_status"], AccreditationStatus.DRAFT)
        self.assertEqual(application["application_status"], AccreditationStatus.DRAFT)
        self.assertTrue(application["checklist_complete"])

    def test_incomplete_checklist_cannot_be_submitted(self):
        self.client.force_authenticate(self.facility_admin)
        facility_response = self.client.post("/api/medical-facilities/", self._facility_payload(), format="json")
        payload = self._checklist_payload(data(facility_response)["id"])
        payload["has_internet_access"] = False
        app_response = self.client.post("/api/facility-accreditation/", payload, format="json")

        submit_response = self.client.patch(f"/api/facility-accreditation/{data(app_response)['id']}/submit/")

        self.assertEqual(submit_response.status_code, 400)

    def test_state_admin_can_approve_only_own_state_facility(self):
        facility, application = self._create_facility_and_application()
        self.client.force_authenticate(self.facility_admin)
        submit_response = self.client.patch(f"/api/facility-accreditation/{application['id']}/submit/")
        self.assertEqual(submit_response.status_code, 200)

        self.client.force_authenticate(self.oyo_state_admin)
        blocked_response = self.client.patch(
            f"/api/facility-accreditation/{application['id']}/approve/",
            {"review_comment": "Wrong state"},
            format="json",
        )
        self.assertEqual(blocked_response.status_code, 404)

        self.client.force_authenticate(self.lagos_state_admin)
        approve_response = self.client.patch(
            f"/api/facility-accreditation/{application['id']}/approve/",
            {"review_comment": "Approved"},
            format="json",
        )

        self.assertEqual(approve_response.status_code, 200)
        self.assertEqual(data(approve_response)["application_status"], AccreditationStatus.APPROVED)
        db_facility = MedicalFacility.objects.get(id=facility["id"])
        self.assertEqual(db_facility.accreditation_status, AccreditationStatus.APPROVED)
        self.assertTrue(db_facility.can_conduct_assessments)
        self.assertIsNotNone(db_facility.accreditation_expiry_date)

    def test_suspended_facility_cannot_conduct_assessments(self):
        facility, application = self._create_facility_and_application()
        self.client.force_authenticate(self.facility_admin)
        self.client.patch(f"/api/facility-accreditation/{application['id']}/submit/")
        self.client.force_authenticate(self.lagos_state_admin)
        self.client.patch(f"/api/facility-accreditation/{application['id']}/approve/", {}, format="json")

        suspend_response = self.client.patch(
            f"/api/facility-accreditation/{application['id']}/suspend/",
            {"review_comment": "Compliance issue"},
            format="json",
        )

        self.assertEqual(suspend_response.status_code, 200)
        db_facility = MedicalFacility.objects.get(id=facility["id"])
        self.assertEqual(db_facility.accreditation_status, AccreditationStatus.SUSPENDED)
        self.assertFalse(db_facility.can_conduct_assessments)

    def test_facility_cannot_approve_itself(self):
        _, application = self._create_facility_and_application()
        self.client.force_authenticate(self.facility_admin)
        self.client.patch(f"/api/facility-accreditation/{application['id']}/submit/")

        response = self.client.patch(f"/api/facility-accreditation/{application['id']}/approve/", {}, format="json")

        self.assertEqual(response.status_code, 403)

    def test_reject_updates_facility_status(self):
        facility, application = self._create_facility_and_application()
        self.client.force_authenticate(self.facility_admin)
        self.client.patch(f"/api/facility-accreditation/{application['id']}/submit/")
        self.client.force_authenticate(self.lagos_state_admin)

        response = self.client.patch(
            f"/api/facility-accreditation/{application['id']}/reject/",
            {"review_comment": "Missing documents"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data(response)["application_status"], AccreditationStatus.REJECTED)
        db_facility = MedicalFacility.objects.get(id=facility["id"])
        self.assertEqual(db_facility.accreditation_status, AccreditationStatus.REJECTED)
