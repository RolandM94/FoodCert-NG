"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchStateFinanceRefunds, type StateRefundItem } from "@/lib/api/state";

function money(value?: string | number | null) {
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(Number(value || 0));
}

export default function Page() {
  const [status, setStatus] = useState("");
  const query = useQuery({ queryKey: ["state-finance-refunds", status], queryFn: () => fetchStateFinanceRefunds({ status }) });
  const rows = query.data || [];

  return (
    <PortalShell role="state_admin" title="State refunds" description="Track refund requests linked to payments in your state.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
            <option value="">All refund statuses</option>
            <option value="requested">Requested</option>
            <option value="approved">Approved</option>
            <option value="processing">Processing</option>
            <option value="refunded">Refunded</option>
            <option value="rejected">Rejected</option>
          </select>
        </section>
        <DataTable<StateRefundItem>
          columns={[
            { key: "payment", header: "Payment", render: (row) => <div><p className="font-bold text-neutral-900">{row.payment_reference}</p><p className="text-xs text-neutral-500">{row.requested_by_email || "Requester unavailable"}</p></div> },
            { key: "amount", header: "Amount", render: (row) => money(row.amount) },
            { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
            { key: "reason", header: "Reason", render: (row) => row.reason },
          ]}
          rows={rows}
          empty={query.isLoading ? "Loading refunds..." : "No refund requests match the current filters."}
        />
      </div>
    </PortalShell>
  );
}
