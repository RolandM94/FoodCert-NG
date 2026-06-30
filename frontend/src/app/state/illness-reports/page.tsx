"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Download, HeartPulse } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable } from "@/components/ui/data-table";
import { IllnessExclusionStatusBadge, ReturnToWorkStatusBadge } from "@/components/ui/illness-status-badges";
import { fetchStateIllnessReports, type StateIllnessMonitoringItem } from "@/lib/api/state";
import { downloadCsv } from "@/lib/export/csv";

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

function StateIllnessReportsPageContent() {
  const searchParams = useSearchParams();
  const [clearanceStatus, setClearanceStatus] = useState("");
  const [exceptionFilter, setExceptionFilter] = useState(searchParams.get("filter") || "active_exclusions");
  const activeOnly = exceptionFilter !== "all";
  const illnessQuery = useQuery({
    queryKey: ["state-illness-monitoring", clearanceStatus, activeOnly],
    queryFn: () => fetchStateIllnessReports({ clearance_status: clearanceStatus, active: activeOnly ? "true" : "" }),
  });
  const sourceRows = illnessQuery.data || [];
  const today = new Date(new Date().toDateString());
  const rows = sourceRows.filter((row) => {
    if (exceptionFilter === "overdue") {
      return Boolean(row.earliest_return_date && !["cleared", "rejected"].includes(row.clearance_status) && new Date(row.earliest_return_date) < today);
    }
    if (exceptionFilter === "public_health") return row.clearance_required || row.clearance_status === "clearance_required";
    return true;
  });

  return (
    <PortalShell role="state_admin" title="Illness & RTW Exceptions" description="Review oversight signals for active exclusions, overdue clearances, and public-health exceptions without exposing clinical notes.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-warning-100 bg-warning-50 p-4 text-sm font-semibold text-warning-800">
          <div className="flex items-start gap-2">
            <AlertTriangle className="mt-0.5 shrink-0" size={16} />
            <p>State users see exception and reporting signals only. Employers manage exclusions operationally, and medical facilities or doctors handle clearance decisions.</p>
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[220px_220px_1fr_auto]">
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={exceptionFilter} onChange={(event) => setExceptionFilter(event.target.value)}>
              <option value="active_exclusions">Active exclusions</option>
              <option value="overdue">Overdue RTW clearance</option>
              <option value="public_health">Public health clearance</option>
              <option value="all">All report signals</option>
            </select>
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={clearanceStatus} onChange={(event) => setClearanceStatus(event.target.value)}>
              <option value="">All clearance statuses</option>
              <option value="pending">Pending</option>
              <option value="under_review">Under review</option>
              <option value="clearance_required">Clearance required</option>
              <option value="cleared">Cleared</option>
              <option value="rejected">Rejected</option>
            </select>
            <span />
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-700 px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-neutral-300"
              disabled={!rows.length}
              onClick={() =>
                downloadCsv("state-illness-monitoring.csv", rows, [
                  { header: "Handler", value: (row) => row.food_handler_name },
                  { header: "Category", value: (row) => row.food_handler_category },
                  { header: "Employer", value: (row) => row.employer_name },
                  { header: "LGA", value: (row) => row.lga_name },
                  { header: "Public health flag", value: (row) => row.suspected_condition },
                  { header: "Exclusion start", value: (row) => row.exclusion_start_date },
                  { header: "Earliest return", value: (row) => row.earliest_return_date },
                  { header: "Clearance required", value: (row) => row.clearance_required },
                  { header: "Clearance status", value: (row) => row.clearance_status },
                  { header: "Cleared at", value: (row) => row.cleared_at },
                  { header: "Return-to-work certificate", value: (row) => row.return_to_work_certificate_number },
                ])
              }
              type="button"
            >
              <Download size={16} />
              Export
            </button>
          </div>
        </section>
        <section className="grid gap-3">
          <div className="flex items-center gap-2"><HeartPulse className="text-brand-700" size={18} /><h2 className="text-base font-bold text-neutral-900">Exception Queue</h2></div>
          <DataTable<StateIllnessMonitoringItem>
            columns={[
              { key: "handler", header: "Handler", render: (row) => <div><p className="font-bold text-neutral-900">{row.food_handler_name}</p><p className="text-xs text-neutral-500">{row.food_handler_category?.replaceAll("_", " ")}</p></div> },
              { key: "employer", header: "Employer", render: (row) => row.employer_name || "Not linked" },
              { key: "lga", header: "LGA", render: (row) => row.lga_name || "Not set" },
              { key: "condition", header: "Public health flag", render: (row) => row.suspected_condition?.replaceAll("_", " ") || "Not specified" },
              { key: "exclusion", header: "Exclusion start", render: (row) => dateLabel(row.exclusion_start_date) },
              { key: "return", header: "Earliest return", render: (row) => dateLabel(row.earliest_return_date) },
              { key: "exclusion_status", header: "Exclusion", render: (row) => <IllnessExclusionStatusBadge status={row.clearance_status} /> },
              { key: "rtw_status", header: "Return-to-work", render: (row) => <ReturnToWorkStatusBadge status={row.clearance_status} earliestReturnDate={row.earliest_return_date} /> },
            ]}
            rows={rows}
            empty={illnessQuery.isLoading ? "Loading exception signals..." : "No illness or return-to-work exception signals match the current filters."}
          />
        </section>
      </div>
    </PortalShell>
  );
}

export default function Page() {
  return (
    <Suspense fallback={null}>
      <StateIllnessReportsPageContent />
    </Suspense>
  );
}
