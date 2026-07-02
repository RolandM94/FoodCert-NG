"""Scheduled jobs for the Performance Indicators engine."""

from celery import shared_task


@shared_task(name="standards.run_performance_indicator_calculations")
def run_performance_indicator_calculations():
    """Recalculate automatic/hybrid KPIs and evaluate indicator alerts.

    Runs daily via Celery beat. Calculation failures are captured per
    indicator by the engine (and surface as calculation_failed alerts)
    rather than aborting the batch.
    """
    from apps.standards.indicator_alerts import IndicatorAlertService
    from apps.standards.kpi_engine import FoodHandlersKpiCalculationService

    calculation_summary = FoodHandlersKpiCalculationService.recalculate_automatic_kpis()
    alert_summary = IndicatorAlertService.evaluate_all()
    return {
        "calculated": len(calculation_summary.get("success", [])),
        "calculation_failures": len(calculation_summary.get("failed", [])),
        "indicators_evaluated": alert_summary.get("evaluated", 0),
        "alerts_triggered": len(alert_summary.get("alerts", [])),
    }
