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
    SAMPLE_COLLECTED = "sample_collected", "Sample Collected"
    IN_PROGRESS = "in_progress", "In Progress"
    POSITIVE = "positive", "Positive"
    NEGATIVE = "negative", "Negative"
    INCONCLUSIVE = "inconclusive", "Inconclusive"
    REPEAT_REQUIRED = "repeat_required", "Repeat Required"
    REVIEWED = "reviewed", "Reviewed"


class LabTest(BaseModel):
    assessment = models.ForeignKey("assessments.MedicalAssessment", on_delete=models.CASCADE, related_name="lab_tests")
    test_type = models.CharField(max_length=64, choices=LabTestType.choices)
    test_name = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=32, choices=LabTestStatus.choices, default=LabTestStatus.REQUESTED, db_index=True)
    result_value = models.CharField(max_length=255, blank=True)
    result_notes = models.TextField(blank=True)
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
    resulted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["assessment"]),
            models.Index(fields=["test_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["requested_at"]),
        ]

    def __str__(self) -> str:
        return self.test_name or self.get_test_type_display()
