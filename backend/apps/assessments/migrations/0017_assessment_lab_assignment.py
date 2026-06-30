from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0001_initial"),
        ("assessments", "0016_assessment_check_in_identity_verification"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="medicalassessment",
            name="assigned_lab_staff",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_lab_assessments", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="medicalassessment",
            name="assigned_lab_unit",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="lab_assessments", to="organizations.organizationunit"),
        ),
        migrations.AddField(
            model_name="medicalassessment",
            name="lab_assigned_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="medicalassessment",
            name="lab_assigned_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="lab_assigned_assessments", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="medicalassessment",
            name="lab_assignment_reason",
            field=models.TextField(blank=True),
        ),
        migrations.AddIndex(
            model_name="medicalassessment",
            index=models.Index(fields=["assigned_lab_staff"], name="assessments_assigne_e49135_idx"),
        ),
        migrations.AddIndex(
            model_name="medicalassessment",
            index=models.Index(fields=["assigned_lab_unit"], name="assessments_assigne_b242da_idx"),
        ),
    ]
