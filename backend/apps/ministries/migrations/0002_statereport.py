from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("locations", "0001_initial"),
        ("ministries", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StateReport",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("report_type", models.CharField(db_index=True, max_length=64)),
                ("reporting_period_start", models.DateField()),
                ("reporting_period_end", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("generated", "Generated"),
                            ("submitted", "Submitted"),
                            ("returned", "Returned"),
                            ("accepted", "Accepted"),
                        ],
                        db_index=True,
                        default="generated",
                        max_length=16,
                    ),
                ),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("file_url", models.URLField(blank=True)),
                ("data_snapshot", models.JSONField(blank=True, default=dict)),
                ("review_comment", models.TextField(blank=True)),
                (
                    "generated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="generated_state_reports",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reviewed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reviewed_state_reports",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("state", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ministry_reports", to="locations.state")),
                (
                    "submitted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="submitted_state_reports",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-reporting_period_end", "-created_at"],
                "indexes": [
                    models.Index(fields=["state"], name="ministries__state_i_6d2d53_idx"),
                    models.Index(fields=["report_type"], name="ministries__report__a02e4c_idx"),
                    models.Index(fields=["status"], name="ministries__status_2f6fd7_idx"),
                    models.Index(fields=["reporting_period_start", "reporting_period_end"], name="ministries__reporti_97dc6a_idx"),
                ],
            },
        ),
    ]
