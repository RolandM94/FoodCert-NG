from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("employers", "0002_rename_employerprofile_employer_and_align_policy"),
        ("food_handlers", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="foodhandlerprofile",
            name="employer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="food_handlers",
                to="employers.employer",
            ),
        ),
    ]
