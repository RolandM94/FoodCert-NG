from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.assessments.models import FitnessDecision, MedicalAssessment
from apps.certificates.models import Certificate, CertificateStatus
from apps.employers.models import Employer, EstablishmentCategory
from apps.facilities.models import AccreditationStatus, FacilityType, MedicalFacility, OwnershipType
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, FoodHandlerStatus, Gender
from apps.illness.models import IllnessReport
from apps.inspections.models import EnforcementAction, Inspection, InspectionStatus
from apps.locations.models import State
from apps.notifications.models import Notification, NotificationChannel, NotificationStatus, NotificationType
from apps.organizations.models import Organization, OrganizationType, OrganizationUnit, OrganizationUnitType
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.reports.models import GeneratedReport, ReportSchedule
from apps.settlements.models import Settlement, SettlementStatus
from apps.vaccinations.models import VaccinationRecord, VaccinationStatus, VaccineType

User = get_user_model()


def data(response):
    if isinstance(response.data, list):
        return response.data
    return response.data.get("data", response.data)


class DashboardReportingTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.employer_org = Organization.objects.create(name="Clean Foods", organization_type=OrganizationType.EMPLOYER, state=self.lagos)
        self.facility_org = Organization.objects.create(name="Mainland Clinic", organization_type=OrganizationType.MEDICAL_FACILITY, state=self.lagos)
        self.oyo_employer_org = Organization.objects.create(name="Oyo Foods", organization_type=OrganizationType.EMPLOYER, state=self.oyo)
        self.employer_user = User.objects.create_user(
            "employer",
            "employer@example.com",
            "StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
            state=self.lagos,
        )
        self.facility_admin = User.objects.create_user(
            "facility-admin",
            "facility@example.com",
            "StrongPass123!",
            role=UserRole.FACILITY_ADMIN,
            organization=self.facility_org,
            state=self.lagos,
        )
        self.state_admin = User.objects.create_user("state-admin", "state@example.com", "StrongPass123!", role=UserRole.STATE_ADMIN, state=self.lagos)
        self.federal_admin = User.objects.create_user("federal", "federal@example.com", "StrongPass123!", role=UserRole.FEDERAL_ADMIN)
        self.doctor = User.objects.create_user(
            "doctor",
            "doctor@example.com",
            "StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.lagos,
        )
        self.handler_user = User.objects.create_user("handler", "handler@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.lagos)
        self.employer = Employer.objects.create(
            user=self.employer_user,
            organization=self.employer_org,
            business_name="Clean Foods",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Ada",
            contact_person_phone="08030000000",
            contact_person_email="ada@example.com",
            address="1 Food Road",
            state=self.lagos,
        )
        self.oyo_employer = Employer.objects.create(
            organization=self.oyo_employer_org,
            business_name="Oyo Foods",
            establishment_category=EstablishmentCategory.BAKERY,
            contact_person_name="Bola",
            contact_person_phone="08030000010",
            contact_person_email="bola@example.com",
            address="2 Oyo Road",
            state=self.oyo,
        )
        self.facility = MedicalFacility.objects.create(
            organization=self.facility_org,
            facility_name="Mainland Clinic",
            facility_type=FacilityType.CLINIC,
            ownership_type=OwnershipType.PRIVATE,
            license_number="MC-001",
            address="12 Health Road",
            state=self.lagos,
            contact_person="Dr Ada",
            phone="08030000001",
            email="clinic@example.com",
            accreditation_status=AccreditationStatus.APPROVED,
            accreditation_start_date=timezone.localdate(),
            accreditation_expiry_date=timezone.localdate() + timezone.timedelta(days=40),
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
            state=self.lagos,
            employer=self.employer,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-REP001",
            current_status=FoodHandlerStatus.FIT,
        )
        self.uncertified_handler = FoodHandlerProfile.objects.create(
            user=User.objects.create_user("handler2", "handler2@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.lagos),
            full_name="Bisi Ade",
            date_of_birth="1994-05-10",
            gender=Gender.FEMALE,
            nin="12345678902",
            phone="08030000004",
            email="bisi@example.com",
            home_address="4 Allen Avenue",
            state=self.lagos,
            employer=self.employer,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-REP002",
            current_status=FoodHandlerStatus.TEMPORARILY_EXCLUDED,
        )
        payment = PaymentTransaction.objects.create(
            payer_user=self.handler_user,
            payer_type="food_handler",
            related_entity_type="food_handler_assessment",
            related_entity_id=self.food_handler.id,
            amount="15000.00",
            payment_provider="mock",
            internal_reference="ASS-REP-001",
            status=PaymentStatus.SUCCESS,
            paid_at=timezone.now(),
        )
        self.assessment = MedicalAssessment.objects.create(
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
            signed_at=timezone.now(),
            status="certificate_issued",
        )
        self.certificate = Certificate.objects.create(
            certificate_number="FCN-LA-REP001",
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
            verification_url="http://localhost:3000/verify/FCN-LA-REP001",
            digital_signature_hash="hash",
        )
        VaccinationRecord.objects.create(
            food_handler=self.food_handler,
            assessment=self.assessment,
            vaccine_type=VaccineType.TYPHOID,
            dose_number=1,
            date_administered=timezone.localdate(),
            status=VaccinationStatus.VALID,
            recorded_by=self.doctor,
        )
        IllnessReport.objects.create(
            food_handler=self.uncertified_handler,
            employer=self.employer,
            reported_by=self.employer_user,
            symptoms={"fever": True},
            clearance_status="cleared",
        )
        Inspection.objects.create(
            inspector=self.state_admin,
            employer=self.employer,
            checklist_responses={"registered": True, "certificates": False},
            compliance_score="50.00",
            enforcement_action=EnforcementAction.WARNING,
            status=InspectionStatus.SUBMITTED,
        )
        Settlement.objects.create(
            facility=self.facility,
            state=self.lagos,
            payment_transaction=payment,
            assessment=self.assessment,
            gross_amount="15000.00",
            facility_amount="10000.00",
            state_amount="3000.00",
            platform_amount="2000.00",
            settlement_status=SettlementStatus.PAID,
        )

    def test_employer_dashboard_is_scoped_and_omits_medical_detail(self):
        self.client.force_authenticate(self.employer_user)

        response = self.client.get("/api/dashboard/employer/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(payload["cards"]["total_food_handlers"], 2)
        self.assertEqual(payload["cards"]["valid_certificates"], 1)
        self.assertEqual(payload["cards"]["compliance_percentage"], 50.0)
        self.assertNotIn("doctor_notes", str(payload))
        self.assertNotIn("lab_tests", str(payload))

    def test_employer_dashboard_defaults_to_branch_manager_unit(self):
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
        self.food_handler.business_branch = branch
        self.food_handler.save(update_fields=["business_branch", "updated_at"])
        self.uncertified_handler.business_branch = other_branch
        self.uncertified_handler.save(update_fields=["business_branch", "updated_at"])
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
        response = self.client.get("/api/dashboard/employer/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(payload["branch"]["id"], str(branch.id))
        self.assertEqual(payload["cards"]["total_food_handlers"], 1)

    def test_nested_employer_dashboard_returns_prd_metrics(self):
        self.client.force_authenticate(self.employer_user)

        response = self.client.get(f"/api/employers/{self.employer.id}/dashboard/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(payload["cards"]["total_handlers"], 2)
        self.assertEqual(payload["cards"]["fit"], 1)
        self.assertEqual(payload["cards"]["excluded"], 1)
        self.assertEqual(payload["cards"]["open_inspections"], 1)
        self.assertEqual(payload["cards"]["compliance_percentage"], 50.0)
        self.assertIn("branch_breakdown", payload["charts"])
        self.assertNotIn("doctor_notes", str(payload))
        self.assertNotIn("lab_tests", str(payload))

    def test_nested_employer_dashboard_locks_branch_manager_scope(self):
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
        self.food_handler.business_branch = branch
        self.food_handler.save(update_fields=["business_branch", "updated_at"])
        self.uncertified_handler.business_branch = other_branch
        self.uncertified_handler.save(update_fields=["business_branch", "updated_at"])
        branch_manager = User.objects.create_user(
            "nested-branch-manager",
            "nested-branch-manager@example.com",
            "StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
            unit=branch,
            unit_restricted=True,
        )

        self.client.force_authenticate(branch_manager)
        response = self.client.get(f"/api/employers/{self.employer.id}/dashboard/?branch={other_branch.id}")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(payload["scope"]["branch"], str(branch.id))
        self.assertEqual(payload["cards"]["total_handlers"], 1)

    def test_nested_employer_notifications_and_settings(self):
        Notification.objects.create(
            recipient=self.employer_user,
            notification_type=NotificationType.COMPLIANCE_NOTICE,
            channel=NotificationChannel.IN_APP,
            status=NotificationStatus.DELIVERED,
            subject="Inspection notice",
            body="Please respond to your inspection notice.",
        )
        self.client.force_authenticate(self.employer_user)

        notifications_response = self.client.get(f"/api/employers/{self.employer.id}/notifications/")
        settings_response = self.client.patch(
            f"/api/employers/{self.employer.id}/settings/",
            {
                "notification_preferences": {"certificate_expiry_reminder": {"email": True, "sms": False, "in_app": True}},
                "business_settings": {"renewal_reminder_days": 30, "auto_assign_branch": False},
            },
            format="json",
        )

        self.assertEqual(notifications_response.status_code, 200)
        self.assertEqual(data(notifications_response)["unread_count"], 1)
        self.assertEqual(settings_response.status_code, 200)
        self.employer.refresh_from_db()
        self.assertEqual(self.employer.business_settings["renewal_reminder_days"], 30)

    def test_state_dashboard_is_state_scoped(self):
        FoodHandlerProfile.objects.create(
            user=User.objects.create_user("oyo-handler", "oyo-handler@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.oyo),
            full_name="Oyo Handler",
            date_of_birth="1990-01-01",
            gender=Gender.MALE,
            nin="22345678901",
            phone="08030000999",
            email="oyo-handler@example.com",
            home_address="Ibadan",
            state=self.oyo,
            employer=self.oyo_employer,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-OYO001",
        )
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/dashboard/state/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data(response)["cards"]["registered_food_handlers"], 2)

    def test_federal_dashboard_requires_federal_role(self):
        self.client.force_authenticate(self.employer_user)
        blocked = self.client.get("/api/dashboard/federal/")
        self.assertEqual(blocked.status_code, 403)

        self.client.force_authenticate(self.federal_admin)
        response = self.client.get("/api/dashboard/federal/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("national_certification_coverage", data(response)["cards"])

    def test_facility_dashboard_reports_settlements_and_accreditation(self):
        self.client.force_authenticate(self.facility_admin)

        response = self.client.get("/api/dashboard/facility/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data(response)["cards"]["settled_amount"], "10000")
        self.assertEqual(data(response)["cards"]["accreditation_status"], AccreditationStatus.APPROVED)

    def test_report_export_creates_csv_file_and_generated_record(self):
        self.client.force_authenticate(self.employer_user)

        response = self.client.get("/api/reports/employer-compliance/?file_format=csv")

        self.assertEqual(response.status_code, 200)
        report = data(response)
        self.assertEqual(report["file_format"], "csv")
        self.assertTrue(report["file_url"].endswith(".csv"))
        self.assertEqual(GeneratedReport.objects.count(), 1)

    def test_nested_employer_compliance_report_is_scoped_and_private(self):
        self.client.force_authenticate(self.employer_user)

        response = self.client.get(f"/api/employers/{self.employer.id}/reports/compliance/?format=csv")

        self.assertEqual(response.status_code, 200)
        report = data(response)
        self.assertEqual(report["report_type"], "employer_compliance")
        self.assertEqual(report["file_format"], "csv")
        self.assertEqual(report["summary"]["cards"]["handler_count"], 2)
        self.assertEqual(report["summary"]["cards"]["certified_count"], 1)
        self.assertNotIn("nin", str(report).lower())
        self.assertNotIn("doctor_notes", str(report).lower())
        self.assertNotIn("lab_tests", str(report).lower())

    def test_nested_employer_certificate_report_supports_expiry_filters(self):
        self.client.force_authenticate(self.employer_user)
        date_to = (timezone.localdate() + timezone.timedelta(days=365)).isoformat()

        response = self.client.get(f"/api/employers/{self.employer.id}/reports/certificates/?format=pdf&date_to={date_to}")

        self.assertEqual(response.status_code, 200)
        report = data(response)
        self.assertEqual(report["report_type"], "employer_certificates")
        self.assertEqual(report["file_format"], "pdf")
        self.assertTrue(report["file_url"].endswith(".pdf"))
        self.assertEqual(report["summary"]["cards"]["total_certificates"], 1)
        self.assertEqual(report["summary"]["sections"]["certificates"][0]["certificate_number"], self.certificate.certificate_number)

    def test_nested_employer_vaccination_report_honors_branch_manager_scope(self):
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
        self.food_handler.business_branch = branch
        self.food_handler.save(update_fields=["business_branch", "updated_at"])
        self.uncertified_handler.business_branch = other_branch
        self.uncertified_handler.save(update_fields=["business_branch", "updated_at"])
        branch_manager = User.objects.create_user(
            "report-branch-manager",
            "report-branch-manager@example.com",
            "StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
            unit=branch,
            unit_restricted=True,
        )
        self.client.force_authenticate(branch_manager)

        response = self.client.get(f"/api/employers/{self.employer.id}/reports/vaccinations/?format=excel")

        self.assertEqual(response.status_code, 200)
        report = data(response)
        self.assertEqual(report["report_type"], "employer_vaccinations")
        self.assertEqual(report["file_format"], "excel")
        self.assertTrue(report["file_url"].endswith(".xls"))
        self.assertEqual(report["summary"]["cards"]["total_handlers"], 1)
        self.assertEqual(report["summary"]["cards"]["typhoid_valid"], 1)

    def test_report_schedule_and_generated_list_are_user_scoped(self):
        self.client.force_authenticate(self.employer_user)
        schedule_response = self.client.post(
            "/api/reports/schedule/",
            {"report_type": "employer_compliance", "frequency": "monthly", "filters": {}, "recipients": ["ops@example.com"]},
            format="json",
        )

        self.assertEqual(schedule_response.status_code, 201)
        self.assertEqual(ReportSchedule.objects.count(), 1)

        list_response = self.client.get("/api/reports/generated/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(data(list_response), [])
