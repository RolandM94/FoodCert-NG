from rest_framework import serializers

from apps.common.security import validate_uploaded_file_security
from apps.lab_tests.models import LabReviewRecommendation, LabTest, LabTestStatus


class LabTestSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source="requested_by.get_full_name", read_only=True)
    resulted_by_name = serializers.CharField(source="resulted_by.get_full_name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)
    result_document_url = serializers.FileField(source="result_document", read_only=True)
    assessment_status = serializers.CharField(source="assessment.status", read_only=True)
    food_handler_name = serializers.CharField(source="assessment.food_handler.full_name", read_only=True)
    facility_name = serializers.CharField(source="assessment.facility.facility_name", read_only=True)
    assigned_lab_staff_name = serializers.CharField(source="assigned_lab_staff.get_full_name", read_only=True)
    assigned_lab_unit_name = serializers.CharField(source="assigned_lab_unit.name", read_only=True)

    class Meta:
        model = LabTest
        fields = (
            "id",
            "assessment",
            "parent_lab_test",
            "assessment_status",
            "food_handler_name",
            "facility_name",
            "test_type",
            "test_name",
            "status",
            "repeat_required",
            "repeat_reason",
            "is_flagged",
            "result_value",
            "result_notes",
            "lab_staff_notes",
            "doctor_review_notes",
            "doctor_recommendation",
            "result_document",
            "result_document_url",
            "assigned_lab_staff",
            "assigned_lab_staff_name",
            "assigned_lab_unit",
            "assigned_lab_unit_name",
            "requested_by",
            "requested_by_name",
            "resulted_by",
            "resulted_by_name",
            "reviewed_by",
            "reviewed_by_name",
            "requested_at",
            "sample_collected_at",
            "resulted_at",
            "submitted_to_doctor_at",
            "reviewed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class LabTestRequestItemSerializer(serializers.Serializer):
    test_type = serializers.ChoiceField(choices=LabTest._meta.get_field("test_type").choices)
    test_name = serializers.CharField(required=False, allow_blank=True)


class LabTestRequestSerializer(serializers.Serializer):
    tests = LabTestRequestItemSerializer(many=True, required=False, default=list)
    include_required = serializers.BooleanField(required=False, default=True)

    def validate(self, attrs):
        if not attrs.get("include_required", True) and not attrs.get("tests"):
            raise serializers.ValidationError("At least one lab test is required when required tests are not included.")
        return attrs


class LabTestRepeatRequestSerializer(serializers.Serializer):
    reason = serializers.CharField()
    test_name = serializers.CharField(required=False, allow_blank=True)


class LabTestResultSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            LabTestStatus.POSITIVE,
            LabTestStatus.NEGATIVE,
            LabTestStatus.INCONCLUSIVE,
            LabTestStatus.REPEAT_REQUIRED,
        ]
    )
    result_value = serializers.CharField(required=False, allow_blank=True)
    result_notes = serializers.CharField(required=False, allow_blank=True)
    lab_staff_notes = serializers.CharField(required=False, allow_blank=True)


class LabSampleCollectedSerializer(serializers.Serializer):
    lab_staff_notes = serializers.CharField(required=False, allow_blank=True)


class LabSubmitToDoctorSerializer(serializers.Serializer):
    lab_staff_notes = serializers.CharField(required=False, allow_blank=True)


class LabDoctorReviewSerializer(serializers.Serializer):
    doctor_review_notes = serializers.CharField(required=False, allow_blank=True)
    doctor_recommendation = serializers.ChoiceField(choices=LabReviewRecommendation.choices, required=False, allow_blank=True)


class LabResultUploadSerializer(serializers.Serializer):
    result_document = serializers.FileField()
    lab_staff_notes = serializers.CharField(required=False, allow_blank=True)

    def validate_result_document(self, value):
        return validate_uploaded_file_security(value)
