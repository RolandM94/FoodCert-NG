"use client";

import { useQuery } from "@tanstack/react-query";
import { Download, Gauge } from "lucide-react";
import { useState } from "react";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchProviderPerformance, listPaymentReconciliations } from "@/lib/api/payments";
import { downloadCsv } from "@/lib/export/csv";
import type { PaymentReconciliationRecord, ProviderPerformanceRow, ReconciliationStatus } from "@/types/payments";

function money(value?: string | number | null) {
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(Number(value || 0));
}

function dateLabel(value?: string | null) {
  return value ? new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" }) : "Not set";
}

const statusOptions: Array<{ value: "" | ReconciliationStatus; label: string }> = [
  { value: "", label: "All statuses" },
  { value: "matched", label: "Matched" },
  { value: "missing_internal", label: "Missing internal" },
  { value: "amount_mismatch", label: "Amount mismatch" },
  { value: "currency_mismatch", label: "Currency mismatch" },
  { value: "duplicate_provider_reference", label: "Duplicate reference" },
  { value: "manually_resolved", label: "Manually resolved" },
];

export function ReconciliationWorkspace({ scope }: { scope: "admin" | "state" | "federal" }) {
  const [providerCode, setProviderCode] = useState("");
  const [status, setStatus] = useState("");
  const params = {
    ...(providerCode ? { provider_code: providerCode } : {}),
    ...(status ? { status } : {}),
  };
  const recordsQuery = useQuery({
    queryKey: ["payment-reconciliations", scope, providerCode, status],
    queryFn: () => listPaymentReconciliations(scope, params),
  });
  const performanceQuery = useQuery({
    queryKey: ["payment-reconciliation-performance", scope],
    queryFn: () => fetchProviderPerformance(scope),
  });
  const records = recordsQuery.data || [];
  const performance = performanceQuery.data || [];

  return (
    <div className="grid gap-5">
      <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
        <div className="grid gap-3 lg:grid-cols-[180px_220px_auto]">
          <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" placeholder="Provider code" value={providerCode} onChange={(event) => setProviderCode(event.target.value)} />
          <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
            {statusOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
          <button
            className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-700 px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-neutral-300"
            disabled={!records.length}
            onClick={() =>
              downloadCsv("payment-reconciliation.csv", records, [
                { header: "Provider", value: (row) => row.provider_code },
                { header: "Provider reference", value: (row) => row.provider_reference },
                { header: "Internal reference", value: (row) => row.internal_reference },
                { header: "Amount", value: (row) => row.amount },
                { header: "Currency", value: (row) => row.currency },
                { header: "Status", value: (row) => row.status },
                { header: "Resolved at", value: (row) => row.resolved_at },
              ])
            }
            type="button"
          >
            <Download size={16} />
            Export
          </button>
        </div>
      </section>

      <DataTable<ProviderPerformanceRow>
        columns={[
          { key: "provider", header: "Provider", render: (row) => <div className="flex items-center gap-2 font-bold text-neutral-900"><Gauge size={16} className="text-brand-700" />{row.provider_code}</div> },
          { key: "total", header: "Records", render: (row) => row.total_records },
          { key: "matched", header: "Matched", render: (row) => row.matched_records },
          { key: "issues", header: "Issues", render: (row) => row.issue_records },
          { key: "resolved", header: "Resolved", render: (row) => row.manually_resolved_records },
          { key: "amount", header: "Provider total", render: (row) => money(row.total_amount) },
        ]}
        rows={performance}
        empty={performanceQuery.isLoading ? "Loading provider performance..." : "No provider performance data yet."}
      />

      <DataTable<PaymentReconciliationRecord>
        columns={[
          { key: "reference", header: "Reference", render: (row) => <div><p className="font-bold text-neutral-900">{row.provider_reference}</p><p className="text-xs text-neutral-500">{row.internal_reference || "No internal match"}</p></div> },
          { key: "provider", header: "Provider", render: (row) => row.provider_code },
          { key: "amount", header: "Amount", render: (row) => `${money(row.amount)} ${row.currency}` },
          { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
          { key: "matched", header: "Matched", render: (row) => dateLabel(row.matched_at) },
          { key: "resolved", header: "Resolved", render: (row) => row.resolved_at ? dateLabel(row.resolved_at) : "Open" },
        ]}
        rows={records}
        empty={recordsQuery.isLoading ? "Loading reconciliation records..." : "No reconciliation records match the current filters."}
      />
    </div>
  );
}
