"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, BarChart3 } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable } from "@/components/ui/data-table";
import { fetchFederalCertificateAnalytics } from "@/lib/api/federal";

export default function Page() {
  const analyticsQuery = useQuery({
    queryKey: ["federal-certificate-analytics"],
    queryFn: fetchFederalCertificateAnalytics,
  });
  const analytics = analyticsQuery.data;

  return (
    <PortalShell role="federal_admin" title="Certificate analytics" description="Aggregate trust monitoring for federal oversight, with sensitive certificate details kept out of the default view.">
      <div className="grid gap-5">
        <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {[
            ["Total certificates", analytics?.cards.total ?? 0],
            ["Active", analytics?.cards.active ?? 0],
            ["Expiring in 30 days", analytics?.cards.expiring_30_days ?? 0],
            ["Invalid attempts", analytics?.cards.invalid_verification_attempts ?? 0],
          ].map(([label, value]) => (
            <div key={label} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <Activity className="mb-3 text-brand-deep" size={18} />
              <p className="text-2xl font-bold text-slate-950">{value}</p>
              <p className="text-sm font-semibold text-slate-500">{label}</p>
            </div>
          ))}
        </section>

        <section className="grid gap-3">
          <div className="flex items-center gap-2"><BarChart3 className="text-brand-deep" size={18} /><h2 className="text-base font-bold text-slate-950">Issuance by state</h2></div>
          <DataTable
            columns={[
              { key: "state_name", header: "State", render: (row) => row.state_name },
              { key: "total", header: "Total", render: (row) => row.total },
              { key: "active", header: "Active", render: (row) => row.active },
              { key: "expired", header: "Expired", render: (row) => row.expired },
              { key: "suspended", header: "Suspended", render: (row) => row.suspended },
              { key: "revoked", header: "Revoked", render: (row) => row.revoked },
            ]}
            rows={analytics?.by_state ?? []}
            empty={analyticsQuery.isLoading ? "Loading state analytics..." : "No certificate analytics available."}
          />
        </section>

        <section className="grid gap-3">
          <div className="flex items-center gap-2"><AlertTriangle className="text-amber-700" size={18} /><h2 className="text-base font-bold text-slate-950">High-risk facilities</h2></div>
          <DataTable
            columns={[
              { key: "facility_name", header: "Facility", render: (row) => row.facility_name },
              { key: "state_name", header: "State", render: (row) => row.state_name },
              { key: "flagged", header: "Flags", render: (row) => row.flagged },
              { key: "suspended", header: "Suspended", render: (row) => row.suspended },
              { key: "revoked", header: "Revoked", render: (row) => row.revoked },
            ]}
            rows={analytics?.high_risk_facilities ?? []}
            empty={analyticsQuery.isLoading ? "Loading facility risks..." : "No high-risk facilities detected."}
          />
        </section>
      </div>
    </PortalShell>
  );
}
