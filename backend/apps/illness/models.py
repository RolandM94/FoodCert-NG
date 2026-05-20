from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


class SuspectedCondition(models.TextChoices):
    GENERAL_DIARRHOEA_VOMITING = "general_diarrhoea_vomiting", "General diarrhoea/vomiting"
    CHOLERA = "cholera", "Cholera"
    SHIGELLA = "shigella", "Shigella"
    HEPATITIS_A = "hepatitis_a", "Hepatitis A"
    INFECTED_SKIN_LESION = "infected_skin_lesion", "Infected skin lesion"
    AMOEBIC_DYSENTERY = "amoebic_dysentery", "Amoebic dysentery"
    TAENIA_SOLIUM = "taenia_solium", "Taenia solium"
    LASSA_FEVER = "lassa_fever", "Lassa fever"
    OTHER = "other", "Other"


class ClearanceStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    UNDER_REVIEW = "under_review", "Under Review"
    CLEARED = "cleared", "Cleared"
    REJECTED = "rejected", "Rejected"
    CLEARANCE_REQUIRED = "clearance_required", "Clearance Required"


class IllnessReport(BaseModel):
    food_handler = models.ForeignKey("food_handlers.FoodHandlerProfile", on_delete=models.PROTECT, related_name="illness_reports")
    employer = models.ForeignKey("employers.Employer", on_delete=models.SET_NULL, null=True, blank=True, related_name="illness_reports")
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reported_illnesses")
    symptoms = models.JSONField(default=dict, blank=True)
    suspected_condition = models.CharField(max_length=64, choices=SuspectedCondition.choices, blank=True)
    symptom_start_date = models.DateField(null=True, blank=True)
    symptom_end_date = models.DateField(null=True, blank=True)
    exclusion_start_date = models.DateField(default=timezone.localdate)
    earliest_return_date = models.DateField(null=True, blank=True)
    clearance_required = models.BooleanField(default=True)
    clearance_status = models.CharField(max_length=32, choices=ClearanceStatus.choices, default=ClearanceStatus.PENDING, db_index=True)
    reviewed_by_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_illness_reports",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    cleared_at = models.DateTimeField(null=True, blank=True)
    return_to_work_certificate_number = models.CharField(max_length=80, blank=True, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["food_handler"]),
            models.Index(fields=["employer"]),
            models.Index(fields=["reported_by"]),
            models.Index(fields=["clearance_status"]),
            models.Index(fields=["suspected_condition"]),
            models.Index(fields=["exclusion_start_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.food_handler} - {self.clearance_status}"
