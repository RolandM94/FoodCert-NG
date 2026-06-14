import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("inspections", "0007_enforcementnotice_enforcementcase_and_more"),
        ("locations", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="InspectionSettingsPolicy",
            fields=[
                ("id", models.UUIDField(default=django.db.models.fields.UUIDField, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("allow_offline_inspections", models.BooleanField(default=True)),
                ("requires_gps_by_default", models.BooleanField(default=False)),
                ("requires_inspector_signature", models.BooleanField(default=False)),
                ("requires_employer_signature", models.BooleanField(default=False)),
                ("auto_open_case_for_high", models.BooleanField(default=True)),
                ("auto_open_case_for_critical", models.BooleanField(default=True)),
                ("auto_require_followup_for_high", models.BooleanField(default=True)),
                ("auto_require_followup_for_critical", models.BooleanField(default=True)),
                ("auto_close_passed_inspections", models.BooleanField(default=False)),
                ("default_templates_json", models.JSONField(blank=True, default=dict, help_text="Map of inspection_type -> template_id")),
                ("severity_levels_json", models.JSONField(blank=True, default=list, help_text="List of severity level configs")),
                ("corrective_deadlines_json", models.JSONField(blank=True, default=list, help_text="List of deadline rules")),
                ("notice_rules_json", models.JSONField(blank=True, default=list, help_text="Notice generation rules by severity")),
                ("escalation_rules_json", models.JSONField(blank=True, default=list, help_text="Escalation trigger rules")),
                ("score_thresholds_json", models.JSONField(blank=True, default=dict, help_text="Score range -> outcome mapping")),
                ("reminder_rules_json", models.JSONField(blank=True, default=dict, help_text="Reminder schedule config")),
                ("state", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="inspection_settings", to="locations.state")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="inspection_settings_updated", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Inspection Settings Policy",
                "verbose_name_plural": "Inspection Settings Policies",
            },
        ),
    ]
