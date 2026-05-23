from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import EmployerStaffRole, UserRole
from apps.assessments.models import Appointment, AppointmentStatus, AssessmentStatus, FitnessDecision, MedicalAssessment
from apps.audit.models import AuditAction, AuditLog
from apps.audit.services import log_action
from apps.employers.models import Employer, EstablishmentCategory
from apps.facilities.models import AccreditationStatus, FacilityType, MedicalFacility, OwnershipType
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, FoodHandlerStatus, Gender
from apps.illness.models import ClearanceStatus, IllnessReport, SuspectedCondition
from apps.lab_tests.models import LabTest, LabTestStatus
from apps.locations.models import State
from apps.nin_verification.models import NINVerification, NINVerificationStatus
from apps.notifications.models import Notification
from apps.organizations.models import Organization, OrganizationType
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.reports.models import GeneratedReport, ReportType
from apps.vaccinations.models import VaccinationRecord, VaccinationStatus

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
        self.facility_admin = User.objects.create_user(
            username="facility-admin",
            email="facility-admin@example.com",
            password="StrongPass123!",
            role=UserRole.FACILITY_ADMIN,
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

    def _create_decision_ready_assessment(self):
        assessment = self._create_verified_assessment()
        assessment.declaration_status = "validated"
        assessment.physical_exam_status = "completed"
        assessment.lab_status = "reviewed"
        assessment.vaccination_status = "reviewed"
        assessment.status = "vaccination_reviewed"
        assessment.doctor = self.doctor
        assessment.save()
        VaccinationRecord.objects.create(food_handler=self.food_handler, assessment=assessment, vaccine_type="typhoid", status=VaccinationStatus.VALID, recorded_by=self.doctor)
        VaccinationRecord.objects.create(food_handler=self.food_handler, assessment=assessment, vaccine_type="hepatitis_a", status=VaccinationStatus.VALID, recorded_by=self.doctor)
        return assessment

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

    def test_assessment_status_snapshot_reports_prerequisite_blockers(self):
        assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            facility=self.facility,
            status=AssessmentStatus.PAYMENT_PENDING,
        )
        self.client.force_authenticate(self.handler_user)

        response = self.client.get(f"/api/assessments/{assessment.id}/status/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        blocker_codes = {blocker["code"] for blocker in payload["blockers"]}
        warning_codes = {warning["code"] for warning in payload["warnings"]}
        self.assertEqual(payload["current_status"], AssessmentStatus.PAYMENT_PENDING)
        self.assertIn("nin_unverified", blocker_codes)
        self.assertIn("payment_required", blocker_codes)
        self.assertIn("branch_missing", warning_codes)
        self.assertEqual(payload["next_action"]["code"], "verify_nin")
        self.assertFalse(payload["can_proceed"])

    def test_assessment_status_snapshot_points_to_declaration_after_prerequisites(self):
        appointment = Appointment.objects.create(
            food_handler=self.food_handler,
            facility=self.facility,
            appointment_date=timezone.now() + timezone.timedelta(days=1),
            status=AppointmentStatus.CONFIRMED,
            doctor=self.doctor,
        )
        assessment = self._create_verified_assessment()
        assessment.appointment = appointment
        assessment.doctor = self.doctor
        assessment.status = AssessmentStatus.APPOINTMENT_BOOKED
        assessment.save(update_fields=["appointment", "doctor", "status", "updated_at"])
        self.client.force_authenticate(self.handler_user)

        response = self.client.get(f"/api/assessments/{assessment.id}/status/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(payload["blockers"], [])
        self.assertEqual(payload["next_action"]["code"], "submit_declaration")
        self.assertTrue(payload["can_proceed"])

    def test_assessment_cancel_and_close_actions_update_status_and_audit(self):
        appointment = Appointment.objects.create(
            food_handler=self.food_handler,
            facility=self.facility,
            appointment_date=timezone.now() + timezone.timedelta(days=1),
            status=AppointmentStatus.CONFIRMED,
        )
        cancel_assessment = self._create_verified_assessment()
        cancel_assessment.appointment = appointment
        cancel_assessment.status = AssessmentStatus.APPOINTMENT_BOOKED
        cancel_assessment.save(update_fields=["appointment", "status", "updated_at"])
        self.client.force_authenticate(self.handler_user)

        cancel_response = self.client.post(
            f"/api/assessments/{cancel_assessment.id}/cancel/",
            {"reason": "Cannot attend."},
            format="json",
        )

        self.assertEqual(cancel_response.status_code, 200)
        cancel_assessment.refresh_from_db()
        appointment.refresh_from_db()
        self.assertEqual(cancel_assessment.status, AssessmentStatus.CLOSED)
        self.assertEqual(appointment.status, AppointmentStatus.CANCELLED)
        self.assertEqual(
            AuditLog.objects.filter(target_id=str(cancel_assessment.id), metadata__event="assessment_cancelled").count(),
            1,
        )

        close_assessment = self._create_verified_assessment()
        self.client.force_authenticate(self.other_doctor)
        blocked = self.client.post(f"/api/assessments/{close_assessment.id}/close/", {"reason": "Wrong facility."}, format="json")
        self.assertEqual(blocked.status_code, 404)

        self.client.force_authenticate(self.facility_admin)
        close_response = self.client.post(f"/api/assessments/{close_assessment.id}/close/", {"notes": "Admin closure."}, format="json")
        self.assertEqual(close_response.status_code, 200)
        close_assessment.refresh_from_db()
        self.assertEqual(close_assessment.status, AssessmentStatus.CLOSED)
        self.assertEqual(AuditLog.objects.filter(target_id=str(close_assessment.id), metadata__event="assessment_closed").count(), 1)

    def test_facility_can_confirm_paid_appointment_and_notify_parties(self):
        appointment = Appointment.objects.create(
            food_handler=self.food_handler,
            facility=self.facility,
            appointment_date=timezone.now() + timezone.timedelta(days=1),
        )
        assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            facility=self.facility,
            appointment=appointment,
            payment_transaction=self.payment,
            status=AssessmentStatus.PAYMENT_CONFIRMED,
        )
        self.client.force_authenticate(self.facility_admin)

        response = self.client.patch(
            f"/api/facilities/{self.facility.id}/appointments/{appointment.id}/confirm/",
            {"notes": "Payment verified."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        appointment.refresh_from_db()
        assessment.refresh_from_db()
        self.assertEqual(appointment.status, AppointmentStatus.CONFIRMED)
        self.assertEqual(assessment.status, AssessmentStatus.APPOINTMENT_BOOKED)
        self.assertEqual(data(response)["payment_status"], PaymentStatus.SUCCESS)
        self.assertEqual(Notification.objects.filter(recipient=self.handler_user).count(), 1)
        self.assertEqual(Notification.objects.filter(recipient=self.employer_user).count(), 1)

    def test_confirm_appointment_requires_successful_payment_and_current_accreditation(self):
        appointment = Appointment.objects.create(
            food_handler=self.food_handler,
            facility=self.facility,
            appointment_date=timezone.now() + timezone.timedelta(days=1),
        )
        self.client.force_authenticate(self.facility_admin)

        unpaid_response = self.client.patch(f"/api/appointments/{appointment.id}/confirm/", {}, format="json")
        self.assertEqual(unpaid_response.status_code, 400)

        MedicalAssessment.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            facility=self.facility,
            appointment=appointment,
            payment_transaction=self.payment,
            status=AssessmentStatus.PAYMENT_CONFIRMED,
        )
        self.facility.accreditation_status = AccreditationStatus.SUSPENDED
        self.facility.save(update_fields=["accreditation_status", "updated_at"])

        suspended_response = self.client.patch(f"/api/appointments/{appointment.id}/confirm/", {}, format="json")
        self.assertEqual(suspended_response.status_code, 400)

    def test_facility_can_reschedule_cancel_no_show_and_assign_doctor(self):
        appointment = Appointment.objects.create(
            food_handler=self.food_handler,
            facility=self.facility,
            appointment_date=timezone.now() + timezone.timedelta(days=1),
        )
        assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            facility=self.facility,
            appointment=appointment,
            payment_transaction=self.payment,
            status=AssessmentStatus.PAYMENT_CONFIRMED,
        )
        self.client.force_authenticate(self.facility_admin)

        bad_assignment = self.client.patch(
            f"/api/appointments/{appointment.id}/assign-doctor/",
            {"doctor": str(self.other_doctor.id)},
            format="json",
        )
        self.assertEqual(bad_assignment.status_code, 403)

        assignment = self.client.patch(
            f"/api/appointments/{appointment.id}/assign-doctor/",
            {"doctor": str(self.doctor.id)},
            format="json",
        )
        self.assertEqual(assignment.status_code, 200)
        appointment.refresh_from_db()
        assessment.refresh_from_db()
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(assessment.doctor, self.doctor)

        new_date = timezone.now() + timezone.timedelta(days=3)
        reschedule = self.client.patch(
            f"/api/appointments/{appointment.id}/reschedule/",
            {"appointment_date": new_date.isoformat(), "reason": "Doctor roster change"},
            format="json",
        )
        self.assertEqual(reschedule.status_code, 200)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, AppointmentStatus.RESCHEDULED)

        no_show = self.client.patch(f"/api/appointments/{appointment.id}/no-show/", {"notes": "Did not arrive."}, format="json")
        self.assertEqual(no_show.status_code, 200)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, AppointmentStatus.NO_SHOW)

        cancel = self.client.patch(f"/api/appointments/{appointment.id}/cancel/", {"reason": "Rebook required."}, format="json")
        self.assertEqual(cancel.status_code, 200)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, AppointmentStatus.CANCELLED)

    def test_facility_assessment_queue_filters_and_scopes_to_facility(self):
        own = MedicalAssessment.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            payment_transaction=self.payment,
            lab_status="reviewed",
            final_decision=FitnessDecision.FIT,
            status=AssessmentStatus.PAYMENT_CONFIRMED,
        )
        MedicalAssessment.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            facility=self.other_facility,
            doctor=self.other_doctor,
            status=AssessmentStatus.PAYMENT_PENDING,
        )
        self.client.force_authenticate(self.facility_admin)

        response = self.client.get(
            f"/api/facilities/{self.facility.id}/assessments/",
            {"doctor": str(self.doctor.id), "lab_status": "reviewed", "payment_status": PaymentStatus.SUCCESS},
        )

        self.assertEqual(response.status_code, 200)
        rows = response.data
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], str(own.id))
        self.assertEqual(rows[0]["payment_status"], PaymentStatus.SUCCESS)
        self.assertEqual(rows[0]["doctor_notes"], "")

    def test_facility_assessment_detail_is_audited_and_privacy_shaped(self):
        assessment = self._create_verified_assessment()
        assessment.doctor_notes = "Restricted clinical note"
        assessment.save(update_fields=["doctor_notes", "updated_at"])
        self.client.force_authenticate(self.lab_staff)

        response = self.client.get(f"/api/facilities/{self.facility.id}/assessments/{assessment.id}/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertFalse(payload["can_view_clinical"])
        self.assertEqual(payload["doctor_notes"], "")
        self.assertIsNone(payload["health_declaration"])
        self.assertEqual(AuditLog.objects.filter(action=AuditAction.MEDICAL_RECORD_ACCESS, target_id=str(assessment.id)).count(), 1)

    def test_facility_can_assign_doctor_from_assessment_queue(self):
        appointment = Appointment.objects.create(
            food_handler=self.food_handler,
            facility=self.facility,
            appointment_date=timezone.now() + timezone.timedelta(days=1),
        )
        assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            facility=self.facility,
            appointment=appointment,
            payment_transaction=self.payment,
            status=AssessmentStatus.PAYMENT_CONFIRMED,
        )
        self.client.force_authenticate(self.facility_admin)

        response = self.client.patch(
            f"/api/facilities/{self.facility.id}/assessments/{assessment.id}/assign-doctor/",
            {"doctor": str(self.doctor.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        assessment.refresh_from_db()
        appointment.refresh_from_db()
        self.assertEqual(assessment.doctor, self.doctor)
        self.assertEqual(appointment.doctor, self.doctor)

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

    def test_declaration_draft_submit_lock_and_reopen_versioning(self):
        assessment = self._create_verified_assessment()
        self.client.force_authenticate(self.handler_user)

        draft_response = self.client.patch(
            f"/api/assessments/{assessment.id}/declaration/",
            {"certified_true": False, "skin_trouble": True},
            format="json",
        )
        self.assertEqual(draft_response.status_code, 200)
        self.assertEqual(data(draft_response)["version"], 1)
        self.assertTrue(data(draft_response)["risk_flag"])
        self.assertIsNone(data(draft_response)["submitted_at"])

        submit_response = self.client.post(
            f"/api/assessments/{assessment.id}/declaration/submit/",
            {"certified_true": True, "skin_trouble": True},
            format="json",
        )
        self.assertEqual(submit_response.status_code, 201)
        self.assertEqual(data(submit_response)["version"], 1)
        self.assertIsNotNone(data(submit_response)["submitted_at"])

        blocked_draft = self.client.patch(
            f"/api/assessments/{assessment.id}/declaration/",
            {"certified_true": False},
            format="json",
        )
        self.assertEqual(blocked_draft.status_code, 400)

        self.client.force_authenticate(self.doctor)
        validate_response = self.client.post(f"/api/assessments/{assessment.id}/declaration/validate/")
        self.assertEqual(validate_response.status_code, 200)
        self.assertTrue(data(validate_response)["is_locked"])

        reopen_locked = self.client.post(
            f"/api/assessments/{assessment.id}/declaration/reopen/",
            {"reason": "Late correction."},
            format="json",
        )
        self.assertEqual(reopen_locked.status_code, 400)

        correction_assessment = self._create_verified_assessment()
        self.client.force_authenticate(self.handler_user)
        correction_submit = self.client.post(
            f"/api/assessments/{correction_assessment.id}/declaration/",
            {"certified_true": True, "skin_trouble": False},
            format="json",
        )
        self.assertEqual(correction_submit.status_code, 201)
        correction_assessment.doctor = self.doctor
        correction_assessment.save(update_fields=["doctor", "updated_at"])

        self.client.force_authenticate(self.doctor)
        clarification = self.client.patch(
            f"/api/doctor/assessments/{correction_assessment.id}/declaration/request-changes/",
            {"reason": "Update the skin symptoms answer."},
            format="json",
        )
        self.assertEqual(clarification.status_code, 200)

        self.client.force_authenticate(self.handler_user)
        corrected_draft = self.client.patch(
            f"/api/assessments/{correction_assessment.id}/declaration/",
            {"certified_true": False, "skin_trouble": True},
            format="json",
        )
        self.assertEqual(corrected_draft.status_code, 200)
        self.assertEqual(data(corrected_draft)["version"], 2)
        self.assertIsNone(data(corrected_draft)["submitted_at"])

        corrected_submit = self.client.post(
            f"/api/assessments/{correction_assessment.id}/declaration/submit/",
            {"certified_true": True, "skin_trouble": True},
            format="json",
        )
        self.assertEqual(corrected_submit.status_code, 201)
        self.assertEqual(data(corrected_submit)["version"], 2)
        self.assertEqual(data(corrected_submit)["clarification_reason"], "")

    def test_doctor_aliases_validate_declaration_and_complete_physical_exam_for_assigned_case(self):
        assessment = self._create_verified_assessment()
        assessment.doctor = self.doctor
        assessment.save(update_fields=["doctor", "updated_at"])
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

        self.client.force_authenticate(self.doctor)
        queue_response = self.client.get("/api/doctor/assessments/")
        detail_response = self.client.get(f"/api/doctor/assessments/{assessment.id}/")
        validate_response = self.client.patch(f"/api/doctor/assessments/{assessment.id}/declaration/validate/")
        exam_response = self.client.post(
            f"/api/doctor/assessments/{assessment.id}/physical-exam/",
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
                "other_notes": "Normal exam.",
            },
            format="json",
        )

        self.assertEqual(queue_response.status_code, 200)
        self.assertEqual(len(data(queue_response)), 1)
        self.assertEqual(detail_response.status_code, 200)
        self.assertTrue(detail_response.data["health_declaration"]["risk_flag"])
        self.assertEqual(validate_response.status_code, 200)
        self.assertEqual(exam_response.status_code, 201)
        assessment.refresh_from_db()
        self.assertEqual(assessment.declaration_status, "validated")
        self.assertEqual(assessment.physical_exam_status, "completed")

        self.client.force_authenticate(self.handler_user)
        locked_response = self.client.post(
            f"/api/assessments/{assessment.id}/declaration/",
            {"certified_true": True},
            format="json",
        )
        self.assertEqual(locked_response.status_code, 400)

    def test_physical_exam_draft_complete_risk_flag_and_access_audit(self):
        assessment = self._create_verified_assessment()
        assessment.doctor = self.doctor
        assessment.save(update_fields=["doctor", "updated_at"])
        self.client.force_authenticate(self.doctor)

        draft_response = self.client.patch(
            f"/api/doctor/assessments/{assessment.id}/physical-exam/draft/",
            {
                "fever": True,
                "jaundice": False,
                "skin_infection": False,
                "boils_styes_sepsis": False,
                "discharge": False,
                "diarrhoea": False,
                "vomiting": False,
                "sore_throat_with_fever": False,
                "cough_or_flu": False,
                "known_typhoid_carrier_history": False,
                "other_notes": "Fever observed.",
            },
            format="json",
        )
        self.assertEqual(draft_response.status_code, 200)
        self.assertTrue(data(draft_response)["risk_flag"])
        self.assertFalse(data(draft_response)["is_completed"])
        assessment.refresh_from_db()
        self.assertEqual(assessment.physical_exam_status, "submitted")

        read_response = self.client.get(f"/api/assessments/{assessment.id}/physical-exam/")
        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(AuditLog.objects.filter(target_id=str(assessment.id), metadata__event="physical_exam_read").count(), 1)

        complete_response = self.client.post(
            f"/api/assessments/{assessment.id}/physical-exam/complete/",
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
                "other_notes": "Cleared on exam.",
            },
            format="json",
        )
        self.assertEqual(complete_response.status_code, 201)
        self.assertFalse(data(complete_response)["risk_flag"])
        self.assertTrue(data(complete_response)["is_completed"])
        assessment.refresh_from_db()
        self.assertEqual(assessment.physical_exam_status, "completed")
        self.assertEqual(assessment.status, AssessmentStatus.PHYSICAL_EXAM_COMPLETED)

    def test_doctor_can_request_declaration_changes_before_validation(self):
        assessment = self._create_verified_assessment()
        assessment.doctor = self.doctor
        assessment.save(update_fields=["doctor", "updated_at"])
        self.client.force_authenticate(self.handler_user)
        self.client.post(
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
        response = self.client.patch(
            f"/api/doctor/assessments/{assessment.id}/declaration/request-changes/",
            {"reason": "Please clarify recent symptoms."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["clarification_reason"], "Please clarify recent symptoms.")
        assessment.refresh_from_db()
        self.assertEqual(assessment.declaration_status, "pending")

    def test_unassigned_doctor_cannot_access_doctor_assessment_alias(self):
        assessment = self._create_verified_assessment()
        self.client.force_authenticate(self.doctor)

        response = self.client.get(f"/api/doctor/assessments/{assessment.id}/")

        self.assertEqual(response.status_code, 404)

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
        hepatitis_response = self.client.post(
            f"/api/assessments/{assessment.id}/vaccinations/",
            {
                "vaccine_type": "hepatitis_a",
                "date_administered": str(timezone.localdate()),
                "dose_number": 2,
            },
            format="json",
        )
        self.assertEqual(hepatitis_response.status_code, 201)

        decision_response = self.client.patch(
            f"/api/assessments/{assessment.id}/fitness-decision/",
            {
                "final_decision": FitnessDecision.FIT,
                "doctor_notes": "Fit for food handling.",
                "digital_signature_confirmation": True,
            },
            format="json",
        )

        self.assertEqual(decision_response.status_code, 200)
        self.assertTrue(data(decision_response)["can_request_certificate"])
        assessment.refresh_from_db()
        self.assertEqual(assessment.final_decision, FitnessDecision.FIT)
        self.assertTrue(assessment.digital_signature_hash)
        self.assertEqual(assessment.signed_by, self.doctor)
        self.assertEqual(GeneratedReport.objects.filter(filters__assessment_id=str(assessment.id), report_type=ReportType.MEDICAL_EXAMINATION).count(), 1)

        second_response = self.client.patch(
            f"/api/assessments/{assessment.id}/fitness-decision/",
            {
                "final_decision": FitnessDecision.NOT_FIT,
                "doctor_notes": "Attempted change.",
                "digital_signature_confirmation": True,
            },
            format="json",
        )
        self.assertEqual(second_response.status_code, 400)

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

    def test_final_decision_requires_digital_signoff_and_blocks_unresolved_illness(self):
        assessment = self._create_verified_assessment()
        assessment.declaration_status = "validated"
        assessment.physical_exam_status = "completed"
        assessment.lab_status = "reviewed"
        assessment.vaccination_status = "reviewed"
        assessment.status = "vaccination_reviewed"
        assessment.doctor = self.doctor
        assessment.save()
        VaccinationRecord.objects.create(food_handler=self.food_handler, assessment=assessment, vaccine_type="typhoid", status=VaccinationStatus.VALID, recorded_by=self.doctor)
        VaccinationRecord.objects.create(food_handler=self.food_handler, assessment=assessment, vaccine_type="hepatitis_a", status=VaccinationStatus.VALID, recorded_by=self.doctor)
        self.client.force_authenticate(self.doctor)

        unsigned = self.client.patch(
            f"/api/doctor/assessments/{assessment.id}/fitness-decision/",
            {"final_decision": FitnessDecision.FIT},
            format="json",
        )
        self.assertEqual(unsigned.status_code, 400)

        IllnessReport.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            reported_by=self.employer_user,
            suspected_condition=SuspectedCondition.CHOLERA,
        )
        blocked = self.client.patch(
            f"/api/doctor/assessments/{assessment.id}/fitness-decision/",
            {"final_decision": FitnessDecision.FIT, "digital_signature_confirmation": True},
            format="json",
        )
        self.assertEqual(blocked.status_code, 400)

    def test_not_fit_decision_generates_report_without_certificate_eligibility(self):
        assessment = self._create_decision_ready_assessment()
        self.client.force_authenticate(self.doctor)

        response = self.client.patch(
            f"/api/doctor/assessments/{assessment.id}/fitness-decision/",
            {
                "final_decision": FitnessDecision.TEMPORARILY_NOT_FIT,
                "doctor_notes": "Follow up required.",
                "digital_signature_confirmation": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(data(response)["can_request_certificate"])
        self.assertEqual(GeneratedReport.objects.filter(filters__assessment_id=str(assessment.id), report_type=ReportType.TEMPORARILY_NOT_FIT).count(), 1)
        assessment.refresh_from_db()
        self.food_handler.refresh_from_db()
        self.assertEqual(assessment.status, AssessmentStatus.TEMPORARILY_NOT_FIT)
        self.assertEqual(self.food_handler.current_status, FoodHandlerStatus.TEMPORARILY_NOT_FIT)
        illness = IllnessReport.objects.get(food_handler=self.food_handler)
        self.assertEqual(illness.clearance_status, ClearanceStatus.PENDING)
        self.assertEqual(illness.notes, "Follow up required.")

    def test_fitness_decision_draft_does_not_sign_or_mutate_final_decision(self):
        assessment = self._create_decision_ready_assessment()
        self.client.force_authenticate(self.doctor)

        response = self.client.patch(
            f"/api/doctor/assessments/{assessment.id}/fitness-decision/draft/",
            {
                "final_decision": FitnessDecision.TEMPORARILY_NOT_FIT,
                "return_to_work_date": str(timezone.localdate() + timezone.timedelta(days=7)),
                "doctor_notes": "Observe for one week.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        assessment.refresh_from_db()
        self.assertEqual(assessment.final_decision, FitnessDecision.PENDING)
        self.assertIsNone(assessment.signed_at)
        self.assertEqual(assessment.decision_draft, FitnessDecision.TEMPORARILY_NOT_FIT)
        self.assertEqual(assessment.decision_draft_notes, "Observe for one week.")
        self.assertFalse(IllnessReport.objects.filter(food_handler=self.food_handler).exists())

    def test_public_health_clearance_decision_creates_clearance_required_case(self):
        assessment = self._create_decision_ready_assessment()
        self.client.force_authenticate(self.doctor)

        response = self.client.patch(
            f"/api/doctor/assessments/{assessment.id}/fitness-decision/",
            {
                "final_decision": FitnessDecision.REQUIRES_PUBLIC_HEALTH_CLEARANCE,
                "doctor_notes": "Escalate for public health clearance.",
                "digital_signature_confirmation": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        assessment.refresh_from_db()
        self.food_handler.refresh_from_db()
        self.assertEqual(assessment.final_decision, FitnessDecision.REQUIRES_PUBLIC_HEALTH_CLEARANCE)
        self.assertEqual(self.food_handler.current_status, FoodHandlerStatus.EXCLUDED)
        illness = IllnessReport.objects.get(food_handler=self.food_handler)
        self.assertTrue(illness.clearance_required)
        self.assertEqual(illness.clearance_status, ClearanceStatus.CLEARANCE_REQUIRED)

        self.client.force_authenticate(self.employer_user)
        employer_response = self.client.get(f"/api/assessments/{assessment.id}/")
        self.assertEqual(employer_response.status_code, 200)
        self.assertNotIn("doctor_notes", data(employer_response))
        self.assertNotIn("decision_draft_notes", data(employer_response))

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

    def test_lab_staff_can_collect_sample_enter_result_and_upload_document_via_alias(self):
        assessment = self._create_verified_assessment()
        assessment.doctor = self.doctor
        assessment.save(update_fields=["doctor", "updated_at"])
        lab_test = LabTest.objects.create(
            assessment=assessment,
            requested_by=self.doctor,
            test_type="stool_microscopy",
        )
        self.client.force_authenticate(self.lab_staff)

        queue_response = self.client.get("/api/lab/requests/")
        collected_response = self.client.patch(
            f"/api/lab/requests/{lab_test.id}/sample-collected/",
            {"lab_staff_notes": "Sample received at front desk."},
            format="json",
        )
        result_response = self.client.patch(
            f"/api/lab/requests/{lab_test.id}/result/",
            {"status": LabTestStatus.INCONCLUSIVE, "result_value": "Borderline", "lab_staff_notes": "Repeat advised."},
            format="json",
        )
        upload_response = self.client.post(
            f"/api/lab/requests/{lab_test.id}/upload-result/",
            {
                "result_document": SimpleUploadedFile("result.pdf", b"%PDF-1.4\n%", content_type="application/pdf"),
                "lab_staff_notes": "PDF result uploaded.",
            },
            format="multipart",
        )

        self.assertEqual(queue_response.status_code, 200)
        self.assertEqual(len(data(queue_response)), 1)
        self.assertEqual(collected_response.status_code, 200)
        self.assertEqual(result_response.status_code, 200)
        self.assertEqual(upload_response.status_code, 200)
        lab_test.refresh_from_db()
        self.assertIsNotNone(lab_test.sample_collected_at)
        self.assertIsNotNone(lab_test.submitted_to_doctor_at)
        self.assertEqual(lab_test.status, LabTestStatus.INCONCLUSIVE)
        self.assertTrue(lab_test.result_document.name)

    def test_lab_staff_cannot_review_and_doctor_reviews_results(self):
        assessment = self._create_verified_assessment()
        assessment.doctor = self.doctor
        assessment.save(update_fields=["doctor", "updated_at"])
        lab_test = LabTest.objects.create(
            assessment=assessment,
            requested_by=self.doctor,
            test_type="stool_microscopy",
            status=LabTestStatus.NEGATIVE,
            result_value="Negative",
            resulted_by=self.lab_staff,
            resulted_at=timezone.now(),
        )

        self.client.force_authenticate(self.lab_staff)
        blocked = self.client.patch(f"/api/lab/requests/{lab_test.id}/review/")
        self.assertEqual(blocked.status_code, 403)

        self.client.force_authenticate(self.doctor)
        response = self.client.patch(f"/api/lab/requests/{lab_test.id}/review/")

        self.assertEqual(response.status_code, 200)
        lab_test.refresh_from_db()
        assessment.refresh_from_db()
        self.assertEqual(lab_test.status, LabTestStatus.REVIEWED)
        self.assertEqual(assessment.lab_status, "reviewed")

    def test_doctor_review_captures_notes_recommendation_and_audit(self):
        assessment = self._create_verified_assessment()
        assessment.doctor = self.doctor
        assessment.save(update_fields=["doctor", "updated_at"])
        lab_test = LabTest.objects.create(
            assessment=assessment,
            requested_by=self.doctor,
            test_type="stool_microscopy",
            status=LabTestStatus.INCONCLUSIVE,
            result_value="Borderline",
            resulted_by=self.lab_staff,
            resulted_at=timezone.now(),
            submitted_to_doctor_at=timezone.now(),
            is_flagged=True,
        )
        self.client.force_authenticate(self.doctor)

        response = self.client.post(
            f"/api/lab-tests/{lab_test.id}/review/",
            {"doctor_review_notes": "Repeat before final decision.", "doctor_recommendation": "repeat_test"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        lab_test.refresh_from_db()
        self.assertEqual(lab_test.status, LabTestStatus.REVIEWED)
        self.assertTrue(lab_test.is_flagged)
        self.assertEqual(lab_test.doctor_review_notes, "Repeat before final decision.")
        self.assertEqual(lab_test.doctor_recommendation, "repeat_test")
        self.assertEqual(AuditLog.objects.filter(target_id=str(lab_test.id), metadata__event="lab_result_reviewed").count(), 1)

    def test_lab_staff_status_aliases_submit_to_doctor_and_access_audit(self):
        assessment = self._create_verified_assessment()
        assessment.doctor = self.doctor
        assessment.save(update_fields=["doctor", "updated_at"])
        self.client.force_authenticate(self.doctor)
        request_response = self.client.post(
            f"/api/assessments/{assessment.id}/lab-tests/",
            {"tests": [], "include_required": True},
            format="json",
        )
        self.assertEqual(request_response.status_code, 201)
        lab_test = LabTest.objects.filter(assessment=assessment, test_type="stool_microscopy").first()
        self.assertIsNotNone(lab_test)
        self.assertEqual(lab_test.status, LabTestStatus.SAMPLE_COLLECTION_PENDING)

        self.client.force_authenticate(self.lab_staff)
        read_response = self.client.get(f"/api/lab/requests/{lab_test.id}/")
        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(AuditLog.objects.filter(target_id=str(lab_test.id), metadata__event="lab_result_read").count(), 1)

        collect_response = self.client.patch(
            f"/api/lab/requests/{lab_test.id}/sample-collected/",
            {"lab_staff_notes": "Sample collected."},
            format="json",
        )
        self.assertEqual(collect_response.status_code, 200)
        self.assertEqual(data(collect_response)["status"], LabTestStatus.SAMPLE_COLLECTED)

        result_response = self.client.patch(
            f"/api/lab/requests/{lab_test.id}/result/",
            {"status": LabTestStatus.NEGATIVE, "result_value": "Negative"},
            format="json",
        )
        self.assertEqual(result_response.status_code, 200)
        self.assertIsNone(data(result_response)["submitted_to_doctor_at"])

        submit_response = self.client.patch(
            f"/api/lab/requests/{lab_test.id}/submit-to-doctor/",
            {"lab_staff_notes": "Ready for review."},
            format="json",
        )
        self.assertEqual(submit_response.status_code, 200)
        self.assertIsNotNone(data(submit_response)["submitted_to_doctor_at"])
        lab_test.refresh_from_db()
        self.assertEqual(lab_test.lab_staff_notes, "Ready for review.")
        self.assertEqual(AuditLog.objects.filter(target_id=str(lab_test.id), metadata__event="lab_result_submitted_to_doctor").count(), 1)

    def test_lab_request_adds_required_tests_and_repeat_preserves_parent(self):
        assessment = self._create_verified_assessment()
        assessment.doctor = self.doctor
        assessment.save(update_fields=["doctor", "updated_at"])
        self.client.force_authenticate(self.doctor)

        request_response = self.client.post(
            f"/api/assessments/{assessment.id}/lab-tests/",
            {"tests": [{"test_type": "other", "test_name": "Additional swab"}]},
            format="json",
        )
        self.assertEqual(request_response.status_code, 201)
        tests = LabTest.objects.filter(assessment=assessment)
        self.assertEqual(tests.count(), 4)
        self.assertTrue(tests.filter(test_type="stool_microscopy").exists())
        self.assertTrue(tests.filter(test_type="stool_culture_sensitivity").exists())
        self.assertTrue(tests.filter(test_type="hepatitis_a_antigen").exists())
        self.assertTrue(tests.filter(test_type="other", test_name="Additional swab").exists())

        parent = tests.get(test_type="stool_microscopy")
        self.client.force_authenticate(self.lab_staff)
        result_response = self.client.patch(
            f"/api/lab-tests/{parent.id}/result/",
            {"status": LabTestStatus.INCONCLUSIVE, "result_value": "Borderline"},
            format="json",
        )
        self.assertEqual(result_response.status_code, 200)
        parent.refresh_from_db()
        self.assertTrue(parent.is_flagged)

        self.client.force_authenticate(self.doctor)
        repeat_response = self.client.post(
            f"/api/lab-tests/{parent.id}/request-repeat/",
            {"reason": "Repeat inconclusive stool microscopy."},
            format="json",
        )
        self.assertEqual(repeat_response.status_code, 200)
        repeat = LabTest.objects.get(id=data(repeat_response)["id"])
        parent.refresh_from_db()
        self.assertEqual(repeat.parent_lab_test, parent)
        self.assertEqual(repeat.test_type, parent.test_type)
        self.assertEqual(repeat.repeat_reason, "Repeat inconclusive stool microscopy.")
        self.assertTrue(parent.repeat_required)
        self.assertEqual(parent.status, LabTestStatus.REPEAT_REQUIRED)
        assessment.refresh_from_db()
        self.assertEqual(assessment.lab_status, "pending")

    def test_doctor_vaccination_review_applies_policy_defaults_and_completes_step(self):
        assessment = self._create_verified_assessment()
        assessment.doctor = self.doctor
        assessment.save(update_fields=["doctor", "updated_at"])
        self.client.force_authenticate(self.doctor)

        typhoid_response = self.client.patch(
            f"/api/doctor/assessments/{assessment.id}/vaccination-review/",
            {
                "vaccine_type": "typhoid",
                "action": "administer",
                "date_administered": str(timezone.localdate()),
                "dose_number": 1,
                "brand_name": "Tyvac",
                "batch_number": "TY-001",
                "vaccinator_name": "Dr Review",
                "vaccination_facility_name": "Mainland Diagnostics",
                "vaccination_facility_address": "1 Mainland Road, Lagos",
                "notes": "Typhoid administered.",
            },
            format="json",
        )
        hepatitis_response = self.client.patch(
            f"/api/doctor/assessments/{assessment.id}/vaccination-review/",
            {
                "vaccine_type": "hepatitis_a",
                "date_administered": str(timezone.localdate()),
                "dose_number": 1,
            },
            format="json",
        )

        self.assertEqual(typhoid_response.status_code, 200)
        self.assertEqual(hepatitis_response.status_code, 200)
        typhoid = VaccinationRecord.objects.get(id=data(typhoid_response)["id"])
        hepatitis = VaccinationRecord.objects.get(id=data(hepatitis_response)["id"])
        self.assertEqual(typhoid.status, VaccinationStatus.ADMINISTERED)
        self.assertEqual(typhoid.expiry_date, timezone.localdate() + timezone.timedelta(days=365 * 3))
        self.assertEqual(typhoid.brand_name, "Tyvac")
        self.assertEqual(typhoid.batch_number, "TY-001")
        self.assertEqual(data(typhoid_response)["compliance_status"], "compliant")
        self.assertEqual(hepatitis.status, VaccinationStatus.SECOND_DOSE_DUE)
        self.assertEqual(hepatitis.reminder_date, timezone.localdate() + timezone.timedelta(days=30 * 6))
        self.assertEqual(hepatitis.next_dose_date, timezone.localdate() + timezone.timedelta(days=30 * 6))
        self.assertEqual(data(hepatitis_response)["compliance_status"], "second_dose_pending")
        assessment.refresh_from_db()
        self.assertEqual(assessment.vaccination_status, "reviewed")
        self.assertEqual(assessment.status, AssessmentStatus.VACCINATION_REVIEWED)

    def test_final_decision_blocks_unreviewed_vaccination_compliance(self):
        assessment = self._create_verified_assessment()
        assessment.declaration_status = "validated"
        assessment.physical_exam_status = "completed"
        assessment.lab_status = "reviewed"
        assessment.vaccination_status = "reviewed"
        assessment.status = "vaccination_reviewed"
        assessment.doctor = self.doctor
        assessment.save()
        self.client.force_authenticate(self.doctor)

        response = self.client.patch(
            f"/api/doctor/assessments/{assessment.id}/fitness-decision/",
            {"final_decision": FitnessDecision.FIT, "digital_signature_confirmation": True},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("vaccination compliance", str(response.data).lower())

    def test_vaccination_review_supports_missing_and_employer_safe_notes(self):
        assessment = self._create_verified_assessment()
        assessment.doctor = self.doctor
        assessment.save(update_fields=["doctor", "updated_at"])
        self.client.force_authenticate(self.doctor)

        response = self.client.patch(
            f"/api/doctor/assessments/{assessment.id}/vaccination-review/",
            {"vaccine_type": "typhoid", "status": "missing", "notes": "Private clinical note."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        record_id = data(response)["id"]
        self.assertEqual(data(response)["notes"], "Private clinical note.")

        self.client.force_authenticate(self.employer_user)
        employer_response = self.client.get(f"/api/vaccinations/{record_id}/")

        self.assertEqual(employer_response.status_code, 200)
        self.assertEqual(data(employer_response)["status"], VaccinationStatus.MISSING)
        self.assertEqual(data(employer_response)["compliance_status"], "due")
        self.assertEqual(data(employer_response)["notes"], "")

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

    def test_assessment_report_access_is_role_safe_and_audited(self):
        assessment = self._create_decision_ready_assessment()
        assessment.doctor_notes = "Restricted doctor decision note."
        assessment.save(update_fields=["doctor_notes", "updated_at"])
        LabTest.objects.create(
            assessment=assessment,
            requested_by=self.doctor,
            test_type="stool_microscopy",
            status=LabTestStatus.POSITIVE,
            result_value="Positive",
            result_notes="Restricted lab note.",
            doctor_review_notes="Restricted doctor lab review.",
        )

        self.client.force_authenticate(self.doctor)
        medical = self.client.get(f"/api/assessments/{assessment.id}/reports/medical/")
        self.assertEqual(medical.status_code, 200)
        self.assertEqual(data(medical)["report_type"], ReportType.MEDICAL_EXAMINATION)
        self.assertIn("Restricted doctor decision note.", str(data(medical)["summary"]))
        self.assertIn("Restricted lab note.", str(data(medical)["summary"]))
        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditAction.MEDICAL_RECORD_ACCESS,
                target_id=str(assessment.id),
                metadata__report_kind="medical",
            ).exists()
        )

        self.client.force_authenticate(self.lab_staff)
        lab_only = self.client.get(f"/api/assessments/{assessment.id}/reports/medical/")
        self.assertEqual(lab_only.status_code, 200)
        self.assertIn("restricted_lab_summary", data(lab_only)["summary"]["sections"])
        self.assertNotIn("Restricted doctor decision note.", str(data(lab_only)["summary"]))
        self.assertNotIn("Restricted lab note.", str(data(lab_only)["summary"]))

        self.client.force_authenticate(self.employer_user)
        blocked_medical = self.client.get(f"/api/assessments/{assessment.id}/reports/medical/")
        self.assertEqual(blocked_medical.status_code, 403)
        summary = self.client.get(f"/api/assessments/{assessment.id}/reports/summary/")
        self.assertEqual(summary.status_code, 200)
        self.assertNotIn("Restricted doctor decision note.", str(data(summary)["summary"]))

    def test_assessment_audit_timeline_correlates_related_events_and_is_restricted(self):
        assessment = self._create_decision_ready_assessment()
        lab_test = LabTest.objects.create(
            assessment=assessment,
            requested_by=self.doctor,
            test_type="stool_microscopy",
            status=LabTestStatus.NEGATIVE,
        )
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=self.lab_staff,
            target=lab_test,
            metadata={"event": "lab_result_recorded"},
        )
        state_admin = User.objects.create_user(
            username="timeline-state",
            email="timeline-state@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.state,
        )

        self.client.force_authenticate(self.facility_admin)
        status_response = self.client.get(f"/api/assessments/{assessment.id}/status/")
        self.assertEqual(status_response.status_code, 200)
        timeline_response = self.client.get(f"/api/assessments/{assessment.id}/audit-timeline/")
        self.assertEqual(timeline_response.status_code, 200)
        labels = [item["label"] for item in timeline_response.data]
        self.assertIn("Lab result recorded", labels)
        self.assertIn("Prerequisite status checked", labels)
        self.assertIn("Audit timeline viewed", labels)

        self.client.force_authenticate(state_admin)
        state_response = self.client.get(f"/api/assessments/{assessment.id}/audit-timeline/")
        self.assertEqual(state_response.status_code, 200)

        self.client.force_authenticate(self.employer_user)
        employer_response = self.client.get(f"/api/assessments/{assessment.id}/audit-timeline/")
        self.assertEqual(employer_response.status_code, 403)

    def test_cross_role_assessment_privacy_and_scope_matrix(self):
        assessment = self._create_decision_ready_assessment()
        assessment.doctor_notes = "Restricted doctor note"
        assessment.decision_draft_notes = "Restricted draft note"
        assessment.digital_signature_hash = "restricted-hash"
        assessment.save(update_fields=["doctor_notes", "decision_draft_notes", "digital_signature_hash", "updated_at"])
        lab_test = LabTest.objects.create(
            assessment=assessment,
            requested_by=self.doctor,
            test_type="stool_microscopy",
            status=LabTestStatus.NEGATIVE,
            result_notes="Restricted lab note",
        )

        other_handler_user = User.objects.create_user(
            username="other-handler",
            email="other-handler@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.state,
        )
        other_handler = FoodHandlerProfile.objects.create(
            user=other_handler_user,
            full_name="Other Handler",
            date_of_birth="1991-01-01",
            gender=Gender.MALE,
            nin="12345678909",
            phone="08030000111",
            email="other@example.com",
            home_address="10 Other Road",
            state=self.state,
            employer=self.employer,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-OTHER001",
        )
        other_assessment = MedicalAssessment.objects.create(
            food_handler=other_handler,
            employer=self.employer,
            facility=self.facility,
            payment_transaction=self.payment,
        )
        other_state = State.objects.create(name="Ogun", code="OG")
        other_state_admin = User.objects.create_user(
            username="other-state-admin",
            email="other-state-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=other_state,
        )
        federal_admin = User.objects.create_user(
            username="federal-privacy",
            email="federal-privacy@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )

        self.client.force_authenticate(self.handler_user)
        handler_list = self.client.get("/api/assessments/")
        self.assertEqual(handler_list.status_code, 200)
        self.assertEqual({row["id"] for row in data(handler_list)}, {str(assessment.id)})
        other_detail = self.client.get(f"/api/assessments/{other_assessment.id}/")
        self.assertEqual(other_detail.status_code, 404)

        self.client.force_authenticate(self.employer_user)
        employer_detail = self.client.get(f"/api/assessments/{assessment.id}/")
        self.assertEqual(employer_detail.status_code, 200)
        employer_payload = data(employer_detail)
        self.assertNotIn("doctor_notes", employer_payload)
        self.assertNotIn("decision_draft_notes", employer_payload)
        self.assertNotIn("digital_signature_hash", employer_payload)
        self.assertNotIn("signed_by", employer_payload)
        self.assertNotIn("lab_tests", employer_payload)

        self.employer_user.employer_staff_role = EmployerStaffRole.FINANCE_USER
        self.employer_user.save(update_fields=["employer_staff_role", "updated_at"])
        finance_detail = self.client.get(f"/api/assessments/{assessment.id}/")
        self.assertEqual(finance_detail.status_code, 200)
        self.assertNotIn("doctor_notes", data(finance_detail))
        self.assertEqual(self.client.get(f"/api/lab-tests/{lab_test.id}/").status_code, 404)

        self.client.force_authenticate(self.other_doctor)
        self.assertEqual(self.client.get(f"/api/doctor/assessments/{assessment.id}/").status_code, 404)
        self.assertEqual(self.client.patch(f"/api/doctor/assessments/{assessment.id}/fitness-decision/", {"final_decision": FitnessDecision.FIT}, format="json").status_code, 404)

        self.client.force_authenticate(self.other_lab_staff)
        self.assertEqual(self.client.patch(f"/api/lab-tests/{lab_test.id}/result/", {"status": LabTestStatus.NEGATIVE}, format="json").status_code, 404)

        self.client.force_authenticate(other_state_admin)
        self.assertEqual(self.client.get(f"/api/assessments/{assessment.id}/").status_code, 404)

        self.client.force_authenticate(federal_admin)
        federal_list = self.client.get("/api/assessments/")
        self.assertEqual(federal_list.status_code, 200)
        self.assertEqual(data(federal_list), [])
        self.assertEqual(self.client.get(f"/api/assessments/{assessment.id}/").status_code, 404)
        self.assertEqual(self.client.get("/api/lab-tests/").status_code, 200)
        self.assertEqual(data(self.client.get("/api/lab-tests/")), [])
        self.assertEqual(data(self.client.get("/api/vaccinations/")), [])

        self.client.force_authenticate(user=None)
        self.assertIn(self.client.get(f"/api/assessments/{assessment.id}/").status_code, {401, 403})
