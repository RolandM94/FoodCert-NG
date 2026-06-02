from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.assessments.models import (
    AssessmentFormScope,
    AssessmentFormStatus,
    AssessmentFormTemplate,
    AssessmentFormType,
    AssessmentRequirementSet,
    AssessmentRequirementSetStatus,
    AssessmentType,
    MedicalAssessment,
)
from apps.employers.models import Employer, EstablishmentCategory
from apps.facilities.models import FacilityType, MedicalFacility, OwnershipType
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, Gender
from apps.illness.models import ClearanceStatus, IllnessReport, SuspectedCondition
from apps.locations.models import State
from apps.organizations.models import Organization, OrganizationType


User = get_user_model()


def payload(response):
    return response.data.get("data", response.data) if isinstance(response.data, dict) else response.data


class AssessmentRequirementResolutionApiTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.oyo = State.objects.create(name="Oyo", code="OY")
        self.facility_org = Organization.objects.create(name="Mainland Diagnostics", organization_type=OrganizationType.MEDICAL_FACILITY, state=self.lagos)
        self.other_facility_org = Organization.objects.create(name="Ibadan Diagnostics", organization_type=OrganizationType.MEDICAL_FACILITY, state=self.oyo)
        self.employer_org = Organization.objects.create(name="Clean Foods", organization_type=OrganizationType.EMPLOYER, state=self.lagos)
        self.facility = self.create_facility(self.facility_org, self.lagos, "MD-001")
        self.other_facility = self.create_facility(self.other_facility_org, self.oyo, "ID-001")
        self.super_admin = User.objects.create_user("super", "super@example.com", "StrongPass123!", role=UserRole.SUPER_ADMIN)
        self.federal_admin = User.objects.create_user("federal", "federal@example.com", "StrongPass123!", role=UserRole.FEDERAL_ADMIN)
        self.state_admin = User.objects.create_user("lagos-state", "lagos-state@example.com", "StrongPass123!", role=UserRole.STATE_ADMIN, state=self.lagos)
        self.other_state_admin = User.objects.create_user("oyo-state", "oyo-state@example.com", "StrongPass123!", role=UserRole.STATE_ADMIN, state=self.oyo)
        self.facility_admin = User.objects.create_user("facility", "facility@example.com", "StrongPass123!", role=UserRole.FACILITY_ADMIN, organization=self.facility_org, state=self.lagos)
        self.other_facility_admin = User.objects.create_user("other-facility", "other-facility@example.com", "StrongPass123!", role=UserRole.FACILITY_ADMIN, organization=self.other_facility_org, state=self.oyo)
        self.handler_user = User.objects.create_user("handler", "handler@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.lagos)
        self.other_handler_user = User.objects.create_user("other-handler", "other-handler@example.com", "StrongPass123!", role=UserRole.FOOD_HANDLER, state=self.lagos)
        self.employer_user = User.objects.create_user("employer", "employer@example.com", "StrongPass123!", role=UserRole.EMPLOYER, organization=self.employer_org, state=self.lagos)
        self.employer = Employer.objects.create(
            user=self.employer_user,
            organization=self.employer_org,
            business_name="Clean Foods",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Operations",
            contact_person_phone="08030000001",
            contact_person_email="operations@example.com",
            address="3 Market Road",
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
            system_identifier="FCN-REQ-001",
        )
        self.assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            facility=self.facility,
            assessment_type=AssessmentType.STANDARD,
        )
        self.national_form = self.create_form("National Declaration", AssessmentFormScope.NATIONAL, AssessmentFormType.HEALTH_DECLARATION)
        self.state_form = self.create_form("Lagos Addendum", AssessmentFormScope.STATE, AssessmentFormType.HEALTH_DECLARATION, state=self.lagos)
        self.facility_form = self.create_form("Facility Intake", AssessmentFormScope.FACILITY, AssessmentFormType.FACILITY_INTAKE, state=self.lagos, facility=self.facility)
        self.return_to_work_form = self.create_form("Return to Work", AssessmentFormScope.NATIONAL, AssessmentFormType.RETURN_TO_WORK)

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

    def create_form(self, name, scope, form_type, **overrides):
        return AssessmentFormTemplate.objects.create(
            name=name,
            scope=scope,
            form_type=form_type,
            status=AssessmentFormStatus.ACTIVE,
            **overrides,
        )

    def create_requirement_set(self, name, scope, forms=(), **overrides):
        status = overrides.pop("status", AssessmentRequirementSetStatus.ACTIVE)
        requirement_set = AssessmentRequirementSet.objects.create(
            name=name,
            scope=scope,
            status=status,
            **overrides,
        )
        requirement_set.required_forms.set(forms)
        return requirement_set

    def test_resolution_unions_national_state_and_facility_requirements_in_precedence_order(self):
        self.create_requirement_set(
            "National Baseline",
            AssessmentFormScope.NATIONAL,
            forms=[self.national_form],
            required_documents=["nin_verification"],
            required_lab_tests=["stool_microscopy"],
            required_vaccinations=["typhoid"],
            blocking_requirements=["national_health_declaration"],
        )
        self.create_requirement_set(
            "Lagos Public Health Addendum",
            AssessmentFormScope.STATE,
            forms=[self.state_form],
            state=self.lagos,
            required_documents=["nin_verification", "lagos_attestation"],
            required_lab_tests=["stool_culture"],
            required_vaccinations=["hepatitis_a"],
            blocking_requirements=["state_health_addendum"],
        )
        self.create_requirement_set(
            "Facility Intake",
            AssessmentFormScope.FACILITY,
            forms=[self.facility_form],
            state=self.lagos,
            facility=self.facility,
            required_documents=[],
            required_lab_tests=["stool_microscopy"],
            advisory_requirements=["arrive_fasting"],
        )
        self.client.force_authenticate(self.handler_user)

        response = self.client.get(f"/api/assessments/{self.assessment.id}/requirements/")

        self.assertEqual(response.status_code, 200, response.data)
        resolved = payload(response)
        self.assertEqual([item["scope"] for item in resolved["applied_requirement_sets"]], ["national", "state", "facility"])
        self.assertEqual([item["name"] for item in resolved["required_forms"]], ["National Declaration", "Lagos Addendum", "Facility Intake"])
        self.assertEqual(resolved["required_documents"], ["nin_verification", "lagos_attestation"])
        self.assertEqual(resolved["required_lab_tests"], ["stool_microscopy", "stool_culture"])
        self.assertEqual(resolved["required_vaccinations"], ["typhoid", "hepatitis_a"])
        self.assertIn("national_health_declaration", resolved["blocking_requirements"])
        self.assertIn("state_health_addendum", resolved["blocking_requirements"])

    def test_context_filters_apply_category_employer_type_and_illness_requirements(self):
        self.create_requirement_set(
            "Food Preparer",
            AssessmentFormScope.NATIONAL,
            forms=[self.national_form],
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            required_lab_tests=["preparer_test"],
        )
        self.create_requirement_set(
            "Restaurant",
            AssessmentFormScope.NATIONAL,
            employer_category=EstablishmentCategory.RESTAURANT_CAFE,
            required_documents=["restaurant_attestation"],
        )
        self.create_requirement_set(
            "Cholera Return to Work",
            AssessmentFormScope.NATIONAL,
            forms=[self.return_to_work_form],
            illness_condition=SuspectedCondition.CHOLERA,
            required_approvals=["public_health_clearance"],
        )
        self.client.force_authenticate(self.handler_user)

        before = payload(self.client.get(f"/api/assessments/{self.assessment.id}/requirements/"))
        self.assertNotIn("public_health_clearance", before["required_approvals"])

        IllnessReport.objects.create(
            food_handler=self.food_handler,
            employer=self.employer,
            reported_by=self.handler_user,
            suspected_condition=SuspectedCondition.CHOLERA,
            clearance_status=ClearanceStatus.PENDING,
        )
        after = payload(self.client.get(f"/api/assessments/{self.assessment.id}/requirements/"))
        self.assertIn("preparer_test", after["required_lab_tests"])
        self.assertIn("restaurant_attestation", after["required_documents"])
        self.assertIn("public_health_clearance", after["required_approvals"])
        self.assertIn("Return to Work", [item["name"] for item in after["required_forms"]])

    def test_retired_expired_and_other_state_sets_do_not_resolve(self):
        self.create_requirement_set("Retired", AssessmentFormScope.NATIONAL, status=AssessmentRequirementSetStatus.RETIRED, required_documents=["retired"])
        self.create_requirement_set("Expired", AssessmentFormScope.NATIONAL, effective_to=timezone.localdate() - timezone.timedelta(days=1), required_documents=["expired"])
        self.create_requirement_set("Other State", AssessmentFormScope.STATE, state=self.oyo, required_documents=["oyo_only"])
        self.client.force_authenticate(self.handler_user)

        resolved = payload(self.client.get(f"/api/assessments/{self.assessment.id}/requirements/"))

        self.assertEqual(resolved["required_documents"], [])

    def test_requirement_set_crud_publish_retire_and_scope_permissions(self):
        self.client.force_authenticate(self.federal_admin)
        created = self.client.post(
            "/api/forms/requirement-sets/",
            {
                "name": "National Baseline",
                "scope": "national",
                "assessment_type": "standard",
                "required_forms": [str(self.national_form.id)],
                "required_documents": ["nin_verification"],
            },
            format="json",
        )
        self.assertEqual(created.status_code, 201, created.data)
        requirement_set_id = payload(created)["id"]
        published = self.client.post(f"/api/forms/requirement-sets/{requirement_set_id}/publish/", format="json")
        self.assertEqual(published.status_code, 200)
        self.assertEqual(payload(published)["status"], AssessmentRequirementSetStatus.ACTIVE)
        retired = self.client.post(f"/api/forms/requirement-sets/{requirement_set_id}/retire/", format="json")
        self.assertEqual(retired.status_code, 200)
        self.assertEqual(payload(retired)["status"], AssessmentRequirementSetStatus.RETIRED)

        self.client.force_authenticate(self.state_admin)
        self.assertEqual(self.client.get(f"/api/forms/requirement-sets/{requirement_set_id}/").status_code, 404)
        blocked = self.client.post("/api/forms/requirement-sets/", {"name": "Blocked", "scope": "national"}, format="json")
        self.assertEqual(blocked.status_code, 403)

    def test_resolution_endpoint_rejects_unrelated_food_handler(self):
        self.client.force_authenticate(self.other_handler_user)

        response = self.client.post("/api/forms/requirements/resolve/", {"assessment": str(self.assessment.id)}, format="json")

        self.assertEqual(response.status_code, 403)
