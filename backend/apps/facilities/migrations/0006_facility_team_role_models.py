from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounts", "0009_alter_userinvite_status"),
        ("facilities", "0005_rename_facilities__facilit_55cedd_idx_facilities__facilit_22951e_idx_and_more"),
        ("organizations", "0006_seed_legacy_roles_and_memberships"),
    ]

    operations = [
        migrations.CreateModel(
            name="FacilityRole",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "professional_category",
                    models.CharField(
                        choices=[
                            ("admin", "Admin"),
                            ("doctor", "Doctor"),
                            ("lab_technician", "Lab Technician"),
                            ("lab_scientist", "Lab Scientist"),
                            ("lab_supervisor", "Lab Supervisor"),
                            ("front_desk", "Front Desk"),
                            ("finance", "Finance"),
                            ("records", "Records"),
                            ("compliance", "Compliance"),
                            ("viewer", "Viewer / Auditor"),
                        ],
                        db_index=True,
                        default="admin",
                        max_length=32,
                    ),
                ),
                ("is_system_default", models.BooleanField(db_index=True, default=False)),
                ("is_custom", models.BooleanField(db_index=True, default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="facility_roles_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "facility",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="facility_roles",
                        to="facilities.medicalfacility",
                    ),
                ),
                (
                    "organization_role",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="facility_roles",
                        to="organizations.role",
                    ),
                ),
            ],
            options={
                "ordering": ["facility__facility_name", "name"],
            },
        ),
        migrations.CreateModel(
            name="FacilityRolePermission",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("permission_key", models.CharField(db_index=True, max_length=150)),
                ("allowed", models.BooleanField(default=True)),
                (
                    "role",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="permissions",
                        to="facilities.facilityrole",
                    ),
                ),
            ],
            options={
                "ordering": ["role__name", "permission_key"],
            },
        ),
        migrations.AddField(
            model_name="facilitystaffprofile",
            name="accepted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="facilitystaffprofile",
            name="invited_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="facility_team_members_invited",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="facilitystaffprofile",
            name="professional_category",
            field=models.CharField(
                choices=[
                    ("admin", "Admin"),
                    ("doctor", "Doctor"),
                    ("lab_technician", "Lab Technician"),
                    ("lab_scientist", "Lab Scientist"),
                    ("lab_supervisor", "Lab Supervisor"),
                    ("front_desk", "Front Desk"),
                    ("finance", "Finance"),
                    ("records", "Records"),
                    ("compliance", "Compliance"),
                    ("viewer", "Viewer / Auditor"),
                ],
                db_index=True,
                default="admin",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="facilitystaffprofile",
            name="role",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="team_members",
                to="facilities.facilityrole",
            ),
        ),
        migrations.AddField(
            model_name="facilitystaffprofile",
            name="status",
            field=models.CharField(
                choices=[
                    ("invited", "Invited"),
                    ("pending_profile", "Pending Profile Completion"),
                    ("pending_license_verification", "Pending License Verification"),
                    ("active", "Active"),
                    ("suspended", "Suspended"),
                    ("removed", "Removed"),
                ],
                db_index=True,
                default="active",
                max_length=40,
            ),
        ),
        migrations.CreateModel(
            name="FacilityInvitation",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "professional_category",
                    models.CharField(
                        choices=[
                            ("admin", "Admin"),
                            ("doctor", "Doctor"),
                            ("lab_technician", "Lab Technician"),
                            ("lab_scientist", "Lab Scientist"),
                            ("lab_supervisor", "Lab Supervisor"),
                            ("front_desk", "Front Desk"),
                            ("finance", "Finance"),
                            ("records", "Records"),
                            ("compliance", "Compliance"),
                            ("viewer", "Viewer / Auditor"),
                        ],
                        db_index=True,
                        default="admin",
                        max_length=32,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("invited", "Invited"),
                            ("pending_profile", "Pending Profile Completion"),
                            ("pending_license_verification", "Pending License Verification"),
                            ("active", "Active"),
                            ("suspended", "Suspended"),
                            ("removed", "Removed"),
                        ],
                        db_index=True,
                        default="invited",
                        max_length=40,
                    ),
                ),
                (
                    "facility",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="team_invitations",
                        to="facilities.medicalfacility",
                    ),
                ),
                (
                    "invite",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="facility_invitation",
                        to="accounts.userinvite",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="invitations",
                        to="facilities.facilityrole",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="FacilityProfessionalProfile",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "professional_category",
                    models.CharField(
                        choices=[
                            ("admin", "Admin"),
                            ("doctor", "Doctor"),
                            ("lab_technician", "Lab Technician"),
                            ("lab_scientist", "Lab Scientist"),
                            ("lab_supervisor", "Lab Supervisor"),
                            ("front_desk", "Front Desk"),
                            ("finance", "Finance"),
                            ("records", "Records"),
                            ("compliance", "Compliance"),
                            ("viewer", "Viewer / Auditor"),
                        ],
                        db_index=True,
                        max_length=32,
                    ),
                ),
                ("license_number", models.CharField(blank=True, max_length=120)),
                ("license_issuing_body", models.CharField(blank=True, max_length=255)),
                ("license_document_url", models.URLField(blank=True)),
                (
                    "verification_status",
                    models.CharField(
                        choices=[
                            ("not_required", "Not Required"),
                            ("pending", "Pending"),
                            ("verified", "Verified"),
                            ("rejected", "Rejected"),
                        ],
                        db_index=True,
                        default="not_required",
                        max_length=32,
                    ),
                ),
                (
                    "facility",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="professional_profiles",
                        to="facilities.medicalfacility",
                    ),
                ),
                (
                    "team_member",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="professional_profile",
                        to="facilities.facilitystaffprofile",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="facility_professional_profiles",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["facility__facility_name", "user__email"],
            },
        ),
        migrations.AddConstraint(
            model_name="facilityrole",
            constraint=models.UniqueConstraint(fields=("facility", "name"), name="unique_facility_role_name"),
        ),
        migrations.AddConstraint(
            model_name="facilityrolepermission",
            constraint=models.UniqueConstraint(fields=("role", "permission_key"), name="unique_facility_role_permission"),
        ),
        migrations.AddConstraint(
            model_name="facilityprofessionalprofile",
            constraint=models.UniqueConstraint(fields=("user", "facility"), name="unique_facility_professional_profile"),
        ),
        migrations.AddIndex(
            model_name="facilityrole",
            index=models.Index(fields=["facility"], name="facilities__facilit_fc7708_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityrole",
            index=models.Index(fields=["professional_category"], name="facilities__profess_69f176_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityrole",
            index=models.Index(fields=["organization_role"], name="facilities__organiz_16d263_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityrole",
            index=models.Index(fields=["is_system_default"], name="facilities__is_syst_61ff47_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityrole",
            index=models.Index(fields=["is_custom"], name="facilities__is_cust_2b444e_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityrolepermission",
            index=models.Index(fields=["role"], name="facilities__role_id_ce2b6d_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityrolepermission",
            index=models.Index(fields=["permission_key"], name="facilities__permiss_8f7a6d_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityrolepermission",
            index=models.Index(fields=["allowed"], name="facilities__allowed_6e752c_idx"),
        ),
        migrations.AddIndex(
            model_name="facilitystaffprofile",
            index=models.Index(fields=["role"], name="facilities__role_id_bf93ef_idx"),
        ),
        migrations.AddIndex(
            model_name="facilitystaffprofile",
            index=models.Index(fields=["professional_category"], name="facilities__profess_27de17_idx"),
        ),
        migrations.AddIndex(
            model_name="facilitystaffprofile",
            index=models.Index(fields=["status"], name="facilities__status_5d4a6c_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityinvitation",
            index=models.Index(fields=["facility"], name="facilities__facilit_fea6bf_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityinvitation",
            index=models.Index(fields=["role"], name="facilities__role_id_99d0c1_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityinvitation",
            index=models.Index(fields=["professional_category"], name="facilities__profess_b29385_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityinvitation",
            index=models.Index(fields=["status"], name="facilities__status_32ec5d_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityprofessionalprofile",
            index=models.Index(fields=["user"], name="facilities__user_id_1f81a0_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityprofessionalprofile",
            index=models.Index(fields=["facility"], name="facilities__facilit_5e24b6_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityprofessionalprofile",
            index=models.Index(fields=["team_member"], name="facilities__team_me_ab8053_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityprofessionalprofile",
            index=models.Index(fields=["professional_category"], name="facilities__profess_1dcac7_idx"),
        ),
        migrations.AddIndex(
            model_name="facilityprofessionalprofile",
            index=models.Index(fields=["verification_status"], name="facilities__verific_5b80bd_idx"),
        ),
    ]
