from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import UUIDModel, TimestampedModel


class UserRole(models.TextChoices):
    SUPER_ADMIN = "super_admin", "Super Admin"
    FEDERAL_ADMIN = "federal_admin", "Federal Admin"
    STATE_ADMIN = "state_admin", "State Ministry Admin"
    FACILITY_ADMIN = "facility_admin", "Medical Facility Admin"
    DOCTOR = "doctor", "Doctor"
    LAB_STAFF = "lab_staff", "Lab Staff"
    EMPLOYER = "employer", "Employer"
    FOOD_HANDLER = "food_handler", "Food Handler"
    INSPECTOR = "inspector", "Inspector"


class UserStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    SUSPENDED = "suspended", "Suspended"


class EmployerStaffRole(models.TextChoices):
    EMPLOYER_ADMIN = "employer_admin", "Employer Admin"
    COMPLIANCE_OFFICER = "compliance_officer", "Compliance Officer"
    BRANCH_MANAGER = "branch_manager", "Branch Manager"
    FINANCE_USER = "finance_user", "Finance User"


class User(UUIDModel, TimestampedModel, AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=32, blank=True)
    role = models.CharField(
        max_length=32,
        choices=UserRole.choices,
        default=UserRole.FOOD_HANDLER,
        db_index=True,
    )
    status = models.CharField(
        max_length=16,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
        db_index=True,
    )
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    unit = models.ForeignKey(
        "organizations.OrganizationUnit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )
    unit_restricted = models.BooleanField(default=False)
    employer_staff_role = models.CharField(max_length=32, choices=EmployerStaffRole.choices, blank=True, db_index=True)
    state = models.ForeignKey(
        "locations.State",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    REQUIRED_FIELDS = ["email"]

    class Meta:
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["status"]),
            models.Index(fields=["organization"]),
            models.Index(fields=["unit"]),
            models.Index(fields=["state"]),
        ]

    def __str__(self) -> str:
        return self.get_full_name() or self.username

    @property
    def current_membership(self):
        return self.memberships.select_related("organization", "role", "unit").filter(status="active").first()

    @property
    def current_organization(self):
        membership = self.current_membership
        return membership.organization if membership else self.organization

    @property
    def current_role(self):
        membership = self.current_membership
        return membership.role if membership else None

    @property
    def current_unit(self):
        membership = self.current_membership
        return membership.unit if membership else self.unit

    @property
    def is_unit_restricted(self):
        membership = self.current_membership
        return membership.unit_restricted if membership else self.unit_restricted


class InviteStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    EXPIRED = "expired", "Expired"
    REVOKED = "revoked", "Revoked"
    FAILED = "failed", "Failed"


class UserInvite(UUIDModel, TimestampedModel):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="invites")
    unit = models.ForeignKey("organizations.OrganizationUnit", on_delete=models.SET_NULL, null=True, blank=True, related_name="invites")
    unit_restricted = models.BooleanField(default=False)
    invited_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="sent_invites")
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    role = models.CharField(max_length=32, choices=UserRole.choices, db_index=True)
    employer_staff_role = models.CharField(max_length=32, choices=EmployerStaffRole.choices, blank=True, db_index=True)
    ministry_staff_role = models.CharField(max_length=64, blank=True, db_index=True)
    facility_staff_type = models.CharField(max_length=64, blank=True, db_index=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=InviteStatus.choices, default=InviteStatus.PENDING, db_index=True)
    token = models.CharField(max_length=128, unique=True, db_index=True)
    accepted_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_invites",
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization"]),
            models.Index(fields=["unit"]),
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["status"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.email} -> {self.organization} ({self.role})"
