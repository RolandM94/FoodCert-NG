"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, Banknote, Download, FileWarning, RefreshCw, Send } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { downloadCsv } from "@/lib/export/csv";
import { getCurrentMedicalFacility } from "@/lib/api/facilities";
import { disputeFacilitySettlement, getFacilitySettlementReport, listFacilitySettlements } from "@/lib/api/settlements";
import type { MedicalFacility } from "@/types/facilities";
import type { FacilitySettlementReport, Settlement, SettlementDisputeStatus, SettlementStatus } from "@/types/settlements";

const STATUS_OPTIONS: Array<["", string] | [SettlementStatus, string]> = [
  ["", "All statuses"],
  ["pending", "Pending"],
  ["processing", "Processing"],
  ["paid", "Paid"],
  ["failed", "Failed"],
  ["cancelled", "Cancelled"],
];

const DISPUTE_OPTIONS: Array<["", string] | [SettlementDisputeStatus, string]> = [
  ["", "All dispute states"],
  ["none", "No dispute"],
  ["open", "Open"],
  ["under_review", "Under review"],
  ["resolved", "Resolved"],
  ["rejected", "Rejected"],
];

function money(value?: string | number | null) {
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(Number(value || 0));
}

function formatDate(value?: string) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium" }).format(new Date(value));
}

