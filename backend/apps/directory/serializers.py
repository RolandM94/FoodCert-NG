from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

from apps.accounts.models import UserRole
from apps.food_handlers.models import FoodHandlerProfile
from apps.employers.models import Employer
from apps.certificates.models import Certificate
from apps.organizations.models import OrganizationUnit


class DirectoryPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


def mask_nin(nin: str) -> str:
    if not nin or len(nin) < 6:
        return "****"
    return nin[:4] + "******" + nin[-2:]


class FoodHandlerDirectorySerializer(serializers.ModelSerializer):
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    branch_name = serializers.CharField(source="business_branch.name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    masked_nin = serializers.SerializerMethodField()

    class Meta:
        model = FoodHandlerProfile
        fields = (
            "id", "user_id", "full_name", "system_identifier", "masked_nin",
            "phone", "email", "gender", "date_of_birth", "passport_photo",
            "employer_id", "employer_name", "business_branch_id", "branch_name",
            "state_id", "state_name", "lga_id", "lga_name",
            "food_handler_category", "current_status", "created_at", "updated_at",
        )
        read_only_fields = fields

    def get_masked_nin(self, obj):
        return mask_nin(obj.nin)


class FoodHandlerDirectoryDetailSerializer(FoodHandlerDirectorySerializer):
    home_address = serializers.CharField(read_only=True)
    emergency_contact = serializers.CharField(read_only=True)
    work_location = serializers.CharField(read_only=True)

    class Meta(FoodHandlerDirectorySerializer.Meta):
        fields = FoodHandlerDirectorySerializer.Meta.fields + (
            "home_address", "emergency_contact", "work_location",
        )


class EmployerDirectorySerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    branch_count = serializers.SerializerMethodField()
    food_handler_count = serializers.IntegerField(source="number_of_food_handlers", read_only=True)

    class Meta:
        model = Employer
        fields = (
            "id", "user_id", "organization_id", "business_name",
            "business_registration_number", "business_type", "establishment_category",
            "contact_person_name", "contact_person_phone", "contact_person_email",
            "address", "state_id", "state_name", "lga_id", "lga_name",
            "branch_count", "food_handler_count",
            "compliance_status", "subscription_status",
            "is_active", "created_at", "updated_at",
        )
        read_only_fields = fields

    def get_branch_count(self, obj):
        if obj.organization_id:
            return obj.organization.units.filter(
                unit_type__in=["branch", "outlet", "site", "store", "regional_office"]
            ).count()
        return 0


class EmployerDirectoryDetailSerializer(EmployerDirectorySerializer):
    class Meta(EmployerDirectorySerializer.Meta):
        pass


class BranchDirectorySerializer(serializers.ModelSerializer):
    employer_name = serializers.CharField(source="organization.employer.business_name", read_only=True)
    employer_id = serializers.SerializerMethodField()
    state_name = serializers.CharField(source="state.name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    manager_name = serializers.CharField(source="manager.get_full_name", read_only=True)
    food_handler_count = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationUnit
        fields = (
            "id", "organization_id", "employer_id", "employer_name",
            "name", "unit_type", "parent_id", "manager_id", "manager_name",
            "state_id", "state_name", "lga_id", "lga_name",
            "address", "phone", "email", "status",
            "food_handler_count", "created_at", "updated_at",
        )
        read_only_fields = fields

    def get_employer_id(self, obj):
        try:
            return obj.organization.employer.id
        except Exception:
            return None

    def get_food_handler_count(self, obj):
        return obj.members.filter(
            food_handler_profile__isnull=False
        ).count() if hasattr(obj, 'members') else 0
