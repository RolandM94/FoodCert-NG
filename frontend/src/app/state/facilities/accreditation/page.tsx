"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ClipboardCheck } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import {
  approveStateFacilityApplication,
  fetchStateFacilityApplications,
  reinstateStateFacilityApplication,
  rejectStateFacilityApplication,
  suspendStateFacilityApplication,
} from "@/lib/api/state";
import type { AccreditationStatus, FacilityAccreditationApplication } from "@/types/facilities";

const STATUS_OPTIONS: [string, string][] = [
  ["", "All applications"],
  ["submitted", "Submitted"],
  ["under_review", "Under review"],
  ["approved", "Approved"],
  ["rejected", "Rejected"],
  ["suspended", "Suspended"],
];

type ActionName = "approve" | "reject" | "suspend" | "reinstate";

function dateLabel(value?: string) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

function checklistScore(row: FacilityAccreditationApplication) {
  const keys: (keyof FacilityAccreditationApplication)[] = [
    "has_reporting_policy",
    "has_medical_records_computers",
    "has_computer_operators",
    "has_standard_forms",
    "has_laboratory_request_forms",
    "has_patient_files",
    "has_qr_certificate_capability",
    "has_internet_access",
    "has_trained_records_staff",
    "has_trained_clinical_staff",
    "has_trained_non_clinical_staff",
  ];
  return `${keys.filter((key) => row[key]).length}/${keys.length}`;
}

function allowedActions(status: AccreditationStatus): ActionName[] {
  if (status === "submitted" || status === "under_review") return ["approve", "reject"];
  if (status === "approved") return ["suspend"];
  if (status === "suspended") return ["reinstate"];
  return [];
}

export default function Page() {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState("");
  const [actionTarget, setActionTarget] = useState<{ application: FacilityAccreditationApplication; action: ActionName } | null>(null);
  const [comment, setComment] = useState("");

  const applicationsQuery = useQuery({
    queryKey: ["state-facility-applications", status],
    queryFn: () => fetchStateFacilityApplications({ status: status || undefined }),
  });

  const actionMutation = useMutation({
    mutationFn: ({ application, action, reviewComment }: { application: FacilityAccreditationApplication; action: ActionName; reviewComment: string }) => {
      if (action === "approve") return approveStateFacilityApplication(application.id, reviewComment);
      if (action === "reject") return rejectStateFacilityApplication(application.id, reviewComment);
      if (action === "suspend") return suspendStateFacilityApplication(application.id, reviewComment);
      return reinstateStateFacilityApplication(application.id, reviewComment);
    },
    onSuccess: () => {
      setActionTarget(null);
      setComment("");
      queryClient.invalidateQueries({ queryKey: ["state-facility-applications"] });
      queryClient.invalidateQueries({ queryKey: ["state-facilities"] });
    },
  });

  const applications = applicationsQuery.data || [];
  const requiresComment = actionTarget?.action === "reject" || actionTarget?.action === "suspend";

  return (
    <PortalShell role="state_admin" title="Facility accreditation" description="Approve, reject, suspend, or reactivate facility accreditation requests.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <label className="grid max-w-xs gap-1 text-xs font-bold uppercase tracking-wide text-slate-500">
            Application status
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm normal-case tracking-normal text-slate-700" value={status} onChange={(event) => setStatus(event.target.value)}>
              {STATUS_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
        </section>

        <section className="grid gap-3">
          <div className="flex items-center gap-2">
            <ClipboardCheck className="text-brand-deep" size={18} />
            <h2 className="text-base font-bold text-slate-950">Accreditation Queue</h2>
          </div>
          {applicationsQuery.isError ? <p className="rounded bg-rose-50 p-3 text-sm font-semibold text-rose-700">Could not load accreditation applications.</p> : null}
          <DataTable<FacilityAccreditationApplication>
            columns={[
              { key: "facility", header: "Facility", render: (row) => <p className="font-bold text-slate-950">{row.facility_name}</p> },
              { key: "checklist", header: "Checklist", render: (row) => <span className={row.checklist_complete ? "font-bold text-emerald-700" : "font-bold text-amber-700"}>{checklistScore(row)}</span> },
              { key: "status", header: "Status", render: (row) => <StatusCell status={row.application_status} /> },
              { key: "submitted", header: "Submitted", render: (row) => dateLabel(row.submitted_at || row.created_at) },
              { key: "reviewer", header: "Reviewer", render: (row) => row.reviewer_name || "Not reviewed" },
              {
                key: "actions",
                header: "Actions",
                render: (row) => (
                  <div className="flex flex-wrap gap-2">
                    {allowedActions(row.application_status).map((action) => (
                      <button
                        className="h-8 rounded border border-slate-200 px-3 text-xs font-bold capitalize text-slate-700 hover:bg-slate-50"
                        key={action}
                        onClick={() => setActionTarget({ application: row, action })}
                        type="button"
                      >
                        {action}
                      </button>
                    ))}
                  </div>
                ),
              },
            ]}
            rows={applications}
            empty={applicationsQuery.isLoading ? "Loading accreditation applications..." : "No applications match the current filter."}
          />
        </section>
      </div>

      {actionTarget ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
          <div className="w-full max-w-md rounded-lg border border-slate-200 bg-white shadow-xl">
            <div className="border-b border-slate-100 px-6 py-4">
              <h2 className="text-lg font-bold capitalize text-slate-950">{actionTarget.action} facility accreditation</h2>
              <p className="mt-1 text-sm text-slate-500">{actionTarget.application.facility_name}</p>
            </div>
            <form
              className="grid gap-4 p-6"
              onSubmit={(event) => {
                event.preventDefault();
                actionMutation.mutate({ application: actionTarget.application, action: actionTarget.action, reviewComment: comment });
              }}
            >
              <label className="grid gap-1 text-sm font-semibold text-slate-700">
                Review comment {requiresComment ? <span className="text-red-500">*</span> : null}
                <textarea className="rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm" required={requiresComment} rows={3} value={comment} onChange={(event) => setComment(event.target.value)} />
              </label>
              {actionMutation.isError ? <p className="rounded bg-red-50 px-3 py-2 text-sm font-semibold text-red-700">Could not complete this accreditation action.</p> : null}
              <div className="flex justify-end gap-3">
                <button className="h-10 rounded border border-slate-200 px-4 text-sm font-semibold text-slate-600 hover:bg-slate-50" onClick={() => setActionTarget(null)} type="button">Cancel</button>
                <button className="h-10 rounded bg-brand-green px-4 text-sm font-bold capitalize text-white hover:bg-brand-deep disabled:opacity-60" disabled={actionMutation.isPending} type="submit">{actionTarget.action}</button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </PortalShell>
  );
}
