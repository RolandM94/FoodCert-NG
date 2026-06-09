"use client";

import { useQuery } from "@tanstack/react-query";
import { Download } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { downloadCsv } from "@/lib/export/csv";
import { fetchStateFinanceSettlements, type StateSettlementItem } from "@/lib/api/state";

function money(value?: string | number | null) {
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(Number(value || 0));
}

export default function Page() {
  const [status, setStatus] = useState("");
  const query = useQuery({ queryKey: ["state-finance-settlements", status], queryFn: () => fetchStateFinanceSettlements({ status }) });
  const rows = query.data || [];

  return (
    <PortalShell role="state_admin" title="State settlements" description="Review state-scoped facility settlements and payout status.">
      <div className="grid gap-5">
        <section className="grid gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm md:grid-cols-[220px_auto]">
          <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="held">Held</option>
            <option value="processing">Processing</option>
            <option value="paid">Paid</option>
            <option value="failed">Failed</option>
          </select>
          <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-700 px-3 text-sm font-semibold text-white disabled:bg-neutral-300" disabled={!rows.length} onClick={() => downloadCsv("state-finance-settlements.csv", rows, [
            { header: "Facility", value: (row) => row.facility_name },
            { header: "Reference", value: (row) => row.settlement_reference },
            { header: "Gross", value: (row) => row.gross_amount },
            { header: "State amount", value: (row) => row.state_amount },
            { header: "Status", value: (row) => row.settlement_status },
          ])} type="button"><Download size={16} />Export</button>
        </section>
        <DataTable<StateSettlementItem>
          columns={[
            { key: "facility", header: "Facility", render: (row) => <div><p className="font-bold text-neutral-900">{row.facility_name}</p><p className="text-xs text-neutral-500">{row.settlement_reference}</p></div> },
            { key: "gross", header: "Gross", render: (row) => money(row.gross_amount) },
            { key: "facility", header: "Facility share", render: (row) => money(row.facility_amount) },
            { key: "state", header: "State share", render: (row) => money(row.state_amount) },
            { key: "status", header: "Status", render: (row) => <StatusCell status={row.settlement_status} /> },
          ]}
          rows={rows}
          empty={query.isLoading ? "Loading settlements..." : "No settlements match the current filters."}
        />
      </div>
    </PortalShell>
  );
}
