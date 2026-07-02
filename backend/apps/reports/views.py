from django.conf import settings
from decimal import Decimal, InvalidOperation
from datetime import date as date_type, datetime as datetime_type
from time import monotonic

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.http import FileResponse
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.locations.models import LGA, State
from apps.reports.models import (
    AnalyticsDataset,
    AnalyticsWidget,
    AnalyticsWorksheet,
    KpiCardDefinition,
    DashboardAlertEvent,
    DashboardAlertRule,
    DashboardCanvas,
    DashboardCanvasBlock,
    DashboardExportJob,
    DashboardTemplate,
    DashboardWidget,
    DataQualityIssue,
    GeneratedReport,
    GeneratedReportStatus,
    MEIndicator,
    PublishedDashboard,
    ReportSchedule,
    ReportTemplate,
    ReportType,
    ScheduledReport,
)
from apps.reports.dataset_registry import (
    REDACTED_VALUE,
    apply_dataset_scope,
    build_field_type_metadata,
    canonicalize_field_type,
    get_dataset_definition,
    get_dataset_worksheet_examples,
    generate_worksheet_preview,
    active_field_types_from_metadata,
    resolve_dataset_from_prompt,
    resolve_field_value,
    serialize_sample_rows,
    sync_analytics_datasets,
)
from apps.reports.serializers import (
    KpiCardDefinitionSerializer,
    AIDashboardFullGenerateSerializer,
    AIDashboardGenerateSerializer,
    AIExplainSerializer,
    AIWidgetGenerateSerializer,
    AIWorksheetGenerateSerializer,
    AnalyticsDatasetSerializer,
    DashboardPublishSerializer,
    PublishedDashboardExportSerializer,
    PublishedDashboardShareEventSerializer,
    PublishedDashboardSharingSerializer,
    AnalyticsWidgetSerializer,
    AnalyticsWorksheetSerializer,
    DashboardAlertEventSerializer,
    DashboardAlertRuleSerializer,
    DashboardExportJobSerializer,
    AnalyticsQuerySerializer,
    DashboardCanvasBlockSerializer,
    DashboardCanvasSerializer,
    DashboardQuerySerializer,
    DashboardTemplateSerializer,
    DashboardWidgetSerializer,
    DataQualityIssueSerializer,
    GenerateReportSerializer,
    GeneratedReportSerializer,
    MECalculationSerializer,
    MEIndicatorSerializer,
    MEIndicatorValueSerializer,
    PublishedDashboardSerializer,
    ReportScheduleSerializer,
    ScheduledReportSerializer,
    ReportTemplateSerializer,
    ReportReviewActionSerializer,
)
from apps.reports.services import AnalyticsService, DashboardService, MEIndicatorService, ReportService
from apps.notifications.models import NotificationCategory, NotificationChannel, NotificationPriority
from apps.notifications.services import NotificationService


WIDGET_EXPORT_FORMATS = ["csv", "json", "png", "pdf"]
User = get_user_model()
PREVIEW_CACHE_TTL = 60 * 5
PUBLISHED_DASHBOARD_CACHE_TTL = 60 * 3
MAX_PREVIEW_ROWS = 100
DEFAULT_TABLE_PAGE_SIZE = 10
QUERY_TIMEOUT_SECONDS = 2.5
BACKGROUND_EXPORT_ROW_THRESHOLD = 50
BACKGROUND_EXPORT_BLOCK_THRESHOLD = 8
OVERRIDABLE_DATASET_FIELD_TYPES = {"string", "number_whole", "number_decimal", "date", "datetime"}
SENSITIVE_AI_TERMS = {
    "diagnosis",
    "doctor_notes",
    "lab_results",
    "nin",
    "phone",
    "email",
    "account_number",
    "bank_details",
    "secret",
    "private",
    "medical",
}


class QueryTimeoutError(APIException):
    status_code = 408
    default_detail = "The dashboard query took too long. Narrow the filters or try again."
    default_code = "dashboard_query_timeout"


def dashboard_account_type_for_user(user):
    mapping = {
        UserRole.FEDERAL_ADMIN: "federal",
        UserRole.STATE_ADMIN: "state",
        UserRole.EMPLOYER: "employer",
        UserRole.FACILITY_ADMIN: "medical_facility",
        UserRole.SUPER_ADMIN: "platform_admin",
    }
    return mapping.get(user.role, "")


def audit_reports_event(*, action, event, target=None, actor=None, request=None, metadata=None, old_value=None, new_value=None):
    log_action(
        action=action,
        actor=actor,
        target=target,
        request=request,
        metadata={"event": event, **(metadata or {})},
        old_value=old_value,
        new_value=new_value,
    )


def preview_cache_key(prefix, *parts):
    return ":".join([prefix, *[str(part) for part in parts]])


def timed_operation(func, *, timeout_message):
    started_at = monotonic()
    result = func()
    elapsed = monotonic() - started_at
    if elapsed > QUERY_TIMEOUT_SECONDS:
        raise QueryTimeoutError(timeout_message)
    return result


