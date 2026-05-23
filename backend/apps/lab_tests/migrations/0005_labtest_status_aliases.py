from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lab_tests", "0004_labtest_repeat_policy_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="labtest",
            name="status",
            field=models.CharField(
                choices=[
                    ("requested", "Requested"),
                    ("sample_collection_pending", "Sample Collection Pending"),
                    ("sample_collected", "Sample Collected"),
                    ("in_progress", "In Progress"),
                    ("result_uploaded", "Result Uploaded"),
                    ("submitted_to_doctor", "Submitted To Doctor"),
                    ("positive", "Positive"),
                    ("negative", "Negative"),
                    ("inconclusive", "Inconclusive"),
                    ("repeat_required", "Repeat Required"),
                    ("reviewed", "Reviewed"),
                ],
                db_index=True,
                default="requested",
                max_length=32,
            ),
        ),
    ]
