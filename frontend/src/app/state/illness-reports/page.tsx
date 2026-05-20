"use client";

import { useQuery } from "@tanstack/react-query";
import { Download, HeartPulse } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchStateIllnessReports, type StateIllnessMonitoringItem } from "@/lib/api/state";
import { downloadCsv } from "@/lib/export/csv";

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const [clearanceStatus, setClearanceStatus] = useState("");
  const [activeOnly, setActiveOnly] = useState(true);
  const illnessQuery = useQuery({
    queryKey: ["state-illness-monitoring", clearanceStatus, activeOnly],
    queryFn: () => fetchStateIllnessReports({ clearance_status: clearanceStatus, active: activeOnly ? "true" : "" }),
  });
  const rows = illnessQuery.data || [];

  return (
    <PortalShell role="state_admin" title="Illness reports" description="Monitor illness exclusions and return-to-work clearance without exposing private clinical notes.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[220px_auto_1fr_auto]">
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={clearanceStatus} onChange={(event) => setClearanceStatus(event.target.value)}>
              <option value="">All clearance statuses</option>
              <option value="pending">Pending</option>
              <option value="under_review">Under review</option>
              <option value="clearance_required">Clearance required</option>
              <option value="cleared">Cleared</option>
              <option value="rejected">Rejected</option>
            </select>
            <label className="inline-flex h-10 items-center gap-2 text-sm font-semibold text-slate-700">
              <input checked={activeOnly} onChange={(event) => setActiveOnly(event.target.checked)} type="checkbox" />
              Active only
            </label>
            <span />
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-deep px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300"
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
          <div className="flex items-center gap-2"><HeartPulse className="text-brand-deep" size={18} /><h2 className="text-base font-bold text-slate-950">Illness & Return-to-Work Monitoring</h2></div>
          <DataTable<StateIllnessMonitoringItem>
            columns={[
              { key: "handler", header: "Handler", render: (row) => <div><p className="font-bold text-slate-950">{row.food_handler_name}</p><p className="text-xs text-slate-500">{row.food_handler_category?.replaceAll("_", " ")}</p></div> },
              { key: "employer", header: "Employer", render: (row) => row.employer_name || "Not linked" },
              { key: "lga", header: "LGA", render: (row) => row.lga_name || "Not set" },
              { key: "condition", header: "Public health flag", render: (row) => row.suspected_condition?.replaceAll("_", " ") || "Not specified" },
              { key: "exclusion", header: "Exclusion start", render: (row) => dateLabel(row.exclusion_start_date) },
              { key: "return", header: "Earliest return", render: (row) => dateLabel(row.earliest_return_date) },
              { key: "status", header: "Clearance", render: (row) => <StatusCell status={row.clearance_status} /> },
            ]}
            rows={rows}
            empty={illnessQuery.isLoading ? "Loading illness reports..." : "No illness reports match the current filters."}
          />
        </section>
      </div>
    </PortalShell>
  );
}
