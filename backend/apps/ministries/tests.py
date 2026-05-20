from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.accounts.services import InviteService
from apps.assessments.models import FitnessDecision, MedicalAssessment
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.certificates.models import Certificate, CertificateRequest, CertificateRequestStatus, CertificateStatus
from apps.facilities.models import AccreditationStatus, FacilityAccreditationApplication, FacilityType, MedicalFacility, OwnershipType
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, Gender
from apps.illness.models import IllnessReport
from apps.inspections.models import EnforcementAction, Inspection, InspectionStatus
from apps.locations.models import LGA
from apps.locations.models import State
from apps.ministries.models import FederalStateQueryStatus, MinistryStaffProfile, MinistryStaffRole, MinistryType, StateReport, StateReportStatus
from apps.ministries.permissions import (
    can_assign_inspections,
    can_manage_federal_queries,
    can_manage_national_policy,
    can_manage_state_fees,
    can_manage_state_users,
    can_review_facility_accreditation,
    can_review_state_reports,
    can_submit_state_reports,
    can_validate_certificates,
    effective_state_id,
)
from apps.organizations.models import Organization, OrganizationType, OrganizationUnitType
from apps.nin_verification.models import NINVerification, NINVerificationStatus
from apps.payments.models import AssessmentFee, PayerType, PaymentStatus, PaymentTransaction
from apps.policy.models import NationalPolicyConfig, StatePolicyConfig
from apps.settlements.models import Settlement, SettlementStatus


User = get_user_model()


def payload(response):
    if isinstance(response.data, dict):
        return response.data.get("data", response.data)
    return response.data


class MinistryNamespaceTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.state_admin = User.objects.create_user(
            "lagos-state",
            "lagos-state@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )
        self.federal_admin = User.objects.create_user(
            "federal-admin",
            "federal-admin@example.com",
            "StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.employer = User.objects.create_user(
            "employer-user",
            "employer-user@example.com",
            "StrongPass123!",
            role=UserRole.EMPLOYER,
            state=self.lagos,
        )

    def test_state_dashboard_alias_requires_state_ministry_role(self):
        self.client.force_authenticate(self.employer)

        response = self.client.get("/api/state/dashboard/")

        self.assertEqual(response.status_code, 403)

    def test_state_dashboard_alias_uses_existing_dashboard_payload(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state/dashboard/")

        self.assertEqual(response.status_code, 200)
        data = payload(response)
        self.assertEqual(data["state"]["name"], "Lagos")
        self.assertIn("registered_food_handlers", data["cards"])

    def test_federal_dashboard_alias_requires_federal_ministry_role(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/federal/dashboard/")

        self.assertEqual(response.status_code, 403)

    def test_federal_dashboard_alias_uses_existing_dashboard_payload(self):
        self.client.force_authenticate(self.federal_admin)

        response = self.client.get("/api/federal/dashboard/")

        self.assertEqual(response.status_code, 200)
        data = payload(response)
        self.assertIn("national_certification_coverage", data["cards"])


class MinistryPermissionHelperTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.state_admin = User.objects.create_user(
            "state-admin",
            "state-admin@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )
        self.federal_admin = User.objects.create_user(
            "federal-policy",
            "federal-policy@example.com",
            "StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )

    def test_state_admin_without_profile_keeps_full_legacy_state_permissions(self):
        self.assertTrue(can_manage_state_users(self.state_admin))
        self.assertTrue(can_review_facility_accreditation(self.state_admin))
        self.assertTrue(can_validate_certificates(self.state_admin))
        self.assertTrue(can_manage_state_fees(self.state_admin))
        self.assertTrue(can_assign_inspections(self.state_admin))
        self.assertTrue(can_submit_state_reports(self.state_admin))

    def test_state_sub_role_limits_actions_to_assigned_duties(self):
        MinistryStaffProfile.objects.create(
            user=self.state_admin,
            ministry_type=MinistryType.STATE,
            sub_role=MinistryStaffRole.CERTIFICATE_VERIFICATION_OFFICER,
            state=self.lagos,
        )

        self.assertTrue(can_validate_certificates(self.state_admin))
        self.assertFalse(can_review_facility_accreditation(self.state_admin))
        self.assertFalse(can_manage_state_fees(self.state_admin))
        self.assertEqual(effective_state_id(self.state_admin), self.lagos.id)

    def test_federal_sub_role_limits_policy_and_query_actions(self):
        MinistryStaffProfile.objects.create(
            user=self.federal_admin,
            ministry_type=MinistryType.FEDERAL,
            sub_role=MinistryStaffRole.NATIONAL_POLICY_OFFICER,
        )

        self.assertTrue(can_manage_national_policy(self.federal_admin))
        self.assertFalse(can_review_state_reports(self.federal_admin))
        self.assertFalse(can_manage_federal_queries(self.federal_admin))


class StateMinistryManagementEndpointTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.ikeja = LGA.objects.create(name="Ikeja", state=self.lagos)
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.lagos_org = Organization.objects.create(
            name="Lagos Ministry of Health",
            organization_type=OrganizationType.STATE_MINISTRY,
            state=self.lagos,
        )
        self.state_admin = User.objects.create_user(
            "lagos-admin",
            "lagos-admin@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
            organization=self.lagos_org,
        )
        self.other_admin = User.objects.create_user(
            "oyo-admin",
            "oyo-admin@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.oyo,
        )

    def test_state_units_endpoint_uses_authenticated_state_organization(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(
            "/api/state/units/",
            {"name": "Food Safety Directorate", "unit_type": OrganizationUnitType.DIRECTORATE},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(str(payload(response)["organization"]), str(self.lagos_org.id))

        list_response = self.client.get("/api/state/units/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(payload(list_response)), 1)

    def test_other_state_admin_cannot_access_lagos_state_unit_detail(self):
        self.client.force_authenticate(self.state_admin)
        created = self.client.post(
            "/api/state/units/",
            {"name": "Verification Desk", "unit_type": OrganizationUnitType.UNIT},
            format="json",
        )
        unit_id = payload(created)["id"]

        self.client.force_authenticate(self.other_admin)
        response = self.client.get(f"/api/state/units/{unit_id}/")

        self.assertEqual(response.status_code, 404)

    def test_state_invite_endpoint_records_ministry_staff_role(self):
        self.client.force_authenticate(self.state_admin)
        unit_response = self.client.post(
            "/api/state/units/",
            {"name": "Ikeja LGA Office", "unit_type": OrganizationUnitType.LGA_OFFICE, "lga": str(self.ikeja.id)},
            format="json",
        )

        response = self.client.post(
            "/api/state/invites/",
            {
                "email": "verifier@example.com",
                "role": UserRole.STATE_ADMIN,
                "ministry_staff_role": MinistryStaffRole.CERTIFICATE_VERIFICATION_OFFICER,
                "unit": payload(unit_response)["id"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(payload(response)["ministry_staff_role"], MinistryStaffRole.CERTIFICATE_VERIFICATION_OFFICER)

    def test_accepting_state_invite_creates_ministry_profile(self):
        invite = InviteService.create_invite(
            actor=self.state_admin,
            organization=self.lagos_org,
            email="finance@example.com",
            role=UserRole.STATE_ADMIN,
            ministry_staff_role=MinistryStaffRole.POLICY_FINANCE_OFFICER,
        )

        response = self.client.post(
            f"/api/invites/{invite.token}/accept/",
            {"username": "finance-user", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        invited_user = User.objects.get(email="finance@example.com")
        self.assertEqual(invited_user.ministry_profile.sub_role, MinistryStaffRole.POLICY_FINANCE_OFFICER)
        self.assertEqual(invited_user.ministry_profile.state, self.lagos)


class StateFacilityAccreditationEndpointTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.lagos_org = Organization.objects.create(
            name="Lagos Clinic",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.lagos,
        )
        self.oyo_org = Organization.objects.create(
            name="Oyo Clinic",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.oyo,
        )
        self.facility = MedicalFacility.objects.create(
            organization=self.lagos_org,
            facility_name="Lagos Clinic",
            facility_type=FacilityType.CLINIC,
            ownership_type=OwnershipType.PRIVATE,
            license_number="LAG-001",
            address="1 Health Road",
            state=self.lagos,
            contact_person="Dr Ada",
            phone="08030000000",
            email="lagos-clinic@example.com",
            accreditation_status=AccreditationStatus.SUBMITTED,
        )
        self.oyo_facility = MedicalFacility.objects.create(
            organization=self.oyo_org,
            facility_name="Oyo Clinic",
            facility_type=FacilityType.CLINIC,
            ownership_type=OwnershipType.PRIVATE,
            license_number="OYO-001",
            address="2 Health Road",
            state=self.oyo,
            contact_person="Dr Bisi",
            phone="08030000001",
            email="oyo-clinic@example.com",
            accreditation_status=AccreditationStatus.SUBMITTED,
        )
        self.application = FacilityAccreditationApplication.objects.create(
            facility=self.facility,
            application_status=AccreditationStatus.SUBMITTED,
            has_reporting_policy=True,
            has_medical_records_computers=True,
            has_computer_operators=True,
            has_standard_forms=True,
            has_laboratory_request_forms=True,
            has_patient_files=True,
            has_qr_certificate_capability=True,
            has_internet_access=True,
            has_trained_records_staff=True,
            has_trained_clinical_staff=True,
            has_trained_non_clinical_staff=True,
        )
        self.oyo_application = FacilityAccreditationApplication.objects.create(
            facility=self.oyo_facility,
            application_status=AccreditationStatus.SUBMITTED,
        )
        self.state_admin = User.objects.create_user(
            "facility-reviewer",
            "facility-reviewer@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )
        self.other_state_admin = User.objects.create_user(
            "oyo-reviewer",
            "oyo-reviewer@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.oyo,
        )
        self.verifier = User.objects.create_user(
            "certificate-verifier",
            "certificate-verifier@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )
        MinistryStaffProfile.objects.create(
            user=self.verifier,
            ministry_type=MinistryType.STATE,
            sub_role=MinistryStaffRole.CERTIFICATE_VERIFICATION_OFFICER,
            state=self.lagos,
        )

    def test_state_facilities_are_scoped_to_current_state(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state/facilities/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload(response)), 1)
        self.assertEqual(payload(response)[0]["facility_name"], "Lagos Clinic")

    def test_state_accreditation_queue_lists_current_state_applications(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state/facilities/applications/?queue=pending")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload(response)), 1)
        self.assertEqual(payload(response)[0]["facility_name"], "Lagos Clinic")

    def test_state_reviewer_can_approve_application(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.patch(
            f"/api/state/facilities/applications/{self.application.id}/approve/",
            {"review_comment": "Meets requirements"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload(response)["application_status"], AccreditationStatus.APPROVED)
        self.facility.refresh_from_db()
        self.assertEqual(self.facility.accreditation_status, AccreditationStatus.APPROVED)

    def test_reject_requires_review_comment(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.patch(f"/api/state/facilities/applications/{self.application.id}/reject/", {}, format="json")

        self.assertEqual(response.status_code, 400)

    def test_non_accreditation_subrole_cannot_approve(self):
        self.client.force_authenticate(self.verifier)

        response = self.client.patch(
            f"/api/state/facilities/applications/{self.application.id}/approve/",
            {"review_comment": "Wrong desk"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_other_state_application_is_not_reachable(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.patch(
            f"/api/state/facilities/applications/{self.oyo_application.id}/approve/",
            {"review_comment": "Wrong state"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)


class StateAssessmentFeeEndpointTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.state_admin = User.objects.create_user(
            "fee-admin",
            "fee-admin@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )
        self.other_state_admin = User.objects.create_user(
            "oyo-fee-admin",
            "oyo-fee-admin@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.oyo,
        )
        self.verifier = User.objects.create_user(
            "fee-verifier",
            "fee-verifier@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )
        MinistryStaffProfile.objects.create(
            user=self.verifier,
            ministry_type=MinistryType.STATE,
            sub_role=MinistryStaffRole.CERTIFICATE_VERIFICATION_OFFICER,
            state=self.lagos,
        )

    def fee_payload(self, facility_type="clinic"):
        return {
            "facility_type": facility_type,
            "amount": "10000.00",
            "state_fee": "2000.00",
            "facility_fee": "7000.00",
            "platform_fee": "1000.00",
            "currency": "NGN",
            "effective_from": "2026-05-18",
            "status": "active",
        }

    def test_state_fee_create_defaults_to_actor_state(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.post("/api/state/fees/", self.fee_payload(), format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(str(payload(response)["state"]), str(self.lagos.id))
        self.assertEqual(AssessmentFee.objects.get().created_by, self.state_admin)

    def test_state_fee_split_is_server_validated(self):
        self.client.force_authenticate(self.state_admin)
        data = self.fee_payload()
        data["platform_fee"] = "2000.00"

        response = self.client.post("/api/state/fees/", data, format="json")

        self.assertEqual(response.status_code, 400)

    def test_state_fee_periods_cannot_overlap_for_same_facility_type(self):
        self.client.force_authenticate(self.state_admin)
        first = self.client.post("/api/state/fees/", self.fee_payload(), format="json")
        self.assertEqual(first.status_code, 201)

        response = self.client.post("/api/state/fees/", self.fee_payload(), format="json")

        self.assertEqual(response.status_code, 400)

    def test_state_fee_listing_is_state_scoped(self):
        AssessmentFee.objects.create(
            state=self.lagos,
            facility_type="clinic",
            amount="10000.00",
            state_fee="2000.00",
            facility_fee="7000.00",
            platform_fee="1000.00",
            effective_from="2026-05-18",
            created_by=self.state_admin,
        )
        AssessmentFee.objects.create(
            state=self.oyo,
            facility_type="clinic",
            amount="9000.00",
            state_fee="2000.00",
            facility_fee="6000.00",
            platform_fee="1000.00",
            effective_from="2026-05-18",
            created_by=self.other_state_admin,
        )
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state/fees/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload(response)), 1)
        self.assertEqual(str(payload(response)[0]["state"]), str(self.lagos.id))

    def test_non_finance_subrole_cannot_create_fee(self):
        self.client.force_authenticate(self.verifier)

        response = self.client.post("/api/state/fees/", self.fee_payload(), format="json")

        self.assertEqual(response.status_code, 403)


class StateCertificateValidationEndpointTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.facility_org = Organization.objects.create(
            name="Lagos Diagnostics",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.lagos,
        )
        self.employer_org = Organization.objects.create(
            name="Clean Foods",
            organization_type=OrganizationType.EMPLOYER,
            state=self.lagos,
        )
        self.handler_user = User.objects.create_user(
            "handler-validation",
            "handler-validation@example.com",
            "StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.lagos,
        )
        self.doctor = User.objects.create_user(
            "doctor-validation",
            "doctor-validation@example.com",
            "StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.lagos,
        )
        self.state_admin = User.objects.create_user(
            "state-validator",
            "state-validator@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )
        self.other_state_admin = User.objects.create_user(
            "oyo-validator",
            "oyo-validator@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.oyo,
        )
        self.finance_user = User.objects.create_user(
            "finance-no-cert",
            "finance-no-cert@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )
        MinistryStaffProfile.objects.create(
            user=self.finance_user,
            ministry_type=MinistryType.STATE,
            sub_role=MinistryStaffRole.POLICY_FINANCE_OFFICER,
            state=self.lagos,
        )
        from apps.employers.models import Employer, EstablishmentCategory

        self.employer = Employer.objects.create(
            organization=self.employer_org,
            business_name="Clean Foods",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Ada",
            contact_person_phone="08030000000",
            contact_person_email="ada@example.com",
            address="1 Food Road",
            state=self.lagos,
        )
        self.facility = MedicalFacility.objects.create(
            organization=self.facility_org,
            facility_name="Lagos Diagnostics",
            facility_type=FacilityType.DIAGNOSTIC_CENTRE,
            ownership_type=OwnershipType.PRIVATE,
            license_number="LD-001",
            address="12 Health Road",
            state=self.lagos,
            contact_person="Dr Ada",
            phone="08030000001",
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
            phone="08030000002",
            email="ada.handler@example.com",
            home_address="3 Allen Avenue",
            state=self.lagos,
            employer=self.employer,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-VAL001",
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
            provider_reference="mock-validation",
            internal_reference="ASS-VAL-001",
            status=PaymentStatus.SUCCESS,
            paid_at=timezone.now(),
            metadata={"facility_id": str(self.facility.id), "state_id": str(self.lagos.id)},
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
        self.request = CertificateRequest.objects.create(
            assessment=self.assessment,
            requested_by=self.doctor,
            status=CertificateRequestStatus.PENDING_VALIDATION,
            request_notes="Ready",
        )

    def test_state_validation_queue_is_state_scoped(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state/certificate-validation-queue/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload(response)), 1)
        self.assertEqual(payload(response)[0]["food_handler_name"], "Ada Okafor")

    def test_other_state_cannot_reach_certificate_request(self):
        self.client.force_authenticate(self.other_state_admin)

        response = self.client.get(f"/api/state/certificate-validation-queue/{self.request.id}/")

        self.assertEqual(response.status_code, 404)

    def test_approve_issues_certificate(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.patch(
            f"/api/state/certificate-validation-queue/{self.request.id}/approve/",
            {"review_notes": "Eligible"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload(response)["status"], CertificateRequestStatus.APPROVED)
        self.assertEqual(Certificate.objects.count(), 1)
        self.assertTrue(payload(response)["certificate_number"].startswith("FCN-LA-"))

    def test_reject_requires_review_notes(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.patch(f"/api/state/certificate-validation-queue/{self.request.id}/reject/", {}, format="json")

        self.assertEqual(response.status_code, 400)

    def test_request_clarification_sets_correction_requested(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.patch(
            f"/api/state/certificate-validation-queue/{self.request.id}/request-clarification/",
            {"review_notes": "Upload missing evidence."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload(response)["status"], CertificateRequestStatus.CORRECTION_REQUESTED)

    def test_non_certificate_subrole_cannot_approve(self):
        self.client.force_authenticate(self.finance_user)

        response = self.client.patch(
            f"/api/state/certificate-validation-queue/{self.request.id}/approve/",
            {"review_notes": "Wrong desk"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)


class StateCertificateRegistryEndpointTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.facility_org = Organization.objects.create(
            name="Registry Diagnostics",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.lagos,
        )
        self.employer_org = Organization.objects.create(
            name="Registry Foods",
            organization_type=OrganizationType.EMPLOYER,
            state=self.lagos,
        )
        self.handler_user = User.objects.create_user("registry-handler", "registry-handler@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.lagos)
        self.doctor = User.objects.create_user("registry-doctor", "registry-doctor@example.com", "StrongPass123!", role=UserRole.DOCTOR, organization=self.facility_org, state=self.lagos)
        self.state_admin = User.objects.create_user("registry-state", "registry-state@example.com", "StrongPass123!", role=UserRole.STATE_ADMIN, state=self.lagos)
        self.other_state_admin = User.objects.create_user("registry-oyo", "registry-oyo@example.com", "StrongPass123!", role=UserRole.STATE_ADMIN, state=self.oyo)
        from apps.employers.models import Employer, EstablishmentCategory

        self.employer = Employer.objects.create(
            organization=self.employer_org,
            business_name="Registry Foods",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Ada",
            contact_person_phone="08030000000",
            contact_person_email="registry@example.com",
            address="1 Registry Road",
            state=self.lagos,
        )
        self.facility = MedicalFacility.objects.create(
            organization=self.facility_org,
            facility_name="Registry Diagnostics",
            facility_type=FacilityType.CLINIC,
            ownership_type=OwnershipType.PRIVATE,
            license_number="REG-001",
            address="1 Health Road",
            state=self.lagos,
            contact_person="Dr Ada",
            phone="08030000001",
            email="registry-facility@example.com",
            accreditation_status=AccreditationStatus.APPROVED,
            accreditation_start_date=timezone.localdate(),
            accreditation_expiry_date=timezone.localdate() + timezone.timedelta(days=365),
        )
        self.food_handler = FoodHandlerProfile.objects.create(
            user=self.handler_user,
            full_name="Registry Handler",
            date_of_birth="1990-01-01",
            gender=Gender.FEMALE,
            nin="12345678901",
            phone="08030000002",
            email="registry.handler@example.com",
            home_address="2 Registry Road",
            state=self.lagos,
            employer=self.employer,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-REG001",
        )
        self.payment = PaymentTransaction.objects.create(
            payer_user=self.handler_user,
            payer_type="food_handler",
            related_entity_type="food_handler_assessment",
            related_entity_id=self.food_handler.id,
            amount="15000.00",
            payment_provider="mock",
            internal_reference="ASS-REG-001",
            status=PaymentStatus.SUCCESS,
            paid_at=timezone.now(),
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
            status="certificate_issued",
            signed_at=timezone.now(),
        )
        self.certificate = Certificate.objects.create(
            certificate_number="FCN-LA-REG001",
            food_handler=self.food_handler,
            assessment=self.assessment,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            issuing_state=self.lagos,
            issued_by_state_user=self.state_admin,
            issue_date=timezone.localdate(),
            expiry_date=timezone.localdate() + timezone.timedelta(days=180),
            status=CertificateStatus.ACTIVE,
            verification_url="http://localhost:3000/verify/FCN-LA-REG001",
            digital_signature_hash="hash",
        )

    def test_state_certificate_registry_is_state_scoped(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state/certificates/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload(response)), 1)
        self.assertEqual(payload(response)[0]["certificate_number"], "FCN-LA-REG001")

    def test_other_state_cannot_reach_certificate_detail(self):
        self.client.force_authenticate(self.other_state_admin)

        response = self.client.get(f"/api/state/certificates/{self.certificate.id}/")

        self.assertEqual(response.status_code, 404)

    def test_registry_searches_certificate_number_and_handler(self):
        self.client.force_authenticate(self.state_admin)

        by_number = self.client.get("/api/state/certificates/?search=REG001")
        by_handler = self.client.get("/api/state/certificates/?search=Registry%20Handler")

        self.assertEqual(len(payload(by_number)), 1)
        self.assertEqual(len(payload(by_handler)), 1)

    def test_suspend_requires_reason_and_updates_certificate(self):
        self.client.force_authenticate(self.state_admin)

        missing_reason = self.client.patch(f"/api/state/certificates/{self.certificate.id}/suspend/", {}, format="json")
        self.assertEqual(missing_reason.status_code, 400)

        response = self.client.patch(
            f"/api/state/certificates/{self.certificate.id}/suspend/",
            {"reason": "Public health review."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload(response)["status"], CertificateStatus.SUSPENDED)
        self.assertEqual(payload(response)["revocation_reason"], "Public health review.")

    def test_revoke_requires_reason_and_updates_certificate(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.patch(
            f"/api/state/certificates/{self.certificate.id}/revoke/",
            {"reason": "Fraud confirmed."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload(response)["status"], CertificateStatus.REVOKED)
        self.assertEqual(payload(response)["revocation_reason"], "Fraud confirmed.")


class StateMonitoringEndpointTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.lagos_lga = LGA.objects.create(name="Ikeja", state=self.lagos)
        self.state_admin = User.objects.create_user("monitor-state", "monitor-state@example.com", "StrongPass123!", role=UserRole.STATE_ADMIN, state=self.lagos)
        self.handler_user = User.objects.create_user("monitor-handler", "monitor-handler@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.lagos)
        self.reporter = User.objects.create_user("monitor-reporter", "monitor-reporter@example.com", "StrongPass123!", role=UserRole.EMPLOYER, state=self.lagos)
        from apps.employers.models import Employer, EstablishmentCategory

        self.employer = Employer.objects.create(
            business_name="Monitor Foods",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Ada",
            contact_person_phone="08030000000",
            contact_person_email="monitor@example.com",
            address="1 Food Road",
            state=self.lagos,
            lga=self.lagos_lga,
            compliance_status="under_review",
        )
        Employer.objects.create(
            business_name="Oyo Foods",
            establishment_category=EstablishmentCategory.BAKERY,
            contact_person_name="Bola",
            contact_person_phone="08030000001",
            contact_person_email="oyo@example.com",
            address="2 Food Road",
            state=self.oyo,
        )
        self.food_handler = FoodHandlerProfile.objects.create(
            user=self.handler_user,
            full_name="Monitor Handler",
            date_of_birth="1991-01-01",
            gender=Gender.FEMALE,
            nin="12345678901",
            phone="08030000002",
            email="handler@example.com",
            home_address="3 Food Road",
            state=self.lagos,
            lga=self.lagos_lga,
            employer=self.employer,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-MON001",
            current_status="temporarily_excluded",
        )
        self.illness = IllnessReport.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            reported_by=self.reporter,
            symptoms={"diarrhoea": True, "vomiting": True},
            suspected_condition="cholera",
            clearance_status="pending",
            notes="Private clinical note",
        )

    def test_state_employer_monitoring_is_state_scoped(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state/employers/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload(response)), 1)
        self.assertEqual(payload(response)[0]["business_name"], "Monitor Foods")

    def test_state_food_handler_monitoring_omits_private_identity_fields(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state/food-handlers/")

        self.assertEqual(response.status_code, 200)
        record = payload(response)[0]
        self.assertEqual(record["full_name"], "Monitor Handler")
        self.assertNotIn("nin", record)
        self.assertNotIn("masked_nin", record)
        self.assertNotIn("date_of_birth", record)

    def test_state_illness_monitoring_omits_symptoms_and_notes(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state/illness-reports/")

        self.assertEqual(response.status_code, 200)
        record = payload(response)[0]
        self.assertEqual(record["clearance_status"], "pending")
        self.assertNotIn("symptoms", record)
        self.assertNotIn("notes", record)

    def test_state_illness_active_filter(self):
        self.illness.clearance_status = "cleared"
        self.illness.save(update_fields=["clearance_status", "updated_at"])
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state/illness-reports/?active=true")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload(response)), 0)


class StateInspectionEndpointTests(APITestCase):
    def setUp(self):
        from apps.employers.models import Employer, EstablishmentCategory

        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.lagos_lga = LGA.objects.create(name="Ikeja", state=self.lagos)
        self.state_admin = User.objects.create_user(
            "inspection-coordinator",
            "inspection-coordinator@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )
        self.inspector = User.objects.create_user(
            "lagos-inspector",
            "lagos-inspector@example.com",
            "StrongPass123!",
            role=UserRole.INSPECTOR,
            state=self.lagos,
        )
        self.oyo_inspector = User.objects.create_user(
            "oyo-inspector",
            "oyo-inspector@example.com",
            "StrongPass123!",
            role=UserRole.INSPECTOR,
            state=self.oyo,
        )
        self.employer = Employer.objects.create(
            business_name="Inspection Foods",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Ada",
            contact_person_phone="08030000000",
            contact_person_email="inspection@example.com",
            address="1 Food Road",
            state=self.lagos,
            lga=self.lagos_lga,
        )
        self.oyo_employer = Employer.objects.create(
            business_name="Oyo Inspection Foods",
            establishment_category=EstablishmentCategory.BAKERY,
            contact_person_name="Bola",
            contact_person_phone="08030000001",
            contact_person_email="oyo-inspection@example.com",
            address="2 Food Road",
            state=self.oyo,
        )
        Inspection.objects.create(
            inspector=self.oyo_inspector,
            employer=self.oyo_employer,
            checklist_responses={"handwash": True},
            compliance_score=100,
            status=InspectionStatus.SUBMITTED,
        )

    def test_state_inspection_list_is_state_scoped(self):
        Inspection.objects.create(
            inspector=self.inspector,
            employer=self.employer,
            checklist_responses={"handwash": True},
            compliance_score=100,
            status=InspectionStatus.SUBMITTED,
        )
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state/inspections/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload(response)), 1)
        self.assertEqual(payload(response)[0]["employer_name"], "Inspection Foods")

    def test_state_coordinator_can_assign_inspection_within_state(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(
            "/api/state/inspections/",
            {
                "inspector": str(self.inspector.id),
                "employer": str(self.employer.id),
                "checklist_responses": {"handwash": True},
                "findings": "Routine visit assigned.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(str(payload(response)["inspector"]), str(self.inspector.id))
        self.assertEqual(str(payload(response)["employer"]), str(self.employer.id))

    def test_state_coordinator_cannot_assign_other_state_employer(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(
            "/api/state/inspections/",
            {"inspector": str(self.inspector.id), "employer": str(self.oyo_employer.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_review_updates_enforcement_and_exposes_audit_history(self):
        inspection = Inspection.objects.create(
            inspector=self.inspector,
            employer=self.employer,
            checklist_responses={"handwash": True},
            compliance_score=100,
            status=InspectionStatus.SUBMITTED,
        )
        self.client.force_authenticate(self.state_admin)

        response = self.client.patch(
            f"/api/state/inspections/{inspection.id}/review/",
            {"enforcement_action": EnforcementAction.COMPLIANCE_NOTICE, "findings": "Correct storage gaps."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = payload(response)
        self.assertEqual(data["enforcement_action"], EnforcementAction.COMPLIANCE_NOTICE)
        self.assertTrue(any(log["metadata"].get("event") == "inspection_reviewed" for log in data["audit_history"]))

    def test_inspector_cannot_close_own_report(self):
        inspection = Inspection.objects.create(
            inspector=self.state_admin,
            employer=self.employer,
            checklist_responses={"handwash": True},
            compliance_score=100,
            status=InspectionStatus.SUBMITTED,
        )
        self.client.force_authenticate(self.state_admin)

        response = self.client.patch(
            f"/api/state/inspections/{inspection.id}/close/",
            {"closure_notes": "Reviewed."},
            format="json",
        )

        self.assertEqual(response.status_code, 403)


class StateReportFinanceEndpointTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.state_admin = User.objects.create_user(
            "report-state",
            "report-state@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )
        self.payer = User.objects.create_user("report-payer", "report-payer@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER)
        self.lagos_org = Organization.objects.create(name="Report Facility Org", organization_type=OrganizationType.MEDICAL_FACILITY, state=self.lagos)
        self.oyo_org = Organization.objects.create(name="Oyo Report Facility Org", organization_type=OrganizationType.MEDICAL_FACILITY, state=self.oyo)
        self.facility = MedicalFacility.objects.create(
            organization=self.lagos_org,
            facility_name="Report Clinic",
            facility_type=FacilityType.CLINIC,
            ownership_type=OwnershipType.PRIVATE,
            license_number="REP-001",
            address="1 Clinic Road",
            state=self.lagos,
            contact_person="Ada",
            phone="08030000000",
            email="report-clinic@example.com",
            accreditation_status=AccreditationStatus.APPROVED,
            accreditation_expiry_date=timezone.localdate() + timezone.timedelta(days=180),
        )
        self.oyo_facility = MedicalFacility.objects.create(
            organization=self.oyo_org,
            facility_name="Oyo Report Clinic",
            facility_type=FacilityType.CLINIC,
            ownership_type=OwnershipType.PRIVATE,
            license_number="REP-002",
            address="2 Clinic Road",
            state=self.oyo,
            contact_person="Bola",
            phone="08030000001",
            email="oyo-report-clinic@example.com",
        )
        self.payment = PaymentTransaction.objects.create(
            payer_user=self.payer,
            payer_type=PayerType.FOOD_HANDLER,
            related_entity_type="assessment",
            related_entity_id=self.facility.id,
            amount="10000.00",
            payment_provider="manual",
            internal_reference="REP-LAGOS-001",
            status=PaymentStatus.SUCCESS,
            metadata={"facility_id": str(self.facility.id)},
        )
        self.oyo_payment = PaymentTransaction.objects.create(
            payer_user=self.payer,
            payer_type=PayerType.FOOD_HANDLER,
            related_entity_type="assessment",
            related_entity_id=self.oyo_facility.id,
            amount="8000.00",
            payment_provider="manual",
            internal_reference="REP-OYO-001",
            status=PaymentStatus.SUCCESS,
            metadata={"facility_id": str(self.oyo_facility.id)},
        )
        self.settlement = Settlement.objects.create(
            facility=self.facility,
            state=self.lagos,
            payment_transaction=self.payment,
            gross_amount="10000.00",
            facility_amount="6000.00",
            state_amount="3000.00",
            platform_amount="1000.00",
            settlement_status=SettlementStatus.PAID,
            settlement_reference="SET-LAGOS-001",
            settled_at=timezone.now(),
        )
        Settlement.objects.create(
            facility=self.oyo_facility,
            state=self.oyo,
            payment_transaction=self.oyo_payment,
            gross_amount="8000.00",
            facility_amount="5000.00",
            state_amount="2000.00",
            platform_amount="1000.00",
            settlement_status=SettlementStatus.PAID,
        )

    def test_state_revenue_is_state_scoped(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state/revenue/")

        self.assertEqual(response.status_code, 200)
        data = payload(response)
        self.assertEqual(data["cards"]["settlement_count"], 1)
        self.assertEqual(data["cards"]["state_amount"], "3000")

    def test_state_settlements_are_state_scoped(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state/settlements/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload(response)), 1)
        self.assertEqual(payload(response)[0]["facility_name"], "Report Clinic")

    def test_state_report_generation_preserves_snapshot(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(
            "/api/state/reports/generate/",
            {
                "report_type": "state_monthly",
                "reporting_period_start": str(timezone.localdate().replace(day=1)),
                "reporting_period_end": str(timezone.localdate()),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        report = payload(response)
        self.assertEqual(report["status"], StateReportStatus.GENERATED)
        self.assertEqual(report["data_snapshot"]["finance"]["cards"]["state_amount"], "3000")

        self.settlement.state_amount = "9999.00"
        self.settlement.save(update_fields=["state_amount", "updated_at"])

        list_response = self.client.get("/api/state/reports/")
        self.assertEqual(payload(list_response)[0]["data_snapshot"]["finance"]["cards"]["state_amount"], "3000")

    def test_state_report_can_be_submitted_to_federal(self):
        self.client.force_authenticate(self.state_admin)
        generated = self.client.post(
            "/api/state/reports/generate/",
            {
                "report_type": "state_monthly",
                "reporting_period_start": str(timezone.localdate().replace(day=1)),
                "reporting_period_end": str(timezone.localdate()),
            },
            format="json",
        )

        response = self.client.patch(f"/api/state/reports/{payload(generated)['id']}/submit/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload(response)["status"], StateReportStatus.SUBMITTED)
        self.assertIsNotNone(payload(response)["submitted_at"])


class FederalStatePerformanceEndpointTests(APITestCase):
    def setUp(self):
        from apps.employers.models import Employer, EstablishmentCategory

        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.fct = State.objects.create(name="Federal Capital Territory", code="FCT", is_fct=True)
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.lagos_lga = LGA.objects.create(name="Ikeja", state=self.lagos)
        self.federal_admin = User.objects.create_user(
            "federal-performance",
            "federal-performance@example.com",
            "StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.state_admin = User.objects.create_user(
            "state-performance",
            "state-performance@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )
        self.handler_user = User.objects.create_user("fed-handler", "fed-handler@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.lagos)
        self.employer = Employer.objects.create(
            business_name="Federal View Foods",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Ada",
            contact_person_phone="08030000000",
            contact_person_email="fed-view@example.com",
            address="1 Food Road",
            state=self.lagos,
            lga=self.lagos_lga,
        )
        FoodHandlerProfile.objects.create(
            user=self.handler_user,
            full_name="Federal Handler",
            date_of_birth="1991-01-01",
            gender=Gender.FEMALE,
            nin="12345678901",
            phone="08030000002",
            email="fed-handler-profile@example.com",
            home_address="3 Food Road",
            state=self.lagos,
            lga=self.lagos_lga,
            employer=self.employer,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-FED001",
            current_status="fit",
        )
        StateReport.objects.create(
            state=self.lagos,
            report_type="state_monthly",
            reporting_period_start=timezone.localdate().replace(day=1),
            reporting_period_end=timezone.localdate(),
            status=StateReportStatus.SUBMITTED,
            generated_by=self.state_admin,
            submitted_by=self.state_admin,
            submitted_at=timezone.now(),
            data_snapshot={"cards": {"example": 1}},
        )

    def test_federal_state_performance_requires_federal_user(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/federal/states/performance/")

        self.assertEqual(response.status_code, 403)

    def test_federal_state_performance_includes_all_states_and_fct(self):
        self.client.force_authenticate(self.federal_admin)

        response = self.client.get("/api/federal/states/performance/")

        self.assertEqual(response.status_code, 200)
        data = payload(response)
        names = {row["state_name"] for row in data["states"]}
        self.assertEqual(names, {"Federal Capital Territory", "Lagos", "Oyo"})
        fct = next(row for row in data["states"] if row["state_code"] == "FCT")
        self.assertTrue(fct["is_fct"])
        self.assertEqual(fct["registered_handlers"], 0)
        lagos = next(row for row in data["states"] if row["state_name"] == "Lagos")
        self.assertEqual(lagos["registered_handlers"], 1)
        self.assertEqual(lagos["latest_report_status"], StateReportStatus.SUBMITTED)
        self.assertNotIn("nin", lagos)
        self.assertNotIn("date_of_birth", lagos)

    def test_federal_state_summary_is_privacy_safe(self):
        self.client.force_authenticate(self.federal_admin)

        response = self.client.get(f"/api/federal/states/{self.lagos.id}/summary/")

        self.assertEqual(response.status_code, 200)
        data = payload(response)
        self.assertEqual(data["state"]["state_name"], "Lagos")
        self.assertEqual(len(data["reports"]), 1)
        self.assertNotIn("handlers", data)


class FederalRegistryPolicyEndpointTests(APITestCase):
    def setUp(self):
        from apps.employers.models import Employer, EstablishmentCategory

        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.lagos_lga = LGA.objects.create(name="Ikeja", state=self.lagos)
        self.federal_admin = User.objects.create_user(
            "federal-registry",
            "federal-registry@example.com",
            "StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.state_admin = User.objects.create_user(
            "registry-state",
            "registry-state@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )
        self.handler_user = User.objects.create_user("registry-handler", "registry-handler@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.lagos)
        self.doctor = User.objects.create_user("registry-doctor", "registry-doctor@example.com", "StrongPass123!", role=UserRole.DOCTOR, state=self.lagos)
        self.facility_org = Organization.objects.create(name="Registry Facility Org", organization_type=OrganizationType.MEDICAL_FACILITY, state=self.lagos)
        self.facility = MedicalFacility.objects.create(
            organization=self.facility_org,
            facility_name="Registry Clinic",
            facility_type=FacilityType.CLINIC,
            ownership_type=OwnershipType.PRIVATE,
            license_number="REG-001",
            address="1 Clinic Road",
            state=self.lagos,
            lga=self.lagos_lga,
            contact_person="Ada",
            phone="08030000000",
            email="registry-clinic@example.com",
            accreditation_status=AccreditationStatus.APPROVED,
            accreditation_expiry_date=timezone.localdate() + timezone.timedelta(days=180),
        )
        self.employer = Employer.objects.create(
            business_name="Registry Foods",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Ada",
            contact_person_phone="08030000001",
            contact_person_email="registry-foods@example.com",
            address="1 Food Road",
            state=self.lagos,
            lga=self.lagos_lga,
        )
        self.food_handler = FoodHandlerProfile.objects.create(
            user=self.handler_user,
            full_name="Registry Handler",
            date_of_birth="1991-01-01",
            gender=Gender.FEMALE,
            nin="12345678901",
            phone="08030000002",
            email="registry-handler-profile@example.com",
            home_address="3 Food Road",
            state=self.lagos,
            lga=self.lagos_lga,
            employer=self.employer,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-REG001",
            current_status="fit",
        )
        self.assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            final_decision=FitnessDecision.FIT,
            signed_at=timezone.now(),
        )
        Certificate.objects.create(
            certificate_number="FCN-REG-CERT-001",
            food_handler=self.food_handler,
            assessment=self.assessment,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            issuing_state=self.lagos,
            issue_date=timezone.localdate(),
            expiry_date=timezone.localdate() + timezone.timedelta(days=365),
            verification_url="https://verify.example.com/FCN-REG-CERT-001",
            digital_signature_hash="abc123",
        )
        StatePolicyConfig.objects.create(
            state=self.lagos,
            requires_state_certificate_validation=False,
            certificate_validity_months=6,
            updated_by=self.federal_admin,
        )

    def test_federal_certificate_registry_is_privacy_safe(self):
        self.client.force_authenticate(self.federal_admin)

        response = self.client.get("/api/federal/certificates/")

        self.assertEqual(response.status_code, 200)
        record = payload(response)[0]
        self.assertEqual(record["certificate_number"], "FCN-REG-CERT-001")
        self.assertNotIn("masked_nin", record)
        self.assertNotIn("date_of_birth", record)
        self.assertNotIn("doctor_notes", record)

    def test_state_user_cannot_access_federal_registries(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/federal/facilities/")

        self.assertEqual(response.status_code, 403)

    def test_federal_policy_can_be_updated_and_state_overrides_are_visible(self):
        self.client.force_authenticate(self.federal_admin)

        response = self.client.patch(
            "/api/federal/policy/",
            {"certificate_validity_months": 18, "nin_required": False},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload(response)["certificate_validity_months"], 18)
        self.assertFalse(payload(response)["nin_required"])
        self.assertEqual(NationalPolicyConfig.objects.count(), 1)

        overrides = self.client.get("/api/federal/state-overrides/")
        self.assertEqual(overrides.status_code, 200)
        self.assertEqual(payload(overrides)[0]["state_name"], "Lagos")
        self.assertEqual(payload(overrides)[0]["certificate_validity_months"], 6)


class FederalOversightQueryEndpointTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.federal_admin = User.objects.create_user(
            "federal-query",
            "federal-query@example.com",
            "StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.state_admin = User.objects.create_user(
            "query-state",
            "query-state@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )
        StateReport.objects.create(
            state=self.lagos,
            report_type="state_monthly",
            reporting_period_start=timezone.localdate().replace(day=1),
            reporting_period_end=timezone.localdate(),
            status=StateReportStatus.SUBMITTED,
            generated_by=self.state_admin,
            submitted_by=self.state_admin,
            submitted_at=timezone.now(),
            data_snapshot={},
        )
        log_action(
            action=AuditAction.SECURITY_EVENT,
            actor=self.federal_admin,
            target_type="Policy",
            target_id="national",
            state=self.lagos,
            metadata={"event": "test_security_event"},
        )

    def test_federal_indicators_and_data_quality_are_federal_only(self):
        self.client.force_authenticate(self.state_admin)
        forbidden = self.client.get("/api/federal/m-and-e/indicators/")
        self.assertEqual(forbidden.status_code, 403)

        self.client.force_authenticate(self.federal_admin)
        indicators = self.client.get("/api/federal/m-and-e/indicators/")
        quality = self.client.get("/api/federal/data-quality/")

        self.assertEqual(indicators.status_code, 200)
        self.assertIn("missing_reports", payload(indicators)["cards"])
        self.assertEqual(quality.status_code, 200)
        self.assertTrue(any(risk["state_name"] == "Oyo" and risk["risk"] == "missing_state_report" for risk in payload(quality)["risks"]))

    def test_federal_audit_log_summary_is_privacy_safe(self):
        self.client.force_authenticate(self.federal_admin)

        response = self.client.get("/api/federal/audit-logs/")

        self.assertEqual(response.status_code, 200)
        record = payload(response)[0]
        self.assertEqual(record["risk_level"], "high")
        self.assertNotIn("old_value", record)
        self.assertNotIn("new_value", record)

    def test_federal_query_lifecycle(self):
        self.client.force_authenticate(self.federal_admin)

        created = self.client.post(
            "/api/federal/queries/",
            {
                "state": str(self.lagos.id),
                "subject": "Clarify report numbers",
                "description": "Please reconcile handler totals.",
                "category": "reporting",
                "priority": "high",
            },
            format="json",
        )

        self.assertEqual(created.status_code, 201)
        query_id = payload(created)["id"]

        responded = self.client.patch(
            f"/api/federal/queries/{query_id}/respond/",
            {"response": "Reviewed with state desk."},
            format="json",
        )
        self.assertEqual(responded.status_code, 200)
        self.assertEqual(payload(responded)["status"], FederalStateQueryStatus.RESPONDED)

        closed = self.client.patch(f"/api/federal/queries/{query_id}/close/")
        self.assertEqual(closed.status_code, 200)
        self.assertEqual(payload(closed)["status"], FederalStateQueryStatus.CLOSED)
