"use client";

import { useQuery } from "@tanstack/react-query";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable } from "@/components/ui/data-table";
import { fetchFederalRevenueByState, type FederalRevenueByStateRow } from "@/lib/api/federal";

function money(value?: string | number | null) {
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(Number(value || 0));
}

export default function Page() {
  const query = useQuery({ queryKey: ["federal-revenue-by-state"], queryFn: () => fetchFederalRevenueByState() });
  return (
    <PortalShell role="federal_admin" title="Revenue by state" description="Compare state-level finance totals using aggregate settlement data.">
      <DataTable<FederalRevenueByStateRow>
        columns={[
          { key: "state", header: "State", render: (row) => <p className="font-bold text-slate-950">{row.state_name}</p> },
          { key: "count", header: "Settlements", render: (row) => row.settlement_count },
          { key: "gross", header: "Gross", render: (row) => money(row.gross_amount) },
          { key: "state_share", header: "State share", render: (row) => money(row.state_amount) },
          { key: "facility_share", header: "Facility share", render: (row) => money(row.facility_amount) },
          { key: "platform_share", header: "Platform share", render: (row) => money(row.platform_amount) },
        ]}
        rows={query.data || []}
        empty={query.isLoading ? "Loading revenue..." : "No revenue records found."}
      />
    </PortalShell>
  );
}
