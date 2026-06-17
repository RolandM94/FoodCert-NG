import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("standards", "0003_meindicatordatasource_value_source_external"),
    ]

    operations = [
        migrations.AddField(
            model_name="meindicatorvalue",
            name="qualitative_category",
            field=models.CharField(blank=True, default="", max_length=128),
        ),
        migrations.CreateModel(
            name="QualitativeIndicatorConfig",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "input_type",
                    models.CharField(
                        choices=[
                            ("text", "Narrative Text"),
                            ("likert_scale", "Rating Scale"),
                            ("category", "Dropdown Category"),
                            ("rubric", "Rubric"),
                        ],
                        default="text",
                        max_length=16,
                    ),
                ),
                ("scale_min", models.IntegerField(blank=True, null=True)),
                ("scale_max", models.IntegerField(blank=True, null=True)),
                ("scale_labels_json", models.JSONField(blank=True, default=dict)),
                ("category_options_json", models.JSONField(blank=True, default=list)),
                ("requires_narrative", models.BooleanField(default=False)),
                (
                    "indicator",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="qualitative_config",
                        to="standards.meindicator",
                    ),
                ),
            ],
            options={
                "ordering": ["indicator__indicator_name"],
            },
        ),
        migrations.AddIndex(
            model_name="qualitativeindicatorconfig",
            index=models.Index(fields=["input_type"], name="standards_q_input_t_4d512a_idx"),
        ),
        migrations.AddIndex(
            model_name="qualitativeindicatorconfig",
            index=models.Index(fields=["requires_narrative"], name="standards_q_require_9d9fd5_idx"),
        ),
    ]
