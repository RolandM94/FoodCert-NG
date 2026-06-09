"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ClipboardCheck, ClipboardList, Download, ShieldCheck } from "lucide-react";
import { useMemo, useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import {
  assignStateInspection,
  closeStateInspection,
  fetchStateEmployers,
  fetchStateInspections,
  fetchStateUsers,
  reviewStateInspection,
  type StateInspectionItem,
} from "@/lib/api/state";
import { downloadCsv } from "@/lib/export/csv";
import type { EnforcementAction, InspectionStatus } from "@/types/inspections";

const enforcementOptions: Array<{ value: EnforcementAction | ""; label: string }> = [
  { value: "", label: "All enforcement" },
  { value: "none", label: "None" },
  { value: "advisory", label: "Advisory" },
  { value: "warning", label: "Warning" },
  { value: "compliance_notice", label: "Compliance notice" },
  { value: "follow_up_required", label: "Follow-up required" },
  { value: "sanction_recommended", label: "Sanction recommended" },
  { value: "escalated_to_state", label: "Escalated to state" },
];

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

function nameFor(user: { first_name?: string; last_name?: string; email?: string; username?: string }) {
  return [user.first_name, user.last_name].filter(Boolean).join(" ") || user.email || user.username || "Unnamed user";
}

export default function Page() {
  const queryClient = useQueryClient();
  const [queue, setQueue] = useState<"" | "active" | "submitted" | "enforcement">("active");
  const [status, setStatus] = useState<InspectionStatus | "">("");
  const [enforcementAction, setEnforcementAction] = useState<EnforcementAction | "">("");
  const [search, setSearch] = useState("");
  const [selectedInspectionId, setSelectedInspectionId] = useState("");
  const [selectedInspectorId, setSelectedInspectorId] = useState("");
  const [selectedEmployerId, setSelectedEmployerId] = useState("");
  const [assignmentFindings, setAssignmentFindings] = useState("");
  const [reviewFindings, setReviewFindings] = useState("");
  const [reviewAction, setReviewAction] = useState<EnforcementAction>("none");
  const [closureNotes, setClosureNotes] = useState("");

  const inspectionsQuery = useQuery({
    queryKey: ["state-inspections", queue, status, enforcementAction, search],
    queryFn: () => fetchStateInspections({ queue, status, enforcement_action: enforcementAction, search }),
  });
  const usersQuery = useQuery({ queryKey: ["state-users"], queryFn: fetchStateUsers });
  const employersQuery = useQuery({ queryKey: ["state-employers-for-inspections"], queryFn: () => fetchStateEmployers() });
  const rows = inspectionsQuery.data || [];
  const inspectors = useMemo(() => (usersQuery.data || []).filter((user) => user.role === "inspector"), [usersQuery.data]);
  const selectedInspection = rows.find((inspection) => inspection.id === selectedInspectionId) || rows[0];

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["state-inspections"] });

  const assignMutation = useMutation({
    mutationFn: () =>
      assignStateInspection({
        inspector: selectedInspectorId,
        employer: selectedEmployerId,
        findings: assignmentFindings,
      }),
    onSuccess: () => {
      setAssignmentFindings("");
      invalidate();
    },
  });

  const reviewMutation = useMutation({
    mutationFn: () =>
      reviewStateInspection(selectedInspection?.id || "", {
        enforcement_action: reviewAction,
        findings: reviewFindings,
      }),
    onSuccess: (inspection) => {
      setSelectedInspectionId(inspection.id);
      setReviewFindings("");
      invalidate();
    },
  });

  const closeMutation = useMutation({
    mutationFn: () => closeStateInspection(selectedInspection?.id || "", closureNotes),
    onSuccess: (inspection) => {
      setSelectedInspectionId(inspection.id);
      setClosureNotes("");
      invalidate();
    },
  });

  return (
    <PortalShell role="state_admin" title="Inspections" description="Assign inspections, review submitted reports, and supervise enforcement closure.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 xl:grid-cols-[1fr_180px_220px_180px_auto]">
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search employer, inspector, or findings" />
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={queue} onChange={(event) => setQueue(event.target.value as typeof queue)}>
              <option value="">All queues</option>
              <option value="active">Active</option>
              <option value="submitted">Submitted</option>
              <option value="enforcement">Enforcement</option>
            </select>
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={enforcementAction} onChange={(event) => setEnforcementAction(event.target.value as EnforcementAction | "")}>
              {enforcementOptions.map((option) => <option key={option.value || "all"} value={option.value}>{option.label}</option>)}
            </select>
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value as InspectionStatus | "")}>
              <option value="">All statuses</option>
              <option value="draft">Draft</option>
              <option value="in_progress">In progress</option>
              <option value="submitted">Submitted</option>
              <option value="employer_response_submitted">Employer response</option>
              <option value="closed">Closed</option>
            </select>
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-700 px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-neutral-300"
              disabled={!rows.length}
              onClick={() =>
                downloadCsv("state-inspections.csv", rows, [
                  { header: "Employer", value: (row) => row.employer_name },
                  { header: "LGA", value: (row) => row.lga_name },
                  { header: "Inspector", value: (row) => row.inspector_name },
                  { header: "Date", value: (row) => row.inspection_date },
                  { header: "Compliance score", value: (row) => row.compliance_score },
                  { header: "Enforcement", value: (row) => row.enforcement_action },
                  { header: "Status", value: (row) => row.status },
                  { header: "Submitted at", value: (row) => row.submitted_at },
                ])
              }
              type="button"
            >
              <Download size={16} />
              Export
            </button>
          </div>
        </section>

        <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
          <div className="grid gap-3">
            <div className="flex items-center gap-2"><ClipboardCheck className="text-brand-700" size={18} /><h2 className="text-base font-bold text-neutral-900">Inspection Workflow</h2></div>
            <DataTable<StateInspectionItem>
              columns={[
                { key: "employer", header: "Employer", render: (row) => <button className="text-left" onClick={() => setSelectedInspectionId(row.id)} type="button"><p className="font-bold text-neutral-900">{row.employer_name}</p><p className="text-xs text-neutral-500">{row.lga_name || "LGA not set"}</p></button> },
                { key: "inspector", header: "Inspector", render: (row) => row.inspector_name || "Unassigned" },
                { key: "date", header: "Date", render: (row) => dateLabel(row.inspection_date) },
                { key: "score", header: "Score", render: (row) => row.compliance_score ? `${row.compliance_score}%` : "Not scored" },
                { key: "enforcement", header: "Enforcement", render: (row) => <StatusCell status={row.enforcement_action} /> },
                { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
              ]}
              rows={rows}
              empty={inspectionsQuery.isLoading ? "Loading inspections..." : "No inspections match the current filters."}
            />
          </div>

          <aside className="grid gap-4">
            <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="mb-3 flex items-center gap-2"><ClipboardList className="text-brand-700" size={18} /><h3 className="text-sm font-bold text-neutral-900">Assign Inspection</h3></div>
              <div className="grid gap-3">
                <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={selectedInspectorId} onChange={(event) => setSelectedInspectorId(event.target.value)}>
                  <option value="">Select inspector</option>
                  {inspectors.map((user) => <option key={user.id} value={user.id}>{nameFor(user)}</option>)}
                </select>
                <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={selectedEmployerId} onChange={(event) => setSelectedEmployerId(event.target.value)}>
                  <option value="">Select employer</option>
                  {(employersQuery.data || []).map((employer) => <option key={employer.id} value={employer.id}>{employer.business_name}</option>)}
                </select>
                <textarea className="min-h-20 rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm" value={assignmentFindings} onChange={(event) => setAssignmentFindings(event.target.value)} placeholder="Assignment note or scope" />
                <button className="h-10 rounded bg-brand-700 px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-neutral-300" disabled={!selectedInspectorId || !selectedEmployerId || assignMutation.isPending} onClick={() => assignMutation.mutate()} type="button">
                  {assignMutation.isPending ? "Assigning..." : "Assign"}
                </button>
              </div>
            </section>

            <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="mb-3 flex items-center gap-2"><ShieldCheck className="text-brand-700" size={18} /><h3 className="text-sm font-bold text-neutral-900">Review & Close</h3></div>
              {selectedInspection ? (
                <div className="grid gap-3">
                  <div>
                    <p className="font-bold text-neutral-900">{selectedInspection.employer_name}</p>
                    <p className="text-xs text-neutral-500">{selectedInspection.inspector_name || "No inspector"} / {dateLabel(selectedInspection.inspection_date)}</p>
                  </div>
                  <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={reviewAction} onChange={(event) => setReviewAction(event.target.value as EnforcementAction)}>
                    {enforcementOptions.filter((option) => option.value).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                  </select>
                  <textarea className="min-h-24 rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm" value={reviewFindings} onChange={(event) => setReviewFindings(event.target.value)} placeholder="Review findings or enforcement note" />
                  <button className="h-10 rounded border border-brand-700 px-3 text-sm font-semibold text-brand-700 disabled:cursor-not-allowed disabled:border-neutral-300 disabled:text-neutral-400" disabled={reviewMutation.isPending} onClick={() => reviewMutation.mutate()} type="button">
                    {reviewMutation.isPending ? "Saving..." : "Save review"}
                  </button>
                  <textarea className="min-h-20 rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm" value={closureNotes} onChange={(event) => setClosureNotes(event.target.value)} placeholder="Closure notes" />
                  <button className="h-10 rounded bg-neutral-900 px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-neutral-300" disabled={closeMutation.isPending || selectedInspection.status === "closed"} onClick={() => closeMutation.mutate()} type="button">
                    {closeMutation.isPending ? "Closing..." : "Close inspection"}
                  </button>
                  <div className="grid gap-2 border-t border-neutral-100 pt-3">
                    {(selectedInspection.audit_history || []).slice(0, 4).map((log) => (
                      <div key={log.id} className="rounded border border-neutral-100 bg-neutral-50 p-2 text-xs text-neutral-600">
                        <p className="font-semibold text-neutral-800">{String(log.metadata.event || log.action).replaceAll("_", " ")}</p>
                        <p>{log.actor_name || "System"} / {dateLabel(log.created_at)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-sm text-neutral-600">Select an inspection to review enforcement history.</p>
              )}
            </section>
          </aside>
        </section>
      </div>
    </PortalShell>
  );
}
