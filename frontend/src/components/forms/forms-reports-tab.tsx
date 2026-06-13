"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { BarChart3, ClipboardCheck, FileStack, Percent, TrendingUp } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { DashboardCard } from "@/components/ui/dashboard-card";
import { StatusBadge } from "@/components/status/status-badge";
import { fetchFormAssignments, fetchFormsAnalytics, fetchFormTemplates } from "@/lib/api/forms";

const STATUS_COLORS: Record<string, string> = {
  not_started: "#94a3b8",
  draft: "#d4d4d8",
  in_progress: "#60a5fa",
  submitted: "#38bdf8",
  reviewed: "#34d399",
  approved: "#22c55e",
  returned: "#fbbf24",
  rejected: "#f87171",
  overdue: "#ef4444",
  cancelled: "#a1a1aa",
  sync_pending: "#a78bfa",
  sync_failed: "#fb923c",
};

const SCORE_COLORS = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#10b981"];
const RISK_COLORS: Record<string, string> = {
  low: "#22c55e",
  medium: "#eab308",
  high: "#f97316",
  critical: "#ef4444",
};

const PURPOSE_OPTIONS = [
  { value: "", label: "All purposes" },
  { value: "inspection_checklist", label: "Inspection Checklist" },
  { value: "employer_data_collection", label: "Employer Data Collection" },
  { value: "employer_compliance", label: "Employer Compliance" },
  { value: "facility_data_collection", label: "Facility Data Collection" },
  { value: "facility_monthly_report", label: "Facility Monthly Report" },
  { value: "accreditation_checklist", label: "Accreditation Checklist" },
  { value: "food_handler_survey", label: "Food Handler Survey" },
  { value: "food_handler_declaration", label: "Food Handler Declaration" },
  { value: "incident_report", label: "Incident Report" },
  { value: "training_feedback", label: "Training Feedback" },
  { value: "general_data_collection", label: "General Data Collection" },
];

const STATUS_OPTIONS = [
  { value: "", label: "All statuses" },
  { value: "not_started", label: "Not started" },
  { value: "draft", label: "Draft" },
  { value: "in_progress", label: "In progress" },
  { value: "submitted", label: "Submitted" },
  { value: "reviewed", label: "Reviewed" },
  { value: "returned", label: "Returned" },
  { value: "overdue", label: "Overdue" },
];

const PRIMARY_MODULE_OPTIONS = [
  { value: "", label: "All modules" },
  { value: "inspections", label: "Inspections" },
  { value: "employers", label: "Employers" },
  { value: "facilities", label: "Facilities" },
  { value: "accreditation", label: "Accreditation" },
  { value: "food_handlers", label: "Food Handlers" },
  { value: "reports", label: "Reports" },
  { value: "compliance", label: "Compliance" },
  { value: "training", label: "Training" },
  { value: "incidents", label: "Incidents" },
  { value: "general", label: "General" },
];

