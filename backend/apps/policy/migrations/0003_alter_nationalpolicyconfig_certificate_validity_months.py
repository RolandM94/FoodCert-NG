from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("policy", "0002_nationalpolicyconfig"),
    ]

    operations = [
        migrations.AlterField(
            model_name="nationalpolicyconfig",
            name="certificate_validity_months",
            field=models.PositiveIntegerField(default=6),
        ),
    ]
