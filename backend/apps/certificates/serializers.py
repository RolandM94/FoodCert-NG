from typing import Optional

from rest_framework import serializers

from apps.assessments.models import MedicalAssessment
from apps.certificates.models import Certificate, CertificateRequest, CertificateVerificationLog


class CertificateRequestSerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="assessment.food_handler.full_name", read_only=True)
    facility_name = serializers.CharField(source="assessment.facility.facility_name", read_only=True)
    issuing_state_name = serializers.CharField(source="assessment.facility.state.name", read_only=True)
    requested_by_name = serializers.CharField(source="requested_by.get_full_name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)
    facility_responded_by_name = serializers.CharField(source="facility_responded_by.get_full_name", read_only=True)

    class Meta:
        model = CertificateRequest
        fields = (
            "id",
            "assessment",
            "food_handler_name",
            "facility_name",
            "issuing_state_name",
            "requested_by",
            "requested_by_name",
            "reviewed_by",
            "reviewed_by_name",
            "status",
            "request_notes",
            "review_notes",
            "reviewed_at",
            "facility_response",
            "facility_responded_by",
            "facility_responded_by_name",
            "facility_responded_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class RequestCertificateSerializer(serializers.Serializer):
    request_notes = serializers.CharField(required=False, allow_blank=True)


class CertificateClarificationResponseSerializer(serializers.Serializer):
    response = serializers.CharField()


class ReviewCertificateRequestSerializer(serializers.Serializer):
    review_notes = serializers.CharField(required=False, allow_blank=True)


class GenerateCertificateSerializer(serializers.Serializer):
    assessment = serializers.PrimaryKeyRelatedField(queryset=MedicalAssessment.objects.all(), required=False)
    certificate_request = serializers.PrimaryKeyRelatedField(queryset=CertificateRequest.objects.all(), required=False)

    def validate(self, attrs):
        if not attrs.get("assessment") and not attrs.get("certificate_request"):
            raise serializers.ValidationError("assessment or certificate_request is required.")
        return attrs


class CertificateSerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    masked_nin = serializers.CharField(source="food_handler.masked_nin", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.get_full_name", read_only=True)
    issuing_state_name = serializers.CharField(source="issuing_state.name", read_only=True)
    effective_status = serializers.CharField(read_only=True)

    class Meta:
        model = Certificate
        fields = (
            "id",
            "certificate_number",
            "food_handler",
            "food_handler_name",
            "masked_nin",
            "assessment",
            "employer",
            "employer_name",
            "facility",
            "facility_name",
            "doctor",
            "doctor_name",
            "issuing_state",
            "issuing_state_name",
            "issued_by_state_user",
            "issue_date",
            "expiry_date",
            "status",
            "effective_status",
            "qr_code_url",
            "verification_url",
            "pdf_url",
            "digital_signature_hash",
            "revoked_by",
            "revoked_at",
            "revocation_reason",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class EmployerCertificateSerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    passport_photo = serializers.ImageField(source="food_handler.passport_photo", read_only=True)
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    certificate_validity = serializers.CharField(source="effective_status", read_only=True)
    fitness_status = serializers.CharField(source="assessment.final_decision", read_only=True)

    class Meta:
        model = Certificate
        fields = (
            "id",
            "certificate_number",
            "food_handler_name",
            "passport_photo",
            "certificate_validity",
            "facility_name",
            "issue_date",
            "expiry_date",
            "fitness_status",
            "verification_url",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CertificatePublicVerificationSerializer(serializers.ModelSerializer):
    certificate_validity = serializers.CharField(source="effective_status", read_only=True)
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    passport_photo = serializers.ImageField(source="food_handler.passport_photo", read_only=True)
    issuing_state_ministry = serializers.SerializerMethodField()
    approved_medical_facility = serializers.CharField(source="facility.facility_name", read_only=True)
    fitness_status = serializers.CharField(source="assessment.final_decision", read_only=True)
    last_verified_at = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = (
            "certificate_validity",
            "certificate_number",
            "food_handler_name",
            "passport_photo",
            "issuing_state_ministry",
            "approved_medical_facility",
            "issue_date",
            "expiry_date",
            "fitness_status",
            "last_verified_at",
        )

    def get_issuing_state_ministry(self, obj) -> str:
        return f"{obj.issuing_state.name} State Ministry of Health"

    def get_last_verified_at(self, obj) -> Optional[str]:
        latest = obj.verification_logs.order_by("-verified_at").first()
        return latest.verified_at if latest else None


class CertificateVerificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateVerificationLog
        fields = (
            "id",
            "certificate",
            "certificate_number_submitted",
            "result",
            "ip_address",
            "user_agent",
            "verified_at",
        )
        read_only_fields = fields


class CertificateStatusChangeSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)