export default function Page() {
  const [facility, setFacility] = useState<MedicalFacility | null>(null);
  const [rows, setRows] = useState<Settlement[]>([]);
  const [cards, setCards] = useState<FacilitySettlementReport["cards"]>({
    paid_assessments: 0,
    completed_assessments: 0,
    pending_settlements: 0,
    processing_settlements: 0,
    paid_settlements: 0,
    failed_settlements: 0,
    gross_amount: 0,
    facility_amount: 0,
    state_amount: 0,
    platform_amount: 0,
    refunds: 0,
    disputes: 0,
  });
  const [filters, setFilters] = useState({ status: "", dispute_status: "", date_from: "", date_to: "" });
  const [disputeRow, setDisputeRow] = useState<Settlement | null>(null);
  const [disputeReason, setDisputeReason] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const params = useMemo(() => Object.fromEntries(Object.entries(filters).filter(([, value]) => value)), [filters]);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const profile = await getCurrentMedicalFacility();
      const [settlements, report] = await Promise.all([
        listFacilitySettlements(profile.id, params),
        getFacilitySettlementReport(profile.id, params),
      ]);
      setFacility(profile);
      setRows(settlements);
      setCards(report.cards);
    } catch {
      setError("Could not load settlement records.");
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  function updateFilter(field: keyof typeof filters, value: string) {
    setFilters((current) => ({ ...current, [field]: value }));
  }

  async function submitDispute() {
    if (!facility || !disputeRow || !disputeReason.trim()) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const updated = await disputeFacilitySettlement(facility.id, disputeRow.id, disputeReason);
      setRows((current) => current.map((row) => row.id === updated.id ? updated : row));
      setDisputeRow(null);
      setDisputeReason("");
      setSuccess("Settlement dispute submitted.");
      await loadData();
    } catch {
      setError("Could not submit settlement dispute.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <PortalShell role="facility_admin" title="Settlements" description="Track facility payouts, reconciliation totals, and settlement disputes without medical record details.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading settlements...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} />{error}</div> : null}
        {success ? <div className="rounded-lg bg-emerald-50 p-3 text-sm font-semibold text-emerald-800">{success}</div> : null}

        <section className="grid gap-3 md:grid-cols-4">
          {[
            ["Gross amount", cards.gross_amount],
            ["Facility share", cards.facility_amount],
            ["State share", cards.state_amount],
            ["Platform share", cards.platform_amount],
          ].map(([label, value]) => (
            <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm" key={label}>
              <Banknote className="text-brand-deep" size={18} />
              <p className="mt-2 text-xs font-bold uppercase text-slate-500">{label}</p>
              <p className="text-xl font-bold text-slate-950">{money(value)}</p>
            </div>
          ))}
        </section>

        <section className="grid gap-3 md:grid-cols-4">
          {[
            ["Paid assessments", cards.paid_assessments],
            ["Completed assessments", cards.completed_assessments],
            ["Pending settlements", cards.pending_settlements],
            ["Disputes", cards.disputes],
          ].map(([label, value]) => (
            <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm" key={label}>
              <p className="text-xs font-bold uppercase text-slate-500">{label}</p>
              <p className="text-2xl font-bold text-slate-950">{value}</p>
            </div>
          ))}
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 lg:grid-cols-[170px_170px_190px_210px_auto_auto]">
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" type="date" value={filters.date_from} onChange={(event) => updateFilter("date_from", event.target.value)} />
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" type="date" value={filters.date_to} onChange={(event) => updateFilter("date_to", event.target.value)} />
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={filters.status} onChange={(event) => updateFilter("status", event.target.value)}>
              {STATUS_OPTIONS.map(([value, text]) => <option key={value || "all"} value={value}>{text}</option>)}
            </select>
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={filters.dispute_status} onChange={(event) => updateFilter("dispute_status", event.target.value)}>
              {DISPUTE_OPTIONS.map(([value, text]) => <option key={value || "all"} value={value}>{text}</option>)}
            </select>
            <button className="inline-flex h-10 items-center justify-center gap-2 rounded border border-slate-200 px-3 text-sm font-bold text-slate-700" type="button" onClick={() => void loadData()}><RefreshCw size={16} /> Apply</button>
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-deep px-3 text-sm font-bold text-white disabled:opacity-60"
              disabled={!rows.length}
              type="button"
              onClick={() => downloadCsv("facility-settlements.csv", rows, [
                { header: "Payment reference", value: (row) => row.payment_reference || row.payment_transaction },
                { header: "Allocation", value: (row) => row.payment_allocation_reference || row.payment_allocation || "" },
                { header: "Assessment", value: (row) => row.assessment || "" },
                { header: "Fee schedule", value: (row) => row.fee_schedule_name || row.fee_schedule || "" },
                { header: "Gross", value: (row) => row.gross_amount },
                { header: "Facility amount", value: (row) => row.facility_amount },
                { header: "State amount", value: (row) => row.state_amount },
                { header: "Platform amount", value: (row) => row.platform_amount },
                { header: "Status", value: (row) => row.settlement_status },
                { header: "Settlement reference", value: (row) => row.settlement_reference },
                { header: "Dispute", value: (row) => row.dispute_status },
                { header: "Settled at", value: (row) => row.settled_at || "" },
              ])}
            ><Download size={16} /> Export</button>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 p-4">
            <h2 className="text-sm font-bold text-slate-950">{facility?.facility_name || "Facility"} settlement ledger</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs font-bold uppercase text-slate-500">
                <tr><th className="p-3">Trace</th><th className="p-3">Gross</th><th className="p-3">Facility</th><th className="p-3">State</th><th className="p-3">Platform</th><th className="p-3">Status</th><th className="p-3">Dispute</th><th className="p-3">Action</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {rows.length ? rows.map((row) => (
                  <tr key={row.id}>
                    <td className="p-3">
                      <p className="font-bold text-slate-950">{row.payment_reference || row.settlement_reference || row.id}</p>
                      <p className="text-xs text-slate-500">Allocation {row.payment_allocation_reference || row.payment_allocation || "legacy"}</p>
                      <p className="text-xs text-slate-500">Fee {row.fee_schedule_name || "Not linked"} · Created {formatDate(row.created_at)}</p>
                    </td>
                    <td className="p-3">{money(row.gross_amount)}</td>
                    <td className="p-3">{money(row.facility_amount)}</td>
                    <td className="p-3">{money(row.state_amount)}</td>
                    <td className="p-3">{money(row.platform_amount)}</td>
                    <td className="p-3"><StatusBadge status={row.settlement_status} /></td>
                    <td className="p-3"><StatusBadge status={row.dispute_status} />{row.dispute_reason ? <p className="mt-1 max-w-48 text-xs text-slate-500">{row.dispute_reason}</p> : null}</td>
                    <td className="p-3">
                      <button className="inline-flex h-9 items-center gap-2 rounded border border-slate-200 px-3 text-xs font-bold text-slate-700 disabled:opacity-60" disabled={row.dispute_status === "open" || row.dispute_status === "under_review"} type="button" onClick={() => setDisputeRow(row)}><FileWarning size={14} /> Dispute</button>
                    </td>
                  </tr>
                )) : (
                  <tr><td className="p-3 text-slate-500" colSpan={8}>No settlement records match the current filters.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        {disputeRow ? (
          <section className="rounded-lg border border-amber-200 bg-amber-50 p-4 shadow-sm">
            <h2 className="text-sm font-bold text-amber-950">Raise settlement dispute</h2>
            <p className="mt-1 text-sm text-amber-900">Reference: {disputeRow.payment_reference || disputeRow.settlement_reference || disputeRow.id}</p>
            <textarea className="mt-3 min-h-24 w-full rounded border border-amber-200 bg-white p-3 text-sm" placeholder="Describe the reconciliation issue" value={disputeReason} onChange={(event) => setDisputeReason(event.target.value)} />
            <div className="mt-3 flex flex-wrap gap-2">
              <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white disabled:opacity-60" disabled={busy || !disputeReason.trim()} type="button" onClick={() => void submitDispute()}><Send size={16} /> Submit dispute</button>
              <button className="h-10 rounded border border-amber-300 px-4 text-sm font-bold text-amber-900" type="button" onClick={() => { setDisputeRow(null); setDisputeReason(""); }}>Cancel</button>
            </div>
          </section>
        ) : null}
      </div>
    </PortalShell>
  );
}
