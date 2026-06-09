"use client";

import { useQuery } from "@tanstack/react-query";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { FilterBar } from "@/components/ui/filter-bar";
import { listMedicalFacilities } from "@/lib/api/facilities";

export function ApprovedFacilitiesClient() {
  const query = useQuery({ queryKey: ["approved-facilities"], queryFn: listMedicalFacilities });

  if (query.isLoading) {
    return <div className="rounded-lg border border-neutral-200 bg-white p-6 text-sm text-neutral-600">Loading facilities...</div>;
  }

  if (query.isError) {
    return <div className="rounded-lg border border-danger-100 bg-danger-50 p-6 text-sm font-semibold text-danger-700">Unable to load approved facilities.</div>;
  }

  const facilities = (query.data ?? []).filter((facility) => facility.accreditation_status === "approved");

  return (
    <div className="grid gap-5">
      <FilterBar label="Search approved facilities" />
      <DataTable
        columns={[
          { key: "name", header: "Facility", render: (row) => row.facility_name },
          { key: "state", header: "State", render: (row) => row.state_name ?? "Unassigned" },
          { key: "type", header: "Type", render: (row) => row.facility_type },
          { key: "status", header: "Status", render: (row) => <StatusCell status={row.accreditation_status} /> }
        ]}
        rows={facilities}
        empty="No approved facilities are listed yet."
      />
    </div>
  );
}
