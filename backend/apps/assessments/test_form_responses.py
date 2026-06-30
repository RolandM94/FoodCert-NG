from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.assessments.models import (
    AssessmentFormQuestion,
    AssessmentFormResponse,
    AssessmentFormResponseStatus,
    AssessmentFormScope,
    AssessmentFormSection,
    AssessmentFormStatus,
    AssessmentFormTemplateSnapshot,
    AssessmentFormTemplate,
    AssessmentFormType,
    AssessmentPrivacyClassification,
    AssessmentQuestionType,
    AssessmentRequirementSet,
    AssessmentRequirementSetStatus,
    AssessmentRespondentRole,
    HealthDeclaration,
    MedicalAssessment,
    StepStatus,
)
from apps.assessments.services import AssessmentFormResponseService, AssessmentRequirementResolutionService, AssessmentService
from apps.audit.models import AuditAction, AuditLog
from apps.employers.models import Employer, EstablishmentCategory
from apps.facilities.models import AccreditationStatus, FacilityType, MedicalFacility, OwnershipType
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, Gender
from apps.locations.models import State
from apps.notifications.models import Notification
from apps.organizations.models import Organization, OrganizationType


User = get_user_model()


def payload(response):
    return response.data.get("data", response.data) if isinstance(response.data, dict) else response.data


class AssessmentFormResponseApiTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.facility_org = Organization.objects.create(
            name="Mainland Diagnostics",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.lagos,
        )
        self.facility = MedicalFacility.objects.create(
            organization=self.facility_org,
            facility_name="Mainland Diagnostics",
            facility_type=FacilityType.DIAGNOSTIC_CENTRE,
            ownership_type=OwnershipType.PRIVATE,
            license_number="MD-001",
            address="12 Health Road",
            state=self.lagos,
            contact_person="Medical Director",
            phone="08030000000",
            email="mainland@example.com",
            accreditation_status=AccreditationStatus.APPROVED,
            accreditation_expiry_date=timezone.localdate() + timezone.timedelta(days=365),
        )
        self.handler_user = User.objects.create_user("handler", "handler@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.lagos)
        self.other_handler_user = User.objects.create_user("other", "other@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.lagos)
        self.doctor = User.objects.create_user("doctor", "doctor@example.com", "StrongPass123!", role=UserRole.DOCTOR, organization=self.facility_org, state=self.lagos)
        self.state_admin = User.objects.create_user("state", "state@example.com", "StrongPass123!", role=UserRole.STATE_ADMIN, state=self.lagos)
        self.inspector = User.objects.create_user("inspector", "inspector@example.com", "StrongPass123!", role=UserRole.INSPECTOR, state=self.lagos)
        self.federal_admin = User.objects.create_user("federal", "federal@example.com", "StrongPass123!", role=UserRole.FEDERAL_ADMIN)
        self.employer_user = User.objects.create_user("employer", "employer@example.com", "StrongPass123!", role=UserRole.EMPLOYER, state=self.lagos)
        self.employer = Employer.objects.create(
            user=self.employer_user,
            business_name="MegaChow",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Operations Lead",
            contact_person_phone="08030000008",
            contact_person_email="ops@megachow.example.com",
            address="10 Kitchen Road",
            state=self.lagos,
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
            system_identifier="FCN-RESP-001",
        )
        self.template = AssessmentFormTemplate.objects.create(
            name="National Health Declaration",
            form_type=AssessmentFormType.HEALTH_DECLARATION,
            scope=AssessmentFormScope.NATIONAL,
            version=3,
            status=AssessmentFormStatus.ACTIVE,
            is_mandatory=True,
        )
        self.section = AssessmentFormSection.objects.create(template=self.template, key="symptoms", title="Symptoms")
        self.question = AssessmentFormQuestion.objects.create(
            section=self.section,
            key="recent_fever",
            label="Have you experienced a recent fever?",
            question_type=AssessmentQuestionType.YES_NO,
            privacy_classification=AssessmentPrivacyClassification.MEDICAL_SENSITIVE,
            respondent_role=AssessmentRespondentRole.FOOD_HANDLER,
            required=True,
        )
        requirement_set = AssessmentRequirementSet.objects.create(
            name="National Baseline",
            scope=AssessmentFormScope.NATIONAL,
            status=AssessmentRequirementSetStatus.ACTIVE,
        )
        requirement_set.required_forms.add(self.template)
        self.assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
        )

    def assign(self):
        [response] = AssessmentRequirementResolutionService.assign_forms(assessment=self.assessment, actor=self.handler_user)
        return response

    def add_question(self, key, question_type, **overrides):
        values = {
            "section": self.section,
            "key": key,
            "label": key.replace("_", " ").title(),
            "question_type": question_type,
            "privacy_classification": AssessmentPrivacyClassification.MEDICAL_SENSITIVE,
            "respondent_role": AssessmentRespondentRole.FOOD_HANDLER,
        }
        values.update(overrides)
        return AssessmentFormQuestion.objects.create(**values)

    def test_assignment_is_idempotent_and_snapshots_exact_template_version(self):
        response = self.assign()
        second = self.assign()

        self.assertEqual(response.id, second.id)
        self.assertEqual(AssessmentFormResponse.objects.count(), 1)
        self.assertEqual(response.template_version, 3)
        self.assertEqual(response.respondent, self.handler_user)
        self.assertEqual(response.respondent_role, AssessmentRespondentRole.FOOD_HANDLER)
        self.assertEqual(response.question_snapshot["sections"][0]["questions"][0]["key"], "recent_fever")

    def test_assessment_creation_assigns_current_resolved_forms(self):
        created = AssessmentService.create_assessment(
            food_handler=self.food_handler,
            facility=self.facility,
            actor=self.handler_user,
        )

        assigned = created.form_responses.get()
        self.assertEqual(assigned.template, self.template)
        self.assertEqual(assigned.status, AssessmentFormResponseStatus.NOT_STARTED)

    def test_draft_submission_locks_response_and_blocks_further_edits(self):
        response = self.assign()
        self.client.force_authenticate(self.handler_user)

        draft = self.client.patch(
            f"/api/assessment-form-responses/{response.id}/",
            {"response_data": {"recent_fever": False}},
            format="json",
        )
        self.assertEqual(draft.status_code, 200, draft.data)
        self.assertEqual(payload(draft)["status"], AssessmentFormResponseStatus.DRAFT)

        submitted = self.client.post(f"/api/assessment-form-responses/{response.id}/submit/", format="json")
        self.assertEqual(submitted.status_code, 200, submitted.data)
        self.assertEqual(payload(submitted)["status"], AssessmentFormResponseStatus.SUBMITTED)
        self.assertTrue(payload(submitted)["is_locked"])

        locked = self.client.patch(
            f"/api/assessment-form-responses/{response.id}/",
            {"response_data": {"recent_fever": True}},
            format="json",
        )
        self.assertEqual(locked.status_code, 400)

    def test_reopen_supersedes_submitted_response_and_preserves_historical_snapshot(self):
        response = self.assign()
        AssessmentFormResponseService.save_draft(response=response, response_data={"recent_fever": False}, actor=self.handler_user)
        AssessmentFormResponseService.submit(response=response, actor=self.handler_user)
        original_snapshot = response.question_snapshot
        self.question.label = "This template changed after assignment"
        self.question.save(update_fields=["label", "updated_at"])

        self.client.force_authenticate(self.doctor)
        reopened = self.client.post(
            f"/api/assessment-form-responses/{response.id}/reopen/",
            {"reason": "Please confirm the symptom history."},
            format="json",
        )

        self.assertEqual(reopened.status_code, 201, reopened.data)
        reopened_data = payload(reopened)
        response.refresh_from_db()
        self.assertEqual(response.status, AssessmentFormResponseStatus.SUPERSEDED)
        self.assertTrue(response.is_locked)
        self.assertEqual(reopened_data["status"], AssessmentFormResponseStatus.REOPENED)
        self.assertEqual(reopened_data["version"], 2)
        self.assertEqual(str(reopened_data["previous_response"]), str(response.id))
        self.assertEqual(reopened_data["question_snapshot"], original_snapshot)

        self.client.force_authenticate(self.handler_user)
        resubmitted = self.client.post(f"/api/assessment-form-responses/{reopened_data['id']}/submit/", format="json")
        self.assertEqual(payload(resubmitted)["status"], AssessmentFormResponseStatus.RESUBMITTED)

    def test_assigned_doctor_can_validate_and_unrelated_handler_cannot_access_response(self):
        response = self.assign()
        AssessmentFormResponseService.save_draft(response=response, response_data={"recent_fever": False}, actor=self.handler_user)
        AssessmentFormResponseService.submit(response=response, actor=self.handler_user)

        self.client.force_authenticate(self.doctor)
        validated = self.client.post(f"/api/assessment-form-responses/{response.id}/validate/", format="json")
        self.assertEqual(validated.status_code, 200, validated.data)
        self.assertEqual(payload(validated)["status"], AssessmentFormResponseStatus.VALIDATED)

        self.client.force_authenticate(self.other_handler_user)
        hidden = self.client.get(f"/api/assessment-form-responses/{response.id}/")
        self.assertEqual(hidden.status_code, 404)

    def test_submission_validates_medical_fields_and_preserves_invalid_draft(self):
        self.add_question(
            "temperature",
            AssessmentQuestionType.TEMPERATURE,
            required=True,
            validation_rules={"min_value": 35, "max_value": 42},
        )
        self.add_question("blood_pressure", AssessmentQuestionType.BLOOD_PRESSURE, required=True)
        response = self.assign()
        self.client.force_authenticate(self.handler_user)
        draft_data = {"recent_fever": False, "temperature": 44, "blood_pressure": {"systolic": 0, "diastolic": 80}}
        self.client.patch(f"/api/assessment-form-responses/{response.id}/", {"response_data": draft_data}, format="json")

        invalid = self.client.post(f"/api/assessment-form-responses/{response.id}/submit/", format="json")

        self.assertEqual(invalid.status_code, 400)
        self.assertIn("temperature", payload(invalid))
        self.assertIn("blood_pressure", payload(invalid))
        response.refresh_from_db()
        self.assertEqual(response.status, AssessmentFormResponseStatus.DRAFT)
        self.assertEqual(response.response_data, draft_data)

        self.client.patch(
            f"/api/assessment-form-responses/{response.id}/",
            {"response_data": {"recent_fever": False, "temperature": 36.8, "blood_pressure": {"systolic": 120, "diastolic": 80}}},
            format="json",
        )
        submitted = self.client.post(f"/api/assessment-form-responses/{response.id}/submit/", format="json")
        self.assertEqual(submitted.status_code, 200, submitted.data)

    def test_conditional_visibility_and_required_logic_are_enforced(self):
        self.add_question(
            "symptom_start_date",
            AssessmentQuestionType.DATE,
            conditional_logic={
                "visible_if": {"question": "recent_fever", "operator": "equals", "value": True},
                "required_if": {"question": "recent_fever", "operator": "equals", "value": True},
            },
        )
        response = self.assign()
        self.client.force_authenticate(self.handler_user)
        self.client.patch(f"/api/assessment-form-responses/{response.id}/", {"response_data": {"recent_fever": True}}, format="json")

        missing_conditional = self.client.post(f"/api/assessment-form-responses/{response.id}/submit/", format="json")

        self.assertEqual(missing_conditional.status_code, 400)
        self.assertIn("symptom_start_date", payload(missing_conditional))

        self.client.patch(
            f"/api/assessment-form-responses/{response.id}/",
            {"response_data": {"recent_fever": True, "symptom_start_date": "2026-06-01"}},
            format="json",
        )
        submitted = self.client.post(f"/api/assessment-form-responses/{response.id}/submit/", format="json")
        self.assertEqual(submitted.status_code, 200, submitted.data)

    def test_publishing_rejects_broken_conditional_logic(self):
        self.template.status = AssessmentFormStatus.APPROVED
        self.template.save(update_fields=["status", "updated_at"])
        self.question.conditional_logic = {
            "visible_if": {"question": "missing_question", "operator": "equals", "value": True},
        }
        self.question.save(update_fields=["conditional_logic", "updated_at"])
        self.client.force_authenticate(self.federal_admin)

        published = self.client.post(f"/api/assessment-forms/templates/{self.template.id}/publish/", format="json")

        self.assertEqual(published.status_code, 400)
        self.assertIn("question:recent_fever", payload(published))
        self.template.refresh_from_db()
        self.assertEqual(self.template.status, AssessmentFormStatus.APPROVED)

    def test_submission_generates_review_flags_without_making_clinical_decision(self):
        self.question.risk_flag_rules = {
            "when": {"use_current_answer": True, "operator": "equals", "value": True},
            "flags": ["medical_review_required", "lab_test_required", "temporary_exclusion_recommended"],
        }
        self.question.save(update_fields=["risk_flag_rules", "updated_at"])
        response = self.assign()
        self.client.force_authenticate(self.handler_user)
        self.client.patch(f"/api/assessment-form-responses/{response.id}/", {"response_data": {"recent_fever": True}}, format="json")

        submitted = self.client.post(f"/api/assessment-form-responses/{response.id}/submit/", format="json")

        self.assertEqual(submitted.status_code, 200, submitted.data)
        self.assertEqual(
            payload(submitted)["risk_flags"],
            ["lab_test_required", "medical_review_required", "temporary_exclusion_recommended"],
        )
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.final_decision, "pending")

    def test_employer_and_inspector_receive_operational_summary_without_medical_payload(self):
        self.question.risk_flag_rules = {
            "when": {"use_current_answer": True, "operator": "equals", "value": True},
            "flags": ["medical_review_required"],
        }
        self.question.save(update_fields=["risk_flag_rules", "updated_at"])
        response = self.assign()
        AssessmentFormResponseService.save_draft(response=response, response_data={"recent_fever": True}, actor=self.handler_user)
        AssessmentFormResponseService.submit(response=response, actor=self.handler_user)

        for actor in [self.employer_user, self.inspector]:
            self.client.force_authenticate(actor)
            detail = self.client.get(f"/api/assessment-form-responses/{response.id}/")
            self.assertEqual(detail.status_code, 200, detail.data)
            data = payload(detail)
            self.assertEqual(data["status"], AssessmentFormResponseStatus.SUBMITTED)
            self.assertNotIn("response_data", data)
            self.assertNotIn("question_snapshot", data)
            self.assertNotIn("risk_flags", data)
            self.assertNotIn("respondent", data)

    def test_sensitive_response_detail_access_is_audited(self):
        response = self.assign()
        AssessmentFormResponseService.save_draft(response=response, response_data={"recent_fever": False}, actor=self.handler_user)

        self.client.force_authenticate(self.doctor)
        detail = self.client.get(f"/api/assessment-form-responses/{response.id}/")

        self.assertEqual(detail.status_code, 200, detail.data)
        self.assertIn("response_data", payload(detail))
        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditAction.MEDICAL_RECORD_ACCESS,
                target_id=str(response.id),
                metadata__event="assessment_form_response_read",
            ).exists()
        )

    def test_form_analytics_returns_aggregate_counts_without_answers(self):
        response = self.assign()
        AssessmentFormResponseService.save_draft(response=response, response_data={"recent_fever": False}, actor=self.handler_user)
        AssessmentFormResponseService.submit(response=response, actor=self.handler_user)

        self.client.force_authenticate(self.state_admin)
        analytics = self.client.get("/api/assessment-forms/analytics/")

        self.assertEqual(analytics.status_code, 200, analytics.data)
        data = payload(analytics)
        self.assertEqual(data["total_responses"], 1)
        self.assertEqual(data["submitted_responses"], 1)
        self.assertEqual(data["completion_rate"], 100)
        self.assertEqual(data["status_counts"][AssessmentFormResponseStatus.SUBMITTED], 1)
        self.assertNotIn("response_data", str(data))
        self.assertEqual(data["usage_by_template"][0]["name"], self.template.name)

    def test_form_assignment_submission_and_reopen_create_notifications(self):
        response = self.assign()
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.handler_user,
                related_object_id=response.id,
                title="Assessment form assigned",
            ).exists()
        )

        AssessmentFormResponseService.save_draft(response=response, response_data={"recent_fever": False}, actor=self.handler_user)
        AssessmentFormResponseService.submit(response=response, actor=self.handler_user)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.doctor,
                related_object_id=response.id,
                title="Assessment form submitted",
            ).exists()
        )

        reopened = AssessmentFormResponseService.reopen(response=response, actor=self.doctor, reason="Please clarify.")
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.handler_user,
                related_object_id=reopened.id,
                title="Assessment form requires clarification",
            ).exists()
        )

    def test_declaration_endpoint_creates_merged_snapshot_and_dynamic_form_response(self):
        self.client.force_authenticate(self.handler_user)

        response = self.client.get(f"/api/assessments/{self.assessment.id}/declaration/")

        self.assertEqual(response.status_code, 200, response.data)
        data = payload(response)
        self.assertTrue(HealthDeclaration.objects.filter(assessment=self.assessment).exists())
        snapshot = AssessmentFormTemplateSnapshot.objects.get(assessment=self.assessment)
        self.assertEqual(data["template_snapshot"], str(snapshot.id))
        self.assertEqual(data["merged_schema"]["template_id"], str(self.template.id))
        self.assertEqual(data["form_response_status"], AssessmentFormResponseStatus.NOT_STARTED)
        merged_audit = AuditLog.objects.get(
            target_id=str(self.assessment.id),
            metadata__event="final_merged_form_generated",
        )
        self.assertEqual(merged_audit.metadata["template_snapshot_id"], str(snapshot.id))

    def test_dynamic_declaration_submission_validation_and_reopen_stay_in_sync_with_legacy_record(self):
        self.question.risk_flag_rules = {
            "when": {"use_current_answer": True, "operator": "equals", "value": True},
            "flags": ["medical_review_required"],
        }
        self.question.save(update_fields=["risk_flag_rules", "updated_at"])
        self.client.force_authenticate(self.handler_user)

        draft = self.client.patch(
            f"/api/assessments/{self.assessment.id}/declaration/",
            {"response_data": {"recent_fever": True, "certified_true": False}},
            format="json",
        )
        self.assertEqual(draft.status_code, 200, draft.data)
        self.assertEqual(payload(draft)["response_data"]["recent_fever"], True)
        declaration = HealthDeclaration.objects.get(assessment=self.assessment)
        self.assertTrue(declaration.risk_flag)

        submitted = self.client.post(
            f"/api/assessments/{self.assessment.id}/declaration/submit/",
            {"response_data": {"recent_fever": True}, "certified_true": True},
            format="json",
        )
        self.assertEqual(submitted.status_code, 201, submitted.data)
        submitted_data = payload(submitted)
        self.assertEqual(submitted_data["form_response_status"], AssessmentFormResponseStatus.SUBMITTED)
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.declaration_status, StepStatus.SUBMITTED)
        declaration.refresh_from_db()
        submit_audit = AuditLog.objects.get(
            target_id=str(declaration.id),
            metadata__event="food_handler_declaration_submitted",
        )
        self.assertEqual(submit_audit.metadata["actor_user_id"], str(self.handler_user.id))
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.doctor,
                related_object_id=str(declaration.id),
                title="Health declaration submitted",
            ).exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.doctor,
                related_object_id=str(declaration.id),
                title="High-risk declaration requires validation",
            ).exists()
        )

        self.client.force_authenticate(self.doctor)
        clarification = self.client.patch(
            f"/api/doctor/assessments/{self.assessment.id}/declaration/request-changes/",
            {"reason": "Please confirm the fever timeline."},
            format="json",
        )
        self.assertEqual(clarification.status_code, 200, clarification.data)
        self.assertEqual(payload(clarification)["form_response_status"], AssessmentFormResponseStatus.REOPENED)
        self.assertTrue(
            AuditLog.objects.filter(
                target_id=str(declaration.id),
                metadata__event="doctor_rejected_declaration",
                metadata__reason="Please confirm the fever timeline.",
            ).exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.handler_user,
                related_object_id=str(declaration.id),
                title="Health declaration requires correction",
            ).exists()
        )

        self.client.force_authenticate(self.handler_user)
        resubmitted = self.client.post(
            f"/api/assessments/{self.assessment.id}/declaration/submit/",
            {"response_data": {"recent_fever": False}, "certified_true": True},
            format="json",
        )
        self.assertEqual(resubmitted.status_code, 201, resubmitted.data)
        self.assertEqual(payload(resubmitted)["form_response_status"], AssessmentFormResponseStatus.RESUBMITTED)
        declaration.refresh_from_db()
        self.assertTrue(
            AuditLog.objects.filter(
                target_id=str(declaration.id),
                metadata__event="declaration_corrected",
                new_value__version=declaration.version,
            ).exists()
        )

        self.client.force_authenticate(self.doctor)
        validated = self.client.post(f"/api/assessments/{self.assessment.id}/declaration/validate/", format="json")
        self.assertEqual(validated.status_code, 200, validated.data)
        validated_data = payload(validated)
        self.assertEqual(validated_data["form_response_status"], AssessmentFormResponseStatus.VALIDATED)
        self.assertIsNotNone(validated_data["validated_at"])
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.declaration_status, StepStatus.VALIDATED)
        self.assertTrue(
            AuditLog.objects.filter(
                target_id=str(declaration.id),
                metadata__event="doctor_validated_declaration",
            ).exists()
        )
