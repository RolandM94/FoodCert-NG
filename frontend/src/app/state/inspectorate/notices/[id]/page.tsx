"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { PortalShell } from "@/components/layout/portal-shell";
import { getEnforcementNotice, submitNoticeForApproval, approveNotice, closeNotice, getCorrectiveActions } from "@/lib/api/inspections";
import { apiClient } from "@/lib/api/client";

function statusColor(status: string): string {
  const map: Record<string, string> = {
    draft: "bg-neutral-100 text-neutral-600", pending_approval: "bg-warning-100 text-warning-700",
    issued: "bg-info-100 text-info-700", acknowledged: "bg-info-100 text-info-700",
    response_submitted: "bg-indigo-100 text-indigo-700", closed: "bg-brand-100 text-brand-700",
    escalated: "bg-danger-100 text-danger-700",
  };
  return map[status] || "bg-neutral-100 text-neutral-500";
}

export default function Page() {
  const { id } = useParams<{ id: string }>();
  const [msg, setMsg] = useState("");
  const noticeQ = useQuery({ queryKey: ["notice", id], queryFn: () => getEnforcementNotice(id) });
  const actionsQ = useQuery({ queryKey: ["corrective-actions", id], queryFn: () => getCorrectiveActions(id) });
  const notice = noticeQ.data || {} as Record<string, unknown>;

  async function handleAction(action: string) {
    try {
      if (action === "submit") { await submitNoticeForApproval(id); setMsg("Submitted for approval."); }
      else if (action === "approve") { await approveNotice(id); setMsg("Notice approved and issued."); }
      else if (action === "close") { await closeNotice(id); setMsg("Notice closed."); }
      noticeQ.refetch();
    } catch { setMsg("Action failed."); }
  }

  if (noticeQ.isLoading) return <PortalShell role="state_admin" title="Notice detail" description=""><p className="p-4 text-neutral-400">Loading...</p></PortalShell>;

  return (
    <PortalShell role="state_admin" title={`Notice ${notice.notice_reference || ""}`} description="Review and manage this enforcement notice.">
      <div className="grid gap-4">
        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className={`rounded px-2 py-1 text-xs font-bold ${statusColor(notice.status as string)}`}>{String(notice.status || "-").replace(/_/g, " ").toUpperCase()}</span>
            <div className="flex gap-2">
              {notice.status === "draft" && <button onClick={() => handleAction("submit")} className="rounded bg-brand-600 px-3 py-1 text-xs font-semibold text-white hover:bg-brand-700">Submit for Approval</button>}
              {notice.status === "pending_approval" && <button onClick={() => handleAction("approve")} className="rounded bg-brand-600 px-3 py-1 text-xs font-semibold text-white hover:bg-brand-700">Approve & Issue</button>}
              {["issued", "acknowledged"].includes(notice.status as string) && <button onClick={() => handleAction("close")} className="rounded bg-danger-500 px-3 py-1 text-xs font-semibold text-white hover:bg-danger-500">Close</button>}
            </div>
          </div>
          {msg && <p className="mb-3 rounded bg-info-50 p-2 text-xs text-info-700">{msg}</p>}
          <div className="grid gap-3 text-sm">
            <div><span className="font-semibold text-neutral-500">Type:</span> <span className="capitalize">{String(notice.notice_type || "-").replace(/_/g, " ")}</span></div>
            <div><span className="font-semibold text-neutral-500">Employer:</span> {notice.employer_name as string || "-"}</div>
            <div><span className="font-semibold text-neutral-500">Deadline:</span> {notice.deadline ? new Date(notice.deadline as string).toLocaleDateString() : "-"}</div>
            <div>
              <span className="font-semibold text-neutral-500">Description:</span>
              <p className="mt-1 whitespace-pre-wrap text-neutral-600">{notice.description as string || "-"}</p>
            </div>
            <div>
              <span className="font-semibold text-neutral-500">Required Corrective Actions:</span>
              <p className="mt-1 whitespace-pre-wrap text-neutral-600">{notice.required_corrective_actions as string || "-"}</p>
            </div>
          </div>
        </div>

        {actionsQ.data && actionsQ.data.length > 0 && (
          <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <h2 className="text-base font-bold text-neutral-900 mb-3">Employer Responses</h2>
            <div className="grid gap-3">
              {actionsQ.data.map((a: Record<string, unknown>, i: number) => (
                <div key={a.id as string || i} className="rounded bg-neutral-50 p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-neutral-500">Response #{i + 1}</span>
                    <span className={`rounded px-2 py-0.5 text-xs font-bold ${(a.status as string) === "accepted" ? "bg-brand-100 text-brand-700" : (a.status as string) === "rejected" ? "bg-danger-100 text-danger-700" : "bg-neutral-200 text-neutral-600"}`}>{String(a.status || "-").replace(/_/g, " ")}</span>
                  </div>
                  <p className="text-sm text-neutral-700">{a.response_note as string}</p>
                  <p className="mt-1 text-xs text-neutral-500">Action taken: {a.action_taken as string}</p>
                  {(a.status as string) === "submitted" && (
                    <div className="mt-2 flex gap-2">
                      <button onClick={async () => { await reviewCorrectiveAction(id, a.id as string, "accept"); actionsQ.refetch(); }} className="rounded bg-green-500 px-2 py-0.5 text-xs text-white hover:bg-green-600">Accept</button>
                      <button onClick={async () => { await reviewCorrectiveAction(id, a.id as string, "reject"); actionsQ.refetch(); }} className="rounded bg-red-400 px-2 py-0.5 text-xs text-white hover:bg-danger-500">Reject</button>
                      <button onClick={async () => { await reviewCorrectiveAction(id, a.id as string, "request_more_evidence"); actionsQ.refetch(); }} className="rounded bg-amber-400 px-2 py-0.5 text-xs text-white hover:bg-warning-500">More Evidence</button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </PortalShell>
  );
}

async function reviewCorrectiveAction(noticeId: string, responseId: string, action: string) {
  await apiClient.post(`/enforcement-notices/${noticeId}/corrective-actions/${responseId}/review/`, { action });
}
