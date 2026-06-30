"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Clock3, FileText, RotateCcw, Send, ShieldAlert } from "lucide-react";
import { useMemo, useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { DashboardCard } from "@/components/ui/dashboard-card";
import { fetchStateReports, generateStateReport, submitStateReport, type StateReportItem } from "@/lib/api/state";
import { getApiErrorMessage } from "@/lib/api/client";

const REPORT_TYPES = [
  ["state_monthly", "State Monthly M&E"],
  ["inspection_outcomes", "Inspection Outcomes"],
  ["illness_trends", "Illness Exclusion Trends"],
  ["return_to_work_report", "Return-to-Work Clearance"],
  ["employer_exclusion_compliance", "Employer Exclusion Compliance"],
  ["rtw_overdue", "Return-to-Work Overdue"],
  ["exclusion_violation", "Exclusion Violation"],
  ["vaccination_coverage", "Vaccination Coverage"],
] as const;

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

function dateTimeLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

function reportTypeLabel(value: string) {
  return REPORT_TYPES.find(([key]) => key === value)?.[1] ?? value.replaceAll("_", " ");
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
  const metrics = useMemo(() => ({
    total: reports.length,
    draft: reports.filter((item) => ["draft", "generated"].includes(item.status)).length,
    submitted: reports.filter((item) => item.status === "submitted").length,
    returned: reports.filter((item) => item.status === "returned").length,
    accepted: reports.filter((item) => item.status === "accepted").length,
  }), [reports]);
  const latestSubmission = useMemo(
    () =>
      [...reports]
        .filter((item) => Boolean(item.submitted_at))
        .sort((a, b) => new Date(b.submitted_at || 0).getTime() - new Date(a.submitted_at || 0).getTime())[0],
    [reports],
  );

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
    <PortalShell role="state_admin" title="State Reports & M&E" description="Generate, review, and submit official state implementation reports to the Federal Ministry.">
      <div className="grid gap-5">
        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
          <DashboardCard icon={FileText} label="Report Drafts" value={metrics.draft} />
          <DashboardCard icon={Send} label="Submitted" value={metrics.submitted} />
          <DashboardCard icon={RotateCcw} label="Returned" value={metrics.returned} />
          <DashboardCard icon={CheckCircle2} label="Accepted" value={metrics.accepted} />
          <DashboardCard icon={Clock3} label="Total Reports" value={metrics.total} />
        </section>

        <section className="grid gap-4 xl:grid-cols-[1.05fr_0.95fr]">
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-700">State M&E Flow</p>
            <h2 className="mt-1 text-lg font-bold text-neutral-900">Prepare submission-ready ministry reports</h2>
            <p className="mt-2 max-w-3xl text-sm text-neutral-500">
              Generate a period report, review the output internally, submit it to Federal, and track whether it was accepted or returned for revision.
            </p>
            <div className="mt-4 grid gap-3 sm:grid-cols-4">
              {[
                ["1", "Generate", "Create a State report draft for the selected reporting period."],
                ["2", "Review", "Check indicators, operational counts, and any quality flags before submission."],
                ["3", "Submit", "Send the approved report to the Federal oversight layer."],
                ["4", "Track", "Monitor whether the report is accepted or returned for correction."],
              ].map(([step, title, detail]) => (
                <div key={step} className="rounded-lg border border-neutral-200 bg-neutral-50 px-4 py-3">
                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-700">Step {step}</p>
                  <p className="mt-2 text-sm font-bold text-neutral-900">{title}</p>
                  <p className="mt-1 text-sm text-neutral-500">{detail}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-700">Submission Watch</p>
            <h2 className="mt-1 text-lg font-bold text-neutral-900">Current reporting posture</h2>
            <div className="mt-4 grid gap-3">
              <div className={`rounded-lg border px-4 py-3 ${metrics.returned ? "border-warning-200 bg-warning-50" : "border-brand-200 bg-brand-50"}`}>
                <div className="flex items-center gap-2">
                  {metrics.returned ? <ShieldAlert size={16} className="text-warning-700" /> : <CheckCircle2 size={16} className="text-brand-700" />}
                  <p className={`text-sm font-bold ${metrics.returned ? "text-warning-900" : "text-brand-900"}`}>
                    {metrics.returned ? "Returned reports need attention" : "No returned reports currently open"}
                  </p>
                </div>
                <p className={`mt-2 text-sm ${metrics.returned ? "text-warning-800" : "text-brand-800"}`}>
                  {metrics.returned
                    ? `${metrics.returned} report${metrics.returned === 1 ? "" : "s"} require revision before the next submission cycle can be closed.`
                    : "State reporting is clear of returned submissions right now."}
                </p>
              </div>
              <div className="rounded-lg border border-neutral-200 bg-neutral-50 px-4 py-3">
                <p className="text-sm font-bold text-neutral-900">Latest submission</p>
                <p className="mt-2 text-sm text-neutral-600">
                  {latestSubmission
                    ? `${reportTypeLabel(latestSubmission.report_type)} submitted ${dateTimeLabel(latestSubmission.submitted_at)}.`
                    : "No state report has been submitted yet."}
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="mb-4">
            <p className="text-sm font-bold text-neutral-900">Generate report draft</p>
            <p className="mt-1 text-sm text-neutral-500">Use this to prepare the State Ministry submission draft for internal review and Federal forwarding.</p>
          </div>
          <div className="grid gap-3 xl:grid-cols-[220px_170px_170px_auto]">
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={reportType} onChange={(event) => setReportType(event.target.value)}>
              {REPORT_TYPES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" type="date" value={periodStart} onChange={(event) => setPeriodStart(event.target.value)} />
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" type="date" value={periodEnd} onChange={(event) => setPeriodEnd(event.target.value)} />
            <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-700 px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-neutral-300" disabled={generateMutation.isPending} onClick={() => generateMutation.mutate()} type="button">
              <FileText size={16} />
              {generateMutation.isPending ? "Generating..." : "Generate report"}
            </button>
          </div>
          {generateMutation.isError ? (
            <p className="mt-3 rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">
              {getApiErrorMessage(generateMutation.error, "Could not generate the state report.")}
            </p>
          ) : null}
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="mb-4">
            <p className="text-sm font-bold text-neutral-900">Submission register</p>
            <p className="mt-1 text-sm text-neutral-500">Track draft, submitted, returned, and accepted reports across reporting periods.</p>
          </div>
          <div className="grid gap-3 md:grid-cols-[220px_1fr]">
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
              <option value="">All report statuses</option>
              <option value="draft">Draft</option>
              <option value="generated">Generated</option>
              <option value="submitted">Submitted</option>
              <option value="returned">Returned</option>
              <option value="accepted">Accepted</option>
            </select>
          </div>
        </section>

        {reportsQuery.isError ? (
          <p className="rounded bg-danger-50 p-3 text-sm font-semibold text-danger-700">
            {getApiErrorMessage(reportsQuery.error, "Could not load state reports.")}
          </p>
        ) : null}

        <DataTable<StateReportItem>
          columns={[
            {
              key: "report",
              header: "Report",
              render: (row) => (
                <div>
                  <p className="font-bold text-neutral-900">{reportTypeLabel(row.report_type)}</p>
                  <p className="text-xs text-neutral-500">{dateLabel(row.reporting_period_start)} - {dateLabel(row.reporting_period_end)}</p>
                </div>
              ),
            },
            { key: "state", header: "State", render: (row) => row.state_name || "State" },
            { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
            {
              key: "generated",
              header: "Generated by",
              render: (row) => (
                <div>
                  <p className="font-semibold text-neutral-900">{row.generated_by_name || "System"}</p>
                  <p className="text-xs text-neutral-500">{dateTimeLabel(row.created_at)}</p>
                </div>
              ),
            },
            {
              key: "submitted",
              header: "Submitted / Reviewed",
              render: (row) => (
                <div>
                  <p className="font-semibold text-neutral-900">{row.submitted_at ? dateTimeLabel(row.submitted_at) : "Not submitted"}</p>
                  <p className="text-xs text-neutral-500">
                    {row.reviewed_at
                      ? `Reviewed ${dateTimeLabel(row.reviewed_at)}`
                      : row.review_comment
                        ? "Review comment available"
                        : "Awaiting Federal review"}
                  </p>
                </div>
              ),
            },
            {
              key: "comment",
              header: "Review note",
              render: (row) => row.review_comment || "No review note",
            },
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

        {submitMutation.isError ? (
          <p className="rounded bg-danger-50 p-3 text-sm font-semibold text-danger-700">
            {getApiErrorMessage(submitMutation.error, "Could not submit the state report.")}
          </p>
        ) : null}
      </div>
    </PortalShell>
  );
}
