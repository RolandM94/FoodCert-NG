from django.db import models

from apps.common.models import BaseModel


class OrganizationType(models.TextChoices):
    PLATFORM_OPERATOR = "platform_operator", "Platform Operator"
    FEDERAL_MINISTRY = "federal_ministry", "Federal Ministry"
    STATE_MINISTRY = "state_ministry", "State Ministry"
    EMPLOYER = "employer", "Employer"
    MEDICAL_FACILITY = "medical_facility", "Medical Facility"


class OrganizationStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    INACTIVE = "inactive", "Inactive"


class OrganizationUnitType(models.TextChoices):
    HEADQUARTERS = "headquarters", "Headquarters"
    DIRECTORATE = "directorate", "Directorate"
    DEPARTMENT = "department", "Department"
    UNIT = "unit", "Unit"
    BRANCH = "branch", "Branch"
    LAB_DEPARTMENT = "lab_department", "Lab Department"
    CLINICAL_DEPARTMENT = "clinical_department", "Clinical Department"
    RECORDS_DEPARTMENT = "records_department", "Records Department"
    LGA_OFFICE = "lga_office", "LGA Office"
    REGIONAL_OFFICE = "regional_office", "Regional Office"
    OTHER = "other", "Other"


class Organization(BaseModel):
    name = models.CharField(max_length=255)
    organization_type = models.CharField(max_length=32, choices=OrganizationType.choices)
    status = models.CharField(
        max_length=32,
        choices=OrganizationStatus.choices,
        default=OrganizationStatus.ACTIVE,
        db_index=True,
    )
    state = models.ForeignKey(
        "locations.State",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="organizations",
    )
    lga = models.ForeignKey(
        "locations.LGA",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="organizations",
    )
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["state"]),
            models.Index(fields=["lga"]),
        ]

    def __str__(self) -> str:
        return self.name


class OrganizationUnit(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="units")
    name = models.CharField(max_length=255)
    unit_type = models.CharField(max_length=32, choices=OrganizationUnitType.choices, default=OrganizationUnitType.UNIT, db_index=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children")
    description = models.TextField(blank=True)
    state = models.ForeignKey("locations.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="organization_units")
    lga = models.ForeignKey("locations.LGA", on_delete=models.SET_NULL, null=True, blank=True, related_name="organization_units")
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["organization__name", "name"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="unique_unit_name_per_organization"),
        ]
        indexes = [
            models.Index(fields=["organization"]),
            models.Index(fields=["unit_type"]),
            models.Index(fields=["parent"]),
            models.Index(fields=["state"]),
            models.Index(fields=["lga"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.organization.name} / {self.name}"
