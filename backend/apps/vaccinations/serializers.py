from rest_framework import serializers

from apps.common.security import validate_uploaded_file_security
from apps.vaccinations.models import VaccinationRecord


class VaccinationRecordSerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    assessment_status = serializers.CharField(source="assessment.status", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.get_full_name", read_only=True)
    certificate_upload_url = serializers.FileField(source="certificate_upload", read_only=True)
    compliance_status = serializers.CharField(read_only=True)
    notes = serializers.SerializerMethodField()

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
            "brand_name",
            "batch_number",
            "vaccinator_name",
            "vaccination_facility_name",
            "vaccination_facility_address",
            "certificate_upload",
            "certificate_upload_url",
            "dose_number",
            "date_administered",
            "expiry_date",
            "status",
            "compliance_status",
            "doctor_clearance",
            "next_dose_date",
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
            "compliance_status",
            "reminder_date",
            "recorded_by",
            "recorded_by_name",
            "reviewed_at",
            "created_at",
            "updated_at",
        )

    def get_notes(self, record):
        request = self.context.get("request")
        if getattr(getattr(request, "user", None), "role", "") == "employer":
            return ""
        return record.notes


class VaccinationRecordSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationRecord
        fields = (
            "vaccine_type",
            "vaccine_name",
            "brand_name",
            "batch_number",
            "vaccinator_name",
            "vaccination_facility_name",
            "vaccination_facility_address",
            "certificate_upload",
            "dose_number",
            "date_administered",
            "expiry_date",
            "doctor_clearance",
            "notes",
        )

    def validate_certificate_upload(self, value):
        return validate_uploaded_file_security(value)


class VaccinationReviewSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=[
            ("mark_valid", "Mark valid"),
            ("mark_missing", "Mark missing"),
            ("mark_expired", "Mark expired"),
            ("mark_incomplete", "Mark incomplete"),
            ("prescribe", "Prescribe"),
            ("administer", "Administer"),
        ],
        required=False,
    )
    status = serializers.ChoiceField(
        choices=[
            ("valid", "Valid"),
            ("missing", "Missing"),
            ("expired", "Expired"),
            ("incomplete", "Incomplete"),
            ("prescribed", "Prescribed"),
            ("administered", "Administered"),
            ("doctor_cleared", "Doctor Cleared"),
            ("second_dose_due", "Second Dose Due"),
        ],
        required=False,
    )
    vaccine_type = serializers.ChoiceField(choices=VaccinationRecord._meta.get_field("vaccine_type").choices)
    vaccine_name = serializers.CharField(required=False, allow_blank=True)
    brand_name = serializers.CharField(required=False, allow_blank=True)
    batch_number = serializers.CharField(required=False, allow_blank=True)
    vaccinator_name = serializers.CharField(required=False, allow_blank=True)
    vaccination_facility_name = serializers.CharField(required=False, allow_blank=True)
    vaccination_facility_address = serializers.CharField(required=False, allow_blank=True)
    certificate_upload = serializers.FileField(required=False, allow_empty_file=False)
    dose_number = serializers.IntegerField(required=False, min_value=1, default=1)
    date_administered = serializers.DateField(required=False, allow_null=True)
    expiry_date = serializers.DateField(required=False, allow_null=True)
    reminder_date = serializers.DateField(required=False, allow_null=True)
    doctor_clearance = serializers.BooleanField(required=False, default=False)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_certificate_upload(self, value):
        return validate_uploaded_file_security(value)
