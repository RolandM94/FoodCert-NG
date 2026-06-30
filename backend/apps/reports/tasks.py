from celery import shared_task
from django.utils import timezone

from apps.locations.models import State
from apps.reports.models import DashboardExportJob, DataQualityIssue, DataQualityIssueSeverity, DataQualityIssueStatus, MEIndicator
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


@shared_task(name="reports.process_dashboard_export_job")
def process_dashboard_export_job(job_id):
    from apps.reports.views import build_published_dashboard_export_payload

    job = DashboardExportJob.objects.select_related("published_dashboard", "published_dashboard__canvas").get(id=job_id)
    job.status = "processing"
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at", "updated_at"])
    try:
        export_data = build_published_dashboard_export_payload(
            job.published_dashboard,
            job.export_format,
            job.block_id or None,
        )
        job.payload = export_data
        job.status = "completed"
        job.completed_at = timezone.now()
        job.error_message = ""
        job.save(update_fields=["payload", "status", "completed_at", "error_message", "updated_at"])
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        job.completed_at = timezone.now()
        job.save(update_fields=["status", "error_message", "completed_at", "updated_at"])
        raise
    return {"job_id": str(job.id), "status": job.status}
