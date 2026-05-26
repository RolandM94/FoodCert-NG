"use client";

import { useState, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { PortalShell } from "@/components/layout/portal-shell";
import { getEnforcementNotice, acknowledgeNotice, submitCorrectiveAction, getCorrectiveActions } from "@/lib/api/inspections";

function statusColor(status: string): string {
  const map: Record<string, string> = {
    issued: "bg-blue-100 text-blue-700", acknowledged: "bg-cyan-100 text-cyan-700",
    response_submitted: "bg-indigo-100 text-indigo-700", closed: "bg-green-100 text-green-700",
  };
  return map[status] || "bg-slate-100 text-slate-500";
}

export default function Page() {
  const { id } = useParams<{ id: string }>();
  const [note, setNote] = useState("");
  const [actionTaken, setActionTaken] = useState("");
  const [msg, setMsg] = useState("");
  const noticeQ = useQuery({ queryKey: ["notice", id], queryFn: () => getEnforcementNotice(id) });
  const actionsQ = useQuery({ queryKey: ["corrective-actions", id], queryFn: () => getCorrectiveActions(id) });
  const notice = noticeQ.data || {} as Record<string, unknown>;

  const handleAcknowledge = useCallback(async () => {
    try { await acknowledgeNotice(id); setMsg("Notice acknowledged."); noticeQ.refetch(); } catch { setMsg("Failed."); }
  }, [id, noticeQ]);

  const handleRespond = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!note.trim() || !actionTaken.trim()) { setMsg("Both fields required."); return; }
    try {
      await submitCorrectiveAction(id, { response_note: note, action_taken: actionTaken });
      setMsg("Response submitted."); setNote(""); setActionTaken("");
      noticeQ.refetch(); actionsQ.refetch();
    } catch { setMsg("Submission failed."); }
  }, [id, note, actionTaken, noticeQ, actionsQ]);

  if (noticeQ.isLoading) return <PortalShell role="employer" title="Notice detail" description=""><p className="p-4 text-slate-400">Loading...</p></PortalShell>;

  const canRespond = (notice.status as string) === "issued" || (notice.status as string) === "acknowledged";
  const daysLeft = notice.deadline
    ? Math.ceil((new Date(notice.deadline as string).getTime() - Date.now()) / 86400000)
    : null;

  return (
    <PortalShell role="employer" title={`Notice ${notice.notice_reference || ""}`} description="Review enforcement notice and submit your corrective action response.">
      <div className="grid gap-4 max-w-3xl">
        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className={`rounded px-2 py-1 text-xs font-bold ${statusColor(notice.status as string)}`}>{String(notice.status || "-").replace(/_/g, " ").toUpperCase()}</span>
            {notice.status === "issued" && (
              <button onClick={handleAcknowledge} className="rounded bg-brand-green px-3 py-1 text-xs font-semibold text-white hover:bg-brand-deep">Acknowledge</button>
            )}
          </div>
          {msg && <p className="mb-3 rounded bg-blue-50 p-2 text-xs text-blue-700">{msg}</p>}
          {daysLeft !== null && daysLeft >= 0 && (
            <p className={`mb-3 rounded p-2 text-xs font-semibold ${daysLeft <= 2 ? "bg-red-50 text-red-700" : "bg-amber-50 text-amber-700"}`}>
              Deadline: {new Date(notice.deadline as string).toLocaleDateString()} ({daysLeft} day{daysLeft !== 1 ? "s" : ""} remaining)
            </p>
          )}
          <div className="grid gap-3 text-sm">
            <div><span className="font-semibold text-slate-500">Type:</span> <span className="capitalize">{String(notice.notice_type || "-").replace(/_/g, " ")}</span></div>
            <div>
              <span className="font-semibold text-slate-500">Description:</span>
              <p className="mt-1 whitespace-pre-wrap text-slate-600">{notice.description as string || "-"}</p>
            </div>
            <div>
              <span className="font-semibold text-slate-500">Required Actions:</span>
              <p className="mt-1 whitespace-pre-wrap rounded bg-amber-50 p-3 text-slate-700">{String(notice.required_corrective_actions || "-")}</p>
            </div>
          </div>
        </div>

        {canRespond && (
          <form onSubmit={handleRespond} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-base font-bold text-slate-950 mb-3">Submit Corrective Action</h2>
            <div className="grid gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Response Note</label>
                <textarea value={note} onChange={(e) => setNote(e.target.value)} rows={3} className="w-full rounded border border-slate-200 p-2 text-sm" placeholder="Describe your response..." />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Action Taken</label>
                <textarea value={actionTaken} onChange={(e) => setActionTaken(e.target.value)} rows={3} className="w-full rounded border border-slate-200 p-2 text-sm" placeholder="Describe the corrective action taken..." />
              </div>
              <button type="submit" className="rounded bg-brand-green px-4 py-2 text-sm font-semibold text-white hover:bg-brand-deep self-start">Submit Response</button>
            </div>
          </form>
        )}

        {actionsQ.data && actionsQ.data.length > 0 && (
          <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-base font-bold text-slate-950 mb-3">Submitted Responses</h2>
            <div className="grid gap-3">
              {actionsQ.data.map((a: Record<string, unknown>, i: number) => (
                <div key={a.id as string || i} className="rounded bg-slate-50 p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-slate-500">Response #{i + 1} - {a.submitted_at ? new Date(a.submitted_at as string).toLocaleDateString() : "-"}</span>
                    <span className={`rounded px-2 py-0.5 text-xs font-bold ${(a.status as string) === "accepted" ? "bg-green-100 text-green-700" : (a.status as string) === "rejected" ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-700"}`}>{String(a.status || "-").replace(/_/g, " ")}</span>
                  </div>
                  <p className="text-sm text-slate-700">{String(a.response_note || "")}</p>
                  <p className="mt-1 text-xs text-slate-500">Action: {String(a.action_taken || "")}</p>
                  {a.review_note ? <p className="mt-1 rounded bg-slate-100 p-2 text-xs text-slate-600">Review: {String(a.review_note)}</p> : null}
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </PortalShell>
  );
}
