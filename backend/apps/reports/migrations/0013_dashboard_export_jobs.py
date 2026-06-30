from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("reports", "0012_dashboard_alert_rules"),
    ]

    operations = [
        migrations.CreateModel(
            name="DashboardExportJob",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("block_id", models.CharField(blank=True, max_length=64)),
                ("export_format", models.CharField(db_index=True, max_length=16)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("processing", "Processing"), ("completed", "Completed"), ("failed", "Failed")], db_index=True, default="pending", max_length=24)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("error_message", models.TextField(blank=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dashboard_export_jobs", to=settings.AUTH_USER_MODEL)),
                ("published_dashboard", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="export_jobs", to="reports.publisheddashboard")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(model_name="dashboardexportjob", index=models.Index(fields=["owner", "status"], name="reports_das_owner_d7b3a3_idx")),
        migrations.AddIndex(model_name="dashboardexportjob", index=models.Index(fields=["published_dashboard", "status"], name="reports_das_publis_f8c42f_idx")),
        migrations.AddIndex(model_name="dashboardexportjob", index=models.Index(fields=["export_format", "status"], name="reports_das_export_1841b3_idx")),
        migrations.AddIndex(model_name="dashboardexportjob", index=models.Index(fields=["completed_at"], name="reports_das_complet_c8bb5d_idx")),
    ]
