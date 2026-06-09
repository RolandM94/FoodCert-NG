"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, CreditCard, RefreshCw, ReceiptText, ShieldCheck, WalletCards, XCircle } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { SubscriptionPlanCard } from "@/components/ui/subscription-plan-card";
import { listEmployers } from "@/lib/api/identity";
import {
  changeEmployerSubscriptionPlan,
  cancelEmployerSubscription,
  checkoutEmployerSubscription,
  getEmployerEntitlements,
  getEmployerSubscription,
  listEmployerInvoices,
  listEmployerPayments,
  listSubscriptionPlans,
  renewEmployerSubscription,
} from "@/lib/api/payments";
import type { BillingCycle, EmployerSubscriptionPlan, InvoiceStatus, PaymentStatus, SubscriptionStatus } from "@/types/payments";

const currency = new Intl.NumberFormat("en-NG", {
  style: "currency",
  currency: "NGN",
  maximumFractionDigits: 0,
});

function money(value: string) {
  return currency.format(Number(value || 0));
}

function planFeatures(plan: EmployerSubscriptionPlan) {
  const features = Object.entries(plan.features || {})
    .filter(([, value]) => Boolean(value))
    .map(([key]) => key.replaceAll("_", " "));
  return [
    `${plan.max_food_handlers} food handlers`,
    `${plan.max_locations} location${plan.max_locations === 1 ? "" : "s"}`,
    ...features.slice(0, 4),
  ];
}

function StatusBadge({ status }: { status: PaymentStatus | SubscriptionStatus | InvoiceStatus }) {
  const tone =
    status === "active" || status === "success" || status === "paid"
      ? "bg-brand-50 text-brand-700 ring-brand-200"
      : status === "pending" || status === "past_due" || status === "trial" || status === "issued"
        ? "bg-warning-50 text-warning-700 ring-warning-100"
        : "bg-danger-50 text-danger-700 ring-danger-100";
  return (
    <span className={`rounded px-2 py-1 text-xs font-bold uppercase tracking-wide ring-1 ${tone}`}>
      {status.replaceAll("_", " ")}
    </span>
  );
}

