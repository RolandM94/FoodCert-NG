"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { PortalShell } from "@/components/layout/portal-shell";
import { listEnforcementNotices } from "@/lib/api/inspections";

function statusColor(status: string): string {
  const map: Record<string, string> = {
    issued: "bg-info-100 text-info-700", acknowledged: "bg-info-100 text-info-700",
    response_submitted: "bg-indigo-100 text-indigo-700", closed: "bg-brand-100 text-brand-700",
    escalated: "bg-danger-100 text-danger-700", corrective_action_pending: "bg-warning-100 text-warning-700",
    draft: "bg-neutral-100 text-neutral-600", pending_approval: "bg-warning-100 text-warning-700",
  };
  return map[status] || "bg-neutral-100 text-neutral-500";
}

export default function Page() {
  const router = useRouter();
  const query = useQuery({ queryKey: ["employer-notices"], queryFn: () => listEnforcementNotices() });
  const notices = query.data?.data || [];

  return (
    <PortalShell role="employer" title="Enforcement notices" description="View enforcement notices for your business and submit corrective action responses.">
      <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead className="border-b bg-neutral-50 text-left text-xs uppercase text-neutral-500">
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
              <tr><td colSpan={5} className="p-6 text-center text-neutral-400">Loading...</td></tr>
            ) : notices.length === 0 ? (
              <tr><td colSpan={5} className="p-6 text-center text-neutral-400">No enforcement notices for your business.</td></tr>
            ) : (
              notices.map((n) => (
                <tr key={n.id as string} className="hover:bg-neutral-50">
                  <td className="p-3 font-mono text-xs">{(n.notice_reference as string) || "-"}</td>
                  <td className="p-3 text-neutral-500 capitalize">{String(n.notice_type || "-").replace(/_/g, " ")}</td>
                  <td className="p-3 text-neutral-500">{n.deadline ? new Date(n.deadline as string).toLocaleDateString() : "-"}</td>
                  <td className="p-3"><span className={`rounded px-2 py-0.5 text-xs font-semibold ${statusColor(n.status as string)}`}>{String(n.status || "-").replace(/_/g, " ")}</span></td>
                  <td className="p-3">
                    <button onClick={() => router.push(`/employer/notices/${n.id as string}`)} className="rounded bg-neutral-100 px-3 py-1 text-xs font-semibold hover:bg-neutral-200">View</button>
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
