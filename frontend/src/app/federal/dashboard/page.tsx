"use client";

import { useCallback, useEffect, useState } from "react";
import { AlertCircle, BadgeCheck, Building2, Flag, ShieldCheck, TrendingUp, Users } from "lucide-react";

import { ChartCard, KPICard } from "@/components/dashboards";
import { PortalShell } from "@/components/layout/portal-shell";
import { apiClient } from "@/lib/api/client";

interface FederalDashboardData {
  cards: Record<string, number | string>;
  charts: {
    compliance_by_state: Array<{ state__name: string; total: number; certified: number }>;
    state_comparison_table: Array<Record<string, number | string>>;
    certification_coverage_by_state: Array<{ state_name: string; state_code: string; coverage: number }>;
    facility_accreditation_by_state: Array<Record<string, number>>;
    vaccination_coverage_by_state: Array<Record<string, number>>;
    state_report_submission_status: Array<Record<string, number | string>>;
    approved_facilities_by_state: Array<{ state__name: string; total: number }>;
    food_handler_categories: Array<{ food_handler_category: string; total: number }>;
    establishment_categories: Array<{ establishment_category: string; total: number }>;
    vaccination_coverage: Record<string, number>;
    illness_trends: Array<{ month: string; total: number }>;
    inspection_trends: Array<{ month: string; total: number }>;
  };
}

export default function Page() {
  const [data, setData] = useState<FederalDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await apiClient.get("/dashboard/federal/");
      setData(res.data.data);
    } catch {
      setError("Could not load federal dashboard.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const complianceBadge = (status: string) => {
    const map: Record<string, string> = { compliant: "bg-brand-100 text-brand-800", partially_compliant: "bg-warning-100 text-warning-700", non_compliant: "bg-danger-100 text-danger-700", high_risk: "bg-danger-500 text-white" };
    return <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-bold ${map[status] || "bg-neutral-100 text-neutral-600"}`}>{status?.replaceAll("_", " ") ?? "N/A"}</span>;
  };

  return (
    <PortalShell role="federal_admin" title="National Dashboard" description="Federal oversight: national certification, state performance, M&E indicators, and compliance analytics.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading national dashboard...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}

        <section className="grid gap-3 sm:grid-cols-2 md:grid-cols-4">
          <KPICard label="Coverage" value={`${data?.cards?.national_certification_coverage ?? "—"}%`} icon={BadgeCheck} subtitle="Certification" />
          <KPICard label="Food Handlers" value={data?.cards?.certified_food_handlers ?? 0} icon={Users} subtitle={`${data?.cards?.registered_food_handlers ?? 0} registered`} />
          <KPICard label="Facilities" value={data?.cards?.approved_facilities ?? 0} icon={Building2} subtitle="Approved" />
          <KPICard label="Vaccination" value={`${data?.cards?.national_vaccination_coverage ?? "—"}%`} icon={ShieldCheck} subtitle="Coverage" />
          <KPICard label="Illness Reports" value={data?.cards?.national_illness_reports ?? 0} icon={Flag} />
          <KPICard label="Inspections" value={data?.cards?.national_inspection_count ?? 0} icon={TrendingUp} />
          <KPICard label="Active States" value={data?.cards?.states_with_active_implementation ?? 0} icon={Users} subtitle="Implementing" />
          <KPICard label="Overdue Reports" value={data?.cards?.states_with_overdue_reports ?? 0} icon={AlertCircle} subtitle="States" />
        </section>

        {data?.cards?.overall_compliance_status ? (
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm flex items-center gap-3">
            <p className="text-sm text-neutral-500">National Compliance Status:</p>
            {complianceBadge(String(data.cards.overall_compliance_status))}
          </div>
        ) : null}

        <div className="grid gap-5 lg:grid-cols-2">
          <ChartCard title="Certification Coverage by State">
            {data?.charts?.certification_coverage_by_state?.length ? (
              <div className="space-y-2">
                {data.charts.certification_coverage_by_state.slice(0, 10).map((s) => (
                  <div className="flex items-center gap-3 text-sm" key={s.state_code}>
                    <p className="w-32 truncate font-medium text-neutral-700">{s.state_name || "Unknown"}</p>
                    <div className="flex-1 rounded-full bg-neutral-100 h-2">
                      <div className="rounded-full bg-brand-600 h-2" style={{ width: `${s.coverage || 0}%` }} />
                    </div>
                    <p className="w-12 text-right text-xs font-bold text-neutral-500">{s.coverage ?? 0}%</p>
                  </div>
                ))}
              </div>
            ) : <p className="text-sm text-neutral-500">No state data available.</p>}
          </ChartCard>

          <ChartCard title="Facility Accreditation by State">
            {data?.charts?.approved_facilities_by_state?.length ? (
              <div className="space-y-2">
                {data.charts.approved_facilities_by_state.slice(0, 10).map((s) => (
                  <div className="flex items-center gap-3 text-sm" key={s.state__name}>
                    <p className="w-32 truncate font-medium text-neutral-700">{s.state__name || "Unknown"}</p>
                    <div className="flex-1 rounded-full bg-neutral-100 h-2">
                      <div className="rounded-full bg-info-500 h-2" style={{ width: `${Math.min((s.total || 0) * 20, 100)}%` }} />
                    </div>
                    <p className="w-12 text-right text-xs font-bold text-neutral-500">{s.total ?? 0}</p>
                  </div>
                ))}
              </div>
            ) : <p className="text-sm text-neutral-500">No facility data.</p>}
          </ChartCard>
        </div>

        <ChartCard title="State Comparison Table" subtitle="Registered handlers, certificates, facilities, compliance status per state">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-neutral-200 text-left text-xs font-bold uppercase text-neutral-500">
                  <th className="p-3">State</th>
                  <th className="p-3">Handlers</th>
                  <th className="p-3">Certified</th>
                  <th className="p-3">Coverage</th>
                  <th className="p-3">Facilities</th>
                  <th className="p-3">Employers</th>
                  <th className="p-3">Inspections</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200">
                {data?.charts?.state_comparison_table?.length ? (
                  data.charts.state_comparison_table.slice(0, 15).map((row, i) => (
                    <tr className="hover:bg-neutral-50" key={String(row.state_id ?? i)}>
                      <td className="p-3 font-bold text-neutral-900">{row.state_name as string || "Unknown"}</td>
                      <td className="p-3">{row.registered_handlers ?? 0}</td>
                      <td className="p-3">{row.certified_handlers ?? 0}</td>
                      <td className="p-3">{row.certification_coverage ?? 0}%</td>
                      <td className="p-3">{row.approved_facilities ?? 0}</td>
                      <td className="p-3">{row.registered_employers ?? 0}</td>
                      <td className="p-3">{row.inspection_count ?? 0}</td>
                    </tr>
                  ))
                ) : (
                  <tr><td className="p-3 text-neutral-500" colSpan={7}>No state comparison data yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </ChartCard>
      </div>
    </PortalShell>
  );
}
