from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("assessments", "0005_rename_assessment_ap_doctor__95e9b4_idx_assessments_doctor__00f435_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="healthdeclaration",
            name="is_locked",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name="healthdeclaration",
            name="reopen_reason",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="healthdeclaration",
            name="reopened_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="healthdeclaration",
            name="version",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="healthdeclaration",
            name="reopened_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="reopened_declarations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name="healthdeclaration",
            index=models.Index(fields=["is_locked"], name="assessments_is_lock_8989a5_idx"),
        ),
    ]
