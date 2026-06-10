from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.assessments.models import FitnessDecision, MedicalAssessment
from apps.certificates.models import Certificate, CertificateRequest, SuspiciousCertificateReport
from apps.certificates.services import CertificateService
from apps.employers.models import Employer, EstablishmentCategory
from apps.facilities.models import AccreditationStatus, FacilityType, MedicalFacility, OwnershipType
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, FoodHandlerStatus, Gender
from apps.illness.models import ClearanceStatus, IllnessReport, SuspectedCondition
from apps.inspections.models import (
    ChecklistCategory,
    ChecklistSeverity,
    EnforcementAction,
    FindingType,
    Inspection,
    InspectionChecklistItem,
    InspectionFinding,
    InspectionResponse,
    InspectionResponseType,
    InspectionStatus,
)
from apps.locations.models import State
from apps.nin_verification.models import NINVerification, NINVerificationStatus
from apps.notifications.models import Notification, NotificationCategory
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
        self.assertTrue(Notification.objects.filter(recipient=self.employer_user, category=NotificationCategory.ENFORCEMENT).exists())

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

    def test_inspector_can_verify_save_and_flag_certificate(self):
        certificate = self._certificate()
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer)
        self.client.force_authenticate(self.inspector)

        verify_response = self.client.post(
            "/api/inspector/certificates/verify-by-number/",
            {"certificate_number": certificate.certificate_number},
            format="json",
        )
        self.assertEqual(verify_response.status_code, 200)
        self.assertEqual(data(verify_response)["certificate_validity"], "valid")
        self.assertNotIn("doctor_notes", str(data(verify_response)))
        self.assertNotIn("lab_tests", str(data(verify_response)))

        save_response = self.client.post(
            f"/api/inspector/certificates/{certificate.id}/save-to-inspection/",
            {"inspection": str(inspection.id)},
            format="json",
        )
        self.assertEqual(save_response.status_code, 201)
        self.assertEqual(data(save_response)["result"], "valid")

        flag_response = self.client.post(
            f"/api/inspector/certificates/{certificate.id}/flag/",
            {"reason": "Photo mismatch", "details": "Handler photo does not match."},
            format="json",
        )
        self.assertEqual(flag_response.status_code, 201)
        self.assertEqual(SuspiciousCertificateReport.objects.count(), 1)

    def test_inspector_food_handler_roster_exposes_operational_rtw_flags(self):
        branch = OrganizationUnit.objects.create(
            organization=self.employer_org,
            name="Ikeja Branch",
            unit_type=OrganizationUnitType.BRANCH,
        )
        certificate = self._certificate()
        self.food_handler.business_branch = branch
        self.food_handler.current_status = FoodHandlerStatus.TEMPORARILY_EXCLUDED
        self.food_handler.save(update_fields=["business_branch", "current_status", "updated_at"])
        IllnessReport.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            reported_by=self.employer_user,
            suspected_condition=SuspectedCondition.GENERAL_DIARRHOEA_VOMITING,
            exclusion_start_date=timezone.localdate(),
            earliest_return_date=timezone.localdate() + timezone.timedelta(days=2),
            clearance_status=ClearanceStatus.CLEARANCE_REQUIRED,
        )
        self.food_handler.current_status = FoodHandlerStatus.TEMPORARILY_EXCLUDED
        self.food_handler.save(update_fields=["current_status", "updated_at"])
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer, branch=branch)
        self.client.force_authenticate(self.inspector)

        roster_response = self.client.get(f"/api/inspections/{inspection.id}/food-handlers/")
        self.assertEqual(roster_response.status_code, 200)
        payload = data(roster_response)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["id"], str(self.food_handler.id))
        self.assertEqual(payload[0]["certificate_number"], certificate.certificate_number)
        self.assertEqual(payload[0]["fitness_status"], FoodHandlerStatus.TEMPORARILY_EXCLUDED)
        self.assertEqual(payload[0]["active_illness_status"], "excluded")
        self.assertEqual(payload[0]["return_to_work_status"], ClearanceStatus.CLEARANCE_REQUIRED)
        self.assertNotIn("symptoms", payload[0])
        self.assertNotIn("notes", payload[0])

        finding_response = self.client.post(
            f"/api/inspections/{inspection.id}/findings/",
            {
                "category": ChecklistCategory.FITNESS_EXCLUSION,
                "finding_type": FindingType.CRITICAL_NON_COMPLIANCE,
                "severity": ChecklistSeverity.CRITICAL,
                "description": "Excluded food handler found handling food.",
                "recommended_action": "Immediate removal from food handling duties, compliance notice, follow-up inspection, and State escalation if repeated or serious.",
                "food_handler": str(self.food_handler.id),
                "certificate": str(certificate.id),
            },
            format="json",
        )
        self.assertEqual(finding_response.status_code, 201)
        self.assertTrue(
            InspectionFinding.objects.filter(
                inspection=inspection,
                food_handler=self.food_handler,
                severity=ChecklistSeverity.CRITICAL,
            ).exists()
        )

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

    def test_inspector_lifecycle_accept_start_submit(self):
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer, status=InspectionStatus.ASSIGNED)
        self.client.force_authenticate(self.inspector)

        accept_resp = self.client.post(f"/api/inspections/{inspection.id}/accept/")
        self.assertEqual(accept_resp.status_code, 200)
        self.assertEqual(data(accept_resp)["status"], InspectionStatus.ACCEPTED)

        start_resp = self.client.post(f"/api/inspections/{inspection.id}/start/")
        self.assertEqual(start_resp.status_code, 200)
        self.assertEqual(data(start_resp)["status"], InspectionStatus.IN_PROGRESS)

        inspection.checklist_responses = {"item_a": True}
        inspection.save()
        submit_resp = self.client.patch(f"/api/inspections/{inspection.id}/submit/")
        self.assertEqual(submit_resp.status_code, 200)
        self.assertEqual(data(submit_resp)["status"], InspectionStatus.SUBMITTED)

    def test_reschedule_request_from_assigned(self):
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer, status=InspectionStatus.ASSIGNED)
        self.client.force_authenticate(self.inspector)
        resp = self.client.post(f"/api/inspections/{inspection.id}/reschedule-request/", {"reason": "Scheduling conflict"}, format="json")
        self.assertEqual(resp.status_code, 200)
        inspection.refresh_from_db()
        self.assertEqual(inspection.status, InspectionStatus.ASSIGNED)

    def test_reschedule_request_from_accepted(self):
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer, status=InspectionStatus.ACCEPTED)
        self.client.force_authenticate(self.inspector)
        resp = self.client.post(f"/api/inspections/{inspection.id}/reschedule-request/", {"reason": "Need to reschedule"}, format="json")
        self.assertEqual(resp.status_code, 200)
        inspection.refresh_from_db()
        self.assertEqual(inspection.status, InspectionStatus.ASSIGNED)

    def test_cancel_inspection(self):
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer, status=InspectionStatus.ASSIGNED)
        self.client.force_authenticate(self.state_admin)
        resp = self.client.post(f"/api/inspections/{inspection.id}/cancel/", {"reason": "No longer needed"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data(resp)["status"], InspectionStatus.CANCELLED)

    def test_return_for_correction(self):
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer, status=InspectionStatus.SUBMITTED)
        self.client.force_authenticate(self.state_admin)
        resp = self.client.post(f"/api/inspections/{inspection.id}/return-for-correction/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data(resp)["status"], InspectionStatus.RETURNED_FOR_CORRECTION)

    def test_checklist_responses_upsert(self):
        item = InspectionChecklistItem.objects.create(
            category=ChecklistCategory.HYGIENE,
            question="Are handwashing stations available?",
            severity_if_failed=ChecklistSeverity.MINOR,
            sort_order=1,
        )
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer)
        self.client.force_authenticate(self.inspector)

        resp = self.client.post(
            f"/api/inspections/{inspection.id}/checklist-responses/",
            {"checklist_item": str(item.id), "response": "yes", "note": "All good"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(data(resp)["response"], "yes")

        list_resp = self.client.get(f"/api/inspections/{inspection.id}/checklist-responses/")
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(len(data(list_resp)), 1)

    def test_findings_create_and_list(self):
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer)
        self.client.force_authenticate(self.inspector)

        resp = self.client.post(
            f"/api/inspections/{inspection.id}/findings/",
            {"category": "hygiene", "finding_type": "minor_non_compliance", "severity": "minor", "description": "Missing soap"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(data(resp)["category"], "hygiene")

        list_resp = self.client.get(f"/api/inspections/{inspection.id}/findings/")
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(len(data(list_resp)), 1)

    def test_evidence_upload_list_delete(self):
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer)
        self.client.force_authenticate(self.inspector)

        upload = self.client.post(
            f"/api/inspections/{inspection.id}/evidence-upload/",
            {"evidence_type": "photo", "file_url": "https://img.example.com/1.jpg", "caption": "Kitchen photo"},
            format="json",
        )
        self.assertEqual(upload.status_code, 201)
        ev_id = data(upload)["id"]

        list_resp = self.client.get(f"/api/inspections/{inspection.id}/evidence-entries/")
        self.assertEqual(len(data(list_resp)), 1)

        del_resp = self.client.delete(f"/api/inspections/{inspection.id}/evidence-entries/{ev_id}/")
        self.assertEqual(del_resp.status_code, 204)

    def test_employer_context_and_compliance_summary(self):
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer, status=InspectionStatus.IN_PROGRESS)
        self.client.force_authenticate(self.inspector)

        ctx_resp = self.client.get(f"/api/inspections/{inspection.id}/employer-context/")
        self.assertEqual(ctx_resp.status_code, 200)
        self.assertEqual(data(ctx_resp)["employer"]["name"], "Clean Foods")

        summary_resp = self.client.get(f"/api/inspections/{inspection.id}/compliance-summary/")
        self.assertEqual(summary_resp.status_code, 200)
        self.assertIn("total_food_handlers", data(summary_resp))

    def test_food_handlers_list_for_inspection(self):
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer, status=InspectionStatus.IN_PROGRESS)
        self.client.force_authenticate(self.inspector)

        resp = self.client.get(f"/api/inspections/{inspection.id}/food-handlers/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(data(resp), list)

    def test_enforcement_notice_create_and_workflow(self):
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer, status=InspectionStatus.SUBMITTED)
        self.client.force_authenticate(self.state_admin)

        create = self.client.post(
            "/api/enforcement-notices/",
            {
                "inspection": str(inspection.id),
                "employer": str(self.employer.id),
                "notice_type": "compliance",
                "description": "Compliance required for hygiene standards.",
                "required_corrective_actions": "Fix handwashing station within 7 days.",
                "deadline": str(timezone.now().date() + timezone.timedelta(days=7)),
            },
            format="json",
        )
        self.assertEqual(create.status_code, 201)
        notice_id = data(create)["id"]
        self.assertEqual(data(create)["status"], "draft")

        submit = self.client.post(f"/api/enforcement-notices/{notice_id}/submit-for-approval/")
        self.assertEqual(submit.status_code, 200)
        self.assertEqual(data(submit)["status"], "pending_approval")

        approve = self.client.post(f"/api/enforcement-notices/{notice_id}/approve/")
        self.assertEqual(approve.status_code, 200)
        self.assertEqual(data(approve)["status"], "issued")

        self.client.force_authenticate(self.employer_user)
        ack = self.client.post(f"/api/enforcement-notices/{notice_id}/acknowledge/")
        self.assertEqual(ack.status_code, 200)

    def test_corrective_action_submission_and_review(self):
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer, status=InspectionStatus.SUBMITTED)
        self.client.force_authenticate(self.state_admin)
        create = self.client.post(
            "/api/enforcement-notices/",
            {
                "inspection": str(inspection.id),
                "employer": str(self.employer.id),
                "notice_type": "compliance",
                "description": "Fix issues.",
                "required_corrective_actions": "Install handwashing station.",
                "deadline": str(timezone.now().date() + timezone.timedelta(days=7)),
            },
            format="json",
        )
        notice_id = data(create)["id"]
        self.client.post(f"/api/enforcement-notices/{notice_id}/submit-for-approval/")
        self.client.post(f"/api/enforcement-notices/{notice_id}/approve/")

        self.client.force_authenticate(self.employer_user)
        action = self.client.post(
            f"/api/enforcement-notices/{notice_id}/corrective-actions/",
            {"response_note": "We have fixed the issue.", "action_taken": "Installed new handwashing station."},
            format="json",
        )
        self.assertEqual(action.status_code, 201)
        resp_id = data(action)["id"]

        self.client.force_authenticate(self.state_admin)
        review = self.client.post(
            f"/api/enforcement-notices/{notice_id}/corrective-actions/{resp_id}/review/",
            {"action": "accept", "review_note": "Verified compliance."},
            format="json",
        )
        self.assertEqual(review.status_code, 200)
        self.assertEqual(data(review)["status"], "accepted")

    def test_enforcement_case_create_escalate_close(self):
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer, status=InspectionStatus.SUBMITTED)
        self.client.force_authenticate(self.state_admin)

        create = self.client.post(
            "/api/enforcement-cases/",
            {"employer": str(self.employer.id), "state": str(self.state.id), "severity": "high", "summary": "Repeated violations."},
            format="json",
        )
        self.assertEqual(create.status_code, 201)
        case_id = data(create)["id"]

        escalation = self.client.post(f"/api/enforcement-cases/{case_id}/escalate/", {"reason": "Critical risk"}, format="json")
        self.assertEqual(escalation.status_code, 200)
        self.assertEqual(data(escalation)["status"], "escalated")

        close = self.client.post(f"/api/enforcement-cases/{case_id}/close/", {"closure_note": "Resolved"}, format="json")
        self.assertEqual(close.status_code, 200)
        self.assertEqual(data(close)["status"], "closed")

    def test_escalate_inspection_to_case(self):
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer, status=InspectionStatus.UNDER_REVIEW)
        self.client.force_authenticate(self.state_admin)

        resp = self.client.post(f"/api/inspections/{inspection.id}/escalate/", {"severity": "critical", "summary": "Critical hygiene violation."}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertIn("case_reference", data(resp))

    def test_create_follow_up(self):
        inspection = Inspection.objects.create(inspector=self.inspector, employer=self.employer, status=InspectionStatus.FOLLOW_UP_REQUIRED, findings="Unresolved violations")
        self.client.force_authenticate(self.state_admin)

        resp = self.client.post(f"/api/inspections/{inspection.id}/create-follow-up/", {"reason": "Re-check compliance"}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(data(resp)["inspection_type"], "follow_up")

    def test_inspector_dashboard_access(self):
        self.client.force_authenticate(self.inspector)
        resp = self.client.get("/api/inspector/dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("cards", data(resp))

    def test_inspector_tasks_with_filters(self):
        Inspection.objects.create(inspector=self.inspector, employer=self.employer, status=InspectionStatus.ASSIGNED)
        self.client.force_authenticate(self.inspector)
        resp = self.client.get("/api/inspector/tasks/?status=assigned")
        self.assertEqual(resp.status_code, 200)

    def test_state_enforcement_dashboard(self):
        self.client.force_authenticate(self.state_admin)
        resp = self.client.get("/api/state/enforcement/dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("cards", data(resp))
        self.assertIn("charts", data(resp))

    def test_federal_enforcement_dashboard(self):
        User.objects.create_user("federal", "fed@example.com", "StrongPass123!", role=UserRole.FEDERAL_ADMIN, state=self.state)
        self.client.force_authenticate(User.objects.get(email="fed@example.com"))
        resp = self.client.get("/api/federal/enforcement/dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("cards", data(resp))

    def test_unauthorized_roles_are_denied(self):
        self.client.force_authenticate(self.handler_user)

        resp = self.client.post("/api/inspections/", {"employer": str(self.employer.id)}, format="json")
        self.assertEqual(resp.status_code, 403)

        resp = self.client.get("/api/inspector/dashboard/")
        self.assertEqual(resp.status_code, 403)

    def test_checklist_items_endpoint(self):
        self.client.force_authenticate(self.state_admin)
        resp = self.client.get("/api/inspection-checklist-items/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(data(resp), list)
