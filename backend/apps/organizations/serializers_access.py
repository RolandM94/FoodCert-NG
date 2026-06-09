from rest_framework import serializers

from apps.organizations.models import Organization
from apps.organizations.serializers_membership import MembershipListSerializer


class EffectivePermissionCheckSerializer(serializers.Serializer):
    permission_code = serializers.CharField(max_length=150)
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,
        allow_null=True,
        source="organization",
    )
    resource_id = serializers.UUIDField(required=False)


class EffectivePermissionResultSerializer(serializers.Serializer):
    allowed = serializers.BooleanField()
    reason = serializers.CharField()
    scope = serializers.CharField()
    organization_id = serializers.CharField(allow_null=True)
    unit_id = serializers.CharField(allow_null=True)
    membership_id = serializers.CharField(allow_null=True)
    role_code = serializers.CharField(allow_blank=True)
    permission_code = serializers.CharField(allow_blank=True)
    filters = serializers.DictField()


class UserMembershipsSerializer(serializers.Serializer):
    memberships = MembershipListSerializer(many=True)
