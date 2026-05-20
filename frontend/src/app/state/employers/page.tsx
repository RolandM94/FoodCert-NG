"use client";

import { useQuery } from "@tanstack/react-query";
import { Building2, Download } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchStateEmployers, type StateEmployerMonitoringItem } from "@/lib/api/state";
import { downloadCsv } from "@/lib/export/csv";

export default function Page() {
  const [search, setSearch] = useState("");
  const [complianceStatus, setComplianceStatus] = useState("");
  const employersQuery = useQuery({
    queryKey: ["state-employers-monitoring", search, complianceStatus],
    queryFn: () => fetchStateEmployers({ search, compliance_status: complianceStatus }),
  });
  const rows = employersQuery.data || [];

  return (
    <PortalShell role="state_admin" title="Employers" description="Review registered food businesses and compliance status.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[1fr_220px_auto]">
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search business name or registration number" />
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={complianceStatus} onChange={(event) => setComplianceStatus(event.target.value)}>
              <option value="">All compliance statuses</option>
              <option value="compliant">Compliant</option>
              <option value="non_compliant">Non compliant</option>
              <option value="under_review">Under review</option>
            </select>
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-deep px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300"
              disabled={!rows.length}
              onClick={() =>
                downloadCsv("state-employers-monitoring.csv", rows, [
                  { header: "Business", value: (row) => row.business_name },
                  { header: "Registration number", value: (row) => row.business_registration_number },
                  { header: "Category", value: (row) => row.establishment_category },
                  { header: "LGA", value: (row) => row.lga_name },
                  { header: "Compliance", value: (row) => row.compliance_status },
                  { header: "Subscription", value: (row) => row.subscription_status },
                  { header: "Handlers", value: (row) => row.food_handler_count },
                  { header: "Active certificates", value: (row) => row.active_certificate_count },
                  { header: "Active illness exclusions", value: (row) => row.active_illness_exclusion_count },
                ])
              }
              type="button"
            >
              <Download size={16} />
              Export
            </button>
          </div>
        </section>
        <section className="grid gap-3">
          <div className="flex items-center gap-2"><Building2 className="text-brand-deep" size={18} /><h2 className="text-base font-bold text-slate-950">Food Business Monitoring</h2></div>
          <DataTable<StateEmployerMonitoringItem>
            columns={[
              { key: "business", header: "Business", render: (row) => <div><p className="font-bold text-slate-950">{row.business_name}</p><p className="text-xs text-slate-500">{row.establishment_category.replaceAll("_", " ")}</p></div> },
              { key: "lga", header: "LGA", render: (row) => row.lga_name || "Not set" },
              { key: "handlers", header: "Handlers", render: (row) => row.food_handler_count },
              { key: "certs", header: "Active certs", render: (row) => row.active_certificate_count },
              { key: "illness", header: "Active illness", render: (row) => row.active_illness_exclusion_count },
              { key: "status", header: "Compliance", render: (row) => <StatusCell status={row.compliance_status} /> },
            ]}
            rows={rows}
            empty={employersQuery.isLoading ? "Loading employers..." : "No employers match the current filters."}
          />
        </section>
      </div>
    </PortalShell>
  );
}
