from django.db import migrations
from django.utils import timezone


LEGACY_ROLES = {
    "super_admin": ("Super Admin", "platform_operator"),
    "federal_admin": ("Federal Admin", "federal_ministry"),
    "state_admin": ("State Ministry Admin", "state_ministry"),
    "facility_admin": ("Medical Facility Admin", "medical_facility"),
    "doctor": ("Doctor", "medical_facility"),
    "lab_staff": ("Lab Staff", "medical_facility"),
    "employer": ("Employer", "employer"),
    "food_handler": ("Food Handler", ""),
    "inspector": ("Inspector", "state_ministry"),
}


def seed_legacy_roles_and_memberships(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Role = apps.get_model("organizations", "Role")
    OrganizationMembership = apps.get_model("organizations", "OrganizationMembership")

    roles = {}
    for code, (name, organization_type) in LEGACY_ROLES.items():
        role, _ = Role.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "organization_type": organization_type,
                "description": f"Legacy compatibility role for {name}.",
                "is_system_role": True,
                "is_custom_role": False,
                "status": "active",
            },
        )
        roles[code] = role

    now = timezone.now()
    for user in User.objects.exclude(organization_id__isnull=True).iterator():
        role = roles.get(user.role) or roles["food_handler"]
        OrganizationMembership.objects.get_or_create(
            user_id=user.id,
            organization_id=user.organization_id,
            status="active",
            defaults={
                "role": role,
                "unit_id": user.unit_id,
                "unit_restricted": user.unit_restricted,
                "joined_at": now,
            },
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_userinvite_unit_restricted_alter_userinvite_status"),
        ("organizations", "0005_organizationmembership_permission_permissionoverride_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_legacy_roles_and_memberships, noop_reverse),
    ]
