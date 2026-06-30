import copy

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.assessments.models import AssessmentFormQuestion, AssessmentFormResponse, AssessmentFormSection, AssessmentFormTemplate, AssessmentFormTemplateAdoption, AssessmentFormTemplateSnapshot, AssessmentRequirementSet, AssessmentType, Appointment, FitnessDecision, HealthDeclaration, MedicalAssessment, PhysicalExamination
from apps.facilities.models import MedicalFacility
from apps.food_handlers.models import FoodHandlerProfile
from apps.lab_tests.serializers import LabTestSerializer
from apps.payments.models import PaymentTransaction
from apps.payments.services import PaymentService
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
            "owner_level", "owner_id", "locked", "inherited_from_question", "editable_by_child", "deletable_by_child",
            "options", "validation_rules", "conditional_logic", "risk_flag", "risk_flag_rules", "privacy_classification",
            "respondent_role", "sort_order", "is_active", "created_at", "updated_at",
        )
        read_only_fields = ("id", "owner_level", "owner_id", "locked", "inherited_from_question", "editable_by_child", "deletable_by_child", "created_at", "updated_at")

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
        fields = ("id", "template", "key", "title", "description", "owner_level", "owner_id", "locked", "inherited_from_section", "editable_by_child", "deletable_by_child", "sort_order", "visibility_rules", "required_completion", "questions", "created_at", "updated_at")
        read_only_fields = ("id", "owner_level", "owner_id", "locked", "inherited_from_section", "editable_by_child", "deletable_by_child", "questions", "created_at", "updated_at")

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
            "owner_organization", "owner_level", "owner_id", "base_template", "superseded_by", "version", "status", "is_mandatory", "requires_approval", "approved_by",
            "approved_at", "review_requested_at", "reviewed_by", "reviewed_at", "review_comment", "published_at",
            "effective_from", "effective_to", "created_by", "parent_template",
            "sections", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "owner_level", "owner_id", "base_template", "superseded_by", "version", "status", "approved_by", "approved_at", "review_requested_at", "reviewed_by",
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
            "template_snapshot", "respondent_role", "status", "response_data", "question_snapshot", "risk_flags", "is_required",
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
            "template_snapshot", "respondent_role", "status", "is_required", "is_locked", "version", "submitted_at",
            "validated_at", "created_at", "updated_at",
        )
        read_only_fields = fields


class AssessmentFormTemplateAdoptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentFormTemplateAdoption
        fields = ("id", "parent_template", "child_template", "adopted_by_level", "adopted_by_id", "adopted_at", "status", "created_at", "updated_at")
        read_only_fields = fields


class AssessmentFormTemplateSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentFormTemplateSnapshot
        fields = ("id", "assessment", "federal_template", "state_template", "facility_template", "merged_schema", "generated_at", "created_at", "updated_at")
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
    assessment_id = serializers.SerializerMethodField()
    assessment_status = serializers.SerializerMethodField()
    declaration_status = serializers.SerializerMethodField()
    payment_transaction_id = serializers.SerializerMethodField()
    payment_receipt_number = serializers.SerializerMethodField()
    pay_at_facility_allowed = serializers.SerializerMethodField()
    can_confirm_payment_at_facility = serializers.SerializerMethodField()

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
            "payment_transaction_id",
            "payment_receipt_number",
            "pay_at_facility_allowed",
            "can_confirm_payment_at_facility",
            "assessment_id",
            "assessment_status",
            "declaration_status",
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
            "payment_transaction_id",
            "payment_receipt_number",
            "pay_at_facility_allowed",
            "can_confirm_payment_at_facility",
            "assessment_id",
            "assessment_status",
            "declaration_status",
            "created_at",
            "updated_at",
        )

    def _linked_assessment(self, appointment):
        return appointment.assessments.first()

    def get_payment_status(self, appointment):
        assessment = self._linked_assessment(appointment)
        return PaymentService.workflow_status(transaction_obj=getattr(assessment, "payment_transaction", None))

    def get_payment_transaction_id(self, appointment):
        assessment = self._linked_assessment(appointment)
        if not assessment or not assessment.payment_transaction_id:
            return None
        return str(assessment.payment_transaction_id)

    def get_payment_receipt_number(self, appointment):
        assessment = self._linked_assessment(appointment)
        transaction_obj = getattr(assessment, "payment_transaction", None)
        receipt = getattr(transaction_obj, "receipt", None) if transaction_obj else None
        return receipt.receipt_number if receipt else ""

    def get_pay_at_facility_allowed(self, appointment):
        assessment = self._linked_assessment(appointment)
        transaction_obj = getattr(assessment, "payment_transaction", None)
        if not transaction_obj:
            return False
        return bool((transaction_obj.metadata or {}).get("pay_at_facility_allowed"))

    def get_can_confirm_payment_at_facility(self, appointment):
        assessment = self._linked_assessment(appointment)
        return PaymentService.can_confirm_at_facility(transaction_obj=getattr(assessment, "payment_transaction", None))

    def get_assessment_id(self, appointment):
        assessment = self._linked_assessment(appointment)
        return str(assessment.id) if assessment else None

    def get_assessment_status(self, appointment):
        assessment = self._linked_assessment(appointment)
        return assessment.status if assessment else None

    def get_declaration_status(self, appointment):
        assessment = self._linked_assessment(appointment)
        return assessment.declaration_status if assessment else None


class AppointmentTransitionSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
    reason = serializers.CharField(required=False, allow_blank=True)


class FacilityPaymentConfirmationSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.CharField(required=False, allow_blank=True, default="cash")


class AppointmentDetailSerializer(AppointmentSerializer):
    food_handler_nin = serializers.CharField(source="food_handler.nin", read_only=True)
    food_handler_date_of_birth = serializers.DateField(source="food_handler.date_of_birth", read_only=True)
    food_handler_passport_photo = serializers.ImageField(source="food_handler.passport_photo", read_only=True)
    checked_in_at = serializers.SerializerMethodField()
    checked_in_by_name = serializers.SerializerMethodField()
    identity_verification_status = serializers.SerializerMethodField()
    identity_verified_at = serializers.SerializerMethodField()
    identity_verified_by_name = serializers.SerializerMethodField()
    identity_mismatch_reason = serializers.SerializerMethodField()

    class Meta(AppointmentSerializer.Meta):
        fields = AppointmentSerializer.Meta.fields + (
            "food_handler_nin",
            "food_handler_date_of_birth",
            "food_handler_passport_photo",
            "checked_in_at",
            "checked_in_by_name",
            "identity_verification_status",
            "identity_verified_at",
            "identity_verified_by_name",
            "identity_mismatch_reason",
        )
        read_only_fields = fields

    def _linked_assessment(self, appointment):
        return appointment.assessments.first()

    def get_checked_in_at(self, appointment):
        assessment = self._linked_assessment(appointment)
        return assessment.checked_in_at if assessment else None

    def get_checked_in_by_name(self, appointment):
        assessment = self._linked_assessment(appointment)
        if not assessment or not assessment.checked_in_by_id:
            return ""
        return assessment.checked_in_by.get_full_name() or assessment.checked_in_by.email

    def get_identity_verification_status(self, appointment):
        assessment = self._linked_assessment(appointment)
        return assessment.identity_verification_status if assessment else "pending"

    def get_identity_verified_at(self, appointment):
        assessment = self._linked_assessment(appointment)
        return assessment.identity_verified_at if assessment else None

    def get_identity_verified_by_name(self, appointment):
        assessment = self._linked_assessment(appointment)
        if not assessment or not assessment.identity_verified_by_id:
            return ""
        return assessment.identity_verified_by.get_full_name() or assessment.identity_verified_by.email

    def get_identity_mismatch_reason(self, appointment):
        assessment = self._linked_assessment(appointment)
        return assessment.identity_mismatch_reason if assessment else ""


class AssessmentCheckInSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)


