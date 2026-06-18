"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";

import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { getApiErrorMessage } from "@/lib/api/client";
import {
  activateMEIndicator,
  approveMEIndicatorValue,
  createMEIndicatorValue,
  confirmMEIndicatorImport,
  downloadMEIndicatorImportTemplate,
  getMEIndicatorDashboardSummary,
  listAllMEIndicatorValues,
  listMEIndicators,
  listMEIndicatorValues,
  listPolicyVersions,
  overrideMEIndicator,
  previewMEIndicatorImport,
  rejectMEIndicatorValue,
  submitMEIndicatorValue,
  updateMEIndicatorValue,
  type MEIndicatorDashboardSummary,
  type MEIndicatorImportPreview,
} from "@/lib/api/standards";
import { MEIndicatorFormDrawer } from "@/features/standards/me-indicator-form-drawer";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import type { MEIndicator, MEIndicatorValue, PolicyVersionStatus } from "@/types/standards";

const TODAY = new Date("2026-06-16T00:00:00");
const PAGE_SIZE = 10;
const KPI_DATA_SOURCES = [
  "manual",
  "food_handler_registry",
  "medical_test_records",
  "test_results",
  "certificate_records",
  "facility_records",
  "facility_handler_mapping",
  "test_centers_labs",
  "inspections",
  "training_orientation",
  "payments",
  "kpi",
];
const POLICY_VERSION_PRIORITY: Record<PolicyVersionStatus, number> = {
  draft: 0,
  returned: 1,
  active: 2,
  approved: 3,
  scheduled: 4,
  under_review: 5,
  retired: 6,
  archived: 7,
};

function statusClass(status: string) {
  if (status === "approved" || status === "active") return "bg-brand-50 text-brand-700";
  if (status === "submitted") return "bg-info-50 text-info-700";
  if (status === "rejected") return "bg-danger-50 text-danger-700";
  if (status === "draft") return "bg-neutral-100 text-neutral-700";
  return "bg-warning-50 text-warning-700";
}

function formatStatus(status: string) {
  return status.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase());
}

function normalizeInputMode(mode: string | null | undefined) {
  if (mode === "automated") return "automatic";
  return mode ?? "manual";
}

function textFromConfig(config: Record<string, unknown> | undefined, key: string, fallback = "") {
  const value = config?.[key];
  return value == null ? fallback : String(value);
}

