from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.audit.models import AuditAction, AuditLog
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
