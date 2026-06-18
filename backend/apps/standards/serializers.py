from rest_framework import serializers

from apps.audit.models import AuditLog

from .models import (
    Approval,
    CertificateTemplate,
    CertificateValidityRule,
    EstablishmentCategory,
    FacilityRequirementRule,
    FoodHandlerCategory,
    IndicatorDisaggregatedValue,
    IndicatorDisaggregation,
    IndicatorEvidence,
    KPIInputMode,
    KPICalculationType,
    KPIProgressRelationship,
    KPIRecordInputType,
    KPIType,
    MEIndicator,
    MEIndicatorDataSource,
    MEIndicatorValue,
    MEIndicatorValueHistory,
    MedicalTestRule,
    PhysicalExaminationRule,
    PolicyDocument,
    PolicyVersion,
    QualitativeIndicatorConfig,
    ReportingTemplate,
    ReturnToWorkRule,
    StateAcknowledgement,
    StateConfigurationControl,
    VaccinationRule,
)


FOOD_HANDLERS_DATA_SOURCES = {
    "food_handler_registry",
    "medical_test_records",
    "test_results",
    "certificate_records",
    "facility_records",
    "facility_handler_mapping",
    "test_centers_labs",
    "inspections",
    "training_orientation",
    "payments",
}


class PolicyVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True, default="",
    )
    submitted_by_name = serializers.CharField(
        source="submitted_by.get_full_name", read_only=True, default="",
    )
    approved_by_name = serializers.CharField(
        source="approved_by.get_full_name", read_only=True, default="",
    )
    published_by_name = serializers.CharField(
        source="published_by.get_full_name", read_only=True, default="",
    )
    handler_category_count = serializers.IntegerField(read_only=True, default=0)
    medical_test_rule_count = serializers.IntegerField(read_only=True, default=0)
    vaccination_rule_count = serializers.IntegerField(read_only=True, default=0)
    acknowledgement_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = PolicyVersion
        fields = (
            "id", "version_code", "title", "description", "version_type",
            "status", "effective_start_date", "effective_end_date",
            "requires_state_acknowledgement", "change_summary",
            "created_by", "created_by_name",
            "submitted_by", "submitted_by_name",
            "approved_by", "approved_by_name",
            "published_by", "published_by_name",
            "submitted_at", "approved_at", "published_at", "retired_at",
            "handler_category_count", "medical_test_rule_count",
            "vaccination_rule_count", "acknowledgement_count",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "status", "submitted_by", "approved_by", "published_by",
            "retired_by", "submitted_at", "approved_at", "published_at",
            "retired_at", "created_at", "updated_at",
        )


class PolicyVersionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyVersion
        fields = (
            "version_code", "title", "description", "version_type",
            "effective_start_date", "effective_end_date",
            "requires_state_acknowledgement", "change_summary",
        )

    def validate_version_code(self, value):
        if PolicyVersion.objects.filter(version_code=value).exists():
            raise serializers.ValidationError("Version code must be unique.")
        return value


