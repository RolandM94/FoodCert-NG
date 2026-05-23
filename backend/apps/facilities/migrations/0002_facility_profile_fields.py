from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("facilities", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="medicalfacility",
            name="is_active",
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AddField(
            model_name="medicalfacility",
            name="operating_hours",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="medicalfacility",
            name="service_capacity",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="medicalfacility",
            name="ward",
            field=models.CharField(blank=True, max_length=120),
        ),
    ]
