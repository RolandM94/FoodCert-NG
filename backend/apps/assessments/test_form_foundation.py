from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import UserRole
from apps.assessments.models import (
    AssessmentFormQuestion,
    AssessmentFormScope,
    AssessmentFormSection,
    AssessmentFormTemplate,
    AssessmentFormType,
    AssessmentPrivacyClassification,
    AssessmentQuestionType,
    AssessmentRespondentRole,
)
from apps.assessments.permissions import can_manage_assessment_form_template
from apps.facilities.models import FacilityType, MedicalFacility, OwnershipType
from apps.food_handlers.models import FoodHandlerProfile
from apps.locations.models import State
from apps.organizations.models import Organization, OrganizationType


User = get_user_model()


class AssessmentFormFoundationTests(TestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.facility_org = Organization.objects.create(
            name="Mainland Diagnostics",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.lagos,
        )
        self.other_facility_org = Organization.objects.create(
            name="Ibadan Diagnostics",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.oyo,
        )
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

    def create_template(self, **overrides):
        values = {
            "name": "National Health Declaration",
            "form_type": AssessmentFormType.HEALTH_DECLARATION,
            "scope": AssessmentFormScope.NATIONAL,
            "created_by": self.federal_admin,
        }
        values.update(overrides)
        return AssessmentFormTemplate(**values)

    def test_scope_ownership_rules_are_enforced(self):
        invalid_templates = [
            self.create_template(scope=AssessmentFormScope.NATIONAL, state=self.lagos),
            self.create_template(scope=AssessmentFormScope.STATE),
            self.create_template(scope=AssessmentFormScope.STATE, state=self.lagos, facility=self.facility),
            self.create_template(scope=AssessmentFormScope.FACILITY),
            self.create_template(scope=AssessmentFormScope.FACILITY, facility=self.facility, state=self.oyo),
        ]
        for template in invalid_templates:
            with self.subTest(scope=template.scope, state=template.state_id, facility=template.facility_id):
                with self.assertRaises(ValidationError):
                    template.full_clean()

        valid_templates = [
            self.create_template(scope=AssessmentFormScope.SYSTEM),
            self.create_template(scope=AssessmentFormScope.NATIONAL),
            self.create_template(scope=AssessmentFormScope.STATE, state=self.lagos),
            self.create_template(scope=AssessmentFormScope.FACILITY, state=self.lagos, facility=self.facility),
        ]
        for template in valid_templates:
            with self.subTest(scope=template.scope):
                template.full_clean()

    def test_question_keys_are_unique_across_template_sections(self):
        template = self.create_template()
        template.full_clean()
        template.save()
        first_section = AssessmentFormSection.objects.create(template=template, key="symptoms", title="Symptoms")
        second_section = AssessmentFormSection.objects.create(template=template, key="exposure", title="Exposure")
        AssessmentFormQuestion.objects.create(
            section=first_section,
            key="recent_diarrhoea_vomiting",
            label="Have you experienced diarrhoea or vomiting recently?",
            question_type=AssessmentQuestionType.YES_NO,
            privacy_classification=AssessmentPrivacyClassification.MEDICAL_SENSITIVE,
            respondent_role=AssessmentRespondentRole.FOOD_HANDLER,
        )
        duplicate = AssessmentFormQuestion(
            section=second_section,
            key="recent_diarrhoea_vomiting",
            label="Duplicate meaning",
            question_type=AssessmentQuestionType.YES_NO,
            privacy_classification=AssessmentPrivacyClassification.MEDICAL_SENSITIVE,
            respondent_role=AssessmentRespondentRole.FOOD_HANDLER,
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_approved_question_types_and_privacy_classifications_include_medical_controls(self):
        self.assertIn(AssessmentQuestionType.BLOOD_PRESSURE, AssessmentQuestionType.values)
        self.assertIn(AssessmentQuestionType.DOCTOR_ONLY_NOTE, AssessmentQuestionType.values)
        self.assertIn(AssessmentPrivacyClassification.MEDICAL_SENSITIVE, AssessmentPrivacyClassification.values)
        self.assertIn(AssessmentPrivacyClassification.RESTRICTED_MEDICAL, AssessmentPrivacyClassification.values)

    def test_dynamic_questions_do_not_extend_food_handler_registration_profile(self):
        registration_fields = {field.name for field in FoodHandlerProfile._meta.get_fields()}
        self.assertNotIn("recent_diarrhoea_vomiting", registration_fields)
        self.assertNotIn("doctor_only_note", registration_fields)
        self.assertNotIn("lab_result_status", registration_fields)

    def test_scope_permissions_match_template_ownership(self):
        national = self.create_template(scope=AssessmentFormScope.NATIONAL)
        state = self.create_template(scope=AssessmentFormScope.STATE, state=self.lagos)
        facility = self.create_template(scope=AssessmentFormScope.FACILITY, state=self.lagos, facility=self.facility)
        system = self.create_template(scope=AssessmentFormScope.SYSTEM)

        self.assertTrue(can_manage_assessment_form_template(self.super_admin, system))
        self.assertTrue(can_manage_assessment_form_template(self.federal_admin, national))
        self.assertFalse(can_manage_assessment_form_template(self.federal_admin, state))
        self.assertTrue(can_manage_assessment_form_template(self.state_admin, state))
        self.assertFalse(can_manage_assessment_form_template(self.other_state_admin, state))
        self.assertTrue(can_manage_assessment_form_template(self.facility_admin, facility))
        self.assertFalse(can_manage_assessment_form_template(self.other_facility_admin, facility))
