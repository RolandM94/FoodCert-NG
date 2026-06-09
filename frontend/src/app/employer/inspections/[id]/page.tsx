"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, ClipboardList, FileImage, MapPin, MessageSquareText } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { InspectionResponseForm } from "@/components/ui/inspection-response-form";
import { listEmployers } from "@/lib/api/identity";
import { getEmployerInspection, submitEmployerInspectionResponse } from "@/lib/api/inspections";
import type { InspectionResponseType, InspectionStatus } from "@/types/inspections";

function formatDate(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

function label(value: string) {
  return value.replaceAll("_", " ");
}

function StatusBadge({ status }: { status: InspectionStatus }) {
  const tone =
    status === "closed"
      ? "bg-neutral-100 text-neutral-700 ring-neutral-200"
      : status === "employer_response_submitted"
        ? "bg-brand-50 text-brand-700 ring-brand-200"
        : status === "submitted"
          ? "bg-warning-50 text-warning-700 ring-warning-100"
          : "bg-info-50 text-info-700 ring-info-100";
  return <span className={`rounded px-2 py-1 text-xs font-bold capitalize ring-1 ${tone}`}>{label(status)}</span>;
}

function checklistValue(value: boolean | string | number) {
  if (typeof value === "boolean") return value ? "Pass" : "Needs attention";
  return String(value);
}

export default function Page() {
  const params = useParams<{ id: string }>();
  const queryClient = useQueryClient();

  const employersQuery = useQuery({
    queryKey: ["employers", "me"],
    queryFn: listEmployers,
  });
  const employer = employersQuery.data?.[0];

  const inspectionQuery = useQuery({
    queryKey: ["employer-inspection", employer?.id, params.id],
    queryFn: () => getEmployerInspection(employer!.id, params.id),
    enabled: Boolean(employer?.id && params.id),
  });

  const mutation = useMutation({
    mutationFn: (payload: { response_type: InspectionResponseType; content: string; evidence_file_url?: string }) =>
      submitEmployerInspectionResponse(employer!.id, params.id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["employer-inspection", employer?.id, params.id] });
      queryClient.invalidateQueries({ queryKey: ["employer-inspections", employer?.id] });
    },
  });

  const inspection = inspectionQuery.data;
  const checklist = inspection ? Object.entries(inspection.checklist_responses || {}) : [];

  return (
    <PortalShell role="employer" title="Inspection Detail" description="Review the submitted report, evidence, notice, and employer response history.">
      <div className="grid gap-6">
        <Link className="inline-flex w-fit items-center gap-2 text-sm font-bold text-brand-700 hover:text-brand-600" href="/employer/inspections">
          <ArrowLeft size={16} />
          Back to inspections
        </Link>

        {inspectionQuery.isError ? (
          <div className="rounded-lg bg-danger-50 p-4 text-sm font-semibold text-danger-700">Could not load this inspection report.</div>
        ) : null}

        {inspection ? (
          <>
            <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Inspection Report</p>
                  <h2 className="mt-2 text-xl font-bold text-neutral-900">{inspection.branch_name || "All branches"}</h2>
                  <p className="mt-2 text-sm leading-6 text-neutral-600">
                    Submitted {formatDate(inspection.submitted_at || inspection.inspection_date)} by {inspection.inspector_name || "Inspector"}.
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <StatusBadge status={inspection.status} />
                  <span className="rounded bg-neutral-100 px-2 py-1 text-xs font-bold capitalize text-neutral-700">
                    {label(inspection.enforcement_action)}
                  </span>
                </div>
              </div>
              <div className="mt-5 grid gap-4 sm:grid-cols-3">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Compliance Score</p>
                  <p className="mt-1 text-lg font-bold text-brand-700">{inspection.compliance_score ? `${Number(inspection.compliance_score).toFixed(0)}%` : "Not scored"}</p>
                </div>
                <div>
                  <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Inspection Date</p>
                  <p className="mt-1 text-sm font-semibold text-neutral-800">{formatDate(inspection.inspection_date)}</p>
                </div>
                <div>
                  <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Responses</p>
                  <p className="mt-1 text-sm font-semibold text-neutral-800">{inspection.responses.length}</p>
                </div>
              </div>
              {inspection.gps_latitude && inspection.gps_longitude ? (
                <p className="mt-5 flex items-center gap-2 text-sm font-semibold text-neutral-600">
                  <MapPin size={16} />
                  {inspection.gps_latitude}, {inspection.gps_longitude}
                </p>
              ) : null}
            </section>

            <section className="grid gap-6 lg:grid-cols-[1fr_0.85fr]">
              <div className="grid gap-6">
                <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                  <div className="mb-4 flex items-center gap-2">
                    <ClipboardList className="text-brand-700" size={18} />
                    <h2 className="text-base font-bold text-neutral-900">Checklist</h2>
                  </div>
                  <div className="grid gap-3">
                    {checklist.map(([key, value]) => (
                      <div className="flex items-center justify-between gap-4 rounded border border-neutral-100 bg-neutral-50 px-3 py-2" key={key}>
                        <span className="text-sm font-semibold capitalize text-neutral-700">{key.replaceAll("_", " ")}</span>
                        <span className="text-sm font-bold text-neutral-900">{checklistValue(value)}</span>
                      </div>
                    ))}
                    {!checklist.length ? <p className="text-sm text-neutral-500">No checklist responses were recorded.</p> : null}
                  </div>
                </div>

                <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                  <h2 className="text-base font-bold text-neutral-900">Findings & Notice</h2>
                  <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-neutral-700">{inspection.findings || "No findings recorded."}</p>
                </div>

                <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                  <div className="mb-4 flex items-center gap-2">
                    <FileImage className="text-brand-700" size={18} />
                    <h2 className="text-base font-bold text-neutral-900">Evidence</h2>
                  </div>
                  <div className="grid gap-3">
                    {inspection.evidence_files.map((file, index) => {
                      const url = typeof file.file_url === "string" ? file.file_url : "";
                      const description = typeof file.description === "string" ? file.description : `Evidence ${index + 1}`;
                      return (
                        <div className="rounded border border-neutral-100 bg-neutral-50 p-3" key={`${url}-${index}`}>
                          <p className="text-sm font-semibold text-neutral-800">{description}</p>
                          {url ? (
                            <a className="mt-1 inline-block text-sm font-bold text-brand-700 hover:text-brand-600" href={url} rel="noreferrer" target="_blank">
                              Open evidence
                            </a>
                          ) : null}
                        </div>
                      );
                    })}
                    {!inspection.evidence_files.length ? <p className="text-sm text-neutral-500">No evidence files were attached.</p> : null}
                  </div>
                </div>
              </div>

              <div className="grid h-fit gap-6">
                <InspectionResponseForm disabled={mutation.isPending} onSubmit={async (payload) => { await mutation.mutateAsync(payload); }} />
                {mutation.isError ? <p className="text-sm font-semibold text-danger-500">Could not submit response. Please review the fields and try again.</p> : null}

                <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                  <div className="mb-4 flex items-center gap-2">
                    <MessageSquareText className="text-brand-700" size={18} />
                    <h2 className="text-base font-bold text-neutral-900">Response History</h2>
                  </div>
                  <div className="grid gap-3">
                    {inspection.responses.map((response) => (
                      <div className="rounded border border-neutral-100 bg-neutral-50 p-3" key={response.id}>
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-sm font-bold capitalize text-neutral-900">{label(response.response_type)}</p>
                          <span className="text-xs font-semibold text-neutral-500">{formatDate(response.submitted_at)}</span>
                        </div>
                        <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-neutral-700">{response.content || "No note provided."}</p>
                        {response.evidence_file_url ? (
                          <a className="mt-2 inline-block text-sm font-bold text-brand-700 hover:text-brand-600" href={response.evidence_file_url} rel="noreferrer" target="_blank">
                            Open submitted evidence
                          </a>
                        ) : null}
                        <p className="mt-2 text-xs text-neutral-500">{response.submitted_by_name || "Employer user"}</p>
                      </div>
                    ))}
                    {!inspection.responses.length ? <p className="text-sm text-neutral-500">No employer responses have been submitted yet.</p> : null}
                  </div>
                </div>
              </div>
            </section>
          </>
        ) : (
          <div className="rounded-lg border border-neutral-200 bg-white p-5 text-sm font-semibold text-neutral-500 shadow-sm">Loading inspection report...</div>
        )}
      </div>
    </PortalShell>
  );
}
