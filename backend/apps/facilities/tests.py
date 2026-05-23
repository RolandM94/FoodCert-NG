from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.assessments.models import AssessmentStatus, MedicalAssessment
from apps.audit.models import AuditAction, AuditLog
from apps.facilities.models import AccreditationStatus, FacilityAccreditationApplication, FacilityDocument, FacilityStaffProfile, MedicalFacility
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, Gender
from apps.lab_tests.models import LabTest
from apps.locations.models import State
from apps.organizations.models import Organization, OrganizationType, OrganizationUnit, OrganizationUnitType

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

    def test_facility_admin_can_register_facility_and_apply(self):
        facility, application = self._create_facility_and_application()

        self.assertEqual(facility["accreditation_status"], AccreditationStatus.DRAFT)
        self.assertTrue(facility["profile_complete"])
        self.assertEqual(facility["ward"], "Ward A")
        self.assertEqual(facility["service_capacity"], 80)
        self.assertEqual(application["application_status"], AccreditationStatus.DRAFT)
        self.assertTrue(application["checklist_complete"])

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
