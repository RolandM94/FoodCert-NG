from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.assessments.models import (
    AssessmentFormQuestion,
    AssessmentFormScope,
    AssessmentFormSection,
    AssessmentFormStatus,
    AssessmentFormTemplate,
    AssessmentFormType,
    AssessmentPrivacyClassification,
    AssessmentQuestionType,
    AssessmentRespondentRole,
)
from apps.audit.models import AuditLog
from apps.facilities.models import FacilityType, MedicalFacility, OwnershipType
from apps.locations.models import State
from apps.notifications.models import Notification
from apps.organizations.models import Organization, OrganizationType


User = get_user_model()


def payload(response):
    return response.data.get("data", response.data) if isinstance(response.data, dict) else response.data


class AssessmentFormLifecycleApiTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.facility_org = Organization.objects.create(name="Mainland Diagnostics", organization_type=OrganizationType.MEDICAL_FACILITY, state=self.lagos)
        self.other_facility_org = Organization.objects.create(name="Ibadan Diagnostics", organization_type=OrganizationType.MEDICAL_FACILITY, state=self.oyo)
        self.facility = self.create_facility(self.facility_org, self.lagos, "MD-001")
        self.other_facility = self.create_facility(self.other_facility_org, self.oyo, "ID-001")
        self.super_admin = User.objects.create_user("super", "super@example.com", "StrongPass123!", role=UserRole.SUPER_ADMIN)
        self.federal_admin = User.objects.create_user("federal", "federal@example.com", "StrongPass123!", role=UserRole.FEDERAL_ADMIN)
        self.state_admin = User.objects.create_user("lagos-state", "lagos-state@example.com", "StrongPass123!", role=UserRole.STATE_ADMIN, state=self.lagos)
        self.other_state_admin = User.objects.create_user("oyo-state", "oyo-state@example.com", "StrongPass123!", role=UserRole.STATE_ADMIN, state=self.oyo)
        self.facility_admin = User.objects.create_user("facility", "facility@example.com", "StrongPass123!", role=UserRole.FACILITY_ADMIN, organization=self.facility_org, state=self.lagos)
        self.other_facility_admin = User.objects.create_user("other-facility", "other-facility@example.com", "StrongPass123!", role=UserRole.FACILITY_ADMIN, organization=self.other_facility_org, state=self.oyo)

    @staticmethod
    def create_facility(organization, state, license_number):
        return MedicalFacility.objects.create(
            organization=organization,
            facility_name=organization.name,
            facility_type=FacilityType.DIAGNOSTIC_CENTRE,
            ownership_type=OwnershipType.PRIVATE,
            license_number=license_number,
            address="12 Health Road",
            state=state,
            contact_person="Medical Director",
            phone="08030000000",
            email=f"{license_number.lower()}@example.com",
        )

    def create_national_template(self):
        self.client.force_authenticate(self.federal_admin)
        response = self.client.post(
            "/api/forms/templates/",
            {
                "name": "National Health Declaration",
                "description": "National minimum declaration.",
                "form_type": "health_declaration",
                "scope": "national",
                "is_mandatory": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        return payload(response)

    def add_section_and_question(self, template_id):
        section = self.client.post(
            "/api/forms/sections/",
            {"template": template_id, "key": "symptoms", "title": "Symptoms", "sort_order": 1},
            format="json",
        )
        self.assertEqual(section.status_code, 201, section.data)
        question = self.client.post(
            "/api/forms/questions/",
            {
                "section": payload(section)["id"],
                "key": "recent_diarrhoea_vomiting",
                "label": "Have you experienced diarrhoea or vomiting recently?",
                "question_type": "yes_no",
                "privacy_classification": "medical_sensitive",
                "respondent_role": "food_handler",
                "required": True,
            },
            format="json",
        )
        self.assertEqual(question.status_code, 201, question.data)
        return payload(section), payload(question)

    def publish_template(self, template_id):
        for action, expected_status in [
            ("submit-for-approval", AssessmentFormStatus.PENDING_APPROVAL),
            ("approve", AssessmentFormStatus.APPROVED),
            ("publish", AssessmentFormStatus.PUBLISHED),
            ("activate", AssessmentFormStatus.ACTIVE),
        ]:
            response = self.client.post(f"/api/forms/templates/{template_id}/{action}/", format="json")
            self.assertEqual(response.status_code, 200, response.data)
            self.assertEqual(payload(response)["status"], expected_status)

    def test_federal_admin_can_build_preview_and_publish_national_template(self):
        template = self.create_national_template()
        section, question = self.add_section_and_question(template["id"])

        preview = self.client.get(f"/api/forms/templates/{template['id']}/preview/")
        self.assertEqual(preview.status_code, 200)
        self.assertEqual(payload(preview)["sections"][0]["id"], section["id"])
        self.assertEqual(payload(preview)["sections"][0]["questions"][0]["id"], question["id"])

        self.publish_template(template["id"])
        self.assertTrue(AuditLog.objects.filter(target_id=template["id"], metadata__event="assessment_form_activated").exists())

    def test_published_template_and_nested_content_are_immutable(self):
        template = self.create_national_template()
        section, _ = self.add_section_and_question(template["id"])
        self.publish_template(template["id"])

        template_edit = self.client.patch(f"/api/forms/templates/{template['id']}/", {"name": "Changed"}, format="json")
        section_edit = self.client.patch(f"/api/forms/sections/{section['id']}/", {"title": "Changed"}, format="json")
        question_create = self.client.post(
            "/api/forms/questions/",
            {
                "section": section["id"],
                "key": "late_question",
                "label": "This must not be added",
                "question_type": "yes_no",
                "privacy_classification": "medical_sensitive",
                "respondent_role": "food_handler",
            },
            format="json",
        )

        self.assertEqual(template_edit.status_code, 400)
        self.assertEqual(section_edit.status_code, 400)
        self.assertEqual(question_create.status_code, 400)

    def test_duplicate_creates_editable_deep_copy_and_version_history(self):
        template = self.create_national_template()
        self.add_section_and_question(template["id"])
        self.publish_template(template["id"])

        duplicated = self.client.post(f"/api/forms/templates/{template['id']}/duplicate/", format="json")
        self.assertEqual(duplicated.status_code, 201, duplicated.data)
        duplicate = payload(duplicated)
        self.assertEqual(duplicate["version"], 2)
        self.assertEqual(duplicate["status"], AssessmentFormStatus.DRAFT)
        self.assertEqual(len(duplicate["sections"]), 1)
        self.assertEqual(len(duplicate["sections"][0]["questions"]), 1)

        edited = self.client.patch(f"/api/forms/templates/{duplicate['id']}/", {"name": "National Health Declaration Updated"}, format="json")
        self.assertEqual(edited.status_code, 200)
        versions = self.client.get(f"/api/forms/templates/{duplicate['id']}/versions/")
        self.assertEqual(versions.status_code, 200)
        self.assertEqual([item["version"] for item in payload(versions)], [1, 2])

    def test_state_and_facility_scope_permissions_are_enforced(self):
        self.client.force_authenticate(self.state_admin)
        blocked_national = self.client.post(
            "/api/forms/templates/",
            {"name": "Blocked", "form_type": "health_declaration", "scope": "national"},
            format="json",
        )
        self.assertEqual(blocked_national.status_code, 403)
        state_form = self.client.post(
            "/api/forms/templates/",
            {"name": "Lagos Addendum", "form_type": "health_declaration", "scope": "state", "state": str(self.lagos.id)},
            format="json",
        )
        self.assertEqual(state_form.status_code, 201, state_form.data)

        self.client.force_authenticate(self.facility_admin)
        facility_form = self.client.post(
            "/api/forms/templates/",
            {"name": "Facility Intake", "form_type": "facility_intake", "scope": "facility", "facility": str(self.facility.id), "requires_approval": True},
            format="json",
        )
        self.assertEqual(facility_form.status_code, 201, facility_form.data)
        form_id = payload(facility_form)["id"]
        submitted = self.client.post(f"/api/forms/templates/{form_id}/submit-for-approval/", format="json")
        self.assertEqual(submitted.status_code, 200)

        self.client.force_authenticate(self.other_facility_admin)
        self.assertEqual(self.client.get(f"/api/forms/templates/{form_id}/").status_code, 404)

        self.client.force_authenticate(self.state_admin)
        approved = self.client.post(f"/api/forms/templates/{form_id}/approve/", format="json")
        self.assertEqual(approved.status_code, 200, approved.data)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.facility_admin,
                related_object_id=form_id,
                title="Facility form approved",
            ).exists()
        )

    def test_facility_form_state_change_request_resubmission_and_publishing_flow(self):
        self.client.force_authenticate(self.facility_admin)
        created = self.client.post(
            "/api/forms/templates/",
            {
                "name": "Facility Intake",
                "description": "Supplementary intake questions for local workflow.",
                "form_type": "facility_intake",
                "scope": "facility",
                "facility": str(self.facility.id),
                "requires_approval": True,
            },
            format="json",
        )
        self.assertEqual(created.status_code, 201, created.data)
        form_id = payload(created)["id"]
        self.add_section_and_question(form_id)
        submitted = self.client.post(f"/api/forms/templates/{form_id}/submit-for-approval/", format="json")
        self.assertEqual(submitted.status_code, 200, submitted.data)
        self.assertEqual(payload(submitted)["status"], AssessmentFormStatus.PENDING_APPROVAL)
        blocked_publish = self.client.post(f"/api/forms/templates/{form_id}/publish/", format="json")
        self.assertEqual(blocked_publish.status_code, 403)

        self.client.force_authenticate(self.state_admin)
        changes = self.client.post(
            f"/api/forms/templates/{form_id}/request-changes/",
            {"reason": "Clarify why this intake question is needed."},
            format="json",
        )
        self.assertEqual(changes.status_code, 200, changes.data)
        self.assertEqual(payload(changes)["status"], AssessmentFormStatus.CHANGES_REQUESTED)
        self.assertEqual(payload(changes)["review_comment"], "Clarify why this intake question is needed.")
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.facility_admin,
                related_object_id=form_id,
                title="Facility form changes requested",
            ).exists()
        )

        self.client.force_authenticate(self.facility_admin)
        edited = self.client.patch(f"/api/forms/templates/{form_id}/", {"description": "Reviewed intake purpose."}, format="json")
        self.assertEqual(edited.status_code, 200, edited.data)
        resubmitted = self.client.post(f"/api/forms/templates/{form_id}/submit-for-approval/", format="json")
        self.assertEqual(resubmitted.status_code, 200, resubmitted.data)

        self.client.force_authenticate(self.state_admin)
        approved = self.client.post(f"/api/forms/templates/{form_id}/approve/", format="json")
        self.assertEqual(approved.status_code, 200, approved.data)
        self.assertEqual(payload(approved)["status"], AssessmentFormStatus.APPROVED)
        published = self.client.post(f"/api/forms/templates/{form_id}/publish/", format="json")
        self.assertEqual(published.status_code, 200, published.data)
        self.assertEqual(payload(published)["status"], AssessmentFormStatus.PUBLISHED)
        activated = self.client.post(f"/api/forms/templates/{form_id}/activate/", format="json")
        self.assertEqual(payload(activated)["status"], AssessmentFormStatus.ACTIVE)

    def test_facility_form_rejection_returns_to_editable_resubmittable_state(self):
        self.client.force_authenticate(self.facility_admin)
        created = self.client.post(
            "/api/forms/templates/",
            {"name": "Facility Intake", "form_type": "facility_intake", "scope": "facility", "facility": str(self.facility.id)},
            format="json",
        )
        form_id = payload(created)["id"]
        self.add_section_and_question(form_id)
        self.client.post(f"/api/forms/templates/{form_id}/submit-for-approval/", format="json")

        self.client.force_authenticate(self.state_admin)
        rejected = self.client.post(f"/api/forms/templates/{form_id}/reject/", {"reason": "Unclear purpose."}, format="json")
        self.assertEqual(rejected.status_code, 200, rejected.data)
        self.assertEqual(payload(rejected)["status"], AssessmentFormStatus.REJECTED)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.facility_admin,
                related_object_id=form_id,
                title="Facility form rejected",
            ).exists()
        )
        self.assertEqual(payload(rejected)["review_comment"], "Unclear purpose.")

        self.client.force_authenticate(self.facility_admin)
        edited = self.client.patch(f"/api/forms/templates/{form_id}/", {"description": "Purpose now documented."}, format="json")
        self.assertEqual(edited.status_code, 200, edited.data)
        resubmitted = self.client.post(f"/api/forms/templates/{form_id}/submit-for-approval/", format="json")
        self.assertEqual(payload(resubmitted)["status"], AssessmentFormStatus.PENDING_APPROVAL)

    def test_state_cannot_approve_facility_forms_that_conflict_or_expose_answers_to_employers(self):
        official = AssessmentFormTemplate.objects.create(
            name="Mandatory National Declaration",
            form_type=AssessmentFormType.HEALTH_DECLARATION,
            scope=AssessmentFormScope.NATIONAL,
            status=AssessmentFormStatus.ACTIVE,
            is_mandatory=True,
        )
        official_section = AssessmentFormSection.objects.create(template=official, key="mandatory", title="Mandatory")
        AssessmentFormQuestion.objects.create(
            section=official_section,
            key="recent_diarrhoea_vomiting",
            label="Have you experienced diarrhoea or vomiting recently?",
            question_type=AssessmentQuestionType.YES_NO,
            privacy_classification=AssessmentPrivacyClassification.MEDICAL_SENSITIVE,
            respondent_role=AssessmentRespondentRole.FOOD_HANDLER,
        )

        self.client.force_authenticate(self.facility_admin)
        duplicate = self.client.post(
            "/api/forms/templates/",
            {"name": "Duplicate Facility Intake", "form_type": "facility_intake", "scope": "facility", "facility": str(self.facility.id)},
            format="json",
        )
        duplicate_id = payload(duplicate)["id"]
        self.add_section_and_question(duplicate_id)
        self.client.post(f"/api/forms/templates/{duplicate_id}/submit-for-approval/", format="json")

        visible = self.client.post(
            "/api/forms/templates/",
            {"name": "Employer Visible Intake", "form_type": "facility_intake", "scope": "facility", "facility": str(self.facility.id)},
            format="json",
        )
        visible_id = payload(visible)["id"]
        section = self.client.post("/api/forms/sections/", {"template": visible_id, "key": "visibility", "title": "Visibility"}, format="json")
        question = self.client.post(
            "/api/forms/questions/",
            {
                "section": payload(section)["id"],
                "key": "local_screening_note",
                "label": "Local screening note",
                "question_type": "long_text",
                "privacy_classification": "employer_safe_summary",
                "respondent_role": "food_handler",
            },
            format="json",
        )
        self.assertEqual(question.status_code, 201, question.data)
        self.client.post(f"/api/forms/templates/{visible_id}/submit-for-approval/", format="json")

        self.client.force_authenticate(self.state_admin)
        duplicate_approval = self.client.post(f"/api/forms/templates/{duplicate_id}/approve/", format="json")
        self.assertEqual(duplicate_approval.status_code, 400)
        self.assertIn("question:recent_diarrhoea_vomiting", payload(duplicate_approval))
        visible_approval = self.client.post(f"/api/forms/templates/{visible_id}/approve/", format="json")
        self.assertEqual(visible_approval.status_code, 400)
        self.assertIn("question:local_screening_note", payload(visible_approval))

    def test_rejected_template_returns_to_editable_state(self):
        template = self.create_national_template()
        submitted = self.client.post(f"/api/forms/templates/{template['id']}/submit-for-approval/", format="json")
        self.assertEqual(submitted.status_code, 200)
        rejected = self.client.post(f"/api/forms/templates/{template['id']}/reject/", {"reason": "Clarify wording."}, format="json")
        self.assertEqual(rejected.status_code, 200)
        self.assertEqual(payload(rejected)["status"], AssessmentFormStatus.REJECTED)
        edited = self.client.patch(f"/api/forms/templates/{template['id']}/", {"description": "Revised wording."}, format="json")
        self.assertEqual(edited.status_code, 200)

    def test_builder_returns_field_errors_for_invalid_question_keys(self):
        template = self.create_national_template()
        first_section, _ = self.add_section_and_question(template["id"])
        second_section = self.client.post(
            "/api/forms/sections/",
            {"template": template["id"], "key": "exposure", "title": "Exposure"},
            format="json",
        )
        self.assertEqual(second_section.status_code, 201)
        duplicate = self.client.post(
            "/api/forms/questions/",
            {
                "section": payload(second_section)["id"],
                "key": "recent_diarrhoea_vomiting",
                "label": "Duplicate key",
                "question_type": "yes_no",
                "privacy_classification": "medical_sensitive",
                "respondent_role": "food_handler",
            },
            format="json",
        )
        self.assertEqual(duplicate.status_code, 400)
        self.assertIn("key", payload(duplicate))
        self.assertNotEqual(first_section["id"], payload(second_section)["id"])
