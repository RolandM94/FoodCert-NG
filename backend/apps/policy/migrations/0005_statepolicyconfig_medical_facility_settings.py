from django.db import migrations, models

import apps.policy.models


class Migration(migrations.Migration):

    dependencies = [
        ("policy", "0004_nationalpolicyconfig_state_certificate_template_overrides_enabled"),
    ]

    operations = [
        migrations.AddField(
            model_name="statepolicyconfig",
            name="medical_facility_settings",
            field=models.JSONField(blank=True, default=apps.policy.models.default_medical_facility_settings),
        ),
    ]
