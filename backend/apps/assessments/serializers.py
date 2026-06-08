import copy

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.assessments.models import AssessmentFormQuestion, AssessmentFormResponse, AssessmentFormSection, AssessmentFormTemplate, AssessmentRequirementSet, AssessmentType, Appointment, FitnessDecision, HealthDeclaration, MedicalAssessment, PhysicalExamination
from apps.facilities.models import MedicalFacility
from apps.food_handlers.models import FoodHandlerProfile
from apps.lab_tests.serializers import LabTestSerializer
from apps.payments.models import PaymentTransaction
from apps.vaccinations.serializers import VaccinationRecordSerializer

User = get_user_model()


def validate_model(instance):
    try:
        instance.full_clean()
    except DjangoValidationError as exc:
        raise serializers.ValidationError(exc.message_dict if hasattr(exc, "message_dict") else exc.messages) from exc


class AssessmentFormQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentFormQuestion
        fields = (
            "id", "section", "key", "label", "help_text", "placeholder", "question_type", "required",
            "options", "validation_rules", "conditional_logic", "risk_flag_rules", "privacy_classification",
            "respondent_role", "sort_order", "is_active", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        instance = copy.copy(self.instance) if self.instance else AssessmentFormQuestion()
        for field, value in attrs.items():
            setattr(instance, field, value)
        validate_model(instance)
        return attrs


class AssessmentFormSectionSerializer(serializers.ModelSerializer):
    questions = AssessmentFormQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = AssessmentFormSection
        fields = ("id", "template", "key", "title", "description", "sort_order", "visibility_rules", "required_completion", "questions", "created_at", "updated_at")
        read_only_fields = ("id", "questions", "created_at", "updated_at")

    def validate(self, attrs):
        instance = copy.copy(self.instance) if self.instance else AssessmentFormSection()
        for field, value in attrs.items():
            setattr(instance, field, value)
        validate_model(instance)
        return attrs


class AssessmentFormTemplateSerializer(serializers.ModelSerializer):
    sections = AssessmentFormSectionSerializer(many=True, read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)

    class Meta:
        model = AssessmentFormTemplate
        fields = (
            "id", "name", "description", "form_type", "scope", "state", "state_name", "facility", "facility_name",
            "owner_organization", "version", "status", "is_mandatory", "requires_approval", "approved_by",
            "approved_at", "review_requested_at", "reviewed_by", "reviewed_at", "review_comment", "published_at",
            "effective_from", "effective_to", "created_by", "parent_template",
            "sections", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "version", "status", "approved_by", "approved_at", "review_requested_at", "reviewed_by",
            "reviewed_at", "review_comment", "published_at", "created_by", "parent_template", "sections",
            "created_at", "updated_at",
        )

    def validate(self, attrs):
        instance = copy.copy(self.instance) if self.instance else AssessmentFormTemplate()
        for field, value in attrs.items():
            setattr(instance, field, value)
        validate_model(instance)
        return attrs


class AssessmentFormRejectionSerializer(serializers.Serializer):
    reason = serializers.CharField()


class AssessmentRequirementSetSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)

    class Meta:
        model = AssessmentRequirementSet
        fields = (
            "id", "name", "description", "scope", "state", "state_name", "facility", "facility_name",
            "assessment_type", "food_handler_category", "employer_category", "illness_condition",
            "required_forms", "required_documents", "required_lab_tests", "required_vaccinations",
            "required_approvals", "blocking_requirements", "advisory_requirements", "version", "status",
            "effective_from", "effective_to", "created_by", "created_at", "updated_at",
        )
        read_only_fields = ("id", "version", "status", "created_by", "created_at", "updated_at")

    def validate(self, attrs):
        instance = copy.copy(self.instance) if self.instance else AssessmentRequirementSet()
        for field, value in attrs.items():
            if field != "required_forms":
                setattr(instance, field, value)
        validate_model(instance)
        return attrs

    def validate_required_forms(self, templates):
        for template in templates:
            if template.status not in {"published", "active"}:
                raise serializers.ValidationError("Requirement sets can only reference published or active form templates.")
        return templates


