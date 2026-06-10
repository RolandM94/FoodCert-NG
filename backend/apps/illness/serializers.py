from rest_framework import serializers

from apps.food_handlers.models import FoodHandlerProfile
from apps.illness.models import IllnessReport


class IllnessReportSerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    reported_by_name = serializers.CharField(source="reported_by.get_full_name", read_only=True)
    reviewed_by_doctor_name = serializers.CharField(source="reviewed_by_doctor.get_full_name", read_only=True)

    class Meta:
        model = IllnessReport
        fields = (
            "id",
            "food_handler",
            "food_handler_name",
            "employer",
            "employer_name",
            "reported_by",
            "reported_by_name",
            "symptoms",
            "suspected_condition",
            "symptom_start_date",
            "symptom_end_date",
            "exclusion_start_date",
            "earliest_return_date",
            "clearance_required",
            "clearance_status",
            "reviewed_by_doctor",
            "reviewed_by_doctor_name",
            "reviewed_at",
            "cleared_at",
            "return_to_work_certificate_number",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "employer",
            "reported_by",
            "reported_by_name",
            "exclusion_start_date",
            "earliest_return_date",
            "clearance_required",
            "clearance_status",
            "reviewed_by_doctor",
            "reviewed_by_doctor_name",
            "reviewed_at",
            "cleared_at",
            "return_to_work_certificate_number",
            "created_at",
            "updated_at",
        )


class IllnessOperationalSerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    reviewed_by_doctor_name = serializers.CharField(source="reviewed_by_doctor.get_full_name", read_only=True)

    class Meta:
        model = IllnessReport
        fields = (
            "id",
            "food_handler",
            "food_handler_name",
            "employer",
            "employer_name",
            "suspected_condition",
            "exclusion_start_date",
            "earliest_return_date",
            "clearance_required",
            "clearance_status",
            "reviewed_by_doctor_name",
            "reviewed_at",
            "cleared_at",
            "return_to_work_certificate_number",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CreateIllnessReportSerializer(serializers.ModelSerializer):
    food_handler = serializers.PrimaryKeyRelatedField(queryset=FoodHandlerProfile.objects.all())

    class Meta:
        model = IllnessReport
        fields = (
            "food_handler",
            "symptoms",
            "suspected_condition",
            "symptom_start_date",
            "symptom_end_date",
            "notes",
        )


class ReviewIllnessReportSerializer(serializers.Serializer):
    suspected_condition = serializers.CharField(required=False, allow_blank=True)
    symptom_end_date = serializers.DateField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class IllnessClearanceSerializer(serializers.Serializer):
    cleared = serializers.BooleanField()
    notes = serializers.CharField(required=False, allow_blank=True)
