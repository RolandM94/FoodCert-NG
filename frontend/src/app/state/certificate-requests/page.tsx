"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileCheck2 } from "lucide-react";
import { useState } from "react";
import { AssessmentAuditTimeline } from "@/components/assessments/assessment-audit-timeline";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { getAssessmentAuditTimeline } from "@/lib/api/assessments";
import {
  approveStateCertificateValidationRequest,
  fetchStateCertificateValidationQueue,
  rejectStateCertificateValidationRequest,
  requestStateCertificateValidationClarification,
  type StateCertificateValidationRequest,
} from "@/lib/api/state";
import type { AssessmentAuditTimelineItem } from "@/types/assessments";

const STATUS_OPTIONS = [
  ["", "All requests"],
  ["pending_validation", "Pending validation"],
  ["correction_requested", "Clarification requested"],
  ["approved", "Approved"],
  ["rejected", "Rejected"],
];

type ActionName = "approve" | "reject" | "request-clarification";

function dateLabel(value?: string) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

function eligibilitySummary(row: StateCertificateValidationRequest) {
  const evidence = row.assessment_evidence_summary;
  const checks = evidence ? [
    ["Payment", evidence.payment_status === "success"],
    ["Declaration", evidence.declaration_status === "validated"],
    ["Exam", evidence.physical_exam_status === "completed"],
    ["Lab", evidence.lab_status === "reviewed"],
    ["Vaccination", evidence.vaccination_status === "reviewed"],
    ["Signed fit", evidence.fit_signed],
    ["Report", evidence.medical_report_generated],
  ] : [
    ["Payment", row.payment_status === "success"],
    ["Declaration", row.declaration_status === "validated"],
    ["Exam", row.physical_exam_status === "completed"],
    ["Lab", row.lab_status === "reviewed"],
    ["Vaccination", row.vaccination_status === "reviewed"],
    ["Signed fit", row.final_decision === "fit"],
  ];
  return `${checks.filter(([, ready]) => ready).length}/${checks.length}`;
}

function allowedActions(row: StateCertificateValidationRequest): ActionName[] {
  if (row.status !== "pending_validation") return [];
  return ["approve", "reject", "request-clarification"];
}

