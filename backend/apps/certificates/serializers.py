from typing import Optional

from rest_framework import serializers

from apps.assessments.models import MedicalAssessment
from apps.certificates.models import Certificate, CertificateRequest, CertificateTemplate, CertificateTemplateScope, CertificateVerificationLog, SuspiciousCertificateReport


class CertificateTemplateSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = CertificateTemplate
        fields = (
            "id",
            "name",
            "scope",
            "state",
            "state_name",
            "ministry_name",
            "subtitle",
            "logo_url",
            "accent_color",
            "signatory_name",
            "signatory_title",
            "footer_note",
            "is_active",
            "is_default",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_by_name", "created_at", "updated_at")

    def validate(self, attrs):
        scope = attrs.get("scope") or getattr(self.instance, "scope", CertificateTemplateScope.NATIONAL)
        state = attrs.get("state") if "state" in attrs else getattr(self.instance, "state", None)
        if scope == CertificateTemplateScope.STATE and not state:
            raise serializers.ValidationError("State templates must be linked to a state.")
        if scope == CertificateTemplateScope.NATIONAL and state:
            raise serializers.ValidationError("National templates cannot be linked to a state.")
        accent_color = attrs.get("accent_color")
        if accent_color and (not accent_color.startswith("#") or len(accent_color) != 7):
            raise serializers.ValidationError("Accent color must be a hex value like #0f5132.")
        return attrs


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
    template_name = serializers.CharField(source="template.name", read_only=True)
    effective_status = serializers.CharField(read_only=True)

    class Meta:
        model = Certificate
        fields = (
            "id",
            "certificate_number",
            "public_id",
            "verification_token",
            "food_handler",
            "food_handler_name",
            "masked_nin",
            "assessment",
            "employer",
            "employer_name",
            "business_branch",
            "facility",
            "facility_name",
            "doctor",
            "doctor_name",
            "issuing_state",
            "issuing_state_name",
            "issued_by_state_user",
            "template",
            "template_name",
            "issue_date",
            "expiry_date",
            "status",
            "effective_status",
            "qr_code_url",
            "verification_url",
            "pdf_url",
            "digital_signature_hash",
            "replaced_by",
            "replacement_reason",
            "suspended_by",
            "suspended_at",
            "suspension_reason",
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


class FoodHandlerCertificateSerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    masked_nin = serializers.CharField(source="food_handler.masked_nin", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    business_branch_name = serializers.CharField(source="business_branch.name", read_only=True)
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.get_full_name", read_only=True)
    issuing_state_name = serializers.CharField(source="issuing_state.name", read_only=True)
    effective_status = serializers.CharField(read_only=True)
    renewal_status = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = (
            "id",
            "certificate_number",
            "public_id",
            "food_handler_name",
            "masked_nin",
            "assessment",
            "employer_name",
            "business_branch",
            "business_branch_name",
            "facility_name",
            "doctor_name",
            "issuing_state_name",
            "issue_date",
            "expiry_date",
            "status",
            "effective_status",
            "qr_code_url",
            "verification_url",
            "pdf_url",
            "replaced_by",
            "replacement_reason",
            "suspended_at",
            "suspension_reason",
            "revoked_at",
            "revocation_reason",
            "renewal_status",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_renewal_status(self, obj):
        from django.utils import timezone

        latest_assessment = obj.food_handler.assessments.exclude(id=obj.assessment_id).filter(created_at__gte=obj.created_at).order_by("-created_at").first()
        if latest_assessment and latest_assessment.created_at.date() >= obj.issue_date:
            if getattr(latest_assessment, "certificate", None):
                return "new_certificate_issued"
            certificate_request = getattr(latest_assessment, "certificate_request", None)
            if certificate_request and certificate_request.status == "pending_validation":
                return "awaiting_state_validation"
            return "assessment_pending"
        if obj.effective_status == "expired":
            return "renewal_overdue"
        if obj.status == "active" and 0 <= (obj.expiry_date - timezone.localdate()).days <= 30:
            return "renewal_due"
        return "not_started"


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
            "verification_token_submitted",
            "result",
            "verifier_type",
            "verifier_user",
            "ip_address",
            "user_agent",
            "location_latitude",
            "location_longitude",
            "verified_at",
        )
        read_only_fields = fields


class CertificateStatusChangeSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class PublicCertificateNumberVerificationSerializer(serializers.Serializer):
    certificate_number = serializers.CharField(max_length=96)


class SuspiciousCertificateReportSerializer(serializers.ModelSerializer):
    certificate_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    verification_token = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = SuspiciousCertificateReport
        fields = (
            "id",
            "certificate",
            "certificate_number",
            "verification_token",
            "certificate_number_submitted",
            "verification_token_submitted",
            "reporter_name",
            "reporter_contact",
            "reason",
            "details",
            "created_at",
        )
        read_only_fields = ("id", "certificate", "certificate_number_submitted", "verification_token_submitted", "created_at")

    def validate(self, attrs):
        if not attrs.get("certificate_number") and not attrs.get("verification_token"):
            raise serializers.ValidationError("Certificate number or verification token is required.")
        return attrs