class DashboardArchitectureScopeMixin:
    permission_classes = [IsAuthenticated, IsActiveUser]

    def _user_account_type(self):
        return dashboard_account_type_for_user(self.request.user)

    def _scoped_queryset(self, queryset):
        if getattr(self, "swagger_fake_view", False):
            return queryset
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return queryset
        account_type = self._user_account_type()
        if hasattr(queryset.model, "account_type") and account_type:
            queryset = queryset.filter(account_type=account_type)
        if hasattr(queryset.model, "organization_id") and user.organization_id:
            queryset = queryset.filter(models.Q(organization_id=user.organization_id) | models.Q(organization__isnull=True))
        if hasattr(queryset.model, "state_id") and user.state_id:
            queryset = queryset.filter(models.Q(state_id=user.state_id) | models.Q(state__isnull=True))
        if hasattr(queryset.model, "owner_id"):
            if user.role in {UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
                return queryset
            queryset = queryset.filter(owner=user)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        defaults = {}
        if "owner" in serializer.fields:
            defaults["owner"] = user
        if "created_by" in serializer.fields:
            defaults["created_by"] = user
        if "account_type" in serializer.fields:
            defaults["account_type"] = self._user_account_type()
        if "organization" in serializer.fields and user.organization_id and not serializer.validated_data.get("organization"):
            defaults["organization_id"] = user.organization_id
        if "state" in serializer.fields and user.state_id and not serializer.validated_data.get("state"):
            defaults["state_id"] = user.state_id
        if "published_by" in serializer.fields:
            defaults["published_by"] = user
            defaults["published_at"] = timezone.now()
        serializer.save(**defaults)


def widget_preview_payload(widget_type, worksheet_preview, visual_config, title):
    metrics = worksheet_preview.get("metrics", [])
    rows = worksheet_preview.get("rows", [])
    dimensions = worksheet_preview.get("dimensions", [])
    total_available_rows = len(rows)
    chart_recommendation = worksheet_preview.get("chart_recommendation", "table")
    summary = {
        "title": title,
        "widget_type": widget_type,
        "chart_recommendation": chart_recommendation,
        "total_rows": worksheet_preview.get("total_rows", 0),
        "dimensions": dimensions,
        "pagination": {
            "page_size": DEFAULT_TABLE_PAGE_SIZE,
            "total_items": total_available_rows,
            "total_pages": max(1, (total_available_rows + DEFAULT_TABLE_PAGE_SIZE - 1) // DEFAULT_TABLE_PAGE_SIZE),
        },
    }
    if widget_type == "kpi_card":
        primary = metrics[0] if metrics else {"label": "Value", "value": worksheet_preview.get("total_rows", 0)}
        return {**summary, "cards": [primary], "rows": rows[:1]}
    if widget_type == "grouped_kpi":
        return {**summary, "cards": metrics[:4], "rows": rows[:3]}
    if widget_type in {"bar_chart", "line_chart", "map"}:
        return {
            **summary,
            "series": rows[:8],
            "x_axis": dimensions[0] if dimensions else "",
            "metrics": metrics,
            "visual_config": visual_config,
        }
    if widget_type == "queue_card":
        return {
            **summary,
            "items": rows[:MAX_PREVIEW_ROWS],
            "count_label": metrics[0]["label"] if metrics else "Queue items",
        }
    if widget_type == "ai_insight":
        top_metric = metrics[0] if metrics else {"label": "Records", "value": worksheet_preview.get("total_rows", 0)}
        insight_lines = [
            f"{top_metric['label']}: {top_metric['value']}",
            f"Preview rows available: {worksheet_preview.get('total_rows', 0)}",
            "Insights are generated only from worksheet output and saved widget configuration.",
        ]
        return {**summary, "insights": insight_lines, "metrics": metrics[:3]}
    return {
        **summary,
        "columns": list(rows[0].keys()) if rows else dimensions,
        "rows": rows[:MAX_PREVIEW_ROWS],
        "metrics": metrics,
    }


def build_published_dashboard_snapshot(canvas):
    blocks = list(
        DashboardCanvasBlock.objects.filter(canvas=canvas, is_active=True)
        .select_related("widget__worksheet")
        .order_by("sort_order", "created_at")
    )
    snapshot_blocks = []
    for block in blocks:
        widget = block.widget
        worksheet_preview = getattr(getattr(widget, "worksheet", None), "preview_output", None) if widget else None
        widget_preview = None
        if widget and worksheet_preview:
            widget_preview = widget_preview_payload(
                widget.widget_type,
                worksheet_preview,
                widget.visual_config or {},
                block.title or widget.title,
            )
        snapshot_blocks.append(
            {
                "id": str(block.id),
                "widget_id": str(widget.id) if widget else None,
                "widget_title": widget.title if widget else "",
                "block_type": block.block_type,
                "title": block.title,
                "content": block.content or {},
                "position": block.position or {},
                "visibility_rules": block.visibility_rules or {},
                "required_permissions": block.required_permissions or [],
                "preview": widget_preview,
                "widget_type": widget.widget_type if widget else "",
                "export_options": widget.export_options if widget else {},
            }
        )
    return {
        "canvas": {
            "id": str(canvas.id),
            "name": canvas.name,
            "description": canvas.description,
            "layout_config": canvas.layout_config or {},
            "global_filters": canvas.global_filters or [],
            "scope_type": canvas.scope_type,
        },
        "blocks": snapshot_blocks,
    }


def published_dashboard_is_accessible(dashboard, user):
    if user.role == UserRole.SUPER_ADMIN:
        return True

    canvas = dashboard.canvas
    visibility_scope = dashboard.visibility_scope
    share_settings = dashboard.share_settings or {}
    allowed_roles = set(share_settings.get("allowed_roles", []) or [])
    allowed_user_ids = {str(item) for item in share_settings.get("user_ids", []) or []}
    allowed_organization_ids = {str(item) for item in share_settings.get("organization_ids", []) or []}
    allowed_state_ids = {str(item) for item in share_settings.get("state_ids", []) or []}

    if canvas.owner_id == user.id:
        return True
    if str(user.id) in allowed_user_ids:
        return True
    if user.role in allowed_roles:
        return True
    if user.organization_id and str(user.organization_id) in allowed_organization_ids:
        return True
    if user.state_id and str(user.state_id) in allowed_state_ids:
        return True

    if visibility_scope == "public":
        return True
    if visibility_scope == "private":
        return user.role in {UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}
    if visibility_scope == "organization":
        return bool(user.organization_id and canvas.organization_id and user.organization_id == canvas.organization_id)
    if visibility_scope == "role_based":
        return user.role in allowed_roles
    if visibility_scope == "selected_users":
        return str(user.id) in allowed_user_ids
    if visibility_scope == "federal_only":
        return user.role in {UserRole.FEDERAL_ADMIN, UserRole.SUPER_ADMIN}
    if visibility_scope == "state_only":
        return bool(user.state_id and canvas.state_id and user.state_id == canvas.state_id)
    return False


def published_dashboard_export_enabled(dashboard):
    share_settings = dashboard.share_settings or {}
    return share_settings.get("allow_export", True) is not False


def _sanitize_export_value(value, sensitive_fields):
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            key_name = str(key)
            if key_name in sensitive_fields:
                sanitized[key_name] = REDACTED_VALUE
                continue
            sanitized[key_name] = _sanitize_export_value(item, sensitive_fields)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_export_value(item, sensitive_fields) for item in value]
    return value


def build_published_dashboard_export_payload(dashboard, export_format, block_id=None):
    block_lookup = {
        str(block.id): block
        for block in dashboard.canvas.blocks.select_related("widget__worksheet__dataset").all()
    }
    snapshot_lookup = {
        str(block.get("id")): block
        for block in (dashboard.snapshot or {}).get("blocks", [])
        if block.get("id")
    }

    if block_id:
        block_key = str(block_id)
        canvas_block = block_lookup.get(block_key)
        snapshot_block = snapshot_lookup.get(block_key)
        if canvas_block is None or snapshot_block is None:
            raise NotFound("Requested dashboard block is not available in this published snapshot.")
        if snapshot_block.get("block_type") != "widget":
            raise PermissionDenied("Only widget blocks can be exported individually.")
        export_options = snapshot_block.get("export_options") or {}
        if export_options.get(export_format, True) is False:
            raise PermissionDenied("This widget does not allow that export format.")

        dataset = getattr(getattr(getattr(canvas_block.widget, "worksheet", None), "dataset", None), "sensitive_fields", []) or []
        sensitive_fields = {str(field) for field in dataset}
        preview = _sanitize_export_value(snapshot_block.get("preview") or {}, sensitive_fields)
        filename_root = (snapshot_block.get("title") or canvas_block.title or "dashboard-widget").strip()
        return {
            "target": "widget",
            "title": snapshot_block.get("title") or canvas_block.title,
            "filename": f"{filename_root.lower().replace(' ', '-')}.{export_format}",
            "payload": preview,
        }

    snapshot = dashboard.snapshot or {}
    sanitized_blocks = []
    for snapshot_block in snapshot.get("blocks", []):
        block_key = str(snapshot_block.get("id") or "")
        canvas_block = block_lookup.get(block_key)
        dataset = getattr(getattr(getattr(getattr(canvas_block, "widget", None), "worksheet", None), "dataset", None), "sensitive_fields", []) or []
        sensitive_fields = {str(field) for field in dataset}
        sanitized_blocks.append(_sanitize_export_value(snapshot_block, sensitive_fields))
    filename_root = (snapshot.get("canvas", {}).get("name") or dashboard.canvas.name or "published-dashboard").strip()
    return {
        "target": "dashboard",
        "title": snapshot.get("canvas", {}).get("name") or dashboard.canvas.name,
        "filename": f"{filename_root.lower().replace(' ', '-')}.{export_format}",
        "payload": {"canvas": snapshot.get("canvas", {}), "blocks": sanitized_blocks},
    }


def resolve_alert_metric_value(widget, metric_key):
    worksheet_preview = getattr(widget.worksheet, "preview_output", {}) or {}
    if metric_key == "total_rows":
        return Decimal(str(worksheet_preview.get("total_rows") or 0))
    metrics = worksheet_preview.get("metrics") or []
    if metric_key.startswith("metric:"):
        field_name = metric_key.split(":", 1)[1]
        metric = next((item for item in metrics if str(item.get("field") or "") == field_name), None)
    elif metric_key.startswith("label:"):
        label = metric_key.split(":", 1)[1]
        metric = next((item for item in metrics if str(item.get("label") or "") == label), None)
    else:
        metric = next((item for item in metrics if str(item.get("field") or item.get("label") or "") == metric_key), None)
    if metric is None:
        return None
    try:
        return Decimal(str(metric.get("value")))
    except (InvalidOperation, TypeError, ValueError):
        return None


def evaluate_operator(observed_value, operator, threshold_value):
    if observed_value is None:
        return False
    if operator == "gt":
        return observed_value > threshold_value
    if operator == "gte":
        return observed_value >= threshold_value
    if operator == "lt":
        return observed_value < threshold_value
    if operator == "lte":
        return observed_value <= threshold_value
    if operator == "eq":
        return observed_value == threshold_value
    if operator == "neq":
        return observed_value != threshold_value
    return False


def _scoped_alert_recipient_queryset(rule):
    queryset = User.objects.filter(is_active=True)
    if rule.organization_id:
        queryset = queryset.filter(organization_id=rule.organization_id)
    if rule.state_id:
        queryset = queryset.filter(state_id=rule.state_id)
    if rule.recipient_user_ids:
        queryset = queryset.filter(models.Q(id=rule.owner_id) | models.Q(id__in=rule.recipient_user_ids)).distinct()
    elif rule.scope_type == "private":
        queryset = queryset.filter(id=rule.owner_id)
    else:
        queryset = queryset.filter(id=rule.owner_id)
    return queryset


def build_alert_recipients(rule):
    recipients = []
    for user in _scoped_alert_recipient_queryset(rule):
        recipients.append(
            {
                "user_id": str(user.id),
                "email": getattr(user, "email", ""),
                "phone": getattr(user, "phone", ""),
                "recipient_type": getattr(user, "role", ""),
                "organization_id": str(user.organization_id) if getattr(user, "organization_id", None) else None,
                "organization_unit_id": None,
            }
        )
    return recipients


def evaluate_dashboard_alert_rule(rule, *, actor=None):
    observed_value = resolve_alert_metric_value(rule.widget, rule.metric_key)
    rule.last_evaluated_at = timezone.now()
    rule.save(update_fields=["last_evaluated_at", "updated_at"])

    if observed_value is None:
        return DashboardAlertEvent.objects.create(
            rule=rule,
            widget=rule.widget,
            status="no_data",
            threshold_value=rule.threshold_value,
            notification_count=0,
            notified_channels=[],
            message=f"No numeric value is available yet for {rule.metric_label or rule.metric_key}.",
            metadata={"metric_key": rule.metric_key},
        )

    triggered = evaluate_operator(observed_value, rule.operator, rule.threshold_value)
    status_value = "triggered" if triggered else "resolved"
    channels = [channel for channel in (rule.notification_channels or []) if channel in NotificationChannel.values] or [NotificationChannel.IN_APP]
    notification_count = 0
    if triggered:
        recipients = build_alert_recipients(rule)
        if recipients:
            notifications = NotificationService.send(
                category=NotificationCategory.REPORTS,
                priority=NotificationPriority.HIGH,
                title=rule.name,
                message=(
                    f"{rule.widget.title}: {rule.metric_label or rule.metric_key} is {observed_value} "
                    f"and matched alert condition {rule.operator} {rule.threshold_value}."
                ),
                action_url="",
                recipients=recipients,
                channels=channels,
                related_object_type="DashboardAlertRule",
                related_object_id=str(rule.id),
            )
            notification_count = len(notifications)
        rule.last_triggered_at = timezone.now()
        rule.trigger_count += 1
        rule.save(update_fields=["last_triggered_at", "trigger_count", "updated_at"])

    event = DashboardAlertEvent.objects.create(
        rule=rule,
        widget=rule.widget,
        status=status_value,
        observed_value=observed_value,
        threshold_value=rule.threshold_value,
        notification_count=notification_count,
        notified_channels=channels if triggered else [],
        message=(
            f"Triggered alert for {rule.metric_label or rule.metric_key}."
            if triggered
            else f"No alert triggered for {rule.metric_label or rule.metric_key}."
        ),
        metadata={"metric_key": rule.metric_key, "operator": rule.operator},
    )
    log_action(
        action=AuditAction.UPDATE,
        actor=actor,
        target=rule,
        metadata={
            "event": "dashboard_alert_evaluated",
            "status": status_value,
            "observed_value": str(observed_value),
        },
    )
    return event


def _slug_words(text):
    return [part.strip().lower() for part in text.replace("/", " ").replace("-", " ").split() if part.strip()]


def assert_ai_prompt_safe(prompt, sensitive_fields=None, *, actor=None, request=None, target=None, context="analytics_ai_request"):
    prompt_words = set(_slug_words(prompt))
    sensitive_fields = sensitive_fields or []
    for field in sensitive_fields:
        field_words = set(_slug_words(str(field)))
        if field_words and field_words.issubset(prompt_words):
            audit_reports_event(
                action=AuditAction.SECURITY_EVENT,
                event=f"{context}_blocked",
                target=target,
                actor=actor,
                request=request,
                metadata={"reason": f"sensitive_field:{field}", "prompt": prompt[:200]},
            )
            raise PermissionDenied(f"AI assistance cannot be used to request sensitive field '{field}'.")
    if prompt_words & SENSITIVE_AI_TERMS:
        audit_reports_event(
            action=AuditAction.SECURITY_EVENT,
            event=f"{context}_blocked",
            target=target,
            actor=actor,
            request=request,
            metadata={"reason": "sensitive_terms", "prompt": prompt[:200]},
        )
        raise PermissionDenied("AI assistance cannot be used to request restricted or sensitive data.")


def widget_sensitive_fields(widget):
    return getattr(getattr(getattr(widget, "worksheet", None), "dataset", None), "sensitive_fields", []) or []


def canvas_sensitive_fields(canvas):
    fields = set()
    for block in canvas.blocks.select_related("widget__worksheet__dataset").all():
        if block.widget:
            fields.update(str(field) for field in widget_sensitive_fields(block.widget))
    return sorted(fields)


def large_export_requested(dashboard, export_format, block_id=None):
    if export_format not in {"csv", "json", "xlsx"}:
        return False
    if block_id:
        snapshot_block = next((block for block in (dashboard.snapshot or {}).get("blocks", []) if str(block.get("id")) == str(block_id)), None)
        preview = snapshot_block.get("preview") if snapshot_block else {}
        row_count = len((preview or {}).get("rows", []) or [])
        return row_count > BACKGROUND_EXPORT_ROW_THRESHOLD
    return len((dashboard.snapshot or {}).get("blocks", []) or []) > BACKGROUND_EXPORT_BLOCK_THRESHOLD


def generate_worksheet_suggestion(definition=None, dataset=None, prompt=None, account_type=None):
    if dataset is None and prompt is not None and account_type is not None:
        definition, dataset, scored = resolve_dataset_from_prompt(prompt, account_type)
        if dataset is None:
            raise NotFound("No dataset could be resolved from the prompt for the current account scope.")

    prompt_words = set(_slug_words(prompt))
    available_fields = dataset.available_fields or []
    examples = get_dataset_worksheet_examples(definition, account_type)

    selected_example = None
    for example in examples:
        example_words = set(_slug_words(example["name"]) + _slug_words(example["description"]))
        if prompt_words & example_words:
            selected_example = example
            break
    if selected_example is None and examples:
        selected_example = examples[0]

    metrics = list(selected_example["metrics"]) if selected_example else []
    dimensions = list(selected_example["dimensions"]) if selected_example else []
    filters = list(selected_example["filters"]) if selected_example else []
    chart_recommendation = selected_example["chart_recommendation"] if selected_example else "table"

    if not metrics and available_fields:
        fallback_metric = next((field for field in available_fields if field.endswith("count") or field.endswith("total")), available_fields[0])
        metrics = [{"field": fallback_metric, "aggregation": "count", "label": dataset.field_labels.get(fallback_metric, fallback_metric.replace("_", " ").title())}]
    if not dimensions:
        fallback_dimension = next((field for field in available_fields if "state" in field or "status" in field or "category" in field), "")
        dimensions = [{"field": fallback_dimension}] if fallback_dimension else []
    if "trend" in prompt_words or "monthly" in prompt_words or "quarterly" in prompt_words:
        trend_dimension = next((field for field in available_fields if "date" in field or "month" in field or "period" in field), "")
        if trend_dimension and trend_dimension not in [item["field"] for item in dimensions]:
            dimensions.append({"field": trend_dimension})
        chart_recommendation = "line"

    return {
        "name": selected_example["name"] if selected_example else f"{dataset.name} Worksheet",
        "description": selected_example["description"] if selected_example else f"AI-generated worksheet draft for {dataset.name.lower()}.",
        "dataset": str(dataset.id),
        "metrics": metrics,
        "dimensions": dimensions,
        "filters": filters,
        "aggregations": [item["aggregation"] for item in metrics],
        "derived_fields": [],
        "query_rules": {"limit": 12},
        "chart_recommendation": chart_recommendation,
        "reasoning": [
            f"Used dataset {dataset.name} because it is accessible to the current account scope.",
            "Matched prompt intent against dataset examples and available non-sensitive fields.",
            "Returned a draft only; review before saving or previewing.",
        ],
    }


def generate_widget_suggestion(worksheet, prompt):
    prompt_words = set(_slug_words(prompt))
    metrics = worksheet.metrics or []
    dimensions = worksheet.dimensions or []
    widget_type = "table"
    if "kpi" in prompt_words or "summary" in prompt_words:
        widget_type = "kpi_card" if len(metrics) <= 1 else "grouped_kpi"
    elif "map" in prompt_words or any("state" in item.get("field", "") or "lga" in item.get("field", "") for item in dimensions):
        widget_type = "map"
    elif "queue" in prompt_words:
        widget_type = "queue_card"
    elif "trend" in prompt_words or "line" in prompt_words:
        widget_type = "line_chart"
    elif "insight" in prompt_words or "explain" in prompt_words:
        widget_type = "ai_insight"
    elif metrics and dimensions:
        widget_type = "bar_chart"

    return {
        "worksheet": str(worksheet.id),
        "title": f"{worksheet.name} {widget_type.replace('_', ' ').title()}",
        "widget_type": widget_type,
        "scope_type": "private",
        "visual_config": {"color": "#16a34a", "showLegend": widget_type in {"bar_chart", "line_chart", "map"}},
        "filter_behavior": {"inherits_global_filters": True},
        "refresh_behavior": {"mode": "manual"},
        "export_options": {"csv": True, "json": True, "png": True, "pdf": True},
        "reasoning": [
            "Used worksheet shape and prompt intent to choose a fitting widget type.",
            "Kept global-filter inheritance enabled so the widget stays compatible with dashboard-wide controls.",
        ],
    }


def generate_dashboard_suggestion(widgets, prompt):
    prompt_words = set(_slug_words(prompt))
    blocks = []
    sort_order = 0

    if "summary" in prompt_words or "executive" in prompt_words:
        blocks.append(
            {
                "block_type": "text",
                "title": "Executive summary",
                "content": {"body": "AI-generated summary placeholder. Review and tailor before publishing."},
                "position": {"w": 12, "h": 220},
                "widget": None,
                "visibility_rules": {},
                "sort_order": sort_order,
            }
        )
        sort_order += 1

    compatible_filter_fields = []
    for widget in widgets:
        worksheet = widget.worksheet
        for dimension in worksheet.dimensions or []:
            field = dimension.get("field", "")
            if field and field not in compatible_filter_fields:
                compatible_filter_fields.append(field)

    if compatible_filter_fields:
        blocks.append(
            {
                "block_type": "filter",
                "title": "Global filter",
                "content": {"label": "Filter", "field": compatible_filter_fields[0], "mode": "select"},
                "position": {"w": 12, "h": 220},
                "widget": None,
                "visibility_rules": {},
                "sort_order": sort_order,
            }
        )
        sort_order += 1

    for widget in widgets:
        blocks.append(
            {
                "block_type": "widget",
                "title": widget.title,
                "content": {},
                "position": {"w": 6 if widget.widget_type not in {"table", "map", "ai_insight"} else 12, "h": 320},
                "widget": str(widget.id),
                "visibility_rules": {},
                "sort_order": sort_order,
            }
        )
        sort_order += 1

    if "insight" in prompt_words or any(widget.widget_type == "ai_insight" for widget in widgets):
        blocks.append(
            {
                "block_type": "ai_insight",
                "title": "AI insight",
                "content": {"prompt": "Highlight anomalies, trends, and follow-up actions for this dashboard section."},
                "position": {"w": 12, "h": 220},
                "widget": None,
                "visibility_rules": {},
                "sort_order": sort_order,
            }
        )

    return {
        "name": "AI-generated dashboard canvas",
        "description": "Draft dashboard arrangement proposed from the selected widgets and prompt.",
        "layout_config": {"columns": 12, "responsive": True},
        "global_filters": [{"label": "Filter", "field": compatible_filter_fields[0], "mode": "select"}] if compatible_filter_fields else [],
        "blocks": blocks,
        "reasoning": [
            "Placed filters first so compatible widgets can respond to the same control.",
            "Balanced widget widths for scanning while keeping tables, maps, and narrative blocks full-width.",
        ],
    }


class SyntheticWorksheet:
    def __init__(self, name, metrics, dimensions, dataset_id):
        self.name = name
        self.metrics = metrics or []
        self.dimensions = dimensions or []
        self.id = None
        self.dataset_id = dataset_id


class SyntheticWidget:
    def __init__(self, title, widget_type, worksheet):
        self.title = title
        self.widget_type = widget_type
        self.worksheet = worksheet
        self.id = None


def generate_dashboard_from_prompt(prompt, account_type):
    definition, dataset, scored = resolve_dataset_from_prompt(prompt, account_type)
    if dataset is None:
        raise NotFound("No dataset could be resolved from the prompt for the current account scope.")

    worksheet_suggestion = generate_worksheet_suggestion(
        definition=definition,
        dataset=dataset,
        prompt=prompt,
        account_type=account_type,
    )
    synthetic_worksheet = SyntheticWorksheet(
        name=worksheet_suggestion["name"],
        metrics=worksheet_suggestion["metrics"],
        dimensions=worksheet_suggestion["dimensions"],
        dataset_id=worksheet_suggestion["dataset"],
    )
    widget_suggestion = generate_widget_suggestion(synthetic_worksheet, prompt)
    synthetic_widget = SyntheticWidget(
        title=widget_suggestion["title"],
        widget_type=widget_suggestion["widget_type"],
        worksheet=synthetic_worksheet,
    )
    dashboard_suggestion = generate_dashboard_suggestion([synthetic_widget], prompt)

    return {
        **dashboard_suggestion,
        "worksheet_suggestion": worksheet_suggestion,
        "widget_suggestion": widget_suggestion,
        "resolved_dataset": {
            "id": str(dataset.id),
            "code": dataset.code,
            "name": dataset.name,
            "match_reason": scored[0].get("reason", "auto-selected") if scored else "auto-selected",
        },
    }


def explain_dashboard_artifact(prompt, widget=None, canvas=None):
    if widget is not None:
        worksheet = widget.worksheet
        return {
            "summary": f"{widget.title} uses the {worksheet.name} worksheet as its source.",
            "insights": [
                f"Widget type: {widget.widget_type.replace('_', ' ')}.",
                f"Worksheet metrics: {len(worksheet.metrics or [])}; dimensions: {len(worksheet.dimensions or [])}.",
                "Global filters remain enabled so this widget can participate in dashboard-wide controls.",
            ],
            "recommended_actions": [
                "Preview the widget after any worksheet change.",
                "Use grouped KPI or chart widgets when you need faster scanning than a table provides.",
            ],
        }
    if canvas is not None:
        blocks = list(canvas.blocks.filter(is_active=True).order_by("sort_order"))
        return {
            "summary": f"{canvas.name} currently contains {len(blocks)} active blocks.",
            "insights": [
                f"Widget blocks: {sum(1 for block in blocks if block.block_type == 'widget')}.",
                f"Filter blocks: {sum(1 for block in blocks if block.block_type == 'filter')}.",
                prompt or "Ask for a tighter executive summary, anomaly review, or layout explanation.",
            ],
            "recommended_actions": [
                "Place global filters above the most reused widgets.",
                "Publish a snapshot only after reviewing text and AI insight blocks for audience fit.",
            ],
        }
    return {
        "summary": "No widget or dashboard was selected for explanation.",
        "insights": [],
        "recommended_actions": [],
    }


DEFAULT_DASHBOARD_TEMPLATES = {
    "federal": [
        {
            "name": "National Compliance Command Center",
            "description": "Top-level federal dashboard for compliance trends, state comparison, and action follow-up.",
            "scope_type": "federal_only",
            "template_config": {
                "name": "National Compliance Command Center",
                "description": "Federal oversight view for compliance performance across states.",
                "layout_config": {"columns": 12, "responsive": True},
                "global_filters": [{"label": "State", "field": "state_name", "mode": "select"}],
                "blocks": [
                    {
                        "block_type": "text",
                        "title": "Executive summary",
                        "content": {"body": "Track national certification coverage, inspections, and reporting quality in one place."},
                        "position": {"w": 12, "h": 220},
                    },
                    {
                        "block_type": "filter",
                        "title": "State filter",
                        "content": {"label": "State", "field": "state_name", "mode": "select"},
                        "position": {"w": 12, "h": 220},
                    },
                    {
                        "block_type": "ai_insight",
                        "title": "AI federal insight",
                        "content": {"prompt": "Summarize national performance shifts, outliers, and states needing intervention."},
                        "position": {"w": 12, "h": 220},
                    },
                ],
            },
        },
        {
            "name": "Federal M&E Performance Brief",
            "description": "Template tuned for indicator monitoring, variance review, and reporting follow-up.",
            "scope_type": "federal_only",
            "template_config": {
                "name": "Federal M&E Performance Brief",
                "description": "M&E-oriented layout for indicator reviews and performance narratives.",
                "layout_config": {"columns": 12, "responsive": True},
                "global_filters": [{"label": "Reporting period", "field": "reporting_period", "mode": "segmented"}],
                "blocks": [
                    {
                        "block_type": "text",
                        "title": "Indicator summary",
                        "content": {"body": "Use this template to anchor key indicator widgets, targets, and review notes."},
                        "position": {"w": 12, "h": 220},
                    },
                    {
                        "block_type": "filter",
                        "title": "Reporting period",
                        "content": {"label": "Reporting period", "field": "reporting_period", "mode": "segmented"},
                        "position": {"w": 12, "h": 220},
                    },
                ],
            },
        },
    ],
    "state": [
        {
            "name": "State Compliance Watchlist",
            "description": "State-level monitoring layout for certificates, queues, inspections, and escalation items.",
            "scope_type": "state_only",
            "template_config": {
                "name": "State Compliance Watchlist",
                "description": "Operational state dashboard for approvals, queues, and compliance follow-up.",
                "layout_config": {"columns": 12, "responsive": True},
                "global_filters": [{"label": "LGA", "field": "lga_name", "mode": "select"}],
                "blocks": [
                    {
                        "block_type": "text",
                        "title": "State operations",
                        "content": {"body": "Track state queues, inspection output, and certificate bottlenecks."},
                        "position": {"w": 12, "h": 220},
                    },
                    {
                        "block_type": "filter",
                        "title": "LGA filter",
                        "content": {"label": "LGA", "field": "lga_name", "mode": "select"},
                        "position": {"w": 12, "h": 220},
                    },
                ],
            },
        }
    ],
    "employer": [
        {
            "name": "Employer Certification Readiness",
            "description": "Employer dashboard template for workforce compliance, expiry risk, and branch-level status.",
            "scope_type": "organization",
            "template_config": {
                "name": "Employer Certification Readiness",
                "description": "Track certificate status, workforce readiness, and branch follow-up actions.",
                "layout_config": {"columns": 12, "responsive": True},
                "global_filters": [{"label": "Branch", "field": "branch_name", "mode": "select"}],
                "blocks": [
                    {
                        "block_type": "text",
                        "title": "Employer summary",
                        "content": {"body": "Use this template to compare branches, certificate risk, and pending staff actions."},
                        "position": {"w": 12, "h": 220},
                    },
                    {
                        "block_type": "filter",
                        "title": "Branch filter",
                        "content": {"label": "Branch", "field": "branch_name", "mode": "select"},
                        "position": {"w": 12, "h": 220},
                    },
                ],
            },
        }
    ],
    "medical_facility": [
        {
            "name": "Facility Throughput Dashboard",
            "description": "Medical facility template for appointments, assessments, lab flow, and clearance follow-up.",
            "scope_type": "organization",
            "template_config": {
                "name": "Facility Throughput Dashboard",
                "description": "Monitor facility throughput from appointment to assessment completion.",
                "layout_config": {"columns": 12, "responsive": True},
                "global_filters": [{"label": "Department", "field": "department_name", "mode": "select"}],
                "blocks": [
                    {
                        "block_type": "text",
                        "title": "Facility overview",
                        "content": {"body": "Start with throughput, backlog, and quality indicators for the facility team."},
                        "position": {"w": 12, "h": 220},
                    },
                    {
                        "block_type": "filter",
                        "title": "Department filter",
                        "content": {"label": "Department", "field": "department_name", "mode": "select"},
                        "position": {"w": 12, "h": 220},
                    },
                ],
            },
        }
    ],
}


def ensure_default_dashboard_templates(account_type):
    template_defs = DEFAULT_DASHBOARD_TEMPLATES.get(account_type, [])
    for template_def in template_defs:
        DashboardTemplate.objects.get_or_create(
            account_type=account_type,
            name=template_def["name"],
            is_system_template=True,
            defaults={
                "description": template_def["description"],
                "scope_type": template_def["scope_type"],
                "template_config": template_def["template_config"],
                "required_permissions": [],
                "privacy_metadata": {},
                "is_active": True,
                "created_by": None,
            },
        )


def clone_dashboard_template_to_canvas(template, user, account_type):
    template_config = template.template_config or {}
    canvas = DashboardCanvas.objects.create(
        owner=user,
        organization_id=user.organization_id,
        state_id=user.state_id,
        account_type=account_type,
        scope_type=template.scope_type or "private",
        name=template_config.get("name") or template.name,
        description=template_config.get("description") or template.description,
        layout_config=template_config.get("layout_config") or {"columns": 12, "responsive": True},
        global_filters=template_config.get("global_filters") or [],
        is_draft=True,
        is_active=True,
    )
    blocks = template_config.get("blocks") or []
    for index, block in enumerate(blocks):
        DashboardCanvasBlock.objects.create(
            canvas=canvas,
            widget_id=block.get("widget"),
            block_type=block.get("block_type", "text"),
            title=block.get("title", ""),
            content=block.get("content", {}),
            position=block.get("position", {"w": 12, "h": 220}),
            visibility_rules=block.get("visibility_rules", {}),
            sort_order=block.get("sort_order", index),
            is_active=True,
        )
    return canvas


class EmployerDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(parameters=[DashboardQuerySerializer], responses=dict)
    def get(self, request):
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(
            DashboardService.employer_dashboard(
                request.user,
                employer_id=serializer.validated_data.get("employer"),
                branch_id=serializer.validated_data.get("branch"),
            )
        )


class FoodHandlerDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(DashboardService.food_handler_dashboard(request.user))


class DoctorDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(parameters=[DashboardQuerySerializer], responses=dict)
    def get(self, request):
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(DashboardService.doctor_dashboard(request.user, facility_id=serializer.validated_data.get("facility")))


class LabDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(parameters=[DashboardQuerySerializer], responses=dict)
    def get(self, request):
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(DashboardService.lab_dashboard(request.user, facility_id=serializer.validated_data.get("facility")))


class InspectorDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(DashboardService.inspector_dashboard(request.user))


class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(DashboardService.admin_dashboard(request.user))


class FacilityDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(parameters=[DashboardQuerySerializer], responses=dict)
    def get(self, request):
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(
            DashboardService.facility_dashboard(
                request.user,
                facility_id=serializer.validated_data.get("facility"),
                department_id=serializer.validated_data.get("department"),
                date_from=serializer.validated_data.get("date_from"),
                date_to=serializer.validated_data.get("date_to"),
                doctor_id=serializer.validated_data.get("doctor"),
                lab_status=serializer.validated_data.get("lab_status", ""),
                assessment_status=serializer.validated_data.get("assessment_status", ""),
                employer_category=serializer.validated_data.get("employer_category", ""),
            )
        )


class StateDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(parameters=[DashboardQuerySerializer], responses=dict)
    def get(self, request):
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(
            DashboardService.state_dashboard(
                request.user,
                state_id=serializer.validated_data.get("state"),
                lga_id=serializer.validated_data.get("lga"),
                facility_id=serializer.validated_data.get("facility"),
                date_from=serializer.validated_data.get("date_from"),
                date_to=serializer.validated_data.get("date_to"),
                employer_category=serializer.validated_data.get("employer_category", ""),
                food_handler_category=serializer.validated_data.get("food_handler_category", ""),
                certificate_status=serializer.validated_data.get("certificate_status", ""),
            )
        )


class FederalDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(DashboardService.federal_dashboard(request.user))


class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    service_method = None
    finance_only = False
    module_key = "analytics"
    module_label = "Analytics"
    dataset_sources = None

    @extend_schema(parameters=[AnalyticsQuerySerializer], responses=dict)
    def get(self, request):
        if self.finance_only and request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("Finance analytics require finance oversight permissions.")
        if not self.finance_only and request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            raise PermissionDenied("You cannot access analytics.")
        serializer = AnalyticsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        filters = AnalyticsService.filters_from_request(serializer.validated_data, request.user)
        payload = self.service_method(filters)
        payload["dashboard_integration"] = {
            "shared_engine": True,
            "module_key": self.module_key,
            "module_label": self.module_label,
            "dataset_sources": self.dataset_sources or [self.module_key],
            "supported_workspaces": ["worksheet_builder", "widget_builder", "canvas_builder"],
            "actions": {
                "add_to_dashboard": True,
                "open_in_dashboard_builder": True,
            },
        }
        return Response(payload)


class CertificateAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.certificate_analytics
    module_key = "certificates"
    module_label = "Certificates"


class AssessmentAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.assessment_analytics
    module_key = "assessments"
    module_label = "Assessment Standards"
    dataset_sources = ["food_handlers"]


class VaccinationAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.vaccination_analytics
    module_key = "vaccinations"
    module_label = "Vaccinations"
    dataset_sources = ["food_handlers"]


class FacilityAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.facility_analytics
    module_key = "facilities"
    module_label = "Medical Facilities"


class EmployerAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.employer_analytics
    module_key = "employers"
    module_label = "Employers"


class InspectionAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.inspection_analytics
    module_key = "inspections"
    module_label = "Inspections"


class EnforcementAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.enforcement_analytics
    module_key = "enforcement"
    module_label = "Compliance Oversight"
    dataset_sources = ["inspections"]


class IllnessAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.illness_analytics
    module_key = "illness"
    module_label = "Illness Reports"
    dataset_sources = ["food_handlers"]


class PaymentAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.payment_analytics
    finance_only = True
    module_key = "payments"
    module_label = "Payments"
    dataset_sources = ["payments"]


class SettlementAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.settlement_analytics
    finance_only = True
    module_key = "settlements"
    module_label = "Settlements"
    dataset_sources = ["payments"]


class DataQualityAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.data_quality_analytics
    module_key = "data_quality"
    module_label = "Data Quality"


class ReportGenerateView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    report_type = None

    @extend_schema(request=GenerateReportSerializer, responses={201: GeneratedReportSerializer})
    def get(self, request):
        serializer = GenerateReportSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        report = ReportService.generate(
            report_type=self.report_type,
            user=request.user,
            file_format=serializer.validated_data.get("file_format", "json"),
            filters=serializer.validated_data.get("filters", {}),
        )
        return Response(GeneratedReportSerializer(report).data)


class EmployerComplianceReportView(ReportGenerateView):
    report_type = ReportType.EMPLOYER_COMPLIANCE


class FacilityPerformanceReportView(ReportGenerateView):
    report_type = ReportType.FACILITY_PERFORMANCE


class StateMonthlyReportView(ReportGenerateView):
    report_type = ReportType.STATE_MONTHLY


class NationalReportView(ReportGenerateView):
    report_type = ReportType.NATIONAL


class VaccinationCoverageReportView(ReportGenerateView):
    report_type = ReportType.VACCINATION_COVERAGE


class IllnessTrendsReportView(ReportGenerateView):
    report_type = ReportType.ILLNESS_TRENDS


class InspectionOutcomesReportView(ReportGenerateView):
    report_type = ReportType.INSPECTION_OUTCOMES


class ReportScheduleViewSet(viewsets.ModelViewSet):
    queryset = ReportSchedule.objects.select_related("created_by").order_by("-created_at")
    serializer_class = ReportScheduleSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["report_type", "status", "frequency"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        return self.queryset.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ReportTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportTemplate.objects.select_related("created_by").order_by("scope", "name")
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["scope", "module", "privacy_level", "is_active"]
    search_fields = ["code", "name", "description", "module"]

    ROLE_SCOPES = {
        UserRole.FOOD_HANDLER: {"food_handler"},
        UserRole.EMPLOYER: {"employer"},
        UserRole.FACILITY_ADMIN: {"facility"},
        UserRole.DOCTOR: {"facility", "doctor"},
        UserRole.LAB_STAFF: {"facility", "lab"},
        UserRole.INSPECTOR: {"inspector"},
        UserRole.STATE_ADMIN: {"state"},
        UserRole.FEDERAL_ADMIN: {"federal"},
        UserRole.SUPER_ADMIN: {"admin", "federal", "state", "facility", "doctor", "lab", "inspector", "employer", "food_handler"},
    }

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return self.queryset
        scopes = self.ROLE_SCOPES.get(user.role, set())
        return self.queryset.filter(is_active=True, scope__in=scopes)

    def _ensure_super_admin(self):
        if self.request.user.role != UserRole.SUPER_ADMIN:
            raise PermissionDenied("Only super admins can manage report templates.")

    def perform_create(self, serializer):
        self._ensure_super_admin()
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        self._ensure_super_admin()
        serializer.save()

    def perform_destroy(self, instance):
        self._ensure_super_admin()
        instance.delete()


class MEIndicatorViewSet(viewsets.ModelViewSet):
    queryset = MEIndicator.objects.order_by("category", "name")
    serializer_class = MEIndicatorSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["category", "reporting_frequency", "is_active"]
    search_fields = ["code", "name", "description", "category"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        if self.request.user.role == UserRole.SUPER_ADMIN:
            return self.queryset
        return self.queryset.filter(is_active=True)

    def _ensure_super_admin(self):
        if self.request.user.role != UserRole.SUPER_ADMIN:
            raise PermissionDenied("Only super admins can manage M&E indicators.")

    def perform_create(self, serializer):
        self._ensure_super_admin()
        serializer.save()

    def perform_update(self, serializer):
        self._ensure_super_admin()
        serializer.save()

    @extend_schema(responses=MEIndicatorValueSerializer(many=True))
    @action(detail=True, methods=["get"], url_path="values")
    def values(self, request, pk=None):
        periods = int(request.query_params.get("periods", 12))
        return Response(MEIndicatorValueSerializer(MEIndicatorService.get_indicator_history(self.get_object().id, periods=periods), many=True).data)


class MECalculateView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(request=MECalculationSerializer, responses=MEIndicatorValueSerializer(many=True))
    def post(self, request):
        serializer = MECalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        state = State.objects.filter(id=serializer.validated_data.get("state")).first() if serializer.validated_data.get("state") else None
        lga = LGA.objects.filter(id=serializer.validated_data.get("lga")).first() if serializer.validated_data.get("lga") else None
        period_start = serializer.validated_data.get("period_start")
        period_end = serializer.validated_data.get("period_end")
        if serializer.validated_data.get("indicator"):
            indicator = MEIndicator.objects.get(id=serializer.validated_data["indicator"])
            values = [MEIndicatorService.calculate_indicator(indicator, state=state, lga=lga, period_start=period_start, period_end=period_end)]
        elif serializer.validated_data.get("category"):
            values = MEIndicatorService.calculate_category(serializer.validated_data["category"], state=state, period_start=period_start, period_end=period_end)
        else:
            values = MEIndicatorService.calculate_all_indicators(state=state, period_start=period_start, period_end=period_end)
        return Response(MEIndicatorValueSerializer(values, many=True).data, status=status.HTTP_201_CREATED)


class MEDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=dict)
    def get(self, request):
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("You cannot access the M&E dashboard.")
        if request.user.role == UserRole.STATE_ADMIN and request.user.state_id:
            return Response(MEIndicatorService.get_state_performance(request.user.state_id))
        return Response(MEIndicatorService.get_national_summary())


class MEStatePerformanceView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(parameters=[DashboardQuerySerializer], responses=dict)
    def get(self, request):
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        state_id = serializer.validated_data.get("state") or getattr(request.user, "state_id", None)
        if not state_id:
            raise PermissionDenied("A state is required for state performance.")
        if request.user.role == UserRole.STATE_ADMIN and str(request.user.state_id) != str(state_id):
            raise PermissionDenied("State users can only access their own state performance.")
        return Response(MEIndicatorService.get_state_performance(state_id))


class MENationalSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=dict)
    def get(self, request):
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only federal and super admin users can access national M&E summaries.")
        return Response(MEIndicatorService.get_national_summary())


class GeneratedReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GeneratedReport.objects.select_related("generated_by", "schedule", "organization", "state", "reviewed_by").order_by("-created_at")
    serializer_class = GeneratedReportSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    filterset_fields = ["report_type", "file_format", "status"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        return self.queryset.filter(generated_by=user)

    @extend_schema(responses=GeneratedReportSerializer)
    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        report = self.get_object()
        if not report.file_url:
            raise NotFound("Report file is not available.")
        relative_path = report.file_url.replace("http://localhost:8000/media/", "")
        file_path = settings.MEDIA_ROOT / relative_path
        if not file_path.exists():
            raise NotFound("Report file was not found.")
        return FileResponse(open(file_path, "rb"), as_attachment=True, filename=file_path.name)

    @extend_schema(responses=GeneratedReportSerializer)
    @action(detail=True, methods=["post"], url_path="submit-to-federal")
    def submit_to_federal(self, request, pk=None):
        return Response(GeneratedReportSerializer(ReportService.submit_to_federal(report=self.get_object(), actor=request.user)).data)

    @extend_schema(responses=GeneratedReportSerializer)
    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        return Response(GeneratedReportSerializer(ReportService.archive(report=self.get_object(), actor=request.user)).data)

    @extend_schema(responses={201: GeneratedReportSerializer})
    @action(detail=True, methods=["post"], url_path="regenerate")
    def regenerate(self, request, pk=None):
        return Response(GeneratedReportSerializer(ReportService.regenerate(report=self.get_object(), actor=request.user)).data, status=status.HTTP_201_CREATED)


class FederalStateReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GeneratedReport.objects.select_related("generated_by", "organization", "state", "reviewed_by").filter(
        state__isnull=False,
        status__in=[
            GeneratedReportStatus.SUBMITTED,
            GeneratedReportStatus.ACCEPTED,
            GeneratedReportStatus.RETURNED_FOR_CORRECTION,
        ],
    ).order_by("-submitted_to_federal_at", "-created_at")
    serializer_class = GeneratedReportSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    filterset_fields = ["report_type", "status", "state"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        if self.request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only federal users can access submitted state reports.")
        return self.queryset

    @extend_schema(request=ReportReviewActionSerializer, responses=GeneratedReportSerializer)
    @action(detail=True, methods=["post"], url_path="accept")
    def accept(self, request, pk=None):
        serializer = ReportReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = ReportService.accept_federal_report(report=self.get_object(), actor=request.user, comment=serializer.validated_data.get("comment", ""))
        return Response(GeneratedReportSerializer(report).data)

    @extend_schema(request=ReportReviewActionSerializer, responses=GeneratedReportSerializer)
    @action(detail=True, methods=["post"], url_path="return-for-correction")
    def return_for_correction(self, request, pk=None):
        serializer = ReportReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = ReportService.return_for_correction(report=self.get_object(), actor=request.user, comment=serializer.validated_data.get("comment", ""))
        return Response(GeneratedReportSerializer(report).data)

    @extend_schema(request=ReportReviewActionSerializer, responses=GeneratedReportSerializer)
    @action(detail=True, methods=["post"], url_path="escalate")
    def escalate(self, request, pk=None):
        serializer = ReportReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = ReportService.escalate_federal_report(report=self.get_object(), actor=request.user, comment=serializer.validated_data.get("comment", ""))
        return Response(GeneratedReportSerializer(report).data)


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    queryset = DashboardWidget.objects.order_by("dashboard_scope", "sort_order", "name")
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["dashboard_scope", "widget_type", "is_active"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        scope = self.request.query_params.get("dashboard_scope")
        qs = self.queryset
        if scope:
            qs = qs.filter(dashboard_scope=scope)
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return qs
        role_scopes = {
            UserRole.FOOD_HANDLER: ["food_handler"],
            UserRole.EMPLOYER: ["employer"],
            UserRole.FACILITY_ADMIN: ["facility"],
            UserRole.DOCTOR: ["doctor"],
            UserRole.LAB_STAFF: ["lab"],
            UserRole.INSPECTOR: ["inspector"],
            UserRole.STATE_ADMIN: ["state"],
            UserRole.FEDERAL_ADMIN: ["federal"],
        }
        allowed = set(role_scopes.get(user.role, []))
        return qs.filter(is_active=True, dashboard_scope__in=allowed)

    def _ensure_admin(self):
        if self.request.user.role != UserRole.SUPER_ADMIN:
            raise PermissionDenied("Only super admins can manage dashboard widgets.")

    def perform_create(self, serializer):
        self._ensure_admin()
        serializer.save()

    def perform_update(self, serializer):
        self._ensure_admin()
        serializer.save()

    def perform_destroy(self, instance):
        self._ensure_admin()
        instance.delete()


class AnalyticsDatasetViewSet(DashboardArchitectureScopeMixin, viewsets.ModelViewSet):
    queryset = AnalyticsDataset.objects.order_by("module_source", "name")
    serializer_class = AnalyticsDatasetSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["module_source", "privacy_level", "is_active"]

    def _compatibility_payload(self, dataset, definition, queryset, field_name: str, target_type: str):
        incompatible_examples = []
        incompatible_rows = 0
        empty_rows = 0
        total_rows = queryset.count()

        for instance in queryset.iterator():
            value = resolve_field_value(instance, field_name, definition.computed_fields)
            if value in (None, ""):
                empty_rows += 1
                continue
            if self._is_value_compatible_with_type(value, target_type):
                continue
            incompatible_rows += 1
            if len(incompatible_examples) < 5:
                display_value = REDACTED_VALUE if field_name in (dataset.sensitive_fields or []) else str(value)
                incompatible_examples.append(display_value)

        return {
            "field": field_name,
            "targetType": target_type,
            "totalRows": total_rows,
            "emptyRows": empty_rows,
            "compatibleRows": max(total_rows - empty_rows - incompatible_rows, 0),
            "incompatibleRows": incompatible_rows,
            "invalidExamples": incompatible_examples,
            "requiresConfirmation": incompatible_rows > 0,
        }

    def _is_value_compatible_with_type(self, value, target_type: str) -> bool:
        target_type = canonicalize_field_type(target_type)
        if target_type == "string":
            return True
        if isinstance(value, bool):
            return target_type == "string"
        if target_type in {"number_whole", "number_decimal"}:
            try:
                number = Decimal(str(value).strip())
            except (InvalidOperation, AttributeError, ValueError):
                return False
            if target_type == "number_decimal":
                return True
            return number == number.to_integral_value()
        if target_type == "date":
            if isinstance(value, datetime_type):
                return True
            if isinstance(value, date_type):
                return True
            text = str(value).strip()
            return bool(parse_date(text) or parse_datetime(text))
        if target_type == "datetime":
            if isinstance(value, datetime_type):
                return True
            text = str(value).strip()
            return bool(parse_datetime(text) or parse_date(text))
        return False

    def get_queryset(self):
        sync_analytics_datasets()
        queryset = self._scoped_queryset(self.queryset)
        if getattr(self, "swagger_fake_view", False):
            return queryset
        user = self.request.user
        account_type = self._user_account_type()
        if user.role == UserRole.SUPER_ADMIN:
            return queryset
        queryset = queryset.filter(is_active=True)
        if not account_type and user.role != UserRole.INSPECTOR:
            return queryset.none()
        allowed_ids = [
            dataset.id
            for dataset in queryset
            if (not dataset.allowed_account_types or account_type in dataset.allowed_account_types)
            and (not dataset.allowed_roles or user.role in dataset.allowed_roles)
        ]
        return queryset.filter(id__in=allowed_ids)

    @action(detail=True, methods=["get"], url_path="sample")
    def sample(self, request, pk=None):
        sync_analytics_datasets()
        dataset = self.get_object()
        definition = get_dataset_definition(dataset.code)
        if definition is None:
            raise NotFound("No dataset registry definition is available for this dataset.")
        try:
            limit = int(request.query_params.get("limit", 5))
        except (TypeError, ValueError):
            limit = 5
        limit = min(max(limit, 1), 25)
        queryset = apply_dataset_scope(definition, definition.queryset(), request.user)
        rows = serialize_sample_rows(definition, queryset, limit=limit)
        audit_reports_event(
            action=AuditAction.UPDATE,
            event="analytics_dataset_sample_viewed",
            target=dataset,
            actor=request.user,
            request=request,
            metadata={"limit": limit},
        )
        return Response(
            {
                "dataset": dataset.code,
                "name": dataset.name,
                "row_count": queryset.count(),
                "sensitive_fields": dataset.sensitive_fields,
                "rows": rows,
            }
        )

    @action(detail=True, methods=["post"], url_path="field-type-compatibility")
    def field_type_compatibility(self, request, pk=None):
        sync_analytics_datasets()
        dataset = self.get_object()
        definition = get_dataset_definition(dataset.code)
        if definition is None:
            raise NotFound("No dataset registry definition is available for this dataset.")
        field_name = str(request.data.get("field") or "").strip()
        target_type = canonicalize_field_type(request.data.get("target_type"))
        if field_name not in (dataset.available_fields or []):
            return Response({"detail": "Unknown dataset field."}, status=status.HTTP_400_BAD_REQUEST)
        if target_type not in OVERRIDABLE_DATASET_FIELD_TYPES:
            return Response({"detail": "Unsupported target field type."}, status=status.HTTP_400_BAD_REQUEST)
        queryset = apply_dataset_scope(definition, definition.queryset(), request.user)
        payload = self._compatibility_payload(dataset, definition, queryset, field_name, target_type)
        return Response(payload)

    @action(detail=True, methods=["post"], url_path="change-field-type")
    def change_field_type(self, request, pk=None):
        sync_analytics_datasets()
        dataset = self.get_object()
        definition = get_dataset_definition(dataset.code)
        if definition is None:
            raise NotFound("No dataset registry definition is available for this dataset.")
        field_name = str(request.data.get("field") or "").strip()
        target_type = canonicalize_field_type(request.data.get("target_type"))
        force = bool(request.data.get("force"))
        if field_name not in (dataset.available_fields or []):
            return Response({"detail": "Unknown dataset field."}, status=status.HTTP_400_BAD_REQUEST)
        if target_type not in OVERRIDABLE_DATASET_FIELD_TYPES:
            return Response({"detail": "Unsupported target field type."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = apply_dataset_scope(definition, definition.queryset(), request.user)
        compatibility = self._compatibility_payload(dataset, definition, queryset, field_name, target_type)
        if compatibility["requiresConfirmation"] and not force:
            return Response(
                {
                    "detail": "Incompatible dataset values were found. Confirm to continue.",
                    "compatibility": compatibility,
                },
                status=status.HTTP_409_CONFLICT,
            )

        field_type_metadata = build_field_type_metadata(
            definition.field_types,
            existing_metadata=dataset.field_type_metadata,
            existing_active_types=dataset.field_types,
        )
        existing_field_metadata = field_type_metadata.get(field_name, {"inferredType": target_type, "type": target_type})
        field_type_metadata[field_name] = {
            "inferredType": canonicalize_field_type(existing_field_metadata.get("inferredType")),
            "type": target_type,
        }
        dataset.field_type_metadata = field_type_metadata
        dataset.field_types = active_field_types_from_metadata(field_type_metadata)
        dataset.save(update_fields=["field_type_metadata", "field_types", "updated_at"])

        audit_reports_event(
            action=AuditAction.UPDATE,
            event="analytics_dataset_field_type_changed",
            target=dataset,
            actor=request.user,
            request=request,
            metadata={
                "field": field_name,
                "target_type": target_type,
                "requires_confirmation": compatibility["requiresConfirmation"],
            },
        )
        serializer = self.get_serializer(dataset)
        return Response(
            {
                "dataset": serializer.data,
                "compatibility": compatibility,
            }
        )

    @action(detail=True, methods=["get"], url_path="worksheet-examples")
    def worksheet_examples(self, request, pk=None):
        sync_analytics_datasets()
        dataset = self.get_object()
        definition = get_dataset_definition(dataset.code)
        if definition is None:
            raise NotFound("No dataset registry definition is available for this dataset.")
        audit_reports_event(
            action=AuditAction.UPDATE,
            event="analytics_dataset_examples_viewed",
            target=dataset,
            actor=request.user,
            request=request,
        )
        return Response(
            {
                "dataset": dataset.code,
                "examples": get_dataset_worksheet_examples(definition, self._user_account_type()),
            }
        )

    @action(detail=True, methods=["get"], url_path="ai-prompt")
    def ai_prompt(self, request, pk=None):
        sync_analytics_datasets()
        dataset = self.get_object()
        definition = get_dataset_definition(dataset.code)
        if definition is None:
            raise NotFound("No dataset registry definition is available for this dataset.")
        audit_reports_event(
            action=AuditAction.UPDATE,
            event="analytics_dataset_ai_prompt_viewed",
            target=dataset,
            actor=request.user,
            request=request,
        )
        return Response(
            {
                "dataset": dataset.code,
                "name": dataset.name,
                "ai_prompt_hints": definition.ai_prompt_hints,
            }
        )

    @action(detail=False, methods=["post"], url_path="generate-worksheet")
    def generate_worksheet(self, request):
        serializer = AIWorksheetGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prompt = serializer.validated_data["prompt"]
        dataset_id = serializer.validated_data.get("dataset")
        account_type = self._user_account_type()

        if dataset_id:
            dataset = self.get_queryset().filter(id=dataset_id).first()
            if dataset is None:
                raise NotFound("Dataset is not available in the current scope.")
            definition = get_dataset_definition(dataset.code)
            if definition is None:
                raise NotFound("No dataset registry definition is available for this dataset.")
        else:
            definition, dataset, scored = resolve_dataset_from_prompt(prompt, account_type)
            if dataset is None:
                raise NotFound("No dataset could be resolved from the prompt for the current account scope.")

        assert_ai_prompt_safe(
            prompt,
            dataset.sensitive_fields or [],
            actor=request.user,
            request=request,
            target=dataset,
            context="analytics_dataset_ai_worksheet_request",
        )
        audit_reports_event(
            action=AuditAction.UPDATE,
            event="analytics_dataset_ai_worksheet_requested",
            target=dataset,
            actor=request.user,
            request=request,
            metadata={"prompt": prompt[:200]},
        )
        return Response(
            generate_worksheet_suggestion(
                definition=definition,
                dataset=dataset,
                prompt=prompt,
                account_type=account_type,
            )
        )

    def perform_create(self, serializer):
        if self.request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only platform or federal admins can manage analytics datasets.")
        serializer.save()
        audit_reports_event(action=AuditAction.CREATE, event="analytics_dataset_created", target=serializer.instance, actor=self.request.user, request=self.request)

    def perform_update(self, serializer):
        if self.request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only platform or federal admins can manage analytics datasets.")
        serializer.save()
        audit_reports_event(action=AuditAction.UPDATE, event="analytics_dataset_updated", target=serializer.instance, actor=self.request.user, request=self.request)

    def perform_destroy(self, instance):
        if self.request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only platform or federal admins can manage analytics datasets.")
        audit_reports_event(action=AuditAction.DELETE, event="analytics_dataset_deleted", target=instance, actor=self.request.user, request=self.request)
        instance.delete()


class AnalyticsWorksheetViewSet(DashboardArchitectureScopeMixin, viewsets.ModelViewSet):
    queryset = AnalyticsWorksheet.objects.select_related("owner", "organization", "state", "dataset").order_by("account_type", "name")
    serializer_class = AnalyticsWorksheetSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["account_type", "scope_type", "dataset", "is_active", "is_template"]

    def get_queryset(self):
        return self._scoped_queryset(self.queryset)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        audit_reports_event(action=AuditAction.UPDATE, event="analytics_worksheet_viewed", target=instance, actor=request.user, request=request)
        return Response(self.get_serializer(instance).data)

    @action(detail=False, methods=["post"], url_path="preview")
    def preview(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dataset = serializer.validated_data["dataset"]
        definition = get_dataset_definition(dataset.code)
        if definition is None:
            raise NotFound("No dataset registry definition is available for this dataset.")
        cache_key = preview_cache_key("worksheet-preview", dataset.id, request.user.id, hash(str(serializer.validated_data)))
        preview = cache.get(cache_key)
        if preview is None:
            preview = timed_operation(
                lambda: generate_worksheet_preview(definition, request.user, serializer.validated_data),
                timeout_message="Worksheet preview timed out. Narrow the filters or reduce the preview size.",
            )
            cache.set(cache_key, preview, PREVIEW_CACHE_TTL)
        audit_reports_event(
            action=AuditAction.UPDATE,
            event="analytics_worksheet_previewed",
            target=dataset,
            actor=request.user,
            request=request,
            metadata={"dataset_code": dataset.code},
        )
        return Response(preview)

    @action(detail=False, methods=["post"], url_path="generate-widget")
    def generate_widget(self, request):
        serializer = AIWidgetGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        worksheet = self.get_queryset().filter(id=serializer.validated_data["worksheet"]).first()
        if worksheet is None:
            raise NotFound("Worksheet is not available in the current scope.")
        assert_ai_prompt_safe(
            serializer.validated_data["prompt"],
            worksheet.dataset.sensitive_fields or [],
            actor=request.user,
            request=request,
            target=worksheet,
            context="analytics_widget_ai_request",
        )
        audit_reports_event(
            action=AuditAction.UPDATE,
            event="analytics_widget_ai_requested",
            target=worksheet,
            actor=request.user,
            request=request,
            metadata={"prompt": serializer.validated_data["prompt"][:200]},
        )
        return Response(generate_widget_suggestion(worksheet, serializer.validated_data["prompt"]))

    def perform_create(self, serializer):
        super().perform_create(serializer)
        audit_reports_event(action=AuditAction.CREATE, event="analytics_worksheet_created", target=serializer.instance, actor=self.request.user, request=self.request)

    def perform_update(self, serializer):
        serializer.save()
        audit_reports_event(action=AuditAction.UPDATE, event="analytics_worksheet_updated", target=serializer.instance, actor=self.request.user, request=self.request)

    def perform_destroy(self, instance):
        audit_reports_event(action=AuditAction.DELETE, event="analytics_worksheet_deleted", target=instance, actor=self.request.user, request=self.request)
        instance.delete()


class AnalyticsWidgetViewSet(DashboardArchitectureScopeMixin, viewsets.ModelViewSet):
    queryset = AnalyticsWidget.objects.select_related("owner", "organization", "state", "worksheet").order_by("account_type", "title")
    serializer_class = AnalyticsWidgetSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["account_type", "scope_type", "worksheet", "widget_type", "is_active"]

    def get_queryset(self):
        return self._scoped_queryset(self.queryset)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        audit_reports_event(action=AuditAction.UPDATE, event="analytics_widget_viewed", target=instance, actor=request.user, request=request)
        return Response(self.get_serializer(instance).data)

    @action(detail=False, methods=["post"], url_path="preview")
    def preview(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        worksheet = serializer.validated_data["worksheet"]
        cache_key = preview_cache_key("widget-preview", worksheet.id, worksheet.updated_at.timestamp(), hash(str(serializer.validated_data)))
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            audit_reports_event(
                action=AuditAction.UPDATE,
                event="analytics_widget_previewed",
                target=worksheet,
                actor=request.user,
                request=request,
                metadata={"widget_type": serializer.validated_data["widget_type"], "cache": "hit"},
            )
            return Response(cached_response)

        worksheet_preview = worksheet.preview_output or {}
        if not worksheet_preview:
            definition = get_dataset_definition(worksheet.dataset.code)
            if definition is None:
                raise NotFound("No dataset registry definition is available for this worksheet dataset.")
            worksheet_preview = timed_operation(
                lambda: generate_worksheet_preview(
                    definition,
                    request.user,
                    {
                        "metrics": worksheet.metrics,
                        "dimensions": worksheet.dimensions,
                        "filters": worksheet.filters,
                        "chart_recommendation": worksheet.chart_recommendation or "table",
                    },
                ),
                timeout_message="Widget preview timed out. Refresh the worksheet with narrower filters.",
            )
        widget_type = serializer.validated_data["widget_type"]
        preview = widget_preview_payload(
            widget_type,
            worksheet_preview,
            serializer.validated_data.get("visual_config", {}),
            serializer.validated_data["title"],
        )
        response_payload = {
            "widget_type": widget_type,
            "title": serializer.validated_data["title"],
            "export_formats": [
                fmt
                for fmt in WIDGET_EXPORT_FORMATS
                if serializer.validated_data.get("export_options", {}).get(fmt, True)
            ],
            "preview": preview,
        }
        cache.set(cache_key, response_payload, PREVIEW_CACHE_TTL)
        audit_reports_event(
            action=AuditAction.UPDATE,
            event="analytics_widget_previewed",
            target=worksheet,
            actor=request.user,
            request=request,
            metadata={"widget_type": widget_type},
        )
        return Response(response_payload)

    @action(detail=False, methods=["post"], url_path="explain")
    def explain(self, request):
        serializer = AIExplainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        widget_id = serializer.validated_data.get("widget")
        if not widget_id:
            raise NotFound("Widget id is required.")
        widget = self.get_queryset().filter(id=widget_id).select_related("worksheet").first()
        if widget is None:
            raise NotFound("Widget is not available in the current scope.")
        assert_ai_prompt_safe(
            serializer.validated_data.get("prompt", ""),
            widget_sensitive_fields(widget),
            actor=request.user,
            request=request,
            target=widget,
            context="analytics_widget_ai_explain_request",
        )
        audit_reports_event(
            action=AuditAction.UPDATE,
            event="analytics_widget_ai_explain_requested",
            target=widget,
            actor=request.user,
            request=request,
            metadata={"prompt": serializer.validated_data.get("prompt", "")[:200]},
        )
        return Response(explain_dashboard_artifact(serializer.validated_data.get("prompt", ""), widget=widget))

    @action(detail=True, methods=["post"], url_path="refresh")
    def refresh(self, request, pk=None):
        widget = self.get_object()
        definition = get_dataset_definition(widget.worksheet.dataset.code)
        if definition is None:
            raise NotFound("No dataset registry definition is available for this worksheet dataset.")
        worksheet_preview = timed_operation(
            lambda: generate_worksheet_preview(
                definition,
                request.user,
                {
                    "metrics": widget.worksheet.metrics,
                    "dimensions": widget.worksheet.dimensions,
                    "filters": widget.worksheet.filters,
                    "chart_recommendation": widget.worksheet.chart_recommendation or "table",
                },
            ),
            timeout_message="Widget refresh timed out. Narrow the worksheet scope and try again.",
        )
        widget.worksheet.preview_output = worksheet_preview
        widget.worksheet.save(update_fields=["preview_output", "updated_at"])
        preview = widget_preview_payload(widget.widget_type, worksheet_preview, widget.visual_config or {}, widget.title)
        cache.set(
            preview_cache_key("widget-preview", widget.worksheet.id, widget.worksheet.updated_at.timestamp(), hash(str(widget.id))),
            {"widget_type": widget.widget_type, "title": widget.title, "export_formats": [fmt for fmt in WIDGET_EXPORT_FORMATS if widget.export_options.get(fmt, True)], "preview": preview},
            PREVIEW_CACHE_TTL,
        )
        audit_reports_event(action=AuditAction.UPDATE, event="analytics_widget_refreshed", target=widget, actor=request.user, request=request)
        return Response({"widget_type": widget.widget_type, "title": widget.title, "export_formats": [fmt for fmt in WIDGET_EXPORT_FORMATS if widget.export_options.get(fmt, True)], "preview": preview})

    def perform_create(self, serializer):
        super().perform_create(serializer)
        audit_reports_event(action=AuditAction.CREATE, event="analytics_widget_created", target=serializer.instance, actor=self.request.user, request=self.request)

    def perform_update(self, serializer):
        serializer.save()
        audit_reports_event(action=AuditAction.UPDATE, event="analytics_widget_updated", target=serializer.instance, actor=self.request.user, request=self.request)

    def perform_destroy(self, instance):
        audit_reports_event(action=AuditAction.DELETE, event="analytics_widget_deleted", target=instance, actor=self.request.user, request=self.request)
        instance.delete()


class DashboardAlertRuleViewSet(DashboardArchitectureScopeMixin, viewsets.ModelViewSet):
    queryset = DashboardAlertRule.objects.select_related("owner", "organization", "state", "widget", "widget__worksheet").order_by("account_type", "name")
    serializer_class = DashboardAlertRuleSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["account_type", "scope_type", "widget", "is_active"]

    def get_queryset(self):
        queryset = self._scoped_queryset(self.queryset)
        widget_id = self.request.query_params.get("widget")
        if widget_id:
            queryset = queryset.filter(widget_id=widget_id)
        return queryset

    def perform_create(self, serializer):
        widget = serializer.validated_data["widget"]
        if not self._scoped_queryset(AnalyticsWidget.objects.all()).filter(id=widget.id).exists():
            raise PermissionDenied("Widget is not available in the current scope.")
        rule = serializer.save(
            owner=self.request.user,
            organization=getattr(self.request.user, "organization", None),
            state=getattr(self.request.user, "state", None),
            account_type=self._user_account_type(),
            scope_type=getattr(widget, "scope_type", "private"),
        )
        log_action(
            action=AuditAction.CREATE,
            actor=self.request.user,
            target=rule,
            request=self.request,
            metadata={"event": "dashboard_alert_created", "widget_id": str(widget.id)},
        )

    def perform_update(self, serializer):
        rule = serializer.save()
        log_action(
            action=AuditAction.UPDATE,
            actor=self.request.user,
            target=rule,
            request=self.request,
            metadata={"event": "dashboard_alert_updated"},
        )

    def perform_destroy(self, instance):
        log_action(
            action=AuditAction.DELETE,
            actor=self.request.user,
            target=instance,
            request=self.request,
            metadata={"event": "dashboard_alert_deleted"},
        )
        instance.delete()

    @action(detail=True, methods=["post"], url_path="evaluate")
    def evaluate(self, request, pk=None):
        rule = self.get_object()
        event = evaluate_dashboard_alert_rule(rule, actor=request.user)
        return Response(DashboardAlertEventSerializer(event).data)

    @action(detail=False, methods=["post"], url_path="evaluate-all")
    def evaluate_all(self, request):
        rules = list(self.get_queryset().filter(is_active=True).select_related("widget", "widget__worksheet"))
        events = [evaluate_dashboard_alert_rule(rule, actor=request.user) for rule in rules]
        return Response(
            {
                "evaluated": len(events),
                "triggered": sum(1 for event in events if event.status == "triggered"),
                "events": DashboardAlertEventSerializer(events, many=True).data,
            }
        )


class DashboardAlertEventViewSet(DashboardArchitectureScopeMixin, viewsets.ReadOnlyModelViewSet):
    queryset = DashboardAlertEvent.objects.select_related("rule", "widget", "rule__owner", "rule__organization", "rule__state").order_by("-created_at")
    serializer_class = DashboardAlertEventSerializer
    filterset_fields = ["rule", "widget", "status"]

    def get_queryset(self):
        queryset = self.queryset
        if getattr(self, "swagger_fake_view", False):
            return queryset
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return queryset
        account_type = self._user_account_type()
        queryset = queryset.filter(rule__account_type=account_type)
        if user.organization_id:
            queryset = queryset.filter(models.Q(rule__organization_id=user.organization_id) | models.Q(rule__organization__isnull=True))
        if user.state_id:
            queryset = queryset.filter(models.Q(rule__state_id=user.state_id) | models.Q(rule__state__isnull=True))
        if user.role not in {UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            queryset = queryset.filter(rule__owner=user)
        return queryset


class DashboardCanvasViewSet(DashboardArchitectureScopeMixin, viewsets.ModelViewSet):
    queryset = DashboardCanvas.objects.select_related("owner", "organization", "state").order_by("account_type", "name")
    serializer_class = DashboardCanvasSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["account_type", "scope_type", "is_active", "is_draft"]

    def get_queryset(self):
        return self._scoped_queryset(self.queryset)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        audit_reports_event(action=AuditAction.UPDATE, event="dashboard_canvas_viewed", target=instance, actor=request.user, request=request)
        return Response(self.get_serializer(instance).data)

    @action(detail=False, methods=["post"], url_path="generate-dashboard")
    def generate_dashboard(self, request):
        serializer = AIDashboardGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        widget_ids = serializer.validated_data.get("widget_ids") or []
        widget_queryset = AnalyticsWidget.objects.select_related("worksheet")
        widget_queryset = self._scoped_queryset(widget_queryset)
        widgets = list(widget_queryset.filter(id__in=widget_ids)) if widget_ids else list(widget_queryset.order_by("title")[:4])
        combined_sensitive_fields = sorted({field for widget in widgets for field in widget_sensitive_fields(widget)})
        assert_ai_prompt_safe(
            serializer.validated_data["prompt"],
            combined_sensitive_fields,
            actor=request.user,
            request=request,
            context="dashboard_canvas_ai_request",
        )
        audit_reports_event(
            action=AuditAction.UPDATE,
            event="dashboard_canvas_ai_requested",
            actor=request.user,
            request=request,
            metadata={"prompt": serializer.validated_data["prompt"][:200], "widget_count": len(widgets)},
        )
        return Response(generate_dashboard_suggestion(widgets, serializer.validated_data["prompt"]))

    @action(detail=False, methods=["post"], url_path="generate-full")
    def generate_full(self, request):
        serializer = AIDashboardFullGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prompt = serializer.validated_data["prompt"]
        account_type = self._user_account_type()
        definition, dataset, scored = resolve_dataset_from_prompt(prompt, account_type)
        if dataset is None:
            raise NotFound("No dataset could be resolved from the prompt for the current account scope.")
        assert_ai_prompt_safe(
            prompt,
            dataset.sensitive_fields or [],
            actor=request.user,
            request=request,
            target=dataset,
            context="dashboard_canvas_ai_full_request",
        )
        audit_reports_event(
            action=AuditAction.UPDATE,
            event="dashboard_canvas_ai_full_requested",
            actor=request.user,
            request=request,
            metadata={"prompt": prompt[:200]},
        )
        try:
            result = generate_dashboard_from_prompt(prompt, account_type)
        except NotFound:
            raise
        except Exception as exc:
            raise APIException(f"Failed to generate dashboard: {exc}")
        return Response(result)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        canvas = self.get_object()
        serializer = DashboardPublishSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        published_dashboard = PublishedDashboard.objects.create(
            canvas=canvas,
            published_by=request.user,
            version_label=validated.get("version_label") or f"v{canvas.published_versions.count() + 1}",
            visibility_scope=validated["visibility_scope"],
            share_settings=validated.get("share_settings", {}),
            snapshot=build_published_dashboard_snapshot(canvas),
            published_at=timezone.now(),
            is_active=True,
        )
        if canvas.is_draft:
            canvas.is_draft = False
            canvas.save(update_fields=["is_draft", "updated_at"])
        log_action(
            action=AuditAction.UPDATE,
            actor=request.user,
            target=published_dashboard,
            request=request,
            metadata={
                "event": "dashboard_published",
                "canvas_id": str(canvas.id),
                "visibility_scope": published_dashboard.visibility_scope,
            },
        )
        response_serializer = PublishedDashboardSerializer(published_dashboard, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="explain")
    def explain(self, request, pk=None):
        canvas = self.get_object()
        serializer = AIExplainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert_ai_prompt_safe(
            serializer.validated_data.get("prompt", ""),
            canvas_sensitive_fields(canvas),
            actor=request.user,
            request=request,
            target=canvas,
            context="dashboard_canvas_ai_explain_request",
        )
        audit_reports_event(
            action=AuditAction.UPDATE,
            event="dashboard_canvas_ai_explain_requested",
            target=canvas,
            actor=request.user,
            request=request,
            metadata={"prompt": serializer.validated_data.get("prompt", "")[:200]},
        )
        return Response(explain_dashboard_artifact(serializer.validated_data.get("prompt", ""), canvas=canvas))

    def perform_create(self, serializer):
        super().perform_create(serializer)
        audit_reports_event(action=AuditAction.CREATE, event="dashboard_canvas_created", target=serializer.instance, actor=self.request.user, request=self.request)

    def perform_update(self, serializer):
        serializer.save()
        audit_reports_event(action=AuditAction.UPDATE, event="dashboard_canvas_updated", target=serializer.instance, actor=self.request.user, request=self.request)

    def perform_destroy(self, instance):
        audit_reports_event(action=AuditAction.DELETE, event="dashboard_canvas_deleted", target=instance, actor=self.request.user, request=self.request)
        instance.delete()


class DashboardCanvasBlockViewSet(DashboardArchitectureScopeMixin, viewsets.ModelViewSet):
    queryset = DashboardCanvasBlock.objects.select_related("canvas", "widget").order_by("canvas", "sort_order", "created_at")
    serializer_class = DashboardCanvasBlockSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["canvas", "block_type", "is_active"]

    def get_queryset(self):
        queryset = self.queryset
        if getattr(self, "swagger_fake_view", False):
            return queryset
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return queryset
        account_type = self._user_account_type()
        queryset = queryset.filter(canvas__account_type=account_type)
        if user.organization_id:
            queryset = queryset.filter(models.Q(canvas__organization_id=user.organization_id) | models.Q(canvas__organization__isnull=True))
        if user.state_id:
            queryset = queryset.filter(models.Q(canvas__state_id=user.state_id) | models.Q(canvas__state__isnull=True))
        if user.role not in {UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            queryset = queryset.filter(canvas__owner=user)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        audit_reports_event(action=AuditAction.UPDATE, event="dashboard_block_viewed", target=instance, actor=request.user, request=request)
        return Response(self.get_serializer(instance).data)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        audit_reports_event(action=AuditAction.CREATE, event="dashboard_block_created", target=serializer.instance, actor=self.request.user, request=self.request)

    def perform_update(self, serializer):
        serializer.save()
        audit_reports_event(action=AuditAction.UPDATE, event="dashboard_block_updated", target=serializer.instance, actor=self.request.user, request=self.request)

    def perform_destroy(self, instance):
        audit_reports_event(action=AuditAction.DELETE, event="dashboard_block_deleted", target=instance, actor=self.request.user, request=self.request)
        instance.delete()


class PublishedDashboardViewSet(DashboardArchitectureScopeMixin, viewsets.ModelViewSet):
    queryset = PublishedDashboard.objects.select_related("canvas", "published_by").order_by("-published_at", "-created_at")
    serializer_class = PublishedDashboardSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["visibility_scope", "is_active", "canvas"]

    def get_queryset(self):
        queryset = self.queryset
        if getattr(self, "swagger_fake_view", False):
            return queryset
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return queryset
        account_type = self._user_account_type()
        queryset = queryset.filter(canvas__account_type=account_type)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        dashboards = [dashboard for dashboard in queryset if published_dashboard_is_accessible(dashboard, request.user)]
        audit_reports_event(
            action=AuditAction.UPDATE,
            event="published_dashboard_list_viewed",
            actor=request.user,
            request=request,
            metadata={"count": len(dashboards)},
        )
        serializer = self.get_serializer(dashboards, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not published_dashboard_is_accessible(instance, request.user):
            raise PermissionDenied("You do not have access to this published dashboard.")
        cache_key = preview_cache_key("published-dashboard", instance.id, instance.updated_at.timestamp())
        payload = cache.get(cache_key)
        if payload is None:
            serializer = self.get_serializer(instance)
            payload = serializer.data
            cache.set(cache_key, payload, PUBLISHED_DASHBOARD_CACHE_TTL)
        audit_reports_event(action=AuditAction.UPDATE, event="published_dashboard_viewed", target=instance, actor=request.user, request=request)
        return Response(payload)

    @action(detail=True, methods=["post"], url_path="export")
    def export(self, request, pk=None):
        dashboard = self.get_object()
        if not published_dashboard_is_accessible(dashboard, request.user):
            raise PermissionDenied("You do not have access to this published dashboard.")
        if not published_dashboard_export_enabled(dashboard):
            raise PermissionDenied("Export is disabled for this published dashboard.")

        serializer = PublishedDashboardExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        if large_export_requested(dashboard, validated["format"], validated.get("block_id")):
            job = DashboardExportJob.objects.create(
                owner=request.user,
                published_dashboard=dashboard,
                block_id=str(validated.get("block_id") or ""),
                export_format=validated["format"],
                status="pending",
            )
            from apps.reports.tasks import process_dashboard_export_job

            try:
                process_dashboard_export_job.delay(str(job.id))
            except Exception:
                process_dashboard_export_job.apply(args=[str(job.id)])
            audit_reports_event(
                action=AuditAction.UPDATE,
                event="published_dashboard_export_queued",
                target=dashboard,
                actor=request.user,
                request=request,
                metadata={"job_id": str(job.id), "format": validated["format"]},
            )
            return Response({"background": True, "job_id": str(job.id), "status": "pending"}, status=status.HTTP_202_ACCEPTED)
        export_data = build_published_dashboard_export_payload(
            dashboard,
            validated["format"],
            validated.get("block_id"),
        )
        log_action(
            action=AuditAction.UPDATE,
            actor=request.user,
            target=dashboard,
            request=request,
            metadata={
                "event": "published_dashboard_exported",
                "format": validated["format"],
                "target": export_data["target"],
                "block_id": str(validated.get("block_id") or ""),
            },
        )
        return Response(export_data)

    @action(detail=True, methods=["post"], url_path="share-event")
    def share_event(self, request, pk=None):
        dashboard = self.get_object()
        if not published_dashboard_is_accessible(dashboard, request.user):
            raise PermissionDenied("You do not have access to this published dashboard.")

        serializer = PublishedDashboardShareEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        log_action(
            action=AuditAction.UPDATE,
            actor=request.user,
            target=dashboard,
            request=request,
            metadata={
                "event": serializer.validated_data["event"],
            },
        )
        return Response({"status": "ok"})

    @action(detail=True, methods=["patch"], url_path="sharing")
    def sharing(self, request, pk=None):
        dashboard = self.get_object()
        canvas = dashboard.canvas
        if request.user.role != UserRole.SUPER_ADMIN and canvas.owner_id != request.user.id and request.user.role not in {UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("You do not have permission to update sharing for this published dashboard.")

        serializer = PublishedDashboardSharingSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        old_value = {
            "visibility_scope": dashboard.visibility_scope,
            "share_settings": dashboard.share_settings or {},
        }
        if "visibility_scope" in serializer.validated_data:
            dashboard.visibility_scope = serializer.validated_data["visibility_scope"]
        if "share_settings" in serializer.validated_data:
            dashboard.share_settings = serializer.validated_data["share_settings"]
        dashboard.save(update_fields=["visibility_scope", "share_settings", "updated_at"])
        log_action(
            action=AuditAction.UPDATE,
            actor=request.user,
            target=dashboard,
            request=request,
            old_value=old_value,
            new_value={
                "visibility_scope": dashboard.visibility_scope,
                "share_settings": dashboard.share_settings or {},
            },
            metadata={"event": "published_dashboard_sharing_updated"},
        )
        return Response(self.get_serializer(dashboard).data)


class DashboardExportJobViewSet(DashboardArchitectureScopeMixin, viewsets.ReadOnlyModelViewSet):
    queryset = DashboardExportJob.objects.select_related("owner", "published_dashboard").order_by("-created_at")
    serializer_class = DashboardExportJobSerializer
    filterset_fields = ["published_dashboard", "status", "export_format"]

    def get_queryset(self):
        queryset = self.queryset
        if getattr(self, "swagger_fake_view", False):
            return queryset
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return queryset
        queryset = queryset.filter(published_dashboard__canvas__account_type=self._user_account_type())
        if user.organization_id:
            queryset = queryset.filter(
                models.Q(published_dashboard__canvas__organization_id=user.organization_id)
                | models.Q(published_dashboard__canvas__organization__isnull=True)
            )
        if user.state_id:
            queryset = queryset.filter(
                models.Q(published_dashboard__canvas__state_id=user.state_id)
                | models.Q(published_dashboard__canvas__state__isnull=True)
            )
        if user.role not in {UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            queryset = queryset.filter(owner=user)
        return queryset


class DashboardTemplateViewSet(DashboardArchitectureScopeMixin, viewsets.ModelViewSet):
    queryset = DashboardTemplate.objects.select_related("source_canvas", "source_published_dashboard", "created_by").order_by("account_type", "name")
    serializer_class = DashboardTemplateSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["account_type", "scope_type", "is_active", "is_system_template"]

    def get_queryset(self):
        queryset = self.queryset
        if getattr(self, "swagger_fake_view", False):
            return queryset
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return queryset
        account_type = self._user_account_type()
        ensure_default_dashboard_templates(account_type)
        queryset = queryset.filter(account_type=account_type, is_active=True)
        if user.role not in {UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            queryset = queryset.filter(models.Q(created_by=user) | models.Q(is_system_template=True))
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        audit_reports_event(action=AuditAction.UPDATE, event="dashboard_template_viewed", target=instance, actor=request.user, request=request)
        return Response(self.get_serializer(instance).data)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user, account_type=self._user_account_type())
        audit_reports_event(action=AuditAction.CREATE, event="dashboard_template_created", target=serializer.instance, actor=user, request=self.request)

    def perform_update(self, serializer):
        serializer.save()
        audit_reports_event(action=AuditAction.UPDATE, event="dashboard_template_updated", target=serializer.instance, actor=self.request.user, request=self.request)

    def perform_destroy(self, instance):
        audit_reports_event(action=AuditAction.DELETE, event="dashboard_template_deleted", target=instance, actor=self.request.user, request=self.request)
        instance.delete()

    @action(detail=True, methods=["post"], url_path="use-template")
    def use_template(self, request, pk=None):
        template = self.get_object()
        canvas = clone_dashboard_template_to_canvas(template, request.user, self._user_account_type())
        audit_reports_event(
            action=AuditAction.CREATE,
            event="dashboard_template_cloned",
            target=template,
            actor=request.user,
            request=request,
            metadata={"canvas_id": str(canvas.id)},
        )
        return Response(DashboardCanvasSerializer(canvas).data, status=status.HTTP_201_CREATED)


class DataQualityIssueViewSet(viewsets.ModelViewSet):
    queryset = DataQualityIssue.objects.select_related("state", "organization", "assigned_to", "resolved_by").order_by("-created_at")
    serializer_class = DataQualityIssueSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "patch", "head", "options"]
    filterset_fields = ["issue_type", "severity", "module", "status", "state"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return self.queryset
        if user.role == UserRole.FEDERAL_ADMIN:
            return self.queryset
        if user.role == UserRole.STATE_ADMIN and user.state_id:
            return self.queryset.filter(state_id=user.state_id)
        if user.role == UserRole.EMPLOYER and user.organization_id:
            return self.queryset.filter(organization_id=user.organization_id)
        return self.queryset.none()

    @extend_schema(request=ReportReviewActionSerializer, responses=DataQualityIssueSerializer)
    @action(detail=True, methods=["post"], url_path="assign")
    def assign(self, request, pk=None):
        issue = self.get_object()
        serializer = ReportReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignee_id = serializer.validated_data.get("comment")
        if assignee_id:
            from apps.accounts.models import User
            assignee = User.objects.filter(id=assignee_id).first()
            if assignee:
                issue.assigned_to = assignee
                issue.status = "assigned"
                issue.save(update_fields=["assigned_to", "status", "updated_at"])
        return Response(DataQualityIssueSerializer(issue).data)

    @extend_schema(responses=DataQualityIssueSerializer)
    @action(detail=True, methods=["post"], url_path="resolve")
    def resolve(self, request, pk=None):
        issue = self.get_object()
        issue.status = "resolved"
        issue.resolved_by = request.user
        issue.resolved_at = timezone.now()
        issue.save(update_fields=["status", "resolved_by", "resolved_at", "updated_at"])
        return Response(DataQualityIssueSerializer(issue).data)

    @extend_schema(responses=DataQualityIssueSerializer)
    @action(detail=True, methods=["post"], url_path="escalate")
    def escalate(self, request, pk=None):
        issue = self.get_object()
        issue.status = "escalated"
        issue.save(update_fields=["status", "updated_at"])
        return Response(DataQualityIssueSerializer(issue).data)


class ScheduledReportViewSet(viewsets.ModelViewSet):
    queryset = ScheduledReport.objects.select_related("report_template", "owner").order_by("-created_at")
    serializer_class = ScheduledReportSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["schedule_frequency", "is_active"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        return self.queryset.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(responses={201: GeneratedReportSerializer})
    @action(detail=True, methods=["post"], url_path="run-now")
    def run_now(self, request, pk=None):
        scheduled = self.get_object()
        report = ReportService.generate(
            report_type=ReportType.STATE_MONTHLY,
            user=request.user,
            file_format=scheduled.output_format or "json",
            filters=scheduled.filters or {},
        )
        scheduled.last_run_at = timezone.now()
        next_map = {"daily": 1, "weekly": 7, "monthly": 30, "quarterly": 90}
        days = next_map.get(scheduled.schedule_frequency, 30)
        scheduled.next_run_at = timezone.now() + timezone.timedelta(days=days)
        scheduled.save(update_fields=["last_run_at", "next_run_at", "updated_at"])
        return Response(GeneratedReportSerializer(report).data, status=status.HTTP_201_CREATED)


class KpiCardDefinitionViewSet(DashboardArchitectureScopeMixin, viewsets.ModelViewSet):
    """The shared KPI card library: definitions, resolution, and instantiation."""

    queryset = KpiCardDefinition.objects.order_by("category", "title")
    serializer_class = KpiCardDefinitionSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["category", "source_type", "is_active"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        queryset = self.queryset
        user = self.request.user
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            queryset = queryset.filter(is_active=True)
        if user.role == UserRole.SUPER_ADMIN:
            return queryset
        account_type = self._user_account_type()
        if account_type:
            queryset = queryset.filter(
                models.Q(allowed_account_types=[]) | models.Q(allowed_account_types__contains=[account_type])
            )
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) | models.Q(code__icontains=search) | models.Q(description__icontains=search)
            )
        return queryset

    def _assert_can_manage(self):
        if self.request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only federal administrators can manage the KPI card library.")

    def perform_create(self, serializer):
        self._assert_can_manage()
        instance = serializer.save(created_by=self.request.user)
        audit_reports_event(action=AuditAction.CREATE, event="kpi_card_created", target=instance, actor=self.request.user, request=self.request)

    def perform_update(self, serializer):
        self._assert_can_manage()
        if serializer.instance.is_system and "code" in serializer.validated_data:
            raise ValidationError("System card codes cannot be changed.")
        instance = serializer.save()
        audit_reports_event(action=AuditAction.UPDATE, event="kpi_card_updated", target=instance, actor=self.request.user, request=self.request)

    def perform_destroy(self, instance):
        self._assert_can_manage()
        if instance.is_system:
            raise ValidationError("System cards cannot be deleted; deactivate them instead.")
        audit_reports_event(action=AuditAction.DELETE, event="kpi_card_deleted", target=instance, actor=self.request.user, request=self.request)
        instance.delete()

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        from apps.reports.kpi_cards import resolve_kpi_card

        card = self.get_object()
        try:
            result = resolve_kpi_card(card, request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"code": card.code, **result})

    @action(detail=False, methods=["post"], url_path="resolve-config")
    def resolve_config(self, request):
        """Resolve an inline (unsaved) config — used to preview drafts and AI output."""
        from apps.reports.kpi_cards import resolve_kpi_card

        config = request.data.get("config") or {}
        if not isinstance(config, dict) or not config:
            return Response({"detail": "A config object is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = resolve_kpi_card(config, request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)

    @action(detail=True, methods=["post"])
    def instantiate(self, request, pk=None):
        """Create a worksheet + kpi_card widget from a definition so the card can fill any widget slot."""
        card = self.get_object()
        if card.source_type != "dataset":
            return Response(
                {"detail": "Snapshot-backed cards mount directly as canvas KPI blocks; widget slots need a dataset-backed card."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        dataset = AnalyticsDataset.objects.filter(code=card.dataset_code, is_active=True).first()
        if dataset is None:
            return Response({"detail": f"Dataset '{card.dataset_code}' is not available."}, status=status.HTTP_400_BAD_REQUEST)
        account_type = self._user_account_type()
        worksheet = AnalyticsWorksheet.objects.create(
            owner=request.user,
            organization_id=request.user.organization_id,
            state_id=request.user.state_id,
            account_type=account_type,
            name=f"{card.title} (KPI card)",
            description=card.description or card.detail,
            dataset=dataset,
            metrics=[{"field": card.metric or "id", "aggregation": card.aggregation, "label": card.title}],
            dimensions=[],
            filters=card.filters or [],
            chart_recommendation="kpi_card",
        )
        widget = AnalyticsWidget.objects.create(
            owner=request.user,
            organization_id=request.user.organization_id,
            state_id=request.user.state_id,
            account_type=account_type,
            worksheet=worksheet,
            title=card.title,
            widget_type="kpi_card",
            visual_config={"kpi_card_code": card.code, "icon": card.icon, "format": card.format, "target": card.target, "trend": card.trend, "detail": card.detail},
        )
        audit_reports_event(action=AuditAction.CREATE, event="kpi_card_instantiated", target=widget, actor=request.user, request=self.request,
                            metadata={"kpi_card_code": card.code})
        return Response(
            {"widget_id": str(widget.id), "worksheet_id": str(worksheet.id), "kpi_card_code": card.code},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        """AI-assist: turn a prompt into a valid KpiCard config (optionally saved to the library)."""
        prompt = (request.data.get("prompt") or "").strip()
        if not prompt:
            return Response({"detail": "A prompt is required."}, status=status.HTTP_400_BAD_REQUEST)
        assert_ai_prompt_safe(prompt, sensitive_fields=None, actor=request.user, request=request, target=None, context="kpi_card_generate")
        account_type = self._user_account_type()
        definition, dataset, _examples = resolve_dataset_from_prompt(prompt, account_type)
        if definition is None or dataset is None:
            return Response({"detail": "Could not match the prompt to an approved dataset."}, status=status.HTTP_400_BAD_REQUEST)
        words = {w for w in prompt.lower().split() if w}
        aggregation = "avg" if words & {"average", "avg", "mean", "score"} else "sum" if words & {"revenue", "amount", "total"} and "amount" in definition.available_fields else "count"
        metric = "amount" if aggregation == "sum" else "compliance_score" if aggregation == "avg" and "compliance_score" in definition.available_fields else ""
        config = {
            "code": f"ai_{dataset.code}_{aggregation}"[:100],
            "title": prompt[:80].strip().capitalize(),
            "category": "ai-drafts",
            "source_type": "dataset",
            "dataset_code": dataset.code,
            "metric": metric,
            "aggregation": aggregation,
            "filters": [],
            "format": "currency" if metric == "amount" else "number",
            "trend": {"compare_to": "prev_period", "window": "30d"},
            "target": {},
            "detail": f"AI draft from prompt: {prompt[:120]}",
            "requires_review": True,
        }
        saved = None
        if request.data.get("save"):
            self._assert_can_manage()
            instance, _created = KpiCardDefinition.objects.update_or_create(
                code=config["code"],
                defaults={key: value for key, value in config.items() if key not in {"code", "requires_review"}} | {"created_by": request.user, "is_active": True},
            )
            saved = KpiCardDefinitionSerializer(instance).data
        audit_reports_event(action=AuditAction.CREATE, event="kpi_card_ai_generated", actor=request.user, request=request,
                            metadata={"prompt": prompt[:200], "saved": bool(saved)})
        return Response({"config": config, "saved": saved})
