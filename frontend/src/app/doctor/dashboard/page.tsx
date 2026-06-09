"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { AlertCircle, ClipboardCheck, ClipboardList, Clock, FileText, HeartPulse, RefreshCw, ShieldCheck, Syringe } from "lucide-react";

import { KPICard } from "@/components/dashboards";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { apiClient } from "@/lib/api/client";
import type { ReactNode } from "react";

interface DoctorDashboardData {
  doctor: { id: string; name: string; facility: string };
  filters: Record<string, string>;
  cards: Record<string, number>;
  sections: {
    pending_queue: Array<Record<string, string>>;
    recent_decisions: Array<Record<string, string>>;
    workload_summary: Array<Record<string, string>>;
  };
}

function dateLabel(value?: string) {
  if (!value) return "";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium" }).format(new Date(value));
}

function decisionBadge(decision: string): ReactNode {
  if (!decision) return null;
  const map: Record<string, { color: string; label: string }> = {
    fit: { color: "bg-brand-100 text-brand-800", label: "Fit" },
    temporarily_not_fit: { color: "bg-warning-100 text-warning-700", label: "Temp Not Fit" },
    not_fit: { color: "bg-danger-100 text-danger-700", label: "Not Fit" },
    pending: { color: "bg-neutral-100 text-neutral-600", label: "Pending" },
  };
  const style = map[decision] || { color: "bg-neutral-100 text-neutral-600", label: decision };
  return <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-bold ${style.color}`}>{style.label}</span>;
}

export default function Page() {
  const [data, setData] = useState<DoctorDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await apiClient.get("/dashboard/doctor/");
      setData(res.data.data);
    } catch {
      setError("Could not load doctor dashboard.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  return (
    <PortalShell role="doctor" title="Doctor Dashboard" description="Review pending declarations, examinations, lab results, vaccinations, and fitness decisions.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading dashboard...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}

        <section className="grid gap-3 sm:grid-cols-2 md:grid-cols-4">
          <KPICard label="Assigned" value={data?.cards?.assigned_assessments ?? 0} icon={ClipboardList} />
          <KPICard label="Declarations" value={data?.cards?.declaration_reviews_pending ?? 0} icon={FileText} subtitle="Pending review" />
          <KPICard label="Physical Exams" value={data?.cards?.physical_exams_pending ?? 0} icon={HeartPulse} subtitle="Pending" />
          <KPICard label="Lab Results" value={data?.cards?.lab_results_pending_review ?? 0} icon={ClipboardCheck} subtitle="Pending review" />
          <KPICard label="Vaccinations" value={data?.cards?.vaccination_reviews_pending ?? 0} icon={Syringe} subtitle="Pending review" />
          <KPICard label="Decisions" value={data?.cards?.decisions_pending ?? 0} icon={ShieldCheck} subtitle="Pending" />
          <KPICard label="Not Fit Cases" value={data?.cards?.temporarily_not_fit_cases ?? 0} icon={AlertCircle} subtitle="Active" />
          <KPICard label="Return-to-Work" value={data?.cards?.return_to_work_reviews_pending ?? 0} icon={Clock} subtitle="Pending review" />
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
          <div className="flex items-center justify-between gap-3 border-b border-neutral-200 p-4">
            <h2 className="text-sm font-bold text-neutral-900">Pending Queue</h2>
            <button className="inline-flex h-9 items-center gap-2 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700" type="button" onClick={() => void loadData()}>
              <RefreshCw size={14} /> Refresh
            </button>
          </div>
          <div className="divide-y divide-neutral-200">
            {data?.sections?.pending_queue?.length ? (
              data.sections.pending_queue.map((item, i) => (
                <div className="flex items-center justify-between gap-3 p-4 text-sm" key={i}>
                  <div><p className="font-bold text-neutral-900">{item.food_handler || item.task}</p><p className="text-xs text-neutral-500">{item.type || item.action}</p></div>
                  {item.status ? <StatusBadge status={item.status} /> : null}
                  {item.assessment_id ? <Link className="text-xs font-bold text-brand-600" href={`/doctor/assessments/${item.assessment_id}`}>Open</Link> : null}
                </div>
              ))
            ) : (
              <p className="p-4 text-sm text-neutral-500">No pending items in your queue.</p>
            )}
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
          <div className="border-b border-neutral-200 p-4">
            <h2 className="text-sm font-bold text-neutral-900">Recent Decisions</h2>
          </div>
          <div className="divide-y divide-neutral-200">
            {data?.sections?.recent_decisions?.length ? (
              data.sections.recent_decisions.map((item) => (
                <div className="flex items-center justify-between gap-3 p-4 text-sm" key={item.id}>
                  <div>
                    <p className="font-bold text-neutral-900">{item.food_handler}</p>
                    <p className="text-xs text-neutral-500">{item.facility} · {dateLabel(item.signed_at)}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {decisionBadge(item.decision)}
                    {item.return_to_work_date ? <span className="inline-flex items-center rounded bg-info-100 px-2 py-0.5 text-xs font-bold text-info-700">RTW: {dateLabel(item.return_to_work_date)}</span> : null}
                    <Link className="text-xs font-bold text-brand-600" href={`/doctor/assessments/${item.id}`}>View</Link>
                  </div>
                </div>
              ))
            ) : (
              <p className="p-4 text-sm text-neutral-500">No recent decisions.</p>
            )}
          </div>
        </section>

        {data?.sections?.workload_summary?.length ? (
          <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-bold text-neutral-900 mb-3">Workload Summary</h2>
            <div className="grid gap-3 md:grid-cols-3">
              {data.sections.workload_summary.map((item, i) => (
                <div className="rounded border border-neutral-200 p-3 text-sm" key={i}>
                  <p className="font-bold text-neutral-900">{item.status || item.category}</p>
                  <p className="text-2xl font-bold text-neutral-900 mt-1">{item.count || item.total}</p>
                </div>
              ))}
            </div>
          </section>
        ) : null}
      </div>
    </PortalShell>
  );
}
