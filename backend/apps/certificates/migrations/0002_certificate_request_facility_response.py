from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("certificates", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="certificaterequest",
            name="facility_response",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="certificaterequest",
            name="facility_responded_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="certificaterequest",
            name="facility_responded_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="facility_certificate_request_responses",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
