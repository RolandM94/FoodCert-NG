from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("settlements", "0002_alter_settlement_assessment"),
    ]

    operations = [
        migrations.AddField(
            model_name="settlement",
            name="dispute_status",
            field=models.CharField(
                choices=[
                    ("none", "None"),
                    ("open", "Open"),
                    ("under_review", "Under Review"),
                    ("resolved", "Resolved"),
                    ("rejected", "Rejected"),
                ],
                db_index=True,
                default="none",
                max_length=24,
            ),
        ),
        migrations.AddField(
            model_name="settlement",
            name="dispute_reason",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="settlement",
            name="disputed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="settlement",
            name="dispute_resolution",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="settlement",
            name="disputed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="settlement_disputes",
                to="accounts.user",
            ),
        ),
        migrations.AddIndex(
            model_name="settlement",
            index=models.Index(fields=["dispute_status"], name="settlements_dispute_4d31cc_idx"),
        ),
    ]
