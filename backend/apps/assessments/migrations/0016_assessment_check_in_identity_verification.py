from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("assessments", "0015_assessment_template_inheritance_and_snapshots"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="medicalassessment",
            name="check_in_notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="medicalassessment",
            name="checked_in_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="medicalassessment",
            name="checked_in_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="checked_in_assessments", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="medicalassessment",
            name="identity_mismatch_flagged_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="medicalassessment",
            name="identity_mismatch_flagged_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="identity_mismatch_assessments", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="medicalassessment",
            name="identity_mismatch_reason",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="medicalassessment",
            name="identity_verification_status",
            field=models.CharField(choices=[("pending", "Pending"), ("verified", "Verified"), ("mismatch", "Mismatch Flagged")], db_index=True, default="pending", max_length=24),
        ),
        migrations.AddField(
            model_name="medicalassessment",
            name="identity_verified_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="medicalassessment",
            name="identity_verified_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="identity_verified_assessments", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="medicalassessment",
            name="status",
            field=models.CharField(choices=[("draft", "Draft"), ("payment_pending", "Payment Pending"), ("payment_confirmed", "Payment Confirmed"), ("appointment_booked", "Appointment Booked"), ("assessment_in_progress", "Assessment In Progress"), ("declaration_submitted", "Declaration Submitted"), ("declaration_validated", "Declaration Validated"), ("physical_exam_completed", "Physical Exam Completed"), ("lab_tests_pending", "Lab Tests Pending"), ("lab_results_reviewed", "Lab Results Reviewed"), ("vaccination_reviewed", "Vaccination Reviewed"), ("doctor_decision_pending", "Doctor Decision Pending"), ("fit", "Fit"), ("temporarily_not_fit", "Temporarily Not Fit"), ("not_fit", "Not Fit"), ("submitted_for_state_validation", "Submitted For State Validation"), ("state_clarification_requested", "State Clarification Requested"), ("state_clarification_responded", "State Clarification Responded"), ("approved_by_state", "Approved By State"), ("rejected_by_state", "Rejected By State"), ("certificate_issued", "Certificate Issued"), ("closed", "Closed")], db_index=True, default="draft", max_length=48),
        ),
        migrations.AddIndex(
            model_name="medicalassessment",
            index=models.Index(fields=["identity_verification_status"], name="assessments_identit_a8f4c8_idx"),
        ),
    ]
