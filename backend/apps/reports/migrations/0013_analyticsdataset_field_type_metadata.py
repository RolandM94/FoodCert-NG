from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0012_dashboard_alert_rules"),
    ]

    operations = [
        migrations.AddField(
            model_name="analyticsdataset",
            name="field_type_metadata",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
