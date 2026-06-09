"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AlertCircle, CreditCard, ReceiptText, RefreshCw } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { listPayments } from "@/lib/api/payments";
import type { PaymentTransaction } from "@/types/payments";

function money(value?: string | number) {
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(Number(value || 0));
}

function dateLabel(value?: string) {
  if (!value) return "Not paid";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium" }).format(new Date(value));
}

export default function Page() {
  const [rows, setRows] = useState<PaymentTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      setRows(await listPayments({ payer_type: "food_handler" }));
    } catch {
      setError("Could not load payment history.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  const paid = rows.filter((row) => row.status === "success");
  const totalPaid = paid.reduce((sum, row) => sum + Number(row.amount || 0), 0);

  return (
    <PortalShell role="food_handler" title="Payments" description="View assessment payments, receipts, retry status, and refund requests.">
      <div className="grid gap-5">
        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}

        <section className="grid gap-3 md:grid-cols-3">
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <CreditCard className="text-brand-700" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Transactions</p>
            <p className="text-2xl font-bold text-neutral-900">{rows.length}</p>
          </div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <ReceiptText className="text-brand-700" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Successful</p>
            <p className="text-2xl font-bold text-neutral-900">{paid.length}</p>
          </div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-bold uppercase text-neutral-500">Total paid</p>
            <p className="mt-2 text-2xl font-bold text-neutral-900">{money(totalPaid)}</p>
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-200 p-4">
            <h2 className="text-sm font-bold text-neutral-900">Payment history</h2>
            <button className="inline-flex h-9 items-center gap-2 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700" onClick={() => void loadData()} type="button"><RefreshCw size={14} /> Refresh</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-neutral-50 text-xs font-bold uppercase text-neutral-500">
                <tr><th className="p-3">Reference</th><th className="p-3">Purpose</th><th className="p-3">Amount</th><th className="p-3">Status</th><th className="p-3">Paid</th><th className="p-3">Action</th></tr>
              </thead>
              <tbody className="divide-y divide-neutral-200">
                {rows.map((row) => (
                  <tr key={row.id}>
                    <td className="p-3 font-bold text-neutral-900">{row.internal_reference}</td>
                    <td className="p-3 capitalize text-neutral-700">{row.related_entity_type.replaceAll("_", " ")}</td>
                    <td className="p-3 text-neutral-700">{money(row.amount)}</td>
                    <td className="p-3"><StatusBadge status={row.status} /></td>
                    <td className="p-3 text-neutral-600">{dateLabel(row.paid_at)}</td>
                    <td className="p-3"><Link className="rounded border border-neutral-200 px-3 py-1.5 text-xs font-bold text-neutral-700" href={`/food-handler/payments/${row.id}`}>Open</Link></td>
                  </tr>
                ))}
                {!rows.length ? <tr><td className="p-3 text-neutral-500" colSpan={6}>{loading ? "Loading payments..." : "No payment records found."}</td></tr> : null}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
