from rest_framework import serializers

from apps.organizations.models import Permission, Role, RolePermission, RoleStatus


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ("id", "code", "name", "module", "description", "is_sensitive", "created_at", "updated_at")
        read_only_fields = fields


class RoleListSerializer(serializers.ModelSerializer):
    permission_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "code",
            "organization_type",
            "description",
            "is_system_role",
            "is_custom_role",
            "status",
            "permission_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class RoleDetailSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    permission_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "code",
            "organization_type",
            "description",
            "is_system_role",
            "is_custom_role",
            "status",
            "permission_count",
            "permissions",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_permissions(self, role):
        permissions = Permission.objects.filter(role_permissions__role=role).order_by("module", "code")
        return PermissionSerializer(permissions, many=True).data


class CreateRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "name", "code", "organization_type", "description", "status")
        read_only_fields = ("id",)

    def validate_status(self, value):
        if value == RoleStatus.DEPRECATED:
            raise serializers.ValidationError("New custom roles cannot be created as deprecated.")
        return value

    def create(self, validated_data):
        return Role.objects.create(
            **validated_data,
            is_system_role=False,
            is_custom_role=True,
            created_by=self.context["request"].user,
        )


class UpdateRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("name", "description", "status")

    def validate(self, attrs):
        if self.instance.is_system_role and "name" in attrs and attrs["name"] != self.instance.name:
            raise serializers.ValidationError("System role names cannot be changed.")
        return attrs


class RolePermissionWriteSerializer(serializers.Serializer):
    permission = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all())

    def save(self, **kwargs):
        return RolePermission.objects.get_or_create(role=self.context["role"], permission=self.validated_data["permission"])[0]
