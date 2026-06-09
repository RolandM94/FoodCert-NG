"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchFederalDataQuality, type FederalDataQualityRisk } from "@/lib/api/federal";

export default function Page() {
  const qualityQuery = useQuery({ queryKey: ["federal-data-quality"], queryFn: fetchFederalDataQuality });
  const rows = qualityQuery.data?.risks || [];

  return (
    <PortalShell role="federal_admin" title="Data quality" description="Review national data quality risks across reports, coverage, queues, and metadata completeness.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="flex items-center gap-2 text-brand-700"><AlertTriangle size={18} /><h2 className="text-base font-bold text-neutral-900">{qualityQuery.data?.cards.risk_count || 0} open quality risks</h2></div>
        </section>
        <DataTable<FederalDataQualityRisk>
          columns={[
            { key: "state", header: "State", render: (row) => <span className="font-bold text-neutral-900">{row.state_name}</span> },
            { key: "risk", header: "Risk", render: (row) => row.risk.replaceAll("_", " ") },
            { key: "severity", header: "Severity", render: (row) => <StatusCell status={row.severity} /> },
            { key: "detail", header: "Detail", render: (row) => row.detail },
          ]}
          rows={rows}
          empty={qualityQuery.isLoading ? "Loading quality risks..." : "No data quality risks found."}
        />
      </div>
    </PortalShell>
  );
}
