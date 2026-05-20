from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.assessments.models import FitnessDecision, MedicalAssessment
from apps.certificates.models import Certificate, CertificateRequest
from apps.certificates.services import CertificateService
from apps.employers.models import Employer, EstablishmentCategory
from apps.facilities.models import AccreditationStatus, FacilityType, MedicalFacility, OwnershipType
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, Gender
from apps.inspections.models import EnforcementAction, Inspection, InspectionResponse, InspectionResponseType, InspectionStatus
from apps.locations.models import State
from apps.nin_verification.models import NINVerification, NINVerificationStatus
from apps.notifications.models import Notification, NotificationType
from apps.organizations.models import Organization, OrganizationType, OrganizationUnit, OrganizationUnitType
from apps.payments.models import PaymentStatus, PaymentTransaction

User = get_user_model()


def data(response):
    if isinstance(response.data, list):
        return response.data
    return response.data.get("data", response.data)


class InspectionWorkflowTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.employer_org = Organization.objects.create(name="Clean Foods", organization_type=OrganizationType.EMPLOYER, state=self.state)
        self.facility_org = Organization.objects.create(name="Mainland Clinic", organization_type=OrganizationType.MEDICAL_FACILITY, state=self.state)
        self.inspector = User.objects.create_user("inspector", "inspector@example.com", "StrongPass123!", role=UserRole.INSPECTOR, state=self.state)
        self.state_admin = User.objects.create_user("state-admin", "state@example.com", "StrongPass123!", role=UserRole.STATE_ADMIN, state=self.state)
        self.doctor = User.objects.create_user(
            "doctor",
            "doctor@example.com",
            "StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.state,
        )
        self.employer_user = User.objects.create_user(
            "employer",
            "employer@example.com",
            "StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
            state=self.state,
        )
        self.handler_user = User.objects.create_user("handler", "handler@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.state)
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
        self.facility = MedicalFacility.objects.create(
            organization=self.facility_org,
            facility_name="Mainland Clinic",
            facility_type=FacilityType.CLINIC,
            ownership_type=OwnershipType.PRIVATE,
            license_number="MC-001",
            address="12 Health Road",
            state=self.state,
            contact_person="Dr Ada",
            phone="08030000001",
            email="clinic@example.com",
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
            system_identifier="FCN-INSP001",
        )

    def _certificate(self):
        NINVerification.objects.create(
            food_handler=self.food_handler,
            nin=self.food_handler.nin,
            status=NINVerificationStatus.VERIFIED,
            verified_at=timezone.now(),
            match_score="100.00",
        )
        payment = PaymentTransaction.objects.create(
            payer_user=self.handler_user,
            payer_type="food_handler",
            related_entity_type="food_handler_assessment",
            related_entity_id=self.food_handler.id,
            amount="15000.00",
            payment_provider="mock",
            internal_reference="ASS-INSP-001",
            status=PaymentStatus.SUCCESS,
            paid_at=timezone.now(),
        )
        assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            payment_transaction=payment,
            declaration_status="validated",
            physical_exam_status="completed",
            lab_status="reviewed",
            vaccination_status="reviewed",
            final_decision=FitnessDecision.FIT,
            status="fit",
            signed_at=timezone.now(),
        )
        CertificateRequest.objects.create(assessment=assessment, status="approved", reviewed_by=self.state_admin, reviewed_at=timezone.now())
        return CertificateService.issue_certificate(assessment=assessment, actor=self.state_admin)

    def test_inspector_can_submit_inspection_with_score_and_notice(self):
        self.client.force_authenticate(self.inspector)
        response = self.client.post(
            "/api/inspections/",
            {
                "employer": str(self.employer.id),
                "checklist_responses": {
                    "all_food_handlers_registered": True,
                    "certificates_valid": False,
                    "handwashing_available": True,
                },
                "enforcement_action": EnforcementAction.COMPLIANCE_NOTICE,
                "findings": "One certificate expired.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        inspection_id = data(response)["id"]
        submit_response = self.client.patch(f"/api/inspections/{inspection_id}/submit/")

        self.assertEqual(submit_response.status_code, 200)
        self.assertEqual(data(submit_response)["status"], InspectionStatus.SUBMITTED)
        self.assertEqual(data(submit_response)["compliance_score"], "66.67")
        self.assertTrue(Notification.objects.filter(recipient=self.employer_user, notification_type=NotificationType.COMPLIANCE_NOTICE).exists())

    def test_inspector_can_add_evidence_and_scan_certificate(self):
        certificate = self._certificate()
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer)
        self.client.force_authenticate(self.inspector)

        evidence_response = self.client.post(
            f"/api/inspections/{inspection.id}/evidence/",
            {"file_url": "https://example.com/evidence/photo.jpg", "description": "Kitchen notice"},
            format="json",
        )
        self.assertEqual(evidence_response.status_code, 200)
        self.assertEqual(len(data(evidence_response)["evidence_files"]), 1)

        scan_response = self.client.post(
            f"/api/inspections/{inspection.id}/scan-certificate/",
            {"certificate_number": certificate.certificate_number},
            format="json",
        )
        self.assertEqual(scan_response.status_code, 201)
        self.assertEqual(data(scan_response)["result"], "valid")

    def test_employer_can_view_own_inspection_report(self):
        Inspection.objects.create(inspector=self.inspector, employer=self.employer, status=InspectionStatus.SUBMITTED)
        self.client.force_authenticate(self.employer_user)

        response = self.client.get("/api/inspections/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data(response)), 1)

    def test_employer_can_view_nested_inspection_history_and_detail(self):
        inspection = Inspection.objects.create(
            inspector=self.inspector,
            employer=self.employer,
            checklist_responses={"handwashing_available": True, "certificates_valid": False},
            compliance_score="50.00",
            findings="Handwashing station needs supplies.",
            evidence_files=[{"file_url": "https://example.com/evidence/photo.jpg", "description": "Sink area"}],
            status=InspectionStatus.SUBMITTED,
            submitted_at=timezone.now(),
        )
        InspectionResponse.objects.create(
            inspection=inspection,
            submitted_by=self.employer_user,
            response_type=InspectionResponseType.ACKNOWLEDGE,
            content="We have received the notice.",
        )
        self.client.force_authenticate(self.employer_user)

        list_response = self.client.get(f"/api/employers/{self.employer.id}/inspections/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(data(list_response)), 1)
        self.assertEqual(data(list_response)[0]["response_count"], 1)

        detail_response = self.client.get(f"/api/employers/{self.employer.id}/inspections/{inspection.id}/")
        self.assertEqual(detail_response.status_code, 200)
        payload = data(detail_response)
        self.assertEqual(payload["checklist_responses"]["certificates_valid"], False)
        self.assertEqual(payload["evidence_files"][0]["description"], "Sink area")
        self.assertEqual(payload["responses"][0]["response_type"], InspectionResponseType.ACKNOWLEDGE)

    def test_employer_can_submit_inspection_response(self):
        inspection = Inspection.objects.create(
            inspector=self.inspector,
            employer=self.employer,
            findings="Display certificates at service counter.",
            status=InspectionStatus.SUBMITTED,
        )
        self.client.force_authenticate(self.employer_user)

        response = self.client.post(
            f"/api/employers/{self.employer.id}/inspections/{inspection.id}/responses/",
            {
                "response_type": InspectionResponseType.CORRECTIVE_ACTION,
                "content": "Certificates have been displayed.",
                "evidence_file_url": "https://example.com/evidence/corrective-action.jpg",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        payload = data(response)
        self.assertEqual(payload["response_type"], InspectionResponseType.CORRECTIVE_ACTION)
        inspection.refresh_from_db()
        self.assertEqual(inspection.status, InspectionStatus.EMPLOYER_RESPONSE_SUBMITTED)

    def test_branch_manager_can_only_respond_to_branch_inspection(self):
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
        branch_inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer, branch=branch, status=InspectionStatus.SUBMITTED)
        other_inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer, branch=other_branch, status=InspectionStatus.SUBMITTED)
        branch_manager = User.objects.create_user(
            "branch-response-manager",
            "branch-response-manager@example.com",
            "StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
            unit=branch,
            unit_restricted=True,
        )

        self.client.force_authenticate(branch_manager)
        list_response = self.client.get(f"/api/employers/{self.employer.id}/inspections/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(data(list_response)), 1)
        self.assertEqual(data(list_response)[0]["id"], str(branch_inspection.id))

        allowed_response = self.client.post(
            f"/api/employers/{self.employer.id}/inspections/{branch_inspection.id}/responses/",
            {"response_type": InspectionResponseType.COMMENT, "content": "Branch manager comment."},
            format="json",
        )
        self.assertEqual(allowed_response.status_code, 201)

        denied_response = self.client.post(
            f"/api/employers/{self.employer.id}/inspections/{other_inspection.id}/responses/",
            {"response_type": InspectionResponseType.COMMENT, "content": "Wrong branch."},
            format="json",
        )
        self.assertEqual(denied_response.status_code, 400)

    def test_branch_specific_inspection_is_scoped_to_branch_manager(self):
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
        Inspection.objects.create(inspector=self.inspector, employer=self.employer, branch=branch, status=InspectionStatus.SUBMITTED)
        Inspection.objects.create(inspector=self.inspector, employer=self.employer, branch=other_branch, status=InspectionStatus.SUBMITTED)
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
        response = self.client.get("/api/inspections/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data(response)), 1)
        self.assertEqual(str(data(response)[0]["branch"]), str(branch.id))

    def test_inspection_branch_must_belong_to_employer_organization(self):
        other_org = Organization.objects.create(name="Other Foods", organization_type=OrganizationType.EMPLOYER, state=self.state)
        bad_branch = OrganizationUnit.objects.create(
            organization=other_org,
            name="Other Branch",
            unit_type=OrganizationUnitType.BRANCH,
        )
        self.client.force_authenticate(self.inspector)
        response = self.client.post(
            "/api/inspections/",
            {"employer": str(self.employer.id), "branch": str(bad_branch.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