export default function Page() {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState("pending_validation");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [actionTarget, setActionTarget] = useState<{ request: StateCertificateValidationRequest; action: ActionName } | null>(null);
  const [timelineTarget, setTimelineTarget] = useState<StateCertificateValidationRequest | null>(null);
  const [timeline, setTimeline] = useState<AssessmentAuditTimelineItem[]>([]);
  const [notes, setNotes] = useState("");

  const queueQuery = useQuery({
    queryKey: ["state-certificate-validation", status, dateFrom, dateTo],
    queryFn: () => fetchStateCertificateValidationQueue({
      status: status || undefined,
      date_from: dateFrom || undefined,
      date_to: dateTo || undefined,
    }),
  });

  const actionMutation = useMutation({
    mutationFn: ({ request, action, reviewNotes }: { request: StateCertificateValidationRequest; action: ActionName; reviewNotes: string }) => {
      if (action === "approve") return approveStateCertificateValidationRequest(request.id, reviewNotes);
      if (action === "reject") return rejectStateCertificateValidationRequest(request.id, reviewNotes);
      return requestStateCertificateValidationClarification(request.id, reviewNotes);
    },
    onSuccess: () => {
      setActionTarget(null);
      setNotes("");
      queryClient.invalidateQueries({ queryKey: ["state-certificate-validation"] });
    },
  });

  async function openTimeline(row: StateCertificateValidationRequest) {
    setTimelineTarget(row);
    setTimeline(await getAssessmentAuditTimeline(row.assessment));
  }

  const rows = queueQuery.data || [];
  const requiresNotes = actionTarget?.action === "reject" || actionTarget?.action === "request-clarification";

  return (
    <PortalShell role="state_admin" title="Certificate requests" description="Validate fit assessments before certificate issuance.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[220px_180px_180px_1fr]">
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-slate-500">
              Status
              <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm normal-case tracking-normal text-slate-700" value={status} onChange={(event) => setStatus(event.target.value)}>
                {STATUS_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-slate-500">
              From
              <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm normal-case tracking-normal text-slate-700" type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} />
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-slate-500">
              To
              <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm normal-case tracking-normal text-slate-700" type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} />
            </label>
          </div>
        </section>

        <section className="grid gap-3">
          <div className="flex items-center gap-2">
            <FileCheck2 className="text-brand-deep" size={18} />
            <h2 className="text-base font-bold text-slate-950">Validation Queue</h2>
          </div>
          {queueQuery.isError ? <p className="rounded bg-rose-50 p-3 text-sm font-semibold text-rose-700">Could not load certificate validation requests.</p> : null}
          <DataTable<StateCertificateValidationRequest>
            columns={[
              { key: "handler", header: "Handler", render: (row) => <div><p className="font-bold text-slate-950">{row.food_handler_name || "Unknown"}</p><p className="text-xs text-slate-500">{row.food_handler_category?.replaceAll("_", " ") || "No category"}</p></div> },
              { key: "facility", header: "Facility", render: (row) => row.facility_name || "Unknown" },
              { key: "eligibility", header: "Evidence", render: (row) => {
                const score = eligibilitySummary(row);
                const [ready, total] = score.split("/");
                return <span className={ready === total ? "font-bold text-emerald-700" : "font-bold text-amber-700"}>{score}</span>;
              } },
              { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
              { key: "certificate", header: "Certificate", render: (row) => row.certificate_number || "Not issued" },
              { key: "created", header: "Created", render: (row) => dateLabel(row.created_at) },
              {
                key: "actions",
                header: "Actions",
                render: (row) => (
                  <div className="flex flex-wrap gap-2">
                    {allowedActions(row).map((action) => (
                      <button
                        className="h-8 rounded border border-slate-200 px-3 text-xs font-bold capitalize text-slate-700 hover:bg-slate-50"
                        key={action}
                        onClick={() => setActionTarget({ request: row, action })}
                        type="button"
                      >
                        {action.replace("-", " ")}
                      </button>
                    ))}
                    <button
                      className="h-8 rounded border border-slate-200 px-3 text-xs font-bold text-slate-700 hover:bg-slate-50"
                      onClick={() => void openTimeline(row)}
                      type="button"
                    >
                      Timeline
                    </button>
                  </div>
                ),
              },
            ]}
            rows={rows}
            empty={queueQuery.isLoading ? "Loading certificate requests..." : "No certificate requests match the current filters."}
          />
        </section>
      </div>

      {actionTarget ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
          <div className="w-full max-w-md rounded-lg border border-slate-200 bg-white shadow-xl">
            <div className="border-b border-slate-100 px-6 py-4">
              <h2 className="text-lg font-bold capitalize text-slate-950">{actionTarget.action.replace("-", " ")} certificate request</h2>
              <p className="mt-1 text-sm text-slate-500">{actionTarget.request.food_handler_name} at {actionTarget.request.facility_name}</p>
            </div>
            <form
              className="grid gap-4 p-6"
              onSubmit={(event) => {
                event.preventDefault();
                actionMutation.mutate({ request: actionTarget.request, action: actionTarget.action, reviewNotes: notes });
              }}
            >
              <label className="grid gap-1 text-sm font-semibold text-slate-700">
                Review notes {requiresNotes ? <span className="text-red-500">*</span> : null}
                <textarea className="rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm" required={requiresNotes} rows={3} value={notes} onChange={(event) => setNotes(event.target.value)} />
              </label>
              {actionMutation.isError ? <p className="rounded bg-red-50 px-3 py-2 text-sm font-semibold text-red-700">Could not complete this validation action.</p> : null}
              <div className="flex justify-end gap-3">
                <button className="h-10 rounded border border-slate-200 px-4 text-sm font-semibold text-slate-600 hover:bg-slate-50" onClick={() => setActionTarget(null)} type="button">Cancel</button>
                <button className="h-10 rounded bg-brand-green px-4 text-sm font-bold capitalize text-white hover:bg-brand-deep disabled:opacity-60" disabled={actionMutation.isPending} type="submit">{actionTarget.action.replace("-", " ")}</button>
              </div>
            </form>
          </div>
        </div>
      ) : null}

      {timelineTarget ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
          <div className="max-h-[85vh] w-full max-w-2xl overflow-auto rounded-lg bg-white p-4 shadow-xl">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-bold text-slate-950">Assessment timeline</h2>
                <p className="text-sm text-slate-500">{timelineTarget.food_handler_name} at {timelineTarget.facility_name}</p>
              </div>
              <button className="h-9 rounded border border-slate-200 px-3 text-sm font-bold text-slate-700" onClick={() => setTimelineTarget(null)} type="button">Close</button>
            </div>
            <AssessmentAuditTimeline items={timeline} />
          </div>
        </div>
      ) : null}
    </PortalShell>
  );
}
