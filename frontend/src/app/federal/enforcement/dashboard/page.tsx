"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Building2, ClipboardCheck, Flag, TrendingUp, Users } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { EmbeddedAnalyticsActions } from "@/features/reports/embedded-analytics-actions";
import { fetchFederalEnforcementDashboard } from "@/lib/api/inspections";

type StateRow = { employer__state__name: string; total: number; this_month: number };
type NoticeRow = { employer__state__name: string; total: number; issued: number };

const cardsConfig: Array<{ key: string; label: string; icon: typeof Flag; color: string }> = [
  { key: "total_inspections", label: "Total Inspections (Nat.)", icon: ClipboardCheck, color: "text-blue-600" },
  { key: "inspections_this_month", label: "This Month", icon: TrendingUp, color: "text-brand-600" },
  { key: "open_enforcement_cases", label: "Open Cases", icon: Flag, color: "text-danger-500" },
  { key: "total_notices_issued", label: "Notices Issued", icon: AlertTriangle, color: "text-orange-500" },
  { key: "critical_findings_national", label: "Critical Findings", icon: AlertTriangle, color: "text-danger-500" },
  { key: "states_with_active_enforcement", label: "States Active", icon: Building2, color: "text-indigo-500" },
  { key: "active_inspectors", label: "Active Inspectors", icon: Users, color: "text-teal-500" },
];

export default function Page() {
  const query = useQuery({ queryKey: ["federal-enforcement-dashboard"], queryFn: fetchFederalEnforcementDashboard });
  const cards = (query.data?.cards || {}) as Record<string, unknown>;
  const charts = (query.data?.charts || {}) as Record<string, unknown>;
  const inspByState = Array.isArray(charts.inspections_by_state) ? charts.inspections_by_state as StateRow[] : null;
  const noticesByState = Array.isArray(charts.notices_by_state) ? charts.notices_by_state as NoticeRow[] : null;

  return (
    <PortalShell role="federal_admin" title="Federal enforcement" description="National aggregate oversight of inspections, enforcement actions, and state-level compliance.">
      <div className="grid gap-5">
        <EmbeddedAnalyticsActions moduleSource="inspections" openInDashboardBuilderHref="/federal/reports/dashboard-builder?module=inspections" />

        <section className="grid gap-3 grid-cols-2 md:grid-cols-4">
          {cardsConfig.map(({ key, label, icon: Icon, color }) => (
            <div key={key} className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="flex items-center gap-2"><Icon size={16} className={color} /><p className="text-xs font-bold uppercase text-neutral-500">{label}</p></div>
              <p className="mt-2 text-2xl font-bold text-neutral-900">{String(Number(cards[key]) || 0)}</p>
            </div>
          ))}
        </section>

        {inspByState && inspByState.length > 0 && (
          <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <h2 className="text-base font-bold text-neutral-900 mb-3">Inspections by State</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-neutral-50 text-left text-xs uppercase text-neutral-500">
                  <tr><th className="p-3">State</th><th className="p-3">Total</th><th className="p-3">This Month</th></tr>
                </thead>
                <tbody className="divide-y">
                  {inspByState.map((s) => (
                    <tr key={s.employer__state__name} className="hover:bg-neutral-50">
                      <td className="p-3 font-medium">{s.employer__state__name || "Unknown"}</td>
                      <td className="p-3">{s.total}</td>
                      <td className="p-3">{s.this_month}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {noticesByState && noticesByState.length > 0 && (
          <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <h2 className="text-base font-bold text-neutral-900 mb-3">Notices by State</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-neutral-50 text-left text-xs uppercase text-neutral-500">
                  <tr><th className="p-3">State</th><th className="p-3">Total</th><th className="p-3">Issued</th></tr>
                </thead>
                <tbody className="divide-y">
                  {noticesByState.map((s) => (
                    <tr key={s.employer__state__name} className="hover:bg-neutral-50">
                      <td className="p-3 font-medium">{s.employer__state__name || "Unknown"}</td>
                      <td className="p-3">{s.total}</td>
                      <td className="p-3">{s.issued}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </div>
    </PortalShell>
  );
}
