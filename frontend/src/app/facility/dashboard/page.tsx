"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, Award, Banknote, CalendarDays, ClipboardList, FlaskConical, RefreshCw, ShieldCheck } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { getCurrentMedicalFacility } from "@/lib/api/facilities";
import { getFacilityDashboard } from "@/lib/api/reports";
import type { DashboardPayload } from "@/types/reports";
import type { MedicalFacility } from "@/types/facilities";

type ChartRow = { status?: string; lab_status?: string; final_decision?: string; settlement_status?: string; total: number };

function numberLabel(value: unknown) {
  return new Intl.NumberFormat("en-NG").format(Number(value || 0));
}

function money(value: unknown) {
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(Number(value || 0));
}

function label(value?: string) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

export default function Page() {
  const [facility, setFacility] = useState<MedicalFacility | null>(null);
  const [dashboard, setDashboard] = useState<DashboardPayload | null>(null);
  const [filters, setFilters] = useState({ date_from: "", date_to: "", lab_status: "", assessment_status: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const params = useMemo(() => Object.fromEntries(Object.entries(filters).filter(([, value]) => value)), [filters]);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const profile = await getCurrentMedicalFacility();
      const row = await getFacilityDashboard({ ...params, facility: profile.id });
      setFacility(profile);
      setDashboard(row);
    } catch {
      setError("Could not load facility dashboard.");
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const cards = dashboard?.cards || {};
  const assessmentStatus = (dashboard?.charts?.assessment_status || []) as ChartRow[];
  const labStatus = (dashboard?.charts?.lab_status || []) as ChartRow[];
  const decisions = (dashboard?.charts?.decision_distribution || []) as ChartRow[];
  const queues = dashboard?.sections?.queue_summary || [];
  const recent = dashboard?.sections?.recent_assessments || [];

  return (
    <PortalShell role="facility_admin" title="Facility dashboard" description="Monitor appointments, assessments, lab work, State validation, certificates, and settlements.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading dashboard...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}

        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 lg:grid-cols-[170px_170px_190px_210px_auto]">
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" type="date" value={filters.date_from} onChange={(event) => setFilters((current) => ({ ...current, date_from: event.target.value }))} />
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" type="date" value={filters.date_to} onChange={(event) => setFilters((current) => ({ ...current, date_to: event.target.value }))} />
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={filters.lab_status} onChange={(event) => setFilters((current) => ({ ...current, lab_status: event.target.value }))}>
              <option value="">All lab states</option><option value="pending">Pending</option><option value="submitted">Submitted</option><option value="reviewed">Reviewed</option>
            </select>
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={filters.assessment_status} onChange={(event) => setFilters((current) => ({ ...current, assessment_status: event.target.value }))}>
              <option value="">All assessment states</option><option value="payment_confirmed">Payment confirmed</option><option value="physical_exam_completed">Exam complete</option><option value="fit">Fit</option><option value="submitted_for_state_validation">Submitted to State</option>
            </select>
            <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-600 px-3 text-sm font-bold text-white" type="button" onClick={() => void loadData()}><RefreshCw size={16} /> Refresh</button>
          </div>
        </section>

        <section className="grid gap-3 md:grid-cols-4">
          {[
            ["Appointments today", cards.appointments_today, CalendarDays],
            ["In progress", cards.assessments_in_progress, ClipboardList],
            ["Lab pending", cards.pending_lab_results, FlaskConical],
            ["Certificates issued", cards.certificates_issued, Award],
            ["State clarifications", cards.state_clarifications, ShieldCheck],
            ["Not-fit reports", cards.not_fit_reports, ClipboardList],
            ["Pending settlements", cards.pending_settlements, Banknote],
            ["Settled amount", money(cards.settled_amount), Banknote],
          ].map(([title, value, Icon]) => {
            const MetricIcon = Icon as typeof ClipboardList;
            return (
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm" key={title as string}>
                <MetricIcon className="text-brand-700" size={18} />
                <p className="mt-2 text-xs font-bold uppercase text-neutral-500">{title as string}</p>
                <p className="text-xl font-bold text-neutral-900">{typeof value === "number" ? numberLabel(value) : String(value ?? "0")}</p>
              </div>
            );
          })}
        </section>

        <section className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-bold text-neutral-900">{facility?.facility_name || "Facility"} queues</h2>
            <div className="mt-4 grid gap-2">
              {queues.map((queue) => (
                <Link className="flex items-center justify-between rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm font-semibold text-neutral-700" href={String(queue.href || "/facility/dashboard")} key={String(queue.name)}>
                  <span>{queue.name}</span><span className="font-bold text-neutral-900">{queue.count}</span>
                </Link>
              ))}
            </div>
            <div className="mt-4 rounded border border-neutral-200 bg-neutral-50 p-3 text-sm text-neutral-700">
              Accreditation: <span className="font-bold capitalize">{label(String(cards.accreditation_status || ""))}</span>
              <p className="mt-1 text-xs text-neutral-500">Re-accreditation countdown: {cards.reaccreditation_countdown_days ?? "Not set"} days</p>
            </div>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-bold text-neutral-900">Operational distributions</h2>
            <div className="mt-4 grid gap-4 md:grid-cols-3">
              {[["Assessments", assessmentStatus, "status"], ["Lab", labStatus, "lab_status"], ["Decisions", decisions, "final_decision"]].map(([title, rows, key]) => (
                <div className="rounded border border-neutral-200 bg-neutral-50 p-3" key={title as string}>
                  <p className="text-xs font-bold uppercase text-neutral-500">{title as string}</p>
                  <div className="mt-2 grid gap-2">
                    {(rows as ChartRow[]).length ? (rows as ChartRow[]).map((row) => (
                      <div className="flex items-center justify-between text-xs" key={String(row[key as keyof ChartRow])}>
                        <span className="capitalize text-neutral-600">{label(String(row[key as keyof ChartRow] || ""))}</span>
                        <span className="font-bold text-neutral-900">{row.total}</span>
                      </div>
                    )) : <p className="text-xs text-neutral-500">No data</p>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
          <div className="border-b border-neutral-200 p-4">
            <h2 className="text-sm font-bold text-neutral-900">Recent assessments</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-neutral-50 text-xs font-bold uppercase text-neutral-500">
                <tr><th className="p-3">Food handler</th><th className="p-3">Status</th><th className="p-3">Decision</th><th className="p-3">Doctor</th></tr>
              </thead>
              <tbody className="divide-y divide-neutral-200">
                {recent.length ? recent.map((row) => (
                  <tr key={String(row.id)}>
                    <td className="p-3 font-bold text-neutral-900">{row.food_handler}</td>
                    <td className="p-3"><StatusBadge status={String(row.status || "")} /></td>
                    <td className="p-3"><StatusBadge status={String(row.decision || "")} /></td>
                    <td className="p-3 text-neutral-700">{row.doctor || "Unassigned"}</td>
                  </tr>
                )) : <tr><td className="p-3 text-neutral-500" colSpan={4}>No recent assessments.</td></tr>}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
