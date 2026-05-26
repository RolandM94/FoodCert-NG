"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { PortalShell } from "@/components/layout/portal-shell";
import { listEnforcementNotices } from "@/lib/api/inspections";

function statusColor(status: string): string {
  const map: Record<string, string> = {
    issued: "bg-blue-100 text-blue-700", acknowledged: "bg-cyan-100 text-cyan-700",
    response_submitted: "bg-indigo-100 text-indigo-700", closed: "bg-green-100 text-green-700",
    escalated: "bg-red-100 text-red-700", corrective_action_pending: "bg-amber-100 text-amber-700",
    draft: "bg-slate-100 text-slate-600", pending_approval: "bg-yellow-100 text-yellow-700",
  };
  return map[status] || "bg-slate-100 text-slate-500";
}

export default function Page() {
  const router = useRouter();
  const query = useQuery({ queryKey: ["employer-notices"], queryFn: () => listEnforcementNotices() });
  const notices = query.data?.data || [];

  return (
    <PortalShell role="employer" title="Enforcement notices" description="View enforcement notices for your business and submit corrective action responses.">
      <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead className="border-b bg-slate-50 text-left text-xs uppercase text-slate-500">
            <tr>
              <th className="p-3">Reference</th>
              <th className="p-3">Type</th>
              <th className="p-3">Deadline</th>
              <th className="p-3">Status</th>
              <th className="p-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {query.isLoading ? (
              <tr><td colSpan={5} className="p-6 text-center text-slate-400">Loading...</td></tr>
            ) : notices.length === 0 ? (
              <tr><td colSpan={5} className="p-6 text-center text-slate-400">No enforcement notices for your business.</td></tr>
            ) : (
              notices.map((n) => (
                <tr key={n.id as string} className="hover:bg-slate-50">
                  <td className="p-3 font-mono text-xs">{(n.notice_reference as string) || "-"}</td>
                  <td className="p-3 text-slate-500 capitalize">{String(n.notice_type || "-").replace(/_/g, " ")}</td>
                  <td className="p-3 text-slate-500">{n.deadline ? new Date(n.deadline as string).toLocaleDateString() : "-"}</td>
                  <td className="p-3"><span className={`rounded px-2 py-0.5 text-xs font-semibold ${statusColor(n.status as string)}`}>{String(n.status || "-").replace(/_/g, " ")}</span></td>
                  <td className="p-3">
                    <button onClick={() => router.push(`/employer/notices/${n.id as string}`)} className="rounded bg-slate-100 px-3 py-1 text-xs font-semibold hover:bg-slate-200">View</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </PortalShell>
  );
}
