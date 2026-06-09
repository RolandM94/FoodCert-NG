"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Calculator, CheckCircle2, CreditCard, ReceiptText } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { listAssessments } from "@/lib/api/assessments";
import { listEmployers } from "@/lib/api/identity";
import {
  getPaymentReceipt,
  initializeEmployerBulkAssessmentPayment,
  quoteEmployerBulkAssessmentPayment,
  verifyPayment,
} from "@/lib/api/payments";
import type { MedicalAssessment } from "@/types/assessments";
import type { BulkAssessmentPaymentQuote, PaymentReceipt, PaymentTransaction } from "@/types/payments";

const currency = new Intl.NumberFormat("en-NG", {
  style: "currency",
  currency: "NGN",
  maximumFractionDigits: 0,
});

function money(value: string) {
  return currency.format(Number(value || 0));
}

function eligibleAssessment(assessment: MedicalAssessment) {
  return ["draft", "payment_pending"].includes(assessment.status) && assessment.payment_status !== "success";
}

export default function Page() {
  const [selected, setSelected] = useState<string[]>([]);
  const [quote, setQuote] = useState<BulkAssessmentPaymentQuote | null>(null);
  const [payment, setPayment] = useState<PaymentTransaction | null>(null);
  const [receipt, setReceipt] = useState<PaymentReceipt | null>(null);

  const employersQuery = useQuery({
    queryKey: ["employers", "me"],
    queryFn: listEmployers,
  });
  const employer = employersQuery.data?.[0];

  const assessmentsQuery = useQuery({
    queryKey: ["employer-assessments"],
    queryFn: listAssessments,
  });

  const eligibleAssessments = useMemo(
    () => (assessmentsQuery.data || []).filter(eligibleAssessment),
    [assessmentsQuery.data]
  );

  const selectedAssessments = eligibleAssessments.filter((assessment) => selected.includes(assessment.id));

  const quoteMutation = useMutation({
    mutationFn: () => quoteEmployerBulkAssessmentPayment(employer!.id, selected),
    onSuccess: (payload) => {
      setQuote(payload);
      setPayment(null);
      setReceipt(null);
    },
  });

  const initializeMutation = useMutation({
    mutationFn: () => initializeEmployerBulkAssessmentPayment(employer!.id, selected),
    onSuccess: async (transaction) => {
      const verified = await verifyPayment(transaction.internal_reference);
      const paymentReceipt = await getPaymentReceipt(verified.id);
      setPayment(verified);
      setReceipt(paymentReceipt);
    },
  });

  function toggleAssessment(id: string) {
    setQuote(null);
    setPayment(null);
    setReceipt(null);
    setSelected((current) => (current.includes(id) ? current.filter((item) => item !== id) : [...current, id]));
  }

  const busy = quoteMutation.isPending || initializeMutation.isPending;

  return (
    <PortalShell
      role="employer"
      title="Bulk Assessment Payments"
      description="Select eligible assessment records, generate a quote, and allocate one employer payment across every selected handler."
    >
      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
          <div className="flex items-center justify-between gap-3 border-b border-neutral-100 p-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Eligible Assessments</p>
              <h2 className="mt-1 text-base font-bold text-neutral-900">Select records to pay</h2>
            </div>
            <span className="rounded bg-neutral-100 px-2 py-1 text-xs font-bold text-neutral-600">
              {selected.length} selected
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-sm">
              <thead className="bg-neutral-50 text-left text-xs font-bold uppercase tracking-wide text-neutral-500">
                <tr>
                  <th className="px-4 py-3">Pay</th>
                  <th className="px-4 py-3">Food Handler</th>
                  <th className="px-4 py-3">Facility</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-50">
                {eligibleAssessments.map((assessment) => (
                  <tr key={assessment.id} className="hover:bg-neutral-50">
                    <td className="px-4 py-3">
                      <input
                        aria-label={`Select ${assessment.food_handler_name || "assessment"}`}
                        checked={selected.includes(assessment.id)}
                        className="h-4 w-4 rounded border-neutral-300 text-brand-700"
                        onChange={() => toggleAssessment(assessment.id)}
                        type="checkbox"
                      />
                    </td>
                    <td className="px-4 py-3">
                      <p className="font-semibold text-neutral-900">{assessment.food_handler_name || "Unnamed handler"}</p>
                      <p className="text-xs text-neutral-500">{assessment.food_handler_identifier || assessment.id}</p>
                    </td>
                    <td className="px-4 py-3 text-neutral-600">{assessment.facility_name || "Not assigned"}</td>
                    <td className="px-4 py-3">
                      <span className="rounded bg-warning-50 px-2 py-1 text-xs font-bold uppercase text-warning-700 ring-1 ring-warning-100">
                        {assessment.status.replaceAll("_", " ")}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-neutral-500">{new Date(assessment.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
                {!eligibleAssessments.length ? (
                  <tr>
                    <td className="px-4 py-8 text-center text-sm font-semibold text-neutral-500" colSpan={5}>
                      No eligible unpaid assessments are available.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>

        <aside className="grid content-start gap-4">
          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-2">
              <Calculator className="text-brand-700" size={18} />
              <h2 className="text-base font-bold text-neutral-900">Quote</h2>
            </div>
            <div className="mt-4 grid gap-3 text-sm">
              <div className="flex items-center justify-between gap-3">
                <span className="text-neutral-500">Selected assessments</span>
                <span className="font-bold text-neutral-900">{selectedAssessments.length}</span>
              </div>
              <div className="flex items-center justify-between gap-3">
                <span className="text-neutral-500">Quoted total</span>
                <span className="font-bold text-neutral-900">{quote ? money(quote.amount) : "Not quoted"}</span>
              </div>
            </div>
            <button
              className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded bg-brand-700 px-3 py-2 text-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-50"
              disabled={!employer || !selected.length || busy}
              onClick={() => quoteMutation.mutate()}
              type="button"
            >
              <ReceiptText size={16} />
              Generate Quote
            </button>
            {quoteMutation.isError ? (
              <p className="mt-3 text-sm font-semibold text-danger-500">Quote could not be generated. Refresh the list and try again.</p>
            ) : null}
          </div>

          {quote ? (
            <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <h2 className="text-base font-bold text-neutral-900">Line Items</h2>
              <div className="mt-4 max-h-72 space-y-3 overflow-y-auto">
                {quote.line_items.map((item) => (
                  <div key={item.assessment_id} className="rounded border border-neutral-100 p-3">
                    <p className="text-sm font-bold text-neutral-900">{item.food_handler_name}</p>
                    <p className="mt-1 text-xs text-neutral-500">{item.facility_name}</p>
                    <p className="mt-2 text-sm font-bold text-brand-700">{money(item.amount)}</p>
                  </div>
                ))}
              </div>
              <button
                className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded bg-brand-600 px-3 py-2 text-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-50"
                disabled={busy}
                onClick={() => initializeMutation.mutate()}
                type="button"
              >
                <CreditCard size={16} />
                Pay Bulk Quote
              </button>
            </div>
          ) : null}

          {payment ? (
            <div className="rounded-lg border border-brand-200 bg-brand-50 p-5 text-brand-700">
              <div className="flex items-center gap-2">
                <CheckCircle2 size={18} />
                <h2 className="text-base font-bold">Payment Confirmed</h2>
              </div>
              <p className="mt-3 text-sm">Reference: {payment.internal_reference}</p>
              <p className="mt-1 text-sm">Amount: {money(payment.amount)}</p>
              <p className="mt-1 text-sm">Receipt lines: {receipt?.line_items?.length ?? 0}</p>
            </div>
          ) : null}
        </aside>
      </div>
    </PortalShell>
  );
}
