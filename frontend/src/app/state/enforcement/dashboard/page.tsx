"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, ClipboardCheck, Flag, GitBranch, SearchCheck, Shield, TrendingUp, BarChart3 } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { fetchStateEnforcementDashboard } from "@/lib/api/inspections";

const cardsConfig: Array<{ key: string; label: string; icon: typeof Shield; color: string }> = [
  { key: "total_inspections", label: "Total Inspections", icon: ClipboardCheck, color: "text-blue-600" },
  { key: "inspections_this_month", label: "This Month", icon: BarChart3, color: "text-brand-600" },
  { key: "open_cases", label: "Open Cases", icon: Flag, color: "text-danger-500" },
  { key: "notices_issued", label: "Notices Issued", icon: AlertTriangle, color: "text-orange-500" },
  { key: "overdue_corrective_actions", label: "Overdue Actions", icon: SearchCheck, color: "text-pink-500" },
  { key: "critical_findings", label: "Critical Findings", icon: Shield, color: "text-danger-500" },
  { key: "follow_ups_pending", label: "Follow-Ups Pending", icon: GitBranch, color: "text-teal-500" },
  { key: "inspectors_active", label: "Active Inspectors", icon: TrendingUp, color: "text-indigo-500" },
];

function num(v: unknown): number {
  return typeof v === "number" ? v : 0;
}

export default function Page() {
  const query = useQuery({ queryKey: ["state-enforcement-dashboard"], queryFn: () => fetchStateEnforcementDashboard() });
  const cards = (query.data?.cards || {}) as Record<string, unknown>;
  const charts = (query.data?.charts || {}) as Record<string, unknown>;
  const findings = Array.isArray(charts.findings_by_severity) ? charts.findings_by_severity as Array<{ severity: string; count: number }> : null;
  const lgaData = Array.isArray(charts.inspections_by_lga) ? charts.inspections_by_lga as Array<{ employer__lga__name: string; count: number }> : null;

  return (
    <PortalShell role="state_admin" title="State enforcement" description="Oversight dashboard for inspections, enforcement notices, cases, and compliance across the state.">
      <div className="grid gap-5">
        <section className="grid gap-3 grid-cols-2 md:grid-cols-4">
          {cardsConfig.map(({ key, label, icon: Icon, color }) => (
            <div key={key} className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="flex items-center gap-2"><Icon size={16} className={color} /><p className="text-xs font-bold uppercase text-neutral-500">{label}</p></div>
              <p className="mt-2 text-2xl font-bold text-neutral-900">{num(cards[key])}</p>
            </div>
          ))}
        </section>

        {findings && findings.length > 0 && (
          <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <h2 className="text-base font-bold text-neutral-900 mb-3">Findings by Severity</h2>
            <div className="grid gap-2">
              {findings.map((item) => (
                <div key={item.severity} className="flex items-center justify-between rounded bg-neutral-50 px-3 py-2">
                  <span className="text-sm font-medium text-neutral-700 capitalize">{item.severity}</span>
                  <span className="rounded-full bg-neutral-200 px-2 py-0.5 text-xs font-bold">{item.count}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {lgaData && lgaData.length > 0 && (
          <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <h2 className="text-base font-bold text-neutral-900 mb-3">Inspections by LGA (Top 10)</h2>
            <div className="grid gap-2">
              {lgaData.slice(0, 10).map((item) => (
                <div key={item.employer__lga__name} className="flex items-center justify-between rounded bg-neutral-50 px-3 py-2">
                  <span className="text-sm font-medium text-neutral-700">{item.employer__lga__name || "Unknown"}</span>
                  <span className="rounded-full bg-brand-600/20 px-2 py-0.5 text-xs font-bold text-brand-700">{item.count}</span>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </PortalShell>
  );
}
