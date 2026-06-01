from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.assessments.models import AssessmentStatus, FitnessDecision, MedicalAssessment
from apps.audit.models import AuditLog
from apps.certificates.models import Certificate, CertificateRequest, CertificateRequestStatus, CertificateStatus, CertificateTemplate, CertificateTemplateScope, SuspiciousCertificateReport, VerificationResult
from apps.certificates.services import CertificateLifecycleJobService, CertificateService
from apps.employers.models import Employer, EstablishmentCategory
from apps.facilities.models import AccreditationStatus, FacilityType, MedicalFacility, OwnershipType
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, Gender
from apps.illness.models import ClearanceStatus, IllnessReport
from apps.inspections.models import Inspection, InspectionCertificateScan
from apps.locations.models import State
from apps.nin_verification.models import NINVerification, NINVerificationStatus
from apps.notifications.models import Notification, NotificationCategory
from apps.organizations.models import Organization, OrganizationType
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.policy.models import NationalPolicyConfig, StatePolicyConfig
from apps.reports.models import GeneratedReport, GeneratedReportStatus, ReportFormat, ReportType

User = get_user_model()


def data(response):
    return response.data.get("data", response.data)


def media_path(url):
    return settings.MEDIA_ROOT / url.replace("http://localhost:8000/media/", "")


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

    def _approve_through_state_queue(self):
        self.client.force_authenticate(self.facility_admin)
        submit_response = self.client.post(
            f"/api/assessments/{self.assessment.id}/submit-to-state/",
            {"request_notes": "Ready for State validation."},
            format="json",
        )
        self.assertEqual(submit_response.status_code, 201)
        request_id = data(submit_response)["id"]

        self.client.force_authenticate(self.state_admin)
        approve_response = self.client.patch(
            f"/api/state/certificate-validation-queue/{request_id}/approve/",
            {"review_notes": "Approved by State."},
            format="json",
        )
        self.assertEqual(approve_response.status_code, 200)
        certificate = Certificate.objects.get(id=data(approve_response)["certificate_id"])
        return certificate

    def test_end_to_end_state_approval_generates_publicly_valid_certificate(self):
        certificate = self._approve_through_state_queue()
        self.client.force_authenticate(user=None)

        verify_response = self.client.get(f"/api/public/certificates/verify/{certificate.verification_token}/")

        self.assertEqual(verify_response.status_code, 200)
        self.assertEqual(data(verify_response)["certificate_validity"], VerificationResult.VALID)
        self.assertEqual(data(verify_response)["certificate_number"], certificate.certificate_number)

    def test_end_to_end_expired_suspended_reinstated_and_revoked_verification_states(self):
        certificate = self._approve_through_state_queue()

        certificate.expiry_date = timezone.localdate() - timezone.timedelta(days=1)
        certificate.digital_signature_hash = CertificateService.signature_hash(
            certificate_number=certificate.certificate_number,
            assessment_id=certificate.assessment_id,
            food_handler_id=certificate.food_handler_id,
            issue_date=certificate.issue_date,
            expiry_date=certificate.expiry_date,
            facility_id=certificate.facility_id,
            issuing_state_id=certificate.issuing_state_id,
            doctor_id=certificate.doctor_id,
            verification_token=certificate.verification_token,
        )
        certificate.save(update_fields=["expiry_date", "digital_signature_hash", "updated_at"])
        self.client.force_authenticate(user=None)
        expired_response = self.client.get(f"/api/public/certificates/verify/{certificate.verification_token}/")
        self.assertEqual(data(expired_response)["certificate_validity"], VerificationResult.EXPIRED)

        certificate.expiry_date = timezone.localdate() + timezone.timedelta(days=180)
        certificate.digital_signature_hash = CertificateService.signature_hash(
            certificate_number=certificate.certificate_number,
            assessment_id=certificate.assessment_id,
            food_handler_id=certificate.food_handler_id,
            issue_date=certificate.issue_date,
            expiry_date=certificate.expiry_date,
            facility_id=certificate.facility_id,
            issuing_state_id=certificate.issuing_state_id,
            doctor_id=certificate.doctor_id,
            verification_token=certificate.verification_token,
        )
        certificate.save(update_fields=["expiry_date", "digital_signature_hash", "updated_at"])
        self.client.force_authenticate(self.state_admin)
        suspend_response = self.client.patch(
            f"/api/state/certificates/{certificate.id}/suspend/",
            {"reason": "Public health review."},
            format="json",
        )
        self.assertEqual(suspend_response.status_code, 200)
        self.client.force_authenticate(user=None)
        suspended_response = self.client.get(f"/api/public/certificates/verify/{certificate.verification_token}/")
        self.assertEqual(data(suspended_response)["certificate_validity"], VerificationResult.SUSPENDED)

        self.client.force_authenticate(self.state_admin)
        reinstate_response = self.client.patch(
            f"/api/state/certificates/{certificate.id}/reinstate/",
            {"reason": "Review cleared."},
            format="json",
        )
        self.assertEqual(reinstate_response.status_code, 200)
        self.client.force_authenticate(user=None)
        valid_response = self.client.get(f"/api/public/certificates/verify/{certificate.verification_token}/")
        self.assertEqual(data(valid_response)["certificate_validity"], VerificationResult.VALID)

        self.client.force_authenticate(self.state_admin)
        revoke_response = self.client.patch(
            f"/api/state/certificates/{certificate.id}/revoke/",
            {"reason": "Fraud confirmed."},
            format="json",
        )
        self.assertEqual(revoke_response.status_code, 200)
        cannot_reinstate = self.client.patch(
            f"/api/state/certificates/{certificate.id}/reinstate/",
            {"reason": "Should fail."},
            format="json",
        )
        self.assertEqual(cannot_reinstate.status_code, 400)
        self.client.force_authenticate(user=None)
        revoked_response = self.client.get(f"/api/public/certificates/verify/{certificate.verification_token}/")
        self.assertEqual(data(revoked_response)["certificate_validity"], VerificationResult.REVOKED)

    def test_end_to_end_replacement_preserves_old_number_and_marks_old_certificate(self):
        certificate = self._approve_through_state_queue()
        old_number = certificate.certificate_number
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(
            f"/api/state/certificates/{certificate.id}/replace/",
            {"reason": "Administrative correction."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        certificate.refresh_from_db()
        self.assertEqual(certificate.certificate_number, old_number)
        self.assertEqual(certificate.status, CertificateStatus.REPLACED)
        self.assertEqual(certificate.replacement_reason, "Administrative correction.")

    def test_end_to_end_public_report_inspector_save_employer_and_federal_privacy(self):
        certificate = self._approve_through_state_queue()
        inspector = User.objects.create_user(
            username="final-inspector",
            email="final-inspector@example.com",
            password="StrongPass123!",
            role=UserRole.INSPECTOR,
            state=self.state,
        )
        inspection = Inspection.objects.create(inspector=inspector, employer=self.employer)

        self.client.force_authenticate(user=None)
        report_response = self.client.post(
            "/api/public/certificates/report-suspicious/",
            {"certificate_number": certificate.certificate_number, "reason": "Presented by wrong person."},
            format="json",
        )
        self.assertEqual(report_response.status_code, 201)
        self.assertEqual(SuspiciousCertificateReport.objects.filter(certificate=certificate).count(), 1)

        self.client.force_authenticate(inspector)
        scan_response = self.client.post(
            f"/api/inspector/certificates/{certificate.id}/save-to-inspection/",
            {"inspection": str(inspection.id)},
            format="json",
        )
        self.assertEqual(scan_response.status_code, 201)
        self.assertTrue(InspectionCertificateScan.objects.filter(inspection=inspection, certificate=certificate).exists())

        self.employer.user = User.objects.create_user(
            username="final-employer",
            email="final-employer@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
            state=self.state,
        )
        self.employer.save(update_fields=["user", "updated_at"])
        self.client.force_authenticate(self.employer.user)
        employer_response = self.client.get(f"/api/certificates/{certificate.id}/")
        self.assertEqual(employer_response.status_code, 200)
        self.assertNotIn("digital_signature_hash", data(employer_response))
        self.assertNotIn("masked_nin", data(employer_response))

        federal = User.objects.create_user(
            username="final-federal",
            email="final-federal@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.client.force_authenticate(federal)
        federal_response = self.client.get("/api/federal/certificates/analytics/")
        self.assertEqual(federal_response.status_code, 200)
        self.assertNotIn("food_handler_name", data(federal_response))
        self.assertNotIn("masked_nin", data(federal_response))

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
        self.assertTrue(certificate["certificate_number"].startswith(f"FCNG-LA-{timezone.localdate():%Y}-"))
        self.assertTrue(certificate["verification_token"])
        self.assertIn(certificate["verification_token"], certificate["verification_url"])
        self.assertEqual(certificate["status"], "active")
        self.assertTrue(certificate["qr_code_url"])
        self.assertTrue(certificate["pdf_url"])

    def test_certificate_generation_uses_state_default_template_when_policy_allows(self):
        template = CertificateTemplate.objects.create(
            name="Lagos Certificate",
            scope=CertificateTemplateScope.STATE,
            state=self.state,
            ministry_name="Lagos State Ministry of Health",
            signatory_name="Director Food Safety",
            is_default=True,
        )
        certificate_request = CertificateRequest.objects.create(
            assessment=self.assessment,
            requested_by=self.doctor,
            status="approved",
            reviewed_by=self.state_admin,
            reviewed_at=timezone.now(),
        )
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(
            "/api/certificates/generate/",
            {"certificate_request": str(certificate_request.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        certificate = Certificate.objects.get(id=data(response)["id"])
        self.assertEqual(certificate.template, template)
        self.assertGreater(media_path(certificate.pdf_url).stat().st_size, 1500)

    def test_certificate_generation_falls_back_to_national_template_when_state_overrides_disabled(self):
        NationalPolicyConfig.objects.create(state_certificate_template_overrides_enabled=False)
        national = CertificateTemplate.objects.create(
            name="National Certificate",
            scope=CertificateTemplateScope.NATIONAL,
            ministry_name="Federal Ministry of Health",
            is_default=True,
        )
        CertificateTemplate.objects.create(
            name="Lagos Certificate",
            scope=CertificateTemplateScope.STATE,
            state=self.state,
            ministry_name="Lagos State Ministry of Health",
            is_default=True,
        )
        certificate_request = CertificateRequest.objects.create(
            assessment=self.assessment,
            requested_by=self.doctor,
            status="approved",
            reviewed_by=self.state_admin,
            reviewed_at=timezone.now(),
        )
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(
            "/api/certificates/generate/",
            {"certificate_request": str(certificate_request.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        certificate = Certificate.objects.get(id=data(response)["id"])
        self.assertEqual(certificate.template, national)

    def test_template_management_permissions_defaults_and_audit(self):
        federal_admin = User.objects.create_user(
            username="federal-template",
            email="federal-template@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.client.force_authenticate(federal_admin)
        national = self.client.post(
            "/api/certificate-templates/",
            {
                "name": "National Default",
                "scope": CertificateTemplateScope.NATIONAL,
                "ministry_name": "Federal Ministry of Health",
                "accent_color": "#0f5132",
            },
            format="json",
        )
        self.assertEqual(national.status_code, 201)
        set_default = self.client.post(f"/api/certificate-templates/{data(national)['id']}/set-default/")
        self.assertEqual(set_default.status_code, 200)
        self.assertTrue(data(set_default)["is_default"])

        self.client.force_authenticate(self.state_admin)
        state_template = self.client.post(
            "/api/certificate-templates/",
            {
                "name": "State Default",
                "scope": CertificateTemplateScope.STATE,
                "ministry_name": "Lagos State Ministry of Health",
                "accent_color": "#166534",
            },
            format="json",
        )
        self.assertEqual(state_template.status_code, 201)
        self.assertEqual(str(data(state_template)["state"]), str(self.state.id))
        self.assertEqual(CertificateTemplate.objects.filter(name="State Default").count(), 1)

    def test_state_template_management_respects_national_policy(self):
        NationalPolicyConfig.objects.create(state_certificate_template_overrides_enabled=False)
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(
            "/api/certificate-templates/",
            {"name": "Blocked State Template", "scope": CertificateTemplateScope.STATE, "ministry_name": "Lagos"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_certificate_artifacts_are_written_with_token_verification_url(self):
        certificate_request = CertificateRequest.objects.create(
            assessment=self.assessment,
            requested_by=self.doctor,
            status="approved",
            reviewed_by=self.state_admin,
            reviewed_at=timezone.now(),
        )
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(
            "/api/certificates/generate/",
            {"certificate_request": str(certificate_request.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        payload = data(response)
        self.assertIn(payload["verification_token"], payload["verification_url"])
        qr_path = media_path(payload["qr_code_url"])
        pdf_path = media_path(payload["pdf_url"])
        self.assertTrue(qr_path.exists())
        self.assertTrue(pdf_path.exists())
        self.assertGreater(qr_path.stat().st_size, 500)
        self.assertGreater(pdf_path.stat().st_size, 1500)
        certificate = Certificate.objects.get(id=payload["id"])
        events = set(
            AuditLog.objects.filter(target_type="Certificate", target_id=str(certificate.id)).values_list("metadata__event", flat=True)
        )
        self.assertIn("certificate_qr_generated", events)
        self.assertIn("certificate_pdf_generated", events)
        self.assertIn("certificate_issued", events)

    def test_public_verification_accepts_opaque_verification_token(self):
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
        token = data(generate_response)["verification_token"]
        certificate_number = data(generate_response)["certificate_number"]
        self.client.force_authenticate(user=None)

        verify_response = self.client.get(f"/api/public/certificates/verify/{token}/")

        self.assertEqual(verify_response.status_code, 200)
        self.assertEqual(data(verify_response)["certificate_validity"], VerificationResult.VALID)
        self.assertEqual(data(verify_response)["certificate_number"], certificate_number)

    def test_hash_tamper_returns_invalid(self):
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
        certificate = Certificate.objects.get(id=data(generate_response)["id"])
        certificate.digital_signature_hash = "tampered"
        certificate.save(update_fields=["digital_signature_hash", "updated_at"])
        self.client.force_authenticate(user=None)

        verify_response = self.client.get(f"/api/public/certificates/verify/{certificate.verification_token}/")

        self.assertEqual(verify_response.status_code, 200)
        self.assertEqual(data(verify_response)["certificate_validity"], VerificationResult.INVALID)
        self.assertTrue(
            AuditLog.objects.filter(
                target_type="Certificate",
                target_id=str(certificate.id),
                metadata__event="certificate_hash_mismatch",
            ).exists()
        )

    def test_public_verify_by_number_endpoint(self):
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

        verify_response = self.client.post(
            "/api/public/certificates/verify-by-number/",
            {"certificate_number": certificate_number},
            format="json",
        )

        self.assertEqual(verify_response.status_code, 200)
        self.assertEqual(data(verify_response)["certificate_validity"], VerificationResult.VALID)

    def test_public_can_report_suspicious_certificate(self):
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

        response = self.client.post(
            "/api/public/certificates/report-suspicious/",
            {
                "certificate_number": certificate_number,
                "reporter_contact": "inspector@example.com",
                "reason": "Passport photo mismatch",
                "details": "The person presenting the certificate does not match the holder.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(SuspiciousCertificateReport.objects.count(), 1)
        report = SuspiciousCertificateReport.objects.get()
        self.assertEqual(report.certificate_number_submitted, certificate_number)
        self.assertEqual(report.certificate.certificate_number, certificate_number)

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

    def test_inspector_certificate_verification_is_privacy_safe_and_audited(self):
        inspector = User.objects.create_user(
            username="inspector-cert",
            email="inspector-cert@example.com",
            password="StrongPass123!",
            role=UserRole.INSPECTOR,
            state=self.state,
        )
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
        certificate = Certificate.objects.get(id=data(certificate_response)["id"])

        self.client.force_authenticate(inspector)
        response = self.client.get(f"/api/inspector/certificates/verify/{certificate.verification_token}/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(payload["certificate_validity"], VerificationResult.VALID)
        self.assertNotIn("masked_nin", payload)
        self.assertNotIn("doctor_name", payload)
        self.assertNotIn("digital_signature_hash", payload)
        self.assertTrue(
            AuditLog.objects.filter(
                target_type="Certificate",
                target_id=str(certificate.id),
                metadata__event="inspector_certificate_verified",
            ).exists()
        )

    def test_food_handler_certificate_view_uses_owner_safe_payload(self):
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

        self.client.force_authenticate(self.handler_user)
        response = self.client.get(f"/api/certificates/{certificate_id}/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertIn("renewal_status", payload)
        self.assertIn("masked_nin", payload)
        self.assertNotIn("digital_signature_hash", payload)
        self.assertNotIn("revoked_by", payload)
        self.assertNotIn("issued_by_state_user", payload)

    def test_food_handler_certificate_download_is_audited(self):
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
        certificate = Certificate.objects.get(id=data(certificate_response)["id"])

        self.client.force_authenticate(self.handler_user)
        response = self.client.get(f"/api/certificates/{certificate.id}/download/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            AuditLog.objects.filter(
                target_type="Certificate",
                target_id=str(certificate.id),
                metadata__event="food_handler_certificate_download",
            ).exists()
        )

    def test_state_and_federal_certificate_downloads_are_audited(self):
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
        certificate = Certificate.objects.get(id=data(certificate_response)["id"])
        federal_admin = User.objects.create_user(
            username="federal-certificate-download",
            email="federal-certificate-download@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )

        for user in [self.state_admin, federal_admin]:
            self.client.force_authenticate(user)
            response = self.client.get(f"/api/certificates/{certificate.id}/download/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Type"], "application/pdf")

        self.assertEqual(
            AuditLog.objects.filter(
                target_type="Certificate",
                target_id=str(certificate.id),
                metadata__event="certificate_download",
            ).count(),
            2,
        )

    def test_food_handler_can_start_own_certificate_renewal(self):
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

        self.client.force_authenticate(self.handler_user)
        response = self.client.post(f"/api/certificates/{certificate_id}/start-renewal/", {}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Notification.objects.filter(
            recipient=self.handler_user,
            category=NotificationCategory.RENEWAL,
        ).exists())

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

    def test_incomplete_food_handler_profile_blocks_certificate_request(self):
        self.food_handler.phone = ""
        self.food_handler.save(update_fields=["phone", "updated_at"])
        self.client.force_authenticate(self.doctor)

        response = self.client.post(f"/api/assessments/{self.assessment.id}/request-certificate/", {}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("profile", str(response.data).lower())

    def test_future_accreditation_start_blocks_certificate_generation(self):
        self.facility.accreditation_start_date = timezone.localdate() + timezone.timedelta(days=1)
        self.facility.save(update_fields=["accreditation_start_date", "updated_at"])
        certificate_request = CertificateRequest.objects.create(
            assessment=self.assessment,
            requested_by=self.doctor,
            status="approved",
            reviewed_by=self.state_admin,
            reviewed_at=timezone.now(),
        )
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(
            "/api/certificates/generate/",
            {"certificate_request": str(certificate_request.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("accreditation", str(response.data).lower())
        self.assertTrue(AuditLog.objects.filter(metadata__event="certificate_generation_failed").exists())

    def test_unresolved_illness_blocks_certificate_request(self):
        IllnessReport.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            reported_by=self.employer_org.users.create_user(
                username="illness-reporter",
                email="illness-reporter@example.com",
                password="StrongPass123!",
                role=UserRole.EMPLOYER,
                organization=self.employer_org,
                state=self.state,
            ),
            clearance_status=ClearanceStatus.PENDING,
            clearance_required=True,
        )
        self.client.force_authenticate(self.doctor)

        response = self.client.post(f"/api/assessments/{self.assessment.id}/request-certificate/", {}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("illness", str(response.data).lower())

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

    def test_lifecycle_job_marks_expired_and_sends_idempotent_reminders(self):
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
        certificate = Certificate.objects.get(id=data(certificate_response)["id"])
        certificate.expiry_date = timezone.localdate() + timezone.timedelta(days=30)
        certificate.save(update_fields=["expiry_date", "updated_at"])

        first = CertificateLifecycleJobService.process_expiry_and_reminders()
        second = CertificateLifecycleJobService.process_expiry_and_reminders()

        self.assertEqual(first["reminders_sent"], 1)
        self.assertEqual(second["reminders_sent"], 0)
        self.assertTrue(Notification.objects.filter(
            recipient=self.handler_user,
            category=NotificationCategory.CERTIFICATE,
            related_object_type="certificate",
            related_object_id=certificate.id,
            title="Certificate expires in 30 days",
        ).exists())

        certificate.expiry_date = timezone.localdate() - timezone.timedelta(days=1)
        certificate.save(update_fields=["expiry_date", "updated_at"])
        expired = CertificateLifecycleJobService.process_expiry_and_reminders()
        certificate.refresh_from_db()

        self.assertEqual(expired["expired_marked"], 1)
        self.assertEqual(certificate.status, "expired")
