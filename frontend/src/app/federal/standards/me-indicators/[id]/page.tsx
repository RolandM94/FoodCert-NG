"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getApiErrorMessage } from "@/lib/api/client";
import {
  calculateMEIndicator,
  getMEIndicator,
  listMEIndicatorDataSources,
  listMEIndicatorValues,
} from "@/lib/api/standards";
import { MEIndicatorFormDrawer } from "@/features/standards/me-indicator-form-drawer";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import type { MEIndicatorValue } from "@/types/standards";

type DetailTab = "values" | "disaggregation" | "history" | "sources";

function nice(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function statusClass(status: string) {
  if (status === "approved" || status === "active") return "bg-brand-50 text-brand-700";
  if (status === "submitted") return "bg-info-50 text-info-700";
  if (status === "rejected") return "bg-danger-50 text-danger-700";
  if (status === "draft") return "bg-neutral-100 text-neutral-700";
  return "bg-warning-50 text-warning-700";
}

function numericValue(value?: string | number | null) {
  if (value == null || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function displayValue(value: MEIndicatorValue | undefined, isQualitative: boolean) {
  if (!value) return "-";
  if (isQualitative) return value.qualitative_category || value.qualitative_value_text || String(value.qualitative_rating ?? "-");
  return value.cumulative_value_numeric ?? value.progress_value_numeric ?? "-";
}

function exportIndicatorSnapshot(indicatorName: string, payload: unknown) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${indicatorName.replace(/\W+/g, "-").toLowerCase()}-snapshot.json`;
  link.click();
  URL.revokeObjectURL(url);
}

export default function MEIndicatorDetailPage() {
  const params = useParams<{ id: string }>();
  const indicatorId = params.id;
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<DetailTab>("values");
  const [editOpen, setEditOpen] = useState(false);
  const [error, setError] = useState("");

  const indicatorQuery = useQuery({
    queryKey: ["standards-me-indicator", indicatorId],
    queryFn: () => getMEIndicator(indicatorId),
  });
  const valuesQuery = useQuery({
    queryKey: ["standards-me-indicator-values", indicatorId],
    queryFn: () => listMEIndicatorValues(indicatorId),
  });
  const sourcesQuery = useQuery({
    queryKey: ["standards-me-indicator-data-sources", indicatorId],
    queryFn: () => listMEIndicatorDataSources(indicatorId),
  });

  const indicator = indicatorQuery.data;
  const values = useMemo(() => (
    Array.isArray(valuesQuery.data) ? valuesQuery.data : []
  ), [valuesQuery.data]);
  const sources = Array.isArray(sourcesQuery.data) ? sourcesQuery.data : [];
  const indicatorType = String(indicator?.formula_config?.indicator_type || "quantitative");
  const inputMode = indicator?.input_mode === "automated" ? "automatic" : (indicator?.input_mode ?? String(indicator?.formula_config?.input_mode ?? "manual"));
  const isQualitative = indicatorType === "qualitative";
  const approvedValues = values.filter((value) => value.approval_status === "approved");
  const latestApproved = approvedValues[0] ?? values[0];
  const latestProgress = numericValue(latestApproved?.progress_value_numeric);
  const latestCumulative = numericValue(latestApproved?.cumulative_value_numeric);
  const target = indicator?.target_value == null ? null : Number(indicator.target_value);
  const achievement = target && target !== 0
    ? Math.round(((latestCumulative ?? latestProgress ?? 0) / target) * 100)
    : null;
  const baseline = String(indicator?.formula_config?.baseline_value ?? "0");
  const currentTarget = String(indicator?.formula_config?.target_value ?? indicator?.target_value ?? "-");
  const currentPeriod = latestApproved
    ? { period_start: latestApproved.period_start, period_end: latestApproved.period_end }
    : { period_start: "2026-04-01", period_end: "2026-06-30" };

  const allHistory = useMemo(() => (
    values.flatMap((value) => (value.history || []).map((item) => ({ ...item, value })))
  ), [values]);
  const disaggregatedRows = values.flatMap((value) => value.disaggregated_values || []);

  const recalculateMutation = useMutation({
    mutationFn: async () => {
      const source = sources[0];
      if (!source) throw new Error("No linked data source is configured for recalculation.");
      return calculateMEIndicator(indicatorId, {
        data_source_id: source.id,
        period_start: currentPeriod.period_start,
        period_end: currentPeriod.period_end,
      });
    },
    onSuccess: () => {
      setError("");
      queryClient.invalidateQueries({ queryKey: ["standards-me-indicator-values", indicatorId] });
    },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to recalculate indicator.")),
  });

  if (indicatorQuery.isLoading) {
    return (
      <StandardsPolicyWorkspaceShell workspace="reporting-me" title="KPI" description="Loading KPI details.">
        <p className="text-sm text-neutral-500">Loading...</p>
      </StandardsPolicyWorkspaceShell>
    );
  }

  if (!indicator) {
    return (
      <StandardsPolicyWorkspaceShell workspace="reporting-me" title="KPI" description="KPI detail.">
        <div className="rounded-lg border border-danger-100 bg-danger-50 p-4 text-sm font-semibold text-danger-700">KPI not found.</div>
      </StandardsPolicyWorkspaceShell>
    );
  }

  return (
    <StandardsPolicyWorkspaceShell workspace="reporting-me" title="KPI Detail" description="Configuration, performance values, operational sources, and audit history for this KPI.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0">
              <Link href="/federal/standards/me-indicators" className="text-sm font-semibold text-brand-700 hover:underline">Back to KPIs</Link>
              <h1 className="mt-2 text-2xl font-semibold text-neutral-950">{indicator.indicator_name}</h1>
              <p className="mt-1 text-sm text-neutral-500">{indicator.description || "No description available."}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                <span className="rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-semibold text-neutral-700">{nice(indicatorType)}</span>
                <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${statusClass(indicator.status)}`}>{nice(indicator.status)}</span>
                <span className="rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-semibold text-neutral-700">{indicator.indicator_code}</span>
                <span className="rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-semibold text-neutral-700">{nice(inputMode)}</span>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <button type="button" onClick={() => setEditOpen(true)} className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50">Edit</button>
              {inputMode === "manual" ? <button type="button" onClick={() => setActiveTab("values")} className="h-10 rounded border border-brand-200 px-4 text-sm font-semibold text-brand-700 hover:bg-brand-50">Enter Data</button> : null}
              {(inputMode === "automatic" || inputMode === "hybrid") ? <button type="button" onClick={() => setActiveTab("sources")} className="h-10 rounded border border-brand-200 px-4 text-sm font-semibold text-brand-700 hover:bg-brand-50">View Source Records</button> : null}
              {(inputMode === "automatic" || inputMode === "hybrid") ? (
                <button type="button" disabled={recalculateMutation.isPending || sources.length === 0} onClick={() => recalculateMutation.mutate()} className="h-10 rounded bg-brand-600 px-4 text-sm font-semibold text-white disabled:opacity-60">Recalculate</button>
              ) : null}
              <button type="button" onClick={() => exportIndicatorSnapshot(indicator.indicator_name, { indicator, values, sources })} className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50">Export</button>
            </div>
          </div>
          {error ? <div className="mt-4 rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</div> : null}
        </section>

        <section className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
          {[
            ["Baseline", baseline],
            ["Latest progress", latestProgress == null ? "-" : latestProgress],
            ["Latest cumulative", latestCumulative == null ? "-" : latestCumulative],
            ["Current target", currentTarget],
            ["Achievement", achievement == null ? "-" : `${achievement}%`],
            ["Last updated", latestApproved?.updated_at ? new Date(latestApproved.updated_at).toLocaleDateString() : "-"],
          ].map(([label, value]) => (
            <div key={label} className="rounded-lg border border-neutral-200 bg-white p-4">
              <p className="text-xs font-semibold uppercase text-neutral-500">{label}</p>
              <p className="mt-2 truncate text-xl font-semibold text-neutral-950">{value}</p>
            </div>
          ))}
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white p-5">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-base font-semibold text-neutral-950">{isQualitative ? "Narrative Timeline" : "Trend View"}</h2>
            <span className="text-xs font-semibold text-neutral-500">{values.length} values</span>
          </div>
          {isQualitative ? (
            <div className="mt-4 space-y-3">
              {values.slice(0, 6).map((value) => (
                <div className="rounded-md border border-neutral-200 p-3" key={value.id}>
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-neutral-900">{value.period_start} to {value.period_end}</p>
                    <span className={`rounded-full px-2 py-1 text-xs font-semibold ${statusClass(value.approval_status)}`}>{nice(value.approval_status)}</span>
                  </div>
                  <p className="mt-2 text-sm text-neutral-600">{value.qualitative_value_text || value.qualitative_category || "No narrative captured."}</p>
                </div>
              ))}
              {!values.length ? <p className="text-sm text-neutral-500">No qualitative values captured yet.</p> : null}
            </div>
          ) : (
            <div className="mt-4 grid gap-2">
              {values.slice().reverse().slice(0, 8).map((value) => {
                const amount = numericValue(value.cumulative_value_numeric) ?? numericValue(value.progress_value_numeric) ?? 0;
                const width = target && target > 0 ? Math.min(100, Math.max(4, (amount / target) * 100)) : Math.min(100, Math.max(4, amount));
                return (
                  <div className="grid gap-2 md:grid-cols-[180px_minmax(0,1fr)_90px]" key={value.id}>
                    <span className="text-sm text-neutral-600">{value.period_end}</span>
                    <div className="h-8 rounded bg-neutral-100">
                      <div className="h-8 rounded bg-brand-500" style={{ width: `${width}%` }} />
                    </div>
                    <span className="text-sm font-semibold text-neutral-900">{amount}</span>
                  </div>
                );
              })}
              {!values.length ? <p className="text-sm text-neutral-500">No values captured yet.</p> : null}
            </div>
          )}
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white">
          <div className="flex gap-1 overflow-x-auto border-b border-neutral-200 px-4">
            {[
              ["values", "Values"],
              ["disaggregation", "Disaggregation"],
              ["history", "History"],
              ["sources", "Linked Sources"],
            ].map(([key, label]) => (
              <button key={key} type="button" onClick={() => setActiveTab(key as DetailTab)} className={`border-b-2 px-3 py-3 text-sm font-semibold ${activeTab === key ? "border-brand-600 text-brand-700" : "border-transparent text-neutral-500"}`}>
                {label}
              </button>
            ))}
          </div>

          <div className="p-4">
            {activeTab === "values" ? (
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead className="text-left text-xs uppercase text-neutral-500"><tr><th className="py-2 pr-4">Period</th><th className="py-2 pr-4">Progress</th><th className="py-2 pr-4">Cumulative</th><th className="py-2 pr-4">Target</th><th className="py-2 pr-4">Status</th><th className="py-2 pr-4">Source</th><th className="py-2 pr-4">Updated By</th><th className="py-2 pr-4">Updated</th></tr></thead>
                  <tbody>
                    {values.map((value) => (
                      <tr className="border-t border-neutral-100" key={value.id}>
                        <td className="py-3 pr-4">{value.period_start} to {value.period_end}</td>
                        <td className="py-3 pr-4">{isQualitative ? displayValue(value, true) : value.progress_value_numeric ?? "-"}</td>
                        <td className="py-3 pr-4">{isQualitative ? value.qualitative_rating ?? "-" : value.cumulative_value_numeric ?? "-"}</td>
                        <td className="py-3 pr-4">{currentTarget}</td>
                        <td className="py-3 pr-4"><span className={`rounded-full px-2 py-1 text-xs font-semibold ${statusClass(value.approval_status)}`}>{nice(value.approval_status)}</span></td>
                        <td className="py-3 pr-4">{nice(value.value_source)}</td>
                        <td className="py-3 pr-4">{value.created_by_name || value.submitted_by_name || "-"}</td>
                        <td className="py-3 pr-4">{new Date(value.updated_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                    {!values.length ? <tr><td className="py-6 text-neutral-500" colSpan={8}>No values captured yet.</td></tr> : null}
                  </tbody>
                </table>
              </div>
            ) : null}

            {activeTab === "disaggregation" ? (
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead className="text-left text-xs uppercase text-neutral-500"><tr><th className="py-2 pr-4">Period</th><th className="py-2 pr-4">Dimensions</th><th className="py-2 pr-4">Value</th></tr></thead>
                  <tbody>
                    {disaggregatedRows.map((row) => (
                      <tr className="border-t border-neutral-100" key={row.id}>
                        <td className="py-3 pr-4">{row.period_start} to {row.period_end}</td>
                        <td className="py-3 pr-4">{Object.entries(row.dimension_values_json).map(([key, value]) => `${key}: ${value}`).join(", ")}</td>
                        <td className="py-3 pr-4 font-semibold">{row.value_numeric}</td>
                      </tr>
                    ))}
                    {!disaggregatedRows.length ? <tr><td className="py-6 text-neutral-500" colSpan={3}>No disaggregated values generated yet.</td></tr> : null}
                  </tbody>
                </table>
              </div>
            ) : null}

            {activeTab === "history" ? (
              <div className="space-y-3">
                {allHistory.map((item) => (
                  <div className="rounded-md border border-neutral-200 p-3" key={item.id}>
                    <p className="text-sm font-semibold text-neutral-950">{nice(item.action)}: {item.value.period_start} to {item.value.period_end}</p>
                    <p className="mt-1 text-xs text-neutral-500">{item.actor_name || "System"} · {new Date(item.created_at).toLocaleString()}</p>
                    {item.comment ? <p className="mt-2 text-sm text-neutral-600">{item.comment}</p> : null}
                  </div>
                ))}
                {!allHistory.length ? <p className="text-sm text-neutral-500">No history captured yet.</p> : null}
              </div>
            ) : null}

            {activeTab === "sources" ? (
              <div className="grid gap-3">
                {sources.map((source) => (
                  <div className="rounded-md border border-neutral-200 p-3" key={source.id}>
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <p className="text-sm font-semibold text-neutral-950">{nice(source.source_type)} · {nice(source.calculation_method)}</p>
                      <span className="text-xs font-semibold text-neutral-500">{nice(source.period_filter_mode)}</span>
                    </div>
                    <p className="mt-2 text-xs text-neutral-500">Value field: {source.value_field_id || "-"} · Source ID: {source.source_id || "-"}</p>
                  </div>
                ))}
                {!sources.length ? <p className="text-sm text-neutral-500">No linked data sources configured.</p> : null}
              </div>
            ) : null}
          </div>
        </section>
      </div>

      <MEIndicatorFormDrawer
        open={editOpen}
        onClose={() => setEditOpen(false)}
        onSuccess={() => {
          setEditOpen(false);
          queryClient.invalidateQueries({ queryKey: ["standards-me-indicator", indicatorId] });
        }}
        mode="edit"
        policyVersionId={indicator.policy_version}
        initial={indicator}
      />
    </StandardsPolicyWorkspaceShell>
  );
}
