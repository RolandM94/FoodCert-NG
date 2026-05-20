from rest_framework import serializers

from apps.common.security import validate_uploaded_file_security
from apps.facilities.models import FacilityAccreditationApplication, MedicalFacility


class MedicalFacilitySerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True)
    can_conduct_assessments = serializers.BooleanField(read_only=True)

    class Meta:
        model = MedicalFacility
        fields = (
            "id",
            "organization",
            "facility_name",
            "facility_type",
            "ownership_type",
            "license_number",
            "registration_number",
            "address",
            "state",
            "state_name",
            "lga",
            "lga_name",
            "contact_person",
            "phone",
            "email",
            "accreditation_status",
            "accreditation_start_date",
            "accreditation_expiry_date",
            "approved_by",
            "approved_by_name",
            "standard_assessment_price",
            "can_conduct_assessments",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "organization",
            "accreditation_status",
            "accreditation_start_date",
            "accreditation_expiry_date",
            "approved_by",
            "approved_by_name",
            "can_conduct_assessments",
            "created_at",
            "updated_at",
        )


class FacilityAccreditationApplicationSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    facility_state = serializers.CharField(source="facility.state.name", read_only=True)
    checklist_complete = serializers.BooleanField(read_only=True)
    reviewer_name = serializers.CharField(source="reviewer.get_full_name", read_only=True)

    class Meta:
        model = FacilityAccreditationApplication
        fields = (
            "id",
            "facility",
            "facility_name",
            "facility_state",
            "application_status",
            "has_reporting_policy",
            "has_medical_records_computers",
            "has_computer_operators",
            "has_standard_forms",
            "has_laboratory_request_forms",
            "has_patient_files",
            "has_qr_certificate_capability",
            "has_internet_access",
            "has_trained_records_staff",
            "has_trained_clinical_staff",
            "has_trained_non_clinical_staff",
            "supporting_document",
            "checklist_complete",
            "reviewer",
            "reviewer_name",
            "review_comment",
            "submitted_at",
            "reviewed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "application_status",
            "checklist_complete",
            "reviewer",
            "reviewer_name",
            "review_comment",
            "submitted_at",
            "reviewed_at",
            "created_at",
            "updated_at",
        )

    def validate_supporting_document(self, value):
        return validate_uploaded_file_security(value)


class AccreditationReviewSerializer(serializers.Serializer):
    review_comment = serializers.CharField(required=False, allow_blank=True)
