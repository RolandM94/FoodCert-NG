from django.contrib import admin

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


@admin.register(PolicyVersion)
class PolicyVersionAdmin(admin.ModelAdmin):
    list_display = ("version_code", "title", "status", "version_type", "effective_start_date", "created_at")
    list_filter = ("status", "version_type")
    search_fields = ("version_code", "title")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(FoodHandlerCategory)
class FoodHandlerCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "risk_level", "status", "policy_version")
    list_filter = ("status", "risk_level")
    search_fields = ("name", "code")


@admin.register(EstablishmentCategory)
class EstablishmentCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "risk_level", "status", "policy_version")
    list_filter = ("status", "risk_level")
    search_fields = ("name", "code")


@admin.register(MedicalTestRule)
class MedicalTestRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "rule_type", "test_type", "blocks_certification", "status")
    list_filter = ("status", "rule_type", "test_type")
    search_fields = ("name", "code")


@admin.register(PhysicalExaminationRule)
class PhysicalExaminationRuleAdmin(admin.ModelAdmin):
    list_display = ("indicator_name", "code", "severity", "blocks_certification", "status")
    list_filter = ("status", "severity")
    search_fields = ("indicator_name", "code")


@admin.register(VaccinationRule)
class VaccinationRuleAdmin(admin.ModelAdmin):
    list_display = ("vaccine_name", "vaccine_code", "required", "validity_months", "status")
    list_filter = ("status", "required")
    search_fields = ("vaccine_name", "vaccine_code")


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ("template_name", "template_version", "status", "policy_version")
    list_filter = ("status",)
    search_fields = ("template_name",)


@admin.register(CertificateValidityRule)
class CertificateValidityRuleAdmin(admin.ModelAdmin):
    list_display = ("certificate_validity_days", "routine_assessment_interval_days", "status")
    list_filter = ("status",)


@admin.register(ReturnToWorkRule)
class ReturnToWorkRuleAdmin(admin.ModelAdmin):
    list_display = ("condition_name", "condition_code", "default_exclusion_hours", "status")
    list_filter = ("status",)
    search_fields = ("condition_name", "condition_code")


@admin.register(FacilityRequirementRule)
class FacilityRequirementRuleAdmin(admin.ModelAdmin):
    list_display = ("requirement_name", "category", "mandatory", "status")
    list_filter = ("status", "category", "mandatory")
    search_fields = ("requirement_name", "requirement_code")


@admin.register(ReportingTemplate)
class ReportingTemplateAdmin(admin.ModelAdmin):
    list_display = ("template_name", "template_code", "reporting_frequency", "status")
    list_filter = ("status", "reporting_frequency")
    search_fields = ("template_name", "template_code")


@admin.register(MEIndicator)
class MEIndicatorAdmin(admin.ModelAdmin):
    list_display = ("indicator_name", "indicator_code", "data_source", "mandatory", "status")
    list_filter = ("status", "data_source", "mandatory")
    search_fields = ("indicator_name", "indicator_code")


@admin.register(MEIndicatorDataSource)
class MEIndicatorDataSourceAdmin(admin.ModelAdmin):
    list_display = ("indicator", "source_type", "calculation_method", "period_filter_mode", "created_at")
    list_filter = ("source_type", "calculation_method", "period_filter_mode")
    search_fields = ("indicator__indicator_name", "indicator__indicator_code", "source_id", "value_field_id")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(QualitativeIndicatorConfig)
class QualitativeIndicatorConfigAdmin(admin.ModelAdmin):
    list_display = ("indicator", "input_type", "scale_min", "scale_max", "requires_narrative")
    list_filter = ("input_type", "requires_narrative")
    search_fields = ("indicator__indicator_name", "indicator__indicator_code")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(IndicatorDisaggregation)
class IndicatorDisaggregationAdmin(admin.ModelAdmin):
    list_display = ("indicator", "field_label", "field_id", "source_type", "level")
    list_filter = ("source_type",)
    search_fields = ("indicator__indicator_name", "indicator__indicator_code", "field_id", "field_label")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(MEIndicatorValue)
class MEIndicatorValueAdmin(admin.ModelAdmin):
    list_display = ("indicator", "period_start", "period_end", "approval_status", "value_source", "created_at")
    list_filter = ("approval_status", "value_source")
    search_fields = ("indicator__indicator_name", "indicator__indicator_code", "notes")
    readonly_fields = ("id", "created_at", "updated_at", "submitted_at", "approved_at")


@admin.register(IndicatorDisaggregatedValue)
class IndicatorDisaggregatedValueAdmin(admin.ModelAdmin):
    list_display = ("indicator", "indicator_value", "period_start", "period_end", "value_numeric")
    list_filter = ("indicator",)
    search_fields = ("indicator__indicator_name", "indicator__indicator_code")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(IndicatorEvidence)
class IndicatorEvidenceAdmin(admin.ModelAdmin):
    list_display = ("title", "indicator", "indicator_value", "evidence_type", "approval_status", "uploaded_by")
    list_filter = ("approval_status", "evidence_type")
    search_fields = ("title", "description", "indicator__indicator_name", "indicator__indicator_code")
    readonly_fields = ("id", "created_at", "updated_at", "approved_at")


@admin.register(MEIndicatorValueHistory)
class MEIndicatorValueHistoryAdmin(admin.ModelAdmin):
    list_display = ("value", "action", "from_status", "to_status", "actor", "created_at")
    list_filter = ("action", "from_status", "to_status")
    search_fields = ("value__indicator__indicator_name", "comment")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(PolicyDocument)
class PolicyDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "document_type", "version_label", "status")
    list_filter = ("status", "document_type")
    search_fields = ("title",)


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ("entity_type", "entity_id", "status", "impact_level", "created_at")
    list_filter = ("status", "impact_level", "entity_type")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(StateAcknowledgement)
class StateAcknowledgementAdmin(admin.ModelAdmin):
    list_display = ("state", "policy_version", "status", "acknowledged_at")
    list_filter = ("status",)


@admin.register(StateConfigurationControl)
class StateConfigurationControlAdmin(admin.ModelAdmin):
    list_display = ("config_domain", "label", "federal_locked", "state_editable", "policy_version")
    list_filter = ("federal_locked", "state_editable")
    search_fields = ("config_domain", "label")
