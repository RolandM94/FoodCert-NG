from django.db import migrations, models


def migrate_kpi_input_modes(apps, schema_editor):
    MEIndicator = apps.get_model("standards", "MEIndicator")
    MEIndicator.objects.filter(input_mode="automated").update(input_mode="automatic")


class Migration(migrations.Migration):

    dependencies = [
        ("standards", "0007_food_handlers_kpi_engine_contract"),
    ]

    operations = [
        migrations.RunPython(migrate_kpi_input_modes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="meindicator",
            name="input_mode",
            field=models.CharField(
                choices=[
                    ("automatic", "Automatic"),
                    ("manual", "Manual"),
                    ("imported", "Imported"),
                    ("hybrid", "Hybrid"),
                ],
                default="manual",
                max_length=16,
            ),
        ),
    ]
