from rest_framework import serializers

from apps.lab_tests.models import LabTest, LabTestStatus


class LabTestSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source="requested_by.get_full_name", read_only=True)
    resulted_by_name = serializers.CharField(source="resulted_by.get_full_name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)

    class Meta:
        model = LabTest
        fields = (
            "id",
            "assessment",
            "test_type",
            "test_name",
            "status",
            "result_value",
            "result_notes",
            "requested_by",
            "requested_by_name",
            "resulted_by",
            "resulted_by_name",
            "reviewed_by",
            "reviewed_by_name",
            "requested_at",
            "resulted_at",
            "reviewed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class LabTestRequestItemSerializer(serializers.Serializer):
    test_type = serializers.ChoiceField(choices=LabTest._meta.get_field("test_type").choices)
    test_name = serializers.CharField(required=False, allow_blank=True)


class LabTestRequestSerializer(serializers.Serializer):
    tests = LabTestRequestItemSerializer(many=True)

    def validate_tests(self, value):
        if not value:
            raise serializers.ValidationError("At least one lab test is required.")
        return value


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
