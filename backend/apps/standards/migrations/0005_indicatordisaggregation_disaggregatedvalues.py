import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("standards", "0004_qualitativeindicatorconfig_value_category"),
    ]

    operations = [
        migrations.CreateModel(
            name="IndicatorDisaggregation",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "source_type",
                    models.CharField(
                        choices=[
                            ("manual", "Manual"),
                            ("form", "Form"),
                            ("indicator", "Indicator"),
                            ("document", "Document"),
                            ("external", "External"),
                        ],
                        default="manual",
                        max_length=16,
                    ),
                ),
                ("field_id", models.CharField(max_length=128)),
                ("field_label", models.CharField(max_length=255)),
                ("level", models.PositiveIntegerField(default=1)),
                (
                    "indicator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="disaggregations",
                        to="standards.meindicator",
                    ),
                ),
            ],
            options={
                "ordering": ["indicator__indicator_name", "level", "field_label"],
            },
        ),
        migrations.CreateModel(
            name="IndicatorDisaggregatedValue",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
                ("dimension_values_json", models.JSONField(blank=True, default=dict)),
                ("value_numeric", models.DecimalField(decimal_places=4, max_digits=18)),
                (
                    "indicator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="disaggregated_values",
                        to="standards.meindicator",
                    ),
                ),
                (
                    "indicator_value",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="disaggregated_values",
                        to="standards.meindicatorvalue",
                    ),
                ),
            ],
            options={
                "ordering": ["indicator__indicator_name", "period_start", "dimension_values_json"],
            },
        ),
        migrations.AddConstraint(
            model_name="indicatordisaggregation",
            constraint=models.UniqueConstraint(fields=("indicator", "field_id"), name="unique_indicator_disaggregation_field"),
        ),
        migrations.AddConstraint(
            model_name="indicatordisaggregation",
            constraint=models.UniqueConstraint(fields=("indicator", "level"), name="unique_indicator_disaggregation_level"),
        ),
        migrations.AddIndex(
            model_name="indicatordisaggregation",
            index=models.Index(fields=["indicator", "source_type"], name="standards_i_indicat_4e4f8c_idx"),
        ),
        migrations.AddIndex(
            model_name="indicatordisaggregation",
            index=models.Index(fields=["indicator", "level"], name="standards_i_indicat_9fb23a_idx"),
        ),
        migrations.AddIndex(
            model_name="indicatordisaggregatedvalue",
            index=models.Index(fields=["indicator", "period_start", "period_end"], name="standards_i_indicat_cda2b5_idx"),
        ),
        migrations.AddIndex(
            model_name="indicatordisaggregatedvalue",
            index=models.Index(fields=["indicator_value"], name="standards_i_indicat_5df5ec_idx"),
        ),
    ]
