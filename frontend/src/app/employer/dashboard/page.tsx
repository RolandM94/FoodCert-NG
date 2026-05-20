"use client";

import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  BadgeCheck,
  BarChart3,
  Bell,
  Building2,
  ClipboardCheck,
  Clock3,
  ShieldAlert,
  ShieldCheck,
  Stethoscope,
  Syringe,
  UsersRound,
} from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { getEmployerDashboard } from "@/lib/api/employer-management";
import { listEmployers } from "@/lib/api/identity";
import { fetchUnits } from "@/lib/api/organizations";
import type { EmployerDashboardCards } from "@/types/employer-management";

function getBranchLock() {
  if (typeof window === "undefined") return { locked: false, unitId: "" };
  try {
    const token = localStorage.getItem("foodcert_access_token");
    const payload = token ? JSON.parse(atob(token.split(".")[1])) : {};
    const userMeta = localStorage.getItem("foodcert_user_meta");
    const parsed = userMeta ? JSON.parse(userMeta) : {};
    return {
      locked: Boolean(parsed.unit_restricted ?? payload.unit_restricted),
      unitId: String(parsed.unit || payload.unit || ""),
    };
  } catch {
    return { locked: false, unitId: "" };
  }
}

function metricLabel(value: keyof EmployerDashboardCards) {
  return value.replaceAll("_", " ");
}

function MetricCard({
  label,
  value,
  tone,
  icon: Icon,
}: {
  label: string;
  value: string | number;
  tone: string;
  icon: typeof UsersRound;
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <p className="text-xs font-bold uppercase tracking-wide text-slate-500">{label}</p>
        <Icon className={tone} size={18} />
      </div>
      <p className="mt-3 text-2xl font-bold text-slate-950">{value}</p>
    </div>
  );
}

function Bar({ label, value, max, detail }: { label: string; value: number; max: number; detail?: string }) {
  const width = max ? Math.max((value / max) * 100, value ? 6 : 0) : 0;
  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-4 text-sm">
        <span className="font-semibold text-slate-700">{label}</span>
        <span className="text-slate-500">{detail || value}</span>
      </div>
      <div className="h-2 rounded bg-slate-100">
        <div className="h-2 rounded bg-brand-green" style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}

function Panel({ title, icon: Icon, children }: { title: string; icon: typeof BarChart3; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-5 flex items-center gap-2">
        <Icon className="text-brand-deep" size={18} />
        <h2 className="text-base font-bold text-slate-950">{title}</h2>
      </div>
      {children}
    </section>
  );
}

