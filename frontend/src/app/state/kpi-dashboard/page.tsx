"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Activity, AlertTriangle, BarChart3, Building2, CheckCircle2, Database, Globe, TrendingUp } from "lucide-react";

import { PortalShell } from "@/components/layout/portal-shell";
import { KPIDashboardFilters, type KPIDashboardFilterValues } from "@/features/standards/kpi-dashboard-filters";
import { KPITrendChart } from "@/features/standards/kpi-trend-chart";
import { KPIComparisonTable } from "@/features/standards/kpi-comparison-table";
import { KPIStateComparisonTable } from "@/features/standards/kpi-state-comparison";
import { KPIDisaggregationWidget, type DisaggregationItem } from "@/features/standards/kpi-disaggregation-widget";
import { getMEIndicatorDashboardSummary } from "@/lib/api/standards";

const DEFAULT_FILTERS: KPIDashboardFilterValues = {
  period_start: "",
  period_end: "",
  status: "",
  input_mode: "",
  data_source: "",
  state_id: "",
  lga_id: "",
  facility_type: "",
  test_center: "",
  certificate_status: "",
  test_status: "",
};

type DashboardTab = "overview" | "rankings" | "lga" | "alerts";

export default function StateKPIDashboardPage() {
  const [filters, setFilters] = useState<KPIDashboardFilterValues>(DEFAULT_FILTERS);
  const [activeTab, setActiveTab] = useState<DashboardTab>("overview");

  const params = useMemo(() => Object.fromEntries(
    Object.entries(filters).filter(([, value]) => value)
  ), [filters]);

  const { data: summary, isLoading } = useQuery({
    queryKey: ["kpi-state-dashboard", params],
    queryFn: () => getMEIndicatorDashboardSummary(params),
  });

  const sourceBreakdown = useMemo<DisaggregationItem[]>(() => {
    return Object.entries(summary?.source_breakdown ?? {})
      .filter(([, value]) => value > 0)
      .sort((a, b) => b[1] - a[1])
      .map(([key, value]) => ({
        dimension: key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
        value,
      }));
  }, [summary?.source_breakdown]);

  function updateFilter(field: keyof KPIDashboardFilterValues, value: string) {
    setFilters((current) => ({ ...current, [field]: value }));
  }

  function resetFilters() {
    setFilters(DEFAULT_FILTERS);
  }

  const cards = summary?.summary_cards ?? [];

  return (
    <PortalShell role="state_admin" title="State KPI Dashboard" description="State-level KPI performance: food handler certification, testing coverage, compliance, and facility indicators.">
      <div className="grid gap-5">
        {/* Filters */}
        <KPIDashboardFilters
          filters={filters}
          onChange={updateFilter}
          onReset={resetFilters}
          showGeography
          showFacilityFilters
        />

        {/* Tab Navigation */}
        <div className="flex gap-1 rounded-lg border border-neutral-200 bg-neutral-50 p-1 overflow-x-auto">
          {([
            { key: "overview", label: "Overview", Icon: BarChart3 },
            { key: "rankings", label: "KPI Rankings", Icon: Activity },
            { key: "lga", label: "LGA Comparison", Icon: Globe },
            { key: "alerts", label: "Alerts", Icon: AlertTriangle },
          ] as const).map(({ key, label, Icon }) => (
            <button
              key={key}
              type="button"
              onClick={() => setActiveTab(key as DashboardTab)}
              className={`inline-flex shrink-0 items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === key
                  ? "bg-white text-neutral-950 shadow-sm"
                  : "text-neutral-500 hover:text-neutral-700"
              }`}
            >
              <Icon size={16} />
              {label}
              {key === "alerts" && (summary?.alerts?.length ?? 0) > 0 ? (
                <span className="inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-danger-500 px-1.5 text-xs font-bold text-white">
                  {summary!.alerts.length}
                </span>
              ) : null}
            </button>
          ))}
        </div>

        {isLoading ? (
          <div className="rounded-lg border border-neutral-200 bg-white p-8 text-center text-sm text-neutral-500 shadow-sm">
            Loading state KPI dashboard...
          </div>
        ) : null}

        {/* Overview Tab */}
        {activeTab === "overview" && (
          <div className="grid gap-5">
            {/* Summary Cards */}
            <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4">
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
                <Database className="text-brand-700" size={18} />
                <p className="mt-2 text-xs font-bold uppercase text-neutral-500">State KPIs</p>
                <p className="text-2xl font-bold text-neutral-900">{isLoading ? "..." : cards.find((c) => c.key === "total")?.value ?? 0}</p>
                <p className="mt-1 text-xs text-neutral-400">Configured for state</p>
              </div>
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
                <Activity className="text-brand-700" size={18} />
                <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Active KPIs</p>
                <p className="text-2xl font-bold text-neutral-900">{isLoading ? "..." : cards.find((c) => c.key === "active")?.value ?? 0}</p>
                <p className="mt-1 text-xs text-neutral-400">Currently reportable</p>
              </div>
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
                <AlertTriangle className="text-warning-600" size={18} />
                <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Due for Reporting</p>
                <p className="text-2xl font-bold text-neutral-900">{isLoading ? "..." : cards.find((c) => c.key === "due")?.value ?? 0}</p>
                <p className="mt-1 text-xs text-neutral-400">Without approved values</p>
              </div>
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
                <CheckCircle2 className="text-brand-700" size={18} />
                <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Data Completeness</p>
                <p className="text-2xl font-bold text-neutral-900">{isLoading ? "..." : `${cards.find((c) => c.key === "completeness")?.value ?? 0}%`}</p>
                <p className="mt-1 text-xs text-neutral-400">KPIs with approved data</p>
              </div>
            </div>

            {/* Trend Chart */}
            <KPITrendChart
              trends={summary?.trends ?? []}
              title="State KPI Trend"
              subtitle="Aggregated approved KPI values by reporting period for this state."
            />

            {/* Bottom widgets */}
            <div className="grid gap-5 xl:grid-cols-2">
              <KPIDisaggregationWidget
                title="KPIs by Source"
                subtitle="Distribution by operational data source."
                items={sourceBreakdown}
                emptyMessage="No source coverage data yet."
              />
              <KPIDisaggregationWidget
                title="Certificate Status Distribution"
                subtitle="KPI values broken down by certification status."
                items={[
                  { dimension: "Facility-certified handlers", value: 0 },
                  { dimension: "Test coverage rate", value: 0 },
                  { dimension: "Certificate renewal rate", value: 0 },
                  { dimension: "Expiring certificates", value: 0 },
                ]}
                emptyMessage="Configure disaggregation by certificate status to populate this view."
              />
            </div>

            {/* Quick Links */}
            <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <h3 className="text-sm font-bold text-neutral-950">Facility KPIs</h3>
              <p className="mt-1 text-xs text-neutral-500">Navigate to facility-level and test center KPIs for detailed operational insights.</p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                {[
                  { icon: Building2, label: "Facility Certification", href: "#", value: "Coverage rates" },
                  { icon: TrendingUp, label: "Test Turnaround", href: "#", value: "Avg processing time" },
                  { icon: CheckCircle2, label: "Certificate Status", href: "#", value: "Valid / expiring / expired" },
                  { icon: Activity, label: "Pending Tests", href: "#", value: "Awaiting processing" },
                ].map((item) => (
                  <button
                    key={item.label}
                    type="button"
                    className="rounded-lg border border-neutral-200 p-4 text-left hover:bg-neutral-50 transition-colors"
                  >
                    <item.icon className="text-brand-700" size={18} />
                    <p className="mt-2 text-sm font-semibold text-neutral-900">{item.label}</p>
                    <p className="mt-1 text-xs text-neutral-500">{item.value}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Rankings Tab */}
        {activeTab === "rankings" && (
          <KPIComparisonTable
            title="State KPI Rankings"
            subtitle="KPIs ranked by achievement against target for this state."
            rows={(summary?.rankings ?? []).map((r) => ({
              id: r.id,
              name: r.name,
              code: r.code,
              latest_value: r.latest_value,
              target: r.target,
              achievement: r.achievement,
              status: r.status,
            }))}
            detailHref={(row) => `/state/kpi-dashboard/${row.id}`}
            emptyMessage="No KPI ranking data available for the selected filters."
          />
        )}

        {/* LGA Comparison Tab */}
        {activeTab === "lga" && (
          <div className="grid gap-5">
            <KPIStateComparisonTable
              rows={summary?.state_comparison ?? []}
              onDrilldown={(state) => {
                setFilters((current) => ({ ...current, state_id: state }));
                setActiveTab("overview");
              }}
            />
            {(!summary?.state_comparison?.length) ? (
              <div className="rounded-lg border border-dashed border-neutral-300 bg-neutral-50 p-8 text-center">
                <Globe className="mx-auto text-neutral-300" size={32} />
                <p className="mt-3 text-sm font-semibold text-neutral-700">LGA Comparison</p>
                <p className="mt-2 text-sm text-neutral-500">
                  LGA-level KPI comparison data is derived from disaggregated indicator values.
                  Ensure KPIs have LGA-level disaggregation configured.
                </p>
              </div>
            ) : null}
          </div>
        )}

        {/* Alerts Tab */}
        {activeTab === "alerts" && (
          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-neutral-950">State KPI Alerts</h3>
                <p className="mt-1 text-xs text-neutral-500">KPIs requiring attention for this state: due for reporting or below performance thresholds.</p>
              </div>
              {summary?.alerts?.length ? (
                <span className="rounded-full bg-danger-500 px-2.5 py-1 text-xs font-bold text-white">{summary.alerts.length} active</span>
              ) : null}
            </div>
            <div className="mt-4 space-y-2">
              {(summary?.alerts ?? []).map((alert, index) => (
                <div key={`${alert.indicator_id ?? index}-${alert.title}`} className={`rounded-md border px-4 py-3 ${
                  alert.severity === "critical" ? "border-danger-100 bg-danger-50 text-danger-700" :
                  alert.severity === "warning" ? "border-warning-100 bg-warning-50 text-warning-700" :
                  "border-info-100 bg-info-50 text-info-700"
                }`}>
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold">{alert.title}</p>
                    {alert.indicator_id ? (
                      <Link href={`/federal/standards/me-indicators/${alert.indicator_id}`} className="shrink-0 rounded border border-neutral-200 bg-white px-2 py-0.5 text-xs font-semibold text-neutral-700 hover:bg-neutral-50">
                        View KPI
                      </Link>
                    ) : null}
                  </div>
                  <p className="mt-1 text-xs">{alert.detail}</p>
                </div>
              ))}
              {!summary?.alerts?.length ? (
                <div className="rounded border border-dashed border-neutral-300 p-6 text-center text-sm text-neutral-500">
                  No alerts for the selected filters. All state KPIs are on track.
                </div>
              ) : null}
            </div>
          </div>
        )}
      </div>
    </PortalShell>
  );
}
