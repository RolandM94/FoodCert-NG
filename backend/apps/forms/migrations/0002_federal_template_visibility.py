from django.db import migrations, models
import django.db.models.deletion


def backfill_template_visibility(apps, schema_editor):
    FormTemplate = apps.get_model("forms", "FormTemplate")
    OrganizationType = {
        "FEDERAL_MINISTRY": "federal_ministry",
    }
    FormTemplate.objects.filter(owner_organization__organization_type=OrganizationType["FEDERAL_MINISTRY"]).update(
        visibility="federal_private"
    )
    FormTemplate.objects.exclude(owner_organization__organization_type=OrganizationType["FEDERAL_MINISTRY"]).update(
        visibility="state_owned"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("forms", "0001_initial"),
        ("locations", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="formassignment",
            name="purpose",
            field=models.CharField(
                choices=[
                    ("inspection_checklist", "Inspection Checklist"),
                    ("employer_data_collection", "Employer Data Collection"),
                    ("employer_compliance", "Employer Compliance Self-Assessment"),
                    ("facility_data_collection", "Medical Facility Data Collection"),
                    ("facility_monthly_report", "Medical Facility Monthly Report"),
                    ("accreditation_checklist", "Accreditation Checklist"),
                    ("re_accreditation_checklist", "Re-accreditation Checklist"),
                    ("food_handler_survey", "Food Handler Survey"),
                    ("food_handler_declaration", "Food Handler Declaration"),
                    ("incident_report", "Incident Report"),
                    ("training_feedback", "Training Feedback"),
                    ("general_data_collection", "General Data Collection"),
                    ("national_policy_template", "National Policy Template"),
                    ("state_reporting_form", "State Reporting Form"),
                    ("federal_me_data_collection", "Federal M&E Data Collection"),
                    ("federal_compliance_review", "Federal Compliance Review"),
                    ("national_incident_reporting", "National Incident Reporting"),
                    ("programme_monitoring_form", "Programme Monitoring Form"),
                    ("guideline_implementation_survey", "Guideline Implementation Survey"),
                    ("cross_state_survey", "Cross-State Survey"),
                    ("national_facility_reporting_template", "National Facility Reporting Template"),
                    ("inspection_performance_reporting_template", "Inspection Performance Reporting Template"),
                ],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="formtemplate",
            name="purpose",
            field=models.CharField(
                choices=[
                    ("inspection_checklist", "Inspection Checklist"),
                    ("employer_data_collection", "Employer Data Collection"),
                    ("employer_compliance", "Employer Compliance Self-Assessment"),
                    ("facility_data_collection", "Medical Facility Data Collection"),
                    ("facility_monthly_report", "Medical Facility Monthly Report"),
                    ("accreditation_checklist", "Accreditation Checklist"),
                    ("re_accreditation_checklist", "Re-accreditation Checklist"),
                    ("food_handler_survey", "Food Handler Survey"),
                    ("food_handler_declaration", "Food Handler Declaration"),
                    ("incident_report", "Incident Report"),
                    ("training_feedback", "Training Feedback"),
                    ("general_data_collection", "General Data Collection"),
                    ("national_policy_template", "National Policy Template"),
                    ("state_reporting_form", "State Reporting Form"),
                    ("federal_me_data_collection", "Federal M&E Data Collection"),
                    ("federal_compliance_review", "Federal Compliance Review"),
                    ("national_incident_reporting", "National Incident Reporting"),
                    ("programme_monitoring_form", "Programme Monitoring Form"),
                    ("guideline_implementation_survey", "Guideline Implementation Survey"),
                    ("cross_state_survey", "Cross-State Survey"),
                    ("national_facility_reporting_template", "National Facility Reporting Template"),
                    ("inspection_performance_reporting_template", "Inspection Performance Reporting Template"),
                ],
                db_index=True,
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="formtemplate",
            name="visibility",
            field=models.CharField(
                choices=[
                    ("state_owned", "State Owned"),
                    ("federal_private", "Federal Private"),
                    ("federal_shared", "Federal Shared"),
                    ("federal_standard", "Federal Standard"),
                ],
                db_index=True,
                default="state_owned",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="formtemplate",
            name="shared_with_states",
            field=models.ManyToManyField(blank=True, related_name="shared_form_templates", to="locations.state"),
        ),
        migrations.AddField(
            model_name="formtemplate",
            name="source_template",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="derived_templates",
                to="forms.formtemplate",
            ),
        ),
        migrations.AddField(
            model_name="formtemplate",
            name="source_version",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="derived_templates",
                to="forms.formtemplateversion",
            ),
        ),
        migrations.AddIndex(
            model_name="formtemplate",
            index=models.Index(fields=["visibility", "status"], name="forms_formt_visibil_c53ee1_idx"),
        ),
        migrations.RunPython(backfill_template_visibility, migrations.RunPython.noop),
    ]
