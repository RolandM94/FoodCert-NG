from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("standards", "0010_meindicatorcalculationlog"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="meindicatorvalue",
            name="original_calculated_value",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name="meindicatorvalue",
            name="override_reason",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="meindicatorvalue",
            name="overridden_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="meindicatorvalue",
            name="overridden_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="overridden_me_indicator_values", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="meindicatorvalue",
            name="overridden_value",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True),
        ),
    ]
