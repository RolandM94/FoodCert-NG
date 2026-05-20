from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employers", "0003_employer_business_type_employer_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="employer",
            name="business_settings",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="employer",
            name="notification_preferences",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
