"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { PortalShell } from "@/components/layout/portal-shell";
import { listEnforcementCases } from "@/lib/api/inspections";

function statusColor(s: string): string {
  const map: Record<string, string> = {
    open: "bg-info-100 text-info-700", under_review: "bg-neutral-200 text-neutral-700",
    awaiting_employer_response: "bg-warning-100 text-warning-700", escalated: "bg-danger-100 text-danger-700",
    resolved: "bg-brand-100 text-brand-700", closed: "bg-neutral-100 text-neutral-500",
  };
  return map[s] || "bg-neutral-100 text-neutral-500";
}

function severityColor(s: string): string {
  const map: Record<string, string> = {
    low: "bg-neutral-100 text-neutral-600", medium: "bg-warning-100 text-warning-700",
    high: "bg-warning-100 text-warning-700", critical: "bg-danger-100 text-danger-700",
  };
  return map[s] || "bg-neutral-100 text-neutral-500";
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
            <button key={s || "all"} onClick={() => setStatusFilter(s)} className={`rounded px-3 py-1 text-xs font-semibold ${statusFilter === s ? "bg-brand-600 text-white" : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"}`}>
              {s ? s.replace(/_/g, " ") : "All"}
            </button>
          ))}
        </div>
        <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead className="border-b bg-neutral-50 text-left text-xs uppercase text-neutral-500">
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
                <tr><td colSpan={6} className="p-6 text-center text-neutral-400">Loading...</td></tr>
              ) : cases.length === 0 ? (
                <tr><td colSpan={6} className="p-6 text-center text-neutral-400">No enforcement cases found.</td></tr>
              ) : (
                cases.map((c) => (
                  <tr key={c.id as string} className="hover:bg-neutral-50">
                    <td className="p-3 font-mono text-xs">{(c.case_reference as string) || "-"}</td>
                    <td className="p-3 font-medium">{c.employer_name as string || "-"}</td>
                    <td className="p-3"><span className={`rounded px-2 py-0.5 text-xs font-bold ${severityColor(c.severity as string)}`}>{String(c.severity || "-")}</span></td>
                    <td className="p-3"><span className={`rounded px-2 py-0.5 text-xs font-bold ${statusColor(c.status as string)}`}>{String(c.status || "-").replace(/_/g, " ")}</span></td>
                    <td className="p-3 text-neutral-500">{c.created_at ? new Date(c.created_at as string).toLocaleDateString() : "-"}</td>
                    <td className="p-3">
                      <button onClick={() => router.push(`/state/inspectorate/cases/${c.id as string}`)} className="rounded bg-neutral-100 px-3 py-1 text-xs font-semibold hover:bg-neutral-200">View</button>
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
