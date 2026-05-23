from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_userinvite_ministry_staff_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="userinvite",
            name="facility_staff_type",
            field=models.CharField(blank=True, db_index=True, max_length=64),
        ),
    ]
