from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0001_initial"),
        ("organizations", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("reports", "0011_flexible_dashboard_architecture"),
    ]

    operations = [
        migrations.CreateModel(
            name="DashboardAlertRule",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("account_type", models.CharField(choices=[("federal", "Federal Ministry"), ("state", "State Ministry"), ("employer", "Employer / Food Business"), ("medical_facility", "Medical Facility"), ("platform_admin", "Platform Admin")], db_index=True, max_length=32)),
                ("scope_type", models.CharField(choices=[("private", "Private"), ("organization", "Organization"), ("role_based", "Role Based"), ("selected_users", "Selected Users"), ("federal_only", "Federal Only"), ("state_only", "State Only"), ("public", "Public")], db_index=True, default="private", max_length=32)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("metric_key", models.CharField(max_length=120)),
                ("metric_label", models.CharField(blank=True, max_length=255)),
                ("operator", models.CharField(choices=[("gt", "Greater Than"), ("gte", "Greater Than or Equal"), ("lt", "Less Than"), ("lte", "Less Than or Equal"), ("eq", "Equal"), ("neq", "Not Equal")], default="lt", max_length=8)),
                ("threshold_value", models.DecimalField(decimal_places=4, max_digits=18)),
                ("notification_channels", models.JSONField(blank=True, default=list)),
                ("recipient_user_ids", models.JSONField(blank=True, default=list)),
                ("required_permissions", models.JSONField(blank=True, default=list)),
                ("privacy_metadata", models.JSONField(blank=True, default=dict)),
                ("last_evaluated_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("last_triggered_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("trigger_count", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="dashboard_alert_rules", to="organizations.organization")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dashboard_alert_rules", to=settings.AUTH_USER_MODEL)),
                ("state", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="dashboard_alert_rules", to="locations.state")),
                ("widget", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alert_rules", to="reports.analyticswidget")),
            ],
            options={"ordering": ["account_type", "name"]},
        ),
        migrations.CreateModel(
            name="DashboardAlertEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(choices=[("triggered", "Triggered"), ("resolved", "Resolved"), ("no_data", "No Data")], db_index=True, max_length=24)),
                ("observed_value", models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True)),
                ("threshold_value", models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True)),
                ("notification_count", models.PositiveIntegerField(default=0)),
                ("notified_channels", models.JSONField(blank=True, default=list)),
                ("message", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("rule", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="history", to="reports.dashboardalertrule")),
                ("widget", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alert_events", to="reports.analyticswidget")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(model_name="dashboardalertrule", index=models.Index(fields=["owner", "is_active"], name="reports_das_owner_9f37b8_idx")),
        migrations.AddIndex(model_name="dashboardalertrule", index=models.Index(fields=["organization", "is_active"], name="reports_das_organiz_0cfa48_idx")),
        migrations.AddIndex(model_name="dashboardalertrule", index=models.Index(fields=["state", "is_active"], name="reports_das_state_i_b3370e_idx")),
        migrations.AddIndex(model_name="dashboardalertrule", index=models.Index(fields=["account_type", "scope_type"], name="reports_das_account_2986db_idx")),
        migrations.AddIndex(model_name="dashboardalertrule", index=models.Index(fields=["widget", "is_active"], name="reports_das_widget__c0e314_idx")),
        migrations.AddIndex(model_name="dashboardalertrule", index=models.Index(fields=["last_triggered_at"], name="reports_das_last_tr_27daa8_idx")),
        migrations.AddIndex(model_name="dashboardalertevent", index=models.Index(fields=["rule", "created_at"], name="reports_das_rule_id_bf3d72_idx")),
        migrations.AddIndex(model_name="dashboardalertevent", index=models.Index(fields=["widget", "created_at"], name="reports_das_widget__0afcbd_idx")),
        migrations.AddIndex(model_name="dashboardalertevent", index=models.Index(fields=["status", "created_at"], name="reports_das_status__2dfa3d_idx")),
    ]
