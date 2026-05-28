from rest_framework import serializers

from apps.reports.models import (
    DashboardWidget,
    DataQualityIssue,
    GeneratedReport,
    MEIndicator,
    MEIndicatorValue,
    ReportFormat,
    ReportSchedule,
    ReportTemplate,
    ReportType,
    ScheduledReport,
)


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
