"use client";

import { useQuery } from "@tanstack/react-query";
import { Banknote, RefreshCw } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { fetchStateFinanceDashboard } from "@/lib/api/state";
import type { StateRevenueSnapshot } from "@/lib/api/state";

function money(value?: string | number | null) {
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(Number(value || 0));
}

export default function Page() {
  const query = useQuery({ queryKey: ["state-finance-dashboard"], queryFn: () => fetchStateFinanceDashboard() });
  const cards = query.data?.cards || ({} as Partial<StateRevenueSnapshot["cards"]>);
  const cardItems: Array<[string, string | number | undefined, string | number | undefined]> = [
    ["Payments", cards.payment_amount, cards.successful_payment_count],
    ["State revenue", cards.state_amount, cards.paid_settlement_count],
    ["Facility payable", cards.facility_amount, cards.settlement_count],
    ["Refund exposure", cards.refund_amount, cards.open_refund_count],
    ["Reconciliation issues", cards.reconciliation_issue_count, cards.reconciliation_issue_count],
  ];

  return (
    <PortalShell role="state_admin" title="State finance" description="Monitor state-scoped payments, settlements, refunds, and reconciliation issues.">
      <div className="grid gap-5">
        <section className="flex items-center justify-between rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="flex items-center gap-2 text-brand-700"><Banknote size={18} /><h2 className="text-base font-bold text-neutral-900">Finance Overview</h2></div>
          <button className="inline-flex items-center gap-2 rounded border border-neutral-200 px-3 py-2 text-sm font-semibold" onClick={() => query.refetch()} type="button"><RefreshCw size={16} />Refresh</button>
        </section>
        <section className="grid gap-3 md:grid-cols-3 xl:grid-cols-5">
          {cardItems.map(([label, amount, count]) => (
            <div key={label} className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <p className="text-xs font-bold uppercase text-neutral-500">{label}</p>
              <p className="mt-2 text-xl font-bold text-neutral-900">{typeof amount === "number" && label === "Reconciliation issues" ? amount : money(amount)}</p>
              <p className="mt-1 text-xs text-neutral-500">{count || 0} records</p>
            </div>
          ))}
        </section>
      </div>
    </PortalShell>
  );
}
