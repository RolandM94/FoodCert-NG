from rest_framework import serializers

from apps.accounts.models import EmployerStaffRole, UserInvite, UserRole, UserStatus
from django.contrib.auth import get_user_model
from apps.employers.models import Employer
from apps.organizations.models import OrganizationUnit

User = get_user_model()


class EmployerSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = Employer
        fields = (
            "id",
            "user",
            "organization",
            "organization_name",
            "business_name",
            "business_registration_number",
            "business_type",
            "establishment_category",
            "contact_person_name",
            "contact_person_phone",
            "contact_person_email",
            "address",
            "state",
            "state_name",
            "lga",
            "lga_name",
            "ward",
            "number_of_food_handlers",
            "compliance_status",
            "subscription_status",
            "notification_preferences",
            "business_settings",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "organization",
            "organization_name",
            "compliance_status",
            "subscription_status",
            "is_active",
            "created_at",
            "updated_at",
        )


class EmployerSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = (
            "id",
            "notification_preferences",
            "business_settings",
            "subscription_status",
            "updated_at",
        )
        read_only_fields = ("id", "subscription_status", "updated_at")

    def validate_notification_preferences(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Notification preferences must be an object.")
        return value

    def validate_business_settings(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Business settings must be an object.")
        return value


class EmployerDashboardQuerySerializer(serializers.Serializer):
    branch = serializers.UUIDField(required=False)


def employer_staff_role_for(user):
    if user.role != UserRole.EMPLOYER:
        return user.role
    if user.employer_staff_role:
        return user.employer_staff_role
    if user.unit_restricted and user.unit_id:
        return EmployerStaffRole.BRANCH_MANAGER
    return EmployerStaffRole.EMPLOYER_ADMIN


class EmployerUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    employer_staff_role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "role",
            "employer_staff_role",
            "status",
            "organization",
            "unit",
            "unit_name",
            "unit_restricted",
            "state",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_employer_staff_role(self, obj):
        return employer_staff_role_for(obj)


class EmployerInviteCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_blank=True)
    employer_staff_role = serializers.ChoiceField(
        choices=[
            (EmployerStaffRole.COMPLIANCE_OFFICER, "Compliance Officer"),
            (EmployerStaffRole.BRANCH_MANAGER, "Branch Manager"),
            (EmployerStaffRole.FINANCE_USER, "Finance User"),
        ]
    )
    unit = serializers.PrimaryKeyRelatedField(queryset=OrganizationUnit.objects.all(), required=False, allow_null=True)
    message = serializers.CharField(required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        staff_role = attrs["employer_staff_role"]
        unit = attrs.get("unit")
        if staff_role == "branch_manager" and not unit:
            raise serializers.ValidationError("Branch manager invites require a branch/unit.")
        if staff_role != "branch_manager" and unit:
            raise serializers.ValidationError("Head office staff invites should not be restricted to a branch.")
        return attrs


class EmployerUserUpdateSerializer(serializers.Serializer):
    employer_staff_role = serializers.ChoiceField(
        choices=[
            (EmployerStaffRole.COMPLIANCE_OFFICER, "Compliance Officer"),
            (EmployerStaffRole.BRANCH_MANAGER, "Branch Manager"),
            (EmployerStaffRole.FINANCE_USER, "Finance User"),
            (EmployerStaffRole.EMPLOYER_ADMIN, "Employer Admin"),
        ],
        required=False,
    )
    unit = serializers.PrimaryKeyRelatedField(queryset=OrganizationUnit.objects.all(), required=False, allow_null=True)
    status = serializers.ChoiceField(choices=UserStatus.choices, required=False)

    def validate(self, attrs):
        staff_role = attrs.get("employer_staff_role")
        unit = attrs.get("unit")
        if staff_role == "branch_manager" and not unit:
            raise serializers.ValidationError("Branch manager assignment requires a branch/unit.")
        return attrs


class EmployerInviteSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    invited_by_name = serializers.CharField(source="invited_by.get_full_name", read_only=True)
    accepted_by_name = serializers.CharField(source="accepted_by.get_full_name", read_only=True)
    employer_staff_role = serializers.SerializerMethodField()

    class Meta:
        model = UserInvite
        fields = (
            "id",
            "organization",
            "organization_name",
            "unit",
            "unit_name",
            "invited_by",
            "invited_by_name",
            "email",
            "phone",
            "role",
            "employer_staff_role",
            "message",
            "status",
            "token",
            "accepted_by",
            "accepted_by_name",
            "accepted_at",
            "expires_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_employer_staff_role(self, obj):
        if obj.employer_staff_role:
            return obj.employer_staff_role
        if obj.role == UserRole.EMPLOYER and obj.unit_id:
            return EmployerStaffRole.BRANCH_MANAGER
        if obj.role == UserRole.EMPLOYER:
            return EmployerStaffRole.EMPLOYER_ADMIN
        return obj.role
