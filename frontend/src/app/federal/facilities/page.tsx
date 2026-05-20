"use client";

import { useQuery } from "@tanstack/react-query";
import { Building2, Download } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchFederalFacilities, type FederalFacilityRegistryItem } from "@/lib/api/federal";
import { downloadCsv } from "@/lib/export/csv";

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const facilitiesQuery = useQuery({
    queryKey: ["federal-facilities", search, status],
    queryFn: () => fetchFederalFacilities({ search, status }),
  });
  const rows = facilitiesQuery.data || [];

  return (
    <PortalShell role="federal_admin" title="Facilities" description="Review national facility accreditation coverage and assessment readiness.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[1fr_220px_auto]">
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search facility or license number" />
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
              <option value="">All statuses</option>
              <option value="approved">Approved</option>
              <option value="submitted">Submitted</option>
              <option value="under_review">Under review</option>
              <option value="suspended">Suspended</option>
              <option value="expired">Expired</option>
            </select>
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-deep px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300"
              disabled={!rows.length}
              onClick={() => downloadCsv("federal-facilities.csv", rows, [
                { header: "Facility", value: (row) => row.facility_name },
                { header: "State", value: (row) => row.state_name },
                { header: "LGA", value: (row) => row.lga_name },
                { header: "Type", value: (row) => row.facility_type },
                { header: "License", value: (row) => row.license_number },
                { header: "Status", value: (row) => row.accreditation_status },
                { header: "Expiry", value: (row) => row.accreditation_expiry_date },
              ])}
              type="button"
            >
              <Download size={16} />
              Export
            </button>
          </div>
        </section>

        <section className="grid gap-3">
          <div className="flex items-center gap-2"><Building2 className="text-brand-deep" size={18} /><h2 className="text-base font-bold text-slate-950">National Facility Registry</h2></div>
          <DataTable<FederalFacilityRegistryItem>
            columns={[
              { key: "facility", header: "Facility", render: (row) => <div><p className="font-bold text-slate-950">{row.facility_name}</p><p className="text-xs text-slate-500">{row.license_number}</p></div> },
              { key: "state", header: "State", render: (row) => row.state_name || "Not set" },
              { key: "type", header: "Type", render: (row) => row.facility_type.replaceAll("_", " ") },
              { key: "ready", header: "Ready", render: (row) => row.can_conduct_assessments ? "Yes" : "No" },
              { key: "expiry", header: "Expiry", render: (row) => dateLabel(row.accreditation_expiry_date) },
              { key: "status", header: "Status", render: (row) => <StatusCell status={row.accreditation_status} /> },
            ]}
            rows={rows}
            empty={facilitiesQuery.isLoading ? "Loading facilities..." : "No facilities match the current filters."}
          />
        </section>
      </div>
    </PortalShell>
  );
}
