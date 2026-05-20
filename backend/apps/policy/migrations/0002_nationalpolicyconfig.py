from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("policy", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="NationalPolicyConfig",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("certificate_validity_months", models.PositiveIntegerField(default=12)),
                ("renewal_reminder_days", models.JSONField(default=list)),
                ("typhoid_validity_years", models.PositiveIntegerField(default=3)),
                ("hepatitis_a_second_dose_months", models.PositiveIntegerField(default=6)),
                ("nin_required", models.BooleanField(default=True)),
                ("payment_before_assessment_required", models.BooleanField(default=True)),
                ("state_validation_before_certificate_required", models.BooleanField(default=True)),
                ("public_qr_verification_enabled", models.BooleanField(default=True)),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="updated_national_policy_configs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
