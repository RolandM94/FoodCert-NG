from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lab_tests", "0005_labtest_status_aliases"),
    ]

    operations = [
        migrations.AddField(
            model_name="labtest",
            name="doctor_recommendation",
            field=models.CharField(
                blank=True,
                choices=[
                    ("cleared", "Cleared"),
                    ("repeat_test", "Repeat Test"),
                    ("temporarily_not_fit", "Temporarily Not Fit"),
                    ("public_health_clearance", "Public Health Clearance"),
                ],
                db_index=True,
                max_length=64,
            ),
        ),
        migrations.AddField(
            model_name="labtest",
            name="doctor_review_notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddIndex(
            model_name="labtest",
            index=models.Index(fields=["doctor_recommendation"], name="lab_tests_l_doctor__6a4b68_idx"),
        ),
    ]
