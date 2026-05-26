"use client";

import { useQuery } from "@tanstack/react-query";
import { Banknote } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { fetchFederalFinanceDashboard } from "@/lib/api/federal";
import type { FederalFinanceDashboard } from "@/lib/api/federal";

function money(value?: string | number | null) {
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(Number(value || 0));
}

export default function Page() {
  const query = useQuery({ queryKey: ["federal-finance-dashboard"], queryFn: () => fetchFederalFinanceDashboard() });
  const cards = query.data?.cards || ({} as FederalFinanceDashboard["cards"]);
  const items: Array<[string, string | number | undefined, string | number | undefined]> = [
    ["Payments", cards.payment_amount, cards.successful_payment_count],
    ["Gross settlements", cards.gross_amount, cards.paid_settlement_count],
    ["State revenue", cards.state_amount, cards.settlement_count],
    ["Subscriptions", cards.invoice_amount_paid, cards.active_subscription_count],
    ["Open issues", cards.reconciliation_issue_count, cards.refund_count],
  ];

  return (
    <PortalShell role="federal_admin" title="Federal finance" description="National aggregate finance monitoring for payments, settlements, subscriptions, refunds, and reconciliation.">
      <section className="grid gap-3 md:grid-cols-3 xl:grid-cols-5">
        {items.map(([label, amount, count]) => (
          <div key={label} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-center gap-2 text-brand-deep"><Banknote size={16} /><p className="text-xs font-bold uppercase text-slate-500">{label}</p></div>
            <p className="mt-2 text-xl font-bold text-slate-950">{label === "Open issues" ? Number(amount || 0) : money(amount)}</p>
            <p className="mt-1 text-xs text-slate-500">{count || 0} records</p>
          </div>
        ))}
      </section>
    </PortalShell>
  );
}
