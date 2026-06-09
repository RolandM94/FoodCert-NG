from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import UserInvite, UserRole, UserStatus
from apps.organizations.models import Organization, OrganizationUnit

User = get_user_model()


PUBLIC_REGISTRATION_ROLES = {UserRole.FOOD_HANDLER, UserRole.EMPLOYER}


class UserSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
            "status",
            "email_verified",
            "phone_verified",
            "organization",
            "organization_name",
            "unit",
            "unit_name",
            "unit_restricted",
            "employer_staff_role",
            "state",
            "state_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "role",
            "status",
            "email_verified",
            "phone_verified",
            "organization",
            "organization_name",
            "unit",
            "unit_name",
            "unit_restricted",
            "employer_staff_role",
            "state",
            "state_name",
            "created_at",
            "updated_at",
        )


class UserAdminSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ("id", "created_at", "updated_at")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    role = serializers.ChoiceField(
        choices=[(role.value, role.label) for role in PUBLIC_REGISTRATION_ROLES],
        default=UserRole.FOOD_HANDLER,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "role",
        )
        read_only_fields = ("id",)

    def validate_username(self, value):
        return value.lower()

    def validate_email(self, value):
        return value.lower()

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class InviteUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), required=False)
    unit = serializers.PrimaryKeyRelatedField(queryset=OrganizationUnit.objects.all(), required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "role",
            "organization",
            "unit",
            "state",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        request_user = self.context["request"].user
        organization = attrs.get("organization") or request_user.organization
        unit = attrs.get("unit") or (request_user.unit if request_user.role == UserRole.EMPLOYER and request_user.unit_id else None)
        state = attrs.get("state") or getattr(organization, "state", None) or request_user.state

        if request_user.role not in {UserRole.SUPER_ADMIN, UserRole.STATE_ADMIN, UserRole.FACILITY_ADMIN, UserRole.EMPLOYER}:
            raise serializers.ValidationError("You cannot invite users.")
        if request_user.role == UserRole.STATE_ADMIN and state != request_user.state:
            raise serializers.ValidationError("State admins can only invite users in their state.")
        if request_user.role == UserRole.FACILITY_ADMIN and organization != request_user.organization:
            raise serializers.ValidationError("Facility admins can only invite users to their organization.")
        if request_user.role == UserRole.EMPLOYER and attrs.get("role") != UserRole.FOOD_HANDLER:
            raise serializers.ValidationError("Employers can only invite food handlers.")
        if request_user.role == UserRole.EMPLOYER and organization != request_user.organization:
            raise serializers.ValidationError("Employers can only invite users to their organization.")
        if unit and unit.organization_id != organization.id:
            raise serializers.ValidationError("Unit must belong to the selected organization.")

        attrs["organization"] = organization
        attrs["unit"] = unit
        attrs["state"] = state
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password", None) or User.objects.make_random_password()
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=UserStatus.choices)


class UserUnitAssignmentSerializer(serializers.Serializer):
    unit = serializers.PrimaryKeyRelatedField(queryset=OrganizationUnit.objects.all(), required=False, allow_null=True)
    unit_restricted = serializers.BooleanField(required=False)


class UserInviteSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    invited_by_email = serializers.EmailField(source="invited_by.email", read_only=True)
    accepted_by_email = serializers.EmailField(source="accepted_by.email", read_only=True)
    expires_at = serializers.DateTimeField(required=False)

    class Meta:
        model = UserInvite
        fields = (
            "id",
            "organization",
            "organization_name",
            "unit",
            "unit_name",
            "unit_restricted",
            "invited_by",
            "invited_by_email",
            "email",
            "phone",
            "role",
            "employer_staff_role",
            "ministry_staff_role",
            "facility_staff_type",
            "message",
            "status",
            "token",
            "accepted_by",
            "accepted_by_email",
            "accepted_at",
            "expires_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "organization",
            "organization_name",
            "invited_by",
            "invited_by_email",
            "status",
            "token",
            "accepted_by",
            "accepted_by_email",
            "accepted_at",
            "created_at",
            "updated_at",
        )


class AcceptInviteSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, validators=[validate_password])
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class FoodCertTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.status != UserStatus.ACTIVE:
            raise serializers.ValidationError("This account is not active.")
        data["user"] = UserSerializer(self.user).data
        return data
