from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.assessments.models import AssessmentStatus, Appointment, AppointmentStatus, IdentityVerificationStatus, MedicalAssessment
from apps.audit.models import AuditAction, AuditLog
from apps.audit.services import log_action
from apps.employers.models import Employer, EstablishmentCategory
from apps.facilities.models import (
    AccreditationStatus,
    FacilityAccreditationApplication,
    FacilityDocument,
    FacilityInvitation,
    FacilityProfessionalCategory,
    FacilityProfessionalProfile,
    FacilityProfessionalVerificationStatus,
    FacilityRole,
    FacilityRolePermission,
    FacilityStaffProfile,
    FacilityStaffType,
    FacilityTeamMemberStatus,
    MedicalFacility,
)
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, Gender
from apps.lab_tests.models import LabTest, LabTestStatus
from apps.locations.models import State
from apps.organizations.models import Organization, OrganizationType, OrganizationUnit, OrganizationUnitType, Role
from apps.policy.models import StatePolicyConfig
from apps.facilities.services import FacilityTeamService
from apps.reports.models import GeneratedReport

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
            "ward": "Ward A",
            "operating_hours": "Mon-Fri 8:00-17:00",
            "service_capacity": 80,
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
            "has_valid_facility_license": True,
            "has_laboratory_capacity": True,
            "has_valid_doctor_credentials": True,
            "has_valid_lab_staff_credentials": True,
            "has_infection_prevention_readiness": True,
            "has_confidentiality_policy": True,
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

    def _create_facility_record(self, suffix="BASE"):
        return MedicalFacility.objects.create(
            organization=Organization.objects.create(
                name=f"Lagos Diagnostics {suffix}",
                organization_type=OrganizationType.MEDICAL_FACILITY,
                state=self.lagos,
            ),
            facility_name=f"Lagos Diagnostics {suffix}",
            facility_type="diagnostic_centre",
            ownership_type="private",
            license_number=f"LAG-{suffix}-001",
            address="12 Health Road",
            state=self.lagos,
            contact_person="Dr Ada",
            phone="08030000000",
            email=f"facility-{suffix.lower()}@example.com",
        )

    def test_chunk1_facility_team_role_and_professional_models_capture_required_fields(self):
        facility = self._create_facility_record("TEAM")
        role_template = Role.objects.create(
            name="Facility Doctor Template",
            code="facility_doctor_template_chunk1",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            is_system_role=True,
        )
        facility_role = FacilityRole.objects.create(
            facility=facility,
            organization_role=role_template,
            name="Medical Doctor",
            description="Doctor role inside the facility account.",
            is_system_default=True,
            created_by=self.facility_admin,
        )
        FacilityRolePermission.objects.create(
            role=facility_role,
            permission_key="declaration.validate",
            allowed=True,
        )
        staff_user = User.objects.create_user(
            username="doctor-user",
            email="doctor-user@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=facility.organization,
            state=self.lagos,
        )
        profile = FacilityStaffProfile.objects.create(
            user=staff_user,
            facility=facility,
            role=facility_role,
            staff_type="doctor",
            professional_category=FacilityProfessionalCategory.DOCTOR,
            status=FacilityTeamMemberStatus.PENDING_LICENSE_VERIFICATION,
            invited_by=self.facility_admin,
            professional_registration_number="MDCN-12345",
        )
        professional = FacilityProfessionalProfile.objects.create(
            user=staff_user,
            facility=facility,
            team_member=profile,
            professional_category=FacilityProfessionalCategory.DOCTOR,
            license_number="MDCN-12345",
            license_issuing_body="MDCN",
            license_document_url="https://example.com/mdcn-12345.pdf",
            verification_status=FacilityProfessionalVerificationStatus.PENDING,
        )

        self.assertEqual(profile.role, facility_role)
        self.assertEqual(profile.professional_category, FacilityProfessionalCategory.DOCTOR)
        self.assertEqual(profile.status, FacilityTeamMemberStatus.PENDING_LICENSE_VERIFICATION)
        self.assertEqual(professional.team_member, profile)
        self.assertEqual(professional.verification_status, FacilityProfessionalVerificationStatus.PENDING)
        self.assertTrue(
            FacilityRolePermission.objects.filter(
                role=facility_role,
                permission_key="declaration.validate",
                allowed=True,
            ).exists()
        )

    def test_chunk1_facility_invitation_wraps_platform_invite_for_team_workflow(self):
        facility = self._create_facility_record("INVITE")
        role_template = Role.objects.create(
            name="Front Desk Template",
            code="front_desk_template_chunk1",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            is_system_role=True,
        )
        facility_role = FacilityRole.objects.create(
            facility=facility,
            organization_role=role_template,
            name="Front Desk",
            is_system_default=True,
            created_by=self.facility_admin,
        )
        from apps.accounts.models import UserInvite

        invite = UserInvite.objects.create(
            organization=facility.organization,
            invited_by=self.facility_admin,
            email="frontdesk@example.com",
            role=UserRole.FACILITY_ADMIN,
            facility_staff_type="front_desk",
            token="chunk1-facility-invite-token",
            expires_at=timezone.now() + timezone.timedelta(days=7),
        )
        facility_invite = FacilityInvitation.objects.create(
            facility=facility,
            invite=invite,
            role=facility_role,
            professional_category=FacilityProfessionalCategory.FRONT_DESK,
            status=FacilityTeamMemberStatus.INVITED,
        )

        self.assertEqual(facility_invite.invite.email, "frontdesk@example.com")
        self.assertEqual(facility_invite.role, facility_role)
        self.assertEqual(facility_invite.professional_category, FacilityProfessionalCategory.FRONT_DESK)

    def test_facility_admin_can_register_facility_and_apply(self):
        facility, application = self._create_facility_and_application()

        self.assertEqual(facility["accreditation_status"], AccreditationStatus.DRAFT)
        self.assertTrue(facility["profile_complete"])
        self.assertEqual(facility["ward"], "Ward A")
        self.assertEqual(facility["service_capacity"], 80)
        self.assertEqual(application["application_status"], AccreditationStatus.DRAFT)
        self.assertTrue(application["checklist_complete"])
        facility_record = MedicalFacility.objects.get(id=facility["id"])
        default_role_names = set(
            FacilityRole.objects.filter(facility=facility_record, is_system_default=True).values_list("name", flat=True)
        )
        self.assertIn("Facility Administrator", default_role_names)
        self.assertIn("Medical Doctor", default_role_names)
        self.assertTrue(
            FacilityRolePermission.objects.filter(
                role__facility=facility_record,
                role__name="Medical Doctor",
                permission_key="doctor_review.final_decision",
                allowed=True,
            ).exists()
        )

    def test_chunk2_protected_permission_rules_block_non_clinical_assignment(self):
        with self.assertRaises(ValueError):
            FacilityTeamService.validate_permission_assignment(
                professional_category=FacilityProfessionalCategory.FINANCE,
                permission_keys=["declaration.validate", "finance.view_payments"],
            )

        FacilityTeamService.validate_permission_assignment(
            professional_category=FacilityProfessionalCategory.DOCTOR,
            permission_keys=["declaration.validate", "doctor_review.final_decision"],
        )

    def test_facility_admin_can_fetch_and_update_current_facility_profile(self):
        facility, _ = self._create_facility_and_application()
        self.client.force_authenticate(self.facility_admin)

        current_response = self.client.get("/api/medical-facilities/me/")
        self.assertEqual(current_response.status_code, 200)
        self.assertEqual(data(current_response)["id"], facility["id"])

        update_response = self.client.patch(
            "/api/medical-facilities/me/",
            {
                "contact_person": "Dr Ada Updated",
                "operating_hours": "Daily 8:00-18:00",
                "service_capacity": 120,
                "ward": "Ward B",
            },
            format="json",
        )

        self.assertEqual(update_response.status_code, 200)
        payload = data(update_response)
        self.assertEqual(payload["contact_person"], "Dr Ada Updated")
        self.assertEqual(payload["operating_hours"], "Daily 8:00-18:00")
        self.assertEqual(payload["service_capacity"], 120)
        self.assertEqual(payload["ward"], "Ward B")
        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditAction.UPDATE,
                target_id=str(facility["id"]),
                metadata__event="facility_profile_updated",
            ).exists()
        )

    def test_current_facility_profile_is_limited_to_facility_admin(self):
        self._create_facility_and_application()

        self.client.force_authenticate(self.lagos_state_admin)
        response = self.client.get("/api/medical-facilities/me/")

        self.assertEqual(response.status_code, 403)

    def test_active_facility_team_member_can_fetch_but_not_update_current_facility_profile(self):
        facility, _ = self._create_facility_and_application()
        db_facility = MedicalFacility.objects.get(id=facility["id"])
        FacilityTeamService.ensure_default_roles(facility=db_facility, actor=self.facility_admin)
        viewer_role = FacilityRole.objects.get(facility=db_facility, name="Viewer / Auditor")
        viewer_user = User.objects.create_user(
            username="facility-viewer",
            email="facility-viewer@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.lagos,
        )
        FacilityStaffProfile.objects.create(
            user=viewer_user,
            facility=db_facility,
            role=viewer_role,
            staff_type=FacilityStaffType.DOCTOR,
            professional_category=FacilityProfessionalCategory.VIEWER,
            status=FacilityTeamMemberStatus.ACTIVE,
            is_active=True,
        )

        self.client.force_authenticate(viewer_user)
        current_response = self.client.get("/api/medical-facilities/me/")
        patch_response = self.client.patch("/api/medical-facilities/me/", {"contact_person": "Changed"}, format="json")

        self.assertEqual(current_response.status_code, 200)
        self.assertEqual(data(current_response)["id"], facility["id"])
        self.assertEqual(patch_response.status_code, 403)

    def test_non_member_org_user_cannot_access_facility_routes(self):
        facility, _ = self._create_facility_and_application()
        outsider = User.objects.create_user(
            username="facility-outsider",
            email="facility-outsider@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.lagos,
        )

        self.client.force_authenticate(outsider)
        me_response = self.client.get("/api/medical-facilities/me/")
        appointments_response = self.client.get(f"/api/medical-facilities/{facility['id']}/appointments/")

        self.assertEqual(me_response.status_code, 403)
        self.assertEqual(appointments_response.status_code, 404)

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
        policy, _ = StatePolicyConfig.objects.get_or_create(state=self.lagos)
        policy.medical_facility_settings = {
            **policy.medical_facility_settings,
            "validity_duration": 2,
            "validity_unit": "years",
        }
        policy.save(update_fields=["medical_facility_settings", "updated_at"])
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
        self.assertEqual(db_facility.accreditation_expiry_date, timezone.localdate().replace(year=timezone.localdate().year + 2))

    def test_facility_admin_can_upload_accreditation_document(self):
        facility, application = self._create_facility_and_application()
        self.client.force_authenticate(self.facility_admin)

        response = self.client.post(
            "/api/facility-documents/",
            {
                "facility": facility["id"],
                "accreditation_application": application["id"],
                "document_type": "facility_license",
                "file": SimpleUploadedFile("license.pdf", b"%PDF-1.4 test", content_type="application/pdf"),
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        payload = data(response)
        self.assertEqual(payload["document_type"], "facility_license")
        self.assertEqual(payload["status"], "uploaded")
        self.assertEqual(FacilityDocument.objects.count(), 1)
        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditAction.CREATE,
                target_id=payload["id"],
                metadata__event="facility_document_uploaded",
            ).exists()
        )

    def test_facility_document_must_match_application_facility(self):
        facility, _ = self._create_facility_and_application()
        other_org = Organization.objects.create(
            name="Other Facility Org",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.lagos,
        )
        other_facility = MedicalFacility.objects.create(
            organization=other_org,
            facility_name="Other Clinic",
            facility_type="clinic",
            ownership_type="private",
            license_number="OTH-001",
            address="1 Other Road",
            state=self.lagos,
            contact_person="Dr Other",
            phone="08030000999",
            email="other@example.com",
        )
        other_application = FacilityAccreditationApplication.objects.create(
            facility=other_facility,
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
            has_valid_facility_license=True,
            has_laboratory_capacity=True,
            has_valid_doctor_credentials=True,
            has_valid_lab_staff_credentials=True,
            has_infection_prevention_readiness=True,
            has_confidentiality_policy=True,
        )
        self.client.force_authenticate(self.facility_admin)

        response = self.client.post(
            "/api/facility-documents/",
            {
                "facility": facility["id"],
                "accreditation_application": str(other_application.id),
                "document_type": "facility_license",
                "file": SimpleUploadedFile("license.pdf", b"%PDF-1.4 test", content_type="application/pdf"),
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)

    def test_state_admin_can_request_more_information(self):
        facility, application = self._create_facility_and_application()
        self.client.force_authenticate(self.facility_admin)
        self.client.patch(f"/api/facility-accreditation/{application['id']}/submit/")

        self.client.force_authenticate(self.lagos_state_admin)
        response = self.client.patch(
            f"/api/facility-accreditation/{application['id']}/request-more-information/",
            {"review_comment": "Upload doctor credentials."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data(response)["application_status"], AccreditationStatus.MORE_INFORMATION_REQUIRED)
        db_facility = MedicalFacility.objects.get(id=facility["id"])
        self.assertEqual(db_facility.accreditation_status, AccreditationStatus.MORE_INFORMATION_REQUIRED)

    def test_approved_facility_can_start_re_accreditation(self):
        facility, application = self._create_facility_and_application()
        self.client.force_authenticate(self.facility_admin)
        self.client.patch(f"/api/facility-accreditation/{application['id']}/submit/")
        self.client.force_authenticate(self.lagos_state_admin)
        self.client.patch(f"/api/facility-accreditation/{application['id']}/approve/", {}, format="json")

        self.client.force_authenticate(self.facility_admin)
        response = self.client.post(f"/api/medical-facilities/{facility['id']}/re-accreditation/")

        self.assertEqual(response.status_code, 201)
        payload = data(response)
        self.assertTrue(payload["is_renewal"])
        self.assertEqual(str(payload["renewal_of"]), application["id"])
        db_facility = MedicalFacility.objects.get(id=facility["id"])
        self.assertEqual(db_facility.accreditation_status, AccreditationStatus.REACCREDITATION_DUE)

    def test_facility_departments_alias_supports_crud_and_workload_metrics(self):
        facility, _ = self._create_facility_and_application()
        db_facility = MedicalFacility.objects.get(id=facility["id"])
        self.client.force_authenticate(self.facility_admin)

        create_response = self.client.post(
            f"/api/medical-facilities/{facility['id']}/departments/",
            {
                "name": "Clinical Assessment",
                "unit_type": OrganizationUnitType.CLINICAL_DEPARTMENT,
                "description": "Doctor assessment team",
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        unit_id = data(create_response)["id"]
        doctor = User.objects.create_user(
            username="facility-doctor",
            email="facility-doctor@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            unit_id=unit_id,
            state=self.lagos,
        )
        handler_user = User.objects.create_user(
            username="handler-dept",
            email="handler-dept@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.lagos,
        )
        handler = FoodHandlerProfile.objects.create(
            user=handler_user,
            full_name="Facility Handler",
            date_of_birth="1994-01-01",
            gender=Gender.FEMALE,
            nin="12345678901",
            phone="08030001000",
            email="handler-dept@example.com",
            home_address="1 Test Street",
            state=self.lagos,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-DEPT001",
        )
        MedicalAssessment.objects.create(
            food_handler=handler,
            facility=db_facility,
            doctor=doctor,
            status=AssessmentStatus.DECLARATION_VALIDATED,
        )

        detail_response = self.client.get(f"/api/medical-facilities/{facility['id']}/departments/{unit_id}/")
        self.assertEqual(detail_response.status_code, 200)
        detail = data(detail_response)
        self.assertEqual(detail["member_count"], 1)
        self.assertEqual(detail["open_assessment_count"], 1)

        update_response = self.client.patch(
            f"/api/medical-facilities/{facility['id']}/departments/{unit_id}/",
            {"description": "Updated clinical team"},
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(data(update_response)["description"], "Updated clinical team")

        delete_response = self.client.delete(f"/api/medical-facilities/{facility['id']}/departments/{unit_id}/")
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(OrganizationUnit.objects.get(id=unit_id).is_active)

    def test_lab_department_workload_counts_pending_lab_tests(self):
        facility, _ = self._create_facility_and_application()
        db_facility = MedicalFacility.objects.get(id=facility["id"])
        lab_unit = OrganizationUnit.objects.create(
            organization=self.facility_org,
            name="Laboratory",
            unit_type=OrganizationUnitType.LAB_DEPARTMENT,
        )
        doctor = User.objects.create_user(
            username="lab-workload-doctor",
            email="lab-workload-doctor@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.lagos,
        )
        handler_user = User.objects.create_user(
            username="handler-lab",
            email="handler-lab@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.lagos,
        )
        handler = FoodHandlerProfile.objects.create(
            user=handler_user,
            full_name="Lab Handler",
            date_of_birth="1994-01-01",
            gender=Gender.MALE,
            nin="12345678902",
            phone="08030001001",
            email="handler-lab@example.com",
            home_address="2 Test Street",
            state=self.lagos,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-DEPT002",
        )
        assessment = MedicalAssessment.objects.create(
            food_handler=handler,
            facility=db_facility,
            doctor=doctor,
            status=AssessmentStatus.LAB_TESTS_PENDING,
        )
        LabTest.objects.create(
            assessment=assessment,
            requested_by=doctor,
            test_type="stool_microscopy",
        )
        self.client.force_authenticate(self.facility_admin)

        response = self.client.get(f"/api/medical-facilities/{facility['id']}/departments/{lab_unit.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data(response)["pending_lab_test_count"], 1)

    def test_facility_admin_can_invite_department_staff(self):
        facility, _ = self._create_facility_and_application()
        department = OrganizationUnit.objects.create(
            organization=self.facility_org,
            name="Clinical",
            unit_type=OrganizationUnitType.CLINICAL_DEPARTMENT,
        )
        self.client.force_authenticate(self.facility_admin)

        response = self.client.post(
            f"/api/medical-facilities/{facility['id']}/invites/",
            {
                "email": "doctor-invite@example.com",
                "phone": "08030004444",
                "role": UserRole.DOCTOR,
                "staff_type": "doctor",
                "department": str(department.id),
                "professional_registration_number": "MDCN-123",
                "message": "Join clinical team",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        payload = data(response)
        self.assertEqual(payload["email"], "doctor-invite@example.com")
        self.assertEqual(payload["unit"], department.id)
        self.assertEqual(payload["facility_staff_type"], "doctor")

    def test_facility_staff_profile_update_scopes_user_to_department(self):
        facility, _ = self._create_facility_and_application()
        db_facility = MedicalFacility.objects.get(id=facility["id"])
        department = OrganizationUnit.objects.create(
            organization=self.facility_org,
            name="Laboratory",
            unit_type=OrganizationUnitType.LAB_DEPARTMENT,
        )
        lab_user = User.objects.create_user(
            username="profile-lab",
            email="profile-lab@example.com",
            password="StrongPass123!",
            role=UserRole.LAB_STAFF,
            organization=self.facility_org,
            state=self.lagos,
        )
        profile = FacilityStaffProfile.objects.create(
            user=lab_user,
            facility=db_facility,
            staff_type="lab_staff",
        )
        self.client.force_authenticate(self.facility_admin)

        response = self.client.patch(
            f"/api/medical-facilities/{facility['id']}/staff/{profile.id}/",
            {
                "department": str(department.id),
                "professional_registration_number": "LAB-456",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(str(payload["department"]), str(department.id))
        self.assertEqual(payload["professional_registration_number"], "LAB-456")
        lab_user.refresh_from_db()
        self.assertEqual(lab_user.unit_id, department.id)
        self.assertTrue(lab_user.unit_restricted)

    def test_facility_admin_can_suspend_and_reactivate_staff_profile(self):
        facility, _ = self._create_facility_and_application()
        db_facility = MedicalFacility.objects.get(id=facility["id"])
        doctor = User.objects.create_user(
            username="profile-doctor",
            email="profile-doctor@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.lagos,
        )
        profile = FacilityStaffProfile.objects.create(
            user=doctor,
            facility=db_facility,
            staff_type="doctor",
        )
        self.client.force_authenticate(self.facility_admin)

        suspend = self.client.patch(f"/api/medical-facilities/{facility['id']}/staff/{profile.id}/suspend/")
        self.assertEqual(suspend.status_code, 200)
        doctor.refresh_from_db()
        self.assertEqual(doctor.status, "suspended")

        reactivate = self.client.patch(f"/api/medical-facilities/{facility['id']}/staff/{profile.id}/reactivate/")
        self.assertEqual(reactivate.status_code, 200)
        doctor.refresh_from_db()
        self.assertEqual(doctor.status, "active")

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

    def test_chunk5_facility_admin_can_verify_identity_and_check_in_assessment(self):
        facility, application = self._create_facility_and_application()
        self.client.force_authenticate(self.facility_admin)
        self.client.patch(f"/api/facility-accreditation/{application['id']}/submit/")
        self.client.force_authenticate(self.lagos_state_admin)
        self.client.patch(f"/api/facility-accreditation/{application['id']}/approve/", {}, format="json")
        db_facility = MedicalFacility.objects.get(id=facility["id"])

        handler_user = User.objects.create_user(
            username="handler-checkin",
            email="handler-checkin@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.lagos,
        )
        handler = FoodHandlerProfile.objects.create(
            user=handler_user,
            full_name="Check In Handler",
            date_of_birth="1995-04-03",
            gender=Gender.FEMALE,
            nin="12345678903",
            phone="08030009999",
            email="handler-checkin@example.com",
            home_address="22 Intake Street",
            state=self.lagos,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-CHECK001",
        )
        appointment = Appointment.objects.create(
            food_handler=handler,
            facility=db_facility,
            appointment_date=timezone.now() + timedelta(hours=2),
            status=AppointmentStatus.CONFIRMED,
        )
        assessment = MedicalAssessment.objects.create(
            food_handler=handler,
            facility=db_facility,
            appointment=appointment,
            status=AssessmentStatus.APPOINTMENT_BOOKED,
        )

        self.client.force_authenticate(self.facility_admin)
        response = self.client.patch(
            f"/api/medical-facilities/{facility['id']}/assessments/{assessment.id}/check-in/",
            {"notes": "Passport and NIN matched at reception."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(payload["identity_verification_status"], IdentityVerificationStatus.VERIFIED)
        self.assertEqual(payload["status"], AssessmentStatus.ASSESSMENT_IN_PROGRESS)
        assessment.refresh_from_db()
        self.assertIsNotNone(assessment.checked_in_at)
        self.assertEqual(assessment.identity_verified_by_id, self.facility_admin.id)
        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditAction.WORKFLOW_TRANSITION,
                target_id=str(assessment.id),
                metadata__event="facility_assessment_checked_in",
            ).exists()
        )

    def test_chunk5_identity_mismatch_pauses_assessment_and_blocks_lab_result_entry(self):
        facility, application = self._create_facility_and_application()
        self.client.force_authenticate(self.facility_admin)
        self.client.patch(f"/api/facility-accreditation/{application['id']}/submit/")
        self.client.force_authenticate(self.lagos_state_admin)
        self.client.patch(f"/api/facility-accreditation/{application['id']}/approve/", {}, format="json")
        db_facility = MedicalFacility.objects.get(id=facility["id"])

        lab_user = User.objects.create_user(
            username="chunk5-lab",
            email="chunk5-lab@example.com",
            password="StrongPass123!",
            role=UserRole.LAB_STAFF,
            organization=self.facility_org,
            state=self.lagos,
        )
        handler_user = User.objects.create_user(
            username="handler-mismatch",
            email="handler-mismatch@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.lagos,
        )
        handler = FoodHandlerProfile.objects.create(
            user=handler_user,
            full_name="Mismatch Handler",
            date_of_birth="1992-06-18",
            gender=Gender.MALE,
            nin="12345678904",
            phone="08030008888",
            email="handler-mismatch@example.com",
            home_address="18 Queue Road",
            state=self.lagos,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-MISMATCH1",
        )
        appointment = Appointment.objects.create(
            food_handler=handler,
            facility=db_facility,
            appointment_date=timezone.now() + timedelta(hours=1),
            status=AppointmentStatus.CONFIRMED,
        )
        assessment = MedicalAssessment.objects.create(
            food_handler=handler,
            facility=db_facility,
            appointment=appointment,
            status=AssessmentStatus.APPOINTMENT_BOOKED,
        )
        lab_test = LabTest.objects.create(
            assessment=assessment,
            requested_by=lab_user,
            test_type="stool_microscopy",
            status=LabTestStatus.SAMPLE_COLLECTION_PENDING,
        )

        self.client.force_authenticate(self.facility_admin)
        mismatch = self.client.patch(
            f"/api/medical-facilities/{facility['id']}/assessments/{assessment.id}/flag-identity-mismatch/",
            {"reason": "Presented document date of birth does not match the record."},
            format="json",
        )

        self.assertEqual(mismatch.status_code, 200)
        assessment.refresh_from_db()
        self.assertEqual(assessment.identity_verification_status, IdentityVerificationStatus.MISMATCH)
        self.assertEqual(assessment.identity_mismatch_reason, "Presented document date of birth does not match the record.")

        self.client.force_authenticate(lab_user)
        result_response = self.client.patch(
            f"/api/lab-tests/{lab_test.id}/result/",
            {"status": LabTestStatus.NEGATIVE, "result_value": "Clear"},
            format="json",
        )

        self.assertEqual(result_response.status_code, 400)
        self.assertIn("identity mismatch", str(data(result_response)).lower())

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

    def test_facility_compliance_dashboard_returns_summary_and_staff_activity(self):
        facility, _ = self._create_facility_and_application()
        db_facility = MedicalFacility.objects.get(id=facility["id"])
        db_facility.accreditation_status = AccreditationStatus.APPROVED
        db_facility.accreditation_start_date = timezone.localdate()
        db_facility.accreditation_expiry_date = timezone.localdate() + timedelta(days=14)
        db_facility.save(update_fields=["accreditation_status", "accreditation_start_date", "accreditation_expiry_date", "updated_at"])

        handler_user = User.objects.create_user(
            username="compliance-handler",
            email="compliance-handler@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.lagos,
        )
        handler = FoodHandlerProfile.objects.create(
            user=handler_user,
            full_name="Compliance Handler",
            date_of_birth="1990-01-01",
            gender=Gender.FEMALE,
            nin="12345678977",
            phone="08030111111",
            email="compliance-handler@example.com",
            home_address="12 Audit Street",
            state=self.lagos,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-COMP-001",
        )
        appointment = Appointment.objects.create(
            food_handler=handler,
            facility=db_facility,
            appointment_date=timezone.now() + timedelta(days=1),
            status=AppointmentStatus.PENDING,
        )
        MedicalAssessment.objects.create(
            food_handler=handler,
            facility=db_facility,
            appointment=appointment,
            status=AssessmentStatus.APPOINTMENT_BOOKED,
        )
        log_action(
            action=AuditAction.UPDATE,
            actor=self.facility_admin,
            organization=db_facility.organization,
            target=db_facility,
            metadata={"event": "facility_profile_reviewed", "module": "Compliance"},
        )

        self.client.force_authenticate(self.facility_admin)
        response = self.client.get(f"/api/medical-facilities/{facility['id']}/compliance-dashboard/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(payload["cards"]["assessments_conducted"], 1)
        self.assertEqual(payload["cards"]["accreditation_status"], AccreditationStatus.APPROVED)
        self.assertTrue(payload["sections"]["staff_activity"])
        self.assertTrue(payload["sections"]["warnings"])

    def test_facility_audit_logs_require_permission_and_support_filters(self):
        facility, _ = self._create_facility_and_application()
        db_facility = MedicalFacility.objects.get(id=facility["id"])
        FacilityTeamService.ensure_default_roles(facility=db_facility, actor=self.facility_admin)
        finance_role = FacilityRole.objects.get(facility=db_facility, name="Finance / Billing Officer")
        compliance_role = FacilityRole.objects.get(facility=db_facility, name="Compliance Officer")

        finance_user = User.objects.create_user(
            username="finance-viewer",
            email="finance-viewer@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.lagos,
        )
        compliance_user = User.objects.create_user(
            username="compliance-viewer",
            email="compliance-viewer@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.lagos,
        )
        FacilityStaffProfile.objects.create(
            user=finance_user,
            facility=db_facility,
            role=finance_role,
            staff_type=FacilityStaffType.FINANCE_USER,
            professional_category=FacilityProfessionalCategory.FINANCE,
            status=FacilityTeamMemberStatus.ACTIVE,
            is_active=True,
        )
        FacilityStaffProfile.objects.create(
            user=compliance_user,
            facility=db_facility,
            role=compliance_role,
            staff_type=FacilityStaffType.FACILITY_ADMIN,
            professional_category=FacilityProfessionalCategory.COMPLIANCE,
            status=FacilityTeamMemberStatus.ACTIVE,
            is_active=True,
        )
        AuditLog.objects.create(
            actor=self.facility_admin,
            action=AuditAction.WORKFLOW_TRANSITION,
            target_type="MedicalAssessment",
            target_id="assessment-12345",
            organization=db_facility.organization,
            metadata={"event": "assessment_checked_in", "assessment_id": "assessment-12345", "module": "Assessments"},
        )
        AuditLog.objects.create(
            actor=compliance_user,
            action=AuditAction.SECURITY_EVENT,
            target_type="MedicalFacility",
            target_id=str(db_facility.id),
            organization=db_facility.organization,
            metadata={"event": "security_review_completed", "module": "Security"},
        )

        self.client.force_authenticate(finance_user)
        denied = self.client.get(f"/api/medical-facilities/{facility['id']}/audit-logs/")
        self.assertEqual(denied.status_code, 403)

        self.client.force_authenticate(compliance_user)
        response = self.client.get(
            f"/api/medical-facilities/{facility['id']}/audit-logs/",
            {"action": AuditAction.WORKFLOW_TRANSITION, "assessment_id": "assessment-12345", "entity_type": "MedicalAssessment"},
        )

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["event"], "assessment_checked_in")
        self.assertEqual(payload[0]["actor_email"], "facility-admin@example.com")

    def test_temporary_unfit_reports_require_permission_and_return_facility_rows(self):
        facility, _ = self._create_facility_and_application()
        db_facility = MedicalFacility.objects.get(id=facility["id"])
        FacilityTeamService.ensure_default_roles(facility=db_facility, actor=self.facility_admin)
        records_role = FacilityRole.objects.get(facility=db_facility, name="Records Officer")
        finance_role = FacilityRole.objects.get(facility=db_facility, name="Finance / Billing Officer")
        permitted_user = User.objects.create_user(
            username="records-user",
            email="records@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.lagos,
        )
        blocked_user = User.objects.create_user(
            username="blocked-finance",
            email="blocked-finance@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.lagos,
        )
        FacilityStaffProfile.objects.create(
            user=permitted_user,
            facility=db_facility,
            role=records_role,
            staff_type=FacilityStaffType.RECORDS_STAFF,
            professional_category=FacilityProfessionalCategory.RECORDS,
            status=FacilityTeamMemberStatus.ACTIVE,
            is_active=True,
        )
        FacilityStaffProfile.objects.create(
            user=blocked_user,
            facility=db_facility,
            role=finance_role,
            staff_type=FacilityStaffType.FINANCE_USER,
            professional_category=FacilityProfessionalCategory.FINANCE,
            status=FacilityTeamMemberStatus.ACTIVE,
            is_active=True,
        )
        employer_org = Organization.objects.create(
            name="Chunk11 Employer",
            organization_type=OrganizationType.EMPLOYER,
            state=self.lagos,
        )
        employer = Employer.objects.create(
            organization=employer_org,
            business_name="Chunk11 Employer",
            establishment_category="restaurant_cafe",
            contact_person_name="Ada",
            contact_person_phone="08030000099",
            contact_person_email="chunk11@example.com",
            address="12 Market Street",
            state=self.lagos,
        )
        handler_user = User.objects.create_user(
            username="chunk11-handler",
            email="chunk11-handler@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.lagos,
        )
        food_handler = FoodHandlerProfile.objects.create(
            user=handler_user,
            full_name="Chunk11 Food Handler",
            date_of_birth="1990-01-01",
            gender=Gender.FEMALE,
            nin="12345678902",
            phone="08031112222",
            email="handler-chunk11@example.com",
            home_address="1 Example Road",
            state=self.lagos,
            employer=employer,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-CHUNK11",
        )
        assessment = MedicalAssessment.objects.create(
            food_handler=food_handler,
            employer=employer,
            facility=db_facility,
            status=AssessmentStatus.TEMPORARILY_NOT_FIT,
            final_decision="temporarily_not_fit",
            return_to_work_date=timezone.localdate() + timedelta(days=7),
            signed_at=timezone.now(),
        )
        GeneratedReport.objects.create(
            report_type="temporarily_not_fit_report",
            file_format="json",
            filters={"assessment_id": str(assessment.id), "kind": "return_to_work"},
            generated_by=self.facility_admin,
            status="generated",
        )

        self.client.force_authenticate(blocked_user)
        denied = self.client.get(f"/api/medical-facilities/{facility['id']}/temporary-unfit-reports/")
        self.assertEqual(denied.status_code, 403)

        self.client.force_authenticate(permitted_user)
        response = self.client.get(f"/api/medical-facilities/{facility['id']}/temporary-unfit-reports/")
        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["food_handler_name"], "Chunk11 Food Handler")
        self.assertEqual(payload[0]["employer_name"], "Chunk11 Employer")

    def test_suspended_facility_staff_loses_facility_route_access_immediately(self):
        facility, _ = self._create_facility_and_application()
        db_facility = MedicalFacility.objects.get(id=facility["id"])
        FacilityTeamService.ensure_default_roles(facility=db_facility, actor=self.facility_admin)
        viewer_role = FacilityRole.objects.get(facility=db_facility, name="Viewer / Auditor")
        viewer_user = User.objects.create_user(
            username="suspended-viewer",
            email="suspended-viewer@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.lagos,
        )
        profile = FacilityStaffProfile.objects.create(
            user=viewer_user,
            facility=db_facility,
            role=viewer_role,
            staff_type=FacilityStaffType.DOCTOR,
            professional_category=FacilityProfessionalCategory.VIEWER,
            status=FacilityTeamMemberStatus.ACTIVE,
            is_active=True,
        )

        self.client.force_authenticate(viewer_user)
        allowed = self.client.get("/api/medical-facilities/me/")
        self.assertEqual(allowed.status_code, 200)

        profile.is_active = False
        profile.status = FacilityTeamMemberStatus.SUSPENDED
        profile.save(update_fields=["is_active", "status", "updated_at"])

        denied = self.client.get("/api/medical-facilities/me/")
        self.assertEqual(denied.status_code, 403)

    def test_sensitive_appointment_action_requires_permission_key(self):
        facility, _ = self._create_facility_and_application()
        db_facility = MedicalFacility.objects.get(id=facility["id"])
        FacilityTeamService.ensure_default_roles(facility=db_facility, actor=self.facility_admin)
        compliance_role = FacilityRole.objects.get(facility=db_facility, name="Compliance Officer")
        compliance_user = User.objects.create_user(
            username="compliance-no-confirm",
            email="compliance-no-confirm@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.lagos,
        )
        FacilityStaffProfile.objects.create(
            user=compliance_user,
            facility=db_facility,
            role=compliance_role,
            staff_type=FacilityStaffType.DOCTOR,
            professional_category=FacilityProfessionalCategory.COMPLIANCE,
            status=FacilityTeamMemberStatus.ACTIVE,
            is_active=True,
        )
        handler_user = User.objects.create_user(
            username="permission-handler",
            email="permission-handler@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.lagos,
        )
        handler = FoodHandlerProfile.objects.create(
            user=handler_user,
            full_name="Permission Handler",
            date_of_birth="1994-02-01",
            gender=Gender.FEMALE,
            nin="12345678905",
            phone="08039999999",
            email="permission-handler@example.com",
            home_address="23 Queue Road",
            state=self.lagos,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-PERM-001",
        )
        appointment = Appointment.objects.create(
            food_handler=handler,
            facility=db_facility,
            appointment_date=timezone.now() + timedelta(hours=4),
            status=AppointmentStatus.PENDING,
        )

        self.client.force_authenticate(compliance_user)
        response = self.client.patch(
            f"/api/medical-facilities/{facility['id']}/appointments/{appointment.id}/confirm/",
            {"notes": "Trying to confirm without permission."},
            format="json",
        )

        self.assertEqual(response.status_code, 403)


class FederalMinimumEnforcementTests(APITestCase):
    def setUp(self):
        from apps.locations.models import State
        from apps.organizations.models import Organization, OrganizationType
        from apps.facilities.models import MedicalFacility, FacilityAccreditationApplication, FacilityType, OwnershipType, AccreditationStatus
        from apps.facilities.services import FacilityAccreditationService

        self.State = State
        self.Application = FacilityAccreditationApplication
        self.AccreditationStatus = AccreditationStatus
        self.service = FacilityAccreditationService

        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.reviewer = User.objects.create_user("fmin-reviewer", "fmin-reviewer@example.com", "StrongPass123!", role=UserRole.STATE_ADMIN, state=self.lagos)
        org = Organization.objects.create(name="FMin Facility Org", organization_type=OrganizationType.MEDICAL_FACILITY, state=self.lagos)
        self.facility = MedicalFacility.objects.create(
            organization=org, facility_name="FMin Clinic", facility_type=FacilityType.CLINIC,
            ownership_type=OwnershipType.PRIVATE, license_number="FMIN-1", address="addr",
            state=self.lagos, contact_person="c", phone="0800", email="fmin@example.com",
            accreditation_status=AccreditationStatus.SUBMITTED,
        )

    def _make_active_policy_with_facility_rule(self):
        from apps.standards.models import PolicyVersion, PolicyVersionStatus, PolicyVersionType, FacilityRequirementRule, StandardStatus
        from apps.standards.services import bump_active_standards_cache_version

        pv = PolicyVersion.objects.create(
            version_code="FAC-1", title="Facility Standard", description="d", version_type=PolicyVersionType.MAJOR,
            status=PolicyVersionStatus.ACTIVE, change_summary="c",
        )
        FacilityRequirementRule.objects.create(
            policy_version=pv, requirement_name="QR capability", requirement_code="qr_capability",
            category="digital_infrastructure", mandatory=True, status=StandardStatus.ACTIVE,
        )
        bump_active_standards_cache_version()
        return pv

    def test_approval_blocked_when_federal_rules_exist_and_checklist_incomplete(self):
        self._make_active_policy_with_facility_rule()
        application = self.Application.objects.create(facility=self.facility, application_status=self.AccreditationStatus.SUBMITTED)
        from rest_framework.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.service.approve(application=application, reviewer=self.reviewer)

    def test_approval_allowed_without_active_federal_rules(self):
        application = self.Application.objects.create(facility=self.facility, application_status=self.AccreditationStatus.SUBMITTED)
        result = self.service.approve(application=application, reviewer=self.reviewer)
        self.assertEqual(result.application_status, self.AccreditationStatus.APPROVED)
