from rest_framework import serializers

from apps.vaccinations.models import VaccinationRecord


class VaccinationRecordSerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    assessment_status = serializers.CharField(source="assessment.status", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.get_full_name", read_only=True)

    class Meta:
        model = VaccinationRecord
        fields = (
            "id",
            "food_handler",
            "food_handler_name",
            "assessment",
            "assessment_status",
            "vaccine_type",
            "vaccine_name",
            "dose_number",
            "date_administered",
            "expiry_date",
            "status",
            "doctor_clearance",
            "reminder_date",
            "notes",
            "recorded_by",
            "recorded_by_name",
            "reviewed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "food_handler",
            "food_handler_name",
            "assessment",
            "assessment_status",
            "status",
            "reminder_date",
            "recorded_by",
            "recorded_by_name",
            "reviewed_at",
            "created_at",
            "updated_at",
        )


class VaccinationRecordSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationRecord
        fields = (
            "vaccine_type",
            "vaccine_name",
            "dose_number",
            "date_administered",
            "expiry_date",
            "doctor_clearance",
            "notes",
        )
