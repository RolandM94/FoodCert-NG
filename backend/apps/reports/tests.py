from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db.models import Count
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole, UserStatus
from apps.assessments.models import FitnessDecision, MedicalAssessment, StepStatus
from apps.certificates.models import Certificate, CertificateRequest, CertificateRequestStatus, CertificateStatus
from apps.employers.models import Employer, EstablishmentCategory
from apps.facilities.models import AccreditationStatus, FacilityType, MedicalFacility, OwnershipType
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, FoodHandlerStatus, Gender
from apps.illness.models import IllnessReport
from apps.inspections.models import EnforcementAction, Inspection, InspectionPriority, InspectionStatus
from apps.lab_tests.models import LabTest, LabTestStatus, LabTestType
from apps.locations.models import LGA, State
from apps.notifications.models import Notification, NotificationCategory
from apps.organizations.models import Organization, OrganizationType, OrganizationUnit, OrganizationUnitType
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.ministries.models import StateReport, StateReportStatus
from apps.reports.models import (
    DashboardWidget,
    DataQualityIssue,
    DataQualityIssueSeverity,
    DataQualityIssueStatus,
    GeneratedReport,
    GeneratedReportStatus,
    MEIndicator,
    MEIndicatorValue,
    ReportSchedule,
    ReportTemplate,
    ReportType,
    ScheduledReport,
    ScheduledReportFrequency,
)
from apps.reports.privacy_serializers import (
    AdminReportSerializer,
    EmployerSafeComplianceSerializer,
    FacilityOperationalSerializer,
    FederalAggregateReportSerializer,
    FinanceReportSerializer,
    FoodHandlerReportSerializer,
    InspectorSafeReportSerializer,
    MedicalRestrictedSerializer,
    StateRegulatoryReportSerializer,
)
from apps.reports.services import ComplianceStatusService, MEIndicatorService
from apps.reports.tasks import run_me_indicator_calculations
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
        self.super_admin = User.objects.create_user("super-admin", "super@example.com", "StrongPass123!", role=UserRole.SUPER_ADMIN, status=UserStatus.ACTIVE)
        self.inspector_user = User.objects.create_user("inspector", "inspector@example.com", "StrongPass123!", role=UserRole.INSPECTOR, state=self.lagos)
        self.doctor = User.objects.create_user(
            "doctor",
            "doctor@example.com",
            "StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.lagos,
        )
        self.lab_staff = User.objects.create_user(
            "lab-staff",
            "lab@example.com",
            "StrongPass123!",
            role=UserRole.LAB_STAFF,
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

    def test_compliance_status_service_returns_handler_and_employer_summary(self):
        handler_status = ComplianceStatusService.get_food_handler_operational_status(self.food_handler.id)
        employer_summary = ComplianceStatusService.get_employer_compliance_summary(self.employer.id)

        self.assertEqual(handler_status["certificate_status"], CertificateStatus.ACTIVE)
        self.assertEqual(handler_status["overall_compliance_status"], "compliant")
        self.assertEqual(employer_summary["total_food_handlers"], 2)
        self.assertEqual(employer_summary["valid_certificates"], 1)
        self.assertEqual(employer_summary["compliance_percentage"], 50.0)
        self.assertEqual(employer_summary["overall_compliance_status"], "partially_compliant")
        self.assertEqual(employer_summary["open_inspections"], 1)

    def test_compliance_status_service_returns_state_and_national_summary(self):
        state_summary = ComplianceStatusService.get_state_compliance_summary(self.lagos.id)
        national_summary = ComplianceStatusService.get_national_compliance_summary()

        self.assertEqual(state_summary["registered_food_handlers"], 2)
        self.assertEqual(state_summary["certified_food_handlers"], 1)
        self.assertEqual(state_summary["registered_employers"], 1)
        self.assertEqual(state_summary["approved_facilities"], 1)
        self.assertEqual(state_summary["enforcement_notices"], 1)
        self.assertEqual(state_summary["overall_compliance_status"], "partially_compliant")
        self.assertEqual(national_summary["registered_food_handlers"], 2)
        self.assertEqual(national_summary["certified_food_handlers"], 1)
        self.assertEqual(national_summary["inspections_conducted"], 1)

    def test_food_handler_dashboard_returns_personal_workflow_state(self):
        IllnessReport.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            reported_by=self.employer_user,
            symptoms={"vomiting": True},
            clearance_status="pending",
            earliest_return_date=timezone.localdate() + timezone.timedelta(days=3),
        )
        self.client.force_authenticate(self.handler_user)

        response = self.client.get("/api/dashboard/food-handler/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(payload["food_handler"]["system_identifier"], "FCN-REP001")
        self.assertEqual(payload["cards"]["certificate_status"], CertificateStatus.ACTIVE)
        self.assertEqual(payload["cards"]["assessment_status"], "certificate_issued")
        self.assertEqual(payload["cards"]["vaccination_status"], "current")
        self.assertEqual(payload["cards"]["renewal_status"], "current")
        self.assertEqual(payload["cards"]["return_to_work_status"], "pending")
        self.assertEqual(payload["sections"]["my_certificate"]["certificate_number"], "FCN-LA-REP001")
        self.assertEqual(payload["sections"]["my_assessment"]["decision"], FitnessDecision.FIT)
        self.assertEqual(payload["sections"]["vaccination_records"][0]["vaccine_type"], VaccineType.TYPHOID)
        self.assertEqual(payload["sections"]["illness_return_to_work"]["clearance_status"], "pending")
        self.assertNotIn("doctor_notes", str(payload))
        self.assertNotIn("lab_tests", str(payload))

    def test_food_handler_dashboard_requires_food_handler_role(self):
        self.client.force_authenticate(self.employer_user)

        response = self.client.get("/api/dashboard/food-handler/")

        self.assertEqual(response.status_code, 403)

    def test_doctor_dashboard_returns_queue_and_workload_metrics(self):
        pending_assessment = MedicalAssessment.objects.create(
            food_handler=self.uncertified_handler,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            declaration_status=StepStatus.SUBMITTED,
            physical_exam_status=StepStatus.PENDING,
            lab_status=StepStatus.SUBMITTED,
            vaccination_status=StepStatus.PENDING,
            final_decision=FitnessDecision.PENDING,
            status="doctor_decision_pending",
        )
        LabTest.objects.create(
            assessment=pending_assessment,
            test_type=LabTestType.TYPHOID,
            status=LabTestStatus.SUBMITTED_TO_DOCTOR,
            requested_by=self.doctor,
            resulted_by=self.facility_admin,
            submitted_to_doctor_at=timezone.now(),
        )
        MedicalAssessment.objects.create(
            food_handler=self.uncertified_handler,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            declaration_status=StepStatus.REVIEWED,
            physical_exam_status=StepStatus.COMPLETED,
            lab_status=StepStatus.REVIEWED,
            vaccination_status=StepStatus.REVIEWED,
            final_decision=FitnessDecision.TEMPORARILY_NOT_FIT,
            return_to_work_date=timezone.localdate() + timezone.timedelta(days=7),
            signed_at=timezone.now(),
            status="temporarily_not_fit",
        )
        IllnessReport.objects.create(
            food_handler=self.uncertified_handler,
            employer=self.employer,
            reported_by=self.employer_user,
            symptoms={"fever": True},
            clearance_status="under_review",
        )
        self.client.force_authenticate(self.doctor)

        response = self.client.get("/api/dashboard/doctor/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(payload["cards"]["assigned_assessments"], 3)
        self.assertEqual(payload["cards"]["declaration_reviews_pending"], 1)
        self.assertEqual(payload["cards"]["physical_exams_pending"], 1)
        self.assertEqual(payload["cards"]["lab_results_pending_review"], 2)
        self.assertEqual(payload["cards"]["vaccination_reviews_pending"], 1)
        self.assertEqual(payload["cards"]["decisions_pending"], 1)
        self.assertEqual(payload["cards"]["temporarily_not_fit_cases"], 1)
        self.assertEqual(payload["cards"]["return_to_work_reviews_pending"], 1)
        queue_types = {item["queue_type"] for item in payload["sections"]["pending_queue"]}
        self.assertTrue({"declaration_review", "physical_exam", "lab_review", "vaccination_review", "decision"}.issubset(queue_types))
        self.assertEqual(payload["sections"]["recent_decisions"][0]["decision"], FitnessDecision.TEMPORARILY_NOT_FIT)
        self.assertIn({"status": "certificate_issued", "total": 1}, payload["sections"]["workload_summary"])
        self.assertNotIn("doctor_notes", str(payload))
        self.assertNotIn("result_notes", str(payload))

    def test_doctor_dashboard_requires_doctor_role(self):
        self.client.force_authenticate(self.employer_user)

        response = self.client.get("/api/dashboard/doctor/")

        self.assertEqual(response.status_code, 403)

    def test_lab_dashboard_returns_lab_queues_and_turnaround_metrics(self):
        now = timezone.now()
        sample_pending = LabTest.objects.create(
            assessment=self.assessment,
            test_type=LabTestType.STOOL_MICROSCOPY,
            test_name="Stool microscopy",
            status=LabTestStatus.SAMPLE_COLLECTION_PENDING,
            requested_by=self.doctor,
            requested_at=now - timezone.timedelta(hours=8),
        )
        result_pending = LabTest.objects.create(
            assessment=self.assessment,
            test_type=LabTestType.TYPHOID,
            test_name="Typhoid",
            status=LabTestStatus.IN_PROGRESS,
            requested_by=self.doctor,
            sample_collected_at=now - timezone.timedelta(hours=4),
            requested_at=now - timezone.timedelta(hours=10),
        )
        submitted = LabTest.objects.create(
            assessment=self.assessment,
            test_type=LabTestType.HEPATITIS_A_ANTIGEN,
            test_name="Hepatitis A antigen",
            status=LabTestStatus.SUBMITTED_TO_DOCTOR,
            requested_by=self.doctor,
            resulted_by=self.lab_staff,
            requested_at=now - timezone.timedelta(hours=12),
            sample_collected_at=now - timezone.timedelta(hours=9),
            resulted_at=now - timezone.timedelta(hours=2),
            submitted_to_doctor_at=now,
        )
        LabTest.objects.create(
            assessment=self.assessment,
            test_type=LabTestType.CHOLERA,
            test_name="Cholera",
            status=LabTestStatus.REPEAT_REQUIRED,
            repeat_required=True,
            requested_by=self.doctor,
            resulted_by=self.lab_staff,
            requested_at=now - timezone.timedelta(hours=20),
            resulted_at=now - timezone.timedelta(hours=5),
        )
        self.client.force_authenticate(self.lab_staff)

        response = self.client.get("/api/dashboard/lab/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(payload["cards"]["lab_requests_pending"], 2)
        self.assertEqual(payload["cards"]["samples_pending_collection"], 1)
        self.assertEqual(payload["cards"]["results_pending_upload"], 1)
        self.assertEqual(payload["cards"]["results_submitted_today"], 1)
        self.assertEqual(payload["cards"]["repeat_tests_required"], 1)
        self.assertEqual(payload["cards"]["average_turnaround_time"], 12.5)
        self.assertEqual(payload["sections"]["pending_sample_collection"][0]["id"], str(sample_pending.id))
        self.assertEqual(payload["sections"]["pending_result_upload"][0]["id"], str(result_pending.id))
        self.assertEqual(payload["sections"]["recent_lab_results"][0]["id"], str(submitted.id))
        self.assertNotIn("result_notes", str(payload))
        self.assertNotIn("lab_staff_notes", str(payload))

    def test_lab_dashboard_requires_lab_staff_role(self):
        self.client.force_authenticate(self.doctor)

        response = self.client.get("/api/dashboard/lab/")

        self.assertEqual(response.status_code, 403)

    def test_inspector_dashboard_returns_tasks_and_performance_summary(self):
        now = timezone.now()
        due = Inspection.objects.create(
            inspector=self.inspector_user,
            employer=self.employer,
            inspection_type="routine",
            priority=InspectionPriority.HIGH,
            status=InspectionStatus.SCHEDULED,
            scheduled_at=now,
            inspection_date=now,
            compliance_score="80.00",
        )
        overdue = Inspection.objects.create(
            inspector=self.inspector_user,
            employer=self.employer,
            inspection_type="complaint_based",
            priority=InspectionPriority.CRITICAL,
            status=InspectionStatus.IN_PROGRESS,
            scheduled_at=now - timezone.timedelta(days=2),
            inspection_date=now - timezone.timedelta(days=2),
            compliance_score="50.00",
        )
        Inspection.objects.create(
            inspector=self.inspector_user,
            employer=self.employer,
            inspection_type="follow_up",
            priority=InspectionPriority.MEDIUM,
            status=InspectionStatus.CORRECTIVE_ACTION_PENDING,
            inspection_date=now - timezone.timedelta(days=1),
            enforcement_action=EnforcementAction.COMPLIANCE_NOTICE,
        )
        Inspection.objects.create(
            inspector=self.inspector_user,
            employer=self.employer,
            inspection_type="follow_up",
            priority=InspectionPriority.MEDIUM,
            status=InspectionStatus.FOLLOW_UP_REQUIRED,
            inspection_date=now - timezone.timedelta(days=1),
        )
        Inspection.objects.create(
            inspector=self.inspector_user,
            employer=self.employer,
            inspection_type="routine",
            priority=InspectionPriority.LOW,
            status=InspectionStatus.SUBMITTED,
            inspection_date=now,
        )
        Inspection.objects.create(
            inspector=self.inspector_user,
            employer=self.employer,
            inspection_type="routine",
            priority=InspectionPriority.LOW,
            status=InspectionStatus.CLOSED,
            inspection_date=now - timezone.timedelta(days=3),
            closed_at=now,
        )
        self.client.force_authenticate(self.inspector_user)

        response = self.client.get("/api/dashboard/inspector/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(payload["cards"]["assigned_inspections"], 6)
        self.assertEqual(payload["cards"]["due_today"], 1)
        self.assertEqual(payload["cards"]["overdue"], 1)
        self.assertEqual(payload["cards"]["in_progress"], 1)
        self.assertEqual(payload["cards"]["submitted"], 1)
        self.assertEqual(payload["cards"]["notices_issued"], 1)
        self.assertEqual(payload["cards"]["corrective_actions_pending"], 1)
        self.assertEqual(payload["cards"]["follow_ups_due"], 1)
        self.assertEqual(payload["cards"]["high_priority"], 2)
        self.assertEqual(payload["cards"]["closed_this_month"], 1)
        task_references = {item["reference"] for item in payload["sections"]["task_list"]}
        self.assertIn(due.reference, task_references)
        self.assertIn(overdue.reference, task_references)
        self.assertEqual(payload["sections"]["performance_summary"]["open"], 4)
        self.assertEqual(payload["sections"]["performance_summary"]["closed"], 1)
        self.assertEqual(payload["sections"]["performance_summary"]["average_compliance_score"], "65")

    def test_inspector_dashboard_requires_inspector_role(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/dashboard/inspector/")

        self.assertEqual(response.status_code, 403)

    def test_admin_dashboard_returns_platform_health_metrics(self):
        failed_payment = PaymentTransaction.objects.create(
            payer_user=self.handler_user,
            payer_type="food_handler",
            related_entity_type="food_handler_assessment",
            related_entity_id=self.food_handler.id,
            amount="12000.00",
            payment_provider="mock",
            internal_reference="ASS-REP-FAILED",
            status=PaymentStatus.FAILED,
        )
        GeneratedReport.objects.create(
            title="Failed National Report",
            report_type="national",
            file_format="json",
            filters={},
            summary={},
            data_snapshot={},
            generated_by=self.super_admin,
            status=GeneratedReportStatus.FAILED,
            error_message="Worker timeout",
        )
        CertificateRequest.objects.create(
            assessment=MedicalAssessment.objects.create(
                food_handler=self.uncertified_handler,
                employer=self.employer,
                facility=self.facility,
                doctor=self.doctor,
                declaration_status=StepStatus.REVIEWED,
                physical_exam_status=StepStatus.COMPLETED,
                lab_status=StepStatus.REVIEWED,
                vaccination_status=StepStatus.REVIEWED,
                final_decision=FitnessDecision.NOT_FIT,
                status="rejected_by_state",
            ),
            requested_by=self.facility_admin,
            reviewed_by=self.state_admin,
            status=CertificateRequestStatus.REJECTED,
        )
        DataQualityIssue.objects.create(
            issue_type="api_error",
            severity=DataQualityIssueSeverity.CRITICAL,
            module="reports",
            target_type="generated_report",
            description="Recent report endpoint failure.",
            status=DataQualityIssueStatus.OPEN,
        )
        self.client.force_authenticate(self.super_admin)

        response = self.client.get("/api/dashboard/admin/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertGreaterEqual(payload["cards"]["total_users"], 9)
        self.assertEqual(payload["cards"]["active_organizations"], 3)
        self.assertEqual(payload["cards"]["active_employers"], 2)
        self.assertEqual(payload["cards"]["active_facilities"], 1)
        self.assertEqual(payload["cards"]["active_state_ministry_accounts"], 1)
        self.assertEqual(payload["cards"]["active_federal_users"], 1)
        self.assertEqual(payload["cards"]["api_errors"], 1)
        self.assertEqual(payload["cards"]["failed_payments"], 1)
        self.assertEqual(payload["cards"]["failed_certificate_generation"], 1)
        self.assertEqual(payload["cards"]["failed_report_jobs"], 1)
        self.assertEqual(payload["cards"]["background_job_health"], "attention_required")
        self.assertIn("megabytes", payload["cards"]["storage_usage"])
        self.assertEqual(payload["sections"]["recent_failed_payments"][0]["id"], str(failed_payment.id))
        self.assertTrue(any(item["status"] == "attention_required" for item in payload["sections"]["system_health"]))

    def test_admin_dashboard_requires_super_admin_role(self):
        self.client.force_authenticate(self.federal_admin)

        response = self.client.get("/api/dashboard/admin/")

        self.assertEqual(response.status_code, 403)

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
            category=NotificationCategory.ENFORCEMENT,
            title="Inspection notice",
            message="Please respond to your inspection notice.",
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
        lga = LGA.objects.create(state=self.lagos, name="Ikeja")
        self.food_handler.lga = lga
        self.food_handler.save(update_fields=["lga", "updated_at"])
        self.uncertified_handler.lga = lga
        self.uncertified_handler.save(update_fields=["lga", "updated_at"])
        self.employer.lga = lga
        self.employer.save(update_fields=["lga", "updated_at"])
        self.facility.lga = lga
        self.facility.save(update_fields=["lga", "updated_at"])
        expiring_assessment = MedicalAssessment.objects.create(
            food_handler=self.uncertified_handler,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            declaration_status=StepStatus.REVIEWED,
            physical_exam_status=StepStatus.COMPLETED,
            lab_status=StepStatus.REVIEWED,
            vaccination_status=StepStatus.REVIEWED,
            final_decision=FitnessDecision.FIT,
            signed_at=timezone.now(),
            status="certificate_issued",
        )
        Certificate.objects.create(
            certificate_number="FCN-LA-EXP001",
            food_handler=self.uncertified_handler,
            assessment=expiring_assessment,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            issuing_state=self.lagos,
            issued_by_state_user=self.state_admin,
            issue_date=timezone.localdate() - timezone.timedelta(days=300),
            expiry_date=timezone.localdate() + timezone.timedelta(days=10),
            status=CertificateStatus.ACTIVE,
            verification_url="http://localhost:3000/verify/FCN-LA-EXP001",
            digital_signature_hash="hash-exp",
        )
        IllnessReport.objects.create(
            food_handler=self.uncertified_handler,
            employer=self.employer,
            reported_by=self.employer_user,
            symptoms={"fever": True},
            clearance_status="pending",
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
        )
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
        payload = data(response)
        self.assertEqual(payload["cards"]["registered_food_handlers"], 2)
        self.assertEqual(payload["cards"]["vaccination_coverage_rate"], 50.0)
        self.assertEqual(payload["cards"]["state_compliance_percentage"], 100.0)
        self.assertEqual(payload["cards"]["return_to_work_pending"], 1)
        self.assertEqual(payload["cards"]["certificates_expiring_soon"], 1)
        self.assertEqual(payload["cards"]["overall_compliance_status"], "compliant")
        self.assertIn("score", payload["cards"]["performance_rating"])
        self.assertEqual(payload["charts"]["lga_drill_down"][0]["lga_name"], "Ikeja")
        self.assertEqual(payload["charts"]["enforcement_notices_by_status"][0]["total"], 1)
        self.assertIn("illness_trends", payload["charts"])
        self.assertIn("assessment_volume_by_facility", payload["charts"])
        self.assertIn("revenue_trend", payload["charts"])

    def test_federal_dashboard_requires_federal_role(self):
        self.client.force_authenticate(self.employer_user)
        blocked = self.client.get("/api/dashboard/federal/")
        self.assertEqual(blocked.status_code, 403)

        self.client.force_authenticate(self.federal_admin)
        response = self.client.get("/api/dashboard/federal/")
        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertIn("national_certification_coverage", payload["cards"])
        self.assertEqual(payload["cards"]["states_with_active_implementation"], 2)
        self.assertEqual(payload["cards"]["states_with_overdue_reports"], 2)
        self.assertIn("national_vaccination_coverage", payload["cards"])
        self.assertIn("national_inspection_count", payload["cards"])
        self.assertIn("national_illness_reports", payload["cards"])
        self.assertIn("national_return_to_work_pending", payload["cards"])
        self.assertIn("overall_compliance_status", payload["cards"])
        self.assertIn("state_comparison_table", payload["charts"])
        self.assertIn("certification_coverage_by_state", payload["charts"])
        self.assertIn("facility_accreditation_by_state", payload["charts"])
        self.assertIn("vaccination_coverage_by_state", payload["charts"])
        self.assertIn("state_report_submission_status", payload["charts"])

    def test_analytics_endpoints_return_chart_payloads(self):
        OrganizationUnit.objects.create(
            organization=self.employer_org,
            name="Ikeja Branch",
            unit_type=OrganizationUnitType.BRANCH,
        )
        OrganizationUnit.objects.create(
            organization=self.employer_org,
            name="Operations Desk",
            unit_type=OrganizationUnitType.DEPARTMENT,
        )
        self.client.force_authenticate(self.state_admin)

        endpoints = [
            "/api/analytics/certificates/",
            "/api/analytics/assessments/",
            "/api/analytics/vaccinations/",
            "/api/analytics/facilities/",
            "/api/analytics/employers/",
            "/api/analytics/inspections/",
            "/api/analytics/enforcement/",
            "/api/analytics/illness/",
            "/api/analytics/data-quality/",
        ]

        for endpoint in endpoints:
            response = self.client.get(endpoint, {"state": str(self.oyo.id)})
            self.assertEqual(response.status_code, 200, endpoint)
            payload = data(response)
            self.assertIn("cards", payload, endpoint)
            self.assertIn("charts", payload, endpoint)

        certificate_payload = data(self.client.get("/api/analytics/certificates/", {"state": str(self.oyo.id)}))
        self.assertEqual(certificate_payload["cards"]["issued"], 1)
        self.assertIn("issuance_trend", certificate_payload["charts"])
        inspections_payload = data(self.client.get("/api/analytics/inspections/", {"date_to": timezone.localdate()}))
        self.assertEqual(inspections_payload["cards"]["inspections"], 1)
        employers_payload = data(self.client.get("/api/analytics/employers/"))
        self.assertEqual(employers_payload["charts"]["branch_by_state"][0]["total"], 1)

    def test_finance_analytics_require_finance_role(self):
        self.client.force_authenticate(self.employer_user)

        blocked = self.client.get("/api/analytics/payments/")

        self.assertEqual(blocked.status_code, 403)

        self.client.force_authenticate(self.federal_admin)
        payments = self.client.get("/api/analytics/payments/")
        settlements = self.client.get("/api/analytics/settlements/")

        self.assertEqual(payments.status_code, 200)
        self.assertEqual(settlements.status_code, 200)
        self.assertEqual(data(payments)["cards"]["successful"], 1)
        self.assertEqual(data(settlements)["cards"]["paid"], 1)

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
        self.assertEqual(report["title"], f"Employer Compliance - {timezone.localdate().isoformat()}")
        self.assertEqual(str(report["organization"]), str(self.employer_org.id))
        self.assertEqual(str(report["state"]), str(self.lagos.id))
        self.assertEqual(report["data_snapshot"], report["summary"])
        self.assertIn(GeneratedReportStatus.RETURNED_FOR_CORRECTION, GeneratedReportStatus.values)

    def test_state_report_can_be_submitted_to_federal(self):
        report = GeneratedReport.objects.create(
            title="Lagos Monthly Report",
            report_type=ReportType.STATE_MONTHLY,
            state=self.lagos,
            file_format="json",
            filters={},
            summary={"cards": {"registered_food_handlers": 2}},
            data_snapshot={"cards": {"registered_food_handlers": 2}},
            generated_by=self.state_admin,
            status=GeneratedReportStatus.GENERATED,
        )
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(f"/api/reports/generated/{report.id}/submit-to-federal/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(payload["status"], GeneratedReportStatus.SUBMITTED)
        self.assertTrue(payload["submitted_to_federal_at"])

    def test_federal_state_report_accept_return_and_escalate_workflow(self):
        submitted = GeneratedReport.objects.create(
            title="Submitted Lagos Report",
            report_type=ReportType.STATE_MONTHLY,
            state=self.lagos,
            file_format="json",
            filters={},
            summary={},
            data_snapshot={},
            generated_by=self.state_admin,
            status=GeneratedReportStatus.SUBMITTED,
            submitted_to_federal_at=timezone.now(),
        )
        returned = GeneratedReport.objects.create(
            title="Returned Candidate",
            report_type=ReportType.VACCINATION_COVERAGE,
            state=self.lagos,
            file_format="json",
            filters={},
            summary={},
            data_snapshot={},
            generated_by=self.state_admin,
            status=GeneratedReportStatus.SUBMITTED,
            submitted_to_federal_at=timezone.now(),
        )
        escalated = GeneratedReport.objects.create(
            title="Escalation Candidate",
            report_type=ReportType.ILLNESS_TRENDS,
            state=self.lagos,
            file_format="json",
            filters={},
            summary={},
            data_snapshot={},
            generated_by=self.state_admin,
            status=GeneratedReportStatus.SUBMITTED,
            submitted_to_federal_at=timezone.now(),
        )
        self.client.force_authenticate(self.federal_admin)

        list_response = self.client.get("/api/federal/state-reports/")
        accept_response = self.client.post(f"/api/federal/state-reports/{submitted.id}/accept/", {"comment": "Accepted."}, format="json")
        return_response = self.client.post(
            f"/api/federal/state-reports/{returned.id}/return-for-correction/",
            {"comment": "Please correct LGA totals."},
            format="json",
        )
        escalate_response = self.client.post(
            f"/api/federal/state-reports/{escalated.id}/escalate/",
            {"comment": "Overdue issue escalated."},
            format="json",
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertGreaterEqual(len(data(list_response)), 3)
        self.assertEqual(data(accept_response)["status"], GeneratedReportStatus.ACCEPTED)
        self.assertEqual(data(accept_response)["review_status"], GeneratedReportStatus.ACCEPTED)
        self.assertEqual(data(return_response)["status"], GeneratedReportStatus.RETURNED_FOR_CORRECTION)
        self.assertEqual(data(return_response)["review_comment"], "Please correct LGA totals.")
        self.assertEqual(data(escalate_response)["status"], GeneratedReportStatus.SUBMITTED)
        self.assertEqual(data(escalate_response)["review_status"], "escalated")

    def test_state_report_archive_and_regenerate_actions(self):
        report = GeneratedReport.objects.create(
            title="Regeneratable Lagos Report",
            report_type=ReportType.STATE_MONTHLY,
            state=self.lagos,
            file_format="json",
            filters={},
            summary={"old": True},
            data_snapshot={"old": True},
            generated_by=self.state_admin,
            status=GeneratedReportStatus.RETURNED_FOR_CORRECTION,
        )
        self.client.force_authenticate(self.state_admin)

        regenerate_response = self.client.post(f"/api/reports/generated/{report.id}/regenerate/")
        archive_response = self.client.post(f"/api/reports/generated/{report.id}/archive/")

        self.assertEqual(regenerate_response.status_code, 201)
        self.assertEqual(data(regenerate_response)["report_type"], ReportType.STATE_MONTHLY)
        self.assertEqual(data(regenerate_response)["status"], GeneratedReportStatus.GENERATED)
        self.assertEqual(archive_response.status_code, 200)
        self.assertEqual(data(archive_response)["status"], GeneratedReportStatus.ARCHIVED)

    def test_federal_state_reports_require_federal_role(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/federal/state-reports/")

        self.assertEqual(response.status_code, 403)

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

    def test_report_templates_are_role_scoped_and_active_only(self):
        ReportTemplate.objects.create(
            code="employer_compliance",
            name="Employer Compliance",
            module="reports",
            scope="employer",
            output_formats=["json", "csv"],
            privacy_level="employer_safe",
        )
        ReportTemplate.objects.create(
            code="state_monthly",
            name="State Monthly",
            module="reports",
            scope="state",
            output_formats=["json"],
            privacy_level="state_aggregate",
        )
        ReportTemplate.objects.create(
            code="inactive_employer",
            name="Inactive Employer",
            module="reports",
            scope="employer",
            output_formats=["json"],
            privacy_level="employer_safe",
            is_active=False,
        )
        self.client.force_authenticate(self.employer_user)

        response = self.client.get("/api/report-templates/")

        self.assertEqual(response.status_code, 200)
        codes = {item["code"] for item in data(response)}
        self.assertEqual(codes, {"employer_compliance"})

    def test_only_super_admin_can_manage_report_templates(self):
        super_admin = User.objects.create_user(
            "reports-super",
            "reports-super@example.com",
            "StrongPass123!",
            role=UserRole.SUPER_ADMIN,
        )
        payload = {
            "code": "custom_admin_report",
            "name": "Custom Admin Report",
            "module": "reports",
            "scope": "admin",
            "output_formats": ["json"],
            "default_filters": {},
            "required_permissions": ["admin"],
            "privacy_level": "platform_sensitive",
            "is_active": True,
        }
        self.client.force_authenticate(self.employer_user)
        blocked = self.client.post("/api/report-templates/", payload, format="json")

        self.client.force_authenticate(super_admin)
        created = self.client.post("/api/report-templates/", payload, format="json")

        self.assertEqual(blocked.status_code, 403)
        self.assertEqual(created.status_code, 201)
        self.assertEqual(data(created)["created_by"], super_admin.id)

    def test_seed_me_indicators_creates_prd_categories(self):
        call_command("seed_me_indicators")

        self.assertGreaterEqual(MEIndicator.objects.count(), 60)
        self.assertEqual(MEIndicator.objects.values("category").distinct().count(), 10)
        category_counts = {
            row["category"]: row["total"]
            for row in MEIndicator.objects.values("category").annotate(total=Count("id"))
        }
        self.assertTrue(all(total >= 5 for total in category_counts.values()))
        self.assertGreaterEqual(category_counts["certification"], 8)
        self.assertGreaterEqual(category_counts["medical_assessment"], 7)
        self.assertGreaterEqual(category_counts["inspection_enforcement"], 7)
        self.assertTrue(MEIndicator.objects.filter(code="certification_coverage_rate", category="certification").exists())
        self.assertTrue(MEIndicator.objects.filter(code="assessment_revenue", category="finance").exists())
        self.assertTrue(MEIndicator.objects.filter(code="overdue_state_reports", category="data_quality").exists())

    def test_me_indicator_value_supports_state_lga_org_disaggregation(self):
        indicator = MEIndicator.objects.create(
            code="test_coverage_rate",
            name="Test coverage rate",
            category="registration_coverage",
            formula="numerator / denominator * 100",
            data_sources=["tests"],
            reporting_frequency="monthly",
            disaggregation_fields=["state", "lga", "organization"],
            visualization_type="trend_card",
        )
        lga = LGA.objects.create(state=self.lagos, name="Ikeja")

        value = MEIndicatorValue.objects.create(
            indicator=indicator,
            state=self.lagos,
            lga=lga,
            organization=self.employer_org,
            period_start=timezone.localdate().replace(day=1),
            period_end=timezone.localdate(),
            numerator_value=Decimal("75.0000"),
            denominator_value=Decimal("100.0000"),
            calculated_value=Decimal("75.0000"),
            disaggregation={"establishment_category": "restaurant_cafe"},
        )

        self.assertEqual(value.state, self.lagos)
        self.assertEqual(value.lga, lga)
        self.assertEqual(value.organization, self.employer_org)
        self.assertEqual(value.calculated_value, Decimal("75.0000"))

    def test_me_indicator_service_calculates_and_stores_indicator_value(self):
        indicator = MEIndicator.objects.create(
            code="calc_certification_coverage_rate",
            name="Calculated certification coverage",
            category="certification",
            formula="active_certified_handlers / registered_food_handlers * 100",
            data_sources=["certificates", "food_handlers"],
            reporting_frequency="monthly",
            disaggregation_fields=["state"],
            visualization_type="trend_card",
        )

        value = MEIndicatorService.calculate_indicator(indicator, state=self.lagos)

        self.assertEqual(value.state, self.lagos)
        self.assertEqual(value.numerator_value, Decimal("1"))
        self.assertEqual(value.denominator_value, Decimal("2"))
        self.assertEqual(value.calculated_value, Decimal("50.0000"))

    def test_me_calculate_endpoint_calculates_indicator_for_state(self):
        indicator = MEIndicator.objects.create(
            code="endpoint_certification_coverage_rate",
            name="Endpoint certification coverage",
            category="certification",
            formula="active_certified_handlers / registered_food_handlers * 100",
            data_sources=["certificates", "food_handlers"],
            reporting_frequency="monthly",
            disaggregation_fields=["state"],
            visualization_type="trend_card",
        )
        self.client.force_authenticate(self.federal_admin)

        response = self.client.post(
            "/api/m-and-e/calculate/",
            {"indicator": str(indicator.id), "state": str(self.lagos.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        payload = data(response)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["indicator_code"], "endpoint_certification_coverage_rate")
        self.assertEqual(payload[0]["calculated_value"], "50.0000")

    def test_me_indicator_api_is_active_scoped_and_super_admin_managed(self):
        inactive = MEIndicator.objects.create(
            code="inactive_me_indicator",
            name="Inactive M&E indicator",
            category="data_quality",
            formula="count(food_handlers)",
            data_sources=["food_handlers"],
            reporting_frequency="weekly",
            disaggregation_fields=["state"],
            visualization_type="kpi_card",
            is_active=False,
        )
        active = MEIndicator.objects.create(
            code="active_me_indicator",
            name="Active M&E indicator",
            category="data_quality",
            formula="count(food_handlers)",
            data_sources=["food_handlers"],
            reporting_frequency="weekly",
            disaggregation_fields=["state"],
            visualization_type="kpi_card",
        )
        self.client.force_authenticate(self.state_admin)
        list_response = self.client.get("/api/m-and-e/indicators/")
        blocked_create = self.client.post(
            "/api/m-and-e/indicators/",
            {
                "code": "state_created_indicator",
                "name": "State Created Indicator",
                "category": "data_quality",
                "formula": "count(food_handlers)",
                "data_sources": ["food_handlers"],
                "reporting_frequency": "weekly",
                "disaggregation_fields": ["state"],
                "visualization_type": "kpi_card",
            },
            format="json",
        )
        self.client.force_authenticate(self.super_admin)
        created = self.client.post(
            "/api/m-and-e/indicators/",
            {
                "code": "super_created_indicator",
                "name": "Super Created Indicator",
                "category": "data_quality",
                "formula": "count(food_handlers)",
                "data_sources": ["food_handlers"],
                "reporting_frequency": "weekly",
                "disaggregation_fields": ["state"],
                "visualization_type": "kpi_card",
            },
            format="json",
        )

        codes = {item["code"] for item in data(list_response)}
        self.assertIn(active.code, codes)
        self.assertNotIn(inactive.code, codes)
        self.assertEqual(blocked_create.status_code, 403)
        self.assertEqual(created.status_code, 201)

    def test_me_state_and_national_summary_endpoints(self):
        self.client.force_authenticate(self.state_admin)
        state_response = self.client.get("/api/m-and-e/state-performance/")
        blocked_national = self.client.get("/api/m-and-e/national-summary/")

        self.client.force_authenticate(self.federal_admin)
        national_response = self.client.get("/api/m-and-e/national-summary/")
        dashboard_response = self.client.get("/api/m-and-e/dashboard/")

        self.assertEqual(state_response.status_code, 200)
        self.assertEqual(data(state_response)["state"]["id"], str(self.lagos.id))
        self.assertEqual(blocked_national.status_code, 403)
        self.assertEqual(national_response.status_code, 200)
        self.assertIn("totals", data(national_response))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertIn("states", data(dashboard_response))

    def test_me_calculation_task_runs_daily_and_creates_threshold_alerts(self):
        MEIndicator.objects.create(
            code="daily_certification_coverage_rate",
            name="Daily certification coverage",
            category="certification",
            formula="active_certified_handlers / registered_food_handlers * 100",
            data_sources=["certificates", "food_handlers"],
            reporting_frequency="daily",
            disaggregation_fields=["state"],
            warning_threshold=Decimal("80.00"),
            critical_threshold=Decimal("40.00"),
            visualization_type="trend_card",
        )

        result = run_me_indicator_calculations.run(run_date=timezone.localdate().isoformat())

        self.assertEqual(result["indicators"], 1)
        self.assertEqual(result["values"], 3)
        self.assertEqual(result["alerts"], 3)
        self.assertEqual(MEIndicatorValue.objects.filter(indicator__code="daily_certification_coverage_rate").count(), 3)
        self.assertTrue(DataQualityIssue.objects.filter(issue_type="me_threshold_breach", metadata__indicator_code="daily_certification_coverage_rate").exists())

    def test_me_calculation_task_includes_monthly_indicators_on_first_day(self):
        MEIndicator.objects.create(
            code="monthly_registered_food_handlers",
            name="Monthly registered food handlers",
            category="registration_coverage",
            formula="registered_food_handlers",
            data_sources=["food_handlers"],
            reporting_frequency="monthly",
            disaggregation_fields=["state"],
            visualization_type="kpi_card",
        )

        result = run_me_indicator_calculations.run(run_date="2026-06-01")

        self.assertEqual(result["period_start"], "2026-05-01")
        self.assertEqual(result["period_end"], "2026-05-31")
        self.assertEqual(result["indicators"], 1)
        self.assertEqual(MEIndicatorValue.objects.filter(indicator__code="monthly_registered_food_handlers").count(), 3)

    def unsafe_report_payload(self):
        return {
            "full_name": "Ada Okafor",
            "email": "ada@example.com",
            "phone": "08030000003",
            "nin": "12345678901",
            "masked_nin": "*******8901",
            "certificate_status": "active",
            "doctor_notes": "Private diagnosis note",
            "diagnosis": "Sensitive diagnosis",
            "declaration_answers": {"fever": True},
            "lab_results": [{"result_notes": "No pathogens detected", "lab_staff_notes": "Internal note"}],
            "treatment_notes": "Sensitive treatment",
            "payment": {
                "amount": "15000.00",
                "provider_reference": "PAY-SECRET",
                "encrypted_secret_key": "secret",
                "bank_details": {"account_number": "0011223344"},
            },
            "rows": [
                {
                    "full_name": "Nested Person",
                    "nin": "99999999999",
                    "doctor_notes": "Nested clinical note",
                    "state": "Lagos",
                }
            ],
        }

    def assert_no_keys_recursive(self, value, forbidden):
        if isinstance(value, dict):
            for key, item in value.items():
                self.assertNotIn(str(key).lower(), forbidden)
                self.assert_no_keys_recursive(item, forbidden)
        elif isinstance(value, list):
            for item in value:
                self.assert_no_keys_recursive(item, forbidden)

    def test_privacy_safe_serializers_block_sensitive_fields(self):
        forbidden = {
            "nin",
            "full_nin",
            "doctor_notes",
            "diagnosis",
            "declaration_answers",
            "lab_results",
            "result_notes",
            "lab_staff_notes",
            "treatment_notes",
            "encrypted_secret_key",
            "webhook_secret",
            "bank_details",
            "account_number",
        }
        serializers = [
            FoodHandlerReportSerializer,
            EmployerSafeComplianceSerializer,
            InspectorSafeReportSerializer,
            StateRegulatoryReportSerializer,
            FederalAggregateReportSerializer,
            FinanceReportSerializer,
            AdminReportSerializer,
        ]

        for serializer_class in serializers:
            payload = serializer_class().to_representation(self.unsafe_report_payload())
            self.assert_no_keys_recursive(payload, forbidden)

    def test_facility_and_medical_restricted_serializers_keep_clinical_but_strip_identity_and_secrets(self):
        facility_payload = FacilityOperationalSerializer().to_representation(self.unsafe_report_payload())
        medical_payload = MedicalRestrictedSerializer().to_representation(self.unsafe_report_payload())

        for payload in (facility_payload, medical_payload):
            self.assertIn("doctor_notes", payload)
            self.assertIn("lab_results", payload)
            self.assertNotIn("nin", payload)
            self.assertNotIn("encrypted_secret_key", str(payload))
            self.assertNotIn("bank_details", str(payload))

    def test_federal_and_admin_serializers_are_aggregate_safe(self):
        federal_payload = FederalAggregateReportSerializer().to_representation(self.unsafe_report_payload())
        admin_payload = AdminReportSerializer().to_representation(self.unsafe_report_payload())

        self.assertNotIn("full_name", federal_payload)
        self.assertNotIn("email", federal_payload)
        self.assertNotIn("phone", federal_payload)
        self.assertNotIn("full_name", admin_payload)
        self.assertNotIn("amount", str(admin_payload))
        self.assertIn("certificate_status", admin_payload)

    def test_seed_dashboard_widgets_creates_widgets_for_all_dashboard_scopes(self):
        call_command("seed_dashboard_widgets")

        expected_scopes = {"food_handler", "employer", "facility", "doctor", "lab", "inspector", "state", "federal", "admin"}
        actual_scopes = set(DashboardWidget.objects.values_list("dashboard_scope", flat=True).distinct())

        self.assertTrue(expected_scopes.issubset(actual_scopes))
        self.assertGreaterEqual(DashboardWidget.objects.count(), 30)
        self.assertTrue(DashboardWidget.objects.filter(code="state_certification_coverage_rate", widget_type="trend_card").exists())
        self.assertTrue(DashboardWidget.objects.filter(code="federal_state_comparison_table", configuration__privacy="aggregate").exists())

    def test_dashboard_widget_ordering_and_configuration(self):
        second = DashboardWidget.objects.create(
            code="test_second_widget",
            name="Second widget",
            dashboard_scope="state",
            widget_type="table",
            metric_code="second_metric",
            configuration={"limit": 10},
            required_permissions=["state"],
            sort_order=20,
        )
        first = DashboardWidget.objects.create(
            code="test_first_widget",
            name="First widget",
            dashboard_scope="state",
            widget_type="kpi_card",
            metric_code="first_metric",
            configuration={"format": "percentage"},
            required_permissions=["state"],
            sort_order=10,
        )

        widgets = list(DashboardWidget.objects.filter(dashboard_scope="state"))

        self.assertEqual(widgets, [first, second])
        self.assertEqual(widgets[0].configuration["format"], "percentage")
        self.assertEqual(widgets[1].configuration["limit"], 10)

    def test_data_quality_issue_tracks_scope_target_and_metadata(self):
        issue = DataQualityIssue.objects.create(
            issue_type="duplicate_nin",
            severity=DataQualityIssueSeverity.HIGH,
            module="food_handlers",
            target_type="food_handler",
            target_id=self.food_handler.id,
            state=self.lagos,
            organization=self.employer_org,
            description="Possible duplicate NIN detected for this food handler.",
            metadata={"matched_profile_ids": [str(self.uncertified_handler.id)], "source": "nightly_scan"},
        )

        self.assertEqual(issue.status, DataQualityIssueStatus.OPEN)
        self.assertEqual(issue.target_id, self.food_handler.id)
        self.assertEqual(issue.state, self.lagos)
        self.assertEqual(issue.organization, self.employer_org)
        self.assertEqual(issue.metadata["source"], "nightly_scan")

    def test_data_quality_issue_assignment_and_resolution_fields(self):
        issue = DataQualityIssue.objects.create(
            issue_type="missing_certificate_expiry",
            severity=DataQualityIssueSeverity.MEDIUM,
            module="certificates",
            target_type="certificate",
            target_id=self.certificate.id,
            state=self.lagos,
            organization=self.employer_org,
            description="Certificate expiry date needs confirmation.",
            status=DataQualityIssueStatus.ASSIGNED,
            assigned_to=self.state_admin,
        )

        issue.status = DataQualityIssueStatus.RESOLVED
        issue.resolved_by = self.state_admin
        issue.resolved_at = timezone.now()
        issue.metadata = {"resolution": "expiry_confirmed"}
        issue.save(update_fields=["status", "resolved_by", "resolved_at", "metadata", "updated_at"])
        issue.refresh_from_db()

        self.assertEqual(issue.assigned_to, self.state_admin)
        self.assertEqual(issue.status, DataQualityIssueStatus.RESOLVED)
        self.assertEqual(issue.resolved_by, self.state_admin)
        self.assertIsNotNone(issue.resolved_at)
        self.assertEqual(issue.metadata["resolution"], "expiry_confirmed")

    def test_scheduled_report_links_template_owner_delivery_and_next_run(self):
        template = ReportTemplate.objects.create(
            code="scheduled_state_monthly",
            name="Scheduled State Monthly",
            module="reports",
            scope="state",
            output_formats=["json", "csv", "pdf"],
            privacy_level="state_aggregate",
        )
        next_run_at = timezone.now() + timezone.timedelta(days=1)

        schedule = ScheduledReport.objects.create(
            report_template=template,
            owner=self.state_admin,
            name="Lagos monthly compliance pack",
            schedule_frequency=ScheduledReportFrequency.MONTHLY,
            filters={"state": str(self.lagos.id), "include_lgas": True},
            output_format="pdf",
            delivery_channels=["email", "in_app"],
            recipients=["state-reports@example.com"],
            next_run_at=next_run_at,
        )

        self.assertEqual(schedule.report_template, template)
        self.assertEqual(schedule.owner, self.state_admin)
        self.assertTrue(schedule.is_active)
        self.assertEqual(schedule.filters["state"], str(self.lagos.id))
        self.assertEqual(schedule.delivery_channels, ["email", "in_app"])
        self.assertEqual(schedule.recipients, ["state-reports@example.com"])
        self.assertEqual(schedule.next_run_at, next_run_at)

    def test_scheduled_report_can_be_deactivated_without_legacy_schedule(self):
        template = ReportTemplate.objects.create(
            code="scheduled_employer_compliance",
            name="Scheduled Employer Compliance",
            module="reports",
            scope="employer",
            output_formats=["json", "csv"],
            privacy_level="employer_safe",
        )
        legacy_schedule = ReportSchedule.objects.create(
            report_type="employer_compliance",
            frequency="monthly",
            filters={"legacy": True},
            recipients=["legacy@example.com"],
            created_by=self.employer_user,
        )
        schedule = ScheduledReport.objects.create(
            report_template=template,
            owner=self.employer_user,
            name="Employer CSV compliance",
            schedule_frequency=ScheduledReportFrequency.WEEKLY,
            output_format="csv",
            delivery_channels=["download_link"],
            recipients=[],
        )

        schedule.is_active = False
        schedule.save(update_fields=["is_active", "updated_at"])
        legacy_schedule.refresh_from_db()
        schedule.refresh_from_db()

        self.assertFalse(schedule.is_active)
        self.assertEqual(legacy_schedule.status, "active")
        self.assertEqual(ReportSchedule.objects.count(), 1)