class AssessmentRequirementResolveSerializer(serializers.Serializer):
    assessment = serializers.PrimaryKeyRelatedField(queryset=MedicalAssessment.objects.all())
    assessment_type = serializers.ChoiceField(choices=AssessmentType.choices, required=False)


class AssessmentFormResponseSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source="template.name", read_only=True)
    form_type = serializers.CharField(source="template.form_type", read_only=True)

    class Meta:
        model = AssessmentFormResponse
        fields = (
            "id", "assessment", "template", "template_name", "form_type", "template_version", "respondent",
            "respondent_role", "status", "response_data", "question_snapshot", "risk_flags", "is_required",
            "is_locked", "version", "previous_response", "submitted_at", "validated_by", "validated_at",
            "created_at", "updated_at",
        )
        read_only_fields = fields


class AssessmentFormResponseSummarySerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source="template.name", read_only=True)
    form_type = serializers.CharField(source="template.form_type", read_only=True)

    class Meta:
        model = AssessmentFormResponse
        fields = (
            "id", "assessment", "template", "template_name", "form_type", "template_version",
            "respondent_role", "status", "is_required", "is_locked", "version", "submitted_at",
            "validated_at", "created_at", "updated_at",
        )
        read_only_fields = fields


class AssessmentFormResponseDraftSerializer(serializers.Serializer):
    response_data = serializers.DictField()


class AssessmentFormResponseReopenSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class AppointmentSerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.get_full_name", read_only=True)
    payment_status = serializers.SerializerMethodField()
    employer_name = serializers.CharField(source="food_handler.employer.business_name", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "food_handler",
            "food_handler_name",
            "facility",
            "facility_name",
            "doctor",
            "doctor_name",
            "employer_name",
            "appointment_date",
            "status",
            "payment_status",
            "reason",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "food_handler_name",
            "facility_name",
            "doctor",
            "doctor_name",
            "employer_name",
            "status",
            "payment_status",
            "created_at",
            "updated_at",
        )

    def get_payment_status(self, appointment):
        assessment = appointment.assessments.select_related("payment_transaction").first()
        if not assessment or not assessment.payment_transaction:
            return "missing"
        return assessment.payment_transaction.status


class AppointmentTransitionSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
    reason = serializers.CharField(required=False, allow_blank=True)


class AssessmentWorkflowItemSerializer(serializers.Serializer):
    code = serializers.CharField()
    label = serializers.CharField()
    detail = serializers.CharField(required=False)
    blocking = serializers.BooleanField(required=False)
    status = serializers.CharField(required=False)


class AssessmentNextActionSerializer(serializers.Serializer):
    code = serializers.CharField()
    label = serializers.CharField()


class AssessmentStatusSnapshotSerializer(serializers.Serializer):
    assessment = serializers.UUIDField()
    current_status = serializers.CharField()
    current_status_label = serializers.CharField()
    stage = serializers.CharField()
    stage_label = serializers.CharField()
    next_action = AssessmentNextActionSerializer()
    blockers = AssessmentWorkflowItemSerializer(many=True)
    warnings = AssessmentWorkflowItemSerializer(many=True)
    steps = AssessmentWorkflowItemSerializer(many=True)
    can_cancel = serializers.BooleanField()
    can_close = serializers.BooleanField()
    can_proceed = serializers.BooleanField()
    updated_at = serializers.DateTimeField()


class AssessmentAuditTimelineItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    action = serializers.CharField()
    event = serializers.CharField()
    label = serializers.CharField()
    actor_name = serializers.CharField(allow_blank=True)
    actor_role = serializers.CharField(allow_blank=True)
    target_type = serializers.CharField(allow_blank=True)
    target_id = serializers.CharField(allow_blank=True)
    metadata = serializers.DictField()
    created_at = serializers.DateTimeField()