class PolicyVersionDetailSerializer(PolicyVersionSerializer):
    food_handler_categories = serializers.SerializerMethodField()
    establishment_categories = serializers.SerializerMethodField()
    medical_test_rules = serializers.SerializerMethodField()
    physical_examination_rules = serializers.SerializerMethodField()
    vaccination_rules = serializers.SerializerMethodField()
    certificate_templates = serializers.SerializerMethodField()
    certificate_validity_rules = serializers.SerializerMethodField()
    return_to_work_rules = serializers.SerializerMethodField()
    facility_requirement_rules = serializers.SerializerMethodField()
    reporting_templates = serializers.SerializerMethodField()
    me_indicators = serializers.SerializerMethodField()
    state_acknowledgements = serializers.SerializerMethodField()
    policy_documents = serializers.SerializerMethodField()
    completeness = serializers.SerializerMethodField()

    class Meta(PolicyVersionSerializer.Meta):
        fields = PolicyVersionSerializer.Meta.fields + (
            "food_handler_categories", "establishment_categories",
            "medical_test_rules", "physical_examination_rules",
            "vaccination_rules", "certificate_templates",
            "certificate_validity_rules", "return_to_work_rules",
            "facility_requirement_rules", "reporting_templates",
            "me_indicators", "state_acknowledgements",
            "policy_documents", "completeness",
        )

    def _summary(self, qs, name_field="name", code_field="code"):
        return list(qs.values("id", name_field, code_field, "status"))

    def get_food_handler_categories(self, obj):
        return self._summary(obj.food_handler_categories.all())

    def get_establishment_categories(self, obj):
        return self._summary(obj.establishment_categories.all())

    def get_medical_test_rules(self, obj):
        return list(obj.medical_test_rules.all().values(
            "id", "name", "code", "rule_type", "test_type",
            "blocks_certification", "status",
        ))

    def get_physical_examination_rules(self, obj):
        return list(obj.physical_examination_rules.all().values(
            "id", "indicator_name", "code", "severity",
            "blocks_certification", "status",
        ))

    def get_vaccination_rules(self, obj):
        return list(obj.vaccination_rules.all().values(
            "id", "vaccine_name", "vaccine_code", "required",
            "validity_months", "status",
        ))

    def get_certificate_templates(self, obj):
        return list(obj.certificate_templates.all().values(
            "id", "template_name", "template_version", "status",
        ))

    def get_certificate_validity_rules(self, obj):
        return list(obj.certificate_validity_rules.all().values(
            "id", "certificate_validity_days",
            "routine_assessment_interval_days", "status",
        ))

    def get_return_to_work_rules(self, obj):
        return list(obj.return_to_work_rules.all().values(
            "id", "condition_name", "condition_code",
            "default_exclusion_hours", "status",
        ))

    def get_facility_requirement_rules(self, obj):
        return list(obj.facility_requirement_rules.all().values(
            "id", "requirement_name", "requirement_code",
            "category", "mandatory", "status",
        ))

    def get_reporting_templates(self, obj):
        return list(obj.reporting_templates.all().values(
            "id", "template_name", "template_code",
            "reporting_frequency", "status",
        ))

    def get_me_indicators(self, obj):
        return list(obj.me_indicators.all().values(
            "id", "indicator_name", "indicator_code",
            "data_source", "mandatory", "status",
        ))

    def get_state_acknowledgements(self, obj):
        return list(obj.state_acknowledgements.select_related("state").values(
            "id", "state__name", "status", "acknowledged_at",
        ))

    def get_policy_documents(self, obj):
        return list(obj.policy_documents.all().values(
            "id", "title", "document_type", "version_label", "status",
        ))

    def get_completeness(self, obj):
        return {
            "has_certificate_template": obj.certificate_templates.exists(),
            "has_medical_test_rules": obj.medical_test_rules.exists(),
            "has_validity_rules": obj.certificate_validity_rules.exists(),
            "has_reporting_template": obj.reporting_templates.exists(),
            "has_handler_categories": obj.food_handler_categories.exists(),
            "has_vaccination_rules": obj.vaccination_rules.exists(),
        }


