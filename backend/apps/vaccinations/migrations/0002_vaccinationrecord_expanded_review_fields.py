from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vaccinations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(model_name="vaccinationrecord", name="batch_number", field=models.CharField(blank=True, max_length=120)),
        migrations.AddField(model_name="vaccinationrecord", name="brand_name", field=models.CharField(blank=True, max_length=160)),
        migrations.AddField(model_name="vaccinationrecord", name="certificate_upload", field=models.FileField(blank=True, upload_to="vaccination_certificates/")),
        migrations.AddField(model_name="vaccinationrecord", name="next_dose_date", field=models.DateField(blank=True, null=True)),
        migrations.AddField(model_name="vaccinationrecord", name="vaccination_facility_address", field=models.TextField(blank=True)),
        migrations.AddField(model_name="vaccinationrecord", name="vaccination_facility_name", field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name="vaccinationrecord", name="vaccinator_name", field=models.CharField(blank=True, max_length=160)),
        migrations.AlterField(
            model_name="vaccinationrecord",
            name="status",
            field=models.CharField(
                choices=[
                    ("valid", "Valid"),
                    ("expired", "Expired"),
                    ("missing", "Missing"),
                    ("incomplete", "Incomplete"),
                    ("prescribed", "Prescribed"),
                    ("administered", "Administered"),
                    ("doctor_cleared", "Doctor Cleared"),
                    ("second_dose_due", "Second Dose Due"),
                ],
                db_index=True,
                default="missing",
                max_length=32,
            ),
        ),
    ]
