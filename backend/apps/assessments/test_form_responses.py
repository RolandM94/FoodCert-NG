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
    AssessmentFormTemplate,
    AssessmentFormType,
    AssessmentPrivacyClassification,
    AssessmentQuestionType,
    AssessmentRequirementSet,
    AssessmentRequirementSetStatus,
    AssessmentRespondentRole,
    MedicalAssessment,
)
from apps.assessments.services import AssessmentFormResponseService, AssessmentRequirementResolutionService, AssessmentService
from apps.facilities.models import AccreditationStatus, FacilityType, MedicalFacility, OwnershipType
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, Gender
from apps.locations.models import State
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
        section = AssessmentFormSection.objects.create(template=self.template, key="symptoms", title="Symptoms")
        self.question = AssessmentFormQuestion.objects.create(
            section=section,
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
            facility=self.facility,
            doctor=self.doctor,
        )

    def assign(self):
        [response] = AssessmentRequirementResolutionService.assign_forms(assessment=self.assessment, actor=self.handler_user)
        return response

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
            f"/api/form-responses/{response.id}/",
            {"response_data": {"recent_fever": False}},
            format="json",
        )
        self.assertEqual(draft.status_code, 200, draft.data)
        self.assertEqual(payload(draft)["status"], AssessmentFormResponseStatus.DRAFT)

        submitted = self.client.post(f"/api/form-responses/{response.id}/submit/", format="json")
        self.assertEqual(submitted.status_code, 200, submitted.data)
        self.assertEqual(payload(submitted)["status"], AssessmentFormResponseStatus.SUBMITTED)
        self.assertTrue(payload(submitted)["is_locked"])

        locked = self.client.patch(
            f"/api/form-responses/{response.id}/",
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
            f"/api/form-responses/{response.id}/reopen/",
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
        resubmitted = self.client.post(f"/api/form-responses/{reopened_data['id']}/submit/", format="json")
        self.assertEqual(payload(resubmitted)["status"], AssessmentFormResponseStatus.RESUBMITTED)

    def test_assigned_doctor_can_validate_and_unrelated_handler_cannot_access_response(self):
        response = self.assign()
        AssessmentFormResponseService.save_draft(response=response, response_data={"recent_fever": False}, actor=self.handler_user)
        AssessmentFormResponseService.submit(response=response, actor=self.handler_user)

        self.client.force_authenticate(self.doctor)
        validated = self.client.post(f"/api/form-responses/{response.id}/validate/", format="json")
        self.assertEqual(validated.status_code, 200, validated.data)
        self.assertEqual(payload(validated)["status"], AssessmentFormResponseStatus.VALIDATED)

        self.client.force_authenticate(self.other_handler_user)
        hidden = self.client.get(f"/api/form-responses/{response.id}/")
        self.assertEqual(hidden.status_code, 404)