class AppointmentRescheduleSerializer(AppointmentTransitionSerializer):
    appointment_date = serializers.DateTimeField()


class AppointmentAssignDoctorSerializer(serializers.Serializer):
    doctor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


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
            "assessment_type",
            "status",
            "declaration_status",
            "physical_exam_status",
            "lab_status",
            "vaccination_status",
            "final_decision",
            "return_to_work_date",
            "doctor_notes",
            "decision_draft",
            "decision_draft_return_to_work_date",
            "decision_draft_notes",
            "decision_draft_saved_at",
            "digital_signature_hash",
            "signed_by",
            "signed_at",
            "can_request_certificate",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        role = getattr(getattr(request, "user", None), "role", "")
        if role not in {"doctor", "facility_admin", "super_admin"}:
            data.pop("doctor_notes", None)
            data.pop("decision_draft_notes", None)
            data.pop("digital_signature_hash", None)
            data.pop("signed_by", None)
        return data


class FacilityAssessmentSerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    food_handler_identifier = serializers.CharField(source="food_handler.system_identifier", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    branch = serializers.CharField(source="food_handler.business_branch", read_only=True)
    branch_name = serializers.CharField(source="food_handler.business_branch.name", read_only=True)
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.get_full_name", read_only=True)
    appointment_status = serializers.CharField(source="appointment.status", read_only=True)
    appointment_date = serializers.DateTimeField(source="appointment.appointment_date", read_only=True)
    payment_status = serializers.SerializerMethodField()
    certificate_submission_status = serializers.SerializerMethodField()
    can_view_clinical = serializers.SerializerMethodField()
    doctor_notes = serializers.SerializerMethodField()

    class Meta:
        model = MedicalAssessment
        fields = (
            "id",
            "food_handler",
            "food_handler_name",
            "food_handler_identifier",
            "employer",
            "employer_name",
            "branch",
            "branch_name",
            "facility",
            "facility_name",
            "doctor",
            "doctor_name",
            "appointment",
            "appointment_status",
            "appointment_date",
            "assessment_date",
            "payment_transaction",
            "payment_status",
            "status",
            "declaration_status",
            "physical_exam_status",
            "lab_status",
            "vaccination_status",
            "final_decision",
            "certificate_submission_status",
            "return_to_work_date",
            "decision_draft",
            "decision_draft_return_to_work_date",
            "decision_draft_notes",
            "decision_draft_saved_at",
            "signed_at",
            "signed_by",
            "digital_signature_hash",
            "can_request_certificate",
            "can_view_clinical",
            "doctor_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def _role(self):
        request = self.context.get("request")
        return getattr(getattr(request, "user", None), "role", "")

    def _can_view_clinical(self):
        return self._role() in {"facility_admin", "doctor"}

    def get_payment_status(self, assessment):
        return assessment.payment_transaction.status if assessment.payment_transaction else "missing"

    def get_certificate_submission_status(self, assessment):
        certificate_request = getattr(assessment, "certificate_request", None)
        if certificate_request:
            return certificate_request.status
        if getattr(assessment, "certificate", None):
            return "certificate_issued"
        if assessment.status == "submitted_for_state_validation":
            return "submitted_for_state_validation"
        return "not_submitted"

    def get_can_view_clinical(self, assessment):
        return self._can_view_clinical()

    def get_doctor_notes(self, assessment):
        return assessment.doctor_notes if self._can_view_clinical() else ""

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not self._can_view_clinical():
            data.pop("decision_draft_notes", None)
        return data


class FacilityAssessmentDetailSerializer(FacilityAssessmentSerializer):
    health_declaration = serializers.SerializerMethodField()
    physical_examination = serializers.SerializerMethodField()
    lab_tests = serializers.SerializerMethodField()
    vaccinations = serializers.SerializerMethodField()

    class Meta(FacilityAssessmentSerializer.Meta):
        fields = FacilityAssessmentSerializer.Meta.fields + (
            "health_declaration",
            "physical_examination",
            "lab_tests",
            "vaccinations",
        )

    def get_health_declaration(self, assessment):
        if not self._can_view_clinical() or not hasattr(assessment, "health_declaration"):
            return None
        return HealthDeclarationSerializer(assessment.health_declaration).data

    def get_physical_examination(self, assessment):
        if not self._can_view_clinical() or not hasattr(assessment, "physical_examination"):
            return None
        return PhysicalExaminationSerializer(assessment.physical_examination).data

    def get_lab_tests(self, assessment):
        if self._role() not in {"facility_admin", "doctor", "lab_staff"}:
            return []
        return LabTestSerializer(assessment.lab_tests.all(), many=True).data

    def get_vaccinations(self, assessment):
        if not self._can_view_clinical():
            return []
        return VaccinationRecordSerializer(assessment.vaccinations.all(), many=True).data


class AssessmentAssignDoctorSerializer(serializers.Serializer):
    doctor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


class CreateMedicalAssessmentSerializer(serializers.Serializer):
    food_handler = serializers.PrimaryKeyRelatedField(queryset=FoodHandlerProfile.objects.all())
    facility = serializers.PrimaryKeyRelatedField(queryset=MedicalFacility.objects.all())
    payment_transaction = serializers.PrimaryKeyRelatedField(
        queryset=PaymentTransaction.objects.all(),
        required=False,
        allow_null=True,
    )
    appointment = serializers.PrimaryKeyRelatedField(queryset=Appointment.objects.all(), required=False, allow_null=True)
    assessment_type = serializers.ChoiceField(choices=AssessmentType.choices, required=False, default=AssessmentType.STANDARD)


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
            "version",
            "is_locked",
            "reopened_by",
            "reopened_at",
            "reopen_reason",
            "submitted_at",
            "validated_by_doctor",
            "validated_at",
            "clarification_requested_by",
            "clarification_requested_at",
            "clarification_reason",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "assessment",
            "assessment_status",
            "risk_flag",
            "version",
            "is_locked",
            "reopened_by",
            "reopened_at",
            "reopen_reason",
            "submitted_at",
            "validated_by_doctor",
            "validated_at",
            "clarification_requested_by",
            "clarification_requested_at",
            "clarification_reason",
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
            "version",
            "is_locked",
            "reopened_by",
            "reopened_at",
            "reopen_reason",
            "submitted_at",
            "validated_by_doctor",
            "validated_at",
            "clarification_requested_by",
            "clarification_requested_at",
            "clarification_reason",
            "created_at",
            "updated_at",
        )


class DeclarationReopenSerializer(serializers.Serializer):
    reason = serializers.CharField()


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
            "risk_flag",
            "is_completed",
            "completed_at",
            "examined_by",
            "examined_by_name",
            "examined_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "assessment", "risk_flag", "is_completed", "completed_at", "examined_by", "examined_by_name", "examined_at", "created_at", "updated_at")


class PhysicalExaminationSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalExamination
        exclude = ("id", "assessment", "risk_flag", "is_completed", "completed_at", "examined_by", "examined_at", "created_at", "updated_at")


class FitnessDecisionSerializer(serializers.Serializer):
    final_decision = serializers.ChoiceField(choices=FitnessDecision.choices)
    return_to_work_date = serializers.DateField(required=False, allow_null=True)
    doctor_notes = serializers.CharField(required=False, allow_blank=True)
    digital_signature_confirmation = serializers.BooleanField(required=False, default=False)


class FitnessDecisionDraftSerializer(serializers.Serializer):
    final_decision = serializers.ChoiceField(choices=FitnessDecision.choices)
    return_to_work_date = serializers.DateField(required=False, allow_null=True)
    doctor_notes = serializers.CharField(required=False, allow_blank=True)


class DeclarationClarificationSerializer(serializers.Serializer):
    reason = serializers.CharField()
