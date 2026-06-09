"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BadgeCheck, Download } from "lucide-react";
import { useState } from "react";
import { CertificateAuditTimeline, CertificateLifecycleModal, CertificateRegistryTable } from "@/components/certificates/certificate-widgets";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusCell } from "@/components/ui/data-table";
import { downloadCertificatePdf } from "@/lib/api/certificates";
import {
  fetchStateCertificates,
  downloadStateCertificateExport,
  fetchStateCertificateAudit,
  reinstateStateCertificate,
  replaceStateCertificate,
  revokeStateCertificate,
  suspendStateCertificate,
  type StateCertificateRegistryItem,
} from "@/lib/api/state";

const STATUS_OPTIONS = [
  ["", "All statuses"],
  ["active", "Active"],
  ["expired", "Expired"],
  ["suspended", "Suspended"],
  ["revoked", "Revoked"],
  ["replaced", "Replaced"],
];

const EXPIRY_OPTIONS = [
  ["", "Any expiry"],
  ["7", "Expiring in 7 days"],
  ["30", "Expiring in 30 days"],
  ["60", "Expiring in 60 days"],
  ["expired", "Expired"],
];

type ActionName = "suspend" | "reinstate" | "revoke" | "replace";

function dateLabel(value?: string) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

function canManage(row: StateCertificateRegistryItem) {
  return ["active", "suspended"].includes(row.status);
}

