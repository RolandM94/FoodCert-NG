from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.audit.models import AuditAction, AuditLog
from apps.certificates.models import (
    Certificate,
    CertificateStatus,
    CertificateTemplate as RuntimeCertificateTemplate,
    CertificateVerificationLog,
    VerificationResult,
)
from apps.employers.models import Employer, EstablishmentCategory
from apps.facilities.models import AccreditationStatus, FacilityType, MedicalFacility, OwnershipType
from apps.food_handlers.models import FoodHandlerProfile, FoodHandlerStatus, Gender
from apps.illness.models import ClearanceStatus, IllnessReport, SuspectedCondition
from apps.locations.models import LGA, State
from apps.organizations.models import Organization, OrganizationType
from apps.assessments.models import MedicalAssessment
from .models import (
    Approval,
    ApprovalStatus,
    CertificateTemplate,
    CertificateValidityRule,
    FacilityRequirementRule,
    FoodHandlerCategory,
    ImpactLevel,
    IndicatorDisaggregatedValue,
    IndicatorDisaggregation,
    IndicatorEvidence,
    MEIndicatorDataSource,
    MEIndicator,
    MEIndicatorCalculationLog,
    MEIndicatorValue,
    MEIndicatorValueHistory,
    MedicalTestRule,
    PolicyVersion,
    PolicyVersionStatus,
    PolicyVersionType,
    QualitativeIndicatorConfig,
    RiskLevel,
    ReportingFrequency,
    ReportingTemplate,
    ReturnToWorkRule,
    RuleType,
    StandardStatus,
    TemplateStatus,
    TestType,
)
from .indicator_calculations import IndicatorCalculationService
from .kpi_engine import FoodHandlersKpiCalculationService, KPIEngineError
from .services import (
    ActivePolicyRuleError,
    ActivePolicyRuleService,
    PolicyVersionService,
    bump_active_standards_cache_version,
)


User = get_user_model()


def payload(response):
    if isinstance(response.data, dict):
        return response.data.get("data", response.data)
    return response.data


class ActiveStandardsApiTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            "federal-standards",
            "federal-standards@example.com",
            "StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.client.force_authenticate(self.user)
        self.active_policy = PolicyVersion.objects.create(
            version_code="NG-FHS-2026-ACTIVE",
            title="Active national food handler standards",
            description="Active downstream policy.",
            version_type=PolicyVersionType.MAJOR,
            status=PolicyVersionStatus.ACTIVE,
            change_summary="Active policy for downstream modules.",
            created_by=self.user,
        )
        self.draft_policy = PolicyVersion.objects.create(
            version_code="NG-FHS-2026-DRAFT",
            title="Draft national food handler standards",
            description="Draft downstream policy.",
            version_type=PolicyVersionType.MINOR,
            status=PolicyVersionStatus.DRAFT,
            change_summary="Draft policy must not leak downstream.",
            created_by=self.user,
        )
        self.active_category = FoodHandlerCategory.objects.create(
            policy_version=self.active_policy,
            name="Restaurant Handler",
            code="REST_HANDLER",
            description="Active category.",
            risk_level=RiskLevel.HIGH,
            status=StandardStatus.ACTIVE,
            created_by=self.user,
        )
        FoodHandlerCategory.objects.create(
            policy_version=self.active_policy,
            name="Inactive Handler",
            code="INACTIVE_HANDLER",
            description="Inactive category.",
            risk_level=RiskLevel.LOW,
            status=StandardStatus.DRAFT,
            created_by=self.user,
        )
        FoodHandlerCategory.objects.create(
            policy_version=self.draft_policy,
            name="Draft Policy Handler",
            code="DRAFT_POLICY_HANDLER",
            description="Draft policy category.",
            risk_level=RiskLevel.MEDIUM,
            status=StandardStatus.ACTIVE,
            created_by=self.user,
        )

    def test_active_handler_categories_return_only_active_policy_active_rules(self):
        response = self.client.get("/api/standards/active/handler-categories/")

        self.assertEqual(response.status_code, 200)
        rows = payload(response)
        self.assertEqual([row["code"] for row in rows], ["REST_HANDLER"])

    def test_active_policy_endpoint_returns_only_active_policy(self):
        response = self.client.get("/api/standards/active/")

        self.assertEqual(response.status_code, 200)
        data = payload(response)
        self.assertEqual(data["version_code"], "NG-FHS-2026-ACTIVE")

    def test_active_standards_cache_refreshes_when_version_is_bumped(self):
        first = self.client.get("/api/standards/active/handler-categories/")
        self.assertEqual(payload(first)[0]["name"], "Restaurant Handler")

        self.active_category.name = "Updated Restaurant Handler"
        self.active_category.save(update_fields=["name", "updated_at"])

        cached = self.client.get("/api/standards/active/handler-categories/")
        self.assertEqual(payload(cached)[0]["name"], "Restaurant Handler")

        bump_active_standards_cache_version()
        refreshed = self.client.get("/api/standards/active/handler-categories/")
        self.assertEqual(payload(refreshed)[0]["name"], "Updated Restaurant Handler")


class MEIndicatorValueWorkflowTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            "federal-indicator-values",
            "federal-indicator-values@example.com",
            "StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.client.force_authenticate(self.user)
        self.policy = PolicyVersion.objects.create(
            version_code="NG-FHS-2026-ME",
            title="M&E policy",
            description="Policy for indicator value tests.",
            version_type=PolicyVersionType.MINOR,
            change_summary="Testing indicator values.",
            created_by=self.user,
        )
        self.indicator = MEIndicator.objects.create(
            policy_version=self.policy,
            indicator_name="Certified food handlers",
            indicator_code="CERT_HANDLERS",
            description="Certified food handlers by period.",
            formula_config={
                "record_input_mode": "progress_only",
                "progress_relationship": "dependent",
            },
            data_source="manual",
            reporting_frequency=ReportingFrequency.QUARTERLY,
            visualization_type="line",
            created_by=self.user,
        )

    def create_value(self):
        response = self.client.post(
            f"/api/federal/standards/me-indicators/{self.indicator.id}/values/",
            {
                "period_start": "2026-04-01",
                "period_end": "2026-06-30",
                "progress_value_numeric": "12",
                "cumulative_value_numeric": "32",
                "notes": "Q2 manual entry.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        return response

    def test_indicator_value_can_be_created_and_listed(self):
        created = self.create_value()

        listed = self.client.get(f"/api/federal/standards/me-indicators/{self.indicator.id}/values/")

        self.assertEqual(listed.status_code, 200)
        self.assertEqual(payload(created)["approval_status"], "draft")
        self.assertEqual(payload(listed)[0]["indicator_code"], "CERT_HANDLERS")
        self.assertTrue(MEIndicatorValueHistory.objects.filter(action="created").exists())

    def test_indicator_value_submit_and_approve_workflow(self):
        value_id = payload(self.create_value())["id"]

        submitted = self.client.post(f"/api/federal/standards/indicator-values/{value_id}/submit/")
        approved = self.client.post(f"/api/federal/standards/indicator-values/{value_id}/approve/", {"comment": "Looks good."}, format="json")

        self.assertEqual(submitted.status_code, 200)
        self.assertEqual(payload(submitted)["approval_status"], "submitted")
        self.assertEqual(approved.status_code, 200)
        self.assertEqual(payload(approved)["approval_status"], "approved")
        self.assertTrue(MEIndicatorValue.objects.filter(id=value_id, approved_by=self.user).exists())
        self.assertTrue(MEIndicatorValueHistory.objects.filter(value_id=value_id, action="approved").exists())

    def test_rejection_requires_comment_and_revision_returns_to_draft(self):
        value_id = payload(self.create_value())["id"]
        self.client.post(f"/api/federal/standards/indicator-values/{value_id}/submit/")

        missing_comment = self.client.post(f"/api/federal/standards/indicator-values/{value_id}/reject/", {}, format="json")
        rejected = self.client.post(f"/api/federal/standards/indicator-values/{value_id}/reject/", {"comment": "Needs evidence."}, format="json")
        revised = self.client.patch(
            f"/api/federal/standards/indicator-values/{value_id}/",
            {"notes": "Evidence added.", "evidence_json": [{"label": "State report", "url": "https://example.test/report.pdf"}]},
            format="json",
        )

        self.assertEqual(missing_comment.status_code, 400)
        self.assertEqual(rejected.status_code, 200)
        self.assertEqual(payload(rejected)["approval_status"], "rejected")
        self.assertEqual(revised.status_code, 200)
        self.assertEqual(payload(revised)["approval_status"], "draft")
        self.assertEqual(payload(revised)["rejection_comment"], "")


class MEIndicatorCalculationEngineTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            "federal-indicator-calcs",
            "federal-indicator-calcs@example.com",
            "StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.client.force_authenticate(self.user)
        self.policy = PolicyVersion.objects.create(
            version_code="NG-FHS-2026-CALC",
            title="M&E calculation policy",
            description="Policy for indicator calculation tests.",
            version_type=PolicyVersionType.MINOR,
            change_summary="Testing indicator calculations.",
            created_by=self.user,
        )
        self.indicator = MEIndicator.objects.create(
            policy_version=self.policy,
            indicator_name="Training completion",
            indicator_code="TRAINING_COMPLETION",
            description="Training completion indicator.",
            formula_config={},
            data_source="manual",
            reporting_frequency=ReportingFrequency.QUARTERLY,
            visualization_type="line",
            created_by=self.user,
        )
        self.records = [
            {"state": "Lagos", "person_id": "A", "completed": 1, "eligible": 2, "score": 80, "date": "2026-04-10"},
            {"state": "Lagos", "person_id": "A", "completed": 1, "eligible": 2, "score": 70, "date": "2026-04-12"},
            {"state": "Lagos", "person_id": "B", "completed": 2, "eligible": 4, "score": 90, "date": "2026-05-01"},
            {"state": "Oyo", "person_id": "C", "completed": 3, "eligible": 6, "score": 60, "date": "2026-05-03"},
        ]

    def source(self, method, **kwargs):
        return MEIndicatorDataSource(
            indicator=self.indicator,
            source_type="medical_test_records",
            calculation_method=method,
            value_field_id=kwargs.get("value_field_id", "completed"),
            numerator_config_json=kwargs.get("numerator_config_json", {}),
            denominator_config_json=kwargs.get("denominator_config_json", {}),
            filter_config_json=kwargs.get("filter_config_json", {"filters": [{"field": "state", "operator": "eq", "value": "Lagos"}]}),
            unicity_field_id=kwargs.get("unicity_field_id", ""),
            period_filter_mode=kwargs.get("period_filter_mode", "current_period"),
        )

    def test_calculation_service_sum_count_unique_average_percentage(self):
        period = {"period_start": "2026-04-01", "period_end": "2026-06-30"}

        total = IndicatorCalculationService.calculate(self.source("sum"), self.records, period)
        count = IndicatorCalculationService.calculate(self.source("count"), self.records, period)
        unique = IndicatorCalculationService.calculate(self.source("unique_count", unicity_field_id="person_id"), self.records, period)
        average = IndicatorCalculationService.calculate(self.source("average", value_field_id="score"), self.records, period)
        percentage = IndicatorCalculationService.calculate(self.source(
            "percentage",
            numerator_config_json={"calculation_method": "sum", "value_field_id": "completed"},
            denominator_config_json={"calculation_method": "sum", "value_field_id": "eligible"},
        ), self.records, period)

        self.assertEqual(str(total["value"]), "4")
        self.assertEqual(str(count["value"]), "3")
        self.assertEqual(str(unique["value"]), "2")
        self.assertEqual(str(average["value"]), "80")
        self.assertEqual(str(percentage["value"]), "50.0")

    def test_calculation_endpoint_stores_snapshot_value(self):
        source = MEIndicatorDataSource.objects.create(
            indicator=self.indicator,
            source_type="medical_test_records",
            source_id="training-form",
            calculation_method="sum",
            value_field_id="completed",
            filter_config_json={
                "date_field_id": "date",
                "filters": [{"field": "state", "operator": "eq", "value": "Lagos"}],
                "mock_records": self.records,
            },
            period_filter_mode="current_period",
        )

        response = self.client.post(
            f"/api/federal/standards/me-indicators/{self.indicator.id}/calculate/",
            {
                "data_source_id": str(source.id),
                "period_start": "2026-04-01",
                "period_end": "2026-06-30",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        data = payload(response)
        self.assertEqual(data["progress_value_numeric"], "4.0000")
        self.assertEqual(data["calculation_snapshot_json"]["calculation_method"], "sum")
        self.assertEqual(data["calculation_snapshot_json"]["record_count"], 3)
        self.assertTrue(MEIndicatorValue.objects.filter(indicator=self.indicator, source_reference_id=str(source.id)).exists())

    def test_calculation_endpoint_stores_disaggregated_values(self):
        source = MEIndicatorDataSource.objects.create(
            indicator=self.indicator,
            source_type="medical_test_records",
            source_id="training-form",
            calculation_method="sum",
            value_field_id="completed",
            filter_config_json={
                "date_field_id": "date",
                "filters": [{"field": "state", "operator": "eq", "value": "Lagos"}],
                "mock_records": [
                    {"state": "Lagos", "gender": "Female", "region": "North", "completed": 2, "date": "2026-04-10"},
                    {"state": "Lagos", "gender": "Female", "region": "South", "completed": 3, "date": "2026-04-12"},
                    {"state": "Lagos", "gender": "Male", "region": "North", "completed": 5, "date": "2026-05-01"},
                    {"state": "Oyo", "gender": "Female", "region": "North", "completed": 99, "date": "2026-05-03"},
                ],
            },
            period_filter_mode="current_period",
        )
        IndicatorDisaggregation.objects.create(
            indicator=self.indicator,
            source_type="medical_test_records",
            field_id="gender",
            field_label="Gender",
            level=1,
        )
        IndicatorDisaggregation.objects.create(
            indicator=self.indicator,
            source_type="medical_test_records",
            field_id="region",
            field_label="Region",
            level=2,
        )

        response = self.client.post(
            f"/api/federal/standards/me-indicators/{self.indicator.id}/calculate/",
            {
                "data_source_id": str(source.id),
                "period_start": "2026-04-01",
                "period_end": "2026-06-30",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        data = payload(response)
        self.assertEqual(data["progress_value_numeric"], "10.0000")
        self.assertEqual(data["calculation_snapshot_json"]["disaggregation_count"], 3)
        rows = {
            (row.dimension_values_json["Gender"], row.dimension_values_json["Region"]): str(row.value_numeric)
            for row in IndicatorDisaggregatedValue.objects.filter(indicator=self.indicator)
        }
        self.assertEqual(rows[("Female", "North")], "2.0000")
        self.assertEqual(rows[("Female", "South")], "3.0000")
        self.assertEqual(rows[("Male", "North")], "5.0000")

    def test_indicator_disaggregation_configuration_endpoint(self):
        response = self.client.post(
            f"/api/federal/standards/me-indicators/{self.indicator.id}/disaggregations/",
            {
                "source_type": "medical_test_records",
                "field_id": "state",
                "field_label": "State",
                "level": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(payload(response)["field_label"], "State")
        self.assertTrue(IndicatorDisaggregation.objects.filter(indicator=self.indicator, field_id="state").exists())

    def test_form_sources_are_not_official_kpi_sources(self):
        response = self.client.post(
            f"/api/federal/standards/me-indicators/{self.indicator.id}/data-sources/forms/",
            {
                "form_template_id": "00000000-0000-0000-0000-000000000000",
                "calculation_method": "sum",
                "value_field_id": "completed",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 410)
        self.assertIn("not official Food Handlers KPI data sources", payload(response)["detail"])

    def create_source_indicator(self, name, code):
        return MEIndicator.objects.create(
            policy_version=self.policy,
            indicator_name=name,
            indicator_code=code,
            description=f"{name} source indicator.",
            formula_config={},
            data_source="manual",
            reporting_frequency=ReportingFrequency.QUARTERLY,
            visualization_type="line",
            created_by=self.user,
        )

    def create_indicator_value(self, indicator, value, status="approved"):
        return MEIndicatorValue.objects.create(
            indicator=indicator,
            period_start="2026-04-01",
            period_end="2026-06-30",
            progress_value_numeric=value,
            cumulative_value_numeric=value,
            value_source="manual",
            source_reference_id=f"{indicator.indicator_code}-{value}-{status}",
            approval_status=status,
            created_by=self.user,
        )

    def test_indicator_can_link_to_indicators_and_sum_approved_values(self):
        source_a = self.create_source_indicator("Inspections completed", "INSPECTIONS_COMPLETED")
        source_b = self.create_source_indicator("Audits completed", "AUDITS_COMPLETED")
        self.create_indicator_value(source_a, 8)
        self.create_indicator_value(source_b, 4)
        self.create_indicator_value(source_b, 99, status="draft")

        linked = self.client.post(
            f"/api/federal/standards/me-indicators/{self.indicator.id}/data-sources/indicators/",
            {
                "source_kpi_ids": [str(source_a.id), str(source_b.id)],
                "calculation_method": "sum",
                "period_filter_mode": "current_period",
            },
            format="json",
        )
        calculated = self.client.post(
            f"/api/federal/standards/me-indicators/{self.indicator.id}/calculate/",
            {
                "data_source_id": payload(linked)["id"],
                "period_start": "2026-04-01",
                "period_end": "2026-06-30",
            },
            format="json",
        )

        self.assertEqual(linked.status_code, 201, linked.data)
        self.assertEqual(calculated.status_code, 201, calculated.data)
        self.assertEqual(payload(calculated)["progress_value_numeric"], "12.0000")
        self.assertEqual(payload(calculated)["calculation_snapshot_json"]["source_type"], "kpi")
        self.assertEqual(payload(calculated)["calculation_snapshot_json"]["record_count"], 2)

    def test_indicator_source_average_uses_selected_approved_indicators(self):
        source_a = self.create_source_indicator("High risk facilities", "HIGH_RISK_FACILITIES")
        source_b = self.create_source_indicator("Medium risk facilities", "MEDIUM_RISK_FACILITIES")
        self.create_indicator_value(source_a, 10)
        self.create_indicator_value(source_b, 20)

        linked = self.client.post(
            f"/api/federal/standards/me-indicators/{self.indicator.id}/data-sources/indicators/",
            {
                "source_kpi_ids": [str(source_a.id), str(source_b.id)],
                "calculation_method": "average",
                "period_filter_mode": "current_period",
            },
            format="json",
        )
        calculated = self.client.post(
            f"/api/federal/standards/me-indicators/{self.indicator.id}/calculate/",
            {
                "data_source_id": payload(linked)["id"],
                "period_start": "2026-04-01",
                "period_end": "2026-06-30",
            },
            format="json",
        )

        self.assertEqual(linked.status_code, 201, linked.data)
        self.assertEqual(payload(calculated)["progress_value_numeric"], "15.0000")

    def test_kpi_dashboard_summary_returns_cards_rankings_and_alerts(self):
        self.indicator.status = StandardStatus.ACTIVE
        self.indicator.target_value = 10
        self.indicator.input_mode = "automatic"
        self.indicator.data_source = "medical_test_records"
        self.indicator.save(update_fields=["status", "target_value", "input_mode", "data_source", "updated_at"])
        self.create_indicator_value(self.indicator, 4)
        due_indicator = self.create_source_indicator("Certificates expiring", "CERTIFICATES_EXPIRING")
        due_indicator.status = StandardStatus.ACTIVE
        due_indicator.save(update_fields=["status", "updated_at"])

        response = self.client.get("/api/federal/standards/me-indicators/dashboard-summary/")

        self.assertEqual(response.status_code, 200, response.data)
        data = payload(response)
        self.assertEqual(data["summary_cards"][0]["key"], "total")
        self.assertGreaterEqual(data["status_breakdown"]["active"], 2)
        self.assertEqual(data["input_mode_breakdown"]["automatic"], 1)
        self.assertTrue(any(row["code"] == "TRAINING_COMPLETION" and row["achievement"] == 40.0 for row in data["rankings"]))
        self.assertTrue(any(alert["indicator_id"] == str(due_indicator.id) for alert in data["alerts"]))

    def test_indicator_source_blocks_self_link_and_circular_dependencies(self):
        source_a = self.create_source_indicator("State submissions", "STATE_SUBMISSIONS")
        direct_self = self.client.post(
            f"/api/federal/standards/me-indicators/{self.indicator.id}/data-sources/indicators/",
            {
                "source_kpi_ids": [str(self.indicator.id)],
                "calculation_method": "sum",
            },
            format="json",
        )
        first_link = self.client.post(
            f"/api/federal/standards/me-indicators/{source_a.id}/data-sources/indicators/",
            {
                "source_kpi_ids": [str(self.indicator.id)],
                "calculation_method": "sum",
            },
            format="json",
        )
        circular = self.client.post(
            f"/api/federal/standards/me-indicators/{self.indicator.id}/data-sources/indicators/",
            {
                "source_kpi_ids": [str(source_a.id)],
                "calculation_method": "sum",
            },
            format="json",
        )

        self.assertEqual(direct_self.status_code, 400)
        self.assertIn("itself", payload(direct_self)["detail"])
        self.assertEqual(first_link.status_code, 201, first_link.data)
        self.assertEqual(circular.status_code, 400)
        self.assertIn("Circular", payload(circular)["detail"])

    def test_qualitative_indicator_config_is_saved_with_indicator(self):
        response = self.client.post(
            "/api/federal/standards/me-indicators/",
            {
                "policy_version": str(self.policy.id),
                "indicator_name": "Stakeholder confidence",
                "indicator_code": "STAKEHOLDER_CONFIDENCE",
                "description": "Qualitative confidence indicator.",
                "formula_config": {"indicator_type": "qualitative"},
                "data_source": "manual",
                "reporting_frequency": "quarterly",
                "visualization_type": "line",
                "mandatory": True,
                "qualitative_config": {
                    "input_type": "rubric",
                    "scale_min": 1,
                    "scale_max": 5,
                    "scale_labels_json": {"1": "Low", "5": "High"},
                    "category_options_json": ["Poor", "Fair", "Good"],
                    "requires_narrative": True,
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        data = payload(response)
        self.assertEqual(data["qualitative_config"]["input_type"], "rubric")
        self.assertTrue(QualitativeIndicatorConfig.objects.filter(indicator_id=data["id"]).exists())

    def test_kpi_calculation_metadata_fields_are_saved_with_indicator(self):
        response = self.client.post(
            "/api/federal/standards/me-indicators/",
            {
                "policy_version": str(self.policy.id),
                "indicator_name": "Expired Certificate Rate",
                "indicator_code": "ME-EXPIRED-RATE",
                "description": "Automatically calculated from certificate records.",
                "kpi_type": "quantitative",
                "unit_of_measurement": "Percentage",
                "input_mode": "automatic",
                "record_input_type": "progress_only",
                "progress_cumulative_relationship": "dependent",
                "target_direction": "lower_better",
                "calculation_type": "percentage",
                "calculation_source": "certificates",
                "numerator_definition": {"status": "expired"},
                "denominator_definition": {"status": "issued"},
                "policy_standard_code": "FH-VALIDITY-2024-001",
                "rule_parameter_key": "certificate_validity_months",
                "allow_manual_override": False,
                "override_requires_reason": False,
                "visibility_scope": {"scope_type": "federal_and_state"},
                "formula_config": {"calculation_method": "percentage"},
                "data_source": "certificate_records",
                "reporting_frequency": "monthly",
                "visualization_type": "line",
                "mandatory": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        data = payload(response)
        self.assertEqual(data["input_mode"], "automatic")
        self.assertEqual(data["calculation_type"], "percentage")
        self.assertEqual(data["calculation_source"], "certificates")
        self.assertEqual(data["policy_standard_code"], "FH-VALIDITY-2024-001")
        self.assertEqual(data["rule_parameter_key"], "certificate_validity_months")
        self.assertEqual(data["numerator_definition"], {"status": "expired"})
        self.assertEqual(data["denominator_definition"], {"status": "issued"})

    def test_builder_style_automatic_kpi_payload_persists_engine_contract_fields(self):
        response = self.client.post(
            "/api/federal/standards/me-indicators/",
            {
                "policy_version": str(self.policy.id),
                "indicator_name": "Facility Accreditation Compliance",
                "indicator_code": "ME-FACILITY-ACCRED",
                "description": "Tracks compliant accredited facilities.",
                "kpi_type": "quantitative",
                "unit_of_measurement": "Percentage",
                "input_mode": "automatic",
                "record_input_type": "progress_only",
                "progress_cumulative_relationship": "dependent",
                "target_direction": "higher_better",
                "calculation_type": "percentage",
                "calculation_source": "medical_facilities",
                "policy_standard_code": "FH-FAC-2024-001",
                "rule_parameter_key": "reaccreditation_interval_months",
                "visibility_scope": {"scope_type": "federal_and_state"},
                "formula_config": {
                    "indicator_type": "quantitative",
                    "calculation_type": "percentage",
                    "calculation_method": "percentage",
                    "calculation_source": "medical_facilities",
                    "policy_standard_code": "FH-FAC-2024-001",
                    "rule_parameter_key": "reaccreditation_interval_months",
                    "numerator_definition": {"status": "approved"},
                    "denominator_definition": {"status": "all"},
                    "link_data_source": True,
                },
                "numerator_definition": {"status": "approved"},
                "denominator_definition": {"status": "all"},
                "data_source": "facility_records",
                "reporting_frequency": "quarterly",
                "visualization_type": "line",
                "mandatory": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        data = payload(response)
        self.assertEqual(data["input_mode"], "automatic")
        self.assertEqual(data["calculation_source"], "medical_facilities")
        self.assertEqual(data["policy_standard_code"], "FH-FAC-2024-001")
        self.assertEqual(data["rule_parameter_key"], "reaccreditation_interval_months")
        self.assertEqual(data["formula_config"]["calculation_source"], "medical_facilities")
        self.assertEqual(data["formula_config"]["policy_standard_code"], "FH-FAC-2024-001")
        self.assertEqual(data["formula_config"]["rule_parameter_key"], "reaccreditation_interval_months")

    def test_hybrid_kpi_requires_manual_override_and_reason_when_builder_payload_sets_it(self):
        response = self.client.post(
            "/api/federal/standards/me-indicators/",
            {
                "policy_version": str(self.policy.id),
                "indicator_name": "Return To Work Clearance Rate",
                "indicator_code": "ME-RTW-RATE",
                "description": "Tracks timely illness clearance completion.",
                "kpi_type": "quantitative",
                "unit_of_measurement": "Percentage",
                "input_mode": "hybrid",
                "record_input_type": "progress_only",
                "progress_cumulative_relationship": "dependent",
                "target_direction": "higher_better",
                "calculation_type": "percentage",
                "calculation_source": "return_to_work_clearances",
                "policy_standard_code": "FH-RTW-2024-001",
                "rule_parameter_key": "standard_exclusion_period_hours_after_symptoms_stop",
                "allow_manual_override": True,
                "override_requires_reason": True,
                "visibility_scope": {"scope_type": "federal_and_state"},
                "formula_config": {
                    "indicator_type": "quantitative",
                    "calculation_type": "percentage",
                    "calculation_method": "percentage",
                    "calculation_source": "return_to_work_clearances",
                    "policy_standard_code": "FH-RTW-2024-001",
                    "rule_parameter_key": "standard_exclusion_period_hours_after_symptoms_stop",
                    "allow_manual_override": True,
                    "override_requires_reason": True,
                    "numerator_definition": {"status": "cleared"},
                    "denominator_definition": {"status": "required"},
                    "link_data_source": True,
                },
                "numerator_definition": {"status": "cleared"},
                "denominator_definition": {"status": "required"},
                "data_source": "medical_test_records",
                "reporting_frequency": "quarterly",
                "visualization_type": "line",
                "mandatory": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        data = payload(response)
        self.assertTrue(data["allow_manual_override"])
        self.assertTrue(data["override_requires_reason"])
        self.assertEqual(data["calculation_source"], "return_to_work_clearances")
        self.assertEqual(data["formula_config"]["override_requires_reason"], True)
    def test_qualitative_value_preserves_category_rating_and_narrative(self):
        qualitative_indicator = MEIndicator.objects.create(
            policy_version=self.policy,
            indicator_name="Public awareness quality",
            indicator_code="PUBLIC_AWARENESS_QUALITY",
            description="Qualitative public awareness indicator.",
            formula_config={"indicator_type": "qualitative"},
            data_source="manual",
            reporting_frequency=ReportingFrequency.QUARTERLY,
            visualization_type="line",
            created_by=self.user,
        )
        QualitativeIndicatorConfig.objects.create(
            indicator=qualitative_indicator,
            input_type="rubric",
            scale_min=1,
            scale_max=5,
            scale_labels_json={"1": "Weak", "5": "Excellent"},
            category_options_json=["Weak", "Moderate", "Strong"],
            requires_narrative=True,
        )

        invalid = self.client.post(
            f"/api/federal/standards/me-indicators/{qualitative_indicator.id}/values/",
            {
                "period_start": "2026-04-01",
                "period_end": "2026-06-30",
                "qualitative_rating": "6",
                "qualitative_category": "Strong",
                "qualitative_value_text": "Strong awareness in pilot states.",
                "value_source": "manual",
            },
            format="json",
        )
        valid = self.client.post(
            f"/api/federal/standards/me-indicators/{qualitative_indicator.id}/values/",
            {
                "period_start": "2026-04-01",
                "period_end": "2026-06-30",
                "qualitative_rating": "5",
                "qualitative_category": "Strong",
                "qualitative_value_text": "Strong awareness in pilot states.",
                "value_source": "manual",
            },
            format="json",
        )

        self.assertEqual(invalid.status_code, 400)
        self.assertIn("above", str(payload(invalid)))
        self.assertEqual(valid.status_code, 201, valid.data)
        data = payload(valid)
        self.assertEqual(data["qualitative_category"], "Strong")
        self.assertEqual(data["qualitative_rating"], "5.00")
        self.assertEqual(data["qualitative_value_text"], "Strong awareness in pilot states.")

    def test_indicator_value_evidence_workflow(self):
        value = MEIndicatorValue.objects.create(
            indicator=self.indicator,
            period_start="2026-04-01",
            period_end="2026-06-30",
            progress_value_numeric=12,
            cumulative_value_numeric=12,
            value_source="manual",
            source_reference_id="manual-evidence",
            created_by=self.user,
        )

        created = self.client.post(
            f"/api/federal/standards/indicator-values/{value.id}/evidence/",
            {
                "title": "State M&E report",
                "description": "Signed state reporting packet.",
                "evidence_type": "text",
            },
            format="json",
        )
        evidence_id = payload(created)["id"]
        submitted = self.client.post(f"/api/federal/standards/indicator-evidence/{evidence_id}/submit/", {}, format="json")
        approved = self.client.post(f"/api/federal/standards/indicator-evidence/{evidence_id}/approve/", {}, format="json")
        official = self.client.get(
            f"/api/federal/standards/indicator-values/{value.id}/evidence/",
            {"approval_status": "approved"},
        )

        self.assertEqual(created.status_code, 201, created.data)
        self.assertEqual(payload(created)["approval_status"], "draft")
        self.assertEqual(submitted.status_code, 200, submitted.data)
        self.assertEqual(payload(submitted)["approval_status"], "submitted")
        self.assertEqual(approved.status_code, 200, approved.data)
        self.assertEqual(payload(approved)["approval_status"], "approved")
        self.assertEqual(len(payload(official)), 1)
        self.assertTrue(IndicatorEvidence.objects.filter(id=evidence_id, approved_by=self.user).exists())

    def test_indicator_evidence_rejection_requires_comment(self):
        value = MEIndicatorValue.objects.create(
            indicator=self.indicator,
            period_start="2026-07-01",
            period_end="2026-09-30",
            progress_value_numeric=3,
            cumulative_value_numeric=3,
            value_source="manual",
            source_reference_id="manual-evidence-reject",
            created_by=self.user,
        )
        evidence = IndicatorEvidence.objects.create(
            indicator=self.indicator,
            indicator_value=value,
            title="Uploaded spreadsheet",
            description="Needs review.",
            evidence_type="text",
            approval_status="submitted",
            uploaded_by=self.user,
        )

        rejected_without_comment = self.client.post(f"/api/federal/standards/indicator-evidence/{evidence.id}/reject/", {}, format="json")
        rejected = self.client.post(
            f"/api/federal/standards/indicator-evidence/{evidence.id}/reject/",
            {"comment": "Wrong reporting period."},
            format="json",
        )

        self.assertEqual(rejected_without_comment.status_code, 400)
        self.assertEqual(rejected.status_code, 200, rejected.data)
        self.assertEqual(payload(rejected)["approval_status"], "rejected")
        self.assertEqual(payload(rejected)["rejection_comment"], "Wrong reporting period.")

    def test_indicator_import_template_preview_and_confirm(self):
        template = self.client.get(f"/api/federal/standards/me-indicators/{self.indicator.id}/import-template/")
        csv_text = "\n".join([
            "indicator_code,period_start,period_end,progress_value,cumulative_value,qualitative_value,rating_category,notes,evidence_reference",
            f"{self.indicator.indicator_code},2025-01-01,2025-03-31,4,4,,,Imported Q1,https://example.test/q1.pdf",
            f"{self.indicator.indicator_code},2025-04-01,2025-06-30,6,10,,,Imported Q2,",
        ])
        preview = self.client.post(
            f"/api/federal/standards/me-indicators/{self.indicator.id}/import-preview/",
            {"csv_text": csv_text},
            format="json",
        )
        confirmed = self.client.post(
            f"/api/federal/standards/me-indicators/{self.indicator.id}/import-confirm/",
            {"csv_text": csv_text, "submit": True},
            format="json",
        )

        self.assertEqual(template.status_code, 200)
        self.assertIn("indicator_code", template.content.decode())
        self.assertEqual(preview.status_code, 200, preview.data)
        self.assertEqual(payload(preview)["summary"]["valid"], 2)
        self.assertEqual(confirmed.status_code, 201, confirmed.data)
        self.assertEqual(payload(confirmed)["summary"]["imported"], 2)
        self.assertTrue(MEIndicatorValue.objects.filter(indicator=self.indicator, value_source="import", approval_status="submitted").exists())

    def test_indicator_import_blocks_approved_period(self):
        MEIndicatorValue.objects.create(
            indicator=self.indicator,
            period_start="2025-01-01",
            period_end="2025-03-31",
            progress_value_numeric=5,
            cumulative_value_numeric=5,
            value_source="manual",
            source_reference_id="approved-q1",
            approval_status="approved",
            created_by=self.user,
        )
        csv_text = "\n".join([
            "indicator_code,period_start,period_end,progress_value,cumulative_value,qualitative_value,rating_category,notes,evidence_reference",
            f"{self.indicator.indicator_code},2025-01-01,2025-03-31,4,4,,,Imported Q1,",
        ])

        preview = self.client.post(
            f"/api/federal/standards/me-indicators/{self.indicator.id}/import-preview/",
            {"csv_text": csv_text},
            format="json",
        )
        confirmed = self.client.post(
            f"/api/federal/standards/me-indicators/{self.indicator.id}/import-confirm/",
            {"csv_text": csv_text},
            format="json",
        )

        self.assertEqual(preview.status_code, 200, preview.data)
        self.assertEqual(payload(preview)["summary"]["invalid"], 1)
        self.assertIn("Approved value already exists", payload(preview)["invalid_rows"][0]["errors"][0])
        self.assertEqual(confirmed.status_code, 400)


class FoodHandlersAutomaticKpiServiceTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.state = State.objects.create(name="Lagos", code="LA")
        self.lga = LGA.objects.create(state=self.state, name="Ikeja")
        self.federal_admin = User.objects.create_user(
            "federal-kpi-engine",
            "federal-kpi-engine@example.com",
            "StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            state=self.state,
        )
        self.doctor = User.objects.create_user(
            "doctor-kpi-engine",
            "doctor-kpi-engine@example.com",
            "StrongPass123!",
            role=UserRole.DOCTOR,
            state=self.state,
        )
        self.state_admin = User.objects.create_user(
            "state-kpi-engine",
            "state-kpi-engine@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.state,
        )
        self.client.force_authenticate(self.federal_admin)
        self.employer_org = Organization.objects.create(
            name="Prime Foods Ltd",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
            lga=self.lga,
        )
        self.employer = Employer.objects.create(
            organization=self.employer_org,
            business_name="Prime Foods Ltd",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Ada",
            contact_person_phone="08000000001",
            contact_person_email="ada@primefoods.example.com",
            address="12 Marina",
            state=self.state,
            lga=self.lga,
        )
        self.facility_org = Organization.objects.create(
            name="Central Medical Lab",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.state,
            lga=self.lga,
        )
        self.facility = MedicalFacility.objects.create(
            organization=self.facility_org,
            facility_name="Central Medical Lab",
            facility_type=FacilityType.CLINIC,
            ownership_type=OwnershipType.PRIVATE,
            license_number="FAC-001",
            address="34 Broad Street",
            state=self.state,
            lga=self.lga,
            contact_person="Lab Manager",
            phone="08000000002",
            email="facility@example.com",
            accreditation_status=AccreditationStatus.APPROVED,
            accreditation_start_date=timezone.localdate() - timezone.timedelta(days=90),
            accreditation_expiry_date=timezone.localdate() + timezone.timedelta(days=180),
        )
        self.facility_admin = User.objects.create_user(
            "facility-kpi-engine",
            "facility-kpi-engine@example.com",
            "StrongPass123!",
            role=UserRole.FACILITY_ADMIN,
            state=self.state,
            organization=self.facility_org,
        )
        self.expired_facility_org = Organization.objects.create(
            name="Old Medical Lab",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.state,
            lga=self.lga,
        )
        self.expired_facility = MedicalFacility.objects.create(
            organization=self.expired_facility_org,
            facility_name="Old Medical Lab",
            facility_type=FacilityType.CLINIC,
            ownership_type=OwnershipType.PRIVATE,
            license_number="FAC-002",
            address="5 Allen Avenue",
            state=self.state,
            lga=self.lga,
            contact_person="Legacy Manager",
            phone="08000000003",
            email="old-facility@example.com",
            accreditation_status=AccreditationStatus.EXPIRED,
            accreditation_start_date=timezone.localdate() - timezone.timedelta(days=500),
            accreditation_expiry_date=timezone.localdate() - timezone.timedelta(days=5),
        )
        self.handler_one_user = User.objects.create_user(
            "handler-one",
            "handler-one@example.com",
            "StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.state,
        )
        self.handler_two_user = User.objects.create_user(
            "handler-two",
            "handler-two@example.com",
            "StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.state,
        )
        self.handler_one = FoodHandlerProfile.objects.create(
            user=self.handler_one_user,
            full_name="Handler One",
            date_of_birth="1990-01-01",
            gender=Gender.FEMALE,
            nin="12345678901",
            phone="08000000004",
            email="handler-one@example.com",
            home_address="1 Food Street",
            state=self.state,
            lga=self.lga,
            employer=self.employer,
            food_handler_category="food_preparer",
            system_identifier="FH-001",
            current_status=FoodHandlerStatus.FIT,
        )
        self.handler_two = FoodHandlerProfile.objects.create(
            user=self.handler_two_user,
            full_name="Handler Two",
            date_of_birth="1991-02-02",
            gender=Gender.MALE,
            nin="",
            phone="08000000005",
            email="handler-two@example.com",
            home_address="",
            state=self.state,
            lga=self.lga,
            employer=self.employer,
            food_handler_category="food_preparer",
            system_identifier="FH-002",
            current_status=FoodHandlerStatus.TEMPORARILY_EXCLUDED,
        )
        self.policy = PolicyVersion.objects.create(
            version_code="FH-POL-2026-KPI",
            title="Food handlers KPI policy",
            description="Active policy for KPI engine tests.",
            version_type=PolicyVersionType.MAJOR,
            status=PolicyVersionStatus.ACTIVE,
            effective_start_date=timezone.now() - timezone.timedelta(days=30),
            published_at=timezone.now() - timezone.timedelta(days=30),
            change_summary="KPI engine tests.",
            created_by=self.federal_admin,
        )
        CertificateValidityRule.objects.create(
            policy_version=self.policy,
            routine_assessment_interval_days=180,
            certificate_validity_days=180,
            renewal_window_days=30,
            grace_period_days=0,
            status=TemplateStatus.ACTIVE,
            created_by=self.federal_admin,
        )
        FacilityRequirementRule.objects.create(
            policy_version=self.policy,
            requirement_name="Annual Re-Accreditation",
            requirement_code="FREQ-REACCREDIT-12M",
            category="reaccreditation",
            mandatory=True,
            evidence_type="file",
            renewal_required=True,
            renewal_interval_days=365,
            status=StandardStatus.ACTIVE,
            created_by=self.federal_admin,
        )
        CertificateTemplate.objects.create(
            policy_version=self.policy,
            template_name="National Certificate Standard",
            template_version="2026.1",
            required_fields=["certificate_id", "qr_code"],
            qr_payload_config={"verification_enabled": True, "central_database_validation": True},
            status=TemplateStatus.ACTIVE,
            created_by=self.federal_admin,
        )
        ReturnToWorkRule.objects.create(
            policy_version=self.policy,
            condition_name="Default exclusion",
            condition_code="RTW-EXCLUDE-48H",
            default_exclusion_hours=48,
            requires_medical_clearance=True,
            clearance_document_required=True,
            status=StandardStatus.ACTIVE,
            created_by=self.federal_admin,
        )
        self.assessment_one = MedicalAssessment.objects.create(
            food_handler=self.handler_one,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            assessment_date=timezone.now() - timezone.timedelta(days=50),
            status="validated",
            final_decision="fit",
            signed_at=timezone.now() - timezone.timedelta(days=49),
        )
        self.assessment_two = MedicalAssessment.objects.create(
            food_handler=self.handler_two,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            assessment_date=timezone.now() - timezone.timedelta(days=220),
            status="validated",
            final_decision="fit",
            signed_at=timezone.now() - timezone.timedelta(days=219),
        )
        self.runtime_certificate_template = RuntimeCertificateTemplate.objects.create(
            name="Runtime Certificate",
            scope="national",
            is_active=True,
            is_default=True,
            created_by=self.federal_admin,
        )
        self.active_certificate = Certificate.objects.create(
            certificate_number="CERT-001",
            verification_token="token-001",
            food_handler=self.handler_one,
            assessment=self.assessment_one,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            issuing_state=self.state,
            template=self.runtime_certificate_template,
            issue_date=timezone.localdate() - timezone.timedelta(days=20),
            expiry_date=timezone.localdate() + timezone.timedelta(days=160),
            status=CertificateStatus.ACTIVE,
            verification_url="https://example.com/verify/token-001",
            digital_signature_hash="hash-001",
        )
        self.expired_certificate = Certificate.objects.create(
            certificate_number="CERT-002",
            verification_token="token-002",
            food_handler=self.handler_two,
            assessment=self.assessment_two,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            issuing_state=self.state,
            template=self.runtime_certificate_template,
            issue_date=timezone.localdate() - timezone.timedelta(days=220),
            expiry_date=timezone.localdate() - timezone.timedelta(days=10),
            status=CertificateStatus.ACTIVE,
            verification_url="https://example.com/verify/token-002",
            digital_signature_hash="hash-002",
        )
        CertificateVerificationLog.objects.create(
            certificate=self.active_certificate,
            certificate_number_submitted=self.active_certificate.certificate_number,
            verification_token_submitted=self.active_certificate.verification_token,
            result=VerificationResult.VALID,
            verifier_type="inspector",
        )
        CertificateVerificationLog.objects.create(
            certificate=self.expired_certificate,
            certificate_number_submitted=self.expired_certificate.certificate_number,
            verification_token_submitted=self.expired_certificate.verification_token,
            result=VerificationResult.INVALID,
            verifier_type="public",
        )
        IllnessReport.objects.create(
            food_handler=self.handler_one,
            employer=self.employer,
            reported_by=self.federal_admin,
            suspected_condition=SuspectedCondition.CHOLERA,
            exclusion_start_date=timezone.localdate() - timezone.timedelta(days=10),
            earliest_return_date=timezone.localdate() - timezone.timedelta(days=2),
            clearance_required=True,
            clearance_status=ClearanceStatus.CLEARED,
            reviewed_by_doctor=self.doctor,
            cleared_at=timezone.now() - timezone.timedelta(days=1),
        )
        IllnessReport.objects.create(
            food_handler=self.handler_two,
            employer=self.employer,
            reported_by=self.federal_admin,
            suspected_condition=SuspectedCondition.SHIGELLA,
            exclusion_start_date=timezone.localdate() - timezone.timedelta(days=5),
            earliest_return_date=timezone.localdate() + timezone.timedelta(days=1),
            clearance_required=True,
            clearance_status=ClearanceStatus.PENDING,
        )
        self.expired_indicator = self.make_indicator(
            "Expired Certificate Rate",
            "ME-EXPIRED-RATE",
            "automatic",
            "certificates",
            "certificate_records",
            "monthly",
            policy_standard_code="FH-VALIDITY-2024-001",
            rule_parameter_key="certificate_validity_months",
        )
        self.certification_indicator = self.make_indicator(
            "Food Handler Certification Rate",
            "ME-CERT-RATE",
            "automatic",
            "certificates",
            "certificate_records",
            "quarterly",
            policy_standard_code="FH-VALIDITY-2024-001",
        )
        self.facility_indicator = self.make_indicator(
            "Facility Accreditation Compliance",
            "ME-FACILITY-ACCRED",
            "automatic",
            "medical_facilities",
            "facility_records",
            "quarterly",
            policy_standard_code="FH-FAC-2024-001",
            rule_parameter_key="reaccreditation_interval_months",
        )
        self.qr_indicator = self.make_indicator(
            "QR Verification Failure Rate",
            "ME-QR-FAIL",
            "automatic",
            "qr_verification_logs",
            "inspections",
            "monthly",
            policy_standard_code="FH-CERT-2024-001",
            rule_parameter_key="requires_qr_code",
        )
        self.rtw_indicator = self.make_indicator(
            "Return-to-Work Clearance Rate",
            "ME-RTW-RATE",
            "hybrid",
            "return_to_work_clearances",
            "medical_test_records",
            "quarterly",
            policy_standard_code="FH-RTW-2024-001",
            rule_parameter_key="standard_exclusion_period_hours_after_symptoms_stop",
            allow_manual_override=True,
            override_requires_reason=True,
        )
        self.completeness_indicator = self.make_indicator(
            "Data Completeness Score",
            "ME-DATA-COMPLETE",
            "automatic",
            "system_required_fields",
            "food_handler_registry",
            "monthly",
        )
        self.manual_indicator = self.make_indicator(
            "Manual KPI",
            "ME-MANUAL",
            "manual",
            "",
            "manual",
            "monthly",
        )

    def make_indicator(self, name, code, input_mode, calculation_source, data_source, reporting_frequency, **extra):
        return MEIndicator.objects.create(
            policy_version=self.policy,
            indicator_name=name,
            indicator_code=code,
            description=f"{name} test indicator.",
            input_mode=input_mode,
            calculation_type="percentage" if calculation_source else "",
            calculation_source=calculation_source,
            data_source=data_source,
            reporting_frequency=reporting_frequency,
            visualization_type="card",
            status=StandardStatus.ACTIVE,
            created_by=self.federal_admin,
            **extra,
        )

    def test_calculate_kpi_persists_value_and_log(self):
        result = FoodHandlersKpiCalculationService.calculate_kpi(
            self.expired_indicator.id,
            filters={"period_start": str(timezone.localdate() - timezone.timedelta(days=365)), "period_end": str(timezone.localdate())},
            actor=self.federal_admin,
        )

        self.expired_indicator.refresh_from_db()
        self.assertEqual(str(result["value"]), "50.0000")
        self.assertEqual(str(self.expired_indicator.latest_value), "50.0000")
        self.assertIsNotNone(self.expired_indicator.last_calculated_at)
        self.assertTrue(
            MEIndicatorValue.objects.filter(
                indicator=self.expired_indicator,
                value_source="automated",
                source_reference_id="automatic-kpi-engine",
            ).exists()
        )
        log = MEIndicatorCalculationLog.objects.get(indicator=self.expired_indicator)
        self.assertEqual(log.calculation_status, "success")
        self.assertEqual(str(log.calculated_value), "50.0000")
        self.assertEqual(log.policy_standard_code, "FH-VALIDITY-2024-001")

    def test_specific_kpi_methods_and_source_records_use_real_operational_data(self):
        common_filters = {"period_start": str(timezone.localdate() - timezone.timedelta(days=365)), "period_end": str(timezone.localdate())}
        certification = FoodHandlersKpiCalculationService.calculate_food_handler_certification_rate(common_filters, period=FoodHandlersKpiCalculationService.resolve_period("quarterly", common_filters))
        facility = FoodHandlersKpiCalculationService.calculate_facility_accreditation_compliance(common_filters, period=FoodHandlersKpiCalculationService.resolve_period("quarterly", common_filters))
        qr = FoodHandlersKpiCalculationService.calculate_qr_verification_failure_rate(
            common_filters,
            period=FoodHandlersKpiCalculationService.resolve_period("monthly", common_filters),
            policy_context=ActivePolicyRuleService.get_active_policy_standard_by_code("FH-CERT-2024-001"),
        )
        rtw = FoodHandlersKpiCalculationService.calculate_return_to_work_clearance_rate(common_filters, period=FoodHandlersKpiCalculationService.resolve_period("quarterly", common_filters))
        records = FoodHandlersKpiCalculationService.get_kpi_source_records(self.qr_indicator.id, common_filters)

        self.assertEqual(str(certification["value"]), "50.0000")
        self.assertEqual(str(facility["value"]), "50.0000")
        self.assertEqual(str(qr["value"]), "50.0000")
        self.assertEqual(str(rtw["value"]), "50.0000")
        self.assertEqual(len(records["records"]), 2)
        self.assertIn("invalid", {row["result"] for row in records["records"]})

    def test_recalculate_automatic_kpis_runs_automatic_and_hybrid_only(self):
        summary = FoodHandlersKpiCalculationService.recalculate_automatic_kpis(
            filters={"period_start": str(timezone.localdate() - timezone.timedelta(days=365)), "period_end": str(timezone.localdate())},
            actor=self.federal_admin,
        )

        success_codes = {row["indicator_code"] for row in summary["success"]}
        self.assertIn("ME-EXPIRED-RATE", success_codes)
        self.assertIn("ME-RTW-RATE", success_codes)
        self.assertIn("ME-DATA-COMPLETE", success_codes)
        self.assertNotIn("ME-MANUAL", success_codes)

    def test_manual_kpi_is_rejected_and_failed_calculation_creates_log(self):
        with self.assertRaisesMessage(KPIEngineError, "Only automatic and hybrid KPIs can be auto-calculated."):
            FoodHandlersKpiCalculationService.calculate_kpi(self.manual_indicator.id, actor=self.federal_admin)

        CertificateTemplate.objects.filter(policy_version=self.policy).delete()
        with self.assertRaisesMessage(ActivePolicyRuleError, "Active policy rule not found for this KPI calculation."):
            FoodHandlersKpiCalculationService.calculate_kpi(
                self.qr_indicator.id,
                filters={"period_start": str(timezone.localdate() - timezone.timedelta(days=30)), "period_end": str(timezone.localdate())},
                actor=self.federal_admin,
            )
        failed_log = MEIndicatorCalculationLog.objects.filter(indicator=self.qr_indicator, calculation_status="failed").latest("created_at")
        self.assertIn("Active policy rule not found", failed_log.error_message)

    def test_calculation_and_source_record_endpoints_expose_engine_output(self):
        FoodHandlersKpiCalculationService.calculate_kpi(
            self.expired_indicator.id,
            filters={"period_start": str(timezone.localdate() - timezone.timedelta(days=365)), "period_end": str(timezone.localdate())},
            actor=self.federal_admin,
        )

        calculation = self.client.get(f"/api/federal/standards/me-indicators/{self.expired_indicator.id}/calculation/")
        source_records = self.client.get(
            f"/api/federal/standards/me-indicators/{self.expired_indicator.id}/source-records/",
            {"period_start": str(timezone.localdate() - timezone.timedelta(days=365)), "period_end": str(timezone.localdate())},
        )

        self.assertEqual(calculation.status_code, 200, calculation.data)
        self.assertEqual(payload(calculation)["linked_policy_standard"], "FH-VALIDITY-2024-001")
        self.assertEqual(str(payload(calculation)["latest_calculated_value"]), "50.0000")
        self.assertEqual(source_records.status_code, 200, source_records.data)
        self.assertEqual(payload(source_records)["count"], 2)
        self.assertEqual(payload(source_records)["records"][0]["certificate_number"], "CERT-001")

    def test_recalculate_endpoint_uses_food_handler_kpi_engine_for_automatic_indicators(self):
        response = self.client.post(
            f"/api/federal/standards/me-indicators/{self.qr_indicator.id}/recalculate/",
            {
                "period_start": str(timezone.localdate() - timezone.timedelta(days=365)),
                "period_end": str(timezone.localdate()),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        data = payload(response)
        self.assertEqual(data["value_source"], "automated")
        self.assertEqual(data["progress_value_numeric"], "50.0000")
        self.assertTrue(MEIndicatorCalculationLog.objects.filter(indicator=self.qr_indicator, calculation_status="success").exists())

    def test_hybrid_override_requires_reason_and_preserves_original_value(self):
        FoodHandlersKpiCalculationService.calculate_kpi(
            self.rtw_indicator.id,
            filters={"period_start": str(timezone.localdate() - timezone.timedelta(days=365)), "period_end": str(timezone.localdate())},
            actor=self.federal_admin,
        )

        missing_reason = self.client.post(
            f"/api/federal/standards/me-indicators/{self.rtw_indicator.id}/override/",
            {
                "period_start": str(timezone.localdate() - timezone.timedelta(days=365)),
                "period_end": str(timezone.localdate()),
                "override_value": "75.0000",
                "reason": "",
            },
            format="json",
        )
        response = self.client.post(
            f"/api/federal/standards/me-indicators/{self.rtw_indicator.id}/override/",
            {
                "period_start": str(timezone.localdate() - timezone.timedelta(days=365)),
                "period_end": str(timezone.localdate()),
                "override_value": "75.0000",
                "reason": "Included validated offline clearances.",
            },
            format="json",
        )

        self.assertEqual(missing_reason.status_code, 400)
        self.assertEqual(response.status_code, 201, response.data)
        data = payload(response)
        self.assertEqual(data["value_source"], "override")
        self.assertEqual(data["override_reason"], "Included validated offline clearances.")
        self.assertEqual(str(data["original_calculated_value"]), "50.0000")
        self.assertEqual(str(data["overridden_value"]), "75.0000")
        self.rtw_indicator.refresh_from_db()
        self.assertEqual(str(self.rtw_indicator.latest_value), "75.0000")
        self.assertTrue(MEIndicatorCalculationLog.objects.filter(indicator=self.rtw_indicator, calculation_status="overridden").exists())

    def test_unauthorized_user_cannot_override_hybrid_kpi(self):
        FoodHandlersKpiCalculationService.calculate_kpi(
            self.rtw_indicator.id,
            filters={"period_start": str(timezone.localdate() - timezone.timedelta(days=365)), "period_end": str(timezone.localdate())},
            actor=self.federal_admin,
        )
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(
            f"/api/federal/standards/me-indicators/{self.rtw_indicator.id}/override/",
            {
                "period_start": str(timezone.localdate() - timezone.timedelta(days=365)),
                "period_end": str(timezone.localdate()),
                "override_value": "75.0000",
                "reason": "Attempted unauthorized override.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_state_admin_source_records_are_scoped_to_their_state(self):
        other_state = State.objects.create(name="Oyo", code="OY")
        other_lga = LGA.objects.create(state=other_state, name="Ibadan North")
        other_org = Organization.objects.create(
            name="Other Foods Ltd",
            organization_type=OrganizationType.EMPLOYER,
            state=other_state,
            lga=other_lga,
        )
        other_employer = Employer.objects.create(
            organization=other_org,
            business_name="Other Foods Ltd",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Bola",
            contact_person_phone="08000000009",
            contact_person_email="bola@otherfoods.example.com",
            address="Ring Road",
            state=other_state,
            lga=other_lga,
        )
        other_handler_user = User.objects.create_user(
            "other-handler",
            "other-handler@example.com",
            "StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=other_state,
        )
        other_handler = FoodHandlerProfile.objects.create(
            user=other_handler_user,
            full_name="Other Handler",
            date_of_birth="1992-03-03",
            gender=Gender.MALE,
            nin="99887766554",
            phone="08000000010",
            email="other-handler@example.com",
            home_address="Bodija",
            state=other_state,
            lga=other_lga,
            employer=other_employer,
            food_handler_category="food_preparer",
            system_identifier="FH-003",
            current_status=FoodHandlerStatus.FIT,
        )
        other_assessment = MedicalAssessment.objects.create(
            food_handler=other_handler,
            employer=other_employer,
            facility=self.facility,
            doctor=self.doctor,
            assessment_date=timezone.now() - timezone.timedelta(days=10),
            status="validated",
            final_decision="fit",
            signed_at=timezone.now() - timezone.timedelta(days=9),
        )
        Certificate.objects.create(
            certificate_number="CERT-003",
            verification_token="token-003",
            food_handler=other_handler,
            assessment=other_assessment,
            employer=other_employer,
            facility=self.facility,
            doctor=self.doctor,
            issuing_state=other_state,
            template=self.runtime_certificate_template,
            issue_date=timezone.localdate() - timezone.timedelta(days=5),
            expiry_date=timezone.localdate() + timezone.timedelta(days=170),
            status=CertificateStatus.ACTIVE,
            verification_url="https://example.com/verify/token-003",
            digital_signature_hash="hash-003",
        )

        self.client.force_authenticate(self.state_admin)
        response = self.client.get(
            f"/api/federal/standards/me-indicators/{self.expired_indicator.id}/source-records/",
            {"period_start": str(timezone.localdate() - timezone.timedelta(days=365)), "period_end": str(timezone.localdate())},
        )

        self.assertEqual(response.status_code, 200, response.data)
        rows = payload(response)["records"]
        self.assertTrue(rows)
        self.assertEqual({row["state"] for row in rows}, {"Lagos"})

    def test_facility_admin_source_records_are_scoped_to_their_facility_and_cannot_recalculate(self):
        self.client.force_authenticate(self.facility_admin)
        records = self.client.get(
            f"/api/federal/standards/me-indicators/{self.expired_indicator.id}/source-records/",
            {"period_start": str(timezone.localdate() - timezone.timedelta(days=365)), "period_end": str(timezone.localdate())},
        )
        recalculate = self.client.post(
            f"/api/federal/standards/me-indicators/{self.expired_indicator.id}/recalculate/",
            {"period_start": str(timezone.localdate() - timezone.timedelta(days=365)), "period_end": str(timezone.localdate())},
            format="json",
        )

        self.assertEqual(records.status_code, 200, records.data)
        self.assertTrue(all(row["facility"] == "Central Medical Lab" for row in payload(records)["records"]))
        self.assertEqual(recalculate.status_code, 403)


class ActivePolicyRuleServiceTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            "federal-policy-rule-reader",
            "federal-policy-rule-reader@example.com",
            "StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.policy = PolicyVersion.objects.create(
            version_code="NG-FHS-2026-RULES",
            title="Active policy rules",
            description="Policy with active standards for KPI rule resolution.",
            version_type=PolicyVersionType.MAJOR,
            status=PolicyVersionStatus.ACTIVE,
            change_summary="Testing active KPI policy lookups.",
            created_by=self.user,
        )
        CertificateValidityRule.objects.create(
            policy_version=self.policy,
            routine_assessment_interval_days=180,
            certificate_validity_days=180,
            renewal_window_days=30,
            grace_period_days=0,
            status=TemplateStatus.ACTIVE,
            created_by=self.user,
        )
        FacilityRequirementRule.objects.create(
            policy_version=self.policy,
            requirement_name="Annual Re-Accreditation",
            requirement_code="FREQ-REACCREDIT-12M",
            category="reaccreditation",
            mandatory=True,
            evidence_type="file",
            renewal_required=True,
            renewal_interval_days=365,
            status=StandardStatus.ACTIVE,
            created_by=self.user,
        )
        CertificateTemplate.objects.create(
            policy_version=self.policy,
            template_name="National Certificate",
            template_version="2026.1",
            required_fields=["certificate_id", "qr_code"],
            qr_payload_config={"verification_enabled": True, "central_database_validation": True},
            status=TemplateStatus.ACTIVE,
            created_by=self.user,
        )
        ReturnToWorkRule.objects.create(
            policy_version=self.policy,
            condition_name="Default exclusion",
            condition_code="RTW-EXCLUDE-48H",
            default_exclusion_hours=48,
            requires_medical_clearance=True,
            employer_acknowledgement_required=True,
            clearance_document_required=True,
            status=StandardStatus.ACTIVE,
            created_by=self.user,
        )
        ReturnToWorkRule.objects.create(
            policy_version=self.policy,
            condition_name="Cholera",
            condition_code="RTW-CHOLERA",
            default_exclusion_hours=168,
            requires_medical_clearance=True,
            requires_lab_clearance=True,
            negative_samples_required=2,
            sample_interval_hours=24,
            status=StandardStatus.ACTIVE,
            created_by=self.user,
        )

    def test_active_policy_rule_service_resolves_required_food_handler_codes(self):
        validity = ActivePolicyRuleService.get_active_policy_standard_by_code("FH-VALIDITY-2024-001")
        facility = ActivePolicyRuleService.get_active_policy_standard_by_code("FH-FAC-2024-001")
        certificate = ActivePolicyRuleService.get_active_policy_standard_by_code("FH-CERT-2024-001")
        return_to_work = ActivePolicyRuleService.get_active_policy_standard_by_code("FH-RTW-2024-001")

        self.assertEqual(validity["parameters"]["certificate_validity_months"], 6)
        self.assertEqual(validity["parameters"]["assessment_validity_months"], 6)
        self.assertEqual(facility["parameters"]["reaccreditation_interval_months"], 12)
        self.assertTrue(certificate["parameters"]["requires_qr_code"])
        self.assertTrue(certificate["parameters"]["certificate_must_be_digitally_verifiable"])
        self.assertEqual(
            return_to_work["parameters"]["standard_exclusion_period_hours_after_symptoms_stop"],
            48,
        )
        self.assertEqual(len(return_to_work["parameters"]["specific_infection_clearance_rules"]), 2)

    def test_missing_active_policy_rule_returns_clear_error(self):
        CertificateValidityRule.objects.filter(policy_version=self.policy).delete()

        with self.assertRaisesMessage(
            ActivePolicyRuleError,
            "Active policy rule not found for this KPI calculation.",
        ):
            ActivePolicyRuleService.get_policy_rule_parameter(
                "FH-VALIDITY-2024-001",
                "certificate_validity_months",
            )


class StandardsHardeningTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.federal_admin = User.objects.create_user(
            "standards-admin",
            "standards-admin@example.com",
            "StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.state_admin = User.objects.create_user(
            "state-admin",
            "state-admin@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
        )
        self.employer = User.objects.create_user(
            "employer",
            "employer@example.com",
            "StrongPass123!",
            role=UserRole.EMPLOYER,
        )
        self.policy = PolicyVersion.objects.create(
            version_code="NG-FHS-2026-HARDENING",
            title="Hardening policy",
            description="Policy used for QA hardening tests.",
            version_type=PolicyVersionType.MAJOR,
            status=PolicyVersionStatus.DRAFT,
            change_summary="Hardening.",
            created_by=self.federal_admin,
        )

    def _add_required_config(self, policy):
        CertificateTemplate.objects.create(
            policy_version=policy,
            template_name="Food handler certificate",
            template_version="v1",
            status=TemplateStatus.ACTIVE,
            created_by=self.federal_admin,
        )
        MedicalTestRule.objects.create(
            policy_version=policy,
            name="Typhoid screening",
            code="TYPHOID",
            test_type=TestType.LABORATORY,
            rule_type=RuleType.MANDATORY,
            status=StandardStatus.ACTIVE,
            created_by=self.federal_admin,
        )
        CertificateValidityRule.objects.create(
            policy_version=policy,
            status=TemplateStatus.ACTIVE,
            created_by=self.federal_admin,
        )
        ReportingTemplate.objects.create(
            policy_version=policy,
            template_name="Monthly state report",
            template_code="MONTHLY_STATE",
            reporting_frequency=ReportingFrequency.MONTHLY,
            status=TemplateStatus.ACTIVE,
            created_by=self.federal_admin,
        )

    def test_published_rules_cannot_be_edited_directly(self):
        category = FoodHandlerCategory.objects.create(
            policy_version=self.policy,
            name="Published Handler",
            code="PUBLISHED_HANDLER",
            risk_level=RiskLevel.HIGH,
            status=StandardStatus.ACTIVE,
            created_by=self.federal_admin,
        )
        self.client.force_authenticate(self.federal_admin)

        response = self.client.patch(
            f"/api/federal/standards/food-handler-categories/{category.id}/",
            {"description": "Direct edit should be blocked."},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        category.refresh_from_db()
        self.assertEqual(category.description, "")

    def test_unauthorized_users_cannot_create_restricted_config(self):
        self.client.force_authenticate(self.employer)

        response = self.client.post(
            "/api/federal/standards/food-handler-categories/",
            {
                "policy_version": str(self.policy.id),
                "name": "Unauthorized Handler",
                "code": "UNAUTHORIZED_HANDLER",
                "risk_level": RiskLevel.LOW,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_state_admin_can_read_but_cannot_create_standards_config(self):
        self.client.force_authenticate(self.state_admin)

        read_response = self.client.get("/api/federal/standards/food-handler-categories/")
        write_response = self.client.post(
            "/api/federal/standards/food-handler-categories/",
            {
                "policy_version": str(self.policy.id),
                "name": "State Write Attempt",
                "code": "STATE_WRITE_ATTEMPT",
                "risk_level": RiskLevel.MEDIUM,
            },
            format="json",
        )

        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(write_response.status_code, 403)

    def test_policy_publication_fails_if_required_config_is_missing(self):
        self.policy.status = PolicyVersionStatus.APPROVED
        self.policy.save(update_fields=["status", "updated_at"])

        with self.assertRaisesRegex(ValueError, "certificate template"):
            PolicyVersionService.publish(self.policy, self.federal_admin)

        self.policy.refresh_from_db()
        self.assertEqual(self.policy.status, PolicyVersionStatus.APPROVED)

    def test_high_impact_policy_submit_requires_approval_record(self):
        self._add_required_config(self.policy)

        PolicyVersionService.submit_for_review(self.policy, self.federal_admin)

        self.policy.refresh_from_db()
        approval = Approval.objects.get(entity_type="PolicyVersion", entity_id=self.policy.id)
        self.assertEqual(self.policy.status, PolicyVersionStatus.UNDER_REVIEW)
        self.assertEqual(approval.status, ApprovalStatus.PENDING)
        self.assertEqual(approval.impact_level, ImpactLevel.HIGH)

    def test_policy_lifecycle_writes_audit_logs(self):
        self._add_required_config(self.policy)

        PolicyVersionService.submit_for_review(self.policy, self.federal_admin)
        self.policy.refresh_from_db()
        PolicyVersionService.approve(self.policy, self.federal_admin, comment="Approved for QA.")
        self.policy.refresh_from_db()
        PolicyVersionService.publish(self.policy, self.federal_admin, comment="Publish QA policy.")

        events = set(
            AuditLog.objects.filter(
                action=AuditAction.WORKFLOW_TRANSITION,
                target_type="PolicyVersion",
                target_id=str(self.policy.id),
            ).values_list("metadata__event", flat=True)
        )
        self.assertIn("policy_version_submitted_for_review", events)
        self.assertIn("policy_version_approved", events)
        self.assertIn("policy_version_published", events)

    def test_rule_create_api_writes_audit_log(self):
        self.client.force_authenticate(self.federal_admin)

        response = self.client.post(
            "/api/federal/standards/food-handler-categories/",
            {
                "policy_version": str(self.policy.id),
                "name": "Audit Handler",
                "code": "AUDIT_HANDLER",
                "risk_level": RiskLevel.MEDIUM,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        data = payload(response)
        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditAction.CREATE,
                target_type="FoodHandlerCategory",
                target_id=data["id"],
                metadata__event="foodhandlercategory_created",
            ).exists()
        )


class PolicyVersionMetadataTests(APITestCase):
    def setUp(self):
        bump_active_standards_cache_version()
        self.user = User.objects.create_user(
            "policy-meta-admin",
            "policy-meta-admin@example.com",
            "StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.client.force_authenticate(self.user)

    def test_create_policy_version_with_metadata_round_trips(self):
        response = self.client.post(
            "/api/federal/standards/policy-versions/",
            {
                "version_code": "FH-2024.1",
                "title": "Food Handler Eligibility Standard",
                "version_type": "major",
                "policy_category": "food_handler_eligibility",
                "legal_basis": "National Guidelines for Food Handlers' Medical Test 2024",
                "scope": "All states and the FCT",
                "affected_entities": ["States", "Medical facilities", "Food handlers"],
                "review_date": "2026-12-31",
                "description": "Defines covered food handler categories.",
                "change_summary": "Initial version.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        data = response.data.get("data", response.data)
        self.assertEqual(data["policy_category"], "food_handler_eligibility")
        self.assertEqual(data["affected_entities"], ["States", "Medical facilities", "Food handlers"])
        self.assertEqual(data["review_date"], "2026-12-31")
        self.assertEqual(data["legal_basis"], "National Guidelines for Food Handlers' Medical Test 2024")

    def test_invalid_policy_category_rejected(self):
        response = self.client.post(
            "/api/federal/standards/policy-versions/",
            {
                "version_code": "FH-2024.2",
                "title": "Bad category",
                "version_type": "minor",
                "policy_category": "not_a_real_category",
                "description": "x",
                "change_summary": "x",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)


class MedicalTestPackageTests(APITestCase):
    def setUp(self):
        from apps.standards.models import PolicyVersion, PolicyVersionStatus, PolicyVersionType
        bump_active_standards_cache_version()
        self.user = User.objects.create_user(
            "package-admin", "package-admin@example.com", "StrongPass123!", role=UserRole.FEDERAL_ADMIN,
        )
        self.client.force_authenticate(self.user)
        self.policy = PolicyVersion.objects.create(
            version_code="PKG-POL-1", title="Package Policy", description="d",
            version_type=PolicyVersionType.MAJOR, status=PolicyVersionStatus.DRAFT, change_summary="c",
        )

    def test_create_package_with_components(self):
        created = self.client.post(
            "/api/federal/standards/medical-test-packages/",
            {"policy_version": str(self.policy.id), "name": "FH Package", "code": "PKG-1", "package_version": "1.0"},
            format="json",
        )
        self.assertEqual(created.status_code, 201, created.data)
        package_id = created.data.get("data", created.data)["id"]

        component = self.client.post(
            "/api/federal/standards/medical-test-package-components/",
            {"package": package_id, "component_type": "stool_microscopy_culture_sensitivity", "label": "Stool MCS", "mandatory": True, "order": 1},
            format="json",
        )
        self.assertEqual(component.status_code, 201, component.data)

        detail = self.client.get(f"/api/federal/standards/medical-test-packages/{package_id}/")
        data = detail.data.get("data", detail.data)
        self.assertEqual(len(data["components"]), 1)
        self.assertEqual(data["mandatory_component_count"], 1)

    def test_cannot_add_component_to_active_policy_package(self):
        from apps.standards.models import PolicyVersion, PolicyVersionStatus, MedicalTestPackage
        active = PolicyVersion.objects.create(
            version_code="PKG-ACTIVE", title="Active", description="d", version_type="major",
            status=PolicyVersionStatus.ACTIVE, change_summary="c",
        )
        package = MedicalTestPackage.objects.create(policy_version=active, name="P", code="PKG-A", status="active")
        blocked = self.client.post(
            "/api/federal/standards/medical-test-package-components/",
            {"package": str(package.id), "component_type": "physical_examination", "label": "PE", "order": 1},
            format="json",
        )
        self.assertEqual(blocked.status_code, 400)

    def test_seed_creates_default_package_with_nine_components(self):
        from apps.standards.models import MedicalTestPackage
        call_command("seed_food_handlers_2024_policy", verbosity=0)
        package = MedicalTestPackage.objects.get(code="FH-PKG-2024-001")
        self.assertEqual(package.components.count(), 9)
        self.assertEqual(package.components.filter(mandatory=True).count(), 8)


class MedicalTestRuleEvaluationTests(APITestCase):
    def setUp(self):
        from apps.standards.models import PolicyVersion, PolicyVersionStatus, PolicyVersionType, MedicalTestRule
        bump_active_standards_cache_version()
        self.MedicalTestRule = MedicalTestRule
        self.user = User.objects.create_user(
            "rule-eval-admin", "rule-eval-admin@example.com", "StrongPass123!", role=UserRole.FEDERAL_ADMIN,
        )
        self.client.force_authenticate(self.user)
        self.policy = PolicyVersion.objects.create(
            version_code="RULE-EVAL-1", title="Rule policy", description="d",
            version_type=PolicyVersionType.MAJOR, status=PolicyVersionStatus.DRAFT, change_summary="c",
        )
        self.rule = MedicalTestRule.objects.create(
            policy_version=self.policy, name="Stool MCS", code="stool_mcs",
            test_type="laboratory", rule_type="mandatory", result_type="positive_negative",
            condition={"operator": "in", "value": ["positive"]},
            action={"block_certification": True, "escalate": "doctor_review"},
            blocking_values=["positive"],
        )

    def test_evaluate_blocks_on_condition_match(self):
        result = self.rule.evaluate("positive")
        self.assertTrue(result["matched_condition"])
        self.assertTrue(result["blocks_certification"])
        self.assertFalse(result["passed"])

    def test_evaluate_passes_on_negative(self):
        result = self.rule.evaluate("negative")
        self.assertFalse(result["blocks_certification"])
        self.assertTrue(result["passed"])

    def test_test_endpoint(self):
        response = self.client.post(
            f"/api/federal/standards/medical-test-rules/{self.rule.id}/test/",
            {"value": "positive"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        data = response.data.get("data", response.data)
        self.assertTrue(data["blocks_certification"])

    def test_test_endpoint_requires_value(self):
        response = self.client.post(f"/api/federal/standards/medical-test-rules/{self.rule.id}/test/", {}, format="json")
        self.assertEqual(response.status_code, 400)


class VaccinationPolicyParamsTests(APITestCase):
    def test_reads_active_policy_validity(self):
        from apps.standards.models import PolicyVersion, PolicyVersionStatus, VaccinationRule
        from apps.standards.services import bump_active_standards_cache_version
        from apps.vaccinations.models import VaccinationRecord

        bump_active_standards_cache_version()
        pv = PolicyVersion.objects.create(
            version_code="VAX-POL-1", title="Vax", description="d", version_type="major",
            status=PolicyVersionStatus.ACTIVE, change_summary="c",
        )
        VaccinationRule.objects.create(
            policy_version=pv, vaccine_name="Typhoid", vaccine_code="typhoid", required=True,
            validity_months=48, dose_schedule=[{"dose": 1, "interval_months": 0}], status="active",
        )
        VaccinationRule.objects.create(
            policy_version=pv, vaccine_name="Hepatitis A", vaccine_code="hepatitis_a", required=True,
            validity_months=120, dose_schedule=[{"dose": 1, "interval_months": 0}, {"dose": 2, "interval_months": 12}], status="active",
        )
        params = VaccinationRecord.policy_validity_params()
        self.assertEqual(params["typhoid_validity_years"], 4)
        self.assertEqual(params["hepatitis_a_second_dose_months"], 12)

    def test_falls_back_to_defaults_without_policy(self):
        from apps.standards.services import bump_active_standards_cache_version
        from apps.vaccinations.models import VaccinationRecord

        bump_active_standards_cache_version()
        params = VaccinationRecord.policy_validity_params()
        self.assertEqual(params, {"typhoid_validity_years": 3, "hepatitis_a_second_dose_months": 6})