function formatLabel(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function FormsReportsTab() {
  const [templateFilter, setTemplateFilter] = useState("");
  const [assignmentFilter, setAssignmentFilter] = useState("");
  const [purposeFilter, setPurposeFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [primaryModuleFilter, setPrimaryModuleFilter] = useState("");
  const [contextTypeFilter, setContextTypeFilter] = useState("");
  const [organizationFilter, setOrganizationFilter] = useState("");
  const [stateFilter, setStateFilter] = useState("");
  const [lgaFilter, setLgaFilter] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const params: Record<string, string> = {};
  if (templateFilter) params.template = templateFilter;
  if (assignmentFilter) params.assignment = assignmentFilter;
  if (purposeFilter) params.purpose = purposeFilter;
  if (statusFilter) params.status = statusFilter;
  if (primaryModuleFilter) params.primary_module = primaryModuleFilter;
  if (contextTypeFilter) params.context_type = contextTypeFilter;
  if (organizationFilter) params.organization = organizationFilter;
  if (stateFilter) params.state = stateFilter;
  if (lgaFilter) params.lga = lgaFilter;
  if (dateFrom) params.date_from = dateFrom;
  if (dateTo) params.date_to = dateTo;

  const analyticsQuery = useQuery({
    queryKey: ["forms-analytics", params],
    queryFn: () => fetchFormsAnalytics(params),
  });

  const templatesQuery = useQuery({
    queryKey: ["forms-report-templates"],
    queryFn: () => fetchFormTemplates(),
  });
  const assignmentsQuery = useQuery({
    queryKey: ["forms-report-assignments"],
    queryFn: () => fetchFormAssignments(),
  });

  const data = analyticsQuery.data;
  const summary = data?.summary;

  return (
    <div className="grid gap-5">
      <div className="grid gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm md:grid-cols-2 xl:grid-cols-4">
        <div className="grid gap-1">
          <label className="text-xs font-semibold text-neutral-500">Template</label>
          <select className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" value={templateFilter} onChange={(e) => setTemplateFilter(e.target.value)}>
            <option value="">All templates</option>
            {(templatesQuery.data || []).map((t) => <option key={t.id} value={t.id}>{t.title}</option>)}
          </select>
        </div>
        <div className="grid gap-1">
          <label className="text-xs font-semibold text-neutral-500">Assignment</label>
          <select className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" value={assignmentFilter} onChange={(e) => setAssignmentFilter(e.target.value)}>
            <option value="">All assignments</option>
            {(assignmentsQuery.data || []).map((a) => <option key={a.id} value={a.id}>{a.title}</option>)}
          </select>
        </div>
        <div className="grid gap-1">
          <label className="text-xs font-semibold text-neutral-500">Purpose</label>
          <select className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" value={purposeFilter} onChange={(e) => setPurposeFilter(e.target.value)}>
            {PURPOSE_OPTIONS.map((o) => <option key={o.value || "all"} value={o.value}>{o.label}</option>)}
          </select>
        </div>
        <div className="grid gap-1">
          <label className="text-xs font-semibold text-neutral-500">Status</label>
          <select className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            {STATUS_OPTIONS.map((o) => <option key={o.value || "all"} value={o.value}>{o.label}</option>)}
          </select>
        </div>
        <div className="grid gap-1">
          <label className="text-xs font-semibold text-neutral-500">Module</label>
          <select className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" value={primaryModuleFilter} onChange={(e) => setPrimaryModuleFilter(e.target.value)}>
            {PRIMARY_MODULE_OPTIONS.map((o) => <option key={o.value || "all"} value={o.value}>{o.label}</option>)}
          </select>
        </div>
        <div className="grid gap-1">
          <label className="text-xs font-semibold text-neutral-500">Context type</label>
          <input className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" placeholder="inspection, employer, facility..." value={contextTypeFilter} onChange={(e) => setContextTypeFilter(e.target.value)} />
        </div>
        <div className="grid gap-1">
          <label className="text-xs font-semibold text-neutral-500">Organization ID</label>
          <input className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" placeholder="Optional organization id" value={organizationFilter} onChange={(e) => setOrganizationFilter(e.target.value)} />
        </div>
        <div className="grid gap-1">
          <label className="text-xs font-semibold text-neutral-500">State ID</label>
          <input className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" placeholder="Optional state id" value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} />
        </div>
        <div className="grid gap-1">
          <label className="text-xs font-semibold text-neutral-500">LGA ID</label>
          <input className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" placeholder="Optional LGA id" value={lgaFilter} onChange={(e) => setLgaFilter(e.target.value)} />
        </div>
        <div className="grid gap-1">
          <label className="text-xs font-semibold text-neutral-500">From</label>
          <input className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
        </div>
        <div className="grid gap-1">
          <label className="text-xs font-semibold text-neutral-500">To</label>
          <input className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
        </div>
      </div>

      {analyticsQuery.isLoading ? (
        <p className="rounded-lg border border-neutral-200 bg-white p-8 text-center text-sm text-neutral-500">Loading analytics...</p>
      ) : !data ? (
        <p className="rounded-lg border border-neutral-200 bg-white p-8 text-center text-sm text-neutral-500">Could not load analytics data.</p>
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            <DashboardCard icon={FileStack} label="Templates" value={summary?.total_templates ?? 0} />
            <DashboardCard icon={ClipboardCheck} label="Assignments" value={summary?.total_assignments ?? 0} />
            <DashboardCard icon={BarChart3} label="Total responses" value={summary?.total_responses ?? 0} />
            <DashboardCard icon={Percent} label="Completion rate" value={`${summary?.completion_rate ?? 0}%`} />
            <DashboardCard icon={TrendingUp} label="Avg score" value={summary?.average_score != null ? `${summary.average_score}` : "N/A"} />
          </div>

          <div className="grid gap-5 lg:grid-cols-2">
            <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <h3 className="mb-4 text-sm font-bold text-neutral-900">Submissions Over Time</h3>
              {data.submissions_over_time.length ? (
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={data.submissions_over_time}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(v) => new Date(v).toLocaleDateString("en-NG", { month: "short", day: "numeric" })} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                    <Tooltip labelFormatter={(v) => new Date(v as string).toLocaleDateString("en-NG", { dateStyle: "medium" })} />
                    <Bar dataKey="count" fill="#3b82f6" radius={[3, 3, 0, 0]} name="Submissions" />
                  </BarChart>
                </ResponsiveContainer>
              ) : <p className="py-8 text-center text-sm text-neutral-400">No submissions in this period.</p>}
            </section>

            <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <h3 className="mb-4 text-sm font-bold text-neutral-900">Response Status Breakdown</h3>
              {data.status_breakdown.length ? (
                <ResponsiveContainer width="100%" height={240}>
                  <PieChart>
                    <Pie data={data.status_breakdown} dataKey="count" nameKey="status" cx="50%" cy="50%" outerRadius={90} label={({ status, count }) => `${formatLabel(status as string)} (${count})`} labelLine={false} fontSize={11}>
                      {data.status_breakdown.map((entry) => (
                        <Cell key={entry.status} fill={STATUS_COLORS[entry.status] || "#a1a1aa"} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value, name) => [value, formatLabel(name as string)]} />
                  </PieChart>
                </ResponsiveContainer>
              ) : <p className="py-8 text-center text-sm text-neutral-400">No response data available.</p>}
            </section>

            <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <h3 className="mb-4 text-sm font-bold text-neutral-900">Score Distribution</h3>
              {data.score_distribution.some((d) => d.count > 0) ? (
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={data.score_distribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="range" tick={{ fontSize: 11 }} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="count" name="Responses" radius={[3, 3, 0, 0]}>
                      {data.score_distribution.map((_, i) => (
                        <Cell key={i} fill={SCORE_COLORS[i] || "#3b82f6"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : <p className="py-8 text-center text-sm text-neutral-400">No scored responses.</p>}
            </section>

            <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <h3 className="mb-4 text-sm font-bold text-neutral-900">Risk Rating Breakdown</h3>
              {data.risk_breakdown.length ? (
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={data.risk_breakdown} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11 }} />
                    <YAxis type="category" dataKey="risk_rating" tick={{ fontSize: 11 }} tickFormatter={formatLabel} width={80} />
                    <Tooltip formatter={(value, name) => [value, formatLabel(name as string)]} />
                    <Bar dataKey="count" name="Responses" radius={[0, 3, 3, 0]}>
                      {data.risk_breakdown.map((entry) => (
                        <Cell key={entry.risk_rating} fill={RISK_COLORS[entry.risk_rating] || "#94a3b8"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : <p className="py-8 text-center text-sm text-neutral-400">No risk-rated responses.</p>}
            </section>
          </div>

          <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
            <div className="border-b border-neutral-200 p-4">
              <h3 className="text-sm font-bold text-neutral-900">Response Rates by Template</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-neutral-200 text-sm">
                <thead className="bg-neutral-50 text-left text-xs font-bold uppercase tracking-wide text-neutral-500">
                  <tr>
                    <th className="px-4 py-3">Template</th>
                    <th className="px-4 py-3">Total</th>
                    <th className="px-4 py-3">Submitted</th>
                    <th className="px-4 py-3">Completion</th>
                    <th className="px-4 py-3">Avg Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-100">
                  {data.template_stats.length ? data.template_stats.map((row) => (
                    <tr key={row.template_id} className="hover:bg-neutral-50">
                      <td className="px-4 py-3 font-semibold text-neutral-900">{row.template_title}</td>
                      <td className="px-4 py-3 text-neutral-600">{row.total}</td>
                      <td className="px-4 py-3"><StatusBadge status={`${row.submitted} submitted`} /></td>
                      <td className="px-4 py-3 font-semibold text-neutral-800">{row.completion_rate}%</td>
                      <td className="px-4 py-3 text-neutral-600">{row.average_score != null ? row.average_score : "—"}</td>
                    </tr>
                  )) : (
                    <tr><td className="px-4 py-6 text-neutral-500" colSpan={5}>No template data available.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
            <div className="border-b border-neutral-200 p-4">
              <h3 className="text-sm font-bold text-neutral-900">Response Rates by Assignment</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-neutral-200 text-sm">
                <thead className="bg-neutral-50 text-left text-xs font-bold uppercase tracking-wide text-neutral-500">
                  <tr>
                    <th className="px-4 py-3">Assignment</th>
                    <th className="px-4 py-3">Recipients</th>
                    <th className="px-4 py-3">Responses</th>
                    <th className="px-4 py-3">Submitted</th>
                    <th className="px-4 py-3">Response rate</th>
                    <th className="px-4 py-3">Completion</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-100">
                  {data.assignment_stats.length ? data.assignment_stats.map((row) => (
                    <tr key={row.assignment_id} className="hover:bg-neutral-50">
                      <td className="px-4 py-3">
                        <p className="font-semibold text-neutral-900">{row.assignment_title}</p>
                        <p className="text-xs text-neutral-500">{row.template_title} / {formatLabel(row.context_type || "general")}</p>
                      </td>
                      <td className="px-4 py-3 text-neutral-600">{row.recipient_count}</td>
                      <td className="px-4 py-3 text-neutral-600">{row.response_count}</td>
                      <td className="px-4 py-3 text-neutral-600">{row.submitted_count}</td>
                      <td className="px-4 py-3 font-semibold text-neutral-800">{row.response_rate}%</td>
                      <td className="px-4 py-3 font-semibold text-neutral-800">{row.completion_rate}%</td>
                    </tr>
                  )) : (
                    <tr><td className="px-4 py-6 text-neutral-500" colSpan={6}>No assignment data available.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
            <div className="border-b border-neutral-200 p-4">
              <h3 className="text-sm font-bold text-neutral-900">Structured Response Analytics</h3>
            </div>
            <div className="grid gap-3 p-4 md:grid-cols-2">
              {data.structured_response_analytics.length ? data.structured_response_analytics.map((row) => (
                <div key={`${row.template_id}-${row.question_key}`} className="rounded border border-neutral-100 bg-neutral-50 p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-bold text-neutral-900">{row.question_label}</p>
                      <p className="mt-1 text-xs text-neutral-500">{row.template_title} / {formatLabel(row.question_type)} / {row.answered} answered</p>
                    </div>
                    {row.average != null ? <StatusBadge status={`avg ${row.average}`} /> : null}
                  </div>
                  <div className="mt-3 grid gap-2">
                    {row.top_values.map((item) => (
                      <div key={item.value} className="flex items-center justify-between rounded bg-white px-2 py-1 text-xs">
                        <span className="font-semibold text-neutral-700">{item.value}</span>
                        <span className="font-bold text-neutral-900">{item.count}</span>
                      </div>
                    ))}
                    {!row.top_values.length ? <p className="text-xs text-neutral-500">No aggregate values available.</p> : null}
                  </div>
                </div>
              )) : <p className="text-sm text-neutral-500">No structured response fields available for the current filters.</p>}
            </div>
          </section>

          <section className="grid gap-5 lg:grid-cols-3">
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <h3 className="text-sm font-bold text-neutral-900">Inspection Analytics</h3>
              <div className="mt-4 grid gap-3">
                <DashboardCard icon={ClipboardCheck} label="Inspections" value={data.inspection_analytics.inspection_count} />
                <DashboardCard icon={TrendingUp} label="Avg inspection score" value={data.inspection_analytics.average_score != null ? `${data.inspection_analytics.average_score}` : "N/A"} />
                {data.inspection_analytics.enforcement_breakdown.slice(0, 4).map((row) => (
                  <div key={row.enforcement_action || "none"} className="flex items-center justify-between rounded border border-neutral-100 bg-neutral-50 px-3 py-2 text-sm">
                    <span className="font-semibold text-neutral-700">{formatLabel(row.enforcement_action || "none")}</span>
                    <span className="font-bold text-neutral-900">{row.count}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <h3 className="text-sm font-bold text-neutral-900">Responses by Organization</h3>
              <div className="mt-4 grid gap-2">
                {data.organization_breakdown.slice(0, 8).map((row) => (
                  <div key={row.organization_id || row.organization_name} className="flex items-center justify-between rounded border border-neutral-100 bg-neutral-50 px-3 py-2 text-sm">
                    <span className="font-semibold text-neutral-700">{row.organization_name}</span>
                    <span className="font-bold text-neutral-900">{row.count}</span>
                  </div>
                ))}
                {!data.organization_breakdown.length ? <p className="text-sm text-neutral-500">No organization data available.</p> : null}
              </div>
            </div>
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <h3 className="text-sm font-bold text-neutral-900">Responses by State</h3>
              <div className="mt-4 grid gap-2">
                {data.location_breakdown.slice(0, 8).map((row) => (
                  <div key={row.state_id || row.state_name} className="flex items-center justify-between rounded border border-neutral-100 bg-neutral-50 px-3 py-2 text-sm">
                    <span className="font-semibold text-neutral-700">{row.state_name}</span>
                    <span className="font-bold text-neutral-900">{row.count}</span>
                  </div>
                ))}
                {!data.location_breakdown.length ? <p className="text-sm text-neutral-500">No location data available.</p> : null}
              </div>
            </div>
          </section>

          {data.purpose_breakdown.length ? (
            <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
              <div className="border-b border-neutral-200 p-4">
                <h3 className="text-sm font-bold text-neutral-900">Assignments by Purpose</h3>
              </div>
              <div className="grid gap-2 p-4 sm:grid-cols-2 lg:grid-cols-3">
                {data.purpose_breakdown.map((row) => (
                  <div key={row.purpose} className="flex items-center justify-between rounded border border-neutral-100 bg-neutral-50 px-3 py-2">
                    <span className="text-sm font-semibold text-neutral-800">{formatLabel(row.purpose)}</span>
                    <span className="text-sm font-bold text-neutral-900">{row.count}</span>
                  </div>
                ))}
              </div>
            </section>
          ) : null}
        </>
      )}
    </div>
  );
}
