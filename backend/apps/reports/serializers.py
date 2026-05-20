from rest_framework import serializers

from apps.reports.models import GeneratedReport, ReportFormat, ReportSchedule, ReportType


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


class GeneratedReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source="generated_by.get_full_name", read_only=True)

    class Meta:
        model = GeneratedReport
        fields = (
            "id",
            "report_type",
            "file_format",
            "filters",
            "summary",
            "file_url",
            "status",
            "generated_by",
            "generated_by_name",
            "schedule",
            "failure_reason",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class GenerateReportSerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(choices=ReportFormat.choices, default=ReportFormat.JSON, required=False)
    filters = serializers.JSONField(required=False)


class ReportTypePathSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=ReportType.choices)
