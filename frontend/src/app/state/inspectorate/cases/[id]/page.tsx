"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { ArrowUp } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { getEnforcementCase, escalateCase, closeCase } from "@/lib/api/inspections";

function statusColor(s: string): string {
  const map: Record<string, string> = {
    open: "bg-blue-100 text-blue-700", under_review: "bg-purple-100 text-purple-700",
    escalated: "bg-red-100 text-red-700", resolved: "bg-green-100 text-green-700", closed: "bg-slate-100 text-slate-500",
  };
  return map[s] || "bg-slate-100 text-slate-500";
}

export default function Page() {
  const { id } = useParams<{ id: string }>();
  const [msg, setMsg] = useState("");
  const query = useQuery({ queryKey: ["case", id], queryFn: () => getEnforcementCase(id) });
  const c = query.data || {} as Record<string, unknown>;

  async function handleEscalate() {
    try { await escalateCase(id); setMsg("Case escalated."); query.refetch(); } catch { setMsg("Escalation failed."); }
  }
  async function handleClose() {
    try { await closeCase(id); setMsg("Case closed."); query.refetch(); } catch { setMsg("Close failed."); }
  }

  if (query.isLoading) return <PortalShell role="state_admin" title="Case detail" description=""><p className="p-4 text-slate-400">Loading...</p></PortalShell>;

  return (
    <PortalShell role="state_admin" title={`Case ${c.case_reference || ""}`} description="Enforcement case detail and escalation management.">
      <div className="grid gap-4 max-w-3xl">
        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className={`rounded px-2 py-1 text-xs font-bold ${statusColor(c.status as string)}`}>{String(c.status || "-").replace(/_/g, " ").toUpperCase()}</span>
            <div className="flex gap-2">
              {!["closed", "resolved"].includes(c.status as string) && (
                <button onClick={handleEscalate} className="inline-flex items-center gap-1 rounded bg-orange-500 px-3 py-1 text-xs font-semibold text-white hover:bg-orange-600"><ArrowUp size={12} />Escalate</button>
              )}
              {!["closed"].includes(c.status as string) && (
                <button onClick={handleClose} className="rounded bg-slate-500 px-3 py-1 text-xs font-semibold text-white hover:bg-slate-600">Close</button>
              )}
            </div>
          </div>
          {msg && <p className="mb-3 rounded bg-blue-50 p-2 text-xs text-blue-700">{msg}</p>}
          <div className="grid gap-3 text-sm">
            <div><span className="font-semibold text-slate-500">Employer:</span> {c.employer_name as string || "-"}</div>
            <div><span className="font-semibold text-slate-500">Severity:</span> <span className="capitalize font-medium">{String(c.severity || "-")}</span></div>
            <div><span className="font-semibold text-slate-500">Escalated to:</span> <span className="capitalize">{String(c.escalated_to || "None").replace(/_/g, " ")}</span></div>
            <div><span className="font-semibold text-slate-500">Opened by:</span> {c.opened_by_name as string || "-"}</div>
            <div>
              <span className="font-semibold text-slate-500">Summary:</span>
              <p className="mt-1 whitespace-pre-wrap text-slate-600">{c.summary as string || "-"}</p>
            </div>
          </div>
        </div>
      </div>
    </PortalShell>
  );
}
