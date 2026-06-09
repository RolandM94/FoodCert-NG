"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { BarChart3, ClipboardList, ShieldCheck } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchFederalStateSummary } from "@/lib/api/federal";

function numberLabel(value?: number) {
  return new Intl.NumberFormat("en-NG").format(value || 0);
}

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const params = useParams<{ id: string }>();
  const summaryQuery = useQuery({
    queryKey: ["federal-state-summary", params.id],
    queryFn: () => fetchFederalStateSummary(params.id),
    enabled: Boolean(params.id),
  });
  const summary = summaryQuery.data;
  const state = summary?.state;

  return (
    <PortalShell role="federal_admin" title={state?.state_name || "State summary"} description="Privacy-safe federal drill-down for state performance, reporting status, queues, and data quality.">
      {!state ? (
        <div className="rounded-lg border border-dashed border-neutral-300 bg-white p-6 text-sm text-neutral-600">
          {summaryQuery.isLoading ? "Loading state summary..." : "State summary not found."}
        </div>
      ) : (
        <div className="grid gap-5">
          <section className="grid gap-3 md:grid-cols-4">
            {[
              ["Registered handlers", numberLabel(state.registered_handlers), ShieldCheck],
              ["Certification coverage", `${state.certification_coverage}%`, BarChart3],
              ["Open validations", numberLabel(state.pending_certificate_validations), ClipboardList],
              ["Data quality", `${state.data_quality_score}%`, BarChart3],
            ].map(([label, value, Icon]) => (
              <div key={label as string} className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
                <div className="mb-2 flex items-center gap-2 text-brand-700"><Icon size={16} /><p className="text-xs font-bold uppercase text-neutral-500">{label as string}</p></div>
                <p className="text-xl font-bold text-neutral-900">{value as string}</p>
              </div>
            ))}
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <h2 className="mb-4 text-base font-bold text-neutral-900">Operational Summary</h2>
              <div className="grid gap-3 text-sm">
                <div className="flex justify-between gap-3"><span className="text-neutral-600">Approved facilities</span><strong>{numberLabel(state.approved_facilities)}</strong></div>
                <div className="flex justify-between gap-3"><span className="text-neutral-600">Pending facility applications</span><strong>{numberLabel(state.pending_facility_applications)}</strong></div>
                <div className="flex justify-between gap-3"><span className="text-neutral-600">Inspections</span><strong>{numberLabel(state.inspection_count)}</strong></div>
                <div className="flex justify-between gap-3"><span className="text-neutral-600">Illness reports</span><strong>{numberLabel(state.illness_reports)}</strong></div>
                <div className="flex justify-between gap-3"><span className="text-neutral-600">Latest report</span><StatusCell status={state.latest_report_status} /></div>
              </div>
            </div>

            <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <h2 className="mb-4 text-base font-bold text-neutral-900">Privacy Boundary</h2>
              <p className="text-sm leading-6 text-neutral-600">
                Federal drill-downs show aggregate implementation and reporting metrics only. Food handler identity, clinical details, NIN, date of birth, symptoms, and notes are not returned here.
              </p>
            </div>
          </section>

          <DataTable
            columns={[
              { key: "type", header: "Report", render: (row) => <span className="font-bold text-neutral-900">{row.report_type.replaceAll("_", " ")}</span> },
              { key: "period", header: "Period", render: (row) => `${dateLabel(row.reporting_period_start)} - ${dateLabel(row.reporting_period_end)}` },
              { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
              { key: "submitted", header: "Submitted", render: (row) => dateLabel(row.submitted_at) },
            ]}
            rows={summary.reports}
            empty="No state reports submitted yet."
          />
        </div>
      )}
    </PortalShell>
  );
}
