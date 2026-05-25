from rest_framework import serializers

from apps.certificates.models import Certificate
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
    food_handler_name = serializers.CharField(source="certificate.food_handler.full_name", read_only=True)
    issuing_state_name = serializers.CharField(source="certificate.issuing_state.name", read_only=True)
    facility_name = serializers.CharField(source="certificate.facility.facility_name", read_only=True)

    class Meta:
        model = InspectionCertificateScan
        fields = (
            "id",
            "inspection",
            "certificate_number",
            "certificate",
            "certificate_status",
            "food_handler_name",
            "issuing_state_name",
            "facility_name",
            "result",
            "scanned_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class InspectorCertificateVerificationSerializer(serializers.ModelSerializer):
    certificate_validity = serializers.CharField(source="effective_status", read_only=True)
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    passport_photo = serializers.ImageField(source="food_handler.passport_photo", read_only=True)
    issuing_state_ministry = serializers.SerializerMethodField()
    approved_medical_facility = serializers.CharField(source="facility.facility_name", read_only=True)
    fitness_status = serializers.CharField(source="assessment.final_decision", read_only=True)
    verification_result = serializers.CharField(read_only=True)

    class Meta:
        model = Certificate
        fields = (
            "id",
            "certificate_number",
            "certificate_validity",
            "verification_result",
            "food_handler_name",
            "passport_photo",
            "issuing_state_ministry",
            "approved_medical_facility",
            "issue_date",
            "expiry_date",
            "fitness_status",
        )

    def get_issuing_state_ministry(self, obj) -> str:
        return f"{obj.issuing_state.name} State Ministry of Health"

    def to_representation(self, instance):
        payload = super().to_representation(instance)
        payload["verification_result"] = self.context.get("verification_result", payload.get("certificate_validity"))
        payload["certificate_validity"] = self.context.get("verification_result", payload.get("certificate_validity"))
        return payload


class InspectorCertificateNumberSerializer(serializers.Serializer):
    certificate_number = serializers.CharField(max_length=96)


class InspectorCertificateSaveSerializer(serializers.Serializer):
    inspection = serializers.PrimaryKeyRelatedField(queryset=Inspection.objects.all())


class InspectorCertificateFlagSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=255)
    details = serializers.CharField(required=False, allow_blank=True)
