"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, FileText, LayoutDashboard } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchFederalStatePerformance, type FederalStatePerformanceRow } from "@/lib/api/federal";

export default function Page() {
  const performanceQuery = useQuery({ queryKey: ["federal-state-performance"], queryFn: fetchFederalStatePerformance });
  const rows = performanceQuery.data?.states || [];

  return (
    <PortalShell role="federal_admin" title="National reports" description="Track official state report submission status and identify follow-up needs.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2"><FileText className="text-brand-700" size={18} /><h2 className="text-base font-bold text-neutral-900">State Submission Monitor</h2></div>
            <Link
              href="/federal/dashboard"
              className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700"
            >
              <LayoutDashboard size={16} />
              Open Dashboard Analytics
              <ArrowRight size={16} />
            </Link>
          </div>
          <p className="mt-3 text-sm text-neutral-500">Use Dashboard Analytics for workbook design, dataset plotting, and dashboard publishing. Reports stays focused on official report monitoring and submission follow-up.</p>
        </section>
        <DataTable<FederalStatePerformanceRow>
          columns={[
            { key: "state", header: "State", render: (row) => <Link className="font-bold text-brand-700" href={`/federal/states/${row.state_id}`}>{row.state_name}</Link> },
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
