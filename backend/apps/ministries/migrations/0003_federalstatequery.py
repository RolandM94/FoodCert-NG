from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("locations", "0001_initial"),
        ("ministries", "0002_statereport"),
    ]

    operations = [
        migrations.CreateModel(
            name="FederalStateQuery",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("subject", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("category", models.CharField(db_index=True, max_length=64)),
                ("priority", models.CharField(choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("urgent", "Urgent")], db_index=True, default="medium", max_length=16)),
                ("status", models.CharField(choices=[("open", "Open"), ("assigned", "Assigned"), ("awaiting_state_response", "Awaiting State Response"), ("responded", "Responded"), ("closed", "Closed")], db_index=True, default="open", max_length=32)),
                ("response", models.TextField(blank=True)),
                ("responded_at", models.DateTimeField(blank=True, null=True)),
                ("closed_at", models.DateTimeField(blank=True, null=True)),
                ("assigned_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_federal_queries", to=settings.AUTH_USER_MODEL)),
                ("raised_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="raised_federal_queries", to=settings.AUTH_USER_MODEL)),
                ("responded_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="responded_federal_queries", to=settings.AUTH_USER_MODEL)),
                ("state", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="federal_queries", to="locations.state")),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["state"], name="ministries__state_i_07a9f7_idx"),
                    models.Index(fields=["category"], name="ministries__categor_568a9f_idx"),
                    models.Index(fields=["priority"], name="ministries__priorit_7f75a8_idx"),
                    models.Index(fields=["status"], name="ministries__status_dde0bc_idx"),
                    models.Index(fields=["created_at"], name="ministries__created_1c9ea6_idx"),
                ],
            },
        ),
    ]
