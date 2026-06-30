from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0001_initial"),
        ("lab_tests", "0006_labtest_doctor_review_metadata"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="labtest",
            name="assigned_lab_staff",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_lab_tests", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="labtest",
            name="assigned_lab_unit",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_lab_tests", to="organizations.organizationunit"),
        ),
        migrations.AddIndex(
            model_name="labtest",
            index=models.Index(fields=["assigned_lab_staff"], name="lab_tests_l_assigne_efc4bf_idx"),
        ),
        migrations.AddIndex(
            model_name="labtest",
            index=models.Index(fields=["assigned_lab_unit"], name="lab_tests_l_assigne_6097db_idx"),
        ),
    ]
