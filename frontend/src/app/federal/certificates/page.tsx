"use client";

import { useQuery } from "@tanstack/react-query";
import { Download, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchFederalCertificates, type FederalCertificateRegistryItem } from "@/lib/api/federal";
import { downloadCsv } from "@/lib/export/csv";

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const certificatesQuery = useQuery({
    queryKey: ["federal-certificates", search, status],
    queryFn: () => fetchFederalCertificates({ search, status }),
  });
  const rows = certificatesQuery.data || [];

  return (
    <PortalShell role="federal_admin" title="Certificate registry" description="Search national certificate issuance and trust status without exposing private identity or medical details.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[1fr_220px_auto]">
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search certificate, handler, employer, or facility" />
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
              <option value="">All statuses</option>
              <option value="active">Active</option>
              <option value="expired">Expired</option>
              <option value="suspended">Suspended</option>
              <option value="revoked">Revoked</option>
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
            ]}
            rows={rows}
            empty={certificatesQuery.isLoading ? "Loading certificates..." : "No certificates match the current filters."}
          />
        </section>
      </div>
    </PortalShell>
  );
}
