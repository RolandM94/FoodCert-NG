from rest_framework import serializers

from apps.assessments.models import Appointment, FitnessDecision, HealthDeclaration, MedicalAssessment, PhysicalExamination
from apps.facilities.models import MedicalFacility
from apps.food_handlers.models import FoodHandlerProfile
from apps.payments.models import PaymentTransaction


class AppointmentSerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "food_handler",
            "food_handler_name",
            "facility",
            "facility_name",
            "appointment_date",
            "status",
            "reason",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "food_handler_name", "facility_name", "created_at", "updated_at")


class MedicalAssessmentSerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.get_full_name", read_only=True)
    can_request_certificate = serializers.BooleanField(read_only=True)

    class Meta:
        model = MedicalAssessment
        fields = (
            "id",
            "food_handler",
            "food_handler_name",
            "employer",
            "employer_name",
            "facility",
            "facility_name",
            "doctor",
            "doctor_name",
            "appointment",
            "assessment_date",
            "payment_transaction",
            "status",
            "declaration_status",
            "physical_exam_status",
            "lab_status",
            "vaccination_status",
            "final_decision",
            "return_to_work_date",
            "signed_at",
            "can_request_certificate",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CreateMedicalAssessmentSerializer(serializers.Serializer):
    food_handler = serializers.PrimaryKeyRelatedField(queryset=FoodHandlerProfile.objects.all())
    facility = serializers.PrimaryKeyRelatedField(queryset=MedicalFacility.objects.all())
    payment_transaction = serializers.PrimaryKeyRelatedField(
        queryset=PaymentTransaction.objects.all(),
        required=False,
        allow_null=True,
    )
    appointment = serializers.PrimaryKeyRelatedField(queryset=Appointment.objects.all(), required=False, allow_null=True)


class HealthDeclarationSerializer(serializers.ModelSerializer):
    assessment_status = serializers.CharField(source="assessment.status", read_only=True)

    class Meta:
        model = HealthDeclaration
        fields = (
            "id",
            "assessment",
            "assessment_status",
            "diarrhoea_vomiting_last_7_days",
            "fever_more_than_one_week",
            "skin_trouble",
            "boils_styes_sepsis",
            "discharge_eye_ear_nose_mouth",
            "recurring_skin_or_ear_infection",
            "recurring_bowel_disorder",
            "cholera_contact_last_5_days",
            "diarrhoea_vomiting_contact_last_7_days",
            "typhoid_paratyphoid_jaundice_contact_last_21_days",
            "typhoid_or_paratyphoid_carrier",
            "previous_or_current_typhoid",
            "certified_true",
            "risk_flag",
            "submitted_at",
            "validated_by_doctor",
            "validated_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "assessment",
            "assessment_status",
            "risk_flag",
            "submitted_at",
            "validated_by_doctor",
            "validated_at",
            "created_at",
            "updated_at",
        )


class HealthDeclarationSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthDeclaration
        exclude = (
            "id",
            "assessment",
            "risk_flag",
            "submitted_at",
            "validated_by_doctor",
            "validated_at",
            "created_at",
            "updated_at",
        )


class PhysicalExaminationSerializer(serializers.ModelSerializer):
    examined_by_name = serializers.CharField(source="examined_by.get_full_name", read_only=True)

    class Meta:
        model = PhysicalExamination
        fields = (
            "id",
            "assessment",
            "fever",
            "jaundice",
            "skin_infection",
            "boils_styes_sepsis",
            "discharge",
            "diarrhoea",
            "vomiting",
            "sore_throat_with_fever",
            "cough_or_flu",
            "known_typhoid_carrier_history",
            "other_notes",
            "examined_by",
            "examined_by_name",
            "examined_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "assessment", "examined_by", "examined_by_name", "examined_at", "created_at", "updated_at")


class PhysicalExaminationSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalExamination
        exclude = ("id", "assessment", "examined_by", "examined_at", "created_at", "updated_at")


class FitnessDecisionSerializer(serializers.Serializer):
    final_decision = serializers.ChoiceField(choices=FitnessDecision.choices)
    return_to_work_date = serializers.DateField(required=False, allow_null=True)
    doctor_notes = serializers.CharField(required=False, allow_blank=True)
