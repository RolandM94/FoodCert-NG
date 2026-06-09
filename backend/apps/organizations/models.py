from django.db import models

from apps.common.models import BaseModel


class OrganizationType(models.TextChoices):
    PLATFORM_OPERATOR = "platform_operator", "Platform Operator"
    FEDERAL_MINISTRY = "federal_ministry", "Federal Ministry"
    STATE_MINISTRY = "state_ministry", "State Ministry"
    EMPLOYER = "employer", "Employer"
    MEDICAL_FACILITY = "medical_facility", "Medical Facility"


class OrganizationStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    PENDING_APPROVAL = "pending_approval", "Pending Approval"
    SUSPENDED = "suspended", "Suspended"
    INACTIVE = "inactive", "Inactive"
    ARCHIVED = "archived", "Archived"


class OrganizationUnitType(models.TextChoices):
    HEADQUARTERS = "headquarters", "Headquarters"
    DIRECTORATE = "directorate", "Directorate"
    DEPARTMENT = "department", "Department"
    UNIT = "unit", "Unit"
    DESK = "desk", "Desk"
    OFFICE = "office", "Office"
    BRANCH = "branch", "Branch"
    REGIONAL_OFFICE = "regional_office", "Regional Office"
    SITE = "site", "Site"
    OUTLET = "outlet", "Outlet"
    STORE = "store", "Store"
    LGA_OFFICE = "lga_office", "LGA Office"
    INSPECTORATE = "inspectorate", "Inspectorate"
    LAB_DEPARTMENT = "lab_department", "Lab Department"
    CLINICAL_DEPARTMENT = "clinical_department", "Clinical Department"
    MEDICAL_RECORDS_DEPARTMENT = "medical_records_department", "Medical Records Department"
    RECORDS_DEPARTMENT = "records_department", "Records Department"
    FINANCE_UNIT = "finance_unit", "Finance Unit"
    ADMINISTRATION_UNIT = "administration_unit", "Administration Unit"
    SUPPORT_UNIT = "support_unit", "Support Unit"
    TECHNICAL_UNIT = "technical_unit", "Technical Unit"
    OTHER = "other", "Other"


class OrganizationUnitStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    SUSPENDED = "suspended", "Suspended"
    CLOSED = "closed", "Closed"
    ARCHIVED = "archived", "Archived"


class RoleStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    DEPRECATED = "deprecated", "Deprecated"


class MembershipStatus(models.TextChoices):
    INVITED = "invited", "Invited"
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    REMOVED = "removed", "Removed"
    EXPIRED = "expired", "Expired"
    PENDING_VERIFICATION = "pending_verification", "Pending Verification"


class PermissionOverrideEffect(models.TextChoices):
    ALLOW = "allow", "Allow"
    DENY = "deny", "Deny"


class Organization(BaseModel):
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
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
    contact_person_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organizations_created",
    )

    class Meta:
        indexes = [
            models.Index(fields=["parent"]),
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
    manager = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_units",
    )
    description = models.TextField(blank=True)
    state = models.ForeignKey("locations.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="organization_units")
    lga = models.ForeignKey("locations.LGA", on_delete=models.SET_NULL, null=True, blank=True, related_name="organization_units")
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    status = models.CharField(
        max_length=32,
        choices=OrganizationUnitStatus.choices,
        default=OrganizationUnitStatus.ACTIVE,
        db_index=True,
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organization_units_created",
    )

    class Meta:
        ordering = ["organization__name", "name"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="unique_unit_name_per_organization"),
        ]
        indexes = [
            models.Index(fields=["organization"]),
            models.Index(fields=["unit_type"]),
            models.Index(fields=["parent"]),
            models.Index(fields=["manager"]),
            models.Index(fields=["state"]),
            models.Index(fields=["lga"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.organization.name} / {self.name}"


class Role(BaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    organization_type = models.CharField(max_length=50, choices=OrganizationType.choices, blank=True)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=True)
    is_custom_role = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=RoleStatus.choices, default=RoleStatus.ACTIVE, db_index=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roles_created",
    )

    class Meta:
        ordering = ["organization_type", "name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["organization_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_system_role"]),
            models.Index(fields=["is_custom_role"]),
        ]

    def __str__(self) -> str:
        return self.name


class Permission(BaseModel):
    code = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=255)
    module = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    is_sensitive = models.BooleanField(default=False)

    class Meta:
        ordering = ["module", "code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["module"]),
            models.Index(fields=["is_sensitive"]),
        ]

    def __str__(self) -> str:
        return self.code


class RolePermission(BaseModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="role_permissions")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["role", "permission"], name="unique_role_permission"),
        ]
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["permission"]),
        ]

    def __str__(self) -> str:
        return f"{self.role.code}: {self.permission.code}"


class OrganizationMembership(BaseModel):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="memberships")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="memberships")
    unit = models.ForeignKey(OrganizationUnit, on_delete=models.SET_NULL, null=True, blank=True, related_name="memberships")
    unit_restricted = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=MembershipStatus.choices, default=MembershipStatus.ACTIVE, db_index=True)
    invited_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="memberships_invited",
    )
    joined_at = models.DateTimeField(null=True, blank=True)
    last_active_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["organization__name", "user__email"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                condition=models.Q(status=MembershipStatus.ACTIVE),
                name="unique_active_membership_per_org",
            ),
        ]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["organization"]),
            models.Index(fields=["role"]),
            models.Index(fields=["unit"]),
            models.Index(fields=["status"]),
            models.Index(fields=["unit_restricted"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} @ {self.organization} ({self.role.code})"


class PermissionOverride(BaseModel):
    membership = models.ForeignKey(OrganizationMembership, on_delete=models.CASCADE, related_name="permission_overrides")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="permission_overrides")
    effect = models.CharField(max_length=20, choices=PermissionOverrideEffect.choices)
    reason = models.TextField(blank=True)
    granted_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="permission_overrides_granted",
    )
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["membership", "permission"], name="unique_membership_permission_override"),
        ]
        indexes = [
            models.Index(fields=["membership"]),
            models.Index(fields=["permission"]),
            models.Index(fields=["effect"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.membership}: {self.effect} {self.permission.code}"
