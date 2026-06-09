from rest_framework import serializers

from apps.accounts.models import User
from apps.audit.models import AuditAction, AuditLog
from apps.organizations.models import OrganizationMembership, OrganizationUnit, PermissionOverride, Role


class MembershipListSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)
    role_code = serializers.CharField(source="role.code", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = (
            "id", "user", "user_name", "user_email", "role", "role_name", "role_code",
            "unit", "unit_name", "unit_restricted", "status", "joined_at", "last_active_at",
            "created_at", "updated_at",
        )
        read_only_fields = fields


class PermissionOverrideSummarySerializer(serializers.ModelSerializer):
    permission_code = serializers.CharField(source="permission.code", read_only=True)
    permission_name = serializers.CharField(source="permission.name", read_only=True)

    class Meta:
        model = PermissionOverride
        fields = ("id", "permission", "permission_code", "permission_name", "effect", "reason", "expires_at")
        read_only_fields = fields


class MembershipAuditSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.get_full_name", read_only=True)

    class Meta:
        model = AuditLog
        fields = ("id", "action", "actor", "actor_name", "old_value", "new_value", "metadata", "created_at")
        read_only_fields = fields


class MembershipDetailSerializer(MembershipListSerializer):
    permissions = serializers.SerializerMethodField()
    overrides = PermissionOverrideSummarySerializer(source="permission_overrides", many=True, read_only=True)
    audit_log = serializers.SerializerMethodField()

    class Meta(MembershipListSerializer.Meta):
        fields = MembershipListSerializer.Meta.fields + ("permissions", "overrides", "audit_log")

    def get_permissions(self, membership):
        return list(membership.role.role_permissions.select_related("permission").values_list("permission__code", flat=True))

    def get_audit_log(self, membership):
        logs = AuditLog.objects.filter(
            target_type="OrganizationMembership",
            target_id=str(membership.id),
        ).select_related("actor").order_by("-created_at")[:10]
        return MembershipAuditSerializer(logs, many=True).data


class CreateMembershipSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.filter(status="active"))
    unit = serializers.PrimaryKeyRelatedField(queryset=OrganizationUnit.objects.all(), required=False, allow_null=True)
    unit_restricted = serializers.BooleanField(default=False)


class UpdateMembershipSerializer(serializers.Serializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.filter(status="active"), required=False)
    unit = serializers.PrimaryKeyRelatedField(queryset=OrganizationUnit.objects.all(), required=False, allow_null=True)
    unit_restricted = serializers.BooleanField(required=False)


class ChangeRoleSerializer(serializers.Serializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.filter(status="active"))


class ChangeUnitSerializer(serializers.Serializer):
    unit = serializers.PrimaryKeyRelatedField(queryset=OrganizationUnit.objects.all(), required=False, allow_null=True)
    unit_restricted = serializers.BooleanField(default=False)
