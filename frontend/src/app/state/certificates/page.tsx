"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BadgeCheck } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import {
  fetchStateCertificates,
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

type ActionName = "suspend" | "revoke";

function dateLabel(value?: string) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

function canManage(row: StateCertificateRegistryItem) {
  return row.status === "active";
}

export default function Page() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [expiryWindow, setExpiryWindow] = useState("");
  const [actionTarget, setActionTarget] = useState<{ certificate: StateCertificateRegistryItem; action: ActionName } | null>(null);
  const [reason, setReason] = useState("");

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
      action === "suspend" ? suspendStateCertificate(certificate.id, lifecycleReason) : revokeStateCertificate(certificate.id, lifecycleReason),
    onSuccess: () => {
      setActionTarget(null);
      setReason("");
      queryClient.invalidateQueries({ queryKey: ["state-certificates"] });
    },
  });

  const certificates = certificatesQuery.data || [];

  return (
    <PortalShell role="state_admin" title="Certificates" description="Search and manage issued, revoked, suspended, and expired certificates.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[1fr_220px_220px]">
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-slate-500">
              Search
              <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm normal-case tracking-normal text-slate-700" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Certificate, handler, employer, facility" />
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-slate-500">
              Status
              <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm normal-case tracking-normal text-slate-700" value={status} onChange={(event) => setStatus(event.target.value)}>
                {STATUS_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-slate-500">
              Expiry
              <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm normal-case tracking-normal text-slate-700" value={expiryWindow} onChange={(event) => setExpiryWindow(event.target.value)}>
                {EXPIRY_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
          </div>
        </section>

        <section className="grid gap-3">
          <div className="flex items-center gap-2">
            <BadgeCheck className="text-brand-deep" size={18} />
            <h2 className="text-base font-bold text-slate-950">Certificate Registry</h2>
          </div>
          {certificatesQuery.isError ? <p className="rounded bg-rose-50 p-3 text-sm font-semibold text-rose-700">Could not load certificates.</p> : null}
          <DataTable<StateCertificateRegistryItem>
            columns={[
              { key: "certificate", header: "Certificate", render: (row) => <div><p className="font-bold text-slate-950">{row.certificate_number}</p><p className="text-xs text-slate-500">{row.issuing_state_name}</p></div> },
              { key: "handler", header: "Food handler", render: (row) => <div><p className="font-semibold text-slate-800">{row.food_handler_name || "Unknown"}</p><p className="text-xs text-slate-500">{row.food_handler_category?.replaceAll("_", " ") || "No category"}</p></div> },
              { key: "employer", header: "Employer", render: (row) => row.employer_name || "Not linked" },
              { key: "facility", header: "Facility", render: (row) => row.facility_name || "Unknown" },
              { key: "expiry", header: "Issue / Expiry", render: (row) => `${dateLabel(row.issue_date)} - ${dateLabel(row.expiry_date)}` },
              { key: "status", header: "Status", render: (row) => <StatusCell status={row.effective_status || row.status} /> },
              {
                key: "actions",
                header: "Actions",
                render: (row) => canManage(row) ? (
                  <div className="flex flex-wrap gap-2">
                    <button className="h-8 rounded border border-slate-200 px-3 text-xs font-bold text-slate-700 hover:bg-slate-50" onClick={() => setActionTarget({ certificate: row, action: "suspend" })} type="button">Suspend</button>
                    <button className="h-8 rounded border border-red-200 px-3 text-xs font-bold text-red-700 hover:bg-red-50" onClick={() => setActionTarget({ certificate: row, action: "revoke" })} type="button">Revoke</button>
                  </div>
                ) : <span className="text-xs font-semibold text-slate-400">No action</span>,
              },
            ]}
            rows={certificates}
            empty={certificatesQuery.isLoading ? "Loading certificates..." : "No certificates match the current filters."}
          />
        </section>
      </div>

      {actionTarget ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
          <div className="w-full max-w-md rounded-lg border border-slate-200 bg-white shadow-xl">
            <div className="border-b border-slate-100 px-6 py-4">
              <h2 className="text-lg font-bold capitalize text-slate-950">{actionTarget.action} certificate</h2>
              <p className="mt-1 text-sm text-slate-500">{actionTarget.certificate.certificate_number}</p>
            </div>
            <form
              className="grid gap-4 p-6"
              onSubmit={(event) => {
                event.preventDefault();
                lifecycleMutation.mutate({ certificate: actionTarget.certificate, action: actionTarget.action, lifecycleReason: reason });
              }}
            >
              <label className="grid gap-1 text-sm font-semibold text-slate-700">
                Reason <span className="text-red-500">*</span>
                <textarea className="rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm" required rows={3} value={reason} onChange={(event) => setReason(event.target.value)} />
              </label>
              {lifecycleMutation.isError ? <p className="rounded bg-red-50 px-3 py-2 text-sm font-semibold text-red-700">Could not complete this certificate action.</p> : null}
              <div className="flex justify-end gap-3">
                <button className="h-10 rounded border border-slate-200 px-4 text-sm font-semibold text-slate-600 hover:bg-slate-50" onClick={() => setActionTarget(null)} type="button">Cancel</button>
                <button className="h-10 rounded bg-brand-green px-4 text-sm font-bold capitalize text-white hover:bg-brand-deep disabled:opacity-60" disabled={lifecycleMutation.isPending} type="submit">{actionTarget.action}</button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </PortalShell>
  );
}
