"use client";

import { useQuery } from "@tanstack/react-query";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchFederalFinanceSubscriptions } from "@/lib/api/federal";
import type { FederalSubscriptionFinance } from "@/lib/api/federal";

function money(value?: string | number | null) {
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(Number(value || 0));
}

export default function Page() {
  const query = useQuery({ queryKey: ["federal-finance-subscriptions"], queryFn: fetchFederalFinanceSubscriptions });
  const cards = query.data?.cards || ({} as FederalSubscriptionFinance["cards"]);
  return (
    <PortalShell role="federal_admin" title="Subscription finance" description="Monitor employer subscriptions and invoice payment status nationally.">
      <div className="grid gap-5">
        <section className="grid gap-3 md:grid-cols-4">
          {[
            ["Active subscriptions", cards.active_subscription_count],
            ["Past due", cards.past_due_subscription_count],
            ["Invoice due", money(cards.invoice_amount_due)],
            ["Invoice paid", money(cards.invoice_amount_paid)],
          ].map(([label, value]) => (
            <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm" key={label}>
              <p className="text-xs font-bold uppercase text-slate-500">{label}</p>
              <p className="mt-2 text-xl font-bold text-slate-950">{value}</p>
            </div>
          ))}
        </section>
        <DataTable<{ status: string; total: number }>
          columns={[
            { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
            { key: "total", header: "Subscriptions", render: (row) => row.total },
          ]}
          rows={query.data?.status || []}
          empty={query.isLoading ? "Loading subscriptions..." : "No subscription status records found."}
        />
      </div>
    </PortalShell>
  );
}
