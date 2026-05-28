from celery import shared_task
from django.utils import timezone

from apps.locations.models import State
from apps.reports.models import DataQualityIssue, DataQualityIssueSeverity, DataQualityIssueStatus, MEIndicator
from apps.reports.services import MEIndicatorService


@shared_task(name="reports.run_me_indicator_calculations")
def run_me_indicator_calculations(run_date=None):
    run_day = timezone.datetime.fromisoformat(run_date).date() if run_date else timezone.localdate()
    period_start = run_day
    period_end = run_day
    indicators = list(MEIndicator.objects.filter(is_active=True, reporting_frequency__in=["daily", "weekly"]).order_by("category", "code"))
    if run_day.day == 1:
        month_end = run_day - timezone.timedelta(days=1)
        period_start = month_end.replace(day=1)
        period_end = month_end
        indicators.extend(MEIndicator.objects.filter(is_active=True, reporting_frequency="monthly").order_by("category", "code"))
    states = list(State.objects.order_by("name"))
    calculated = []
    for indicator in indicators:
        calculated.append(MEIndicatorService.calculate_indicator(indicator, period_start=period_start, period_end=period_end))
        for state in states:
            calculated.append(MEIndicatorService.calculate_indicator(indicator, state=state, period_start=period_start, period_end=period_end))
    alerts = [create_threshold_alert(value) for value in calculated if threshold_breached(value)]
    for state in states:
        MEIndicatorService.get_state_performance(state.id)
    MEIndicatorService.get_national_summary()
    return {
        "date": run_day.isoformat(),
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "indicators": len(indicators),
        "values": len(calculated),
        "alerts": sum(1 for alert in alerts if alert is not None),
        "states_warmed": len(states),
    }


def threshold_breached(value):
    indicator = value.indicator
    if indicator.critical_threshold is not None and value.calculated_value < indicator.critical_threshold:
        return True
    if indicator.warning_threshold is not None and value.calculated_value < indicator.warning_threshold:
        return True
    return False


def create_threshold_alert(value):
    indicator = value.indicator
    severity = DataQualityIssueSeverity.HIGH
    threshold = indicator.warning_threshold
    if indicator.critical_threshold is not None and value.calculated_value < indicator.critical_threshold:
        severity = DataQualityIssueSeverity.CRITICAL
        threshold = indicator.critical_threshold
    issue, _created = DataQualityIssue.objects.update_or_create(
        issue_type="me_threshold_breach",
        module="reports",
        target_type="me_indicator",
        target_id=indicator.id,
        state=value.state,
        organization=value.organization,
        status=DataQualityIssueStatus.OPEN,
        defaults={
            "severity": severity,
            "description": f"{indicator.name} is below threshold for {value.period_start} to {value.period_end}.",
            "metadata": {
                "indicator_code": indicator.code,
                "calculated_value": str(value.calculated_value),
                "threshold": str(threshold),
                "period_start": value.period_start.isoformat(),
                "period_end": value.period_end.isoformat(),
            },
        },
    )
    return issue
