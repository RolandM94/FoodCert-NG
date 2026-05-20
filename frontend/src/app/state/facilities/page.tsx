"use client";

import { useQuery } from "@tanstack/react-query";
import { Building2 } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchStateFacilities } from "@/lib/api/state";
import type { MedicalFacility } from "@/types/facilities";

const STATUS_OPTIONS = [
  ["", "All statuses"],
  ["submitted", "Submitted"],
  ["under_review", "Under review"],
  ["approved", "Approved"],
  ["rejected", "Rejected"],
  ["suspended", "Suspended"],
  ["expired", "Expired"],
  ["reaccreditation_due", "Re-accreditation due"],
];

const TYPE_OPTIONS = [
  ["", "All facility types"],
  ["hospital", "Hospital"],
  ["clinic", "Clinic"],
  ["diagnostic_centre", "Diagnostic centre"],
  ["primary_health_centre", "Primary health centre"],
  ["mobile_health_unit", "Mobile health unit"],
];

function dateLabel(value?: string) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const [status, setStatus] = useState("");
  const [facilityType, setFacilityType] = useState("");
  const [search, setSearch] = useState("");
  const facilitiesQuery = useQuery({
    queryKey: ["state-facilities", status, facilityType, search],
    queryFn: () => fetchStateFacilities({ status: status || undefined, facility_type: facilityType || undefined, search: search || undefined }),
  });
  const facilities = facilitiesQuery.data || [];

  return (
    <PortalShell role="state_admin" title="Facilities" description="Review medical facilities and accreditation status in your state.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[1fr_220px_220px_auto] md:items-end">
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-slate-500">
              Search
              <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm normal-case tracking-normal text-slate-700" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Facility name" />
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-slate-500">
              Status
              <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm normal-case tracking-normal text-slate-700" value={status} onChange={(event) => setStatus(event.target.value)}>
                {STATUS_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-slate-500">
              Type
              <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm normal-case tracking-normal text-slate-700" value={facilityType} onChange={(event) => setFacilityType(event.target.value)}>
                {TYPE_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <Link className="inline-flex h-10 items-center justify-center rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep" href="/state/facilities/accreditation">
              Accreditation queue
            </Link>
          </div>
        </section>

        <section className="grid gap-3">
          <div className="flex items-center gap-2">
            <Building2 className="text-brand-deep" size={18} />
            <h2 className="text-base font-bold text-slate-950">Facility Registry</h2>
          </div>
          {facilitiesQuery.isError ? <p className="rounded bg-rose-50 p-3 text-sm font-semibold text-rose-700">Could not load facilities.</p> : null}
          <DataTable<MedicalFacility>
            columns={[
              { key: "facility", header: "Facility", render: (row) => <div><p className="font-bold text-slate-950">{row.facility_name}</p><p className="text-xs text-slate-500">{row.license_number}</p></div> },
              { key: "type", header: "Type", render: (row) => row.facility_type.replaceAll("_", " ") },
              { key: "lga", header: "LGA", render: (row) => row.lga_name || "Not set" },
              { key: "status", header: "Status", render: (row) => <StatusCell status={row.accreditation_status} /> },
              { key: "expiry", header: "Expiry", render: (row) => dateLabel(row.accreditation_expiry_date) },
              { key: "assessments", header: "Assessment ready", render: (row) => row.can_conduct_assessments ? "Yes" : "No" },
            ]}
            rows={facilities}
            empty={facilitiesQuery.isLoading ? "Loading facilities..." : "No facilities match the current filters."}
          />
        </section>
      </div>
    </PortalShell>
  );
}
