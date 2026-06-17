from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("standards", "0006_indicatorevidence"),
    ]

    operations = [
        migrations.AddField(
            model_name="meindicator",
            name="kpi_type",
            field=models.CharField(
                choices=[("quantitative", "Quantitative"), ("qualitative", "Qualitative")],
                default="quantitative",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="unit_of_measurement",
            field=models.CharField(blank=True, default="count", max_length=64),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="input_mode",
            field=models.CharField(
                choices=[("manual", "Manual Only"), ("automated", "Automated Only"), ("hybrid", "Hybrid")],
                default="manual",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="record_input_type",
            field=models.CharField(
                choices=[
                    ("progress_only", "Progress Only"),
                    ("cumulative_only", "Cumulative Only"),
                    ("progress_or_cumulative", "Progress or Cumulative"),
                ],
                default="progress_only",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="progress_cumulative_relationship",
            field=models.CharField(
                choices=[("dependent", "Dependent"), ("same", "Same"), ("independent", "Independent")],
                default="dependent",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="target_direction",
            field=models.CharField(
                choices=[
                    ("higher_better", "Higher Is Better"),
                    ("lower_better", "Lower Is Better"),
                    ("exact", "Exact Target"),
                    ("range", "Target Range"),
                ],
                default="higher_better",
                max_length=24,
            ),
        ),
        migrations.AddField(
            model_name="meindicator",
            name="visibility_scope",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="meindicator",
            name="data_source",
            field=models.CharField(
                choices=[
                    ("manual", "Manual"),
                    ("food_handler_registry", "Food Handler Registry"),
                    ("medical_test_records", "Medical Test Records"),
                    ("test_results", "Test Results"),
                    ("certificate_records", "Certificate Records"),
                    ("facility_records", "Facility Records"),
                    ("facility_handler_mapping", "Facility-Handler Mapping"),
                    ("test_centers_labs", "Test Centers / Labs"),
                    ("inspections", "Inspections"),
                    ("training_orientation", "Training / Orientation"),
                    ("payments", "Payments"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="meindicatordatasource",
            name="source_type",
            field=models.CharField(
                choices=[
                    ("manual", "Manual"),
                    ("kpi", "KPI"),
                    ("food_handler_registry", "Food Handler Registry"),
                    ("medical_test_records", "Medical Test Records"),
                    ("test_results", "Test Results"),
                    ("certificate_records", "Certificate Records"),
                    ("facility_records", "Facility Records"),
                    ("facility_handler_mapping", "Facility-Handler Mapping"),
                    ("test_centers_labs", "Test Centers / Labs"),
                    ("inspections", "Inspections"),
                    ("training_orientation", "Training / Orientation"),
                    ("payments", "Payments"),
                ],
                default="manual",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="meindicatordatasource",
            name="calculation_method",
            field=models.CharField(
                choices=[
                    ("count", "Count"),
                    ("unique_count", "Unique Count"),
                    ("sum", "Sum"),
                    ("average", "Average"),
                    ("percentage", "Percentage"),
                    ("ratio", "Ratio"),
                    ("formula", "Formula"),
                ],
                max_length=16,
            ),
        ),
        migrations.AlterField(
            model_name="indicatordisaggregation",
            name="source_type",
            field=models.CharField(
                choices=[
                    ("manual", "Manual"),
                    ("kpi", "KPI"),
                    ("food_handler_registry", "Food Handler Registry"),
                    ("medical_test_records", "Medical Test Records"),
                    ("test_results", "Test Results"),
                    ("certificate_records", "Certificate Records"),
                    ("facility_records", "Facility Records"),
                    ("facility_handler_mapping", "Facility-Handler Mapping"),
                    ("test_centers_labs", "Test Centers / Labs"),
                    ("inspections", "Inspections"),
                    ("training_orientation", "Training / Orientation"),
                    ("payments", "Payments"),
                ],
                default="manual",
                max_length=32,
            ),
        ),
    ]