class FoodHandlerCategorySerializer(serializers.ModelSerializer):
    policy_version_code = serializers.CharField(
        source="policy_version.version_code", read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True, default="",
    )

    class Meta:
        model = FoodHandlerCategory
        fields = (
            "id", "policy_version", "policy_version_code",
            "name", "code", "description", "risk_level",
            "certificate_required", "medical_test_rule_group_id",
            "vaccination_rule_group_id", "nationally_locked",
            "allow_state_subcategories", "status",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")


class EstablishmentCategorySerializer(serializers.ModelSerializer):
    policy_version_code = serializers.CharField(
        source="policy_version.version_code", read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True, default="",
    )

    class Meta:
        model = EstablishmentCategory
        fields = (
            "id", "policy_version", "policy_version_code",
            "name", "code", "description", "risk_level",
            "required_handler_categories", "compliance_requirements",
            "inspection_required", "required_documents",
            "allow_state_subcategories", "status",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")


class MedicalTestRuleSerializer(serializers.ModelSerializer):
    policy_version_code = serializers.CharField(
        source="policy_version.version_code", read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True, default="",
    )

    class Meta:
        model = MedicalTestRule
        fields = (
            "id", "policy_version", "policy_version_code",
            "name", "code", "test_type", "rule_type", "result_type",
            "accepted_values", "blocking_values", "blocks_certification",
            "requires_attachment", "requires_doctor_validation",
            "requires_lab_validation", "validity_days",
            "applicable_categories", "applicable_establishment_risk_levels",
            "emergency_activation_rule", "status",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def validate(self, attrs):
        rule_type = attrs.get("rule_type", getattr(self.instance, "rule_type", None))
        result_type = attrs.get("result_type", getattr(self.instance, "result_type", None))
        if rule_type == "mandatory" and not result_type:
            raise serializers.ValidationError(
                {"result_type": "Mandatory test rules must include a result type."}
            )
        blocks = attrs.get("blocks_certification", getattr(self.instance, "blocks_certification", False))
        blocking_values = attrs.get("blocking_values", getattr(self.instance, "blocking_values", []))
        if blocks and not blocking_values:
            raise serializers.ValidationError(
                {"blocking_values": "A blocking test must define which result values block certification."}
            )
        return attrs


class PhysicalExaminationRuleSerializer(serializers.ModelSerializer):
    policy_version_code = serializers.CharField(
        source="policy_version.version_code", read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True, default="",
    )

    class Meta:
        model = PhysicalExaminationRule
        fields = (
            "id", "policy_version", "policy_version_code",
            "indicator_name", "code", "description", "severity",
            "requires_doctor_notes", "blocks_certification",
            "requires_reexamination", "requires_exclusion",
            "return_to_work_rule", "public_health_escalation", "status",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")


class VaccinationRuleSerializer(serializers.ModelSerializer):
    policy_version_code = serializers.CharField(
        source="policy_version.version_code", read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True, default="",
    )

    class Meta:
        model = VaccinationRule
        fields = (
            "id", "policy_version", "policy_version_code",
            "vaccine_name", "vaccine_code", "required",
            "dose_schedule", "validity_months", "grace_period_days",
            "evidence_required", "evidence_fields",
            "blocks_certification_if_missing", "blocks_certification_if_expired",
            "requires_doctor_prescription_if_missing",
            "applicable_categories", "status",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def validate(self, attrs):
        required = attrs.get("required", getattr(self.instance, "required", False))
        dose_schedule = attrs.get("dose_schedule", getattr(self.instance, "dose_schedule", []))
        validity_months = attrs.get("validity_months", getattr(self.instance, "validity_months", None))
        if required and not dose_schedule and not validity_months:
            raise serializers.ValidationError(
                "Required vaccines must have a dose schedule or validity period."
            )
        return attrs


class CertificateTemplateSerializer(serializers.ModelSerializer):
    policy_version_code = serializers.CharField(
        source="policy_version.version_code", read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True, default="",
    )

    class Meta:
        model = CertificateTemplate
        fields = (
            "id", "policy_version", "policy_version_code",
            "template_name", "template_version",
            "layout_config", "required_fields",
            "certificate_number_format", "qr_payload_config",
            "public_verification_fields", "status_rules",
            "revocation_reasons", "digital_signature_config", "status",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")


class CertificateValidityRuleSerializer(serializers.ModelSerializer):
    policy_version_code = serializers.CharField(
        source="policy_version.version_code", read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True, default="",
    )

    class Meta:
        model = CertificateValidityRule
        fields = (
            "id", "policy_version", "policy_version_code",
            "routine_assessment_interval_days", "certificate_validity_days",
            "renewal_window_days", "grace_period_days",
            "expiry_reminder_days", "illness_suspension_enabled",
            "emergency_revalidation_enabled", "status",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")


class ReturnToWorkRuleSerializer(serializers.ModelSerializer):
    policy_version_code = serializers.CharField(
        source="policy_version.version_code", read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True, default="",
    )

    class Meta:
        model = ReturnToWorkRule
        fields = (
            "id", "policy_version", "policy_version_code",
            "condition_name", "condition_code",
            "default_exclusion_hours", "requires_medical_clearance",
            "requires_lab_clearance", "negative_samples_required",
            "sample_interval_hours", "requires_health_authority_approval",
            "employer_acknowledgement_required",
            "clearance_document_required", "status",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")


class FacilityRequirementRuleSerializer(serializers.ModelSerializer):
    policy_version_code = serializers.CharField(
        source="policy_version.version_code", read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True, default="",
    )

    class Meta:
        model = FacilityRequirementRule
        fields = (
            "id", "policy_version", "policy_version_code",
            "requirement_name", "requirement_code", "category",
            "mandatory", "evidence_type", "renewal_required",
            "renewal_interval_days", "suspension_trigger", "status",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")


class ReportingTemplateSerializer(serializers.ModelSerializer):
    policy_version_code = serializers.CharField(
        source="policy_version.version_code", read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True, default="",
    )

    class Meta:
        model = ReportingTemplate
        fields = (
            "id", "policy_version", "policy_version_code",
            "template_name", "template_code", "reporting_frequency",
            "deadline_rule", "required_sections", "required_indicators",
            "required_uploads", "scoring_config",
            "approval_required", "status",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")


class QualitativeIndicatorConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualitativeIndicatorConfig
        fields = (
            "id", "input_type", "scale_min", "scale_max",
            "scale_labels_json", "category_options_json",
            "requires_narrative", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        input_type = attrs.get("input_type", getattr(self.instance, "input_type", "text"))
        scale_min = attrs.get("scale_min", getattr(self.instance, "scale_min", None))
        scale_max = attrs.get("scale_max", getattr(self.instance, "scale_max", None))
        options = attrs.get("category_options_json", getattr(self.instance, "category_options_json", []))
        if input_type in {"likert_scale", "rubric"}:
            if scale_min is None or scale_max is None:
                raise serializers.ValidationError("Scale minimum and maximum are required for rating indicators.")
            if scale_min >= scale_max:
                raise serializers.ValidationError("Scale minimum must be less than scale maximum.")
        if input_type in {"category", "rubric"} and not options:
            raise serializers.ValidationError("Category options are required for category and rubric indicators.")
        return attrs


class IndicatorDisaggregationSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicatorDisaggregation
        fields = (
            "id", "indicator", "source_type", "field_id",
            "field_label", "level", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        field_id = attrs.get("field_id", getattr(self.instance, "field_id", ""))
        field_label = attrs.get("field_label", getattr(self.instance, "field_label", ""))
        level = attrs.get("level", getattr(self.instance, "level", 1))
        if not field_id.strip():
            raise serializers.ValidationError("Disaggregation field id is required.")
        if not field_label.strip():
            raise serializers.ValidationError("Disaggregation field label is required.")
        if level < 1:
            raise serializers.ValidationError("Disaggregation level must be 1 or higher.")
        return attrs


class IndicatorDisaggregatedValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicatorDisaggregatedValue
        fields = (
            "id", "indicator_value", "indicator", "period_start",
            "period_end", "dimension_values_json", "value_numeric",
            "created_at", "updated_at",
        )
        read_only_fields = fields


class IndicatorEvidenceSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.get_full_name", read_only=True, default="",
    )
    approved_by_name = serializers.CharField(
        source="approved_by.get_full_name", read_only=True, default="",
    )
    indicator_name = serializers.CharField(
        source="indicator.indicator_name", read_only=True, default="",
    )

    class Meta:
        model = IndicatorEvidence
        fields = (
            "id", "indicator", "indicator_name", "indicator_value",
            "document_id", "file_id", "file_url", "title",
            "description", "evidence_type", "approval_status",
            "uploaded_by", "uploaded_by_name", "approved_by",
            "approved_by_name", "approved_at", "rejection_comment",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "indicator_name", "approval_status", "uploaded_by",
            "uploaded_by_name", "approved_by", "approved_by_name",
            "approved_at", "rejection_comment", "created_at", "updated_at",
        )

    def validate(self, attrs):
        document_id = attrs.get("document_id", getattr(self.instance, "document_id", ""))
        file_id = attrs.get("file_id", getattr(self.instance, "file_id", ""))
        file_url = attrs.get("file_url", getattr(self.instance, "file_url", ""))
        description = attrs.get("description", getattr(self.instance, "description", ""))
        evidence_type = attrs.get("evidence_type", getattr(self.instance, "evidence_type", "text"))
        if evidence_type == "file" and not (file_id or file_url):
            raise serializers.ValidationError("File evidence requires a file id or file URL.")
        if evidence_type == "url" and not file_url:
            raise serializers.ValidationError("URL evidence requires a URL.")
        if evidence_type == "text" and not (description or document_id):
            raise serializers.ValidationError("Text evidence requires a description or linked document.")
        return attrs


class MEIndicatorSerializer(serializers.ModelSerializer):
    policy_version_code = serializers.CharField(
        source="policy_version.version_code", read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True, default="",
    )
    qualitative_config = QualitativeIndicatorConfigSerializer(required=False, allow_null=True)
    disaggregations = IndicatorDisaggregationSerializer(many=True, read_only=True)

    class Meta:
        model = MEIndicator
        fields = (
            "id", "policy_version", "policy_version_code",
            "indicator_name", "indicator_code", "description",
            "kpi_type", "unit_of_measurement", "input_mode",
            "record_input_type", "progress_cumulative_relationship",
            "target_direction", "calculation_type", "calculation_source",
            "numerator_definition", "denominator_definition",
            "policy_standard_code", "rule_parameter_key",
            "allow_manual_override", "override_requires_reason",
            "last_calculated_at", "latest_value", "achievement_value",
            "visibility_scope",
            "formula_config", "data_source", "reporting_frequency",
            "target_value", "threshold_config", "visualization_type",
            "federal_dashboard_visible", "state_dashboard_visible",
            "mandatory", "status", "qualitative_config",
            "disaggregations",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def validate(self, attrs):
        formula_config = attrs.get("formula_config", getattr(self.instance, "formula_config", {}) or {})
        kpi_type = attrs.get("kpi_type", formula_config.get("indicator_type", getattr(self.instance, "kpi_type", KPIType.QUANTITATIVE)))
        input_mode = attrs.get("input_mode", formula_config.get("input_mode", getattr(self.instance, "input_mode", KPIInputMode.MANUAL)))
        if input_mode == "automated":
            input_mode = KPIInputMode.AUTOMATIC
            attrs["input_mode"] = KPIInputMode.AUTOMATIC
        record_input_type = attrs.get("record_input_type", formula_config.get("record_input_mode", getattr(self.instance, "record_input_type", KPIRecordInputType.PROGRESS_ONLY)))
        relationship = attrs.get("progress_cumulative_relationship", formula_config.get("progress_relationship", getattr(self.instance, "progress_cumulative_relationship", KPIProgressRelationship.DEPENDENT)))
        data_source = attrs.get("data_source", getattr(self.instance, "data_source", "manual"))
        calculation_method = formula_config.get("calculation_method", "")
        calculation_type = attrs.get("calculation_type", formula_config.get("calculation_type", getattr(self.instance, "calculation_type", "")))

        if record_input_type == KPIRecordInputType.PROGRESS_OR_CUMULATIVE and relationship == KPIProgressRelationship.INDEPENDENT:
            raise serializers.ValidationError("Independent relationship is invalid for progress-or-cumulative KPIs.")
        if kpi_type == KPIType.QUANTITATIVE and not attrs.get("unit_of_measurement", getattr(self.instance, "unit_of_measurement", "")):
            raise serializers.ValidationError("Quantitative KPIs require a unit of measurement.")
        if input_mode in {KPIInputMode.AUTOMATIC, KPIInputMode.HYBRID} and data_source not in FOOD_HANDLERS_DATA_SOURCES:
            raise serializers.ValidationError("Automatic and hybrid KPIs must use a Food Handlers operational data source.")
        if input_mode == KPIInputMode.HYBRID and attrs.get("allow_manual_override", getattr(self.instance, "allow_manual_override", False)) is False:
            raise serializers.ValidationError("Hybrid KPIs must allow manual override.")
        if calculation_type == KPICalculationType.PERCENTAGE and not (
            attrs.get("numerator_definition", getattr(self.instance, "numerator_definition", {}))
            and attrs.get("denominator_definition", getattr(self.instance, "denominator_definition", {}))
        ):
            raise serializers.ValidationError("Percentage KPIs require numerator and denominator definitions.")
        numerator_definition = attrs.get("numerator_definition", getattr(self.instance, "numerator_definition", {}))
        denominator_definition = attrs.get("denominator_definition", getattr(self.instance, "denominator_definition", {}))
        if calculation_method == "percentage" and not (
            (formula_config.get("numerator") and formula_config.get("denominator"))
            or (numerator_definition and denominator_definition)
            or (formula_config.get("numerator_definition") and formula_config.get("denominator_definition"))
        ):
            raise serializers.ValidationError("Percentage KPIs require numerator and denominator configuration.")
        return attrs

    def create(self, validated_data):
        formula_config = validated_data.get("formula_config", {}) or {}
        formula_config.setdefault("indicator_type", validated_data.get("kpi_type", KPIType.QUANTITATIVE))
        formula_config.setdefault("unit_of_measurement", validated_data.get("unit_of_measurement", "count"))
        formula_config.setdefault("input_mode", validated_data.get("input_mode", KPIInputMode.MANUAL))
        formula_config.setdefault("record_input_mode", validated_data.get("record_input_type", KPIRecordInputType.PROGRESS_ONLY))
        formula_config.setdefault("progress_relationship", validated_data.get("progress_cumulative_relationship", KPIProgressRelationship.DEPENDENT))
        formula_config.setdefault("target_direction", validated_data.get("target_direction", "higher_better"))
        formula_config.setdefault("calculation_type", validated_data.get("calculation_type", ""))
        formula_config.setdefault("calculation_source", validated_data.get("calculation_source", ""))
        formula_config.setdefault("numerator_definition", validated_data.get("numerator_definition", {}))
        formula_config.setdefault("denominator_definition", validated_data.get("denominator_definition", {}))
        formula_config.setdefault("policy_standard_code", validated_data.get("policy_standard_code", ""))
        formula_config.setdefault("rule_parameter_key", validated_data.get("rule_parameter_key", ""))
        formula_config.setdefault("allow_manual_override", validated_data.get("allow_manual_override", False))
        formula_config.setdefault("override_requires_reason", validated_data.get("override_requires_reason", False))
        validated_data["formula_config"] = formula_config
        qualitative_config = validated_data.pop("qualitative_config", None)
        indicator = super().create(validated_data)
        if qualitative_config:
            QualitativeIndicatorConfig.objects.create(indicator=indicator, **qualitative_config)
        return indicator

    def update(self, instance, validated_data):
        formula_config = validated_data.get("formula_config", instance.formula_config or {})
        for field, key in [
            ("kpi_type", "indicator_type"),
            ("unit_of_measurement", "unit_of_measurement"),
            ("input_mode", "input_mode"),
            ("record_input_type", "record_input_mode"),
            ("progress_cumulative_relationship", "progress_relationship"),
            ("target_direction", "target_direction"),
            ("calculation_type", "calculation_type"),
            ("calculation_source", "calculation_source"),
            ("numerator_definition", "numerator_definition"),
            ("denominator_definition", "denominator_definition"),
            ("policy_standard_code", "policy_standard_code"),
            ("rule_parameter_key", "rule_parameter_key"),
            ("allow_manual_override", "allow_manual_override"),
            ("override_requires_reason", "override_requires_reason"),
        ]:
            if field in validated_data:
                formula_config[key] = validated_data[field]
        validated_data["formula_config"] = formula_config
        qualitative_config = validated_data.pop("qualitative_config", serializers.empty)
        indicator = super().update(instance, validated_data)
        if qualitative_config is not serializers.empty:
            if qualitative_config is None:
                QualitativeIndicatorConfig.objects.filter(indicator=indicator).delete()
            else:
                QualitativeIndicatorConfig.objects.update_or_create(
                    indicator=indicator,
                    defaults=qualitative_config,
                )
        return indicator


class MEIndicatorValueHistorySerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(
        source="actor.get_full_name", read_only=True, default="",
    )

    class Meta:
        model = MEIndicatorValueHistory
        fields = (
            "id", "value", "action", "from_status", "to_status",
            "snapshot_json", "comment", "actor", "actor_name",
            "created_at", "updated_at",
        )
        read_only_fields = fields


class MEIndicatorValueSerializer(serializers.ModelSerializer):
    indicator_name = serializers.CharField(
        source="indicator.indicator_name", read_only=True,
    )
    indicator_code = serializers.CharField(
        source="indicator.indicator_code", read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True, default="",
    )
    submitted_by_name = serializers.CharField(
        source="submitted_by.get_full_name", read_only=True, default="",
    )
    approved_by_name = serializers.CharField(
        source="approved_by.get_full_name", read_only=True, default="",
    )
    history = MEIndicatorValueHistorySerializer(many=True, read_only=True)
    disaggregated_values = IndicatorDisaggregatedValueSerializer(many=True, read_only=True)
    evidence_items = IndicatorEvidenceSerializer(many=True, read_only=True)

    class Meta:
        model = MEIndicatorValue
        fields = (
            "id", "indicator", "indicator_name", "indicator_code",
            "period_start", "period_end",
            "progress_value_numeric", "cumulative_value_numeric",
            "qualitative_value_text", "qualitative_rating",
            "qualitative_category",
            "value_source", "source_reference_id", "approval_status",
            "calculation_snapshot_json", "evidence_json", "notes",
            "rejection_comment", "created_by", "created_by_name",
            "submitted_by", "submitted_by_name", "submitted_at",
            "approved_by", "approved_by_name", "approved_at",
            "history", "disaggregated_values", "evidence_items",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "indicator_name", "indicator_code", "approval_status",
            "created_by", "created_by_name", "submitted_by",
            "submitted_by_name", "submitted_at", "approved_by",
            "approved_by_name", "approved_at", "rejection_comment",
            "history", "disaggregated_values", "evidence_items",
            "created_at", "updated_at",
        )

    def validate(self, attrs):
        period_start = attrs.get("period_start", getattr(self.instance, "period_start", None))
        period_end = attrs.get("period_end", getattr(self.instance, "period_end", None))
        if period_start and period_end and period_start > period_end:
            raise serializers.ValidationError("Period start cannot be after period end.")
        indicator = attrs.get("indicator", getattr(self.instance, "indicator", None))
        try:
            config = getattr(indicator, "qualitative_config", None)
        except QualitativeIndicatorConfig.DoesNotExist:
            config = None
        if not config:
            return attrs

        qualitative_text = attrs.get("qualitative_value_text", getattr(self.instance, "qualitative_value_text", ""))
        qualitative_rating = attrs.get("qualitative_rating", getattr(self.instance, "qualitative_rating", None))
        qualitative_category = attrs.get("qualitative_category", getattr(self.instance, "qualitative_category", ""))
        if config.requires_narrative and not qualitative_text:
            raise serializers.ValidationError("Narrative evidence is required for this indicator.")
        if config.input_type in {"category", "rubric"}:
            options = [str(option) for option in (config.category_options_json or [])]
            if not qualitative_category:
                raise serializers.ValidationError("Select a qualitative category.")
            if options and qualitative_category not in options:
                raise serializers.ValidationError("Selected qualitative category is not configured for this indicator.")
        if config.input_type in {"likert_scale", "rubric"}:
            if qualitative_rating is None:
                raise serializers.ValidationError("Qualitative rating is required for this indicator.")
            if config.scale_min is not None and qualitative_rating < config.scale_min:
                raise serializers.ValidationError("Qualitative rating is below the configured scale minimum.")
            if config.scale_max is not None and qualitative_rating > config.scale_max:
                raise serializers.ValidationError("Qualitative rating is above the configured scale maximum.")
        return attrs


class MEIndicatorDataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MEIndicatorDataSource
        fields = (
            "id", "indicator", "source_type", "source_id",
            "calculation_method", "value_field_id",
            "numerator_config_json", "denominator_config_json",
            "filter_config_json", "unicity_field_id",
            "period_filter_mode", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        source_type = attrs.get("source_type", getattr(self.instance, "source_type", "manual"))
        calculation_method = attrs.get("calculation_method", getattr(self.instance, "calculation_method", "count"))
        if source_type not in FOOD_HANDLERS_DATA_SOURCES and source_type not in {"manual", "kpi"}:
            raise serializers.ValidationError("KPI data sources must be Food Handlers operational modules, manual, or KPI dependencies.")
        if calculation_method in {"percentage", "ratio"}:
            numerator = attrs.get("numerator_config_json", getattr(self.instance, "numerator_config_json", {}))
            denominator = attrs.get("denominator_config_json", getattr(self.instance, "denominator_config_json", {}))
            if not numerator or not denominator:
                raise serializers.ValidationError("Percentage and ratio rules require numerator and denominator configuration.")
        return attrs


class MEIndicatorCalculationSerializer(serializers.Serializer):
    data_source_id = serializers.UUIDField(required=False)
    source_type = serializers.CharField(required=False, default="manual")
    source_id = serializers.CharField(required=False, allow_blank=True, default="")
    calculation_method = serializers.ChoiceField(
        choices=["count", "unique_count", "sum", "average", "percentage", "ratio", "formula"],
        required=False,
    )
    value_field_id = serializers.CharField(required=False, allow_blank=True, default="")
    numerator_config_json = serializers.JSONField(required=False, default=dict)
    denominator_config_json = serializers.JSONField(required=False, default=dict)
    filter_config_json = serializers.JSONField(required=False, default=dict)
    unicity_field_id = serializers.CharField(required=False, allow_blank=True, default="")
    period_filter_mode = serializers.ChoiceField(
        choices=["all_time", "current_period", "custom_period"],
        required=False,
        default="current_period",
    )
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    records = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    def validate(self, attrs):
        if attrs["period_start"] > attrs["period_end"]:
            raise serializers.ValidationError("Period start cannot be after period end.")
        if not attrs.get("data_source_id") and not attrs.get("calculation_method"):
            raise serializers.ValidationError("Provide data_source_id or calculation_method.")
        if attrs.get("source_type") not in FOOD_HANDLERS_DATA_SOURCES and attrs.get("source_type") not in {"manual", "kpi"}:
            raise serializers.ValidationError("KPI data sources must be Food Handlers operational modules, manual, or KPI dependencies.")
        if attrs.get("calculation_method") in {"percentage", "ratio"} and not (attrs.get("numerator_config_json") and attrs.get("denominator_config_json")):
            raise serializers.ValidationError("Percentage and ratio calculations require numerator and denominator configuration.")
        return attrs


class MEIndicatorFormSourceSerializer(serializers.Serializer):
    form_template_id = serializers.UUIDField()
    calculation_method = serializers.ChoiceField(
        choices=["sum", "count", "unique_count", "average", "percentage"],
    )
    value_field_id = serializers.CharField(required=False, allow_blank=True, default="")
    numerator_config_json = serializers.JSONField(required=False, default=dict)
    denominator_config_json = serializers.JSONField(required=False, default=dict)
    filter_config_json = serializers.JSONField(required=False, default=dict)
    unicity_field_id = serializers.CharField(required=False, allow_blank=True, default="")
    period_filter_mode = serializers.ChoiceField(
        choices=["all_time", "current_period", "custom_period"],
        required=False,
        default="current_period",
    )


class MEIndicatorIndicatorSourceSerializer(serializers.Serializer):
    source_kpi_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        required=False,
    )
    source_indicator_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        required=False,
    )
    calculation_method = serializers.ChoiceField(choices=["sum", "average", "ratio", "formula"])
    period_filter_mode = serializers.ChoiceField(
        choices=["all_time", "current_period", "custom_period"],
        required=False,
        default="current_period",
    )

    def validate(self, attrs):
        ids = attrs.get("source_kpi_ids") or attrs.get("source_indicator_ids")
        if not ids:
            raise serializers.ValidationError("At least one source KPI is required.")
        attrs["source_kpi_ids"] = ids
        return attrs


class PolicyDocumentSerializer(serializers.ModelSerializer):
    policy_version_code = serializers.CharField(
        source="policy_version.version_code", read_only=True, default="",
    )
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.get_full_name", read_only=True, default="",
    )
    published_by_name = serializers.CharField(
        source="published_by.get_full_name", read_only=True, default="",
    )

    class Meta:
        model = PolicyDocument
        fields = (
            "id", "policy_version", "policy_version_code",
            "title", "document_type", "description",
            "file_url", "version_label", "target_audience",
            "requires_acknowledgement", "status",
            "uploaded_by", "uploaded_by_name",
            "published_by", "published_by_name",
            "published_at", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "status", "published_by", "published_at",
            "created_at", "updated_at",
        )


class ApprovalSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(
        source="requested_by.get_full_name", read_only=True, default="",
    )
    reviewer_name = serializers.CharField(
        source="reviewer.get_full_name", read_only=True, default="",
    )
    approver_name = serializers.CharField(
        source="approver.get_full_name", read_only=True, default="",
    )
    entity_label = serializers.SerializerMethodField()
    action_url = serializers.SerializerMethodField()
    change_diff = serializers.SerializerMethodField()

    class Meta:
        model = Approval
        fields = (
            "id", "entity_type", "entity_id",
            "requested_by", "requested_by_name",
            "reviewer", "reviewer_name",
            "approver", "approver_name",
            "status", "impact_level",
            "request_comment", "review_comment", "approval_comment",
            "entity_label", "action_url", "change_diff",
            "reviewed_at", "approved_at",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "reviewer", "approver", "reviewed_at", "approved_at",
            "created_at", "updated_at",
        )

    def get_entity_label(self, obj):
        if obj.entity_type == "PolicyVersion":
            policy = PolicyVersion.objects.filter(id=obj.entity_id).first()
            if policy:
                return f"{policy.version_code} — {policy.title}"
        return f"{obj.entity_type} {obj.entity_id}"

    def get_action_url(self, obj):
        if obj.entity_type == "PolicyVersion":
            return f"/federal/standards-policy/policy-governance/policy-versions/{obj.entity_id}"
        return ""

    def get_change_diff(self, obj):
        audit = AuditLog.objects.filter(
            target_type=obj.entity_type,
            target_id=str(obj.entity_id),
        ).exclude(old_value__isnull=True, new_value__isnull=True).order_by("-created_at").first()
        if audit:
            return {
                "old_value": audit.old_value or {},
                "new_value": audit.new_value or {},
                "event": audit.metadata.get("event", ""),
            }
        if obj.entity_type == "PolicyVersion":
            policy = PolicyVersion.objects.filter(id=obj.entity_id).first()
            if policy:
                return {
                    "old_value": {},
                    "new_value": {
                        "version_code": policy.version_code,
                        "title": policy.title,
                        "status": policy.status,
                        "effective_start_date": policy.effective_start_date,
                        "requires_state_acknowledgement": policy.requires_state_acknowledgement,
                    },
                    "event": "approval_requested",
                }
        return {"old_value": {}, "new_value": {}, "event": ""}


class ApprovalActionSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True, default="")


class StandardsAuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.get_full_name", read_only=True, default="")
    actor_email = serializers.CharField(source="actor.email", read_only=True, default="")
    state_name = serializers.CharField(source="state.name", read_only=True, default="")
    organization_name = serializers.CharField(source="organization.name", read_only=True, default="")
    event = serializers.SerializerMethodField()
    policy_version = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = (
            "id", "actor", "actor_name", "actor_email",
            "action", "target_type", "target_id",
            "organization", "organization_name", "state", "state_name",
            "ip_address", "user_agent", "old_value", "new_value",
            "metadata", "event", "policy_version",
            "created_at", "updated_at",
        )
        read_only_fields = fields

    def get_event(self, obj):
        return obj.metadata.get("event", "") if isinstance(obj.metadata, dict) else ""

    def get_policy_version(self, obj):
        if obj.target_type == "PolicyVersion":
            return obj.target_id
        metadata = obj.metadata if isinstance(obj.metadata, dict) else {}
        return str(metadata.get("policy_version") or metadata.get("policy_version_id") or "")


class StateAcknowledgementSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    policy_version_code = serializers.CharField(
        source="policy_version.version_code", read_only=True,
    )
    acknowledged_by_name = serializers.CharField(
        source="acknowledged_by.get_full_name", read_only=True, default="",
    )

    class Meta:
        model = StateAcknowledgement
        fields = (
            "id", "policy_version", "policy_version_code",
            "state", "state_name",
            "acknowledged_by", "acknowledged_by_name",
            "acknowledgement_comment", "acknowledged_at", "status",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "policy_version", "state",
            "acknowledged_by", "acknowledged_at",
            "created_at", "updated_at",
        )


class StateConfigurationControlSerializer(serializers.ModelSerializer):
    policy_version_code = serializers.CharField(
        source="policy_version.version_code", read_only=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True, default="",
    )

    class Meta:
        model = StateConfigurationControl
        fields = (
            "id", "policy_version", "policy_version_code",
            "config_domain", "label", "description",
            "federal_locked", "state_editable",
            "requires_federal_approval",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class PolicyVersionSubmitSerializer(serializers.Serializer):
    pass


class PolicyVersionPublishSerializer(serializers.Serializer):
    effective_date = serializers.DateTimeField(required=False)
    comment = serializers.CharField(required=False, allow_blank=True, default="")
