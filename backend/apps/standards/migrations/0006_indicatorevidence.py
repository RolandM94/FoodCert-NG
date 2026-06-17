import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("standards", "0005_indicatordisaggregation_disaggregatedvalues"),
    ]

    operations = [
        migrations.CreateModel(
            name="IndicatorEvidence",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("document_id", models.CharField(blank=True, default="", max_length=128)),
                ("file_id", models.CharField(blank=True, default="", max_length=128)),
                ("file_url", models.CharField(blank=True, default="", max_length=512)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, default="")),
                (
                    "evidence_type",
                    models.CharField(
                        choices=[
                            ("text", "Text"),
                            ("file", "File Upload"),
                            ("checklist", "Checklist"),
                            ("url", "URL"),
                            ("inspection", "Inspection"),
                        ],
                        default="text",
                        max_length=16,
                    ),
                ),
                (
                    "approval_status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("submitted", "Submitted"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                        ],
                        db_index=True,
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("rejection_comment", models.TextField(blank=True, default="")),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approved_indicator_evidence",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "indicator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evidence",
                        to="standards.meindicator",
                    ),
                ),
                (
                    "indicator_value",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evidence_items",
                        to="standards.meindicatorvalue",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="uploaded_indicator_evidence",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="indicatorevidence",
            index=models.Index(fields=["indicator", "approval_status"], name="standards_i_indicat_e07512_idx"),
        ),
        migrations.AddIndex(
            model_name="indicatorevidence",
            index=models.Index(fields=["indicator_value", "approval_status"], name="standards_i_indicat_04c7f4_idx"),
        ),
        migrations.AddIndex(
            model_name="indicatorevidence",
            index=models.Index(fields=["evidence_type"], name="standards_i_eviden_5c7f47_idx"),
        ),
    ]
