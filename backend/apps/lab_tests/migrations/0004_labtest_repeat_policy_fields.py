from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("lab_tests", "0003_rename_lab_tests_l_sample__f6fbff_idx_lab_tests_l_sample__b24f03_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="labtest",
            name="is_flagged",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name="labtest",
            name="repeat_reason",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="labtest",
            name="repeat_required",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name="labtest",
            name="parent_lab_test",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="repeat_tests",
                to="lab_tests.labtest",
            ),
        ),
        migrations.AddIndex(
            model_name="labtest",
            index=models.Index(fields=["parent_lab_test"], name="lab_tests_l_parent__1f93e0_idx"),
        ),
        migrations.AddIndex(
            model_name="labtest",
            index=models.Index(fields=["repeat_required"], name="lab_tests_l_repeat__c26bc5_idx"),
        ),
        migrations.AddIndex(
            model_name="labtest",
            index=models.Index(fields=["is_flagged"], name="lab_tests_l_is_flag_34277e_idx"),
        ),
    ]
