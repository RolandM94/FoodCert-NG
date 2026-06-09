"use client";

import { useQuery } from "@tanstack/react-query";
import { Download, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchFederalUnifiedCertificateRegistry } from "@/lib/api/federal";
import type { UnifiedCertificateRegistryItem, UnifiedCertificateRegistryTab } from "@/lib/api/state";
import { downloadCsv } from "@/lib/export/csv";

const TABS: Array<{ key: UnifiedCertificateRegistryTab; label: string }> = [
  { key: "pending_review", label: "Pending Review" },
  { key: "food_handler_certificates", label: "Food Handler Certificates" },
  { key: "employer_accreditation_certificates", label: "Employer Accreditation Certificates" },
  { key: "facility_accreditation_certificates", label: "Facility Accreditation Certificates" },
  { key: "all", label: "All Records" },
];

function dateLabel(value?: string | null) {
  if (!value) return "Not issued";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const [tab, setTab] = useState<UnifiedCertificateRegistryTab>("food_handler_certificates");
  const [search, setSearch] = useState("");
  const registryQuery = useQuery({
    queryKey: ["federal-unified-certificate-registry", tab, search],
    queryFn: () => fetchFederalUnifiedCertificateRegistry({ tab, search: search || undefined }),
  });
  const rows = registryQuery.data || [];

  return (
    <PortalShell role="federal_admin" title="Certificate Registry" description="National read-only registry for food handler certificates and employer/facility accreditation certificates.">
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
            <div className="flex flex-col gap-2 sm:flex-row">
              <input
                className="h-10 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm lg:w-80"
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search owner, certificate, status"
                value={search}
              />
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-700 px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-neutral-300"
                disabled={!rows.length}
                onClick={() => downloadCsv("federal-unified-certificate-registry.csv", rows, [
                  { header: "Record type", value: (row) => row.record_type },
                  { header: "Owner type", value: (row) => row.owner_type },
                  { header: "Owner", value: (row) => row.owner_name },
                  { header: "Certificate", value: (row) => row.certificate_number },
                  { header: "State", value: (row) => row.issuing_state_name },
                  { header: "Issue date", value: (row) => row.issue_date || "" },
                  { header: "Expiry date", value: (row) => row.expiry_date || "" },
                  { header: "Status", value: (row) => row.status },
                ])}
                type="button"
              >
                <Download size={16} />
                Export
              </button>
            </div>
          </div>
        </section>

        <section className="grid gap-3">
          <div className="flex items-center gap-2"><ShieldCheck className="text-brand-700" size={18} /><h2 className="text-base font-bold text-neutral-900">National Certificate Registry</h2></div>
          <DataTable<UnifiedCertificateRegistryItem>
            columns={[
              { key: "owner", header: "Owner", render: (row) => <div><p className="font-bold text-neutral-900">{row.owner_name || "Unknown"}</p><p className="text-xs capitalize text-neutral-500">{row.owner_type.replaceAll("_", " ")}</p></div> },
              { key: "record", header: "Record", render: (row) => <span className="capitalize">{row.record_type.replaceAll("_", " ")}</span> },
              { key: "certificate", header: "Certificate", render: (row) => row.certificate_number || "Not issued" },
              { key: "state", header: "State", render: (row) => row.issuing_state_name || "Not set" },
              { key: "dates", header: "Issue / Expiry", render: (row) => `${dateLabel(row.issue_date)} - ${dateLabel(row.expiry_date)}` },
              { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
            ]}
            rows={rows}
            empty={registryQuery.isLoading ? "Loading certificate registry..." : "No registry records match this tab or search."}
          />
        </section>
      </div>
    </PortalShell>
  );
}
