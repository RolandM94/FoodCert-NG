from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("standards", "0009_kpi_calculation_metadata"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MEIndicatorCalculationLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
                ("calculated_value", models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True)),
                ("numerator_value", models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True)),
                ("denominator_value", models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True)),
                ("filters_used", models.JSONField(blank=True, default=dict)),
                ("policy_standard_code", models.CharField(blank=True, default="", max_length=64)),
                ("policy_standard_id", models.CharField(blank=True, default="", max_length=128)),
                ("calculation_status", models.CharField(choices=[("success", "Success"), ("failed", "Failed"), ("overridden", "Overridden")], db_index=True, default="success", max_length=16)),
                ("error_message", models.TextField(blank=True, default="")),
                ("source_record_count", models.PositiveIntegerField(default=0)),
                ("snapshot_json", models.JSONField(blank=True, default=dict)),
                ("calculated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="me_indicator_calculation_logs", to=settings.AUTH_USER_MODEL)),
                ("indicator", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="calculation_logs", to="standards.meindicator")),
                ("policy_version", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="indicator_calculation_logs", to="standards.policyversion")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="meindicatorcalculationlog",
            index=models.Index(fields=["indicator", "period_start", "period_end"], name="standards_m_indicat_a3d92e_idx"),
        ),
        migrations.AddIndex(
            model_name="meindicatorcalculationlog",
            index=models.Index(fields=["calculation_status"], name="standards_m_calcula_9f0aa6_idx"),
        ),
        migrations.AddIndex(
            model_name="meindicatorcalculationlog",
            index=models.Index(fields=["policy_version"], name="standards_m_policy__4fb073_idx"),
        ),
    ]
