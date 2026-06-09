"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchFederalFinanceSettlements, type FederalFinanceSettlementItem } from "@/lib/api/federal";

function money(value?: string | number | null) {
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(Number(value || 0));
}

export default function Page() {
  const [status, setStatus] = useState("");
  const query = useQuery({ queryKey: ["federal-finance-settlements", status], queryFn: () => fetchFederalFinanceSettlements({ status }) });
  return (
    <PortalShell role="federal_admin" title="National settlements" description="Aggregate settlement monitoring across states and facilities.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="held">Held</option>
            <option value="processing">Processing</option>
            <option value="paid">Paid</option>
            <option value="failed">Failed</option>
          </select>
        </section>
        <DataTable<FederalFinanceSettlementItem>
          columns={[
            { key: "state", header: "State / facility", render: (row) => <div><p className="font-bold text-neutral-900">{row.state_name}</p><p className="text-xs text-neutral-500">{row.facility_name}</p></div> },
            { key: "reference", header: "Reference", render: (row) => row.settlement_reference },
            { key: "gross", header: "Gross", render: (row) => money(row.gross_amount) },
            { key: "status", header: "Status", render: (row) => <StatusCell status={row.settlement_status} /> },
          ]}
          rows={query.data || []}
          empty={query.isLoading ? "Loading settlements..." : "No settlements match the current filters."}
        />
      </div>
    </PortalShell>
  );
}
