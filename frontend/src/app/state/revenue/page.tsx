"use client";

import { useQuery } from "@tanstack/react-query";
import { Banknote, Download } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchStateRevenue, fetchStateSettlements, type StateSettlementItem } from "@/lib/api/state";
import { downloadCsv } from "@/lib/export/csv";

function money(value?: string | number | null) {
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(Number(value || 0));
}

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [status, setStatus] = useState("");
  const revenueQuery = useQuery({
    queryKey: ["state-revenue", dateFrom, dateTo],
    queryFn: () => fetchStateRevenue({ date_from: dateFrom, date_to: dateTo }),
  });
  const settlementsQuery = useQuery({
    queryKey: ["state-settlements", status, dateFrom, dateTo],
    queryFn: () => fetchStateSettlements({ status, date_from: dateFrom, date_to: dateTo }),
  });
  const snapshot = revenueQuery.data;
  const rows = settlementsQuery.data || [];

  return (
    <PortalShell role="state_admin" title="Revenue" description="Review state revenue, facility settlement splits, and reconciliation status.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 lg:grid-cols-[170px_170px_220px_auto]">
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} />
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} />
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
              <option value="">All settlement statuses</option>
              <option value="pending">Pending</option>
              <option value="processing">Processing</option>
              <option value="paid">Paid</option>
              <option value="failed">Failed</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-deep px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300"
              disabled={!rows.length}
              onClick={() =>
                downloadCsv("state-settlements.csv", rows, [
                  { header: "Facility", value: (row) => row.facility_name },
                  { header: "Gross", value: (row) => row.gross_amount },
                  { header: "Facility amount", value: (row) => row.facility_amount },
                  { header: "State amount", value: (row) => row.state_amount },
                  { header: "Platform amount", value: (row) => row.platform_amount },
                  { header: "Status", value: (row) => row.settlement_status },
                  { header: "Reference", value: (row) => row.settlement_reference },
                  { header: "Settled at", value: (row) => row.settled_at },
                ])
              }
              type="button"
            >
              <Download size={16} />
              Export
            </button>
          </div>
        </section>

        <section className="grid gap-3 md:grid-cols-4">
          {[
            ["Gross revenue", snapshot?.cards.gross_amount],
            ["State share", snapshot?.cards.state_amount],
            ["Facility share", snapshot?.cards.facility_amount],
            ["Platform share", snapshot?.cards.platform_amount],
          ].map(([label, value]) => (
            <div key={label} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <div className="mb-2 flex items-center gap-2 text-brand-deep"><Banknote size={16} /><p className="text-xs font-bold uppercase text-slate-500">{label}</p></div>
              <p className="text-xl font-bold text-slate-950">{money(value)}</p>
            </div>
          ))}
        </section>

        <DataTable<StateSettlementItem>
          columns={[
            { key: "facility", header: "Facility", render: (row) => <div><p className="font-bold text-slate-950">{row.facility_name}</p><p className="text-xs text-slate-500">{row.settlement_reference || "No reference"}</p></div> },
            { key: "gross", header: "Gross", render: (row) => money(row.gross_amount) },
            { key: "facility_share", header: "Facility share", render: (row) => money(row.facility_amount) },
            { key: "state", header: "State share", render: (row) => money(row.state_amount) },
            { key: "platform", header: "Platform share", render: (row) => money(row.platform_amount) },
            { key: "status", header: "Status", render: (row) => <StatusCell status={row.settlement_status} /> },
            { key: "settled", header: "Settled", render: (row) => dateLabel(row.settled_at) },
          ]}
          rows={rows}
          empty={settlementsQuery.isLoading ? "Loading settlements..." : "No settlements match the current filters."}
        />
      </div>
    </PortalShell>
  );
}
