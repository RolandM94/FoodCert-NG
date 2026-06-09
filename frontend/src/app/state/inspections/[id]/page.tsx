"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { ClipboardCheck, History, MessageSquareText } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusCell } from "@/components/ui/data-table";
import { fetchStateInspection } from "@/lib/api/state";

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const params = useParams<{ id: string }>();
  const inspectionQuery = useQuery({
    queryKey: ["state-inspection", params.id],
    queryFn: () => fetchStateInspection(params.id),
    enabled: Boolean(params.id),
  });
  const inspection = inspectionQuery.data;

  return (
    <PortalShell role="state_admin" title="Inspection detail" description="Review inspection findings, employer responses, enforcement status, and audit history.">
      {!inspection ? (
        <div className="rounded-lg border border-dashed border-neutral-300 bg-white p-6 text-sm text-neutral-600">
          {inspectionQuery.isLoading ? "Loading inspection..." : "Inspection not found."}
        </div>
      ) : (
        <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
          <section className="grid gap-4">
            <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <div className="mb-4 flex items-center gap-2">
                <ClipboardCheck className="text-brand-700" size={18} />
                <h2 className="text-base font-bold text-neutral-900">{inspection.employer_name}</h2>
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <div><p className="text-xs font-semibold uppercase text-neutral-500">Inspector</p><p className="text-sm font-semibold text-neutral-900">{inspection.inspector_name || "Not set"}</p></div>
                <div><p className="text-xs font-semibold uppercase text-neutral-500">Inspection date</p><p className="text-sm font-semibold text-neutral-900">{dateLabel(inspection.inspection_date)}</p></div>
                <div><p className="text-xs font-semibold uppercase text-neutral-500">LGA</p><p className="text-sm font-semibold text-neutral-900">{inspection.lga_name || "Not set"}</p></div>
                <div><p className="text-xs font-semibold uppercase text-neutral-500">Score</p><p className="text-sm font-semibold text-neutral-900">{inspection.compliance_score ? `${inspection.compliance_score}%` : "Not scored"}</p></div>
                <div><p className="text-xs font-semibold uppercase text-neutral-500">Enforcement</p><StatusCell status={inspection.enforcement_action} /></div>
                <div><p className="text-xs font-semibold uppercase text-neutral-500">Status</p><StatusCell status={inspection.status} /></div>
              </div>
            </div>

            <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <h3 className="mb-3 text-sm font-bold text-neutral-900">Findings</h3>
              <p className="whitespace-pre-wrap text-sm leading-6 text-neutral-700">{inspection.findings || "No findings recorded."}</p>
            </div>

            <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <h3 className="mb-3 text-sm font-bold text-neutral-900">Checklist</h3>
              <div className="grid gap-2">
                {Object.entries(inspection.checklist_responses || {}).length ? Object.entries(inspection.checklist_responses).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between rounded border border-neutral-100 bg-neutral-50 px-3 py-2 text-sm">
                    <span className="font-semibold text-neutral-800">{key.replaceAll("_", " ")}</span>
                    <span className="text-neutral-600">{String(value)}</span>
                  </div>
                )) : <p className="text-sm text-neutral-600">No checklist responses recorded.</p>}
              </div>
            </div>
          </section>

          <aside className="grid gap-4">
            <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="mb-3 flex items-center gap-2"><MessageSquareText className="text-brand-700" size={18} /><h3 className="text-sm font-bold text-neutral-900">Employer Responses</h3></div>
              <div className="grid gap-2">
                {(inspection.responses || []).length ? inspection.responses?.map((response) => (
                  <div key={response.id} className="rounded border border-neutral-100 bg-neutral-50 p-3 text-sm">
                    <p className="font-semibold text-neutral-900">{response.response_type.replaceAll("_", " ")}</p>
                    <p className="mt-1 text-neutral-600">{response.content || "No comment supplied."}</p>
                    <p className="mt-2 text-xs text-neutral-500">{response.submitted_by_name || "Employer"} / {dateLabel(response.submitted_at)}</p>
                  </div>
                )) : <p className="text-sm text-neutral-600">No employer responses yet.</p>}
              </div>
            </section>

            <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="mb-3 flex items-center gap-2"><History className="text-brand-700" size={18} /><h3 className="text-sm font-bold text-neutral-900">Audit History</h3></div>
              <div className="grid gap-2">
                {(inspection.audit_history || []).length ? inspection.audit_history?.map((log) => (
                  <div key={log.id} className="rounded border border-neutral-100 bg-neutral-50 p-3 text-xs">
                    <p className="font-semibold text-neutral-900">{String(log.metadata.event || log.action).replaceAll("_", " ")}</p>
                    <p className="mt-1 text-neutral-600">{log.actor_name || "System"} / {dateLabel(log.created_at)}</p>
                  </div>
                )) : <p className="text-sm text-neutral-600">No audit activity yet.</p>}
              </div>
            </section>
          </aside>
        </div>
      )}
    </PortalShell>
  );
}
