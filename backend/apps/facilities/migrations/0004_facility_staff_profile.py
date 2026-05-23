from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("facilities", "0003_accreditation_documents_and_renewals"),
        ("organizations", "0004_alter_organizationunit_unit_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="FacilityStaffProfile",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "staff_type",
                    models.CharField(
                        choices=[
                            ("facility_admin", "Facility Admin"),
                            ("doctor", "Doctor"),
                            ("lab_staff", "Lab Staff"),
                            ("records_staff", "Medical Records Staff"),
                            ("finance_user", "Finance/Settlement User"),
                            ("viewer", "Viewer"),
                        ],
                        db_index=True,
                        max_length=32,
                    ),
                ),
                ("professional_registration_number", models.CharField(blank=True, max_length=120)),
                ("digital_signature_url", models.URLField(blank=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                (
                    "department",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="facility_staff_profiles",
                        to="organizations.organizationunit",
                    ),
                ),
                (
                    "facility",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="staff_profiles",
                        to="facilities.medicalfacility",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="facility_staff_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["user__email"],
            },
        ),
        migrations.AddIndex(
            model_name="facilitystaffprofile",
            index=models.Index(fields=["facility"], name="facilities__facilit_9f59e7_idx"),
        ),
        migrations.AddIndex(
            model_name="facilitystaffprofile",
            index=models.Index(fields=["department"], name="facilities__departm_e5b539_idx"),
        ),
        migrations.AddIndex(
            model_name="facilitystaffprofile",
            index=models.Index(fields=["staff_type"], name="facilities__staff_t_45e5b6_idx"),
        ),
        migrations.AddIndex(
            model_name="facilitystaffprofile",
            index=models.Index(fields=["is_active"], name="facilities__is_acti_2d674b_idx"),
        ),
    ]
