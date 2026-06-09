"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Download, MapPinned } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchFederalStatePerformance, type FederalStatePerformanceRow } from "@/lib/api/federal";
import { downloadCsv } from "@/lib/export/csv";

function numberLabel(value?: number) {
  return new Intl.NumberFormat("en-NG").format(value || 0);
}

export default function Page() {
  const performanceQuery = useQuery({ queryKey: ["federal-state-performance"], queryFn: fetchFederalStatePerformance });
  const rows = performanceQuery.data?.states || [];

  return (
    <PortalShell role="federal_admin" title="States" description="Compare state implementation, federal reporting, open queues, and data quality.">
      <div className="grid gap-5">
        <section className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="flex items-center gap-2">
            <MapPinned className="text-brand-700" size={18} />
            <h2 className="text-base font-bold text-neutral-900">National State Performance Table</h2>
          </div>
          <button
            className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-700 px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-neutral-300"
            disabled={!rows.length}
            onClick={() =>
              downloadCsv("federal-state-performance.csv", rows, [
                { header: "State", value: (row) => row.state_name },
                { header: "Code", value: (row) => row.state_code },
                { header: "FCT", value: (row) => row.is_fct },
                { header: "Registered handlers", value: (row) => row.registered_handlers },
                { header: "Certified handlers", value: (row) => row.certified_handlers },
                { header: "Coverage", value: (row) => row.certification_coverage },
                { header: "Approved facilities", value: (row) => row.approved_facilities },
                { header: "Pending facility applications", value: (row) => row.pending_facility_applications },
                { header: "Pending certificate validations", value: (row) => row.pending_certificate_validations },
                { header: "Inspections", value: (row) => row.inspection_count },
                { header: "Illness reports", value: (row) => row.illness_reports },
                { header: "Latest report", value: (row) => row.latest_report_status },
                { header: "Data quality", value: (row) => row.data_quality_score },
              ])
            }
            type="button"
          >
            <Download size={16} />
            Export
          </button>
        </section>

        <DataTable<FederalStatePerformanceRow>
          columns={[
            { key: "state", header: "State", render: (row) => <Link className="font-bold text-brand-700" href={`/federal/states/${row.state_id}`}>{row.state_name}{row.is_fct ? " (FCT)" : ""}</Link> },
            { key: "handlers", header: "Handlers", render: (row) => numberLabel(row.registered_handlers) },
            { key: "certified", header: "Certified", render: (row) => numberLabel(row.certified_handlers) },
            { key: "coverage", header: "Coverage", render: (row) => `${row.certification_coverage}%` },
            { key: "facilities", header: "Facilities", render: (row) => numberLabel(row.approved_facilities) },
            { key: "validations", header: "Validations", render: (row) => numberLabel(row.pending_certificate_validations) },
            { key: "inspections", header: "Inspections", render: (row) => numberLabel(row.inspection_count) },
            { key: "report", header: "Report", render: (row) => <StatusCell status={row.latest_report_status} /> },
            { key: "quality", header: "Data quality", render: (row) => `${row.data_quality_score}%` },
          ]}
          rows={rows}
          empty={performanceQuery.isLoading ? "Loading states..." : "No states configured yet."}
        />
      </div>
    </PortalShell>
  );
}
