"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Calendar, CheckCircle, ClipboardCheck, Clock, Flag, GitBranch, SearchCheck, Timer, TrendingUp } from "lucide-react";
import { useRouter } from "next/navigation";
import { PortalShell } from "@/components/layout/portal-shell";
import { fetchInspectorDashboard, fetchInspectorTasks } from "@/lib/api/inspections";

const cardsConfig: Array<{ key: string; label: string; icon: typeof Clock; color: string }> = [
  { key: "assigned_inspections", label: "Assigned", icon: ClipboardCheck, color: "text-blue-600" },
  { key: "due_today", label: "Due Today", icon: Calendar, color: "text-amber-500" },
  { key: "overdue", label: "Overdue", icon: AlertTriangle, color: "text-red-500" },
  { key: "in_progress", label: "In Progress", icon: Timer, color: "text-brand-green" },
  { key: "submitted", label: "Submitted", icon: CheckCircle, color: "text-indigo-500" },
  { key: "notices_issued", label: "Notices Issued", icon: Flag, color: "text-orange-500" },
  { key: "corrective_actions_pending", label: "Actions Pending", icon: SearchCheck, color: "text-pink-500" },
  { key: "follow_ups", label: "Follow-Ups", icon: GitBranch, color: "text-teal-500" },
  { key: "high_priority", label: "High Priority", icon: AlertTriangle, color: "text-red-600" },
  { key: "closed_this_month", label: "Closed (Month)", icon: TrendingUp, color: "text-slate-500" },
];

function statusColor(status: string): string {
  const map: Record<string, string> = {
    assigned: "bg-blue-100 text-blue-700", accepted: "bg-cyan-100 text-cyan-700",
    in_progress: "bg-green-100 text-green-700", submitted: "bg-indigo-100 text-indigo-700",
    closed: "bg-slate-100 text-slate-600", cancelled: "bg-red-100 text-red-600",
    escalated: "bg-orange-100 text-orange-700", under_review: "bg-purple-100 text-purple-700",
  };
  return map[status] || "bg-slate-100 text-slate-500";
}

export default function Page() {
  const router = useRouter();
  const dashboard = useQuery({ queryKey: ["inspector-dashboard"], queryFn: fetchInspectorDashboard });
  const tasks = useQuery({ queryKey: ["inspector-tasks"], queryFn: () => fetchInspectorTasks() });

  const cards = dashboard.data?.cards || {} as Record<string, number>;
  const taskList = tasks.data?.data || [];

  return (
    <PortalShell role="inspector" title="Inspector dashboard" description="Track your assigned inspections, deadlines, and enforcement activity.">
      <div className="grid gap-5">
        <section className="grid gap-3 grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
          {cardsConfig.map(({ key, label, icon: Icon, color }) => (
            <div key={key} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex items-center gap-2"><Icon size={16} className={color} /><p className="text-xs font-bold uppercase text-slate-500">{label}</p></div>
              <p className="mt-2 text-2xl font-bold text-slate-950">{(cards as Record<string, number>)[key] ?? 0}</p>
            </div>
          ))}
        </section>

        <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between border-b p-4">
            <h2 className="text-base font-bold text-slate-950">Inspection Tasks</h2>
            <button onClick={() => router.push("/inspector/inspections/new")} className="rounded bg-brand-green px-4 py-2 text-sm font-semibold text-white hover:bg-brand-deep">New Inspection</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b bg-slate-50 text-left text-xs uppercase text-slate-500">
                <tr>
                  <th className="p-3">Reference</th>
                  <th className="p-3">Employer</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Date</th>
                  <th className="p-3">Priority</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {tasks.isLoading ? (
                  <tr><td colSpan={7} className="p-6 text-center text-slate-400">Loading tasks...</td></tr>
                ) : taskList.length === 0 ? (
                  <tr><td colSpan={7} className="p-6 text-center text-slate-400">No inspection tasks assigned to you.</td></tr>
                ) : (
                  taskList.map((t: Record<string, unknown>) => (
                    <tr key={t.id as string} className="hover:bg-slate-50">
                      <td className="p-3 font-mono text-xs">{(t.reference as string) || (t.id as string).slice(0, 8)}</td>
                      <td className="p-3 font-medium">{t.employer_name as string || "-"}</td>
                      <td className="p-3 text-slate-500">{String(t.inspection_type || "-").replace(/_/g, " ")}</td>
                      <td className="p-3 text-slate-500">{t.scheduled_at ? new Date(t.scheduled_at as string).toLocaleDateString() : (t.inspection_date ? new Date(t.inspection_date as string).toLocaleDateString() : "-")}</td>
                      <td className="p-3"><span className={`rounded px-2 py-0.5 text-xs font-semibold ${t.priority === "critical" ? "bg-red-100 text-red-700" : t.priority === "high" ? "bg-orange-100 text-orange-700" : "bg-slate-100 text-slate-600"}`}>{String(t.priority || "medium")}</span></td>
                      <td className="p-3"><span className={`rounded px-2 py-0.5 text-xs font-semibold ${statusColor(t.status as string)}`}>{String(t.status || "-").replace(/_/g, " ")}</span></td>
                      <td className="p-3">
                        <button onClick={() => router.push(`/inspector/inspections/${t.id as string}`)} className="rounded bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-200">View</button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
