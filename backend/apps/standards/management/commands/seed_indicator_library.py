from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.standards.models import (
    IndicatorLifecycleStatus,
    IndicatorOwnerType,
    IndicatorScopeType,
    IndicatorTarget,
    IndicatorTargetSource,
    IndicatorThreshold,
    IndicatorThresholdSeverity,
    IndicatorVisibility,
    MEIndicator,
    PolicyVersion,
    PolicyVersionType,
    StandardStatus,
)

# (code, name, category, unit, direction, target, higher_is_better)
NATIONAL_INDICATORS = [
    ("PI-NAT-CERT-COVERAGE", "National Certificate Coverage Rate", "coverage", "percentage", "higher_better", 90, True),
    ("PI-NAT-FACILITY-COVERAGE", "Accredited Facility Coverage Rate", "capacity", "percentage", "higher_better", 80, True),
    ("PI-NAT-INSPECTION-COMPLETION", "Inspection Completion Rate", "inspections", "percentage", "higher_better", 85, True),
    ("PI-NAT-CAPA-CLOSURE", "Corrective Action Closure Rate", "enforcement", "percentage", "higher_better", 90, True),
    ("PI-NAT-REPORTING-COMPLIANCE", "State Reporting Compliance Rate", "governance", "percentage", "higher_better", 95, True),
    ("PI-NAT-TEMPLATE-ADOPTION", "Federal Template Adoption Rate", "governance", "percentage", "higher_better", 100, True),
    ("PI-NAT-CERT-TURNAROUND", "Average Certificate Issuance Turnaround Time", "timeliness", "days", "lower_better", 3, False),
    ("PI-NAT-EMPLOYER-COMPLIANCE", "Employer Compliance Coverage Rate", "compliance", "percentage", "higher_better", 85, True),
]

STATE_INDICATORS = [
    ("PI-ST-LGA-COVERAGE", "Food Handler Certificate Coverage by LGA", "coverage", "percentage", "higher_better", 90, True),
    ("PI-ST-PENDING-VALIDATION", "Pending Certificate Validation Rate", "operations", "percentage", "lower_better", 10, False),
    ("PI-ST-EXPIRED-RATE", "Expired Certificate Rate", "compliance", "percentage", "lower_better", 5, False),
    ("PI-ST-OVERDUE-INSPECTION", "Overdue Inspection Rate", "inspections", "percentage", "lower_better", 10, False),
]


class Command(BaseCommand):
    help = "Seed the default Performance Indicators library (national + state) with targets and thresholds."

    def _percentage_bands(self, indicator, higher_is_better):
        if higher_is_better:
            bands = [
                ("Green", IndicatorThresholdSeverity.GOOD, 90, None, "#16A34A", "Meeting target"),
                ("Amber", IndicatorThresholdSeverity.WARNING, 70, 89.9999, "#D97706", "Below target"),
                ("Red", IndicatorThresholdSeverity.CRITICAL, None, 69.9999, "#DC2626", "Critical - escalate"),
            ]
        else:
            bands = [
                ("Green", IndicatorThresholdSeverity.GOOD, None, 10, "#16A34A", "Within acceptable range"),
                ("Amber", IndicatorThresholdSeverity.WARNING, 10.0001, 20, "#D97706", "Elevated"),
                ("Red", IndicatorThresholdSeverity.CRITICAL, 20.0001, None, "#DC2626", "Critical - escalate"),
            ]
        for name, severity, lo, hi, color, action in bands:
            IndicatorThreshold.objects.get_or_create(
                indicator=indicator, scope_type=IndicatorScopeType.NATIONAL, band_name=name,
                defaults={
                    "severity": severity, "min_value": lo, "max_value": hi,
                    "color": color, "label": name, "action_recommendation": action,
                },
            )

    def _days_bands(self, indicator, target):
        bands = [
            ("Green", IndicatorThresholdSeverity.GOOD, None, target, "#16A34A", "On time"),
            ("Amber", IndicatorThresholdSeverity.WARNING, target + 0.0001, target * 2, "#D97706", "Delayed"),
            ("Red", IndicatorThresholdSeverity.CRITICAL, target * 2 + 0.0001, None, "#DC2626", "Critical delay"),
        ]
        for name, severity, lo, hi, color, action in bands:
            IndicatorThreshold.objects.get_or_create(
                indicator=indicator, scope_type=IndicatorScopeType.NATIONAL, band_name=name,
                defaults={
                    "severity": severity, "min_value": lo, "max_value": hi,
                    "color": color, "label": name, "action_recommendation": action,
                },
            )

    def _seed_indicator(self, policy, code, name, category, unit, direction, target, higher_is_better, owner_type, visibility):
        indicator, created = MEIndicator.objects.get_or_create(
            policy_version=policy, indicator_code=code,
            defaults={
                "indicator_name": name,
                "description": f"{name} (default library indicator).",
                "unit_of_measurement": unit,
                "target_direction": direction,
                "data_source": "manual",
                "reporting_frequency": "monthly",
                "visualization_type": "card",
                "category": category,
                "owner_type": owner_type,
                "visibility": visibility,
                "lifecycle_status": IndicatorLifecycleStatus.ACTIVE,
                "status": StandardStatus.ACTIVE,
                "version": "1.0",
                "target_value": target,
                "federal_dashboard_visible": True,
                "state_dashboard_visible": True,
                "dashboard_enabled": True,
                "report_enabled": True,
                "ai_enabled": True,
                "published_at": timezone.now(),
            },
        )
        if not created:
            return indicator, False
        IndicatorTarget.objects.get_or_create(
            indicator=indicator, scope_type=IndicatorScopeType.NATIONAL, scope_id="",
            defaults={"target_value": target, "target_unit": unit, "source": IndicatorTargetSource.FEDERAL_DEFAULT},
        )
        if unit == "days":
            self._days_bands(indicator, target)
        else:
            self._percentage_bands(indicator, higher_is_better)
        return indicator, True

    def handle(self, *args, **options):
        policy, _ = PolicyVersion.objects.get_or_create(
            version_code="PI-LIB-2026",
            defaults={
                "title": "Performance Indicators Library",
                "description": "Container policy version for the default Performance Indicators library.",
                "version_type": PolicyVersionType.MAJOR,
                "status": "active",
                "change_summary": "Default indicator library.",
            },
        )
        created = 0
        for code, name, category, unit, direction, target, higher in NATIONAL_INDICATORS:
            _, was_created = self._seed_indicator(
                policy, code, name, category, unit, direction, target, higher,
                IndicatorOwnerType.FEDERAL, IndicatorVisibility.FEDERAL_STANDARD,
            )
            created += int(was_created)
        for code, name, category, unit, direction, target, higher in STATE_INDICATORS:
            _, was_created = self._seed_indicator(
                policy, code, name, category, unit, direction, target, higher,
                IndicatorOwnerType.STATE, IndicatorVisibility.STATE_OWNED,
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f"Seeded Performance Indicators library: {created} new indicators "
            f"({len(NATIONAL_INDICATORS)} national + {len(STATE_INDICATORS)} state templates) with targets and thresholds."
        ))
