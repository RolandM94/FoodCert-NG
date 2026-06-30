"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BadgeCheck, Download, FileCheck2 } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { downloadAccreditationCertificatePdf, downloadCertificatePdf } from "@/lib/api/certificates";
import {
  approveStateCertificateValidationRequest,
  approveStateFacilityApplication,
  fetchStateUnifiedCertificateRegistry,
  rejectStateCertificateValidationRequest,
  rejectStateFacilityApplication,
  requestStateCertificateValidationClarification,
  type UnifiedCertificateRegistryItem,
  type UnifiedCertificateRegistryTab,
} from "@/lib/api/state";

const TABS: Array<{ key: UnifiedCertificateRegistryTab; label: string }> = [
  { key: "pending_review", label: "Pending Review" },
  { key: "food_handler_certificates", label: "Food Handler Certificates" },
  { key: "employer_accreditation_certificates", label: "Employer Accreditation Certificates" },
  { key: "facility_accreditation_certificates", label: "Facility Accreditation Certificates" },
];

type PendingAction = "approve" | "reject" | "request-clarification";

function dateLabel(value?: string | null) {
  if (!value) return "Not issued";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

function recordLabel(recordType: string) {
  return recordType.replaceAll("_", " ");
}

function StateCertificatesPageContent() {
  const params = useSearchParams();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<UnifiedCertificateRegistryTab>((params.get("tab") as UnifiedCertificateRegistryTab) || "pending_review");
  const [search, setSearch] = useState("");
  const [actionTarget, setActionTarget] = useState<{ row: UnifiedCertificateRegistryItem; action: PendingAction } | null>(null);
  const [notes, setNotes] = useState("");

  const registryQuery = useQuery({
    queryKey: ["state-unified-certificate-registry", tab, search],
    queryFn: () => fetchStateUnifiedCertificateRegistry({ tab, search: search || undefined }),
  });

  const actionMutation = useMutation({
    mutationFn: async ({ row, action, reviewNotes }: { row: UnifiedCertificateRegistryItem; action: PendingAction; reviewNotes: string }) => {
      if (row.record_type === "food_handler_certificate_request") {
        if (action === "approve") return approveStateCertificateValidationRequest(row.source_id, reviewNotes);
        if (action === "reject") return rejectStateCertificateValidationRequest(row.source_id, reviewNotes);
        return requestStateCertificateValidationClarification(row.source_id, reviewNotes);
      }
      if (row.record_type === "facility_accreditation_application") {
        if (action === "approve") return approveStateFacilityApplication(row.source_id, reviewNotes);
        return rejectStateFacilityApplication(row.source_id, reviewNotes);
      }
      throw new Error("No workflow action is available for this record.");
    },
    onSuccess: () => {
      setActionTarget(null);
      setNotes("");
      queryClient.invalidateQueries({ queryKey: ["state-unified-certificate-registry"] });
    },
  });

  const rows = registryQuery.data || [];

  return (
    <PortalShell role="state_admin" title="Certificate Registry" description="Review pending certificate work and manage issued food handler, employer, and facility accreditation certificates.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div className="flex flex-wrap gap-2">
              {TABS.map((item) => (
                <button
                  className={`rounded px-3 py-2 text-sm font-bold ${tab === item.key ? "bg-brand-600 text-white" : "border border-neutral-200 text-neutral-700 hover:bg-neutral-50"}`}
                  key={item.key}
                  onClick={() => setTab(item.key)}
                  type="button"
                >
                  {item.label}
                </button>
              ))}
            </div>
            <input
              className="h-10 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm lg:w-80"
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search owner, certificate, status"
              value={search}
            />
          </div>
        </section>

        <section className="grid gap-3">
          <div className="flex items-center gap-2">
            {tab === "pending_review" ? <FileCheck2 className="text-brand-700" size={18} /> : <BadgeCheck className="text-brand-700" size={18} />}
            <h2 className="text-base font-bold text-neutral-900">{TABS.find((item) => item.key === tab)?.label}</h2>
          </div>
          {registryQuery.isError ? <p className="rounded bg-danger-50 p-3 text-sm font-semibold text-danger-700">Could not load certificate registry.</p> : null}
          <DataTable<UnifiedCertificateRegistryItem>
            columns={[
              { key: "owner", header: "Owner", render: (row) => <div><p className="font-bold text-neutral-900">{row.owner_name || "Unknown"}</p><p className="text-xs capitalize text-neutral-500">{row.owner_type.replaceAll("_", " ")}</p></div> },
              { key: "record", header: "Record", render: (row) => <span className="capitalize">{recordLabel(row.record_type)}</span> },
              { key: "certificate", header: "Certificate", render: (row) => row.certificate_number || "Not issued" },
              { key: "state", header: "State", render: (row) => row.issuing_state_name || "Not set" },
              { key: "dates", header: "Issue / Expiry", render: (row) => `${dateLabel(row.issue_date)} - ${dateLabel(row.expiry_date)}` },
              { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
              {
                key: "actions",
                header: "Actions",
                render: (row) => (
                  <div className="flex flex-wrap gap-2">
                    {tab === "pending_review" && ["food_handler_certificate_request", "facility_accreditation_application"].includes(row.record_type) ? (
                      <>
                        <button className="h-8 rounded border border-brand-200 px-3 text-xs font-bold text-brand-700" onClick={() => setActionTarget({ row, action: "approve" })} type="button">Approve</button>
                        <button className="h-8 rounded border border-danger-100 px-3 text-xs font-bold text-danger-700" onClick={() => setActionTarget({ row, action: "reject" })} type="button">Reject</button>
                        {row.record_type === "food_handler_certificate_request" ? (
                          <button className="h-8 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700" onClick={() => setActionTarget({ row, action: "request-clarification" })} type="button">Clarify</button>
                        ) : null}
                      </>
                    ) : null}
                    {tab !== "pending_review" && row.certificate_number ? (
                      <button
                        className="inline-flex h-8 items-center gap-1 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700 hover:bg-neutral-50"
                        onClick={() => {
                          if (row.record_type === "food_handler_certificate") {
                            void downloadCertificatePdf(row.source_id, row.certificate_number);
                          } else {
                            void downloadAccreditationCertificatePdf(row.source_id, row.certificate_number);
                          }
                        }}
                        type="button"
                      >
                        <Download size={13} /> PDF
                      </button>
                    ) : null}
                  </div>
                ),
              },
            ]}
            rows={rows}
            empty={registryQuery.isLoading ? "Loading certificate registry..." : "No records match this tab or search."}
          />
        </section>
      </div>

      {actionTarget ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-neutral-900/50 p-4">
          <div className="w-full max-w-md rounded-lg border border-neutral-200 bg-white shadow-xl">
            <div className="border-b border-neutral-100 px-6 py-4">
              <h2 className="text-lg font-bold capitalize text-neutral-900">{actionTarget.action.replace("-", " ")} review</h2>
              <p className="mt-1 text-sm text-neutral-500">{actionTarget.row.owner_name}</p>
            </div>
            <form
              className="grid gap-4 p-6"
              onSubmit={(event) => {
                event.preventDefault();
                actionMutation.mutate({ row: actionTarget.row, action: actionTarget.action, reviewNotes: notes });
              }}
            >
              <label className="grid gap-1 text-sm font-semibold text-neutral-700">
                Review notes
                <textarea className="rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm" rows={3} value={notes} onChange={(event) => setNotes(event.target.value)} />
              </label>
              {actionMutation.isError ? <p className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">Could not complete this action.</p> : null}
              <div className="flex justify-end gap-3">
                <button className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-600 hover:bg-neutral-50" onClick={() => setActionTarget(null)} type="button">Cancel</button>
                <button className="h-10 rounded bg-brand-600 px-4 text-sm font-bold capitalize text-white hover:bg-brand-700 disabled:opacity-60" disabled={actionMutation.isPending} type="submit">{actionTarget.action.replace("-", " ")}</button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </PortalShell>
  );
}

export default function Page() {
  return (
    <Suspense fallback={null}>
      <StateCertificatesPageContent />
    </Suspense>
  );
}
