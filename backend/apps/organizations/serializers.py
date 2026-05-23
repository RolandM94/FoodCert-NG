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
    member_count = serializers.SerializerMethodField()
    open_assessment_count = serializers.SerializerMethodField()
    pending_lab_test_count = serializers.SerializerMethodField()
    records_ready_count = serializers.SerializerMethodField()

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
            "state_name",
            "lga_name",
            "member_count",
            "open_assessment_count",
            "pending_lab_test_count",
            "records_ready_count",
            "created_at",
            "updated_at",
        )

    def get_member_count(self, unit):
        return unit.members.filter(status="active").count()

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
