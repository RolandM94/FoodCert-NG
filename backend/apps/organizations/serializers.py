from rest_framework import serializers

from apps.accounts.models import User
from apps.organizations.models import Organization, OrganizationStatus, OrganizationUnit


class OrganizationSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    children_count = serializers.SerializerMethodField()
    membership_count = serializers.SerializerMethodField()
    unit_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = (
            "id",
            "parent",
            "parent_name",
            "name",
            "organization_type",
            "status",
            "state",
            "state_name",
            "lga",
            "lga_name",
            "address",
            "contact_person_name",
            "phone",
            "email",
            "website",
            "created_by",
            "created_by_email",
            "children_count",
            "membership_count",
            "unit_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id", "parent_name", "created_by", "created_by_email", "children_count",
            "membership_count", "unit_count", "created_at", "updated_at",
        )

    def get_children_count(self, organization):
        return organization.children.count()

    def get_membership_count(self, organization):
        return organization.memberships.filter(status="active").count()

    def get_unit_count(self, organization):
        return organization.units.count()

    def validate_status(self, value):
        if self.instance and self.instance.status == OrganizationStatus.ARCHIVED and value == OrganizationStatus.ACTIVE:
            raise serializers.ValidationError("Archived organizations must be moved out of archive before reactivation.")
        return value


class OrganizationUnitSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    manager_name = serializers.CharField(source="manager.get_full_name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    member_count = serializers.SerializerMethodField()
    open_assessment_count = serializers.SerializerMethodField()
    pending_lab_test_count = serializers.SerializerMethodField()
    records_ready_count = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

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
            "manager",
            "manager_name",
            "description",
            "state",
            "state_name",
            "lga",
            "lga_name",
            "address",
            "phone",
            "email",
            "status",
            "is_active",
            "created_by",
            "created_by_email",
            "children",
            "member_count",
            "open_assessment_count",
            "pending_lab_test_count",
            "records_ready_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "organization",
            "organization_name",
            "parent_name",
            "manager_name",
            "state_name",
            "lga_name",
            "created_by",
            "created_by_email",
            "children",
            "member_count",
            "open_assessment_count",
            "pending_lab_test_count",
            "records_ready_count",
            "created_at",
            "updated_at",
        )

    def get_member_count(self, unit):
        return unit.memberships.filter(status="active").count() or unit.members.filter(status="active").count()

    def get_children(self, unit):
        return [
            {
                "id": str(child.id),
                "name": child.name,
                "unit_type": child.unit_type,
                "status": child.status,
                "is_active": child.is_active,
                "member_count": child.memberships.filter(status="active").count() or child.members.filter(status="active").count(),
            }
            for child in unit.children.order_by("name")
        ]

    def get_open_assessment_count(self, unit):
        from apps.assessments.models import AssessmentStatus, MedicalAssessment

        queryset = MedicalAssessment.objects.filter(facility__organization_id=unit.organization_id).exclude(
            status__in=[
                AssessmentStatus.CERTIFICATE_ISSUED,
                AssessmentStatus.CLOSED,
            ]
        )
        if unit.unit_type == "clinical_department":
            queryset = queryset.filter(doctor__unit=unit)
        return queryset.count()

    def get_pending_lab_test_count(self, unit):
        from apps.lab_tests.models import LabTest, LabTestStatus

        queryset = LabTest.objects.filter(assessment__facility__organization_id=unit.organization_id).exclude(
            status=LabTestStatus.REVIEWED
        )
        if unit.unit_type == "lab_department":
            queryset = queryset.filter(resulted_by__isnull=True) | queryset.filter(resulted_by__unit=unit)
        return queryset.distinct().count()

    def get_records_ready_count(self, unit):
        from apps.assessments.models import AssessmentStatus, MedicalAssessment

        if unit.unit_type != "records_department":
            return 0
        return MedicalAssessment.objects.filter(
            facility__organization_id=unit.organization_id,
            status__in=[
                AssessmentStatus.FIT,
                AssessmentStatus.TEMPORARILY_NOT_FIT,
                AssessmentStatus.NOT_FIT,
                AssessmentStatus.SUBMITTED_FOR_STATE_VALIDATION,
                AssessmentStatus.CERTIFICATE_ISSUED,
            ],
        ).count()


class OrganizationUnitAssignUserSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    unit_restricted = serializers.BooleanField(default=False)
