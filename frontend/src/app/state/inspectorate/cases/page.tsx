"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { PortalShell } from "@/components/layout/portal-shell";
import { listEnforcementCases } from "@/lib/api/inspections";

function statusColor(s: string): string {
  const map: Record<string, string> = {
    open: "bg-blue-100 text-blue-700", under_review: "bg-purple-100 text-purple-700",
    awaiting_employer_response: "bg-yellow-100 text-yellow-700", escalated: "bg-red-100 text-red-700",
    resolved: "bg-green-100 text-green-700", closed: "bg-slate-100 text-slate-500",
  };
  return map[s] || "bg-slate-100 text-slate-500";
}

function severityColor(s: string): string {
  const map: Record<string, string> = {
    low: "bg-slate-100 text-slate-600", medium: "bg-yellow-100 text-yellow-700",
    high: "bg-orange-100 text-orange-700", critical: "bg-red-100 text-red-700",
  };
  return map[s] || "bg-slate-100 text-slate-500";
}

export default function Page() {
  const router = useRouter();
  const [statusFilter, setStatusFilter] = useState("");
  const query = useQuery({
    queryKey: ["enforcement-cases", statusFilter],
    queryFn: () => listEnforcementCases(statusFilter ? { status: statusFilter } : {}),
  });
  const cases = query.data?.data || [];

  return (
    <PortalShell role="state_admin" title="Enforcement cases" description="Track and manage enforcement cases across the state.">
      <div className="grid gap-4">
        <div className="flex gap-2">
          {["", "open", "under_review", "awaiting_employer_response", "escalated", "resolved", "closed"].map((s) => (
            <button key={s || "all"} onClick={() => setStatusFilter(s)} className={`rounded px-3 py-1 text-xs font-semibold ${statusFilter === s ? "bg-brand-green text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`}>
              {s ? s.replace(/_/g, " ") : "All"}
            </button>
          ))}
        </div>
        <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead className="border-b bg-slate-50 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="p-3">Case Ref</th>
                <th className="p-3">Employer</th>
                <th className="p-3">Severity</th>
                <th className="p-3">Status</th>
                <th className="p-3">Opened</th>
                <th className="p-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {query.isLoading ? (
                <tr><td colSpan={6} className="p-6 text-center text-slate-400">Loading...</td></tr>
              ) : cases.length === 0 ? (
                <tr><td colSpan={6} className="p-6 text-center text-slate-400">No enforcement cases found.</td></tr>
              ) : (
                cases.map((c) => (
                  <tr key={c.id as string} className="hover:bg-slate-50">
                    <td className="p-3 font-mono text-xs">{(c.case_reference as string) || "-"}</td>
                    <td className="p-3 font-medium">{c.employer_name as string || "-"}</td>
                    <td className="p-3"><span className={`rounded px-2 py-0.5 text-xs font-bold ${severityColor(c.severity as string)}`}>{String(c.severity || "-")}</span></td>
                    <td className="p-3"><span className={`rounded px-2 py-0.5 text-xs font-bold ${statusColor(c.status as string)}`}>{String(c.status || "-").replace(/_/g, " ")}</span></td>
                    <td className="p-3 text-slate-500">{c.created_at ? new Date(c.created_at as string).toLocaleDateString() : "-"}</td>
                    <td className="p-3">
                      <button onClick={() => router.push(`/state/inspectorate/cases/${c.id as string}`)} className="rounded bg-slate-100 px-3 py-1 text-xs font-semibold hover:bg-slate-200">View</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </PortalShell>
  );
}
