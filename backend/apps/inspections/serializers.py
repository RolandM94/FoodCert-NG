from rest_framework import serializers

from apps.employers.models import Employer
from apps.inspections.models import Inspection, InspectionCertificateScan, InspectionResponse, InspectionResponseType


class InspectionSerializer(serializers.ModelSerializer):
    inspector_name = serializers.CharField(source="inspector.get_full_name", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = Inspection
        fields = (
            "id",
            "inspector",
            "inspector_name",
            "employer",
            "employer_name",
            "branch",
            "branch_name",
            "inspection_date",
            "gps_latitude",
            "gps_longitude",
            "checklist_responses",
            "compliance_score",
            "enforcement_action",
            "findings",
            "evidence_files",
            "status",
            "submitted_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "inspector", "inspector_name", "compliance_score", "evidence_files", "submitted_at", "created_at", "updated_at")


class InspectionResponseSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source="submitted_by.get_full_name", read_only=True)

    class Meta:
        model = InspectionResponse
        fields = (
            "id",
            "inspection",
            "submitted_by",
            "submitted_by_name",
            "response_type",
            "content",
            "evidence_file_url",
            "submitted_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class InspectionResponseCreateSerializer(serializers.Serializer):
    response_type = serializers.ChoiceField(choices=InspectionResponseType.choices)
    content = serializers.CharField(required=False, allow_blank=True)
    evidence_file_url = serializers.URLField(required=False, allow_blank=True)


class CreateInspectionSerializer(serializers.ModelSerializer):
    employer = serializers.PrimaryKeyRelatedField(queryset=Employer.objects.all())

    class Meta:
        model = Inspection
        fields = (
            "employer",
            "branch",
            "inspection_date",
            "gps_latitude",
            "gps_longitude",
            "checklist_responses",
            "enforcement_action",
            "findings",
            "status",
        )


class InspectionEvidenceSerializer(serializers.Serializer):
    file_url = serializers.URLField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    uploaded_at = serializers.DateTimeField(required=False)


class CertificateScanSerializer(serializers.Serializer):
    certificate_number = serializers.CharField()


class InspectionCertificateScanSerializer(serializers.ModelSerializer):
    certificate_status = serializers.CharField(source="certificate.effective_status", read_only=True)

    class Meta:
        model = InspectionCertificateScan
        fields = (
            "id",
            "inspection",
            "certificate_number",
            "certificate",
            "certificate_status",
            "result",
            "scanned_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
