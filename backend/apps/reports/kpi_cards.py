"""KPI card resolver: turns a KpiCardDefinition (or inline config) into a value.

Three-layer separation:
- Definition lives in KpiCardDefinition (registry).
- This module is the data resolver: config -> {value, formatted, trend, status}.
- Rendering happens in the frontend <KpiCard/> which is surface-agnostic.

Sources:
- dataset: aggregates a registered analytics dataset with the caller's scope
  enforced via apply_dataset_scope (same rules as worksheets).
- snapshot: reads a key from the existing DashboardService federal payload,
  guaranteeing exact parity with the legacy operational dashboard cards.
"""

import hashlib
import json
from decimal import Decimal

from django.core.cache import cache
from django.db.models import Avg, Sum
from django.utils import timezone

from apps.reports.dataset_registry import apply_dataset_scope, get_dataset_definition
from apps.reports.models import KpiCardAggregation, KpiCardFormat, KpiCardSourceType

CACHE_TTL_SECONDS = 120
SNAPSHOT_CACHE_TTL_SECONDS = 120

WINDOW_DAYS = {"7d": 7, "30d": 30, "90d": 90, "365d": 365}

FILTER_OPERATORS = {
    "eq": "",
    "neq": "",  # negated below
    "in": "__in",
    "gte": "__gte",
    "lte": "__lte",
    "gt": "__gt",
    "lt": "__lt",
    "contains": "__icontains",
}


def _config_from_definition(definition):
    return {
        "code": definition.code,
        "source_type": definition.source_type,
        "dataset_code": definition.dataset_code,
        "metric": definition.metric,
        "aggregation": definition.aggregation,
        "filters": definition.filters or [],
        "snapshot_key": definition.snapshot_key,
        "format": definition.format,
        "trend": definition.trend or {},
        "target": definition.target or {},
    }


def _cache_key(config, user):
    scope = f"{getattr(user, 'role', '')}:{getattr(user, 'state_id', '')}:{getattr(user, 'organization_id', '')}"
    digest = hashlib.sha256(json.dumps(config, sort_keys=True, default=str).encode()).hexdigest()[:24]
    return f"kpi_card:{digest}:{scope}"


def _apply_filters(queryset, filters):
    for item in filters or []:
        field = item.get("field")
        operator = item.get("operator", "eq")
        value = item.get("value")
        if not field or operator not in FILTER_OPERATORS:
            continue
        lookup = f"{field}{FILTER_OPERATORS[operator]}"
        if operator == "neq":
            queryset = queryset.exclude(**{lookup: value})
        else:
            queryset = queryset.filter(**{lookup: value})
    return queryset


def _aggregate(queryset, aggregation, metric, date_field="created_at"):
    if aggregation == KpiCardAggregation.COUNT:
        return queryset.count()
    if not metric:
        return queryset.count()
    if aggregation == KpiCardAggregation.SUM:
        return queryset.aggregate(v=Sum(metric))["v"] or 0
    if aggregation == KpiCardAggregation.AVG:
        value = queryset.aggregate(v=Avg(metric))["v"]
        return round(float(value), 2) if value is not None else None
    if aggregation == KpiCardAggregation.LATEST:
        row = queryset.order_by(f"-{date_field}").values_list(metric, flat=True).first()
        return row
    return queryset.count()


