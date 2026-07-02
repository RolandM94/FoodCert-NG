"""Performance Indicator alerting.

Evaluates active indicators against targets, threshold bands, and calculation
health, then notifies federal/state officers through NotificationService
(category M&E). Triggers per the Performance Indicators PRD §16.1:

- Indicator below target
- Indicator in critical threshold band
- Indicator result missing for the current period
- Indicator calculation failed
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.notifications.models import (
    NotificationCategory,
    NotificationChannel,
    NotificationPriority,
)
from apps.notifications.services import NotificationService

from .indicator_pi import resolve_effective_target, resolve_performance_band
from .models import (
    IndicatorCalculationStatus,
    IndicatorThresholdSeverity,
    KPITargetDirection,
    MEIndicator,
    MEIndicatorCalculationLog,
)

User = get_user_model()

RESULT_MISSING_GRACE_DAYS = 7


def _recipients_for_indicator(indicator):
    """Federal programme officers always; state admins when the indicator is state-scoped."""
    roles_query = User.objects.filter(is_active=True, role="federal_admin")
    users = list(roles_query)
    if indicator.owner_state_id:
        users += list(User.objects.filter(is_active=True, role="state_admin", state_id=indicator.owner_state_id))
    return [
        {
            "user_id": str(user.id),
            "email": user.email or "",
            "phone": getattr(user, "phone", "") or "",
            "recipient_type": user.role or "",
            "organization_id": str(user.organization_id) if user.organization_id else "",
            "organization_unit_id": str(user.unit_id) if user.unit_id else "",
        }
        for user in users
    ]


def _is_below_target(indicator, value, target):
    if value is None or target is None:
        return False
    if indicator.target_direction == KPITargetDirection.LOWER_BETTER:
        return Decimal(value) > Decimal(target)
    return Decimal(value) < Decimal(target)


class IndicatorAlertService:
    @classmethod
    def evaluate_indicator(cls, indicator, *, actor=None, notify=True):
        """Return the list of triggered alerts for one indicator (and optionally notify)."""
        alerts = []
        today = timezone.localdate()

        latest_value = indicator.values.order_by("-period_end", "-created_at").first()
        target = resolve_effective_target(indicator)

        if latest_value is not None:
            observed = latest_value.cumulative_value_numeric or latest_value.progress_value_numeric
            if _is_below_target(indicator, observed, target):
                alerts.append({
                    "trigger": "below_target",
                    "priority": NotificationPriority.HIGH,
                    "title": f"{indicator.indicator_name} is below target",
                    "message": (
                        f"{indicator.indicator_code} recorded {observed} against a target of {target} "
                        f"for the period ending {latest_value.period_end:%Y-%m-%d}."
                    ),
                })
            band = resolve_performance_band(indicator, observed)
            if band and band["severity"] == IndicatorThresholdSeverity.CRITICAL:
                alerts.append({
                    "trigger": "critical_band",
                    "priority": NotificationPriority.CRITICAL,
                    "title": f"{indicator.indicator_name} is in the critical band",
                    "message": (
                        f"{indicator.indicator_code} value {observed} falls in the '{band['band_name']}' band. "
                        f"{band.get('action_recommendation') or ''}"
                    ).strip(),
                })
        else:
            activated_recently = indicator.published_at and (today - indicator.published_at.date()).days < RESULT_MISSING_GRACE_DAYS
            if not activated_recently:
                alerts.append({
                    "trigger": "result_missing",
                    "priority": NotificationPriority.HIGH,
                    "title": f"{indicator.indicator_name} has no results",
                    "message": f"{indicator.indicator_code} is active but has no recorded results yet.",
                })

        latest_log = (
            MEIndicatorCalculationLog.objects.filter(indicator=indicator)
            .order_by("-created_at")
            .first()
        )
        if latest_log and latest_log.calculation_status == IndicatorCalculationStatus.FAILED:
            alerts.append({
                "trigger": "calculation_failed",
                "priority": NotificationPriority.CRITICAL,
                "title": f"{indicator.indicator_name} calculation failed",
                "message": f"{indicator.indicator_code}: {latest_log.error_message or 'Unknown calculation error.'}",
            })

        if notify and alerts:
            recipients = _recipients_for_indicator(indicator)
            for alert in alerts:
                if recipients:
                    NotificationService.send(
                        category=NotificationCategory.M_AND_E,
                        priority=alert["priority"],
                        title=alert["title"],
                        message=alert["message"],
                        action_url="/federal/performance-indicators/results",
                        recipients=recipients,
                        channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
                        related_object_type="MEIndicator",
                        related_object_id=str(indicator.id),
                    )
                log_action(
                    action=AuditAction.WORKFLOW_TRANSITION,
                    actor=actor,
                    target=indicator,
                    metadata={"event": "indicator_alert_triggered", "trigger": alert["trigger"]},
                )
        return alerts

    @classmethod
    def evaluate_all(cls, *, actor=None, notify=True):
        summary = {"evaluated": 0, "alerts": []}
        indicators = MEIndicator.objects.filter(status="active").select_related("owner_state")
        for indicator in indicators:
            triggered = cls.evaluate_indicator(indicator, actor=actor, notify=notify)
            summary["evaluated"] += 1
            for alert in triggered:
                summary["alerts"].append({
                    "indicator_id": str(indicator.id),
                    "indicator_code": indicator.indicator_code,
                    "trigger": alert["trigger"],
                })
        return summary
