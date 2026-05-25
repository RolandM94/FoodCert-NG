"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Download, Eye, Flag, ShieldAlert, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchFederalCertificateAnalytics, fetchFederalCertificates, flagFederalCertificate, type FederalCertificateRegistryItem } from "@/lib/api/federal";
import { downloadCsv } from "@/lib/export/csv";

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [flagged, setFlagged] = useState("");
  const [flagTarget, setFlagTarget] = useState<FederalCertificateRegistryItem | null>(null);
  const [flagReason, setFlagReason] = useState("");
  const [flagDetails, setFlagDetails] = useState("");
  const queryClient = useQueryClient();
  const certificatesQuery = useQuery({
    queryKey: ["federal-certificates", search, status, flagged],
    queryFn: () => fetchFederalCertificates({ search, status, flagged }),
  });
  const analyticsQuery = useQuery({
    queryKey: ["federal-certificate-analytics"],
    queryFn: fetchFederalCertificateAnalytics,
  });
  const flagMutation = useMutation({
    mutationFn: ({ id, reason, details }: { id: string; reason: string; details: string }) => flagFederalCertificate(id, reason, details),
    onSuccess: () => {
      setFlagTarget(null);
      setFlagReason("");
      setFlagDetails("");
      queryClient.invalidateQueries({ queryKey: ["federal-certificates"] });
      queryClient.invalidateQueries({ queryKey: ["federal-certificate-analytics"] });
    },
  });
  const rows = certificatesQuery.data || [];
  const cards = analyticsQuery.data?.cards;

  return (
    <PortalShell role="federal_admin" title="Certificate registry" description="Search national certificate issuance and trust status without exposing private identity or medical details.">
      <div className="grid gap-5">
        {cards ? (
          <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-7">
            {[
              ["Total", cards.total],
              ["Active", cards.active],
              ["Expired", cards.expired],
              ["Expiring 30d", cards.expiring_30_days],
              ["Suspended", cards.suspended],
              ["Revoked", cards.revoked],
              ["Flagged", cards.flagged],
              ["Invalid attempts", cards.invalid_verification_attempts],
            ].map(([label, value]) => (
              <div key={label} className="rounded-lg border border-slate-200 bg-white p-3 text-center shadow-sm">
                <ShieldAlert className="mx-auto mb-1 text-slate-400" size={16} />
                <p className="text-xl font-bold text-slate-950">{value}</p>
                <p className="text-xs font-semibold text-slate-500">{label}</p>
              </div>
            ))}
          </section>
        ) : null}
        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[1fr_180px_180px_auto]">
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search certificate, handler, employer, or facility" />
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
              <option value="">All statuses</option>
              <option value="active">Active</option>
              <option value="expired">Expired</option>
              <option value="suspended">Suspended</option>
              <option value="revoked">Revoked</option>
            </select>
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={flagged} onChange={(event) => setFlagged(event.target.value)}>
              <option value="">All trust states</option>
              <option value="true">Flagged only</option>
            </select>
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-deep px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300"
              disabled={!rows.length}
              onClick={() => downloadCsv("federal-certificates.csv", rows, [
                { header: "Certificate", value: (row) => row.certificate_number },
                { header: "Handler", value: (row) => row.food_handler_name },
                { header: "Employer", value: (row) => row.employer_name },
                { header: "Facility", value: (row) => row.facility_name },
                { header: "State", value: (row) => row.issuing_state_name },
                { header: "Issue date", value: (row) => row.issue_date },
                { header: "Expiry date", value: (row) => row.expiry_date },
                { header: "Status", value: (row) => row.effective_status },
                { header: "Suspicious reports", value: (row) => row.suspicious_report_count },
              ])}
              type="button"
            >
              <Download size={16} />
              Export
            </button>
          </div>
        </section>

        <section className="grid gap-3">
          <div className="flex items-center gap-2"><ShieldCheck className="text-brand-deep" size={18} /><h2 className="text-base font-bold text-slate-950">National Certificate Trust Registry</h2></div>
          <DataTable<FederalCertificateRegistryItem>
            columns={[
              { key: "cert", header: "Certificate", render: (row) => <div><p className="font-bold text-slate-950">{row.certificate_number}</p><p className="text-xs text-slate-500">{row.food_handler_name}</p></div> },
              { key: "state", header: "State", render: (row) => row.issuing_state_name || "Not set" },
              { key: "employer", header: "Employer", render: (row) => row.employer_name || "Not linked" },
              { key: "facility", header: "Facility", render: (row) => row.facility_name || "Not set" },
              { key: "expiry", header: "Expiry", render: (row) => dateLabel(row.expiry_date) },
              { key: "status", header: "Status", render: (row) => <StatusCell status={row.effective_status} /> },
              { key: "flags", header: "Flags", render: (row) => row.suspicious_report_count ? <span className="font-bold text-amber-700">{row.suspicious_report_count}</span> : "None" },
              { key: "actions", header: "Actions", render: (row) => (
                <div className="flex flex-wrap gap-2">
                  <Link className="inline-flex h-8 items-center gap-1 rounded border border-slate-200 px-2 text-xs font-bold text-slate-700 hover:bg-slate-50" href={`/federal/certificates/${row.id}`}><Eye size={13} /> View</Link>
                  <button className="inline-flex h-8 items-center gap-1 rounded border border-amber-200 px-2 text-xs font-bold text-amber-800 hover:bg-amber-50" onClick={() => setFlagTarget(row)} type="button"><Flag size={13} /> Flag</button>
                </div>
              ) },
            ]}
            rows={rows}
            empty={certificatesQuery.isLoading ? "Loading certificates..." : "No certificates match the current filters."}
          />
        </section>
      </div>

      {flagTarget ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
          <div className="w-full max-w-md rounded-lg border border-slate-200 bg-white shadow-xl">
            <div className="border-b border-slate-100 px-6 py-4">
              <h2 className="text-lg font-bold text-slate-950">Flag certificate</h2>
              <p className="mt-1 text-sm text-slate-500">{flagTarget.certificate_number}</p>
            </div>
            <form
              className="grid gap-4 p-6"
              onSubmit={(event) => {
                event.preventDefault();
                flagMutation.mutate({ id: flagTarget.id, reason: flagReason, details: flagDetails });
              }}
            >
              <label className="grid gap-1 text-sm font-semibold text-slate-700">
                Reason
                <textarea className="rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm" required rows={3} value={flagReason} onChange={(event) => setFlagReason(event.target.value)} />
              </label>
              <label className="grid gap-1 text-sm font-semibold text-slate-700">
                Context
                <textarea className="rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm" rows={3} value={flagDetails} onChange={(event) => setFlagDetails(event.target.value)} />
              </label>
              {flagMutation.isError ? <p className="rounded bg-red-50 px-3 py-2 text-sm font-semibold text-red-700">Could not flag this certificate.</p> : null}
              <div className="flex justify-end gap-3">
                <button className="h-10 rounded border border-slate-200 px-4 text-sm font-semibold text-slate-600 hover:bg-slate-50" onClick={() => setFlagTarget(null)} type="button">Cancel</button>
                <button className="h-10 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep disabled:opacity-60" disabled={flagMutation.isPending} type="submit">Flag</button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </PortalShell>
  );
}
