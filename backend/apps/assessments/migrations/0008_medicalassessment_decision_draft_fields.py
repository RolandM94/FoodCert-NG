from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessments", "0007_physicalexamination_draft_completion"),
    ]

    operations = [
        migrations.AddField(
            model_name="medicalassessment",
            name="decision_draft",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("fit", "Fit"),
                    ("temporarily_not_fit", "Temporarily Not Fit"),
                    ("not_fit", "Not Fit"),
                    ("requires_vaccination", "Requires Vaccination"),
                    ("requires_lab_test", "Requires Lab Test"),
                    ("requires_recheck", "Requires Recheck"),
                    ("requires_treatment", "Requires Treatment"),
                    ("requires_public_health_clearance", "Requires Public Health Clearance"),
                    ("return_to_work_on_date", "Return To Work On Date"),
                ],
                default="pending",
                max_length=64,
            ),
        ),
        migrations.AddField(
            model_name="medicalassessment",
            name="decision_draft_return_to_work_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="medicalassessment",
            name="decision_draft_notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="medicalassessment",
            name="decision_draft_saved_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
