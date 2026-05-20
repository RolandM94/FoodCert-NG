"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { FileText } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchFederalStatePerformance, type FederalStatePerformanceRow } from "@/lib/api/federal";

export default function Page() {
  const performanceQuery = useQuery({ queryKey: ["federal-state-performance"], queryFn: fetchFederalStatePerformance });
  const rows = performanceQuery.data?.states || [];

  return (
    <PortalShell role="federal_admin" title="National reports" description="Track official state report submission status and identify follow-up needs.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex items-center gap-2"><FileText className="text-brand-deep" size={18} /><h2 className="text-base font-bold text-slate-950">State Submission Monitor</h2></div>
        </section>
        <DataTable<FederalStatePerformanceRow>
          columns={[
            { key: "state", header: "State", render: (row) => <Link className="font-bold text-brand-deep" href={`/federal/states/${row.state_id}`}>{row.state_name}</Link> },
            { key: "status", header: "Latest report", render: (row) => <StatusCell status={row.latest_report_status} /> },
            { key: "period", header: "Period end", render: (row) => row.latest_report_period_end || "Not submitted" },
            { key: "quality", header: "Data quality", render: (row) => `${row.data_quality_score}%` },
            { key: "queues", header: "Open queues", render: (row) => row.pending_certificate_validations + row.pending_facility_applications },
          ]}
          rows={rows}
          empty={performanceQuery.isLoading ? "Loading report status..." : "No state report data found."}
        />
      </div>
    </PortalShell>
  );
}