export default function Page() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [expiryWindow, setExpiryWindow] = useState("");
  const [actionTarget, setActionTarget] = useState<{ certificate: StateCertificateRegistryItem; action: ActionName } | null>(null);
  const [auditTarget, setAuditTarget] = useState<StateCertificateRegistryItem | null>(null);
  const [reason, setReason] = useState("");
  const [exporting, setExporting] = useState(false);

  const certificatesQuery = useQuery({
    queryKey: ["state-certificates", search, status, expiryWindow],
    queryFn: () => fetchStateCertificates({
      search: search || undefined,
      status: status || undefined,
      expiry_window: expiryWindow || undefined,
    }),
  });

  const lifecycleMutation = useMutation({
    mutationFn: ({ certificate, action, lifecycleReason }: { certificate: StateCertificateRegistryItem; action: ActionName; lifecycleReason: string }) =>
      action === "suspend" ? suspendStateCertificate(certificate.id, lifecycleReason)
        : action === "reinstate" ? reinstateStateCertificate(certificate.id, lifecycleReason)
          : action === "replace" ? replaceStateCertificate(certificate.id, lifecycleReason)
            : revokeStateCertificate(certificate.id, lifecycleReason),
    onSuccess: () => {
      setActionTarget(null);
      setReason("");
      queryClient.invalidateQueries({ queryKey: ["state-certificates"] });
    },
  });

  const auditQuery = useQuery({
    queryKey: ["state-certificate-audit", auditTarget?.id],
    queryFn: () => fetchStateCertificateAudit(auditTarget!.id),
    enabled: !!auditTarget,
  });

  const certificates = certificatesQuery.data || [];

  return (
    <PortalShell role="state_admin" title="Certificates" description="Search and manage issued, revoked, suspended, and expired certificates.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[1fr_220px_220px]">
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              Search
              <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm normal-case tracking-normal text-neutral-700" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Certificate, handler, employer, facility" />
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              Status
              <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm normal-case tracking-normal text-neutral-700" value={status} onChange={(event) => setStatus(event.target.value)}>
                {STATUS_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              Expiry
              <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm normal-case tracking-normal text-neutral-700" value={expiryWindow} onChange={(event) => setExpiryWindow(event.target.value)}>
                {EXPIRY_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
          </div>
          <button
            className="mt-3 inline-flex h-10 items-center gap-2 rounded border border-neutral-200 bg-white px-3 text-sm font-bold text-neutral-700 hover:bg-neutral-50 disabled:opacity-50"
            disabled={exporting}
            onClick={async () => {
              setExporting(true);
              try {
                await downloadStateCertificateExport();
              } finally {
                setExporting(false);
              }
            }}
            type="button"
          >
            <Download size={16} />
            Export registry
          </button>
        </section>

        <section className="grid gap-3">
          <div className="flex items-center gap-2">
            <BadgeCheck className="text-brand-700" size={18} />
            <h2 className="text-base font-bold text-neutral-900">Certificate Registry</h2>
          </div>
          {certificatesQuery.isError ? <p className="rounded bg-danger-50 p-3 text-sm font-semibold text-danger-700">Could not load certificates.</p> : null}
          <CertificateRegistryTable<StateCertificateRegistryItem>
            columns={[
              { key: "certificate", header: "Certificate", render: (row) => <div><p className="font-bold text-neutral-900">{row.certificate_number}</p><p className="text-xs text-neutral-500">{row.issuing_state_name}</p></div> },
              { key: "handler", header: "Food handler", render: (row) => <div><p className="font-semibold text-neutral-800">{row.food_handler_name || "Unknown"}</p><p className="text-xs text-neutral-500">{row.food_handler_category?.replaceAll("_", " ") || "No category"}</p></div> },
              { key: "employer", header: "Employer", render: (row) => row.employer_name || "Not linked" },
              { key: "facility", header: "Facility", render: (row) => row.facility_name || "Unknown" },
              { key: "expiry", header: "Issue / Expiry", render: (row) => `${dateLabel(row.issue_date)} - ${dateLabel(row.expiry_date)}` },
              { key: "status", header: "Status", render: (row) => <StatusCell status={row.effective_status || row.status} /> },
              {
                key: "actions",
                header: "Actions",
                render: (row) => (
                  <div className="flex flex-wrap gap-2">
                    <button className="inline-flex h-8 items-center gap-1 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700 hover:bg-neutral-50" onClick={() => void downloadCertificatePdf(row.id, row.certificate_number)} type="button"><Download size={13} /> PDF</button>
                    {canManage(row) && row.status === "active" ? <button className="h-8 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700 hover:bg-neutral-50" onClick={() => setActionTarget({ certificate: row, action: "suspend" })} type="button">Suspend</button> : null}
                    {canManage(row) && row.status === "suspended" ? <button className="h-8 rounded border border-brand-200 px-3 text-xs font-bold text-brand-700 hover:bg-brand-50" onClick={() => setActionTarget({ certificate: row, action: "reinstate" })} type="button">Reinstate</button> : null}
                    {canManage(row) && row.status !== "revoked" ? <button className="h-8 rounded border border-warning-100 px-3 text-xs font-bold text-warning-700 hover:bg-warning-50" onClick={() => setActionTarget({ certificate: row, action: "replace" })} type="button">Replace</button> : null}
                    {canManage(row) ? <button className="h-8 rounded border border-danger-100 px-3 text-xs font-bold text-danger-700 hover:bg-danger-50" onClick={() => setActionTarget({ certificate: row, action: "revoke" })} type="button">Revoke</button> : null}
                    <button className="h-8 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700 hover:bg-neutral-50" onClick={() => setAuditTarget(row)} type="button">Audit</button>
                  </div>
                ),
              },
            ]}
            rows={certificates}
            empty={certificatesQuery.isLoading ? "Loading certificates..." : "No certificates match the current filters."}
          />
        </section>
      </div>

      {actionTarget ? (
        <CertificateLifecycleModal
          certificateNumber={actionTarget.certificate.certificate_number}
          isError={lifecycleMutation.isError}
          isPending={lifecycleMutation.isPending}
          onCancel={() => setActionTarget(null)}
          onSubmit={() => lifecycleMutation.mutate({ certificate: actionTarget.certificate, action: actionTarget.action, lifecycleReason: reason })}
          reason={reason}
          setReason={setReason}
          title={`${actionTarget.action} certificate`}
        />
      ) : null}

      {auditTarget ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-neutral-900/50 p-4">
          <div className="w-full max-w-2xl rounded-lg border border-neutral-200 bg-white shadow-xl">
            <div className="border-b border-neutral-100 px-6 py-4">
              <h2 className="text-lg font-bold text-neutral-900">Certificate audit</h2>
              <p className="mt-1 text-sm text-neutral-500">{auditTarget.certificate_number}</p>
            </div>
            <div className="max-h-[60vh] overflow-auto p-6">
              {!auditQuery.isLoading ? <CertificateAuditTimeline items={auditQuery.data || []} /> : null}
              {auditQuery.isLoading ? <p className="text-sm text-neutral-500">Loading audit events...</p> : null}
            </div>
            <div className="border-t border-neutral-100 px-6 py-4 text-right">
              <button className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-600 hover:bg-neutral-50" onClick={() => setAuditTarget(null)} type="button">Close</button>
            </div>
          </div>
        </div>
      ) : null}
    </PortalShell>
  );
}
