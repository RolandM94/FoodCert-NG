from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("facilities", "0002_facility_profile_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="facilityaccreditationapplication",
            name="application_status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("submitted", "Submitted"),
                    ("under_review", "Under Review"),
                    ("more_information_required", "More Information Required"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                    ("suspended", "Suspended"),
                    ("expired", "Expired"),
                    ("reaccreditation_due", "Re-accreditation Due"),
                ],
                db_index=True,
                default="draft",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="medicalfacility",
            name="accreditation_status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("submitted", "Submitted"),
                    ("under_review", "Under Review"),
                    ("more_information_required", "More Information Required"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                    ("suspended", "Suspended"),
                    ("expired", "Expired"),
                    ("reaccreditation_due", "Re-accreditation Due"),
                ],
                db_index=True,
                default="draft",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="facilityaccreditationapplication",
            name="has_confidentiality_policy",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="facilityaccreditationapplication",
            name="has_infection_prevention_readiness",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="facilityaccreditationapplication",
            name="has_laboratory_capacity",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="facilityaccreditationapplication",
            name="has_valid_doctor_credentials",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="facilityaccreditationapplication",
            name="has_valid_facility_license",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="facilityaccreditationapplication",
            name="has_valid_lab_staff_credentials",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="facilityaccreditationapplication",
            name="is_renewal",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name="facilityaccreditationapplication",
            name="renewal_of",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="renewal_applications",
                to="facilities.facilityaccreditationapplication",
            ),
        ),
        migrations.CreateModel(
            name="FacilityDocument",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "document_type",
                    models.CharField(
                        choices=[
                            ("facility_license", "Facility license"),
                            ("corporate_registration", "Corporate registration"),
                            ("medical_director_credential", "Medical director credential"),
                            ("doctor_license", "Doctor license"),
                            ("lab_staff_credential", "Lab staff credential"),
                            ("laboratory_license", "Laboratory license"),
                            ("documentation_policy", "Documentation policy"),
                            ("confidentiality_policy", "Confidentiality policy"),
                            ("facility_photo", "Facility photo"),
                            ("equipment_list", "Equipment list"),
                            ("digital_readiness", "Digital readiness"),
                            ("bank_details", "Bank details"),
                            ("state_required_form", "State required form"),
                            ("other", "Other"),
                        ],
                        db_index=True,
                        max_length=64,
                    ),
                ),
                ("file", models.FileField(upload_to="facility_documents/")),
                (
                    "status",
                    models.CharField(
                        choices=[("uploaded", "Uploaded"), ("accepted", "Accepted"), ("rejected", "Rejected")],
                        db_index=True,
                        default="uploaded",
                        max_length=32,
                    ),
                ),
                ("review_comment", models.TextField(blank=True)),
                (
                    "accreditation_application",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="facilities.facilityaccreditationapplication",
                    ),
                ),
                (
                    "facility",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="facilities.medicalfacility",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="uploaded_facility_documents",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="facilitydocument",
            index=models.Index(fields=["facility"], name="facilities__facilit_55cedd_idx"),
        ),
        migrations.AddIndex(
            model_name="facilitydocument",
            index=models.Index(fields=["accreditation_application"], name="facilities__accredi_01f7b6_idx"),
        ),
        migrations.AddIndex(
            model_name="facilitydocument",
            index=models.Index(fields=["document_type"], name="facilities__documen_8e32b4_idx"),
        ),
        migrations.AddIndex(
            model_name="facilitydocument",
            index=models.Index(fields=["status"], name="facilities__status_5d924c_idx"),
        ),
    ]
