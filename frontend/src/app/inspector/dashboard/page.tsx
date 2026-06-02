"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { AlertTriangle, CalendarCheck, CheckCircle2, ClipboardList, Clock, FileSearch, Flag, RefreshCw, ShieldAlert, TrendingUp } from "lucide-react";

import { KPICard } from "@/components/dashboards";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { apiClient } from "@/lib/api/client";

interface InspectorDashboardData {
  inspector: { id: string; name: string; state: string };
  cards: Record<string, number>;
  sections: {
    task_list: Array<{ id: string; reference: string; employer: string; branch: string; type: string; scheduled_date: string; priority: string; status: string }>;
    performance_summary: Record<string, number | string>;
    status_breakdown: Array<{ status: string; total: number }>;
    priority_breakdown: Array<{ priority: string; total: number }>;
  };
}

function dateLabel(value?: string) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium" }).format(new Date(value));
}

export default function Page() {
  const [data, setData] = useState<InspectorDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await apiClient.get("/dashboard/inspector/");
      setData(res.data.data);
    } catch {
      setError("Could not load inspector dashboard.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  return (
    <PortalShell role="inspector" title="Inspector Dashboard" description="View assigned inspections, track progress, review findings, and manage enforcement notices.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading dashboard...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><Flag size={16} />{error}</div> : null}

        <section className="grid gap-3 sm:grid-cols-2 md:grid-cols-5">
          <KPICard label="Assigned" value={data?.cards?.assigned_inspections ?? 0} icon={ClipboardList} />
          <KPICard label="Due Today" value={data?.cards?.due_today ?? 0} icon={CalendarCheck} />
          <KPICard label="In Progress" value={data?.cards?.in_progress ?? 0} icon={TrendingUp} />
          <KPICard label="Submitted" value={data?.cards?.submitted ?? 0} icon={CheckCircle2} />
          <KPICard label="Overdue" value={data?.cards?.overdue ?? 0} icon={Clock} />
          <KPICard label="Notices Issued" value={data?.cards?.notices_issued ?? 0} icon={FileSearch} />
          <KPICard label="Corrective Actions" value={data?.cards?.corrective_actions_pending ?? 0} icon={AlertTriangle} subtitle="Pending" />
          <KPICard label="Follow-ups Due" value={data?.cards?.follow_ups_due ?? 0} icon={RefreshCw} />
          <KPICard label="High Priority" value={data?.cards?.high_priority ?? 0} icon={ShieldAlert} />
          <KPICard label="Closed (Month)" value={data?.cards?.closed_this_month ?? 0} icon={CheckCircle2} />
        </section>

        <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between gap-3 border-b border-slate-200 p-4">
            <h2 className="text-sm font-bold text-slate-950">Inspection Tasks</h2>
            <button className="inline-flex h-9 items-center gap-2 rounded border border-slate-200 px-3 text-xs font-bold text-slate-700" type="button" onClick={() => void loadData()}>
              <RefreshCw size={14} /> Refresh
            </button>
          </div>
          <div className="divide-y divide-slate-200">
            {data?.sections?.task_list?.length ? (
              data.sections.task_list.map((task) => (
                <div className="flex items-center justify-between gap-3 p-4 text-sm" key={task.id}>
                  <div>
                    <p className="font-bold text-slate-950">{task.reference || task.employer}</p>
                    <p className="text-xs text-slate-500">{task.employer} · {task.branch || "HQ"} · {task.type} · {dateLabel(task.scheduled_date)}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusBadge status={task.status} />
                    {task.priority === "high" || task.priority === "critical" ? <span className="inline-flex items-center rounded bg-rose-100 px-2 py-0.5 text-xs font-bold text-rose-800">{task.priority}</span> : null}
                    <Link className="text-xs font-bold text-brand-green" href={`/inspector/inspections/${task.id}`}>View</Link>
                  </div>
                </div>
              ))
            ) : (
              <p className="p-4 text-sm text-slate-500">No inspection tasks assigned.</p>
            )}
          </div>
        </section>

        {data?.sections?.performance_summary ? (
          <div className="grid gap-3 md:grid-cols-5">
            <KPICard label="Open" value={data.sections.performance_summary.open ?? 0} icon={ClipboardList} />
            <KPICard label="Submitted" value={data.sections.performance_summary.submitted ?? 0} icon={FileSearch} />
            <KPICard label="Closed" value={data.sections.performance_summary.closed ?? 0} icon={CheckCircle2} />
            <KPICard label="Escalated" value={data.sections.performance_summary.escalated ?? 0} icon={ShieldAlert} />
            <KPICard label="Avg Compliance" value={`${data.sections.performance_summary.average_compliance_score}%`} icon={TrendingUp} />
          </div>
        ) : null}
      </div>
    </PortalShell>
  );
}
