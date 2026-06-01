"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { AlertCircle, ArrowLeft, FileWarning, ReceiptText, Send } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { createRefundRequest, getPayment, getPaymentReceipt, listRefundRequests } from "@/lib/api/payments";
import type { PaymentReceipt, PaymentTransaction, RefundRequest } from "@/types/payments";

function money(value?: string | number) {
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(Number(value || 0));
}

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function Page() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [payment, setPayment] = useState<PaymentTransaction | null>(null);
  const [receipt, setReceipt] = useState<PaymentReceipt | null>(null);
  const [refunds, setRefunds] = useState<RefundRequest[]>([]);
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const row = await getPayment(id);
      setPayment(row);
      const refundRows = await listRefundRequests(id);
      setRefunds(refundRows);
      if (row.status === "success") {
        setReceipt(await getPaymentReceipt(id));
      }
    } catch {
      setError("Could not load payment details.");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  async function submitRefund() {
    if (!reason.trim()) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const refund = await createRefundRequest(id, { reason });
      setRefunds((current) => [refund, ...current.filter((item) => item.id !== refund.id)]);
      setReason("");
      setSuccess("Refund request submitted.");
    } catch {
      setError("Could not submit refund request.");
    } finally {
      setBusy(false);
    }
  }

  const openRefund = refunds.find((refund) => ["requested", "under_review", "approved", "processing"].includes(refund.status));

  return (
    <PortalShell role="food_handler" title="Payment Details" description="Review receipt details and submit a refund request where policy allows.">
      <div className="grid gap-5">
        <Link className="inline-flex w-fit items-center gap-2 rounded border border-slate-200 px-3 py-2 text-sm font-bold text-slate-700" href="/food-handler/payments"><ArrowLeft size={16} /> Payments</Link>
        {loading ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading payment...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} />{error}</div> : null}
        {success ? <div className="rounded-lg bg-emerald-50 p-3 text-sm font-semibold text-emerald-800">{success}</div> : null}

        {payment ? (
          <section className="grid gap-4 lg:grid-cols-[1fr_0.78fr]">
            <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-xs font-bold uppercase text-brand-deep">Transaction</p>
              <h2 className="mt-1 break-all text-xl font-bold text-slate-950">{payment.internal_reference}</h2>
              <dl className="mt-5 grid gap-3 sm:grid-cols-2">
                <div><dt className="text-xs font-bold uppercase text-slate-500">Amount</dt><dd className="text-sm font-semibold text-slate-900">{money(payment.amount)}</dd></div>
                <div><dt className="text-xs font-bold uppercase text-slate-500">Status</dt><dd className="mt-1"><StatusBadge status={payment.status} /></dd></div>
                <div><dt className="text-xs font-bold uppercase text-slate-500">Purpose</dt><dd className="text-sm font-semibold capitalize text-slate-900">{payment.related_entity_type.replaceAll("_", " ")}</dd></div>
                <div><dt className="text-xs font-bold uppercase text-slate-500">Paid at</dt><dd className="text-sm font-semibold text-slate-900">{dateLabel(payment.paid_at)}</dd></div>
              </dl>

              {receipt ? (
                <div className="mt-5 rounded border border-emerald-200 bg-emerald-50 p-4">
                  <div className="flex items-center gap-2 text-emerald-800"><ReceiptText size={18} /><p className="text-sm font-bold">Receipt</p></div>
                  <p className="mt-2 text-sm font-bold text-emerald-950">{receipt.receipt_number}</p>
                  <p className="text-xs text-emerald-800">{dateLabel(receipt.issued_at)}</p>
                </div>
              ) : null}
            </div>

            <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center gap-2">
                <FileWarning className="text-brand-deep" size={18} />
                <h2 className="text-base font-bold text-slate-950">Refund request</h2>
              </div>
              {openRefund ? (
                <div className="mt-4 rounded border border-amber-200 bg-amber-50 p-3">
                  <p className="text-sm font-bold text-amber-950">Request in progress</p>
                  <p className="mt-1 text-sm text-amber-900">{openRefund.reason}</p>
                  <div className="mt-2"><StatusBadge status={openRefund.status} /></div>
                </div>
              ) : payment.status === "success" ? (
                <div className="mt-4 grid gap-3">
                  <textarea className="min-h-28 rounded border border-slate-200 bg-slate-50 p-3 text-sm" placeholder="Explain why you are requesting a refund" value={reason} onChange={(event) => setReason(event.target.value)} />
                  <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white disabled:opacity-60" disabled={busy || !reason.trim()} onClick={() => void submitRefund()} type="button"><Send size={16} /> Submit request</button>
                </div>
              ) : (
                <p className="mt-4 text-sm text-slate-600">Refund requests are available after successful payment.</p>
              )}

              <div className="mt-5 grid gap-2">
                {refunds.map((refund) => (
                  <div className="rounded border border-slate-200 p-3" key={refund.id}>
                    <div className="flex items-center justify-between gap-2"><p className="text-sm font-bold text-slate-950">{money(refund.amount)}</p><StatusBadge status={refund.status} /></div>
                    <p className="mt-1 text-sm text-slate-600">{refund.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>
        ) : null}
      </div>
    </PortalShell>
  );
}
