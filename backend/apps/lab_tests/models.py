from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


class LabTestType(models.TextChoices):
    STOOL_MICROSCOPY = "stool_microscopy", "Stool Microscopy"
    STOOL_CULTURE_SENSITIVITY = "stool_culture_sensitivity", "Stool Culture and Sensitivity"
    HEPATITIS_A_ANTIGEN = "hepatitis_a_antigen", "Hepatitis A Antigen"
    TYPHOID = "typhoid", "Typhoid"
    CHOLERA = "cholera", "Cholera"
    OTHER = "other", "Other"


class LabTestStatus(models.TextChoices):
    REQUESTED = "requested", "Requested"
    SAMPLE_COLLECTION_PENDING = "sample_collection_pending", "Sample Collection Pending"
    SAMPLE_COLLECTED = "sample_collected", "Sample Collected"
    IN_PROGRESS = "in_progress", "In Progress"
    RESULT_UPLOADED = "result_uploaded", "Result Uploaded"
    SUBMITTED_TO_DOCTOR = "submitted_to_doctor", "Submitted To Doctor"
    POSITIVE = "positive", "Positive"
    NEGATIVE = "negative", "Negative"
    INCONCLUSIVE = "inconclusive", "Inconclusive"
    REPEAT_REQUIRED = "repeat_required", "Repeat Required"
    REVIEWED = "reviewed", "Reviewed"


class LabReviewRecommendation(models.TextChoices):
    CLEARED = "cleared", "Cleared"
    REPEAT_TEST = "repeat_test", "Repeat Test"
    TEMPORARILY_NOT_FIT = "temporarily_not_fit", "Temporarily Not Fit"
    PUBLIC_HEALTH_CLEARANCE = "public_health_clearance", "Public Health Clearance"


class LabTest(BaseModel):
    assessment = models.ForeignKey("assessments.MedicalAssessment", on_delete=models.CASCADE, related_name="lab_tests")
    parent_lab_test = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="repeat_tests",
    )
    test_type = models.CharField(max_length=64, choices=LabTestType.choices)
    test_name = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=32, choices=LabTestStatus.choices, default=LabTestStatus.REQUESTED, db_index=True)
    repeat_required = models.BooleanField(default=False, db_index=True)
    repeat_reason = models.TextField(blank=True)
    is_flagged = models.BooleanField(default=False, db_index=True)
    result_value = models.CharField(max_length=255, blank=True)
    result_notes = models.TextField(blank=True)
    lab_staff_notes = models.TextField(blank=True)
    doctor_review_notes = models.TextField(blank=True)
    doctor_recommendation = models.CharField(max_length=64, choices=LabReviewRecommendation.choices, blank=True, db_index=True)
    result_document = models.FileField(upload_to="lab_results/", blank=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="requested_lab_tests")
    resulted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resulted_lab_tests",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_lab_tests",
    )
    requested_at = models.DateTimeField(default=timezone.now)
    sample_collected_at = models.DateTimeField(null=True, blank=True)
    resulted_at = models.DateTimeField(null=True, blank=True)
    submitted_to_doctor_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["assessment"]),
            models.Index(fields=["parent_lab_test"]),
            models.Index(fields=["test_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["repeat_required"]),
            models.Index(fields=["is_flagged"]),
            models.Index(fields=["doctor_recommendation"]),
            models.Index(fields=["requested_at"]),
            models.Index(fields=["sample_collected_at"], name="lab_tests_l_sample__b24f03_idx"),
            models.Index(fields=["submitted_to_doctor_at"], name="lab_tests_l_submitt_ab2192_idx"),
        ]

    def __str__(self) -> str:
        return self.test_name or self.get_test_type_display()

    def calculate_flagged(self) -> bool:
        return self.status in {LabTestStatus.POSITIVE, LabTestStatus.INCONCLUSIVE, LabTestStatus.REPEAT_REQUIRED}