export default function Page() {
  const [branch, setBranch] = useState("");
  const [branchLock, setBranchLock] = useState({ locked: false, unitId: "" });
  const employersQuery = useQuery({ queryKey: ["employers", "me"], queryFn: listEmployers });
  const employer = employersQuery.data?.[0];

  useEffect(() => {
    const lock = getBranchLock();
    setBranchLock(lock);
    if (lock.locked && lock.unitId) setBranch(lock.unitId);
  }, []);

  const unitsQuery = useQuery({
    queryKey: ["employer-units", employer?.organization],
    queryFn: () => fetchUnits(employer!.organization),
    enabled: Boolean(employer?.organization),
  });

  const dashboardQuery = useQuery({
    queryKey: ["employer-dashboard", employer?.id, branch],
    queryFn: () => getEmployerDashboard(employer!.id, branch ? { branch } : undefined),
    enabled: Boolean(employer?.id),
  });

  const dashboard = dashboardQuery.data;
  const branchRows = dashboard?.charts.branch_breakdown || [];
  const maxBranchHandlers = Math.max(...branchRows.map((row) => row.total_handlers), 1);
  const certMax = Math.max(...(dashboard?.charts.certificate_status_distribution || []).map((row) => row.count || 0), 1);
  const expiringMax = Math.max(dashboard?.cards.total_handlers || 0, 1);
  const illnessMax = Math.max(...(dashboard?.charts.illness_reports_trend || []).map((trend) => trend.count || 0), 1);
  const metrics = useMemo(() => {
    if (!dashboard) return [];
    const cards = dashboard.cards;
    return [
      ["total_handlers", cards.total_handlers, UsersRound, "text-slate-700"],
      ["fit", cards.fit, ShieldCheck, "text-brand-deep"],
      ["certification_pending", cards.certification_pending, Clock3, "text-amber-600"],
      ["expired_certificates", cards.expired_certificates, ShieldAlert, "text-rose-700"],
      ["expiring_soon", cards.expiring_soon, AlertTriangle, "text-amber-700"],
      ["expiring_7d", cards.expiring_7d, AlertTriangle, "text-rose-600"],
      ["temporarily_not_fit", cards.temporarily_not_fit, Stethoscope, "text-orange-700"],
      ["excluded", cards.excluded, ShieldAlert, "text-rose-700"],
      ["vaccination_due", cards.vaccination_due, Syringe, "text-sky-700"],
      ["active_branches", cards.active_branches, Building2, "text-slate-700"],
      ["open_inspections", cards.open_inspections, ClipboardCheck, "text-amber-700"],
      ["compliance_percentage", `${cards.compliance_percentage}%`, BadgeCheck, "text-brand-deep"],
    ] as const;
  }, [dashboard]);

  return (
    <PortalShell role="employer" title="Employer Dashboard" description="Monitor certification, vaccination, illness exclusions, inspections, and compliance by branch.">
      <div className="grid gap-6">
        <section className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-brand-deep">Scope</p>
            <p className="mt-1 text-sm text-slate-600">{branchLock.locked ? "Branch manager view is locked to the assigned branch." : "Head office can switch between all branches."}</p>
          </div>
          <select
            className="h-10 min-w-64 rounded border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700 disabled:bg-slate-50 disabled:text-slate-500"
            disabled={branchLock.locked}
            onChange={(event) => setBranch(event.target.value)}
            value={branch}
          >
            <option value="">All branches</option>
            {(unitsQuery.data || []).filter((unit) => unit.unit_type === "branch").map((unit) => (
              <option key={unit.id} value={unit.id}>{unit.name}</option>
            ))}
          </select>
        </section>

        {dashboard?.open_inspection_notices.length ? (
          <section className="rounded-lg border border-amber-200 bg-amber-50 p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 text-amber-700" size={20} />
              <div>
                <p className="font-bold text-amber-900">{dashboard.open_inspection_notices.length} open inspection notice{dashboard.open_inspection_notices.length === 1 ? "" : "s"}</p>
                <p className="mt-1 text-sm text-amber-800">{dashboard.open_inspection_notices[0].findings_summary || "Review recent inspection activity and respond where required."}</p>
              </div>
            </div>
          </section>
        ) : null}

        {dashboardQuery.isError ? <p className="rounded-lg bg-rose-50 p-4 text-sm font-semibold text-rose-700">Could not load employer dashboard.</p> : null}

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {metrics.map(([key, value, Icon, tone]) => (
            <MetricCard key={key} icon={Icon} label={metricLabel(key)} tone={tone} value={value} />
          ))}
        </section>

        <div className="grid gap-6 lg:grid-cols-2">
          <Panel icon={BarChart3} title="Compliance By Branch">
            <div className="grid gap-4">
              {branchRows.map((row) => (
                <Bar key={row.branch} detail={`${row.compliance_percentage}% compliant`} label={row.branch_name} max={maxBranchHandlers} value={row.total_handlers} />
              ))}
              {!branchRows.length ? <p className="text-sm text-slate-500">No branch compliance data yet.</p> : null}
            </div>
          </Panel>

          <Panel icon={BadgeCheck} title="Certificate Status">
            <div className="grid gap-4">
              {(dashboard?.charts.certificate_status_distribution || []).map((row) => (
                <Bar key={row.status} label={row.status?.replaceAll("_", " ") || "Unknown"} max={certMax} value={row.count || 0} />
              ))}
              {!dashboard?.charts.certificate_status_distribution.length ? <p className="text-sm text-slate-500">No certificates recorded yet.</p> : null}
            </div>
          </Panel>

          <Panel icon={Syringe} title="Vaccination Coverage">
            <div className="grid gap-4">
              {(dashboard?.charts.vaccination_coverage_summary || []).map((row) => (
                <div key={row.vaccine_type} className="grid gap-2 text-sm">
                  <p className="font-bold capitalize text-slate-950">{row.vaccine_type?.replaceAll("_", " ")}</p>
                  <div className="grid grid-cols-4 gap-2 text-center">
                    <span className="rounded bg-emerald-50 p-2 font-semibold text-brand-deep">Valid {row.valid || 0}</span>
                    <span className="rounded bg-rose-50 p-2 font-semibold text-rose-700">Expired {row.expired || 0}</span>
                    <span className="rounded bg-amber-50 p-2 font-semibold text-amber-700">Due {row.due || 0}</span>
                    <span className="rounded bg-slate-50 p-2 font-semibold text-slate-600">Missing {row.missing || 0}</span>
                  </div>
                </div>
              ))}
            </div>
          </Panel>

          <Panel icon={Clock3} title="Expiring Certificates">
            <div className="grid gap-4">
              {(dashboard?.charts.expiring_certificates_timeline || []).map((row) => (
                <Bar key={row.label} label={row.label || ""} max={expiringMax} value={row.count || 0} />
              ))}
            </div>
          </Panel>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Panel icon={Bell} title="Recent Activity">
            <div className="divide-y divide-slate-100">
              {(dashboard?.recent_activity || []).map((item) => (
                <div key={`${item.kind}-${item.id}`} className="py-3">
                  <p className="font-semibold text-slate-950">{item.title}</p>
                  <p className="mt-1 text-sm text-slate-600">{item.description}</p>
                </div>
              ))}
              {!dashboard?.recent_activity.length ? <p className="text-sm text-slate-500">No recent activity yet.</p> : null}
            </div>
          </Panel>

          <Panel icon={Stethoscope} title="Illness Reports Trend">
            <div className="grid gap-4">
              {(dashboard?.charts.illness_reports_trend || []).map((row) => (
                <Bar key={row.label} label={row.label || ""} max={illnessMax} value={row.count || 0} />
              ))}
            </div>
          </Panel>
        </div>
      </div>
    </PortalShell>
  );
}
