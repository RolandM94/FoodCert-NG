from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessments", "0006_healthdeclaration_version_lock"),
    ]

    operations = [
        migrations.AddField(
            model_name="physicalexamination",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="physicalexamination",
            name="is_completed",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name="physicalexamination",
            name="risk_flag",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddIndex(
            model_name="physicalexamination",
            index=models.Index(fields=["risk_flag"], name="assessments_risk_fl_5d221c_idx"),
        ),
        migrations.AddIndex(
            model_name="physicalexamination",
            index=models.Index(fields=["is_completed"], name="assessments_is_comp_9d5af6_idx"),
        ),
    ]
