from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessments", "0008_medicalassessment_decision_draft_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="medicalassessment",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("payment_pending", "Payment Pending"),
                    ("payment_confirmed", "Payment Confirmed"),
                    ("appointment_booked", "Appointment Booked"),
                    ("declaration_submitted", "Declaration Submitted"),
                    ("declaration_validated", "Declaration Validated"),
                    ("physical_exam_completed", "Physical Exam Completed"),
                    ("lab_tests_pending", "Lab Tests Pending"),
                    ("lab_results_reviewed", "Lab Results Reviewed"),
                    ("vaccination_reviewed", "Vaccination Reviewed"),
                    ("doctor_decision_pending", "Doctor Decision Pending"),
                    ("fit", "Fit"),
                    ("temporarily_not_fit", "Temporarily Not Fit"),
                    ("not_fit", "Not Fit"),
                    ("submitted_for_state_validation", "Submitted For State Validation"),
                    ("state_clarification_requested", "State Clarification Requested"),
                    ("state_clarification_responded", "State Clarification Responded"),
                    ("approved_by_state", "Approved By State"),
                    ("rejected_by_state", "Rejected By State"),
                    ("certificate_issued", "Certificate Issued"),
                    ("closed", "Closed"),
                ],
                db_index=True,
                default="draft",
                max_length=48,
            ),
        ),
    ]
