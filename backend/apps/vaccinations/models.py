from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


class VaccineType(models.TextChoices):
    TYPHOID = "typhoid", "Typhoid"
    HEPATITIS_A = "hepatitis_a", "Hepatitis A"
    OTHER = "other", "Other"


class VaccinationStatus(models.TextChoices):
    VALID = "valid", "Valid"
    EXPIRED = "expired", "Expired"
    MISSING = "missing", "Missing"
    DOCTOR_CLEARED = "doctor_cleared", "Doctor Cleared"
    SECOND_DOSE_DUE = "second_dose_due", "Second Dose Due"


class VaccinationRecord(BaseModel):
    food_handler = models.ForeignKey("food_handlers.FoodHandlerProfile", on_delete=models.CASCADE, related_name="vaccinations")
    assessment = models.ForeignKey(
        "assessments.MedicalAssessment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vaccinations",
    )
    vaccine_type = models.CharField(max_length=32, choices=VaccineType.choices)
    vaccine_name = models.CharField(max_length=160, blank=True)
    dose_number = models.PositiveSmallIntegerField(default=1)
    date_administered = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=VaccinationStatus.choices, default=VaccinationStatus.MISSING, db_index=True)
    doctor_clearance = models.BooleanField(default=False)
    reminder_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="recorded_vaccinations")
    reviewed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-date_administered", "-created_at"]
        indexes = [
            models.Index(fields=["food_handler"]),
            models.Index(fields=["assessment"]),
            models.Index(fields=["vaccine_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["expiry_date"]),
        ]

    def derive_dates_and_status(self, *, typhoid_validity_years=3, hepatitis_a_second_dose_months=6):
        if self.vaccine_type == VaccineType.TYPHOID and self.date_administered and not self.expiry_date:
            self.expiry_date = self.date_administered + timedelta(days=365 * typhoid_validity_years)
        if self.vaccine_type == VaccineType.HEPATITIS_A and self.date_administered and self.dose_number == 1:
            self.reminder_date = self.date_administered + timedelta(days=30 * hepatitis_a_second_dose_months)
        today = timezone.localdate()
        if self.doctor_clearance:
            self.status = VaccinationStatus.DOCTOR_CLEARED
        elif not self.date_administered:
            self.status = VaccinationStatus.MISSING
        elif self.expiry_date and self.expiry_date < today:
            self.status = VaccinationStatus.EXPIRED
        elif self.vaccine_type == VaccineType.HEPATITIS_A and self.dose_number == 1:
            self.status = VaccinationStatus.SECOND_DOSE_DUE
        else:
            self.status = VaccinationStatus.VALID
