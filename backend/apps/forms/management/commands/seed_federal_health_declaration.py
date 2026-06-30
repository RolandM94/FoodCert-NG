from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.forms.models import (
    FormPrimaryModule,
    FormTemplate,
    FormTemplatePurpose,
    FormTemplateStatus,
    FormTemplateVersion,
    FormTemplateVisibility,
    FormVersionStatus,
)
from apps.organizations.models import Organization, OrganizationType


def _q(key, label, qtype, *, required=True, risk=False, options=None):
    question = {
        "key": key,
        "id": key,
        "label": label,
        "type": qtype,
        "required": required,
        "field_owner": "federal",
        "locked": True,
    }
    if risk:
        question["risk_flag"] = True
    if options:
        question["options"] = options
    return question


YES_NO = ["Yes", "No"]


NATIONAL_DECLARATION_SCHEMA = {
    "sections": [
        {
            "key": "identity_information",
            "title": "Identity Information",
            "questions": [
                _q("full_name", "Full name", "text"),
                _q("nin", "National Identification Number (NIN)", "text"),
                _q("date_of_birth", "Date of birth", "date"),
                _q("gender", "Gender", "single_choice", options=["Male", "Female"]),
                _q("passport_photo", "Passport photograph", "file"),
            ],
        },
        {
            "key": "food_handler_information",
            "title": "Food Handler Information",
            "questions": [
                _q("food_handler_category", "Food handler category", "text"),
                _q("employer_name", "Employer (if applicable)", "text", required=False),
            ],
        },
        {
            "key": "recent_illness_declaration",
            "title": "Recent Illness Declaration",
            "questions": [
                _q("fever", "Fever", "single_choice", risk=True, options=YES_NO),
                _q("jaundice", "Jaundice", "single_choice", risk=True, options=YES_NO),
                _q("diarrhoea", "Diarrhoea", "single_choice", risk=True, options=YES_NO),
                _q("vomiting", "Vomiting", "single_choice", risk=True, options=YES_NO),
                _q("cough_or_flu", "Cough or flu", "single_choice", risk=True, options=YES_NO),
                _q("sore_throat", "Sore throat", "single_choice", risk=True, options=YES_NO),
            ],
        },
        {
            "key": "communicable_disease_history",
            "title": "Communicable Disease History",
            "questions": [
                _q("typhoid_carrier_history", "Known typhoid carrier history", "single_choice", risk=True, options=YES_NO),
                _q("cholera_history", "Recent cholera", "single_choice", risk=True, options=YES_NO),
                _q("hepatitis_a_history", "Hepatitis A history", "single_choice", risk=True, options=YES_NO),
                _q("dysentery_history", "Recent dysentery", "single_choice", risk=True, options=YES_NO),
                _q("gastrointestinal_infection", "Recent gastrointestinal infection", "single_choice", risk=True, options=YES_NO),
            ],
        },
        {
            "key": "skin_and_infection_declaration",
            "title": "Skin and Infection Declaration",
            "questions": [
                _q("skin_infection", "Skin infection", "single_choice", risk=True, options=YES_NO),
                _q("boils_cuts_lesions", "Boils, cuts or lesions", "single_choice", risk=True, options=YES_NO),
                _q("discharge", "Discharge from eyes/nose/ears/mouth", "single_choice", risk=True, options=YES_NO),
            ],
        },
        {
            "key": "vaccination_history",
            "title": "Vaccination History",
            "questions": [
                _q("current_medication", "Current medication", "text", required=False),
                _q("typhoid_vaccination_certificate", "Typhoid vaccination certificate", "file"),
                _q("typhoid_vaccination_date", "Typhoid vaccination date", "date", required=False),
                _q("hepatitis_a_vaccination_certificate", "Hepatitis A vaccination certificate", "file"),
                _q("hepatitis_a_vaccination_date", "Hepatitis A vaccination date", "date", required=False),
            ],
        },
        {
            "key": "consent",
            "title": "Consent",
            "questions": [
                _q("consent_for_assessment", "I consent to assessment and certificate processing", "checkbox"),
            ],
        },
        {
            "key": "declaration_statement",
            "title": "Declaration Statement",
            "questions": [
                _q("declaration_certification", "I confirm the information provided is true", "checkbox"),
            ],
        },
    ]
}


class Command(BaseCommand):
    help = "Seed the National Food Handler Health Declaration Form template (federal-locked)."

    def handle(self, *args, **options):
        existing = FormTemplate.objects.filter(
            purpose=FormTemplatePurpose.FOOD_HANDLER_DECLARATION,
            visibility=FormTemplateVisibility.FEDERAL_STANDARD,
            title="National Food Handler Health Declaration Form",
        ).first()
        if existing:
            self.stdout.write(self.style.WARNING("National health declaration template already exists; skipping."))
            return

        federal_org = (
            Organization.objects.filter(organization_type=OrganizationType.FEDERAL_MINISTRY).order_by("created_at").first()
        )
        if not federal_org:
            federal_org = Organization.objects.create(
                name="Federal Ministry of Health and Social Welfare",
                organization_type=OrganizationType.FEDERAL_MINISTRY,
            )

        template = FormTemplate.objects.create(
            title="National Food Handler Health Declaration Form",
            description="National base health declaration template. Federal fields are locked; states and facilities may add fields but cannot delete, hide, rename, weaken, or make Federal fields optional.",
            purpose=FormTemplatePurpose.FOOD_HANDLER_DECLARATION,
            owner_organization=federal_org,
            target_respondent_type="food_handler",
            primary_module=FormPrimaryModule.FOOD_HANDLERS,
            visibility=FormTemplateVisibility.FEDERAL_STANDARD,
            status=FormTemplateStatus.PUBLISHED,
            current_version=1,
        )
        FormTemplateVersion.objects.create(
            template=template,
            version_number=1,
            schema_json=NATIONAL_DECLARATION_SCHEMA,
            status=FormVersionStatus.PUBLISHED if hasattr(FormVersionStatus, "PUBLISHED") else FormVersionStatus.DRAFT,
            published_at=timezone.now(),
        )

        section_count = len(NATIONAL_DECLARATION_SCHEMA["sections"])
        field_count = sum(len(s["questions"]) for s in NATIONAL_DECLARATION_SCHEMA["sections"])
        self.stdout.write(self.style.SUCCESS(
            f"Seeded National Health Declaration template: {section_count} sections, {field_count} federal-locked fields."
        ))
