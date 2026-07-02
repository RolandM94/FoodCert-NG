from django.core.management.base import BaseCommand

from apps.reports.models import KpiCardDefinition

# The shared, system-wide KPI card library. The first five entries mirror the
# legacy federal dashboard snapshot cards exactly (snapshot source = zero
# value drift); the rest are general-purpose dataset-driven cards.
KPI_CARD_SEEDS = [
    # --- Legacy federal snapshot cards (parity with /federal/dashboard) ---
    {
        "code": "states_adopted_declaration_template",
        "title": "States adopted",
        "category": "adoption",
        "icon": "ClipboardCheck",
        "source_type": "snapshot",
        "snapshot_key": "states_adopted_federal_declaration_template",
        "detail": "States with an adopted declaration template.",
        "allowed_account_types": ["federal"],
    },
    {
        "code": "states_on_latest_template_version",
        "title": "Latest version",
        "category": "adoption",
        "icon": "RefreshCw",
        "source_type": "snapshot",
        "snapshot_key": "states_using_latest_federal_template_version",
        "detail": "States currently aligned to the latest federal declaration version.",
        "allowed_account_types": ["federal"],
    },
    {
        "code": "states_pending_template_adoption",
        "title": "Pending adoption",
        "category": "adoption",
        "icon": "Clock3",
        "source_type": "snapshot",
        "snapshot_key": "states_pending_federal_template_adoption",
        "detail": "States still pending declaration template adoption.",
        "target": {"operator": "gt", "warning": 0, "critical": 10},
        "allowed_account_types": ["federal"],
    },
    {
        "code": "declarations_submitted_nationally",
        "title": "Declarations",
        "category": "declarations",
        "icon": "FileCheck2",
        "source_type": "snapshot",
        "snapshot_key": "declarations_submitted_nationally",
        "detail": "Total health declarations submitted nationally.",
        "allowed_account_types": ["federal"],
    },
    {
        "code": "declaration_risk_flags_total",
        "title": "Risk flags",
        "category": "risk",
        "icon": "AlertTriangle",
        "source_type": "snapshot",
        "snapshot_key": "risk_flags_total",
        "detail": "Total declaration risk flags across all reporting states.",
        "target": {"operator": "gt", "warning": 0, "critical": 25},
        "allowed_account_types": ["federal"],
    },
    # --- Workforce ---
    {
        "code": "food_handlers_total",
        "title": "Registered food handlers",
        "category": "workforce",
        "icon": "UsersRound",
        "dataset_code": "food_handlers",
        "aggregation": "count",
        "trend": {"compare_to": "prev_period", "window": "30d"},
        "detail": "All food handlers registered on the platform.",
    },
    {
        "code": "food_handlers_new_30d",
        "title": "New food handlers (30d)",
        "category": "workforce",
        "icon": "UsersRound",
        "dataset_code": "food_handlers",
        "aggregation": "count",
        "trend": {"compare_to": "prev_period", "window": "30d"},
        "detail": "Registrations in the last 30 days with prior-period comparison.",
    },
    # --- Certificates ---
    {
        "code": "certificates_total",
        "title": "Certificates issued",
        "category": "certificates",
        "icon": "BadgeCheck",
        "dataset_code": "certificates",
        "aggregation": "count",
        "trend": {"compare_to": "prev_period", "window": "30d"},
        "detail": "All food handler certificates ever issued.",
    },
    {
        "code": "certificates_active",
        "title": "Active certificates",
        "category": "certificates",
        "icon": "BadgeCheck",
        "dataset_code": "certificates",
        "aggregation": "count",
        "filters": [{"field": "status", "operator": "eq", "value": "active"}],
        "detail": "Certificates currently in active status.",
    },
    {
        "code": "certificates_expired",
        "title": "Expired certificates",
        "category": "certificates",
        "icon": "AlertTriangle",
        "dataset_code": "certificates",
        "aggregation": "count",
        "filters": [{"field": "status", "operator": "eq", "value": "expired"}],
        "target": {"operator": "gt", "warning": 50, "critical": 200},
        "detail": "Certificates that have lapsed and need renewal.",
    },
    {
        "code": "certificates_revoked",
        "title": "Revoked certificates",
        "category": "risk",
        "icon": "AlertTriangle",
        "dataset_code": "certificates",
        "aggregation": "count",
        "filters": [{"field": "status", "operator": "eq", "value": "revoked"}],
        "target": {"operator": "gt", "warning": 0, "critical": 20},
        "detail": "Certificates withdrawn for cause.",
    },
    # --- Employers ---
    {
        "code": "employers_total",
        "title": "Registered employers",
        "category": "employers",
        "icon": "Building2",
        "dataset_code": "employers",
        "aggregation": "count",
        "trend": {"compare_to": "prev_period", "window": "30d"},
        "detail": "Food businesses registered on the platform.",
    },
    {
        "code": "employers_compliant",
        "title": "Compliant employers",
        "category": "employers",
        "icon": "ShieldCheck",
        "dataset_code": "employers",
        "aggregation": "count",
        "filters": [{"field": "compliance_status", "operator": "eq", "value": "compliant"}],
        "detail": "Employers currently marked compliant.",
    },
    {
        "code": "employers_active",
        "title": "Active employers",
        "category": "employers",
        "icon": "Building2",
        "dataset_code": "employers",
        "aggregation": "count",
        "filters": [{"field": "is_active", "operator": "eq", "value": True}],
        "detail": "Employers with an active account.",
    },
    # --- Facilities ---
    {
        "code": "facilities_approved",
        "title": "Approved facilities",
        "category": "facilities",
        "icon": "Building2",
        "dataset_code": "medical_facilities",
        "aggregation": "count",
        "filters": [{"field": "accreditation_status", "operator": "eq", "value": "approved"}],
        "detail": "Medical facilities holding current accreditation.",
    },
    {
        "code": "facilities_suspended",
        "title": "Suspended facilities",
        "category": "risk",
        "icon": "AlertTriangle",
        "dataset_code": "medical_facilities",
        "aggregation": "count",
        "filters": [{"field": "accreditation_status", "operator": "eq", "value": "suspended"}],
        "target": {"operator": "gt", "warning": 0, "critical": 5},
        "detail": "Facilities whose accreditation is suspended.",
    },
    {
        "code": "facility_capacity_avg",
        "title": "Avg service capacity",
        "category": "facilities",
        "icon": "Activity",
        "dataset_code": "medical_facilities",
        "metric": "service_capacity",
        "aggregation": "avg",
        "detail": "Average declared assessment capacity per facility.",
    },
    # --- Inspections ---
    {
        "code": "inspections_total_30d_trend",
        "title": "Inspections",
        "category": "inspections",
        "icon": "ClipboardCheck",
        "dataset_code": "inspections",
        "aggregation": "count",
        "trend": {"compare_to": "prev_period", "window": "30d"},
        "detail": "All inspections with a 30-day prior-period comparison.",
    },
    {
        "code": "inspections_avg_compliance_score",
        "title": "Avg compliance score",
        "category": "inspections",
        "icon": "Scale",
        "dataset_code": "inspections",
        "metric": "compliance_score",
        "aggregation": "avg",
        "format": "percent",
        "target": {"operator": "lt", "warning": 70, "critical": 50},
        "detail": "Mean inspection compliance score across businesses.",
    },
    # --- Finance ---
    {
        "code": "payments_volume",
        "title": "Payment transactions",
        "category": "finance",
        "icon": "Banknote",
        "dataset_code": "payment_transactions",
        "aggregation": "count",
        "trend": {"compare_to": "prev_period", "window": "30d"},
        "detail": "All payment transactions processed.",
        "allowed_account_types": ["federal"],
    },
    {
        "code": "payments_success_amount",
        "title": "Collected revenue",
        "category": "finance",
        "icon": "Banknote",
        "dataset_code": "payment_transactions",
        "metric": "amount",
        "aggregation": "sum",
        "format": "currency",
        "filters": [{"field": "status", "operator": "eq", "value": "success"}],
        "trend": {"compare_to": "prev_period", "window": "30d", "date_field": "paid_at"},
        "detail": "Total successfully collected payments.",
        "allowed_account_types": ["federal"],
    },
    # --- Indicators ---
    {
        "code": "performance_indicators_active",
        "title": "Active indicators",
        "category": "indicators",
        "icon": "Gauge",
        "dataset_code": "performance_indicators",
        "aggregation": "count",
        "filters": [{"field": "lifecycle_status", "operator": "eq", "value": "active"}],
        "detail": "Performance indicators currently active in the national library.",
    },
]


class Command(BaseCommand):
    help = "Seed the shared KPI card library (legacy dashboard cards + general-purpose catalog)."

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for seed in KPI_CARD_SEEDS:
            _, was_created = KpiCardDefinition.objects.update_or_create(
                code=seed["code"],
                defaults={**{key: value for key, value in seed.items() if key != "code"}, "is_system": True},
            )
            created += int(was_created)
            updated += int(not was_created)
        self.stdout.write(self.style.SUCCESS(
            f"Seeded KPI card library: {created} created, {updated} updated ({len(KPI_CARD_SEEDS)} total)."
        ))
