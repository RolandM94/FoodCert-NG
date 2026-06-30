from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from django.apps import apps
from django.db.models import Q, QuerySet

from apps.accounts.models import UserRole
from apps.reports.models import AnalyticsDataset, DashboardPrivacyLevel


REDACTED_VALUE = "***redacted***"
SUPPORTED_FIELD_TYPES = {"string", "number_whole", "number_decimal", "date", "datetime"}


def canonicalize_field_type(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in SUPPORTED_FIELD_TYPES:
        return normalized
    if normalized in {"number", "integer", "int", "whole", "count"}:
        return "number_whole"
    if normalized in {"float", "decimal", "currency", "amount", "percentage"}:
        return "number_decimal"
    if normalized in {"date"}:
        return "date"
    if normalized in {"datetime", "timestamp"}:
        return "datetime"
    return "string"


def build_field_type_metadata(inferred_types: dict[str, str], existing_metadata: dict[str, Any] | None = None, existing_active_types: dict[str, str] | None = None) -> dict[str, dict[str, str]]:
    existing_metadata = existing_metadata or {}
    existing_active_types = existing_active_types or {}
    metadata: dict[str, dict[str, str]] = {}
    for field_name, inferred_type in inferred_types.items():
        canonical_inferred = canonicalize_field_type(inferred_type)
        existing = existing_metadata.get(field_name, {}) if isinstance(existing_metadata.get(field_name), dict) else {}
        active_type = existing.get("type") or existing_active_types.get(field_name) or canonical_inferred
        metadata[field_name] = {
            "inferredType": canonical_inferred,
            "type": canonicalize_field_type(active_type),
        }
    return metadata


def active_field_types_from_metadata(metadata: dict[str, dict[str, str]]) -> dict[str, str]:
    return {field_name: canonicalize_field_type(config.get("type")) for field_name, config in metadata.items()}


@dataclass(frozen=True)
class DatasetDefinition:
    code: str
    name: str
    description: str
    module_source: str
    model_label: str
    allowed_account_types: list[str]
    allowed_roles: list[str]
    available_fields: list[str]
    field_labels: dict[str, str]
    field_types: dict[str, str]
    sensitive_fields: list[str] = field(default_factory=list)
    default_filters: dict[str, Any] = field(default_factory=dict)
    joinable_datasets: list[str] = field(default_factory=list)
    aggregation_rules: dict[str, Any] = field(default_factory=dict)
    required_permissions: list[str] = field(default_factory=list)
    privacy_level: str = DashboardPrivacyLevel.INTERNAL
    sample_ordering: list[str] = field(default_factory=lambda: ["-created_at"])
    state_scope_paths: list[str] = field(default_factory=list)
    employer_scope_paths: list[str] = field(default_factory=list)
    facility_scope_paths: list[str] = field(default_factory=list)
    base_filters: dict[str, Any] = field(default_factory=dict)
    computed_fields: dict[str, Any] = field(default_factory=dict)
    worksheet_examples: list[dict[str, Any]] = field(default_factory=list)
    ai_prompt_hints: dict[str, Any] = field(default_factory=dict)

    @property
    def model(self):
        return apps.get_model(self.model_label)

    def queryset(self) -> QuerySet:
        return self.model.objects.filter(**self.base_filters)


def _safe_percentage(numerator: Any, denominator: Any) -> float:
    if numerator is None or denominator in (None, 0, Decimal("0")):
        return 0.0
    return round((float(numerator) / float(denominator)) * 100, 2)


def _indicator_source_modules(indicator: Any) -> str:
    sources = getattr(indicator, "data_sources", None) or []
    return ", ".join(str(source) for source in sources if source) if isinstance(sources, list) else str(sources)


def _indicator_owner_label(row: Any) -> str:
    if getattr(row, "organization", None):
        return row.organization.name
    if getattr(row, "lga", None):
        return row.lga.name
    if getattr(row, "state", None):
        return row.state.name
    return "National"


def _indicator_baseline_value(row: Any) -> Any:
    indicator = getattr(row, "indicator", None)
    if indicator is None:
        return None
    scoped_values = indicator.values.all()
    state_id = getattr(row, "state_id", None)
    lga_id = getattr(row, "lga_id", None)
    organization_id = getattr(row, "organization_id", None)
    if state_id:
        scoped_values = scoped_values.filter(state_id=state_id)
    if lga_id:
        scoped_values = scoped_values.filter(lga_id=lga_id)
    if organization_id:
        scoped_values = scoped_values.filter(organization_id=organization_id)
    baseline = scoped_values.order_by("period_start", "created_at").first()
    return getattr(baseline, "calculated_value", None) if baseline else None


def performance_status(row: Any) -> str:
    target = getattr(row.indicator, "target_value", None)
    actual = getattr(row, "calculated_value", None)
    if target in (None, 0, Decimal("0")) or actual is None:
        return "no_target"
    achievement = _safe_percentage(actual, target)
    if achievement >= 100:
        return "on_track"
    if achievement >= 75:
        return "watch"
    return "critical"


def indicator_ai_prompt_hints(dataset_code: str) -> dict[str, Any]:
    return {
        "dataset_code": dataset_code,
        "analysis_rules": [
            "Use only returned indicator records, sample rows, or worksheet output as evidence.",
            "Do not infer or fabricate missing KPI values, targets, baselines, or approvals.",
            "When comparing performance, distinguish actual value from target value and achievement percentage.",
            "Respect account scope: federal can compare cross-state results, state can compare within state/LGA scope, employers and facilities stay within their own records.",
            "If approval or validation data is absent in the worksheet result, say that validation status is unavailable instead of guessing.",
        ],
        "recommended_widget_types": ["kpi_card", "trend_card", "bar_chart", "line_chart", "table"],
        "prompt_scaffold": (
            "Analyze the selected indicator dataset using only the provided rows. "
            "Summarize the latest actual value, target, achievement percentage, trend direction, "
            "and any meaningful state/LGA/owner differences supported by the data."
        ),
    }


DATASET_DEFINITIONS: list[DatasetDefinition] = [
    DatasetDefinition(
        code="food_handlers",
        name="Food Handlers",
        description="Registered food handlers with profile, category, status, and location details.",
        module_source="food_handlers",
        model_label="food_handlers.FoodHandlerProfile",
        allowed_account_types=["federal", "state", "employer"],
        allowed_roles=[UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.EMPLOYER, UserRole.SUPER_ADMIN],
        available_fields=[
            "system_identifier",
            "full_name",
            "gender",
            "date_of_birth",
            "nin",
            "phone",
            "email",
            "state__name",
            "lga__name",
            "employer__business_name",
            "business_branch__name",
            "food_handler_category",
            "current_status",
            "created_at",
        ],
        field_labels={
            "system_identifier": "Handler ID",
            "full_name": "Full name",
            "gender": "Gender",
            "date_of_birth": "Date of birth",
            "nin": "NIN",
            "phone": "Phone",
            "email": "Email",
            "state__name": "State",
            "lga__name": "LGA",
            "employer__business_name": "Employer",
            "business_branch__name": "Branch",
            "food_handler_category": "Category",
            "current_status": "Status",
            "created_at": "Registered at",
        },
        field_types={
            "system_identifier": "string",
            "full_name": "string",
            "gender": "enum",
            "date_of_birth": "date",
            "nin": "string",
            "phone": "string",
            "email": "string",
            "state__name": "string",
            "lga__name": "string",
            "employer__business_name": "string",
            "business_branch__name": "string",
            "food_handler_category": "enum",
            "current_status": "enum",
            "created_at": "datetime",
        },
        sensitive_fields=["nin", "phone", "email", "date_of_birth"],
        joinable_datasets=["employers", "certificates", "indicator_results", "indicator_performance"],
        aggregation_rules={"current_status": ["count"], "food_handler_category": ["count"], "created_at": ["count_by_month"]},
        required_permissions=["analytics.view"],
        state_scope_paths=["state_id"],
        employer_scope_paths=["employer__organization_id"],
    ),
    DatasetDefinition(
        code="certificates",
        name="Certificates",
        description="Food handler certificates with issuing state, facility, employer, status, and validity windows.",
        module_source="certificates",
        model_label="certificates.Certificate",
        allowed_account_types=["federal", "state", "employer", "medical_facility"],
        allowed_roles=[UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.EMPLOYER, UserRole.FACILITY_ADMIN, UserRole.SUPER_ADMIN],
        available_fields=[
            "certificate_number",
            "food_handler__full_name",
            "employer__business_name",
            "facility__facility_name",
            "issuing_state__name",
            "issue_date",
            "expiry_date",
            "status",
            "created_at",
        ],
        field_labels={
            "certificate_number": "Certificate number",
            "food_handler__full_name": "Food handler",
            "employer__business_name": "Employer",
            "facility__facility_name": "Medical facility",
            "issuing_state__name": "Issuing state",
            "issue_date": "Issue date",
            "expiry_date": "Expiry date",
            "status": "Status",
            "created_at": "Created at",
        },
        field_types={
            "certificate_number": "string",
            "food_handler__full_name": "string",
            "employer__business_name": "string",
            "facility__facility_name": "string",
            "issuing_state__name": "string",
            "issue_date": "date",
            "expiry_date": "date",
            "status": "enum",
            "created_at": "datetime",
        },
        joinable_datasets=["food_handlers", "employers", "medical_facilities", "indicator_results"],
        aggregation_rules={"status": ["count"], "issue_date": ["count_by_month"], "expiry_date": ["count_by_month"]},
        required_permissions=["analytics.view"],
        state_scope_paths=["issuing_state_id"],
        employer_scope_paths=["employer__organization_id"],
        facility_scope_paths=["facility__organization_id"],
    ),
    DatasetDefinition(
        code="employers",
        name="Employers",
        description="Registered food business employers with compliance, subscription, and establishment details.",
        module_source="employers",
        model_label="employers.Employer",
        allowed_account_types=["federal", "state", "employer"],
        allowed_roles=[UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.EMPLOYER, UserRole.SUPER_ADMIN],
        available_fields=[
            "business_name",
            "business_registration_number",
            "establishment_category",
            "contact_person_name",
            "contact_person_email",
            "state__name",
            "lga__name",
            "number_of_food_handlers",
            "compliance_status",
            "subscription_status",
            "is_active",
            "created_at",
        ],
        field_labels={
            "business_name": "Business name",
            "business_registration_number": "Registration number",
            "establishment_category": "Establishment category",
            "contact_person_name": "Contact person",
            "contact_person_email": "Contact email",
            "state__name": "State",
            "lga__name": "LGA",
            "number_of_food_handlers": "Food handlers",
            "compliance_status": "Compliance status",
            "subscription_status": "Subscription status",
            "is_active": "Active",
            "created_at": "Created at",
        },
        field_types={
            "business_name": "string",
            "business_registration_number": "string",
            "establishment_category": "enum",
            "contact_person_name": "string",
            "contact_person_email": "string",
            "state__name": "string",
            "lga__name": "string",
            "number_of_food_handlers": "integer",
            "compliance_status": "enum",
            "subscription_status": "enum",
            "is_active": "boolean",
            "created_at": "datetime",
        },
        sensitive_fields=["contact_person_email"],
        joinable_datasets=["food_handlers", "certificates", "inspections", "indicator_results", "indicator_performance"],
        aggregation_rules={"compliance_status": ["count"], "establishment_category": ["count"], "number_of_food_handlers": ["sum", "avg"]},
        required_permissions=["analytics.view"],
        state_scope_paths=["state_id"],
        employer_scope_paths=["organization_id"],
    ),
    DatasetDefinition(
        code="medical_facilities",
        name="Medical Facilities",
        description="Medical facility records covering accreditation, ownership, type, capacity, and geography.",
        module_source="facilities",
        model_label="facilities.MedicalFacility",
        allowed_account_types=["federal", "state", "medical_facility"],
        allowed_roles=[UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.FACILITY_ADMIN, UserRole.SUPER_ADMIN],
        available_fields=[
            "facility_name",
            "facility_type",
            "ownership_type",
            "license_number",
            "state__name",
            "lga__name",
            "service_capacity",
            "accreditation_status",
            "accreditation_start_date",
            "accreditation_expiry_date",
            "is_active",
            "created_at",
        ],
        field_labels={
            "facility_name": "Facility name",
            "facility_type": "Facility type",
            "ownership_type": "Ownership type",
            "license_number": "License number",
            "state__name": "State",
            "lga__name": "LGA",
            "service_capacity": "Service capacity",
            "accreditation_status": "Accreditation status",
            "accreditation_start_date": "Accreditation start",
            "accreditation_expiry_date": "Accreditation expiry",
            "is_active": "Active",
            "created_at": "Created at",
        },
        field_types={
            "facility_name": "string",
            "facility_type": "enum",
            "ownership_type": "enum",
            "license_number": "string",
            "state__name": "string",
            "lga__name": "string",
            "service_capacity": "integer",
            "accreditation_status": "enum",
            "accreditation_start_date": "date",
            "accreditation_expiry_date": "date",
            "is_active": "boolean",
            "created_at": "datetime",
        },
        sensitive_fields=["license_number"],
        joinable_datasets=["certificates", "indicator_results", "indicator_performance"],
        aggregation_rules={"facility_type": ["count"], "accreditation_status": ["count"], "service_capacity": ["sum", "avg"]},
        required_permissions=["analytics.view"],
        state_scope_paths=["state_id"],
        facility_scope_paths=["organization_id"],
    ),
    DatasetDefinition(
        code="inspections",
        name="Inspections",
        description="Inspection records covering employer visits, compliance scores, enforcement, and workflow status.",
        module_source="inspections",
        model_label="inspections.Inspection",
        allowed_account_types=["federal", "state", "employer"],
        allowed_roles=[UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.EMPLOYER, UserRole.INSPECTOR, UserRole.SUPER_ADMIN],
        available_fields=[
            "reference",
            "inspection_type",
            "priority",
            "employer__business_name",
            "branch__name",
            "inspection_date",
            "compliance_score",
            "enforcement_action",
            "status",
            "created_at",
        ],
        field_labels={
            "reference": "Inspection reference",
            "inspection_type": "Inspection type",
            "priority": "Priority",
            "employer__business_name": "Employer",
            "branch__name": "Branch",
            "inspection_date": "Inspection date",
            "compliance_score": "Compliance score",
            "enforcement_action": "Enforcement action",
            "status": "Status",
            "created_at": "Created at",
        },
        field_types={
            "reference": "string",
            "inspection_type": "enum",
            "priority": "enum",
            "employer__business_name": "string",
            "branch__name": "string",
            "inspection_date": "datetime",
            "compliance_score": "decimal",
            "enforcement_action": "enum",
            "status": "enum",
            "created_at": "datetime",
        },
        joinable_datasets=["employers", "indicator_results", "indicator_performance"],
        aggregation_rules={"status": ["count"], "priority": ["count"], "compliance_score": ["avg"]},
        required_permissions=["analytics.view"],
        state_scope_paths=["employer__state_id"],
        employer_scope_paths=["employer__organization_id"],
    ),
    DatasetDefinition(
        code="payment_transactions",
        name="Payment Transactions",
        description="Platform payment transactions for assessments and related financial events.",
        module_source="payments",
        model_label="payments.PaymentTransaction",
        allowed_account_types=["federal"],
        allowed_roles=[UserRole.FEDERAL_ADMIN, UserRole.SUPER_ADMIN],
        available_fields=[
            "payer_type",
            "related_entity_type",
            "amount",
            "currency",
            "payment_provider",
            "internal_reference",
            "status",
            "paid_at",
            "created_at",
        ],
        field_labels={
            "payer_type": "Payer type",
            "related_entity_type": "Related entity",
            "amount": "Amount",
            "currency": "Currency",
            "payment_provider": "Payment provider",
            "internal_reference": "Internal reference",
            "status": "Status",
            "paid_at": "Paid at",
            "created_at": "Created at",
        },
        field_types={
            "payer_type": "enum",
            "related_entity_type": "string",
            "amount": "decimal",
            "currency": "string",
            "payment_provider": "string",
            "internal_reference": "string",
            "status": "enum",
            "paid_at": "datetime",
            "created_at": "datetime",
        },
        sensitive_fields=["internal_reference"],
        joinable_datasets=["indicator_results", "indicator_performance"],
        aggregation_rules={"status": ["count"], "amount": ["sum", "avg"], "paid_at": ["sum_by_month"]},
        required_permissions=["analytics.finance"],
        privacy_level=DashboardPrivacyLevel.FINANCIAL,
        state_scope_paths=[],
    ),
    DatasetDefinition(
        code="indicators",
        name="Indicators",
        description="Indicator definitions including code, category, formula, frequency, thresholds, and source modules.",
        module_source="reports",
        model_label="reports.MEIndicator",
        allowed_account_types=["federal", "state", "employer", "medical_facility"],
        allowed_roles=[UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.EMPLOYER, UserRole.FACILITY_ADMIN, UserRole.SUPER_ADMIN],
        available_fields=[
            "code",
            "name",
            "category",
            "description",
            "formula",
            "reporting_frequency",
            "baseline_value",
            "target_value",
            "actual_value",
            "achievement_percentage",
            "performance_status",
            "warning_threshold",
            "critical_threshold",
            "visualization_type",
            "data_sources",
            "is_active",
        ],
        field_labels={
            "code": "Indicator code",
            "name": "Indicator name",
            "category": "Category",
            "description": "Description",
            "formula": "Formula",
            "reporting_frequency": "Reporting period",
            "baseline_value": "Baseline value",
            "target_value": "Target",
            "actual_value": "Latest actual value",
            "achievement_percentage": "Achievement %",
            "performance_status": "Performance status",
            "warning_threshold": "Warning threshold",
            "critical_threshold": "Critical threshold",
            "visualization_type": "Visualization",
            "data_sources": "Source modules",
            "is_active": "Active",
        },
        field_types={
            "code": "string",
            "name": "string",
            "category": "string",
            "description": "string",
            "formula": "string",
            "reporting_frequency": "enum",
            "baseline_value": "decimal",
            "target_value": "decimal",
            "actual_value": "decimal",
            "achievement_percentage": "decimal",
            "performance_status": "string",
            "warning_threshold": "decimal",
            "critical_threshold": "decimal",
            "visualization_type": "string",
            "data_sources": "json",
            "is_active": "boolean",
        },
        joinable_datasets=["indicator_targets", "indicator_results", "indicator_performance"],
        aggregation_rules={
            "category": ["count"],
            "reporting_frequency": ["count"],
            "calculation_metadata": {
                "formula_field": "formula",
                "target_field": "target_value",
                "actual_field": "latest_value",
                "source_modules_field": "data_sources",
            },
        },
        required_permissions=["analytics.view"],
        computed_fields={
            "baseline_value": lambda row: None,
            "actual_value": lambda row: getattr(row, "target_value", None),
            "achievement_percentage": lambda row: None,
            "performance_status": lambda row: "definition_only",
        },
        worksheet_examples=[
            {
                "key": "indicator_catalogue",
                "name": "Indicator Catalogue by Category",
                "description": "Browse active indicators grouped by category and reporting period.",
                "recommended_for": ["federal", "state"],
                "metrics": [{"field": "code", "aggregation": "count"}],
                "dimensions": [{"field": "category"}, {"field": "reporting_frequency"}],
                "filters": [{"field": "is_active", "operator": "eq", "value": True}],
                "chart_recommendation": "bar",
            }
        ],
        ai_prompt_hints=indicator_ai_prompt_hints("indicators"),
    ),
    DatasetDefinition(
        code="indicator_targets",
        name="Indicator Targets",
        description="Target-oriented view of indicators including baseline targets and threshold metadata.",
        module_source="reports",
        model_label="reports.MEIndicator",
        allowed_account_types=["federal", "state", "employer", "medical_facility"],
        allowed_roles=[UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.EMPLOYER, UserRole.FACILITY_ADMIN, UserRole.SUPER_ADMIN],
        available_fields=[
            "code",
            "name",
            "category",
            "reporting_frequency",
            "baseline_value",
            "target_value",
            "actual_value",
            "achievement_percentage",
            "performance_status",
            "warning_threshold",
            "critical_threshold",
            "is_active",
        ],
        field_labels={
            "code": "Indicator code",
            "name": "Indicator name",
            "category": "Category",
            "reporting_frequency": "Reporting period",
            "baseline_value": "Baseline value",
            "target_value": "Target value",
            "actual_value": "Latest actual value",
            "achievement_percentage": "Achievement %",
            "performance_status": "Performance status",
            "warning_threshold": "Warning threshold",
            "critical_threshold": "Critical threshold",
            "is_active": "Active",
        },
        field_types={
            "code": "string",
            "name": "string",
            "category": "string",
            "reporting_frequency": "enum",
            "baseline_value": "decimal",
            "target_value": "decimal",
            "actual_value": "decimal",
            "achievement_percentage": "decimal",
            "performance_status": "string",
            "warning_threshold": "decimal",
            "critical_threshold": "decimal",
            "is_active": "boolean",
        },
        joinable_datasets=["indicators", "indicator_results", "indicator_performance"],
        aggregation_rules={
            "category": ["count"],
            "target_value": ["avg"],
            "calculation_metadata": {"target_field": "target_value", "baseline_field": "baseline_value"},
        },
        required_permissions=["analytics.view"],
        computed_fields={
            "baseline_value": lambda row: None,
            "actual_value": lambda row: getattr(row, "target_value", None),
            "achievement_percentage": lambda row: None,
            "performance_status": lambda row: "target_definition",
        },
        worksheet_examples=[
            {
                "key": "targets_by_category",
                "name": "Target Coverage by Category",
                "description": "Compare configured indicator targets and thresholds by category.",
                "recommended_for": ["federal", "state"],
                "metrics": [{"field": "target_value", "aggregation": "avg"}],
                "dimensions": [{"field": "category"}],
                "filters": [{"field": "is_active", "operator": "eq", "value": True}],
                "chart_recommendation": "bar",
            }
        ],
        ai_prompt_hints=indicator_ai_prompt_hints("indicator_targets"),
    ),
    DatasetDefinition(
        code="indicator_results",
        name="Indicator Results",
        description="Indicator measurements by period, geography, and organization with numerator, denominator, and actual values.",
        module_source="reports",
        model_label="reports.MEIndicatorValue",
        allowed_account_types=["federal", "state", "employer", "medical_facility"],
        allowed_roles=[UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.EMPLOYER, UserRole.FACILITY_ADMIN, UserRole.SUPER_ADMIN],
        available_fields=[
            "indicator__code",
            "indicator__name",
            "indicator__category",
            "state__name",
            "lga__name",
            "organization__name",
            "owner_name",
            "period_start",
            "period_end",
            "baseline_value",
            "numerator_value",
            "denominator_value",
            "calculated_value",
            "actual_value",
            "indicator__target_value",
            "achievement_percentage",
            "performance_status",
            "source_module",
            "calculated_at",
        ],
        field_labels={
            "indicator__code": "Indicator code",
            "indicator__name": "Indicator name",
            "indicator__category": "Category",
            "state__name": "State",
            "lga__name": "LGA",
            "organization__name": "Organization",
            "owner_name": "Owner",
            "period_start": "Period start",
            "period_end": "Period end",
            "baseline_value": "Baseline value",
            "numerator_value": "Numerator",
            "denominator_value": "Denominator",
            "calculated_value": "Actual value",
            "actual_value": "Actual value",
            "indicator__target_value": "Target value",
            "achievement_percentage": "Achievement %",
            "performance_status": "Status",
            "source_module": "Source module",
            "calculated_at": "Calculated at",
        },
        field_types={
            "indicator__code": "string",
            "indicator__name": "string",
            "indicator__category": "string",
            "state__name": "string",
            "lga__name": "string",
            "organization__name": "string",
            "owner_name": "string",
            "period_start": "date",
            "period_end": "date",
            "baseline_value": "decimal",
            "numerator_value": "decimal",
            "denominator_value": "decimal",
            "calculated_value": "decimal",
            "actual_value": "decimal",
            "indicator__target_value": "decimal",
            "achievement_percentage": "decimal",
            "performance_status": "string",
            "source_module": "string",
            "calculated_at": "datetime",
        },
        joinable_datasets=["indicators", "indicator_targets", "food_handlers", "employers", "medical_facilities"],
        aggregation_rules={
            "calculated_value": ["avg", "min", "max"],
            "period_end": ["count_by_month"],
            "calculation_metadata": {
                "numerator_field": "numerator_value",
                "denominator_field": "denominator_value",
                "actual_field": "calculated_value",
                "target_field": "indicator__target_value",
                "approval_status": "not_available_in_legacy_results_model",
            },
        },
        required_permissions=["analytics.view"],
        state_scope_paths=["state_id"],
        employer_scope_paths=["organization_id"],
        facility_scope_paths=["organization_id"],
        computed_fields={
            "owner_name": _indicator_owner_label,
            "baseline_value": _indicator_baseline_value,
            "actual_value": lambda row: getattr(row, "calculated_value", None),
            "achievement_percentage": lambda row: _safe_percentage(getattr(row, "calculated_value", None), getattr(row.indicator, "target_value", None)),
            "performance_status": performance_status,
            "source_module": lambda row: _indicator_source_modules(row.indicator),
        },
        worksheet_examples=[
            {
                "key": "state_indicator_trend",
                "name": "Indicator Trend by State",
                "description": "Track approved indicator results over time across states or LGAs.",
                "recommended_for": ["federal", "state"],
                "metrics": [{"field": "actual_value", "aggregation": "avg"}],
                "dimensions": [{"field": "period_end"}, {"field": "state__name"}],
                "filters": [{"field": "indicator__category", "operator": "in", "value": ["certification", "inspection_enforcement"]}],
                "chart_recommendation": "line",
            },
            {
                "key": "organization_indicator_result",
                "name": "Organization Indicator Results",
                "description": "Review actual results for the current employer or facility by reporting period.",
                "recommended_for": ["employer", "medical_facility"],
                "metrics": [{"field": "actual_value", "aggregation": "avg"}],
                "dimensions": [{"field": "period_end"}, {"field": "indicator__name"}],
                "filters": [],
                "chart_recommendation": "table",
            },
        ],
        ai_prompt_hints=indicator_ai_prompt_hints("indicator_results"),
    ),
    DatasetDefinition(
        code="indicator_performance",
        name="Indicator Performance",
        description="Performance view of indicator results with achievement percentage, target, and status-derived fields.",
        module_source="reports",
        model_label="reports.MEIndicatorValue",
        allowed_account_types=["federal", "state", "employer", "medical_facility"],
        allowed_roles=[UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.EMPLOYER, UserRole.FACILITY_ADMIN, UserRole.SUPER_ADMIN],
        available_fields=[
            "indicator__code",
            "indicator__name",
            "indicator__category",
            "state__name",
            "lga__name",
            "organization__name",
            "owner_name",
            "period_end",
            "baseline_value",
            "calculated_value",
            "actual_value",
            "indicator__target_value",
            "achievement_percentage",
            "performance_status",
            "source_module",
        ],
        field_labels={
            "indicator__code": "Indicator code",
            "indicator__name": "Indicator name",
            "indicator__category": "Category",
            "state__name": "State",
            "lga__name": "LGA",
            "organization__name": "Organization",
            "owner_name": "Owner",
            "period_end": "Period end",
            "baseline_value": "Baseline value",
            "calculated_value": "Actual value",
            "actual_value": "Actual value",
            "indicator__target_value": "Target value",
            "achievement_percentage": "Achievement %",
            "performance_status": "Performance status",
            "source_module": "Source module",
        },
        field_types={
            "indicator__code": "string",
            "indicator__name": "string",
            "indicator__category": "string",
            "state__name": "string",
            "lga__name": "string",
            "organization__name": "string",
            "owner_name": "string",
            "period_end": "date",
            "baseline_value": "decimal",
            "calculated_value": "decimal",
            "actual_value": "decimal",
            "indicator__target_value": "decimal",
            "achievement_percentage": "decimal",
            "performance_status": "string",
            "source_module": "string",
        },
        joinable_datasets=["indicators", "indicator_targets", "indicator_results"],
        aggregation_rules={"achievement_percentage": ["avg", "min", "max"], "performance_status": ["count"]},
        required_permissions=["analytics.view"],
        state_scope_paths=["state_id"],
        employer_scope_paths=["organization_id"],
        facility_scope_paths=["organization_id"],
        computed_fields={
            "owner_name": _indicator_owner_label,
            "baseline_value": _indicator_baseline_value,
            "actual_value": lambda row: getattr(row, "calculated_value", None),
            "achievement_percentage": lambda row: _safe_percentage(row.calculated_value, getattr(row.indicator, "target_value", None)),
            "performance_status": lambda row: performance_status(row),
            "source_module": lambda row: _indicator_source_modules(row.indicator),
        },
        worksheet_examples=[
            {
                "key": "performance_heatmap",
                "name": "Indicator Performance Watchlist",
                "description": "Surface indicators below target by owner, state, or reporting period.",
                "recommended_for": ["federal", "state"],
                "metrics": [{"field": "achievement_percentage", "aggregation": "avg"}],
                "dimensions": [{"field": "owner_name"}, {"field": "indicator__name"}],
                "filters": [{"field": "performance_status", "operator": "in", "value": ["watch", "critical"]}],
                "chart_recommendation": "table",
            },
            {
                "key": "facility_performance_snapshot",
                "name": "Facility KPI Snapshot",
                "description": "Summarize current facility or employer KPI achievement against target.",
                "recommended_for": ["employer", "medical_facility"],
                "metrics": [{"field": "achievement_percentage", "aggregation": "avg"}],
                "dimensions": [{"field": "indicator__name"}],
                "filters": [],
                "chart_recommendation": "kpi_card",
            },
        ],
        ai_prompt_hints=indicator_ai_prompt_hints("indicator_performance"),
    ),
]


DATASET_DEFINITION_MAP = {definition.code: definition for definition in DATASET_DEFINITIONS}


def _slug_words(text: str) -> list[str]:
    return [part.strip().lower() for part in text.replace("/", " ").replace("-", " ").split() if part.strip()]


def resolve_dataset_from_prompt(prompt: str, account_type: str) -> tuple[DatasetDefinition | None, AnalyticsDataset | None, list[dict[str, Any]]]:
    prompt_words = set(_slug_words(prompt))
    sync_analytics_datasets()
    datasets = AnalyticsDataset.objects.filter(is_active=True, allowed_account_types__contains=[account_type]).order_by("name")

    if not datasets.exists():
        datasets = AnalyticsDataset.objects.filter(is_active=True).order_by("name")
    if not datasets.exists():
        return None, None, []

    scored: list[dict[str, Any]] = []
    for dataset in datasets:
        definition = DATASET_DEFINITION_MAP.get(dataset.code)
        if definition is None:
            continue
        score = 0
        name_words = set(_slug_words(dataset.name))
        desc_words = set(_slug_words(dataset.description or ""))
        label_words = set()
        for label in (dataset.field_labels or {}).values():
            label_words |= set(_slug_words(label))
        example_words = set()
        for example in definition.worksheet_examples:
            example_words |= set(_slug_words(example.get("name", "")))
            example_words |= set(_slug_words(example.get("description", "")))
        score += len(prompt_words & name_words) * 10
        score += len(prompt_words & desc_words) * 5
        score += len(prompt_words & label_words) * 3
        score += len(prompt_words & example_words) * 2
        reason_parts = []
        if score > 0:
            matched_name = prompt_words & name_words
            matched_desc = prompt_words & desc_words
            matched_label = prompt_words & label_words
            if matched_name:
                reason_parts.append(f"name matched: {', '.join(sorted(matched_name)[:3])}")
            if matched_desc:
                reason_parts.append(f"description matched: {', '.join(sorted(matched_desc)[:3])}")
            if matched_label:
                reason_parts.append(f"field labels matched: {', '.join(sorted(matched_label)[:3])}")
        scored.append({
            "dataset": dataset,
            "definition": definition,
            "score": score,
            "reason": "; ".join(reason_parts) if reason_parts else "default (no keyword match, first available dataset)",
        })

    scored.sort(key=lambda item: item["score"], reverse=True)
    best = scored[0]
    return best["definition"], best["dataset"], scored


def sync_analytics_datasets() -> tuple[int, int]:
    created = 0
    updated = 0
    for definition in DATASET_DEFINITIONS:
        _, was_created = AnalyticsDataset.objects.update_or_create(
            code=definition.code,
            defaults={
                "name": definition.name,
                "description": definition.description,
                "module_source": definition.module_source,
                "allowed_account_types": definition.allowed_account_types,
                "allowed_roles": definition.allowed_roles,
                "available_fields": definition.available_fields,
                "field_labels": definition.field_labels,
                "sensitive_fields": definition.sensitive_fields,
                "default_filters": definition.default_filters,
                "joinable_datasets": definition.joinable_datasets,
                "aggregation_rules": definition.aggregation_rules,
                "required_permissions": definition.required_permissions,
                "privacy_level": definition.privacy_level,
                "is_active": True,
            },
        )
        dataset = AnalyticsDataset.objects.get(code=definition.code)
        metadata = build_field_type_metadata(
            definition.field_types,
            existing_metadata=dataset.field_type_metadata,
            existing_active_types=dataset.field_types,
        )
        dataset.field_type_metadata = metadata
        dataset.field_types = active_field_types_from_metadata(metadata)
        dataset.save(update_fields=["field_type_metadata", "field_types", "updated_at"])
        if was_created:
            created += 1
        else:
            updated += 1
    return created, updated


def get_dataset_definition(code: str) -> DatasetDefinition | None:
    return DATASET_DEFINITION_MAP.get(code)


def get_dataset_worksheet_examples(definition: DatasetDefinition, account_type: str) -> list[dict[str, Any]]:
    if not definition.worksheet_examples:
        return []
    return [
        example
        for example in definition.worksheet_examples
        if not example.get("recommended_for") or account_type in example.get("recommended_for", [])
    ]


def get_dataset_allowed_fields(definition: DatasetDefinition) -> set[str]:
    return set(definition.available_fields) | set(definition.computed_fields.keys())


def _matches_filter(value: Any, operator: str, expected: Any) -> bool:
    if operator == "eq":
        return value == expected
    if operator == "neq":
        return value != expected
    if operator == "in":
        expected_values = expected if isinstance(expected, list) else [expected]
        return value in expected_values
    if operator == "contains":
        return str(expected).lower() in str(value or "").lower()
    if operator == "gt":
        return value is not None and expected is not None and value > expected
    if operator == "gte":
        return value is not None and expected is not None and value >= expected
    if operator == "lt":
        return value is not None and expected is not None and value < expected
    if operator == "lte":
        return value is not None and expected is not None and value <= expected
    return True


def _aggregate_metric(values: list[Any], aggregation: str) -> Any:
    if aggregation == "count":
        return len([value for value in values if value not in (None, "")])
    if aggregation == "count_distinct":
        return len({value for value in values if value not in (None, "")})
    numeric_values = [float(value) for value in values if isinstance(value, (int, float, Decimal))]
    if aggregation == "sum":
        return round(sum(numeric_values), 2)
    if aggregation == "avg":
        return round(sum(numeric_values) / len(numeric_values), 2) if numeric_values else 0
    if aggregation == "min":
        return min(numeric_values) if numeric_values else None
    if aggregation == "max":
        return max(numeric_values) if numeric_values else None
    if aggregation == "percentage":
        valid_values = [value for value in numeric_values if value is not None]
        return round(sum(valid_values) / len(valid_values), 2) if valid_values else 0
    if aggregation == "rate":
        valid_values = [value for value in numeric_values if value is not None]
        return round(sum(valid_values) / len(valid_values), 4) if valid_values else 0
    if aggregation == "ratio":
        valid_values = [value for value in numeric_values if value is not None]
        if len(valid_values) < 2:
            return round(valid_values[0], 4) if valid_values else 0
        denominator = valid_values[1]
        if denominator == 0:
            return 0
        return round(valid_values[0] / denominator, 4)
    if aggregation == "variance":
        if not numeric_values:
            return 0
        mean = sum(numeric_values) / len(numeric_values)
        return round(sum((value - mean) ** 2 for value in numeric_values) / len(numeric_values), 4)
    return len([value for value in values if value not in (None, "")])


def generate_worksheet_preview(
    definition: DatasetDefinition,
    user: Any,
    payload: dict[str, Any],
    row_limit: int = 12,
) -> dict[str, Any]:
    queryset = apply_dataset_scope(definition, definition.queryset(), user)
    rows = serialize_sample_rows(definition, queryset, limit=50)
    filters = payload.get("filters") or []
    metrics = payload.get("metrics") or []
    dimensions = payload.get("dimensions") or []
    chart_recommendation = payload.get("chart_recommendation") or "table"

    filtered_rows: list[dict[str, Any]] = []
    for row in rows:
        include = True
        for item in filters:
            field_name = item.get("field")
            if not field_name:
                continue
            include = include and _matches_filter(row.get(field_name), item.get("operator", "eq"), item.get("value"))
        if include:
            filtered_rows.append(row)

    dimension_fields = [item.get("field") for item in dimensions if item.get("field")]
    metric_cards = []
    for metric in metrics:
        field_name = metric.get("field")
        aggregation = metric.get("aggregation", "count")
        label = metric.get("label") or f"{aggregation} {field_name}"
        values = [row.get(field_name) for row in filtered_rows] if field_name else [1 for _ in filtered_rows]
        metric_cards.append(
            {
                "field": field_name,
                "aggregation": aggregation,
                "label": label,
                "value": _aggregate_metric(values, aggregation),
            }
        )

    grouped_rows: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    if dimension_fields:
        for row in filtered_rows:
            group_key = tuple(row.get(field_name) for field_name in dimension_fields)
            grouped_rows.setdefault(group_key, []).append(row)
    else:
        grouped_rows[(None,)] = filtered_rows

    preview_rows: list[dict[str, Any]] = []
    for group_key, grouped_items in list(grouped_rows.items())[:row_limit]:
        preview_row: dict[str, Any] = {}
        if dimension_fields:
            for index, field_name in enumerate(dimension_fields):
                preview_row[field_name] = group_key[index]
        for metric in metrics:
            field_name = metric.get("field")
            aggregation = metric.get("aggregation", "count")
            label = metric.get("label") or field_name or aggregation
            values = [item.get(field_name) for item in grouped_items] if field_name else [1 for _ in grouped_items]
            preview_row[field_name or label] = _aggregate_metric(values, aggregation)
        if not dimension_fields and not metrics and grouped_items:
            preview_row = {key: grouped_items[0].get(key) for key in list(grouped_items[0].keys())[:5]}
        preview_rows.append(preview_row)

    return {
        "dataset_code": definition.code,
        "chart_recommendation": chart_recommendation,
        "total_rows": len(filtered_rows),
        "dimensions": dimension_fields,
        "metrics": metric_cards,
        "rows": preview_rows,
    }


def apply_dataset_scope(definition: DatasetDefinition, queryset: QuerySet, user: Any) -> QuerySet:
    if user.role == UserRole.SUPER_ADMIN:
        return queryset
    if user.role == UserRole.FEDERAL_ADMIN:
        return queryset
    if user.role == UserRole.STATE_ADMIN and user.state_id and definition.state_scope_paths:
        query = Q()
        for path in definition.state_scope_paths:
            query |= Q(**{path: user.state_id})
        queryset = queryset.filter(query)
    if user.role == UserRole.EMPLOYER and user.organization_id and definition.employer_scope_paths:
        query = Q()
        for path in definition.employer_scope_paths:
            query |= Q(**{path: user.organization_id})
        queryset = queryset.filter(query)
    if user.role == UserRole.FACILITY_ADMIN and user.organization_id and definition.facility_scope_paths:
        query = Q()
        for path in definition.facility_scope_paths:
            query |= Q(**{path: user.organization_id})
        queryset = queryset.filter(query)
    return queryset


def resolve_field_value(instance: Any, field_name: str, computed_fields: dict[str, Any] | None = None) -> Any:
    if computed_fields and field_name in computed_fields:
        return computed_fields[field_name](instance)
    value = instance
    for part in field_name.split("__"):
        if value is None:
            return None
        value = getattr(value, part, None)
        if callable(value):
            value = value()
    return value


def serialize_sample_rows(definition: DatasetDefinition, queryset: QuerySet, limit: int = 5) -> list[dict[str, Any]]:
    rows = []
    for instance in queryset.order_by(*definition.sample_ordering)[:limit]:
        row = {}
        for field_name in definition.available_fields:
            value = resolve_field_value(instance, field_name, definition.computed_fields)
            if field_name in definition.sensitive_fields and value not in (None, ""):
                value = REDACTED_VALUE
            row[field_name] = value
        for computed_field in definition.computed_fields:
            if computed_field not in row:
                row[computed_field] = resolve_field_value(instance, computed_field, definition.computed_fields)
        rows.append(row)
    return rows
