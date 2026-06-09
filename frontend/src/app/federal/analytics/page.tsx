"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, ClipboardList, ShieldCheck, type LucideIcon } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchFederalIndicators, type FederalStatePerformanceRow } from "@/lib/api/federal";

export default function Page() {
  const indicatorsQuery = useQuery({ queryKey: ["federal-indicators"], queryFn: fetchFederalIndicators });
  const cards = indicatorsQuery.data?.cards || {};
  const lowCoverage = indicatorsQuery.data?.sections.low_coverage_states || [];
  const qualityRisks = indicatorsQuery.data?.sections.top_data_quality_risks || [];
  const metricCards: Array<[string, string | number | undefined, LucideIcon]> = [
    ["States", cards.states_monitored, Activity],
    ["Coverage", `${cards.national_certification_coverage || 0}%`, ShieldCheck],
    ["Low coverage", cards.low_coverage_states, AlertTriangle],
    ["Missing reports", cards.missing_reports, ClipboardList],
    ["Cert validations", cards.open_certificate_validations, ClipboardList],
    ["Facility apps", cards.open_facility_applications, ClipboardList],
  ];

  return (
    <PortalShell role="federal_admin" title="Analytics" description="Monitor national M&E indicators, coverage risks, report gaps, and data quality trends.">
      <div className="grid gap-5">
        <section className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
          {metricCards.map(([label, value, Icon]) => (
            <div key={label} className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="mb-2 flex items-center gap-2 text-brand-700"><Icon size={16} /><p className="text-xs font-bold uppercase text-neutral-500">{label}</p></div>
              <p className="text-xl font-bold text-neutral-900">{String(value ?? 0)}</p>
            </div>
          ))}
        </section>

        <section className="grid gap-5 xl:grid-cols-2">
          <div className="grid gap-3">
            <h2 className="text-base font-bold text-neutral-900">Low Certification Coverage</h2>
            <DataTable<FederalStatePerformanceRow>
              columns={[
                { key: "state", header: "State", render: (row) => row.state_name },
                { key: "coverage", header: "Coverage", render: (row) => `${row.certification_coverage}%` },
                { key: "handlers", header: "Handlers", render: (row) => row.registered_handlers },
                { key: "report", header: "Report", render: (row) => <StatusCell status={row.latest_report_status} /> },
              ]}
              rows={lowCoverage}
              empty={indicatorsQuery.isLoading ? "Loading indicators..." : "No low coverage states."}
            />
          </div>
          <div className="grid gap-3">
            <h2 className="text-base font-bold text-neutral-900">Data Quality Watchlist</h2>
            <DataTable<FederalStatePerformanceRow>
              columns={[
                { key: "state", header: "State", render: (row) => row.state_name },
                { key: "quality", header: "Data quality", render: (row) => `${row.data_quality_score}%` },
                { key: "queues", header: "Open queues", render: (row) => row.pending_certificate_validations + row.pending_facility_applications },
                { key: "report", header: "Report", render: (row) => <StatusCell status={row.latest_report_status} /> },
              ]}
              rows={qualityRisks}
              empty={indicatorsQuery.isLoading ? "Loading quality risks..." : "No data quality watchlist items."}
            />
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
