"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Activity, Building2, ClipboardCheck, MapPinned, ShieldCheck, UsersRound, type LucideIcon } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchFederalStatePerformance, type FederalStatePerformanceRow } from "@/lib/api/federal";

function numberLabel(value?: number) {
  return new Intl.NumberFormat("en-NG").format(value || 0);
}

export default function Page() {
  const performanceQuery = useQuery({ queryKey: ["federal-state-performance"], queryFn: fetchFederalStatePerformance });
  const payload = performanceQuery.data;
  const states = payload?.states || [];
  const totals = payload?.totals;
  const metricCards: Array<[string, string | number | undefined, LucideIcon]> = [
    ["States/FCT", totals?.states, MapPinned],
    ["Handlers", totals?.registered_handlers, UsersRound],
    ["Certified", totals?.certified_handlers, ShieldCheck],
    ["Coverage", `${totals?.certification_coverage || 0}%`, Activity],
    ["Facilities", totals?.approved_facilities, Building2],
    ["Inspections", totals?.inspection_count, ClipboardCheck],
  ];

  return (
    <PortalShell role="federal_admin" title="Federal dashboard" description="National oversight of certification coverage, facilities, inspections, reporting, and state performance.">
      <div className="grid gap-5">
        <section className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
          {metricCards.map(([label, value, Icon]) => (
            <div key={label} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <div className="mb-2 flex items-center gap-2 text-brand-deep"><Icon size={16} /><p className="text-xs font-bold uppercase text-slate-500">{label}</p></div>
              <p className="text-xl font-bold text-slate-950">{typeof value === "number" ? numberLabel(value) : value}</p>
            </div>
          ))}
        </section>

        <section className="grid gap-3">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-base font-bold text-slate-950">State Performance</h2>
            <Link className="rounded border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700" href="/federal/states">View all states</Link>
          </div>
          <DataTable<FederalStatePerformanceRow>
            columns={[
              { key: "state", header: "State", render: (row) => <Link className="font-bold text-brand-deep" href={`/federal/states/${row.state_id}`}>{row.state_name}{row.is_fct ? " (FCT)" : ""}</Link> },
              { key: "handlers", header: "Handlers", render: (row) => numberLabel(row.registered_handlers) },
              { key: "coverage", header: "Coverage", render: (row) => `${row.certification_coverage}%` },
              { key: "facilities", header: "Facilities", render: (row) => numberLabel(row.approved_facilities) },
              { key: "queues", header: "Open queues", render: (row) => numberLabel(row.pending_facility_applications + row.pending_certificate_validations) },
              { key: "report", header: "Report", render: (row) => <StatusCell status={row.latest_report_status} /> },
              { key: "quality", header: "Data quality", render: (row) => `${row.data_quality_score}%` },
            ]}
            rows={states.slice(0, 10)}
            empty={performanceQuery.isLoading ? "Loading state performance..." : "No states configured yet."}
          />
        </section>
      </div>
    </PortalShell>
  );
}
