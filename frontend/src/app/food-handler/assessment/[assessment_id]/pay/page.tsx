"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AlertCircle, ArrowLeft, CheckCircle2, CreditCard, ReceiptText, RefreshCw } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { getAssessmentPaymentQuote, getPaymentReceipt, initializeAssessmentPayment, verifyPayment } from "@/lib/api/payments";
import type { AssessmentPaymentQuote, PaymentReceipt, PaymentTransaction } from "@/types/payments";

function money(value?: string | number) {
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(Number(value || 0));
}

function dateLabel(value?: string) {
  if (!value) return "Not issued";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function Page() {
  const params = useParams<{ assessment_id: string }>();
  const assessmentId = params.assessment_id;
  const [quote, setQuote] = useState<AssessmentPaymentQuote | null>(null);
  const [payment, setPayment] = useState<PaymentTransaction | null>(null);
  const [receipt, setReceipt] = useState<PaymentReceipt | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadQuote() {
      setLoading(true);
      setError("");
      try {
        setQuote(await getAssessmentPaymentQuote(assessmentId));
      } catch {
        setError("Could not load assessment payment details.");
      } finally {
        setLoading(false);
      }
    }
    void loadQuote();
  }, [assessmentId]);

  async function startPayment() {
    setBusy(true);
    setError("");
    try {
      const initialized = await initializeAssessmentPayment(assessmentId);
      setPayment(initialized);
      const verified = await verifyPayment(initialized.internal_reference);
      setPayment(verified);
      if (verified.status === "success") {
        setReceipt(await getPaymentReceipt(verified.id));
      }
    } catch {
      setError("Payment could not be completed. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <PortalShell role="food_handler" title="Assessment Payment" description="Review the approved assessment fee and complete payment before your appointment can be confirmed.">
      <div className="grid gap-5">
        <Link className="inline-flex w-fit items-center gap-2 rounded border border-neutral-200 px-3 py-2 text-sm font-bold text-neutral-700" href="/food-handler/assessments">
          <ArrowLeft size={16} /> Assessments
        </Link>

        {loading ? <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading payment details...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}

        {quote ? (
          <section className="grid gap-4 lg:grid-cols-[1fr_0.72fr]">
            <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <div className="flex items-center gap-3">
                <CreditCard className="text-brand-700" size={22} />
                <div>
                  <p className="text-xs font-bold uppercase text-brand-700">Approved fee</p>
                  <h2 className="text-xl font-bold text-neutral-900">{money(quote.amount)}</h2>
                </div>
              </div>

              <dl className="mt-5 grid gap-3 sm:grid-cols-2">
                <div><dt className="text-xs font-bold uppercase text-neutral-500">Facility</dt><dd className="text-sm font-semibold text-neutral-900">{quote.facility_name}</dd></div>
                <div><dt className="text-xs font-bold uppercase text-neutral-500">State</dt><dd className="text-sm font-semibold text-neutral-900">{quote.state_name}</dd></div>
                <div><dt className="text-xs font-bold uppercase text-neutral-500">Fee schedule</dt><dd className="text-sm font-semibold text-neutral-900">{quote.fee_name}</dd></div>
                <div><dt className="text-xs font-bold uppercase text-neutral-500">Currency</dt><dd className="text-sm font-semibold text-neutral-900">{quote.currency}</dd></div>
              </dl>

              <div className="mt-5 rounded bg-neutral-50 p-3 text-sm text-neutral-700">
                <p className="font-bold text-neutral-900">Split preview</p>
                <p className="mt-1">{money(quote.facility_fee)} facility / {money(quote.state_fee)} state / {money(quote.platform_fee)} platform</p>
              </div>

              <button className="mt-5 inline-flex h-11 items-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60" disabled={busy || payment?.status === "success"} onClick={() => void startPayment()} type="button">
                {busy ? <RefreshCw size={16} /> : <CreditCard size={16} />}
                {payment?.status === "success" ? "Payment complete" : "Pay assessment fee"}
              </button>
            </div>

            <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <h2 className="text-base font-bold text-neutral-900">Status</h2>
              <p className="mt-2 text-sm leading-6 text-neutral-600">{quote.terms_notice}</p>
              <p className="mt-3 text-sm leading-6 text-neutral-600">{quote.refund_policy_summary}</p>

              {payment ? (
                <div className="mt-5 rounded border border-neutral-200 p-3">
                  <p className="text-xs font-bold uppercase text-neutral-500">Transaction</p>
                  <p className="mt-1 break-all text-sm font-bold text-neutral-900">{payment.internal_reference}</p>
                  <p className="mt-1 text-sm font-semibold capitalize text-neutral-700">{payment.status.replaceAll("_", " ")}</p>
                </div>
              ) : null}

              {receipt ? (
                <div className="mt-5 rounded border border-brand-200 bg-brand-50 p-3">
                  <div className="flex items-center gap-2 text-brand-800"><CheckCircle2 size={18} /><p className="text-sm font-bold">Receipt issued</p></div>
                  <p className="mt-2 text-sm font-semibold text-brand-900">{receipt.receipt_number}</p>
                  <p className="text-xs text-brand-800">{dateLabel(receipt.issued_at)}</p>
                  <div className="mt-3 inline-flex items-center gap-2 text-sm font-bold text-brand-900"><ReceiptText size={16} /> {money(receipt.amount)}</div>
                </div>
              ) : null}
            </div>
          </section>
        ) : null}
      </div>
    </PortalShell>
  );
}
