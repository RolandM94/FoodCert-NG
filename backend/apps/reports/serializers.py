from rest_framework import serializers

from apps.reports.models import (
    AnalyticsDataset,
    DashboardExportJob,
    DashboardAlertEvent,
    DashboardAlertRule,
    AnalyticsWidget,
    AnalyticsWorksheet,
    DashboardCanvas,
    DashboardCanvasBlock,
    DashboardTemplate,
    DashboardWidget,
    DataQualityIssue,
    GeneratedReport,
    MEIndicator,
    MEIndicatorValue,
    PublishedDashboard,
    ReportFormat,
    ReportSchedule,
    ReportTemplate,
    ReportType,
    ScheduledReport,
)
from apps.reports.dataset_registry import get_dataset_allowed_fields, get_dataset_definition


MEASURE_TYPE_TOKENS = ("number", "decimal", "float", "integer", "currency", "amount", "percentage", "rate", "ratio")
VALID_ANALYTICS_AGGREGATIONS = {"sum", "count", "count_distinct", "avg", "min", "max", "percentage", "rate", "ratio", "variance"}


def _dataset_field_kind(dataset, field_name: str) -> str:
    metadata = (dataset.field_type_metadata or {}).get(field_name, {}) if dataset else {}
    field_type = str(metadata.get("type") or (dataset.field_types or {}).get(field_name) or "").lower()
    if any(token in field_type for token in MEASURE_TYPE_TOKENS):
        return "measure"
    lower = field_name.lower()
    if lower.endswith("_id") or "identifier" in lower or "code" in lower or "number" in lower:
        return "dimension"
    return "dimension"


def _is_time_dimension(field_name: str) -> bool:
    lower = field_name.lower()
    return any(token in lower for token in ("date", "month", "quarter", "week", "day", "year", "period"))


def _is_geo_dimension(field_name: str) -> bool:
    lower = field_name.lower()
    return any(token in lower for token in ("state", "lga", "ward", "location", "country"))


class DashboardQuerySerializer(serializers.Serializer):
    employer = serializers.UUIDField(required=False)
    branch = serializers.UUIDField(required=False)
    facility = serializers.UUIDField(required=False)
    department = serializers.UUIDField(required=False)
    state = serializers.UUIDField(required=False)
    lga = serializers.UUIDField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    employer_category = serializers.CharField(required=False, allow_blank=True)
    food_handler_category = serializers.CharField(required=False, allow_blank=True)
    certificate_status = serializers.CharField(required=False, allow_blank=True)
    doctor = serializers.UUIDField(required=False)
    lab_status = serializers.CharField(required=False, allow_blank=True)
    assessment_status = serializers.CharField(required=False, allow_blank=True)


class AnalyticsQuerySerializer(serializers.Serializer):
    state = serializers.UUIDField(required=False)
    lga = serializers.UUIDField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    employer_category = serializers.CharField(required=False, allow_blank=True)
    facility_type = serializers.CharField(required=False, allow_blank=True)


class MECalculationSerializer(serializers.Serializer):
    indicator = serializers.UUIDField(required=False)
    category = serializers.CharField(required=False, allow_blank=True)
    state = serializers.UUIDField(required=False)
    lga = serializers.UUIDField(required=False)
    period_start = serializers.DateField(required=False)
    period_end = serializers.DateField(required=False)


class ReportReviewActionSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True)


class ReportScheduleSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = ReportSchedule
        fields = (
            "id",
            "report_type",
            "frequency",
            "filters",
            "recipients",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_by_name", "created_at", "updated_at")


class ScheduledReportSerializer(serializers.ModelSerializer):
    report_template_code = serializers.CharField(source="report_template.code", read_only=True)
    report_template_name = serializers.CharField(source="report_template.name", read_only=True)
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)

    class Meta:
        model = ScheduledReport
        fields = (
            "id",
            "report_template",
            "report_template_code",
            "report_template_name",
            "owner",
            "owner_name",
            "name",
            "schedule_frequency",
            "filters",
            "output_format",
            "delivery_channels",
            "recipients",
            "is_active",
            "last_run_at",
            "next_run_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "report_template_code", "report_template_name", "owner", "owner_name", "last_run_at", "created_at", "updated_at")


class ReportTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = ReportTemplate
        fields = (
            "id",
            "code",
            "name",
            "description",
            "module",
            "scope",
            "output_formats",
            "default_filters",
            "required_permissions",
            "privacy_level",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_by_name", "created_at", "updated_at")


class MEIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MEIndicator
        fields = (
            "id",
            "code",
            "name",
            "description",
            "category",
            "numerator_definition",
            "denominator_definition",
            "formula",
            "data_sources",
            "reporting_frequency",
            "disaggregation_fields",
            "target_value",
            "warning_threshold",
            "critical_threshold",
            "visualization_type",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class MEIndicatorValueSerializer(serializers.ModelSerializer):
    indicator_code = serializers.CharField(source="indicator.code", read_only=True)
    indicator_name = serializers.CharField(source="indicator.name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = MEIndicatorValue
        fields = (
            "id",
            "indicator",
            "indicator_code",
            "indicator_name",
            "state",
            "state_name",
            "lga",
            "lga_name",
            "organization",
            "organization_name",
            "period_start",
            "period_end",
            "numerator_value",
            "denominator_value",
            "calculated_value",
            "disaggregation",
            "calculated_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "indicator_code", "indicator_name", "state_name", "lga_name", "organization_name", "calculated_at", "created_at", "updated_at")


class DashboardWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = (
            "id",
            "code",
            "name",
            "dashboard_scope",
            "widget_type",
            "metric_code",
            "configuration",
            "required_permissions",
            "sort_order",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AnalyticsDatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsDataset
        fields = (
            "id",
            "code",
            "name",
            "description",
            "module_source",
            "allowed_account_types",
            "allowed_roles",
            "available_fields",
            "field_labels",
            "field_types",
            "field_type_metadata",
            "sensitive_fields",
            "default_filters",
            "joinable_datasets",
            "aggregation_rules",
            "required_permissions",
            "privacy_level",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AnalyticsWorksheetSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)
    dataset_code = serializers.CharField(source="dataset.code", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)

    class Meta:
        model = AnalyticsWorksheet
        fields = (
            "id",
            "owner",
            "owner_name",
            "organization",
            "organization_name",
            "state",
            "state_name",
            "account_type",
            "scope_type",
            "name",
            "description",
            "dataset",
            "dataset_code",
            "metrics",
            "dimensions",
            "filters",
            "aggregations",
            "derived_fields",
            "query_rules",
            "chart_recommendation",
            "preview_output",
            "required_permissions",
            "privacy_metadata",
            "is_active",
            "is_template",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "owner", "owner_name", "organization_name", "state_name", "dataset_code", "created_at", "updated_at")
        extra_kwargs = {
            "account_type": {"required": False},
            "organization": {"required": False, "allow_null": True},
            "state": {"required": False, "allow_null": True},
        }

    def validate(self, attrs):
        request = self.context.get("request")
        if request is not None and not attrs.get("account_type"):
            user_role = getattr(request.user, "role", "")
            role_to_account_type = {
                "super_admin": "platform_admin",
                "federal_admin": "federal",
                "state_admin": "state",
                "employer": "employer",
                "facility_admin": "medical_facility",
            }
            attrs["account_type"] = role_to_account_type.get(user_role, attrs.get("account_type"))
        dataset = attrs.get("dataset", getattr(self.instance, "dataset", None))
        if not dataset:
            return attrs
        definition = get_dataset_definition(dataset.code)
        if definition is None:
            raise serializers.ValidationError({"dataset": "Selected dataset is not registered for analytics worksheets."})
        allowed_fields = get_dataset_allowed_fields(definition)
        sensitive_fields = set(dataset.sensitive_fields or [])

        def check_entries(key: str, entries: list[dict], field_key: str = "field"):
            errors = []
            for index, entry in enumerate(entries):
                field_name = entry.get(field_key)
                if not field_name:
                    continue
                if field_name not in allowed_fields:
                    errors.append(f"{key}[{index}] uses unsupported field '{field_name}'.")
                if field_name in sensitive_fields:
                    errors.append(f"{key}[{index}] cannot use sensitive field '{field_name}'.")
            return errors

        metrics = attrs.get("metrics", getattr(self.instance, "metrics", [])) or []
        dimensions = attrs.get("dimensions", getattr(self.instance, "dimensions", [])) or []
        filters = attrs.get("filters", getattr(self.instance, "filters", [])) or []
        chart_recommendation = attrs.get("chart_recommendation", getattr(self.instance, "chart_recommendation", "")) or "table"

        problems = []
        problems.extend(check_entries("metrics", metrics))
        problems.extend(check_entries("dimensions", dimensions))
        problems.extend(check_entries("filters", filters))
        problems.extend(check_entries("derived_fields", attrs.get("derived_fields", getattr(self.instance, "derived_fields", [])) or [], field_key="source_field"))

        for index, metric in enumerate(metrics):
            field_name = metric.get("field")
            aggregation = str(metric.get("aggregation") or "count").lower()
            if aggregation not in VALID_ANALYTICS_AGGREGATIONS:
                problems.append(f"metrics[{index}] uses unsupported aggregation '{aggregation}'.")
            if field_name and _dataset_field_kind(dataset, field_name) != "measure":
                problems.append(f"metrics[{index}] field '{field_name}' is a dimension and cannot be aggregated as a measure.")

        for index, dimension in enumerate(dimensions):
            field_name = dimension.get("field")
            if field_name and _dataset_field_kind(dataset, field_name) != "dimension":
                problems.append(f"dimensions[{index}] field '{field_name}' is a measure and cannot be used as a grouping dimension.")

        normalized_chart = "kpi" if chart_recommendation == "kpi_card" else chart_recommendation
        time_dimensions = [item.get("field") for item in dimensions if item.get("field") and _is_time_dimension(item["field"])]
        geo_dimensions = [item.get("field") for item in dimensions if item.get("field") and _is_geo_dimension(item["field"])]
        if normalized_chart == "kpi" and len(metrics) != 1:
            problems.append("KPI cards should use one primary measure.")
        if normalized_chart == "bar" and (len(dimensions) < 1 or len(metrics) < 1):
            problems.append("Bar charts require one dimension and one measure.")
        if normalized_chart == "grouped_bar" and (len(dimensions) < 2 or len(metrics) < 1):
            problems.append("Grouped bar charts require a primary dimension, a secondary dimension, and one measure.")
        if normalized_chart == "line":
            if not time_dimensions:
                problems.append("Line charts require a time-based dimension such as Month, Quarter, Year, Issue Date, Test Date, or Inspection Date.")
            if not metrics:
                problems.append("Line charts require at least one measure.")
        if normalized_chart == "map":
            if not geo_dimensions:
                problems.append("Map charts require a geographic dimension such as State, LGA, Ward, or Facility Location.")
            if not metrics:
                problems.append("Map charts require one measure.")
        if normalized_chart in {"pie", "donut"} and (len(dimensions) != 1 or len(metrics) != 1):
            problems.append("Pie and donut charts require one dimension and one measure.")

        if problems:
            raise serializers.ValidationError({"worksheet": problems})
        return attrs


class AnalyticsWidgetSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)
    worksheet_name = serializers.CharField(source="worksheet.name", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)

    def validate(self, attrs):
        worksheet = attrs.get("worksheet", getattr(self.instance, "worksheet", None))
        widget_type = attrs.get("widget_type", getattr(self.instance, "widget_type", ""))
        allowed_widget_types = {
            "kpi_card",
            "grouped_kpi",
            "bar_chart",
            "line_chart",
            "table",
            "map",
            "queue_card",
            "ai_insight",
        }
        if widget_type not in allowed_widget_types:
            raise serializers.ValidationError({"widget_type": "Unsupported widget type."})
        if worksheet is None:
            raise serializers.ValidationError({"worksheet": "Worksheet is required."})
        return attrs

    class Meta:
        model = AnalyticsWidget
        fields = (
            "id",
            "owner",
            "owner_name",
            "organization",
            "organization_name",
            "state",
            "state_name",
            "account_type",
            "scope_type",
            "worksheet",
            "worksheet_name",
            "title",
            "widget_type",
            "visual_config",
            "filter_behavior",
            "refresh_behavior",
            "export_options",
            "required_permissions",
            "privacy_metadata",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "owner", "owner_name", "organization_name", "state_name", "worksheet_name", "created_at", "updated_at")


class DashboardAlertRuleSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)
    widget_title = serializers.CharField(source="widget.title", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)

    def validate(self, attrs):
        widget = attrs.get("widget", getattr(self.instance, "widget", None))
        if widget is None:
            raise serializers.ValidationError({"widget": "Widget is required."})
        channels = attrs.get("notification_channels", getattr(self.instance, "notification_channels", [])) or []
        if not isinstance(channels, list) or not all(isinstance(item, str) for item in channels):
            raise serializers.ValidationError({"notification_channels": "Notification channels must be a list of channel codes."})
        recipient_user_ids = attrs.get("recipient_user_ids", getattr(self.instance, "recipient_user_ids", [])) or []
        if not isinstance(recipient_user_ids, list):
            raise serializers.ValidationError({"recipient_user_ids": "Recipient user ids must be a list."})
        return attrs

    class Meta:
        model = DashboardAlertRule
        fields = (
            "id",
            "owner",
            "owner_name",
            "organization",
            "organization_name",
            "state",
            "state_name",
            "account_type",
            "scope_type",
            "widget",
            "widget_title",
            "name",
            "description",
            "metric_key",
            "metric_label",
            "operator",
            "threshold_value",
            "notification_channels",
            "recipient_user_ids",
            "required_permissions",
            "privacy_metadata",
            "last_evaluated_at",
            "last_triggered_at",
            "trigger_count",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "owner",
            "owner_name",
            "organization_name",
            "state_name",
            "widget_title",
            "last_evaluated_at",
            "last_triggered_at",
            "trigger_count",
            "created_at",
            "updated_at",
        )


class DashboardAlertEventSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source="rule.name", read_only=True)
    widget_title = serializers.CharField(source="widget.title", read_only=True)

    class Meta:
        model = DashboardAlertEvent
        fields = (
            "id",
            "rule",
            "rule_name",
            "widget",
            "widget_title",
            "status",
            "observed_value",
            "threshold_value",
            "notification_count",
            "notified_channels",
            "message",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class DashboardExportJobSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)
    published_dashboard_label = serializers.CharField(source="published_dashboard.version_label", read_only=True)

    class Meta:
        model = DashboardExportJob
        fields = (
            "id",
            "owner",
            "owner_name",
            "published_dashboard",
            "published_dashboard_label",
            "block_id",
            "export_format",
            "status",
            "payload",
            "error_message",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class DashboardCanvasSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)

    class Meta:
        model = DashboardCanvas
        fields = (
            "id",
            "owner",
            "owner_name",
            "organization",
            "organization_name",
            "state",
            "state_name",
            "account_type",
            "scope_type",
            "name",
            "description",
            "layout_config",
            "global_filters",
            "required_permissions",
            "privacy_metadata",
            "is_draft",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "owner", "owner_name", "organization_name", "state_name", "created_at", "updated_at")


class DashboardCanvasBlockSerializer(serializers.ModelSerializer):
    canvas_name = serializers.CharField(source="canvas.name", read_only=True)
    widget_title = serializers.CharField(source="widget.title", read_only=True)

    class Meta:
        model = DashboardCanvasBlock
        fields = (
            "id",
            "canvas",
            "canvas_name",
            "widget",
            "widget_title",
            "block_type",
            "title",
            "content",
            "position",
            "visibility_rules",
            "required_permissions",
            "privacy_metadata",
            "sort_order",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "canvas_name", "widget_title", "created_at", "updated_at")


class DashboardPublishSerializer(serializers.Serializer):
    version_label = serializers.CharField(required=False, allow_blank=True, max_length=64)
    visibility_scope = serializers.ChoiceField(
        choices=(
            "private",
            "organization",
            "role_based",
            "selected_users",
            "federal_only",
            "state_only",
            "public",
        )
    )
    share_settings = serializers.JSONField(required=False)

    def validate_share_settings(self, value):
        if value in (None, ""):
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("Share settings must be a JSON object.")
        for key in ("allowed_roles", "user_ids", "organization_ids", "state_ids"):
            if key in value and not isinstance(value[key], list):
                raise serializers.ValidationError(f"{key} must be a list.")
        return value


class PublishedDashboardExportSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=("pdf", "png", "csv", "xlsx", "json"))
    block_id = serializers.UUIDField(required=False)


class PublishedDashboardShareEventSerializer(serializers.Serializer):
    event = serializers.ChoiceField(choices=("link_copied", "share_viewed"))


class PublishedDashboardSharingSerializer(serializers.Serializer):
    visibility_scope = serializers.ChoiceField(
        choices=(
            "private",
            "organization",
            "role_based",
            "selected_users",
            "federal_only",
            "state_only",
            "public",
        ),
        required=False,
    )
    share_settings = serializers.JSONField(required=False)

    def validate_share_settings(self, value):
        if value in (None, ""):
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("Share settings must be a JSON object.")
        for key in ("allowed_roles", "user_ids", "organization_ids", "state_ids"):
            if key in value and not isinstance(value[key], list):
                raise serializers.ValidationError(f"{key} must be a list.")
        return value


class AIWorksheetGenerateSerializer(serializers.Serializer):
    dataset = serializers.UUIDField(required=False)
    prompt = serializers.CharField()


class AIWidgetGenerateSerializer(serializers.Serializer):
    worksheet = serializers.UUIDField()
    prompt = serializers.CharField()


class AIDashboardGenerateSerializer(serializers.Serializer):
    prompt = serializers.CharField()
    widget_ids = serializers.ListField(child=serializers.UUIDField(), required=False)


class AIDashboardFullGenerateSerializer(serializers.Serializer):
    prompt = serializers.CharField()


class AIExplainSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=False, allow_blank=True)
    widget = serializers.UUIDField(required=False)
    canvas = serializers.UUIDField(required=False)


class PublishedDashboardSerializer(serializers.ModelSerializer):
    canvas_name = serializers.CharField(source="canvas.name", read_only=True)
    published_by_name = serializers.CharField(source="published_by.get_full_name", read_only=True)

    class Meta:
        model = PublishedDashboard
        fields = (
            "id",
            "canvas",
            "canvas_name",
            "published_by",
            "published_by_name",
            "version_label",
            "visibility_scope",
            "share_settings",
            "snapshot",
            "published_at",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "canvas_name", "published_by", "published_by_name", "published_at", "created_at", "updated_at")


class DashboardTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    source_canvas_name = serializers.CharField(source="source_canvas.name", read_only=True)
    source_published_dashboard_label = serializers.CharField(source="source_published_dashboard.version_label", read_only=True)

    class Meta:
        model = DashboardTemplate
        fields = (
            "id",
            "name",
            "description",
            "account_type",
            "scope_type",
            "source_canvas",
            "source_canvas_name",
            "source_published_dashboard",
            "source_published_dashboard_label",
            "template_config",
            "required_permissions",
            "privacy_metadata",
            "is_system_template",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "source_canvas_name",
            "source_published_dashboard_label",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        )


class DataQualityIssueSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)
    resolved_by_name = serializers.CharField(source="resolved_by.get_full_name", read_only=True)

    class Meta:
        model = DataQualityIssue
        fields = (
            "id",
            "issue_type",
            "severity",
            "module",
            "target_type",
            "target_id",
            "state",
            "state_name",
            "organization",
            "organization_name",
            "description",
            "status",
            "assigned_to",
            "assigned_to_name",
            "resolved_by",
            "resolved_by_name",
            "resolved_at",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "state_name", "organization_name", "assigned_to_name", "resolved_by_name", "created_at", "updated_at")


class GeneratedReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source="generated_by.get_full_name", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)

    class Meta:
        model = GeneratedReport
        fields = (
            "id",
            "title",
            "report_type",
            "organization",
            "organization_name",
            "state",
            "state_name",
            "reporting_period_start",
            "reporting_period_end",
            "file_format",
            "filters",
            "summary",
            "data_snapshot",
            "file_url",
            "status",
            "generated_by",
            "generated_by_name",
            "schedule",
            "failure_reason",
            "error_message",
            "submitted_to_federal_at",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "review_status",
            "review_comment",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class GenerateReportSerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(choices=ReportFormat.choices, default=ReportFormat.JSON, required=False)
    filters = serializers.JSONField(required=False)


class ReportTypePathSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=ReportType.choices)