function numeric(value: string | number | null | undefined) {
  if (value == null || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function exportRows(rows: Array<Record<string, string | number | null>>) {
  const headers = Object.keys(rows[0] ?? { indicator: "", code: "", status: "" });
  const csv = [
    headers.join(","),
    ...rows.map((row) => headers.map((header) => `"${String(row[header] ?? "").replace(/"/g, '""')}"`).join(",")),
  ].join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "me-indicators.csv";
  link.click();
  URL.revokeObjectURL(url);
}

function DashboardPanel({
  summary,
  isLoading,
}: {
  summary?: MEIndicatorDashboardSummary;
  isLoading: boolean;
}) {
  const maxTrend = Math.max(1, ...(summary?.trends ?? []).map((point) => point.value));
  const breakdownRows = Object.entries(summary?.source_breakdown ?? {})
    .filter(([, value]) => value > 0)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6);

  return (
    <section className="grid gap-4">
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        {(summary?.summary_cards ?? [
          { key: "loading-total", label: "Total KPIs", value: 0, helper: "Loading dashboard" },
          { key: "loading-active", label: "Active KPIs", value: 0, helper: "Loading dashboard" },
          { key: "loading-due", label: "Due for Reporting", value: 0, helper: "Loading dashboard" },
          { key: "loading-completeness", label: "Data Completeness", value: 0, suffix: "%", helper: "Loading dashboard" },
          { key: "loading-automatic", label: "Automatic/Hybrid", value: 0, helper: "Loading dashboard" },
        ]).map((card) => (
          <div key={card.key} className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-bold uppercase text-neutral-500">{card.label}</p>
            <p className="mt-2 text-2xl font-semibold text-neutral-950">{isLoading ? "..." : `${card.value}${card.suffix ?? ""}`}</p>
            <p className="mt-1 text-xs text-neutral-500">{card.helper}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(320px,0.8fr)]">
        <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-sm font-semibold text-neutral-950">National KPI Trend</h2>
              <p className="mt-1 text-xs text-neutral-500">Approved KPI values grouped by reporting period.</p>
            </div>
            <span className="rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-semibold text-neutral-600">{summary?.trends.length ?? 0} periods</span>
          </div>
          <div className="mt-4 grid gap-3">
            {(summary?.trends ?? []).slice(-8).map((point) => (
              <div className="grid items-center gap-3 sm:grid-cols-[88px_minmax(0,1fr)_80px]" key={point.period}>
                <span className="text-xs font-semibold text-neutral-500">{point.period}</span>
                <div className="h-8 rounded bg-neutral-100">
                  <div className="h-8 rounded bg-brand-500" style={{ width: `${Math.max(4, Math.min(100, (point.value / maxTrend) * 100))}%` }} />
                </div>
                <span className="text-sm font-semibold text-neutral-900">{point.value}</span>
              </div>
            ))}
            {!summary?.trends.length ? <p className="rounded border border-dashed border-neutral-300 p-4 text-sm text-neutral-500">No approved KPI values are available for the selected filters.</p> : null}
          </div>
        </div>

        <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <h2 className="text-sm font-semibold text-neutral-950">Alerts</h2>
          <div className="mt-3 space-y-2">
            {(summary?.alerts ?? []).map((alert, index) => (
              <div key={`${alert.indicator_id ?? index}-${alert.title}`} className={`rounded-md border px-3 py-2 ${
                alert.severity === "critical" ? "border-danger-100 bg-danger-50 text-danger-700" :
                alert.severity === "warning" ? "border-warning-100 bg-warning-50 text-warning-700" :
                "border-info-100 bg-info-50 text-info-700"
              }`}>
                <p className="text-sm font-semibold">{alert.title}</p>
                <p className="mt-1 text-xs">{alert.detail}</p>
              </div>
            ))}
            {!summary?.alerts.length ? <p className="rounded border border-dashed border-neutral-300 p-4 text-sm text-neutral-500">No dashboard alerts for the selected filters.</p> : null}
          </div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <h2 className="text-sm font-semibold text-neutral-950">Source Coverage</h2>
          <div className="mt-3 space-y-2">
            {breakdownRows.map(([source, count]) => (
              <div className="flex items-center justify-between rounded-md bg-neutral-50 px-3 py-2 text-sm" key={source}>
                <span className="font-medium text-neutral-700">{formatStatus(source)}</span>
                <span className="font-semibold text-neutral-950">{count}</span>
              </div>
            ))}
            {!breakdownRows.length ? <p className="text-sm text-neutral-500">No source coverage yet.</p> : null}
          </div>
        </div>

        <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <h2 className="text-sm font-semibold text-neutral-950">Top KPI Performance</h2>
          <div className="mt-3 overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="text-left text-xs uppercase text-neutral-500"><tr><th className="py-2 pr-3">KPI</th><th className="py-2 pr-3">Latest</th><th className="py-2 pr-3">Target</th><th className="py-2 pr-3">Achievement</th></tr></thead>
              <tbody>
                {(summary?.rankings ?? []).slice(0, 5).map((row) => (
                  <tr className="border-t border-neutral-100" key={row.id}>
                    <td className="py-3 pr-3"><Link href={`/federal/standards/me-indicators/${row.id}`} className="font-semibold text-brand-700 hover:underline">{row.code}</Link></td>
                    <td className="py-3 pr-3">{row.latest_value ?? "-"}</td>
                    <td className="py-3 pr-3">{row.target ?? "-"}</td>
                    <td className="py-3 pr-3">{row.achievement == null ? "-" : `${row.achievement}%`}</td>
                  </tr>
                ))}
                {!summary?.rankings.length ? <tr><td className="py-6 text-neutral-500" colSpan={4}>No KPI ranking data yet.</td></tr> : null}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
}

function IndicatorDataEntryModal({
  indicator,
  onClose,
}: {
  indicator: MEIndicator;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const [error, setError] = useState("");
  const [selectedValue, setSelectedValue] = useState<MEIndicatorValue | null>(null);
  const [rejecting, setRejecting] = useState<MEIndicatorValue | null>(null);
  const [rejectComment, setRejectComment] = useState("");
  const [form, setForm] = useState({
    period_start: "2026-04-01",
    period_end: "2026-06-30",
    progress_value_numeric: "",
    cumulative_value_numeric: "",
    qualitative_value_text: "",
    qualitative_rating: "",
    qualitative_category: "",
    notes: "",
    override_reason: "",
  });
  const indicatorType = String(indicator.formula_config?.indicator_type || "quantitative");
  const inputMode = normalizeInputMode(indicator.input_mode);
  const qualitativeConfig = indicator.qualitative_config;
  const qualitativeInputType = qualitativeConfig?.input_type ?? "text";
  const qualitativeOptions = qualitativeConfig?.category_options_json ?? [];
  const scaleMin = qualitativeConfig?.scale_min ?? 1;
  const scaleMax = qualitativeConfig?.scale_max ?? 5;
  const isQualitative = indicatorType === "qualitative";

  const valuesQuery = useQuery({
    queryKey: ["standards-me-indicator-values", indicator.id],
    queryFn: () => listMEIndicatorValues(indicator.id),
  });
  const values = Array.isArray(valuesQuery.data) ? valuesQuery.data : [];
  const latestAutomatedValue = values.find((value) => value.value_source === "automated");

  const saveValueMutation = useMutation({
    mutationFn: async () => {
      if (inputMode === "hybrid") {
        return overrideMEIndicator(indicator.id, {
          period_start: form.period_start,
          period_end: form.period_end,
          override_value: form.cumulative_value_numeric || form.progress_value_numeric,
          reason: form.override_reason,
        });
      }
      const payload: Partial<MEIndicatorValue> = {
        period_start: form.period_start,
        period_end: form.period_end,
        progress_value_numeric: form.progress_value_numeric || null,
        cumulative_value_numeric: form.cumulative_value_numeric || null,
        qualitative_value_text: form.qualitative_value_text,
        qualitative_rating: form.qualitative_rating || null,
        qualitative_category: form.qualitative_category,
        notes: form.notes,
        value_source: "manual",
      };
      if (selectedValue) return updateMEIndicatorValue(selectedValue.id, payload);
      return createMEIndicatorValue(indicator.id, payload);
    },
    onSuccess: () => {
      setError("");
      setSelectedValue(null);
      setForm({
        period_start: "2026-04-01",
        period_end: "2026-06-30",
        progress_value_numeric: "",
        cumulative_value_numeric: "",
        qualitative_value_text: "",
        qualitative_rating: "",
        qualitative_category: "",
        notes: "",
        override_reason: "",
      });
      queryClient.invalidateQueries({ queryKey: ["standards-me-indicator-values", indicator.id] });
      queryClient.invalidateQueries({ queryKey: ["standards-me-indicator", indicator.id] });
    },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to save indicator value.")),
  });
  const submitMutation = useMutation({
    mutationFn: submitMEIndicatorValue,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["standards-me-indicator-values", indicator.id] }),
    onError: (err) => setError(getApiErrorMessage(err, "Failed to submit indicator value.")),
  });
  const approveMutation = useMutation({
    mutationFn: (id: string) => approveMEIndicatorValue(id, "Approved from Federal KPI workspace."),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["standards-me-indicator-values", indicator.id] }),
    onError: (err) => setError(getApiErrorMessage(err, "Failed to approve indicator value.")),
  });
  const rejectMutation = useMutation({
    mutationFn: () => rejecting ? rejectMEIndicatorValue(rejecting.id, rejectComment) : Promise.reject(new Error("Select a value first.")),
    onSuccess: () => {
      setRejecting(null);
      setRejectComment("");
      queryClient.invalidateQueries({ queryKey: ["standards-me-indicator-values", indicator.id] });
    },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to reject indicator value.")),
  });

  function editValue(value: MEIndicatorValue) {
    setSelectedValue(value);
    setForm({
      period_start: value.period_start,
      period_end: value.period_end,
      progress_value_numeric: value.progress_value_numeric == null ? "" : String(value.progress_value_numeric),
      cumulative_value_numeric: value.cumulative_value_numeric == null ? "" : String(value.cumulative_value_numeric),
      qualitative_value_text: value.qualitative_value_text || "",
      qualitative_rating: value.qualitative_rating == null ? "" : String(value.qualitative_rating),
      qualitative_category: value.qualitative_category || "",
      notes: value.notes || "",
      override_reason: value.override_reason || "",
    });
  }

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/40" onClick={onClose} />
      <div className="fixed inset-x-0 bottom-0 top-12 z-50 mx-auto flex w-[min(1120px,100vw)] flex-col overflow-hidden rounded-t-2xl bg-white shadow-2xl lg:bottom-8 lg:top-8 lg:rounded-2xl">
        <header className="flex items-center justify-between border-b border-neutral-200 px-5 py-4">
          <div>
            <h2 className="text-lg font-semibold text-neutral-950">{inputMode === "hybrid" ? "Override KPI Value" : "Data Entry"}</h2>
            <p className="text-sm text-slate-400">{indicator.indicator_name}</p>
          </div>
          <button onClick={onClose} type="button" className="rounded-full bg-neutral-50 px-3 py-1.5 text-sm font-semibold text-neutral-500 hover:text-neutral-900">Close</button>
        </header>
        <div className="grid min-h-0 flex-1 lg:grid-cols-[360px_minmax(0,1fr)]">
          <aside className="border-r border-neutral-200 p-5">
            <p className="text-xs font-bold uppercase text-neutral-500">KPI</p>
            <h3 className="mt-2 text-base font-bold text-neutral-950">{indicator.indicator_name}</h3>
            <p className="mt-2 text-sm text-neutral-500">{indicator.description || "No description available"}</p>
            {inputMode === "hybrid" ? (
              <div className="mt-4 rounded-lg border border-warning-200 bg-warning-50 p-3 text-sm text-warning-900">
                <p className="font-semibold">Hybrid override workflow</p>
                <p className="mt-1">The system-calculated value is preserved. Your override will be stored separately and must include a reason.</p>
                <p className="mt-2 text-xs">Latest calculated value: {latestAutomatedValue?.cumulative_value_numeric ?? latestAutomatedValue?.progress_value_numeric ?? indicator.latest_value ?? "-"}</p>
              </div>
            ) : null}
            <div className="mt-5 grid grid-cols-2 overflow-hidden rounded-lg border border-neutral-200 bg-neutral-50 text-center">
              {[
                ["Type", indicatorType],
                ["Unit", String(indicator.formula_config?.unit_of_measurement || "Number")],
                ["Period", indicator.reporting_frequency],
                ["Input", isQualitative ? qualitativeInputType : String(indicator.formula_config?.record_input_mode || "progress_only")],
              ].map(([label, value]) => (
                <div className="border-b border-r border-neutral-200 px-3 py-3" key={label}>
                  <p className="text-xs text-slate-400">{label}</p>
                  <p className="mt-1 text-sm font-medium capitalize text-neutral-900">{value.replace(/_/g, " ")}</p>
                </div>
              ))}
            </div>
          </aside>
          <main className="min-h-0 overflow-y-auto p-5">
            {error ? <div className="mb-4 rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</div> : null}
            <section className="rounded-lg border border-neutral-200 bg-white p-4">
              <h3 className="text-sm font-semibold text-neutral-950">
                {inputMode === "hybrid" ? "Override current period value" : selectedValue ? "Revise value" : "Enter current period value"}
              </h3>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <label className="text-sm font-medium text-neutral-700">Period start<input type="date" className="mt-1 h-10 w-full rounded border border-neutral-200 px-3" value={form.period_start} onChange={(event) => setForm((current) => ({ ...current, period_start: event.target.value }))} /></label>
                <label className="text-sm font-medium text-neutral-700">Period end<input type="date" className="mt-1 h-10 w-full rounded border border-neutral-200 px-3" value={form.period_end} onChange={(event) => setForm((current) => ({ ...current, period_end: event.target.value }))} /></label>
                {!isQualitative ? (
                  <>
                    <label className="text-sm font-medium text-neutral-700">Progress<input className="mt-1 h-10 w-full rounded border border-neutral-200 px-3" value={form.progress_value_numeric} onChange={(event) => setForm((current) => ({ ...current, progress_value_numeric: event.target.value }))} /></label>
                    <label className="text-sm font-medium text-neutral-700">Cumulative<input className="mt-1 h-10 w-full rounded border border-neutral-200 px-3" value={form.cumulative_value_numeric} onChange={(event) => setForm((current) => ({ ...current, cumulative_value_numeric: event.target.value }))} /></label>
                  </>
                ) : null}
                {isQualitative && ["likert_scale", "rubric"].includes(qualitativeInputType) ? (
                  <label className="text-sm font-medium text-neutral-700">Rating<input type="number" min={scaleMin} max={scaleMax} className="mt-1 h-10 w-full rounded border border-neutral-200 px-3" value={form.qualitative_rating} onChange={(event) => setForm((current) => ({ ...current, qualitative_rating: event.target.value }))} /></label>
                ) : null}
                {isQualitative && ["category", "rubric"].includes(qualitativeInputType) ? (
                  <label className="text-sm font-medium text-neutral-700">Category
                    <select className="mt-1 h-10 w-full rounded border border-neutral-200 bg-white px-3" value={form.qualitative_category} onChange={(event) => setForm((current) => ({ ...current, qualitative_category: event.target.value }))}>
                      <option value="">Select category</option>
                      {qualitativeOptions.map((option) => <option key={option} value={option}>{option}</option>)}
                    </select>
                  </label>
                ) : null}
                {inputMode === "hybrid" ? (
                  <label className="text-sm font-medium text-neutral-700 md:col-span-2">Override reason
                    <input className="mt-1 h-10 w-full rounded border border-neutral-200 px-3" value={form.override_reason} onChange={(event) => setForm((current) => ({ ...current, override_reason: event.target.value }))} />
                  </label>
                ) : null}
                <label className="text-sm font-medium text-neutral-700">Notes<input className="mt-1 h-10 w-full rounded border border-neutral-200 px-3" value={form.notes} onChange={(event) => setForm((current) => ({ ...current, notes: event.target.value }))} /></label>
              </div>
              {isQualitative ? (
                <textarea className="mt-3 min-h-20 w-full rounded border border-neutral-200 px-3 py-2 text-sm" placeholder={qualitativeConfig?.requires_narrative ? "Narrative required" : "Narrative or qualitative notes"} value={form.qualitative_value_text} onChange={(event) => setForm((current) => ({ ...current, qualitative_value_text: event.target.value }))} />
              ) : null}
              <div className="mt-4 flex justify-end gap-2">
                {selectedValue && inputMode !== "hybrid" ? <button type="button" className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-700" onClick={() => setSelectedValue(null)}>Cancel revision</button> : null}
                <button type="button" onClick={() => saveValueMutation.mutate()} disabled={saveValueMutation.isPending} className="h-10 rounded bg-brand-600 px-4 text-sm font-semibold text-white disabled:opacity-60">{saveValueMutation.isPending ? "Saving..." : inputMode === "hybrid" ? "Apply Override" : "Save Draft"}</button>
              </div>
            </section>

            <section className="mt-5 rounded-lg border border-neutral-200 bg-white p-4">
              <h3 className="text-sm font-semibold text-neutral-950">Submitted values</h3>
              <div className="mt-3 overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead className="text-left text-xs uppercase text-neutral-500"><tr><th className="py-2 pr-4">Period</th><th className="py-2 pr-4">{isQualitative ? "Qualitative value" : "Progress"}</th><th className="py-2 pr-4">{isQualitative ? "Rating" : "Cumulative"}</th><th className="py-2 pr-4">Status</th><th className="py-2 pr-4">Actions</th></tr></thead>
                  <tbody>
                    {values.map((value) => (
                      <tr className="border-t border-neutral-100" key={value.id}>
                        <td className="py-3 pr-4">{value.period_start} to {value.period_end}</td>
                        <td className="py-3 pr-4">{isQualitative ? (value.qualitative_category || value.qualitative_value_text || "-") : (value.progress_value_numeric ?? "-")}</td>
                        <td className="py-3 pr-4">{isQualitative ? (value.qualitative_rating ?? "-") : (value.cumulative_value_numeric ?? "-")}</td>
                        <td className="py-3 pr-4"><span className={`rounded-full px-2 py-1 text-xs font-semibold ${statusClass(value.approval_status)}`}>{formatStatus(value.approval_status)}</span></td>
                        <td className="py-3 pr-4">
                          <div className="flex flex-wrap gap-2">
                            {inputMode !== "hybrid" && ["draft", "rejected"].includes(value.approval_status) ? <button className="rounded border border-neutral-200 px-2 py-1 text-xs font-bold" onClick={() => editValue(value)} type="button">Edit</button> : null}
                            {inputMode !== "hybrid" && ["draft", "rejected"].includes(value.approval_status) ? <button className="rounded border border-brand-200 px-2 py-1 text-xs font-bold text-brand-700" onClick={() => submitMutation.mutate(value.id)} type="button">Submit</button> : null}
                            {value.approval_status === "submitted" ? <button className="rounded bg-brand-600 px-2 py-1 text-xs font-bold text-white" onClick={() => approveMutation.mutate(value.id)} type="button">Approve</button> : null}
                            {value.approval_status === "submitted" ? <button className="rounded border border-danger-100 px-2 py-1 text-xs font-bold text-danger-700" onClick={() => setRejecting(value)} type="button">Reject</button> : null}
                          </div>
                          {value.value_source === "override" && value.override_reason ? <p className="mt-2 text-xs text-warning-700">Reason: {value.override_reason}</p> : null}
                        </td>
                      </tr>
                    ))}
                    {!values.length ? <tr><td className="py-6 text-neutral-500" colSpan={5}>{valuesQuery.isLoading ? "Loading values..." : "No values entered yet."}</td></tr> : null}
                  </tbody>
                </table>
              </div>
            </section>
          </main>
        </div>
      </div>
      {rejecting ? (
        <div className="fixed inset-0 z-[60] grid place-items-center bg-black/30 p-4">
          <form className="w-full max-w-md rounded-lg bg-white p-5 shadow-xl" onSubmit={(event) => { event.preventDefault(); rejectMutation.mutate(); }}>
            <h3 className="text-base font-bold text-neutral-950">Reject value</h3>
            <textarea required className="mt-3 min-h-24 w-full rounded border border-neutral-200 px-3 py-2 text-sm" placeholder="Reason for rejection" value={rejectComment} onChange={(event) => setRejectComment(event.target.value)} />
            <div className="mt-4 flex justify-end gap-2">
              <button type="button" onClick={() => setRejecting(null)} className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold">Cancel</button>
              <button type="submit" disabled={!rejectComment || rejectMutation.isPending} className="h-10 rounded bg-danger-600 px-4 text-sm font-semibold text-white disabled:opacity-60">Reject</button>
            </div>
          </form>
        </div>
      ) : null}
    </>
  );
}

function IndicatorImportModal({
  indicator,
  onClose,
  onImported,
}: {
  indicator: MEIndicator;
  onClose: () => void;
  onImported: () => void;
}) {
  const [csvText, setCsvText] = useState("");
  const [submit, setSubmit] = useState(false);
  const [preview, setPreview] = useState<MEIndicatorImportPreview | null>(null);
  const [error, setError] = useState("");

  const previewMutation = useMutation({
    mutationFn: () => previewMEIndicatorImport(indicator.id, { csv_text: csvText }),
    onSuccess: (result) => {
      setError("");
      setPreview(result);
    },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to preview import.")),
  });
  const confirmMutation = useMutation({
    mutationFn: () => confirmMEIndicatorImport(indicator.id, { csv_text: csvText, submit }),
    onSuccess: () => {
      onImported();
      onClose();
    },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to confirm import.")),
  });

  async function downloadTemplate() {
    try {
      const blob = await downloadMEIndicatorImportTemplate(indicator.id);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${indicator.indicator_code}-indicator-import-template.csv`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to download template."));
    }
  }

  async function readFile(file: File | null) {
    if (!file) return;
    setCsvText(await file.text());
    setPreview(null);
  }

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/40" onClick={onClose} />
      <div className="fixed inset-x-0 bottom-0 top-12 z-50 mx-auto flex w-[min(980px,100vw)] flex-col overflow-hidden rounded-t-2xl bg-white shadow-2xl lg:bottom-8 lg:top-8 lg:rounded-2xl">
        <header className="flex items-center justify-between border-b border-neutral-200 px-5 py-4">
          <div>
            <h2 className="text-lg font-semibold text-neutral-950">Bulk Import Historical Data</h2>
            <p className="text-sm text-slate-400">{indicator.indicator_name}</p>
          </div>
          <button onClick={onClose} type="button" className="rounded-full bg-neutral-50 px-3 py-1.5 text-sm font-semibold text-neutral-500 hover:text-neutral-900">Close</button>
        </header>
        <main className="min-h-0 flex-1 overflow-y-auto p-5">
          {error ? <div className="mb-4 rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</div> : null}
          <section className="rounded-lg border border-neutral-200 bg-white p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-neutral-950">CSV template</p>
                <p className="mt-1 text-sm text-neutral-500">Template columns include period values, qualitative fields, and notes.</p>
              </div>
              <button type="button" onClick={downloadTemplate} className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50">Download Template</button>
            </div>
            <div className="mt-4 grid gap-3">
              <input type="file" accept=".csv,text/csv" onChange={(event) => readFile(event.target.files?.[0] ?? null)} className="text-sm text-neutral-700" />
              <textarea className="min-h-48 rounded border border-neutral-200 px-3 py-2 font-mono text-xs" placeholder="Paste CSV here" value={csvText} onChange={(event) => { setCsvText(event.target.value); setPreview(null); }} />
              <label className="inline-flex items-center gap-2 text-sm font-medium text-neutral-700">
                <input type="checkbox" checked={submit} onChange={(event) => setSubmit(event.target.checked)} />
                Submit imported rows for approval immediately
              </label>
            </div>
            <div className="mt-4 flex justify-end gap-2">
              <button type="button" disabled={!csvText || previewMutation.isPending} onClick={() => previewMutation.mutate()} className="h-10 rounded border border-brand-200 px-4 text-sm font-semibold text-brand-700 disabled:opacity-60">Preview Import</button>
              <button type="button" disabled={!preview || preview.summary.invalid > 0 || preview.summary.valid === 0 || confirmMutation.isPending} onClick={() => confirmMutation.mutate()} className="h-10 rounded bg-brand-600 px-4 text-sm font-semibold text-white disabled:opacity-60">Confirm Import</button>
            </div>
          </section>

          {preview ? (
            <section className="mt-5 rounded-lg border border-neutral-200 bg-white p-4">
              <div className="grid gap-3 sm:grid-cols-3">
                <div className="rounded bg-neutral-50 p-3"><p className="text-xs font-semibold uppercase text-neutral-500">Total</p><p className="mt-1 text-xl font-semibold text-neutral-950">{preview.summary.total}</p></div>
                <div className="rounded bg-brand-50 p-3"><p className="text-xs font-semibold uppercase text-brand-700">Valid</p><p className="mt-1 text-xl font-semibold text-brand-700">{preview.summary.valid}</p></div>
                <div className="rounded bg-danger-50 p-3"><p className="text-xs font-semibold uppercase text-danger-700">Invalid</p><p className="mt-1 text-xl font-semibold text-danger-700">{preview.summary.invalid}</p></div>
              </div>
              <div className="mt-4 overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead className="text-left text-xs uppercase text-neutral-500"><tr><th className="py-2 pr-4">Row</th><th className="py-2 pr-4">Period</th><th className="py-2 pr-4">Progress</th><th className="py-2 pr-4">Cumulative</th><th className="py-2 pr-4">Errors</th></tr></thead>
                  <tbody>
                    {[...preview.valid_rows, ...preview.invalid_rows].map((row) => (
                      <tr className="border-t border-neutral-100" key={row.row}>
                        <td className="py-3 pr-4">{row.row}</td>
                        <td className="py-3 pr-4">{String(row.data.period_start ?? "")} to {String(row.data.period_end ?? "")}</td>
                        <td className="py-3 pr-4">{String(row.data.progress_value_numeric ?? "-")}</td>
                        <td className="py-3 pr-4">{String(row.data.cumulative_value_numeric ?? "-")}</td>
                        <td className={`py-3 pr-4 ${row.valid ? "text-brand-700" : "text-danger-700"}`}>{row.valid ? "Valid" : row.errors.join("; ")}</td>
                      </tr>
                    ))}
                    {preview.errors.map((row) => (
                      <tr className="border-t border-neutral-100" key={`error-${row.row}`}>
                        <td className="py-3 pr-4">{row.row}</td>
                        <td className="py-3 pr-4" colSpan={3}>File error</td>
                        <td className="py-3 pr-4 text-danger-700">{row.errors.join("; ")}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          ) : null}
        </main>
      </div>
    </>
  );
}

export default function MEIndicatorsPage() {
  const queryClient = useQueryClient();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerMode, setDrawerMode] = useState<"create" | "edit">("create");
  const [editing, setEditing] = useState<MEIndicator | null>(null);
  const [dataEntryIndicator, setDataEntryIndicator] = useState<MEIndicator | null>(null);
  const [importIndicator, setImportIndicator] = useState<MEIndicator | null>(null);
  const [policyVersionId, setPolicyVersionId] = useState("");
  const [actionError, setActionError] = useState("");
  const [page, setPage] = useState(1);
  const [dashboardFilters, setDashboardFilters] = useState({
    period_start: "",
    period_end: "",
    status: "",
    input_mode: "",
    data_source: "",
  });
  const [filters, setFilters] = useState({
    search: "",
    indicator_type: "",
    status: "",
    reporting_frequency: "",
    due_for_reporting: "",
    created_by: "",
  });

  const { data, isLoading } = useQuery({
    queryKey: ["standards-me-indicators"],
    queryFn: () => listMEIndicators(),
  });
  const { data: versions } = useQuery({
    queryKey: ["standards-policy-versions"],
    queryFn: () => listPolicyVersions(),
  });
  const { data: allValues } = useQuery({
    queryKey: ["standards-me-indicator-values-all"],
    queryFn: () => listAllMEIndicatorValues(),
  });
  const dashboardParams = useMemo(() => Object.fromEntries(
    Object.entries(dashboardFilters).filter(([, value]) => value)
  ), [dashboardFilters]);
  const { data: dashboardSummary, isLoading: dashboardLoading } = useQuery({
    queryKey: ["standards-me-indicator-dashboard-summary", dashboardParams],
    queryFn: () => getMEIndicatorDashboardSummary(dashboardParams),
  });

  const rows = useMemo(() => (
    Array.isArray(data) ? data : []
  ), [data]);
  const values = useMemo(() => Array.isArray(allValues) ? allValues : [], [allValues]);
  const availableVersions = useMemo(() => (
    (Array.isArray(versions) ? versions : [])
      .filter((version) => !["retired", "archived"].includes(version.status))
      .sort((a, b) => {
        const priorityDelta = (POLICY_VERSION_PRIORITY[a.status] ?? 99) - (POLICY_VERSION_PRIORITY[b.status] ?? 99);
        if (priorityDelta !== 0) return priorityDelta;
        return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
      })
  ), [versions]);
  const preferredCreateVersion = availableVersions[0] ?? null;
  const valueSummary = useMemo(() => {
    const grouped = new Map<string, MEIndicatorValue[]>();
    values.forEach((value) => {
      grouped.set(value.indicator, [...(grouped.get(value.indicator) ?? []), value]);
    });
    const summary = new Map<string, { latest?: MEIndicatorValue; latestApproved?: MEIndicatorValue; due: boolean }>();
    grouped.forEach((indicatorValues, indicatorId) => {
      const sorted = [...indicatorValues].sort((a, b) => new Date(b.period_end).getTime() - new Date(a.period_end).getTime());
      const latest = sorted[0];
      const latestApproved = sorted.find((value) => value.approval_status === "approved");
      const latestDate = latest ? new Date(latest.period_end) : null;
      summary.set(indicatorId, {
        latest,
        latestApproved,
        due: !latestDate || latestDate < TODAY,
      });
    });
    return summary;
  }, [values]);
  const optionSets = useMemo(() => ({
    creators: Array.from(new Set(rows.map((row) => row.created_by_name).filter(Boolean))).sort(),
  }), [rows]);
  const filteredRows = useMemo(() => {
    const search = filters.search.trim().toLowerCase();
    return rows.filter((row) => {
      const formula = row.formula_config ?? {};
      const indicatorType = textFromConfig(formula, "indicator_type", "quantitative");
      const due = valueSummary.get(row.id)?.due ?? true;
      if (search && !`${row.indicator_name} ${row.indicator_code} ${row.description}`.toLowerCase().includes(search)) return false;
      if (filters.indicator_type && indicatorType !== filters.indicator_type) return false;
      if (filters.status && row.status !== filters.status) return false;
      if (filters.reporting_frequency && row.reporting_frequency !== filters.reporting_frequency) return false;
      if (filters.due_for_reporting && String(due) !== filters.due_for_reporting) return false;
      if (filters.created_by && row.created_by_name !== filters.created_by) return false;
      return true;
    });
  }, [filters, rows, valueSummary]);
  const importableRows = useMemo(
    () => filteredRows.filter((row) => ["manual", "imported"].includes(normalizeInputMode(row.input_mode ?? textFromConfig(row.formula_config, "input_mode", "manual")))),
    [filteredRows]
  );
  const pageCount = Math.max(1, Math.ceil(filteredRows.length / PAGE_SIZE));
  const pagedRows = filteredRows.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const activateMutation = useMutation({
    mutationFn: activateMEIndicator,
    onSuccess: () => {
      setActionError("");
      queryClient.invalidateQueries({ queryKey: ["standards-me-indicators"] });
      queryClient.invalidateQueries({ queryKey: ["standards-policy-versions"] });
    },
    onError: (err) => setActionError(getApiErrorMessage(err, "Failed to activate KPI.")),
  });

  function openCreate() {
    if (!preferredCreateVersion) {
      setActionError("Create a policy version first so the KPI builder has a Standards version to attach to.");
      return;
    }
    setActionError("");
    setPolicyVersionId(preferredCreateVersion.id);
    setEditing(null);
    setDrawerMode("create");
    setDrawerOpen(true);
  }

  function openEdit(row: MEIndicator) {
    setPolicyVersionId(row.policy_version);
    setEditing(row);
    setDrawerMode("edit");
    setDrawerOpen(true);
  }

  function updateFilter(field: keyof typeof filters, value: string) {
    setFilters((current) => ({ ...current, [field]: value }));
    setPage(1);
  }

  function updateDashboardFilter(field: keyof typeof dashboardFilters, value: string) {
    setDashboardFilters((current) => ({ ...current, [field]: value }));
  }

  function calculationPeriodFor(row: MEIndicator) {
    const latest = valueSummary.get(row.id)?.latestApproved ?? valueSummary.get(row.id)?.latest;
    if (latest) {
      return { period_start: latest.period_start, period_end: latest.period_end };
    }
    return { period_start: "2026-04-01", period_end: "2026-06-30" };
  }

  const recalculateMutation = useMutation({
    mutationFn: async (row: MEIndicator) => {
      const period = calculationPeriodFor(row);
      const sourceType = row.data_source === "manual" ? "food_handler_registry" : row.data_source;
      return calculateMEIndicator(row.id, {
        source_type: sourceType,
        calculation_method: (textFromConfig(row.formula_config, "calculation_method", "percentage") || "percentage") as "count" | "unique_count" | "sum" | "average" | "percentage" | "ratio" | "formula",
        value_field_id: textFromConfig(row.formula_config, "value_field_id", "value"),
        filter_config_json: {
          date_field_id: textFromConfig(row.formula_config, "date_field_id", "date"),
          scope_field_id: textFromConfig(row.formula_config, "scope_field_id"),
          filters: [],
        },
        period_start: period.period_start,
        period_end: period.period_end,
      });
    },
    onSuccess: () => {
      setActionError("");
      queryClient.invalidateQueries({ queryKey: ["standards-me-indicators"] });
      queryClient.invalidateQueries({ queryKey: ["standards-me-indicator-values-all"] });
    },
    onError: (err) => setActionError(getApiErrorMessage(err, "Failed to recalculate KPI.")),
  });

  const columns: DataTableColumn<MEIndicator>[] = [
    {
      key: "indicator_name",
      header: "KPI",
      render: (row) => (
        <Link href={`/federal/standards/me-indicators/${row.id}`} className="font-medium text-brand-700 hover:underline">
          {row.indicator_name}
        </Link>
      ),
    },
    { key: "indicator_code", header: "Code", render: (row) => row.indicator_code },
    {
      key: "kpi_type",
      header: "KPI Type",
      render: (row) => formatStatus(textFromConfig(row.formula_config, "indicator_type", "quantitative")),
    },
    {
      key: "input_mode",
      header: "Input Mode",
      render: (row) => formatStatus(normalizeInputMode(row.input_mode ?? textFromConfig(row.formula_config, "input_mode", "manual"))),
    },
    {
      key: "reporting_frequency",
      header: "Frequency",
      render: (row) => row.reporting_frequency.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase()),
    },
    {
      key: "latest_value",
      header: "Latest Value",
      render: (row) => {
        const latest = valueSummary.get(row.id)?.latestApproved ?? valueSummary.get(row.id)?.latest;
        if (!latest) return "-";
        const indicatorType = textFromConfig(row.formula_config, "indicator_type", "quantitative");
        if (indicatorType === "qualitative") return latest.qualitative_category || latest.qualitative_value_text || latest.qualitative_rating || "-";
        return latest.cumulative_value_numeric ?? latest.progress_value_numeric ?? "-";
      },
    },
    { key: "target", header: "Target", render: (row) => row.target_value ?? textFromConfig(row.formula_config, "target_value", "-") },
    {
      key: "achievement",
      header: "Achievement",
      render: (row) => {
        const latest = valueSummary.get(row.id)?.latestApproved ?? valueSummary.get(row.id)?.latest;
        const target = numeric(row.target_value ?? textFromConfig(row.formula_config, "target_value"));
        const current = numeric(latest?.cumulative_value_numeric) ?? numeric(latest?.progress_value_numeric);
        if (!target || current == null) return "-";
        return `${Math.round((current / target) * 100)}%`;
      },
    },
    {
      key: "status",
      header: "Status",
      render: (row) => (
        <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
          row.status === "active" ? "bg-brand-50 text-brand-700" :
          row.status === "draft" ? "bg-neutral-100 text-neutral-700" :
          row.status === "retired" ? "bg-neutral-100 text-neutral-500" :
          "bg-warning-50 text-warning-700"
        }`}>
          {row.status.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase())}
        </span>
      ),
    },
    {
      key: "updated_at",
      header: "Last Updated",
      render: (row) => {
        const latest = valueSummary.get(row.id)?.latest;
        return latest?.updated_at ? new Date(latest.updated_at).toLocaleDateString() : new Date(row.updated_at).toLocaleDateString();
      },
    },
    {
      key: "id",
      header: "Action",
      render: (row) => {
        const inputMode = normalizeInputMode(row.input_mode ?? textFromConfig(row.formula_config, "input_mode", "manual"));
        const latest = valueSummary.get(row.id)?.latestApproved ?? valueSummary.get(row.id)?.latest;
        const canRecalculate = inputMode === "automatic" || inputMode === "hybrid";
        const canEnterData = inputMode === "manual";
        const canImport = inputMode === "manual" || inputMode === "imported";
        return (
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => openEdit(row)} className="rounded border border-neutral-200 px-3 py-1.5 text-xs font-semibold text-neutral-700 hover:bg-neutral-50">
              Edit KPI
            </button>
            {canEnterData ? (
              <button type="button" onClick={() => setDataEntryIndicator(row)} className="rounded border border-brand-200 px-3 py-1.5 text-xs font-semibold text-brand-700 hover:bg-brand-50">
                Enter Data
              </button>
            ) : null}
            {canImport ? (
              <button type="button" onClick={() => setImportIndicator(row)} className="rounded border border-neutral-200 px-3 py-1.5 text-xs font-semibold text-neutral-700 hover:bg-neutral-50">
                {inputMode === "imported" ? "View Imported Records" : "Import"}
              </button>
            ) : null}
            {canRecalculate ? (
              <>
                <Link href={`/federal/standards/me-indicators/${row.id}`} className="rounded border border-neutral-200 px-3 py-1.5 text-xs font-semibold text-neutral-700 hover:bg-neutral-50">
                  View Calculation
                </Link>
                <Link href={`/federal/standards/me-indicators/${row.id}`} className="rounded border border-neutral-200 px-3 py-1.5 text-xs font-semibold text-neutral-700 hover:bg-neutral-50">
                  View Source Records
                </Link>
                <button type="button" onClick={() => recalculateMutation.mutate(row)} className="rounded border border-brand-200 px-3 py-1.5 text-xs font-semibold text-brand-700 hover:bg-brand-50" disabled={recalculateMutation.isPending}>
                  {latest ? "Recalculate" : "Calculate"}
                </button>
              </>
            ) : null}
            {inputMode === "hybrid" ? (
              <button type="button" onClick={() => setDataEntryIndicator(row)} className="rounded border border-warning-200 px-3 py-1.5 text-xs font-semibold text-warning-700 hover:bg-warning-50">
                Override Value
              </button>
            ) : null}
            {row.status === "draft" ? (
              <button
                type="button"
                onClick={() => activateMutation.mutate(row.id)}
                className="rounded border border-neutral-200 px-3 py-1.5 text-xs font-semibold text-neutral-700 hover:bg-neutral-50"
              >
                Activate
              </button>
            ) : null}
          </div>
        );
      },
    },
  ];

  return (
    <StandardsPolicyWorkspaceShell workspace="reporting-me" title="Food Handlers KPI Indicator Engine" description="Configure national Food Handler KPIs, operational data sources, targets, and reporting periods.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="flex flex-wrap items-end gap-3">
            <label className="text-sm font-medium text-neutral-700">
              Period start
              <input type="date" className="mt-1 h-10 rounded border border-neutral-200 px-3 text-sm" value={dashboardFilters.period_start} onChange={(event) => updateDashboardFilter("period_start", event.target.value)} />
            </label>
            <label className="text-sm font-medium text-neutral-700">
              Period end
              <input type="date" className="mt-1 h-10 rounded border border-neutral-200 px-3 text-sm" value={dashboardFilters.period_end} onChange={(event) => updateDashboardFilter("period_end", event.target.value)} />
            </label>
            <label className="text-sm font-medium text-neutral-700">
              KPI status
              <select className="mt-1 h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={dashboardFilters.status} onChange={(event) => updateDashboardFilter("status", event.target.value)}>
                <option value="">All statuses</option>
                <option value="draft">Draft</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="retired">Retired</option>
                <option value="archived">Archived</option>
              </select>
            </label>
            <label className="text-sm font-medium text-neutral-700">
              Input mode
              <select className="mt-1 h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={dashboardFilters.input_mode} onChange={(event) => updateDashboardFilter("input_mode", event.target.value)}>
                <option value="">All modes</option>
                <option value="automatic">Automatic</option>
                <option value="manual">Manual</option>
                <option value="imported">Imported</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </label>
            <label className="text-sm font-medium text-neutral-700">
              Source
              <select className="mt-1 h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={dashboardFilters.data_source} onChange={(event) => updateDashboardFilter("data_source", event.target.value)}>
                <option value="">All sources</option>
                {KPI_DATA_SOURCES.map((source) => <option key={source} value={source}>{formatStatus(source)}</option>)}
              </select>
            </label>
            <button type="button" onClick={() => setDashboardFilters({ period_start: "", period_end: "", status: "", input_mode: "", data_source: "" })} className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50">
              Reset Dashboard
            </button>
          </div>
        </section>

        <DashboardPanel summary={dashboardSummary} isLoading={dashboardLoading} />

        <section className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div>
            <p className="text-sm font-semibold text-neutral-900">{filteredRows.length} of {rows.length} KPIs</p>
            <p className="mt-1 text-sm text-neutral-500">Search, filter, export, and identify Food Handler KPIs due for reporting.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => exportRows(filteredRows.map((row) => {
              const latest = valueSummary.get(row.id)?.latestApproved ?? valueSummary.get(row.id)?.latest;
              const target = row.target_value ?? textFromConfig(row.formula_config, "target_value", "");
              const current = numeric(latest?.cumulative_value_numeric) ?? numeric(latest?.progress_value_numeric);
              const achievement = numeric(target) && current != null ? `${Math.round((current / Number(target)) * 100)}%` : "";
              return {
                kpi: row.indicator_name,
                code: row.indicator_code,
                type: textFromConfig(row.formula_config, "indicator_type", "quantitative"),
                input_mode: row.input_mode ?? textFromConfig(row.formula_config, "input_mode", "manual"),
                reporting_frequency: row.reporting_frequency,
                latest_value: latest ? String(latest.cumulative_value_numeric ?? latest.progress_value_numeric ?? latest.qualitative_category ?? latest.qualitative_value_text ?? "") : "",
                target: target == null ? "" : String(target),
                achievement,
                status: row.status,
                last_updated: latest?.updated_at ?? row.updated_at,
              };
            }))} className="inline-flex h-10 items-center rounded-md border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50">Export List</button>
            <button type="button" disabled={importableRows.length === 0} onClick={() => setImportIndicator(importableRows[0])} className="inline-flex h-10 items-center rounded-md border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50 disabled:text-neutral-400">Bulk Import</button>
            <button type="button" disabled className="inline-flex h-10 items-center rounded-md border border-neutral-200 px-4 text-sm font-semibold text-neutral-400">Archive Selected</button>
            <button type="button" onClick={openCreate} className="inline-flex h-10 items-center rounded-md bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700">
              Build KPI
            </button>
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <input className="h-10 rounded border border-neutral-200 px-3 text-sm" placeholder="Search name, code, description" value={filters.search} onChange={(event) => updateFilter("search", event.target.value)} />
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={filters.indicator_type} onChange={(event) => updateFilter("indicator_type", event.target.value)}>
              <option value="">All types</option>
              <option value="quantitative">Quantitative</option>
              <option value="qualitative">Qualitative</option>
            </select>
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={filters.status} onChange={(event) => updateFilter("status", event.target.value)}>
              <option value="">All statuses</option>
              <option value="draft">Draft</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="retired">Retired</option>
            </select>
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={filters.reporting_frequency} onChange={(event) => updateFilter("reporting_frequency", event.target.value)}>
              <option value="">All frequencies</option>
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="biannual">Biannual</option>
              <option value="annual">Annual</option>
              <option value="ad_hoc">Ad hoc</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="custom">Custom</option>
            </select>
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={filters.due_for_reporting} onChange={(event) => updateFilter("due_for_reporting", event.target.value)}>
              <option value="">All due states</option>
              <option value="true">Due for reporting</option>
              <option value="false">Not due</option>
            </select>
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm xl:col-span-2" value={filters.created_by} onChange={(event) => updateFilter("created_by", event.target.value)}>
              <option value="">All creators</option>
              {optionSets.creators.map((option) => <option key={option} value={option}>{option}</option>)}
            </select>
            <button type="button" onClick={() => { setFilters({ search: "", indicator_type: "", status: "", reporting_frequency: "", due_for_reporting: "", created_by: "" }); setPage(1); }} className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50">
              Clear Filters
            </button>
          </div>
        </section>

        {!preferredCreateVersion ? (
          <div className="rounded border border-warning-100 bg-warning-50 p-3 text-sm text-warning-700">
            Create a policy version before adding KPIs.
          </div>
        ) : preferredCreateVersion.status !== "draft" && preferredCreateVersion.status !== "returned" ? (
          <div className="rounded border border-info-100 bg-info-50 p-3 text-sm text-info-700">
            New KPIs will open against the latest available policy version: <span className="font-semibold">{preferredCreateVersion.version_code}</span>.
          </div>
        ) : null}
        {actionError ? <div className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{actionError}</div> : null}

        {isLoading ? (
          <p className="text-sm text-neutral-500">Loading...</p>
        ) : (
          <>
            <DataTable<MEIndicator>
              columns={columns}
              rows={pagedRows}
              empty="No KPIs match the current filters."
            />
            <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-neutral-200 bg-white px-4 py-3 text-sm text-neutral-600">
              <span>Page {Math.min(page, pageCount)} of {pageCount}</span>
              <div className="flex gap-2">
                <button type="button" disabled={page <= 1} onClick={() => setPage((current) => Math.max(1, current - 1))} className="h-9 rounded border border-neutral-200 px-3 font-semibold disabled:opacity-50">Previous</button>
                <button type="button" disabled={page >= pageCount} onClick={() => setPage((current) => Math.min(pageCount, current + 1))} className="h-9 rounded border border-neutral-200 px-3 font-semibold disabled:opacity-50">Next</button>
              </div>
            </div>
          </>
        )}
      </div>
      <MEIndicatorFormDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onSuccess={() => setDrawerOpen(false)}
        mode={drawerMode}
        policyVersionId={policyVersionId}
        initial={editing}
      />
      {dataEntryIndicator ? (
        <IndicatorDataEntryModal indicator={dataEntryIndicator} onClose={() => setDataEntryIndicator(null)} />
      ) : null}
      {importIndicator ? (
        <IndicatorImportModal
          indicator={importIndicator}
          onClose={() => setImportIndicator(null)}
          onImported={() => {
            queryClient.invalidateQueries({ queryKey: ["standards-me-indicator-values-all"] });
            queryClient.invalidateQueries({ queryKey: ["standards-me-indicator-values", importIndicator.id] });
          }}
        />
      ) : null}
    </StandardsPolicyWorkspaceShell>
  );
}
