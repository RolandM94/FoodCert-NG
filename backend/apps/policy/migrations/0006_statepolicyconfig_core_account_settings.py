from django.db import migrations, models

import apps.policy.models


class Migration(migrations.Migration):

    dependencies = [
        ("policy", "0005_statepolicyconfig_medical_facility_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="statepolicyconfig",
            name="notification_settings",
            field=models.JSONField(blank=True, default=apps.policy.models.default_notification_settings),
        ),
        migrations.AddField(
            model_name="statepolicyconfig",
            name="security_access_settings",
            field=models.JSONField(blank=True, default=apps.policy.models.default_security_access_settings),
        ),
        migrations.AddField(
            model_name="statepolicyconfig",
            name="state_profile_settings",
            field=models.JSONField(blank=True, default=apps.policy.models.default_state_profile_settings),
        ),
    ]
