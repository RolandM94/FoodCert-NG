"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { ArrowUp } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { getEnforcementCase, escalateCase, closeCase } from "@/lib/api/inspections";

function statusColor(s: string): string {
  const map: Record<string, string> = {
    open: "bg-info-100 text-info-700", under_review: "bg-neutral-200 text-neutral-700",
    escalated: "bg-danger-100 text-danger-700", resolved: "bg-brand-100 text-brand-700", closed: "bg-neutral-100 text-neutral-500",
  };
  return map[s] || "bg-neutral-100 text-neutral-500";
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

  if (query.isLoading) return <PortalShell role="state_admin" title="Case detail" description=""><p className="p-4 text-neutral-400">Loading...</p></PortalShell>;

  return (
    <PortalShell role="state_admin" title={`Case ${c.case_reference || ""}`} description="Enforcement case detail and escalation management.">
      <div className="grid gap-4 max-w-3xl">
        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className={`rounded px-2 py-1 text-xs font-bold ${statusColor(c.status as string)}`}>{String(c.status || "-").replace(/_/g, " ").toUpperCase()}</span>
            <div className="flex gap-2">
              {!["closed", "resolved"].includes(c.status as string) && (
                <button onClick={handleEscalate} className="inline-flex items-center gap-1 rounded bg-orange-500 px-3 py-1 text-xs font-semibold text-white hover:bg-orange-600"><ArrowUp size={12} />Escalate</button>
              )}
              {!["closed"].includes(c.status as string) && (
                <button onClick={handleClose} className="rounded bg-neutral-500 px-3 py-1 text-xs font-semibold text-white hover:bg-neutral-600">Close</button>
              )}
            </div>
          </div>
          {msg && <p className="mb-3 rounded bg-info-50 p-2 text-xs text-info-700">{msg}</p>}
          <div className="grid gap-3 text-sm">
            <div><span className="font-semibold text-neutral-500">Employer:</span> {c.employer_name as string || "-"}</div>
            <div><span className="font-semibold text-neutral-500">Severity:</span> <span className="capitalize font-medium">{String(c.severity || "-")}</span></div>
            <div><span className="font-semibold text-neutral-500">Escalated to:</span> <span className="capitalize">{String(c.escalated_to || "None").replace(/_/g, " ")}</span></div>
            <div><span className="font-semibold text-neutral-500">Opened by:</span> {c.opened_by_name as string || "-"}</div>
            <div>
              <span className="font-semibold text-neutral-500">Summary:</span>
              <p className="mt-1 whitespace-pre-wrap text-neutral-600">{c.summary as string || "-"}</p>
            </div>
          </div>
        </div>
      </div>
    </PortalShell>
  );
}
