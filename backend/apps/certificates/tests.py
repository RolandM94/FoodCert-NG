from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.assessments.models import AssessmentStatus, FitnessDecision, MedicalAssessment
from apps.certificates.models import Certificate, CertificateRequest, CertificateRequestStatus, VerificationResult
from apps.employers.models import Employer, EstablishmentCategory
from apps.facilities.models import AccreditationStatus, FacilityType, MedicalFacility, OwnershipType
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, Gender
from apps.locations.models import State
from apps.nin_verification.models import NINVerification, NINVerificationStatus
from apps.organizations.models import Organization, OrganizationType
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.policy.models import StatePolicyConfig
from apps.reports.models import GeneratedReport, GeneratedReportStatus, ReportFormat, ReportType

User = get_user_model()


def data(response):
    return response.data.get("data", response.data)


class CertificateIssuanceTests(APITestCase):
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
        self.facility_admin = User.objects.create_user(
            username="facility-admin",
            email="facility-admin@example.com",
            password="StrongPass123!",
            role=UserRole.FACILITY_ADMIN,
            organization=self.facility_org,
            state=self.state,
        )
        self.state_admin = User.objects.create_user(
            username="state-admin",
            email="state-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.state,
        )
        self.employer = Employer.objects.create(
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
            system_identifier="FCN-CERT001",
        )
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
        self.payment = PaymentTransaction.objects.create(
            payer_user=self.handler_user,
            payer_type="food_handler",
            related_entity_type="food_handler_assessment",
            related_entity_id=self.food_handler.id,
            amount="15000.00",
            payment_provider="mock",
            provider_reference="mock-assessment",
            internal_reference="ASS-CERT-001",
            status=PaymentStatus.SUCCESS,
            paid_at=timezone.now(),
            metadata={"facility_id": str(self.facility.id), "state_id": str(self.state.id)},
        )
        self.assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            payment_transaction=self.payment,
            declaration_status="validated",
            physical_exam_status="completed",
            lab_status="reviewed",
            vaccination_status="reviewed",
            final_decision=FitnessDecision.FIT,
            status="fit",
            signed_at=timezone.now(),
        )
        GeneratedReport.objects.create(
            report_type=ReportType.MEDICAL_EXAMINATION,
            file_format=ReportFormat.JSON,
            filters={"assessment_id": str(self.assessment.id)},
            generated_by=self.doctor,
            status=GeneratedReportStatus.GENERATED,
        )

    def test_assessment_submit_to_state_alias_syncs_status_and_blocks_direct_issuance(self):
        self.client.force_authenticate(self.facility_admin)

        response = self.client.post(
            f"/api/assessments/{self.assessment.id}/submit-to-state/",
            {"request_notes": "Ready for State validation."},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data(response)["status"], CertificateRequestStatus.PENDING_VALIDATION)
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.status, AssessmentStatus.SUBMITTED_FOR_STATE_VALIDATION)

        blocked = self.client.post(
            "/api/certificates/generate/",
            {"certificate_request": data(response)["id"]},
            format="json",
        )
        self.assertEqual(blocked.status_code, 400)

    def test_clarification_approval_and_issue_sync_assessment_statuses(self):
        certificate_request = CertificateRequest.objects.create(
            assessment=self.assessment,
            requested_by=self.facility_admin,
            status=CertificateRequestStatus.PENDING_VALIDATION,
        )
        self.client.force_authenticate(self.state_admin)

        clarification = self.client.patch(
            f"/api/certificate-requests/{certificate_request.id}/request-clarification/",
            {"review_notes": "Confirm vaccination evidence."},
            format="json",
        )
        self.assertEqual(clarification.status_code, 200)
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.status, AssessmentStatus.STATE_CLARIFICATION_REQUESTED)

        self.client.force_authenticate(self.facility_admin)
        response = self.client.post(
            f"/api/facilities/{self.facility.id}/assessments/{self.assessment.id}/respond-to-clarification/",
            {"response": "Vaccination evidence confirmed."},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.status, AssessmentStatus.STATE_CLARIFICATION_RESPONDED)

        self.client.force_authenticate(self.state_admin)
        approve = self.client.patch(
            f"/api/certificate-requests/{certificate_request.id}/approve/",
            {"review_notes": "Approved."},
            format="json",
        )
        self.assertEqual(approve.status_code, 200)
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.status, AssessmentStatus.APPROVED_BY_STATE)

        issue = self.client.post(
            "/api/certificates/generate/",
            {"certificate_request": str(certificate_request.id)},
            format="json",
        )
        self.assertEqual(issue.status_code, 201)
        self.assessment.refresh_from_db()
        self.food_handler.refresh_from_db()
        self.assertEqual(self.assessment.status, AssessmentStatus.CERTIFICATE_ISSUED)
        self.assertEqual(self.food_handler.current_status, "fit")

    def test_certificate_request_requires_state_approval_before_generation(self):
        self.client.force_authenticate(self.doctor)
        request_response = self.client.post(
            f"/api/assessments/{self.assessment.id}/request-certificate/",
            {"request_notes": "Ready for state review."},
            format="json",
        )
        self.assertEqual(request_response.status_code, 201)
        certificate_request = data(request_response)
        self.assertEqual(certificate_request["status"], "pending_validation")

        blocked_generate = self.client.post(
            "/api/certificates/generate/",
            {"certificate_request": certificate_request["id"]},
            format="json",
        )
        self.assertEqual(blocked_generate.status_code, 400)

        self.client.force_authenticate(self.state_admin)
        approve_response = self.client.patch(
            f"/api/certificate-requests/{certificate_request['id']}/approve/",
            {"review_notes": "Approved by Lagos SMOH."},
            format="json",
        )
        self.assertEqual(approve_response.status_code, 200)
        self.assertEqual(data(approve_response)["status"], "approved")

        generate_response = self.client.post(
            "/api/certificates/generate/",
            {"certificate_request": certificate_request["id"]},
            format="json",
        )
        self.assertEqual(generate_response.status_code, 201)
        certificate = data(generate_response)
        self.assertTrue(certificate["certificate_number"].startswith("FCN-LA-"))
        self.assertEqual(certificate["status"], "active")
        self.assertTrue(certificate["qr_code_url"])
        self.assertTrue(certificate["pdf_url"])

    def test_public_verification_hides_private_medical_data(self):
        certificate_request = CertificateRequest.objects.create(
            assessment=self.assessment,
            requested_by=self.doctor,
            status="approved",
            reviewed_by=self.state_admin,
            reviewed_at=timezone.now(),
        )
        self.client.force_authenticate(self.state_admin)
        generate_response = self.client.post(
            "/api/certificates/generate/",
            {"certificate_request": str(certificate_request.id)},
            format="json",
        )
        certificate_number = data(generate_response)["certificate_number"]
        self.client.force_authenticate(user=None)

        verify_response = self.client.get(f"/api/public/certificates/verify/{certificate_number}/")

        self.assertEqual(verify_response.status_code, 200)
        payload = data(verify_response)
        self.assertEqual(payload["certificate_validity"], VerificationResult.VALID)
        self.assertEqual(payload["food_handler_name"], "Ada Okafor")
        self.assertNotIn("masked_nin", payload)
        self.assertNotIn("doctor_notes", payload)
        self.assertNotIn("lab_tests", payload)

    def test_employer_certificate_view_uses_limited_privacy_payload(self):
        self.employer.user = User.objects.create_user(
            username="employer",
            email="employer@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
            state=self.state,
        )
        self.employer.save(update_fields=["user", "updated_at"])
        certificate_request = CertificateRequest.objects.create(
            assessment=self.assessment,
            requested_by=self.doctor,
            status="approved",
            reviewed_by=self.state_admin,
            reviewed_at=timezone.now(),
        )
        self.client.force_authenticate(self.state_admin)
        certificate_response = self.client.post(
            "/api/certificates/generate/",
            {"certificate_request": str(certificate_request.id)},
            format="json",
        )
        certificate_id = data(certificate_response)["id"]

        self.client.force_authenticate(self.employer.user)
        response = self.client.get(f"/api/certificates/{certificate_id}/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertIn("certificate_validity", payload)
        self.assertIn("fitness_status", payload)
        self.assertNotIn("masked_nin", payload)
        self.assertNotIn("doctor_name", payload)
        self.assertNotIn("digital_signature_hash", payload)
        self.assertNotIn("pdf_url", payload)

    def test_revoked_certificate_verifies_as_revoked(self):
        certificate_request = CertificateRequest.objects.create(
            assessment=self.assessment,
            requested_by=self.doctor,
            status="approved",
            reviewed_by=self.state_admin,
            reviewed_at=timezone.now(),
        )
        self.client.force_authenticate(self.state_admin)
        certificate_response = self.client.post(
            "/api/certificates/generate/",
            {"certificate_request": str(certificate_request.id)},
            format="json",
        )
        certificate_id = data(certificate_response)["id"]
        certificate_number = data(certificate_response)["certificate_number"]

        revoke_response = self.client.patch(
            f"/api/certificates/{certificate_id}/revoke/",
            {"reason": "Fraud report confirmed."},
            format="json",
        )
        self.assertEqual(revoke_response.status_code, 200)

        self.client.force_authenticate(user=None)
        verify_response = self.client.get(f"/api/public/certificates/verify/{certificate_number}/")

        self.assertEqual(verify_response.status_code, 200)
        self.assertEqual(data(verify_response)["certificate_validity"], VerificationResult.REVOKED)

    def test_non_fit_assessment_cannot_request_certificate(self):
        self.assessment.final_decision = FitnessDecision.NOT_FIT
        self.assessment.save(update_fields=["final_decision", "updated_at"])
        self.client.force_authenticate(self.doctor)

        response = self.client.post(f"/api/assessments/{self.assessment.id}/request-certificate/", {}, format="json")

        self.assertEqual(response.status_code, 400)

    def test_policy_can_disable_state_validation(self):
        StatePolicyConfig.objects.create(state=self.state, requires_state_certificate_validation=False)
        self.client.force_authenticate(self.doctor)
        response = self.client.post(
            "/api/certificates/generate/",
            {"assessment": str(self.assessment.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Certificate.objects.count(), 1)
