from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("employers", "0001_initial"),
        ("food_handlers", "0001_initial"),
        ("locations", "0001_initial"),
        ("organizations", "0002_organization_address_organization_email_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="EmployerProfile",
            new_name="Employer",
        ),
        migrations.AlterField(
            model_name="employer",
            name="compliance_status",
            field=models.CharField(
                choices=[
                    ("compliant", "Compliant"),
                    ("non_compliant", "Non Compliant"),
                    ("under_review", "Under Review"),
                ],
                db_index=True,
                default="under_review",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="employer",
            name="subscription_status",
            field=models.CharField(
                choices=[
                    ("active", "Active"),
                    ("expired", "Expired"),
                    ("cancelled", "Cancelled"),
                    ("never_subscribed", "Never Subscribed"),
                ],
                db_index=True,
                default="never_subscribed",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="employer",
            name="organization",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="employer",
                to="organizations.organization",
            ),
        ),
        migrations.AlterField(
            model_name="employer",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="employer",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
