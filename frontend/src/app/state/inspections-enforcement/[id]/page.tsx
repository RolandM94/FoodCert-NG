"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle, ArrowLeft, Camera, ClipboardCheck, FileText,
  History, Image, MessageSquareText, Plus, ShieldCheck,
} from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { KoboFormRenderer, type KoboSchema } from "@/components/forms/kobo-form-renderer";
import { fetchInspectionFormWorkspace, getEvidence, getFindings, createFinding, escalateInspection, createFollowUp } from "@/lib/api/inspections";
import { fetchStateInspection, reviewStateInspection, closeStateInspection } from "@/lib/api/state";
import type { KoboLogic } from "@/lib/forms/kobo-logic";
import { getApiErrorMessage } from "@/lib/api/client";
import { useState } from "react";

function dateLabel(value?: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const params = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const inspectionQuery = useQuery({
    queryKey: ["ie-inspection", params.id],
    queryFn: () => fetchStateInspection(params.id),
    enabled: Boolean(params.id),
  });
  const formQuery = useQuery({
    queryKey: ["ie-form-workspace", params.id],
    queryFn: () => fetchInspectionFormWorkspace(params.id),
    enabled: Boolean(params.id),
  });
  const findingsQuery = useQuery({
    queryKey: ["ie-findings", params.id],
    queryFn: () => getFindings(params.id),
    enabled: Boolean(params.id),
  });
  const evidenceQuery = useQuery({
    queryKey: ["ie-evidence", params.id],
    queryFn: () => getEvidence(params.id),
    enabled: Boolean(params.id),
  });

  const closeMut = useMutation({
    mutationFn: () => closeStateInspection(params.id, "Closed from inspection detail."),
    onSuccess: () => { setSuccess("Inspection closed."); setError(""); queryClient.invalidateQueries({ queryKey: ["ie-inspection", params.id] }); },
    onError: (err) => setError(getApiErrorMessage(err, "Could not close.")),
  });

  const escalateMut = useMutation({
    mutationFn: () => escalateInspection(params.id, { severity: "high", summary: "Escalated from detail view." }),
    onSuccess: () => { setSuccess("Inspection escalated to enforcement case."); setError(""); queryClient.invalidateQueries({ queryKey: ["ie-inspection", params.id] }); },
    onError: (err) => setError(getApiErrorMessage(err, "Could not escalate.")),
  });

  const followUpMut = useMutation({
    mutationFn: () => createFollowUp(params.id, { reason: "Follow-up inspection requested." }),
    onSuccess: () => { setSuccess("Follow-up inspection created."); setError(""); },
    onError: (err) => setError(getApiErrorMessage(err, "Could not create follow-up.")),
  });

  const inspection = inspectionQuery.data;
  const formResponse = formQuery.data?.response || null;
  const formSchema = (formResponse?.template_schema || {}) as KoboSchema;
  const formLogic = (formResponse?.template_logic || {}) as KoboLogic;
  const findings = findingsQuery.data || [];
  const evidence = evidenceQuery.data || [];

  return (
    <PortalShell role="state_admin" title="Inspection Detail" description="Full inspection workspace with findings, evidence, notices, and enforcement actions.">
      <div className="grid gap-5">
        <Link className="inline-flex w-fit items-center gap-2 text-sm font-bold text-brand-700" href="/state/inspections-enforcement?tab=inspections">
          <ArrowLeft size={16} /> Back to inspections
        </Link>

        {error ? <p className="rounded border border-danger-100 bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</p> : null}
        {success ? <p className="rounded border border-brand-100 bg-brand-50 px-3 py-2 text-sm font-semibold text-brand-800">{success}</p> : null}

        {!inspection ? (
          <div className="rounded-lg border border-neutral-200 bg-white p-6 text-sm text-neutral-500">{inspectionQuery.isLoading ? "Loading..." : "Inspection not found."}</div>
        ) : (
          <>
            <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2"><ClipboardCheck className="text-brand-700" size={18} /><h2 className="text-lg font-bold text-neutral-900">{inspection.employer_name}</h2></div>
                  <p className="mt-1 text-sm text-neutral-500">{inspection.inspector_name || "No inspector"} · {dateLabel(inspection.inspection_date)} · {inspection.lga_name || "LGA not set"}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <StatusBadge status={inspection.status} />
                  <StatusBadge status={inspection.enforcement_action} />
                </div>
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <div><p className="text-xs font-bold uppercase text-neutral-500">Score</p><p className="text-sm font-semibold">{inspection.compliance_score ? `${inspection.compliance_score}%` : "Not scored"}</p></div>
                <div><p className="text-xs font-bold uppercase text-neutral-500">Reference</p><p className="text-sm font-semibold">{inspection.reference || "—"}</p></div>
                <div><p className="text-xs font-bold uppercase text-neutral-500">Submitted</p><p className="text-sm font-semibold">{dateLabel(inspection.submitted_at)}</p></div>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <button className="h-8 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700 disabled:opacity-50" disabled={closeMut.isPending || inspection.status === "closed"} onClick={() => closeMut.mutate()} type="button">Close Inspection</button>
                <button className="h-8 rounded border border-warning-200 px-3 text-xs font-bold text-warning-700 disabled:opacity-50" disabled={escalateMut.isPending} onClick={() => escalateMut.mutate()} type="button">Escalate to Case</button>
                <button className="h-8 rounded border border-brand-200 px-3 text-xs font-bold text-brand-700 disabled:opacity-50" disabled={followUpMut.isPending} onClick={() => followUpMut.mutate()} type="button">Schedule Follow-up</button>
              </div>
            </section>

            {formResponse && formSchema.sections?.length ? (
              <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
                <div className="flex items-center justify-between border-b border-neutral-200 p-4">
                  <div className="flex items-center gap-2"><FileText className="text-brand-700" size={16} /><h3 className="text-sm font-bold text-neutral-900">{formResponse.template_title || "Inspection Checklist"}</h3></div>
                  <StatusBadge status={formResponse.status} />
                </div>
                <div className="p-4">
                  <KoboFormRenderer schema={formSchema} values={formResponse.response_json || {}} readOnly logic={formLogic} />
                </div>
              </section>
            ) : null}

            <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
              <div className="flex items-center justify-between border-b border-neutral-200 p-4">
                <div className="flex items-center gap-2"><AlertTriangle className="text-warning-700" size={16} /><h3 className="text-sm font-bold text-neutral-900">Findings ({findings.length})</h3></div>
              </div>
              <div className="grid gap-2 p-4">
                {findings.map((finding) => (
                  <div key={String(finding.id)} className="rounded border border-neutral-100 bg-neutral-50 p-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <StatusBadge status={String(finding.severity || "minor")} />
                      <StatusBadge status={String(finding.status || "open")} />
                      <span className="text-xs text-neutral-500">{String(finding.category || "").replaceAll("_", " ")}</span>
                    </div>
                    <p className="mt-2 text-sm font-semibold text-neutral-900">{String(finding.description || "Finding")}</p>
                    {finding.recommended_action ? <p className="mt-1 text-xs text-neutral-600">{String(finding.recommended_action)}</p> : null}
                  </div>
                ))}
                {!findings.length ? <p className="text-sm text-neutral-500">No findings recorded.</p> : null}
              </div>
            </section>

            <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
              <div className="flex items-center justify-between border-b border-neutral-200 p-4">
                <div className="flex items-center gap-2"><Image className="text-neutral-600" size={16} /><h3 className="text-sm font-bold text-neutral-900">Evidence ({evidence.length})</h3></div>
              </div>
              <div className="grid gap-2 p-4 sm:grid-cols-2 lg:grid-cols-3">
                {evidence.map((item) => (
                  <div key={String(item.id)} className="rounded border border-neutral-100 bg-neutral-50 p-3">
                    <div className="flex items-center gap-2">
                      <Camera size={14} className="text-neutral-400" />
                      <span className="text-xs font-semibold text-neutral-800">{String(item.evidence_type || "photo").replaceAll("_", " ")}</span>
                    </div>
                    <p className="mt-1 text-xs text-neutral-600">{String(item.caption || "No caption")}</p>
                    {item.file_url ? <a className="mt-1 block text-xs font-bold text-brand-700" href={String(item.file_url)} target="_blank" rel="noreferrer">View file</a> : null}
                  </div>
                ))}
                {!evidence.length ? <p className="text-sm text-neutral-500">No evidence uploaded.</p> : null}
              </div>
            </section>

            {(inspection.responses || []).length ? (
              <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
                <div className="flex items-center gap-2 border-b border-neutral-200 p-4"><MessageSquareText className="text-brand-700" size={16} /><h3 className="text-sm font-bold text-neutral-900">Employer Responses</h3></div>
                <div className="grid gap-2 p-4">
                  {inspection.responses?.map((resp) => (
                    <div key={resp.id} className="rounded border border-neutral-100 bg-neutral-50 p-3 text-sm">
                      <p className="font-semibold text-neutral-900">{resp.response_type.replaceAll("_", " ")}</p>
                      <p className="mt-1 text-neutral-600">{resp.content || "No comment."}</p>
                      <p className="mt-2 text-xs text-neutral-500">{resp.submitted_by_name || "Employer"} · {dateLabel(resp.submitted_at)}</p>
                    </div>
                  ))}
                </div>
              </section>
            ) : null}

            {(inspection.audit_history || []).length ? (
              <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
                <div className="flex items-center gap-2 border-b border-neutral-200 p-4"><History className="text-neutral-600" size={16} /><h3 className="text-sm font-bold text-neutral-900">Audit Log</h3></div>
                <div className="grid gap-2 p-4">
                  {inspection.audit_history?.map((log) => (
                    <div key={log.id} className="rounded border border-neutral-100 bg-neutral-50 p-2 text-xs">
                      <p className="font-semibold text-neutral-800">{String(log.metadata.event || log.action).replaceAll("_", " ")}</p>
                      <p className="text-neutral-500">{log.actor_name || "System"} · {dateLabel(log.created_at)}</p>
                    </div>
                  ))}
                </div>
              </section>
            ) : null}
          </>
        )}
      </div>
    </PortalShell>
  );
}
