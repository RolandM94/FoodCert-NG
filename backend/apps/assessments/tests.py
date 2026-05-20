from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.assessments.models import Appointment, FitnessDecision, MedicalAssessment
from apps.employers.models import Employer, EstablishmentCategory
from apps.facilities.models import AccreditationStatus, FacilityType, MedicalFacility, OwnershipType
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, Gender
from apps.lab_tests.models import LabTest, LabTestStatus
from apps.locations.models import State
from apps.nin_verification.models import NINVerification, NINVerificationStatus
from apps.organizations.models import Organization, OrganizationType
from apps.payments.models import PaymentStatus, PaymentTransaction

User = get_user_model()


def data(response):
    return response.data.get("data", response.data)


class MedicalAssessmentWorkflowTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.facility_org = Organization.objects.create(
            name="Mainland Diagnostics",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.state,
        )
        self.employer_org = Organization.objects.create(
            name="Clean Foods Ltd",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
        )
        self.handler_user = User.objects.create_user(
            username="handler",
            email="handler@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.state,
        )
        self.doctor = User.objects.create_user(
            username="doctor",
            email="doctor@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.state,
        )
        self.lab_staff = User.objects.create_user(
            username="lab",
            email="lab@example.com",
            password="StrongPass123!",
            role=UserRole.LAB_STAFF,
            organization=self.facility_org,
            state=self.state,
        )
        self.other_facility_org = Organization.objects.create(
            name="Island Clinic",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.state,
        )
        self.other_doctor = User.objects.create_user(
            username="other-doctor",
            email="other-doctor@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.other_facility_org,
            state=self.state,
        )
        self.other_lab_staff = User.objects.create_user(
            username="other-lab",
            email="other-lab@example.com",
            password="StrongPass123!",
            role=UserRole.LAB_STAFF,
            organization=self.other_facility_org,
            state=self.state,
        )
        self.employer_user = User.objects.create_user(
            username="employer",
            email="employer@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
            state=self.state,
        )
        self.employer = Employer.objects.create(
            user=self.employer_user,
            organization=self.employer_org,
            business_name="Clean Foods Ltd",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Ada Okafor",
            contact_person_phone="08030000002",
            contact_person_email="ops@cleanfoods.example",
            address="3 Market Road",
            state=self.state,
        )
        self.facility = MedicalFacility.objects.create(
            organization=self.facility_org,
            facility_name="Mainland Diagnostics",
            facility_type=FacilityType.DIAGNOSTIC_CENTRE,
            ownership_type=OwnershipType.PRIVATE,
            license_number="MD-001",
            address="12 Health Road",
            state=self.state,
            contact_person="Dr Ada",
            phone="08030000000",
            email="facility@example.com",
            accreditation_status=AccreditationStatus.APPROVED,
            accreditation_start_date=timezone.localdate(),
            accreditation_expiry_date=timezone.localdate() + timezone.timedelta(days=365),
        )
        self.unapproved_facility = MedicalFacility.objects.create(
            organization=Organization.objects.create(
                name="Pending Facility",
                organization_type=OrganizationType.MEDICAL_FACILITY,
                state=self.state,
            ),
            facility_name="Pending Facility",
            facility_type=FacilityType.CLINIC,
            ownership_type=OwnershipType.PRIVATE,
            license_number="PF-001",
            address="99 Pending Road",
            state=self.state,
            contact_person="Dr Ben",
            phone="08030000010",
            email="pending@example.com",
        )
        self.other_facility = MedicalFacility.objects.create(
            organization=self.other_facility_org,
            facility_name="Island Clinic",
            facility_type=FacilityType.CLINIC,
            ownership_type=OwnershipType.PRIVATE,
            license_number="IC-001",
            address="5 Island Road",
            state=self.state,
            contact_person="Dr Ola",
            phone="08030000011",
            email="island@example.com",
            accreditation_status=AccreditationStatus.APPROVED,
            accreditation_start_date=timezone.localdate(),
            accreditation_expiry_date=timezone.localdate() + timezone.timedelta(days=365),
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
            system_identifier="FCN-ASSESS001",
        )
        self.payment = PaymentTransaction.objects.create(
            payer_user=self.handler_user,
            payer_type="food_handler",
            related_entity_type="food_handler_assessment",
            related_entity_id=self.food_handler.id,
            amount="15000.00",
            payment_provider="mock",
            provider_reference="mock-assessment",
            internal_reference="ASS-ASSESS-001",
            status=PaymentStatus.SUCCESS,
            paid_at=timezone.now(),
            metadata={"facility_id": str(self.facility.id), "state_id": str(self.state.id)},
        )

    def _create_verified_assessment(self):
        NINVerification.objects.create(
            food_handler=self.food_handler,
            nin=self.food_handler.nin,
            status=NINVerificationStatus.VERIFIED,
            verified_at=timezone.now(),
            verified_full_name=self.food_handler.full_name,
            verified_date_of_birth=self.food_handler.date_of_birth,
            verified_gender=self.food_handler.gender,
            match_score="100.00",
        )
        return MedicalAssessment.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            facility=self.facility,
            payment_transaction=self.payment,
            status="payment_confirmed",
        )

    def test_food_handler_can_book_only_approved_facility(self):
        self.client.force_authenticate(self.handler_user)

        blocked = self.client.post(
            "/api/appointments/",
            {
                "food_handler": str(self.food_handler.id),
                "facility": str(self.unapproved_facility.id),
                "appointment_date": timezone.now().isoformat(),
            },
            format="json",
        )
        self.assertEqual(blocked.status_code, 400)

        response = self.client.post(
            "/api/appointments/",
            {
                "food_handler": str(self.food_handler.id),
                "facility": str(self.facility.id),
                "appointment_date": timezone.now().isoformat(),
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_assessment_created_with_pending_status_if_payment_not_successful(self):
        pending_payment = PaymentTransaction.objects.create(
            payer_user=self.handler_user,
            payer_type="food_handler",
            related_entity_type="food_handler_assessment",
            related_entity_id=self.food_handler.id,
            amount="15000.00",
            payment_provider="mock",
            internal_reference="ASS-PENDING-001",
            status=PaymentStatus.PENDING,
            metadata={"facility_id": str(self.facility.id), "state_id": str(self.state.id)},
        )
        self.client.force_authenticate(self.handler_user)

        response = self.client.post(
            "/api/assessments/",
            {
                "food_handler": str(self.food_handler.id),
                "facility": str(self.facility.id),
                "payment_transaction": str(pending_payment.id),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data(response)["status"], "payment_pending")

    def test_declaration_sets_risk_flag_and_doctor_validates(self):
        assessment = self._create_verified_assessment()
        self.client.force_authenticate(self.handler_user)

        declaration_response = self.client.post(
            f"/api/assessments/{assessment.id}/declaration/",
            {
                "diarrhoea_vomiting_last_7_days": True,
                "fever_more_than_one_week": False,
                "skin_trouble": False,
                "boils_styes_sepsis": False,
                "discharge_eye_ear_nose_mouth": False,
                "recurring_skin_or_ear_infection": False,
                "recurring_bowel_disorder": False,
                "cholera_contact_last_5_days": False,
                "diarrhoea_vomiting_contact_last_7_days": False,
                "typhoid_paratyphoid_jaundice_contact_last_21_days": False,
                "typhoid_or_paratyphoid_carrier": False,
                "previous_or_current_typhoid": False,
                "certified_true": True,
            },
            format="json",
        )

        self.assertEqual(declaration_response.status_code, 201)
        self.assertTrue(data(declaration_response)["risk_flag"])

        self.client.force_authenticate(self.doctor)
        validate_response = self.client.patch(f"/api/declarations/{data(declaration_response)['id']}/validate/")

        self.assertEqual(validate_response.status_code, 200)
        assessment.refresh_from_db()
        self.assertEqual(assessment.declaration_status, "validated")

    def test_full_workflow_allows_fit_decision_after_required_steps(self):
        assessment = self._create_verified_assessment()
        self.client.force_authenticate(self.handler_user)
        declaration_response = self.client.post(
            f"/api/assessments/{assessment.id}/declaration/",
            {
                "certified_true": True,
                "diarrhoea_vomiting_last_7_days": False,
                "fever_more_than_one_week": False,
                "skin_trouble": False,
                "boils_styes_sepsis": False,
                "discharge_eye_ear_nose_mouth": False,
                "recurring_skin_or_ear_infection": False,
                "recurring_bowel_disorder": False,
                "cholera_contact_last_5_days": False,
                "diarrhoea_vomiting_contact_last_7_days": False,
                "typhoid_paratyphoid_jaundice_contact_last_21_days": False,
                "typhoid_or_paratyphoid_carrier": False,
                "previous_or_current_typhoid": False,
            },
            format="json",
        )
        self.client.force_authenticate(self.doctor)
        self.client.patch(f"/api/declarations/{data(declaration_response)['id']}/validate/")
        exam_response = self.client.post(
            f"/api/assessments/{assessment.id}/physical-examination/",
            {
                "fever": False,
                "jaundice": False,
                "skin_infection": False,
                "boils_styes_sepsis": False,
                "discharge": False,
                "diarrhoea": False,
                "vomiting": False,
                "sore_throat_with_fever": False,
                "cough_or_flu": False,
                "known_typhoid_carrier_history": False,
            },
            format="json",
        )
        self.assertEqual(exam_response.status_code, 201)
        lab_request = self.client.post(
            f"/api/assessments/{assessment.id}/lab-tests/",
            {"tests": [{"test_type": "stool_microscopy"}, {"test_type": "hepatitis_a_antigen"}]},
            format="json",
        )
        self.assertEqual(lab_request.status_code, 201)

        self.client.force_authenticate(self.lab_staff)
        for lab_test in LabTest.objects.filter(assessment=assessment):
            result_response = self.client.patch(
                f"/api/lab-tests/{lab_test.id}/result/",
                {"status": LabTestStatus.NEGATIVE, "result_value": "Negative"},
                format="json",
            )
            self.assertEqual(result_response.status_code, 200)

        self.client.force_authenticate(self.doctor)
        for lab_test in LabTest.objects.filter(assessment=assessment):
            review_response = self.client.patch(f"/api/lab-tests/{lab_test.id}/review/")
            self.assertEqual(review_response.status_code, 200)
        vaccination_response = self.client.post(
            f"/api/assessments/{assessment.id}/vaccinations/",
            {
                "vaccine_type": "typhoid",
                "date_administered": str(timezone.localdate()),
                "dose_number": 1,
            },
            format="json",
        )
        self.assertEqual(vaccination_response.status_code, 201)

        decision_response = self.client.patch(
            f"/api/assessments/{assessment.id}/fitness-decision/",
            {"final_decision": FitnessDecision.FIT, "doctor_notes": "Fit for food handling."},
            format="json",
        )

        self.assertEqual(decision_response.status_code, 200)
        self.assertTrue(data(decision_response)["can_request_certificate"])
        assessment.refresh_from_db()
        self.assertEqual(assessment.final_decision, FitnessDecision.FIT)

    def test_final_decision_requires_verified_nin(self):
        assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            facility=self.facility,
            payment_transaction=self.payment,
            declaration_status="validated",
            physical_exam_status="completed",
            lab_status="reviewed",
            vaccination_status="reviewed",
            status="vaccination_reviewed",
        )
        self.client.force_authenticate(self.doctor)

        response = self.client.patch(
            f"/api/assessments/{assessment.id}/fitness-decision/",
            {"final_decision": FitnessDecision.FIT},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_other_facility_doctor_cannot_touch_assessment_workflow(self):
        assessment = self._create_verified_assessment()
        self.client.force_authenticate(self.handler_user)
        declaration_response = self.client.post(
            f"/api/assessments/{assessment.id}/declaration/",
            {
                "certified_true": True,
                "diarrhoea_vomiting_last_7_days": False,
                "fever_more_than_one_week": False,
                "skin_trouble": False,
                "boils_styes_sepsis": False,
                "discharge_eye_ear_nose_mouth": False,
                "recurring_skin_or_ear_infection": False,
                "recurring_bowel_disorder": False,
                "cholera_contact_last_5_days": False,
                "diarrhoea_vomiting_contact_last_7_days": False,
                "typhoid_paratyphoid_jaundice_contact_last_21_days": False,
                "typhoid_or_paratyphoid_carrier": False,
                "previous_or_current_typhoid": False,
            },
            format="json",
        )
        self.assertEqual(declaration_response.status_code, 201)

        self.client.force_authenticate(self.other_doctor)
        declaration_validate = self.client.patch(f"/api/declarations/{data(declaration_response)['id']}/validate/")
        physical_exam = self.client.post(
            f"/api/assessments/{assessment.id}/physical-examination/",
            {
                "fever": False,
                "jaundice": False,
                "skin_infection": False,
                "boils_styes_sepsis": False,
                "discharge": False,
                "diarrhoea": False,
                "vomiting": False,
                "sore_throat_with_fever": False,
                "cough_or_flu": False,
                "known_typhoid_carrier_history": False,
            },
            format="json",
        )
        lab_request = self.client.post(
            f"/api/assessments/{assessment.id}/lab-tests/",
            {"tests": [{"test_type": "stool_microscopy"}]},
            format="json",
        )

        self.assertEqual(declaration_validate.status_code, 404)
        self.assertEqual(physical_exam.status_code, 404)
        self.assertEqual(lab_request.status_code, 404)

    def test_other_facility_lab_staff_cannot_record_results(self):
        assessment = self._create_verified_assessment()
        lab_test = LabTest.objects.create(
            assessment=assessment,
            requested_by=self.doctor,
            test_type="stool_microscopy",
        )

        self.client.force_authenticate(self.other_lab_staff)
        response = self.client.patch(
            f"/api/lab-tests/{lab_test.id}/result/",
            {"status": LabTestStatus.NEGATIVE, "result_value": "Negative"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        lab_test.refresh_from_db()
        self.assertEqual(lab_test.status, "requested")
        self.assertIsNone(lab_test.resulted_by)

    def test_employer_does_not_receive_clinical_detail_payloads(self):
        assessment = self._create_verified_assessment()
        self.client.force_authenticate(self.handler_user)
        declaration_response = self.client.post(
            f"/api/assessments/{assessment.id}/declaration/",
            {
                "certified_true": True,
                "diarrhoea_vomiting_last_7_days": True,
                "fever_more_than_one_week": False,
                "skin_trouble": False,
                "boils_styes_sepsis": False,
                "discharge_eye_ear_nose_mouth": False,
                "recurring_skin_or_ear_infection": False,
                "recurring_bowel_disorder": False,
                "cholera_contact_last_5_days": False,
                "diarrhoea_vomiting_contact_last_7_days": False,
                "typhoid_paratyphoid_jaundice_contact_last_21_days": False,
                "typhoid_or_paratyphoid_carrier": False,
                "previous_or_current_typhoid": False,
            },
            format="json",
        )
        self.assertEqual(declaration_response.status_code, 201)
        LabTest.objects.create(
            assessment=assessment,
            requested_by=self.doctor,
            test_type="stool_microscopy",
            status=LabTestStatus.POSITIVE,
            result_value="Positive",
            result_notes="Restricted clinical note",
        )
        assessment.doctor_notes = "Restricted doctor note"
        assessment.save(update_fields=["doctor_notes", "updated_at"])

        self.client.force_authenticate(self.employer_user)
        employer_assessment = self.client.get(f"/api/assessments/{assessment.id}/")
        employer_declarations = self.client.get("/api/declarations/")
        employer_lab_tests = self.client.get("/api/lab-tests/")

        self.assertEqual(employer_assessment.status_code, 200)
        employer_payload = data(employer_assessment)
        self.assertNotIn("doctor_notes", employer_payload)
        self.assertNotIn("lab_tests", employer_payload)
        self.assertEqual(employer_declarations.status_code, 200)
        self.assertEqual(data(employer_declarations), [])
        self.assertEqual(employer_lab_tests.status_code, 200)
        self.assertEqual(data(employer_lab_tests), [])
