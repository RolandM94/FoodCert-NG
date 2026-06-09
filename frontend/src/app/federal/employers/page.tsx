"use client";

import { useQuery } from "@tanstack/react-query";
import { BriefcaseBusiness, Download } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchFederalEmployers, type FederalEmployerRegistryItem } from "@/lib/api/federal";
import { downloadCsv } from "@/lib/export/csv";

export default function Page() {
  const [search, setSearch] = useState("");
  const [complianceStatus, setComplianceStatus] = useState("");
  const employersQuery = useQuery({
    queryKey: ["federal-employers", search, complianceStatus],
    queryFn: () => fetchFederalEmployers({ search, compliance_status: complianceStatus }),
  });
  const rows = employersQuery.data || [];

  return (
    <PortalShell role="federal_admin" title="Employers" description="Review national food business registration and compliance coverage.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[1fr_220px_auto]">
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search business or registration number" />
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={complianceStatus} onChange={(event) => setComplianceStatus(event.target.value)}>
              <option value="">All compliance statuses</option>
              <option value="compliant">Compliant</option>
              <option value="non_compliant">Non compliant</option>
              <option value="under_review">Under review</option>
            </select>
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-700 px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-neutral-300"
              disabled={!rows.length}
              onClick={() => downloadCsv("federal-employers.csv", rows, [
                { header: "Business", value: (row) => row.business_name },
                { header: "Registration", value: (row) => row.business_registration_number },
                { header: "State", value: (row) => row.state_name },
                { header: "LGA", value: (row) => row.lga_name },
                { header: "Category", value: (row) => row.establishment_category },
                { header: "Compliance", value: (row) => row.compliance_status },
                { header: "Handlers", value: (row) => row.food_handler_count },
              ])}
              type="button"
            >
              <Download size={16} />
              Export
            </button>
          </div>
        </section>

        <section className="grid gap-3">
          <div className="flex items-center gap-2"><BriefcaseBusiness className="text-brand-700" size={18} /><h2 className="text-base font-bold text-neutral-900">National Employer Registry</h2></div>
          <DataTable<FederalEmployerRegistryItem>
            columns={[
              { key: "business", header: "Business", render: (row) => <div><p className="font-bold text-neutral-900">{row.business_name}</p><p className="text-xs text-neutral-500">{row.establishment_category.replaceAll("_", " ")}</p></div> },
              { key: "state", header: "State", render: (row) => row.state_name || "Not set" },
              { key: "lga", header: "LGA", render: (row) => row.lga_name || "Not set" },
              { key: "handlers", header: "Handlers", render: (row) => row.food_handler_count },
              { key: "subscription", header: "Subscription", render: (row) => <StatusCell status={row.subscription_status} /> },
              { key: "compliance", header: "Compliance", render: (row) => <StatusCell status={row.compliance_status} /> },
            ]}
            rows={rows}
            empty={employersQuery.isLoading ? "Loading employers..." : "No employers match the current filters."}
          />
        </section>
      </div>
    </PortalShell>
  );
}
