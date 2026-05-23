from django.db import migrations, models


REPORT_TYPE_CHOICES = [
    ("employer_compliance", "Employer Compliance"),
    ("employer_certificates", "Employer Certificate Expiry"),
    ("employer_vaccinations", "Employer Vaccination Compliance"),
    ("facility_performance", "Facility Performance"),
    ("state_monthly", "State Monthly"),
    ("national", "National"),
    ("vaccination_coverage", "Vaccination Coverage"),
    ("illness_trends", "Illness Trends"),
    ("inspection_outcomes", "Inspection Outcomes"),
    ("medical_examination", "Medical Examination Report"),
    ("temporarily_not_fit_report", "Temporarily Not Fit Report"),
    ("return_to_work_report", "Return To Work Report"),
    ("assessment_completion", "Assessment Completion Summary"),
    ("vaccination_review_report", "Vaccination Review Report"),
    ("restricted_lab_summary", "Restricted Lab Summary"),
]


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0003_medical_report_types"),
    ]

    operations = [
        migrations.AlterField(
            model_name="generatedreport",
            name="report_type",
            field=models.CharField(choices=REPORT_TYPE_CHOICES, db_index=True, max_length=64),
        ),
        migrations.AlterField(
            model_name="reportschedule",
            name="report_type",
            field=models.CharField(choices=REPORT_TYPE_CHOICES, db_index=True, max_length=64),
        ),
    ]