export default function Page() {
  const queryClient = useQueryClient();
  const [billingCycle, setBillingCycle] = useState<BillingCycle>("monthly");

  const employersQuery = useQuery({
    queryKey: ["employers", "me"],
    queryFn: listEmployers,
  });
  const employer = employersQuery.data?.[0];

  const plansQuery = useQuery({
    queryKey: ["subscription-plans"],
    queryFn: listSubscriptionPlans,
  });

  const subscriptionQuery = useQuery({
    queryKey: ["employer-subscription", employer?.id],
    queryFn: () => getEmployerSubscription(employer!.id),
    enabled: Boolean(employer?.id),
  });

  const invoicesQuery = useQuery({
    queryKey: ["employer-invoices", employer?.id],
    queryFn: () => listEmployerInvoices(employer!.id),
    enabled: Boolean(employer?.id),
  });

  const paymentsQuery = useQuery({
    queryKey: ["employer-payments", employer?.id],
    queryFn: () => listEmployerPayments(employer!.id),
    enabled: Boolean(employer?.id),
  });

  const entitlementsQuery = useQuery({
    queryKey: ["employer-entitlements", employer?.id],
    queryFn: () => getEmployerEntitlements(employer!.id),
    enabled: Boolean(employer?.id),
  });

  const currentSubscription = subscriptionQuery.data;
  const activePlans = useMemo(
    () => (plansQuery.data || []).filter((plan) => plan.status === "active"),
    [plansQuery.data]
  );

  const checkoutMutation = useMutation({
    mutationFn: (planId: string) =>
      currentSubscription
        ? changeEmployerSubscriptionPlan(employer!.id, { plan_id: planId, billing_cycle: billingCycle })
        : checkoutEmployerSubscription(employer!.id, { plan_id: planId, billing_cycle: billingCycle }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["employer-subscription", employer?.id] });
      queryClient.invalidateQueries({ queryKey: ["employer-invoices", employer?.id] });
      queryClient.invalidateQueries({ queryKey: ["employer-payments", employer?.id] });
      queryClient.invalidateQueries({ queryKey: ["employer-entitlements", employer?.id] });
    },
  });

  const renewMutation = useMutation({
    mutationFn: () => renewEmployerSubscription(employer!.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["employer-subscription", employer?.id] });
      queryClient.invalidateQueries({ queryKey: ["employer-invoices", employer?.id] });
      queryClient.invalidateQueries({ queryKey: ["employer-payments", employer?.id] });
      queryClient.invalidateQueries({ queryKey: ["employer-entitlements", employer?.id] });
    },
  });

  const cancelMutation = useMutation({
    mutationFn: () => cancelEmployerSubscription(employer!.id, { reason: "Cancelled from employer billing dashboard" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["employer-subscription", employer?.id] });
      queryClient.invalidateQueries({ queryKey: ["employer-entitlements", employer?.id] });
    },
  });

  const usage = currentSubscription?.usage_percentage ?? 0;
  const expiryWarning = currentSubscription?.is_active && (currentSubscription.days_until_expiry ?? 999) <= 7;
  const isExpired = currentSubscription && !currentSubscription.is_active;
  const entitlements = entitlementsQuery.data || currentSubscription?.entitlements;

  return (
    <PortalShell
      role="employer"
      title="Subscription & Billing"
      description="Manage plan capacity, billing cycle, invoices, and employer subscription payments."
    >
      <div className="grid gap-6">
        {expiryWarning ? (
          <div className="flex items-start gap-3 rounded-lg border border-warning-100 bg-warning-50 p-4 text-warning-700">
            <AlertTriangle size={20} />
            <div>
              <p className="text-sm font-bold">Subscription expires soon</p>
              <p className="mt-1 text-sm">Renew or change plan within {currentSubscription?.days_until_expiry} days to avoid premium feature restrictions.</p>
            </div>
          </div>
        ) : null}

        {isExpired ? (
          <div className="flex items-start gap-3 rounded-lg border border-danger-100 bg-danger-50 p-4 text-danger-700">
            <AlertTriangle size={20} />
            <div>
              <p className="text-sm font-bold">Subscription inactive</p>
              <p className="mt-1 text-sm">Regulatory visibility remains available, but premium capacity, branch reporting, and advanced exports may be restricted.</p>
            </div>
          </div>
        ) : null}

        <section className="grid gap-4 lg:grid-cols-[1fr_0.7fr]">
          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-3">
              <WalletCards className="text-brand-700" size={22} />
              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Current Plan</p>
                <h2 className="mt-1 text-xl font-bold text-neutral-900">{currentSubscription?.plan_name || "No active plan"}</h2>
              </div>
            </div>
            <div className="mt-5 grid gap-4 sm:grid-cols-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Status</p>
                <div className="mt-2">{currentSubscription ? <StatusBadge status={currentSubscription.status} /> : <StatusBadge status="expired" />}</div>
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Billing Cycle</p>
                <p className="mt-2 text-sm font-semibold capitalize text-neutral-900">{currentSubscription?.billing_cycle || "Not set"}</p>
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Renewal Date</p>
                <p className="mt-2 text-sm font-semibold text-neutral-900">
                  {currentSubscription?.expires_at ? new Date(currentSubscription.expires_at).toLocaleDateString() : "Not scheduled"}
                </p>
              </div>
            </div>
            <div className="mt-6">
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="font-semibold text-neutral-700">Food handler usage</span>
                <span className="text-neutral-500">
                  {currentSubscription?.handlers_used ?? 0} / {currentSubscription?.max_food_handlers ?? 5}
                </span>
              </div>
              <div className="mt-2 h-2 rounded bg-neutral-100">
                <div className="h-2 rounded bg-brand-600" style={{ width: `${Math.min(usage, 100)}%` }} />
              </div>
            </div>
            {currentSubscription ? (
              <div className="mt-5 flex flex-wrap gap-2">
                <button
                  className="inline-flex items-center gap-2 rounded border border-brand-700 px-3 py-2 text-sm font-bold text-brand-700 disabled:cursor-not-allowed disabled:opacity-50"
                  disabled={!employer || renewMutation.isPending}
                  onClick={() => renewMutation.mutate()}
                  type="button"
                >
                  <RefreshCw size={16} />
                  Renew
                </button>
                {currentSubscription.status !== "cancelled" ? (
                  <button
                    className="inline-flex items-center gap-2 rounded border border-danger-100 px-3 py-2 text-sm font-bold text-danger-700 disabled:cursor-not-allowed disabled:opacity-50"
                    disabled={!employer || cancelMutation.isPending}
                    onClick={() => cancelMutation.mutate()}
                    type="button"
                  >
                    <XCircle size={16} />
                    Cancel
                  </button>
                ) : null}
              </div>
            ) : null}
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-3">
              <CreditCard className="text-brand-700" size={22} />
              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Billing Controls</p>
                <h2 className="mt-1 text-base font-bold text-neutral-900">Cycle preference</h2>
              </div>
            </div>
            <div className="mt-5 grid grid-cols-2 rounded-lg border border-neutral-200 bg-neutral-50 p-1">
              {(["monthly", "yearly"] as BillingCycle[]).map((cycle) => (
                <button
                  key={cycle}
                  className={`rounded px-3 py-2 text-sm font-bold capitalize ${billingCycle === cycle ? "bg-white text-brand-700 shadow-sm" : "text-neutral-500"}`}
                  onClick={() => setBillingCycle(cycle)}
                  type="button"
                >
                  {cycle}
                </button>
              ))}
            </div>
            <p className="mt-4 text-sm leading-6 text-neutral-600">
              Changing plans creates a verified subscription payment through the configured payment provider and activates the selected plan.
            </p>
            <div className="mt-5 rounded-lg border border-neutral-200 bg-white p-4">
              <div className="flex items-center gap-2">
                <ShieldCheck className="text-brand-700" size={18} />
                <p className="text-sm font-bold text-neutral-900">Entitlements</p>
              </div>
              <div className="mt-4 grid gap-3 text-sm">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-neutral-500">Premium features</span>
                  <StatusBadge status={entitlements?.premium_features_active ? "active" : "expired"} />
                </div>
                <div className="flex items-center justify-between gap-3">
                  <span className="text-neutral-500">Regulatory access</span>
                  <StatusBadge status={entitlements?.regulatory_access === false ? "cancelled" : "active"} />
                </div>
                <div className="grid grid-cols-3 gap-2 pt-1 text-center">
                  <div className="rounded border border-neutral-100 p-2">
                    <p className="text-xs text-neutral-500">Handlers</p>
                    <p className="font-bold text-neutral-900">{entitlements?.limits.max_food_handlers ?? currentSubscription?.max_food_handlers ?? 5}</p>
                  </div>
                  <div className="rounded border border-neutral-100 p-2">
                    <p className="text-xs text-neutral-500">Locations</p>
                    <p className="font-bold text-neutral-900">{entitlements?.limits.max_locations ?? currentSubscription?.max_locations ?? 1}</p>
                  </div>
                  <div className="rounded border border-neutral-100 p-2">
                    <p className="text-xs text-neutral-500">Users</p>
                    <p className="font-bold text-neutral-900">{entitlements?.limits.max_users ?? currentSubscription?.max_users ?? 1}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section>
          <div className="mb-3 flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Plans</p>
              <h2 className="mt-1 text-lg font-bold text-neutral-900">Upgrade or change plan</h2>
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            {activePlans.map((plan) => {
              const price = billingCycle === "yearly" ? plan.price_yearly : plan.price_monthly;
              const current = currentSubscription?.plan === plan.id && currentSubscription?.billing_cycle === billingCycle;
              return (
                <SubscriptionPlanCard
                  key={plan.id}
                  actionLabel={currentSubscription ? "Change Plan" : "Subscribe"}
                  current={current}
                  description={plan.description}
                  disabled={checkoutMutation.isPending || !employer}
                  features={planFeatures(plan)}
                  name={plan.name}
                  onAction={() => checkoutMutation.mutate(plan.id)}
                  price={`${money(price)} / ${billingCycle === "yearly" ? "year" : "month"}`}
                  selected={currentSubscription?.plan === plan.id}
                />
              );
            })}
          </div>
          {checkoutMutation.isError ? (
            <p className="mt-3 text-sm font-semibold text-danger-500">Could not update subscription. Please check the selected plan and try again.</p>
          ) : null}
          {renewMutation.isError || cancelMutation.isError ? (
            <p className="mt-3 text-sm font-semibold text-danger-500">Could not update billing lifecycle. Please try again.</p>
          ) : null}
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <ReceiptText className="text-brand-700" size={18} />
              <h2 className="text-base font-bold text-neutral-900">Billing History</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[520px] text-left text-sm">
                <thead className="text-xs font-bold uppercase tracking-wide text-neutral-500">
                  <tr>
                    <th className="border-b border-neutral-100 py-2">Invoice</th>
                    <th className="border-b border-neutral-100 py-2">Date</th>
                    <th className="border-b border-neutral-100 py-2">Amount</th>
                    <th className="border-b border-neutral-100 py-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {(invoicesQuery.data || []).map((invoice) => (
                    <tr key={invoice.id}>
                      <td className="border-b border-neutral-50 py-3 font-semibold text-neutral-900">{invoice.invoice_number}</td>
                      <td className="border-b border-neutral-50 py-3 text-neutral-600">{invoice.date}</td>
                      <td className="border-b border-neutral-50 py-3 text-neutral-600">{money(invoice.amount)}</td>
                      <td className="border-b border-neutral-50 py-3"><StatusBadge status={invoice.status} /></td>
                    </tr>
                  ))}
                  {!invoicesQuery.data?.length ? (
                    <tr><td className="py-5 text-neutral-500" colSpan={4}>No invoices yet.</td></tr>
                  ) : null}
                </tbody>
              </table>
            </div>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <CreditCard className="text-brand-700" size={18} />
              <h2 className="text-base font-bold text-neutral-900">Payment History</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[520px] text-left text-sm">
                <thead className="text-xs font-bold uppercase tracking-wide text-neutral-500">
                  <tr>
                    <th className="border-b border-neutral-100 py-2">Date</th>
                    <th className="border-b border-neutral-100 py-2">Amount</th>
                    <th className="border-b border-neutral-100 py-2">Reference</th>
                    <th className="border-b border-neutral-100 py-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {(paymentsQuery.data || []).map((payment) => (
                    <tr key={payment.id}>
                      <td className="border-b border-neutral-50 py-3 text-neutral-600">{new Date(payment.created_at).toLocaleDateString()}</td>
                      <td className="border-b border-neutral-50 py-3 text-neutral-600">{money(payment.amount)}</td>
                      <td className="border-b border-neutral-50 py-3 font-semibold text-neutral-900">{payment.provider_reference || payment.internal_reference}</td>
                      <td className="border-b border-neutral-50 py-3"><StatusBadge status={payment.status} /></td>
                    </tr>
                  ))}
                  {!paymentsQuery.data?.length ? (
                    <tr><td className="py-5 text-neutral-500" colSpan={4}>No payments yet.</td></tr>
                  ) : null}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
