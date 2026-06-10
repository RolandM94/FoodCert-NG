"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileText, Send } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchStateReports, generateStateReport, submitStateReport, type StateReportItem } from "@/lib/api/state";

function defaultMonthStart() {
  const date = new Date();
  return new Date(date.getFullYear(), date.getMonth(), 1).toISOString().slice(0, 10);
}

function defaultToday() {
  return new Date().toISOString().slice(0, 10);
}

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const queryClient = useQueryClient();
  const [reportType, setReportType] = useState("state_monthly");
  const [periodStart, setPeriodStart] = useState(defaultMonthStart());
  const [periodEnd, setPeriodEnd] = useState(defaultToday());
  const [status, setStatus] = useState("");

  const reportsQuery = useQuery({
    queryKey: ["state-reports", status],
    queryFn: () => fetchStateReports({ status }),
  });
  const reports = reportsQuery.data || [];

  const generateMutation = useMutation({
    mutationFn: () =>
      generateStateReport({
        report_type: reportType,
        reporting_period_start: periodStart,
        reporting_period_end: periodEnd,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["state-reports"] }),
  });

  const submitMutation = useMutation({
    mutationFn: submitStateReport,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["state-reports"] }),
  });

  return (
    <PortalShell role="state_admin" title="State reports" description="Generate official state compliance and finance reports for federal submission.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 xl:grid-cols-[220px_170px_170px_auto]">
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={reportType} onChange={(event) => setReportType(event.target.value)}>
              <option value="state_monthly">State monthly</option>
              <option value="inspection_outcomes">Inspection outcomes</option>
              <option value="illness_trends">Illness exclusion report</option>
              <option value="return_to_work_report">Return-to-work clearance report</option>
              <option value="employer_exclusion_compliance">Employer exclusion compliance report</option>
              <option value="rtw_overdue">RTW overdue report</option>
              <option value="exclusion_violation">Exclusion violation report</option>
              <option value="vaccination_coverage">Vaccination coverage</option>
            </select>
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" type="date" value={periodStart} onChange={(event) => setPeriodStart(event.target.value)} />
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" type="date" value={periodEnd} onChange={(event) => setPeriodEnd(event.target.value)} />
            <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-700 px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-neutral-300" disabled={generateMutation.isPending} onClick={() => generateMutation.mutate()} type="button">
              <FileText size={16} />
              {generateMutation.isPending ? "Generating..." : "Generate report"}
            </button>
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[220px_1fr]">
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
              <option value="">All report statuses</option>
              <option value="generated">Generated</option>
              <option value="submitted">Submitted</option>
              <option value="returned">Returned</option>
              <option value="accepted">Accepted</option>
            </select>
          </div>
        </section>

        <DataTable<StateReportItem>
          columns={[
            { key: "report", header: "Report", render: (row) => <div><p className="font-bold text-neutral-900">{row.report_type.replaceAll("_", " ")}</p><p className="text-xs text-neutral-500">{dateLabel(row.reporting_period_start)} - {dateLabel(row.reporting_period_end)}</p></div> },
            { key: "state", header: "State", render: (row) => row.state_name || "State" },
            { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
            { key: "generated", header: "Generated by", render: (row) => row.generated_by_name || "System" },
            { key: "submitted", header: "Submitted", render: (row) => row.submitted_at ? dateLabel(row.submitted_at) : "Not submitted" },
            {
              key: "action",
              header: "Action",
              render: (row) => (
                <button
                  className="inline-flex h-9 items-center gap-2 rounded border border-brand-700 px-3 text-xs font-semibold text-brand-700 disabled:cursor-not-allowed disabled:border-neutral-300 disabled:text-neutral-400"
                  disabled={!["draft", "generated", "returned"].includes(row.status) || submitMutation.isPending}
                  onClick={() => submitMutation.mutate(row.id)}
                  type="button"
                >
                  <Send size={14} />
                  Submit
                </button>
              ),
            },
          ]}
          rows={reports}
          empty={reportsQuery.isLoading ? "Loading state reports..." : "No state reports yet."}
        />
      </div>
    </PortalShell>
  );
}
