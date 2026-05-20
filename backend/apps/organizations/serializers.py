from rest_framework import serializers

from apps.organizations.models import Organization, OrganizationUnit


class OrganizationSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)

    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "organization_type",
            "status",
            "state",
            "state_name",
            "lga",
            "lga_name",
            "address",
            "phone",
            "email",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class OrganizationUnitSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)

    class Meta:
        model = OrganizationUnit
        fields = (
            "id",
            "organization",
            "organization_name",
            "name",
            "unit_type",
            "parent",
            "parent_name",
            "description",
            "state",
            "state_name",
            "lga",
            "lga_name",
            "address",
            "phone",
            "email",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "organization", "organization_name", "parent_name", "state_name", "lga_name", "created_at", "updated_at")