class AssessmentIdentityMismatchSerializer(serializers.Serializer):
    reason = serializers.CharField()


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
    assigned_lab_staff_name = serializers.CharField(source="assigned_lab_staff.get_full_name", read_only=True)
    assigned_lab_unit_name = serializers.CharField(source="assigned_lab_unit.name", read_only=True)
    payment_status = serializers.SerializerMethodField()
    certificate_submission_status = serializers.SerializerMethodField()
    can_view_clinical = serializers.SerializerMethodField()
    doctor_notes = serializers.SerializerMethodField()
    workflow_recommendation = serializers.SerializerMethodField()
    checked_in_at = serializers.DateTimeField(read_only=True)
    checked_in_by_name = serializers.CharField(source="checked_in_by.get_full_name", read_only=True)
    identity_verification_status = serializers.CharField(read_only=True)
    identity_verified_at = serializers.DateTimeField(read_only=True)
    identity_verified_by_name = serializers.CharField(source="identity_verified_by.get_full_name", read_only=True)
    identity_mismatch_reason = serializers.CharField(read_only=True)

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
            "assigned_lab_staff",
            "assigned_lab_staff_name",
            "assigned_lab_unit",
            "assigned_lab_unit_name",
            "appointment",
            "appointment_status",
            "appointment_date",
            "assessment_date",
            "checked_in_at",
            "checked_in_by_name",
            "payment_transaction",
            "payment_status",
            "status",
            "identity_verification_status",
            "identity_verified_at",
            "identity_verified_by_name",
            "identity_mismatch_reason",
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
            "workflow_recommendation",
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
        return PaymentService.workflow_status(transaction_obj=assessment.payment_transaction)

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

    def get_workflow_recommendation(self, assessment):
        if not self._can_view_clinical():
            return None
        from apps.assessments.services import AssessmentService

        return AssessmentService.workflow_recommendation(assessment)

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
    reason = serializers.CharField(required=False, allow_blank=True)


class AssessmentAssignLabSerializer(serializers.Serializer):
    lab_staff = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    lab_unit = serializers.UUIDField(required=False, allow_null=True)
    reason = serializers.CharField(required=False, allow_blank=True)


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
    response_data = serializers.SerializerMethodField()
    merged_schema = serializers.SerializerMethodField()
    template_snapshot = serializers.SerializerMethodField()
    form_response_id = serializers.SerializerMethodField()
    form_response_status = serializers.SerializerMethodField()

    class Meta:
        model = HealthDeclaration
        fields = (
            "id",
            "assessment",
            "assessment_status",
            "template_snapshot",
            "merged_schema",
            "form_response_id",
            "form_response_status",
            "response_data",
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
            "template_snapshot",
            "merged_schema",
            "form_response_id",
            "form_response_status",
            "response_data",
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

    def _response(self, declaration):
        return getattr(declaration, "_current_form_response", None)

    def get_response_data(self, declaration):
        response = self._response(declaration)
        return response.response_data if response else {}

    def get_merged_schema(self, declaration):
        snapshot = getattr(declaration.assessment, "declaration_template_snapshot", None)
        return snapshot.merged_schema if snapshot else {}

    def get_template_snapshot(self, declaration):
        snapshot = getattr(declaration.assessment, "declaration_template_snapshot", None)
        return str(snapshot.id) if snapshot else None

    def get_form_response_id(self, declaration):
        response = self._response(declaration)
        return str(response.id) if response else None

    def get_form_response_status(self, declaration):
        response = self._response(declaration)
        return response.status if response else ""


class HealthDeclarationSubmitSerializer(serializers.Serializer):
    response_data = serializers.DictField(required=False)
    diarrhoea_vomiting_last_7_days = serializers.BooleanField(required=False)
    fever_more_than_one_week = serializers.BooleanField(required=False)
    skin_trouble = serializers.BooleanField(required=False)
    boils_styes_sepsis = serializers.BooleanField(required=False)
    discharge_eye_ear_nose_mouth = serializers.BooleanField(required=False)
    recurring_skin_or_ear_infection = serializers.BooleanField(required=False)
    recurring_bowel_disorder = serializers.BooleanField(required=False)
    cholera_contact_last_5_days = serializers.BooleanField(required=False)
    diarrhoea_vomiting_contact_last_7_days = serializers.BooleanField(required=False)
    typhoid_paratyphoid_jaundice_contact_last_21_days = serializers.BooleanField(required=False)
    typhoid_or_paratyphoid_carrier = serializers.BooleanField(required=False)
    previous_or_current_typhoid = serializers.BooleanField(required=False)
    certified_true = serializers.BooleanField(required=False)


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
