from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("standards", "0008_kpi_input_mode_automatic_imported"),
    ]

    operations = [
        migrations.AddField(
            model_name="meindicator",
            name="achievement_value",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="allow_manual_override",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="calculation_source",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="calculation_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("percentage", "Percentage"),
                    ("count", "Count"),
                    ("unique_count", "Unique Count"),
                    ("ratio", "Ratio"),
                    ("average", "Average"),
                    ("sum", "Sum"),
                    ("score", "Score"),
                    ("formula", "Formula"),
                ],
                default="",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="denominator_definition",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="last_calculated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="latest_value",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="numerator_definition",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="override_requires_reason",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="policy_standard_code",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="rule_parameter_key",
            field=models.CharField(blank=True, default="", max_length=128),
        ),
    ]