def _resolve_dataset(config, user):
    definition = get_dataset_definition(config.get("dataset_code") or "")
    if definition is None:
        raise ValueError(f"Dataset '{config.get('dataset_code')}' is not registered.")
    base = definition.model.objects.all()
    if definition.base_filters:
        base = base.filter(**definition.base_filters)
    base = apply_dataset_scope(definition, base, user)
    base = _apply_filters(base, config.get("filters"))

    aggregation = config.get("aggregation", KpiCardAggregation.COUNT)
    metric = config.get("metric", "")
    trend_config = config.get("trend") or {}
    date_field = trend_config.get("date_field", "created_at")

    value = _aggregate(base, aggregation, metric, date_field)

    trend = None
    window_days = WINDOW_DAYS.get(trend_config.get("window", ""))
    if window_days and trend_config.get("compare_to", "prev_period") == "prev_period":
        now = timezone.now()
        current_start = now - timezone.timedelta(days=window_days)
        previous_start = now - timezone.timedelta(days=window_days * 2)
        current = _aggregate(base.filter(**{f"{date_field}__gte": current_start}), aggregation, metric, date_field)
        previous = _aggregate(
            base.filter(**{f"{date_field}__gte": previous_start, f"{date_field}__lt": current_start}),
            aggregation, metric, date_field,
        )
        if current is not None and previous is not None:
            delta = float(current) - float(previous)
            trend = {
                "delta": round(delta, 2),
                "direction": "up" if delta > 0 else "down" if delta < 0 else "flat",
                "label": f"vs prev {window_days}d",
                "current": float(current),
                "previous": float(previous),
            }
    return value, trend


def _federal_snapshot(user):
    """Per-user cached copy of the legacy federal dashboard payload."""
    from apps.reports.services import DashboardService

    key = f"kpi_card_snapshot:federal:{getattr(user, 'id', '')}"
    payload = cache.get(key)
    if payload is None:
        payload = DashboardService.federal_dashboard(user)
        cache.set(key, payload, SNAPSHOT_CACHE_TTL_SECONDS)
    return payload


def _resolve_snapshot(config, user):
    payload = _federal_snapshot(user)
    snapshot_key = config.get("snapshot_key") or ""
    if snapshot_key == "risk_flags_total":
        rows = (payload.get("charts") or {}).get("risk_flag_trends_by_state") or []
        return sum(int(row.get("total") or 0) for row in rows), None
    value = (payload.get("cards") or {}).get(snapshot_key)
    if value is None:
        raise ValueError(f"Snapshot key '{snapshot_key}' not found in the dashboard payload.")
    return value, None


def _status_for(value, target):
    """Map a value onto good/warning/critical using breach thresholds.

    target = {"operator": "gt"|"gte"|"lt"|"lte", "warning": x, "critical": y}
    The operator describes the breach comparison, e.g. {"operator": "gt",
    "warning": 0} means "value > 0 is a warning".
    """
    if value is None or not target:
        return None
    operator = target.get("operator", "gt")
    compare = {
        "gt": lambda a, b: a > b,
        "gte": lambda a, b: a >= b,
        "lt": lambda a, b: a < b,
        "lte": lambda a, b: a <= b,
    }.get(operator)
    if compare is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    critical = target.get("critical")
    warning = target.get("warning")
    if critical is not None and compare(numeric, float(critical)):
        return "critical"
    if warning is not None and compare(numeric, float(warning)):
        return "warning"
    return "good"


def _format_value(value, fmt):
    if value is None:
        return "—"
    if isinstance(value, Decimal):
        value = float(value)
    if fmt == KpiCardFormat.PERCENT:
        return f"{value:,.1f}%" if isinstance(value, float) else f"{value:,}%"
    if fmt == KpiCardFormat.CURRENCY:
        return f"₦{value:,.2f}" if isinstance(value, float) else f"₦{value:,}"
    if isinstance(value, float):
        return f"{value:,.2f}".rstrip("0").rstrip(".")
    return f"{value:,}"


def resolve_kpi_card(config_or_definition, user):
    """Resolve a card config (or KpiCardDefinition) to {value, formatted, trend, status}."""
    config = (
        _config_from_definition(config_or_definition)
        if hasattr(config_or_definition, "source_type")
        else dict(config_or_definition)
    )
    key = _cache_key(config, user)
    cached = cache.get(key)
    if cached is not None:
        return cached

    if config.get("source_type") == KpiCardSourceType.SNAPSHOT:
        value, trend = _resolve_snapshot(config, user)
    else:
        value, trend = _resolve_dataset(config, user)

    result = {
        "value": float(value) if isinstance(value, Decimal) else value,
        "formatted": _format_value(value, config.get("format", KpiCardFormat.NUMBER)),
        "trend": trend,
        "status": _status_for(value, config.get("target") or {}),
    }
    cache.set(key, result, CACHE_TTL_SECONDS)
    return result
