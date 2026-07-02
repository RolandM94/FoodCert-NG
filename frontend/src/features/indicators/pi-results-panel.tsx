"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { getApiErrorMessage } from "@/lib/api/client";
import {
  aiExplainIndicatorResult,
  listIndicatorResults,
  listPerformanceIndicators,
} from "@/lib/api/performance-indicators";
import type { IndicatorAIExplanation, MEIndicatorValue } from "@/types/standards";

const SEVERITY_PILL: Record<string, { className: string; symbol: string }> = {
  good: { className: "bg-brand-50 text-brand-700", symbol: "●" },
  warning: { className: "bg-warning-50 text-warning-700", symbol: "▲" },
  critical: { className: "bg-danger-50 text-danger-700", symbol: "■" },
};

function BandPill({ band, severity }: { band: string; severity: string }) {
  if (!band) return <span className="text-neutral-400">—</span>;
  const pill = SEVERITY_PILL[severity] ?? { className: "bg-neutral-100 text-neutral-700", symbol: "●" };
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${pill.className}`}>
      <span aria-hidden>{pill.symbol}</span>
      {band}
    </span>
  );
}

function toNumber(value: string | number | null | undefined): number | null {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

/** Single-series trend line: brand hue, one axis, recessive grid, hover tooltips, labeled target reference. */
function TrendChart({ values }: { values: MEIndicatorValue[] }) {
  const points = useMemo(
    () =>
      [...values]
        .sort((a, b) => a.period_end.localeCompare(b.period_end))
        .map((value) => ({
          period: value.period_end,
          y: toNumber(value.cumulative_value_numeric ?? value.progress_value_numeric),
          target: toNumber(value.target_value),
        }))
        .filter((point): point is { period: string; y: number; target: number | null } => point.y !== null),
    [values],
  );

  if (points.length < 2) {
    return <p className="text-sm text-neutral-500">Not enough result history to draw a trend yet.</p>;
  }

  const width = 640;
  const height = 220;
  const pad = { top: 16, right: 96, bottom: 28, left: 44 };
  const target = points.find((point) => point.target !== null)?.target ?? null;
  const yValues = points.map((point) => point.y).concat(target !== null ? [target] : []);
  const yMin = Math.min(...yValues);
  const yMax = Math.max(...yValues);
  const range = yMax - yMin || 1;
  const yLo = yMin - range * 0.12;
  const yHi = yMax + range * 0.12;

  const x = (index: number) => pad.left + (index / (points.length - 1)) * (width - pad.left - pad.right);
  const y = (value: number) => pad.top + (1 - (value - yLo) / (yHi - yLo)) * (height - pad.top - pad.bottom);

  const path = points.map((point, index) => `${index === 0 ? "M" : "L"}${x(index).toFixed(1)},${y(point.y).toFixed(1)}`).join(" ");
  const last = points[points.length - 1];
  const gridValues = [yLo + (yHi - yLo) * 0.25, yLo + (yHi - yLo) * 0.5, yLo + (yHi - yLo) * 0.75];

  return (
    <svg
      role="img"
      aria-label={`Trend of the last ${points.length} results${target !== null ? ` against a target of ${target}` : ""}`}
      viewBox={`0 0 ${width} ${height}`}
      className="w-full"
    >
      {gridValues.map((gridValue) => (
        <g key={gridValue}>
          <line x1={pad.left} x2={width - pad.right} y1={y(gridValue)} y2={y(gridValue)} stroke="#E5E7EB" strokeWidth={1} />
          <text x={pad.left - 6} y={y(gridValue) + 3} textAnchor="end" fontSize={10} fill="#6B7280">
            {Math.round(gridValue * 10) / 10}
          </text>
        </g>
      ))}
      {target !== null ? (
        <g>
          <line x1={pad.left} x2={width - pad.right} y1={y(target)} y2={y(target)} stroke="#9CA3AF" strokeWidth={1.5} strokeDasharray="5 4" />
          <text x={width - pad.right + 6} y={y(target) + 3} fontSize={10} fontWeight={600} fill="#6B7280">
            Target {target}
          </text>
        </g>
      ) : null}
      <path d={path} fill="none" stroke="#16A34A" strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
      {points.map((point, index) => (
        <circle key={point.period} cx={x(index)} cy={y(point.y)} r={4} fill="#16A34A" stroke="#FFFFFF" strokeWidth={2}>
          <title>{`${point.period}: ${point.y}${target !== null ? ` (target ${target})` : ""}`}</title>
        </circle>
      ))}
      <text x={x(points.length - 1) + 8} y={y(last.y) + 3} fontSize={11} fontWeight={700} fill="#111827">
        {last.y}
      </text>
      <text x={pad.left} y={height - 6} fontSize={10} fill="#6B7280">{points[0].period}</text>
      <text x={width - pad.right} y={height - 6} fontSize={10} textAnchor="end" fill="#6B7280">{last.period}</text>
    </svg>
  );
}

export function PIResultsPanel({ filterParams }: { filterParams?: Record<string, string> }) {
  const [selectedId, setSelectedId] = useState<string>("");
  const [explanation, setExplanation] = useState<IndicatorAIExplanation | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);

  const indicatorsQuery = useQuery({
    queryKey: ["pi-results-indicators", filterParams ?? {}],
    queryFn: () => listPerformanceIndicators(filterParams),
  });
  const indicators = useMemo(() => (Array.isArray(indicatorsQuery.data) ? indicatorsQuery.data : []), [indicatorsQuery.data]);
  const activeId = selectedId || indicators[0]?.id || "";
  const activeIndicator = indicators.find((indicator) => indicator.id === activeId) ?? null;

  const resultsQuery = useQuery({
    queryKey: ["pi-results", activeId],
    queryFn: () => listIndicatorResults(activeId),
    enabled: Boolean(activeId),
  });
  const results = useMemo(() => (Array.isArray(resultsQuery.data) ? resultsQuery.data : []), [resultsQuery.data]);

  const explainMutation = useMutation({
    mutationFn: () => aiExplainIndicatorResult(activeId),
    onSuccess: (data) => { setExplanation(data); setAiError(null); },
    onError: (error) => { setAiError(getApiErrorMessage(error, "Could not generate an explanation.")); },
  });

  const columns: DataTableColumn<MEIndicatorValue>[] = [
    { key: "period", header: "Period", render: (row) => `${row.period_start} → ${row.period_end}` },
    { key: "value", header: "Value", render: (row) => <span className="tabular-nums">{row.cumulative_value_numeric ?? row.progress_value_numeric ?? "—"}</span> },
    { key: "target", header: "Target", render: (row) => <span className="tabular-nums">{row.target_value ?? "—"}</span> },
    { key: "variance", header: "Variance", render: (row) => <span className="tabular-nums">{row.variance_from_target ?? "—"}</span> },
    { key: "band", header: "Band", render: (row) => <BandPill band={row.performance_band} severity={row.performance_severity} /> },
    { key: "source", header: "Source", render: (row) => row.value_source },
    { key: "approval", header: "Approval", render: (row) => row.approval_status },
  ];

  return (
    <div className="grid gap-5">
      <div className="flex flex-wrap items-center gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
        <label className="text-sm font-semibold text-neutral-700" htmlFor="pi-results-indicator">Indicator</label>
        <select
          id="pi-results-indicator"
          className="h-10 min-w-64 rounded-md border border-neutral-200 bg-white px-3 text-sm"
          value={activeId}
          onChange={(event) => { setSelectedId(event.target.value); setExplanation(null); setAiError(null); }}
        >
          {indicators.map((indicator) => (
            <option key={indicator.id} value={indicator.id}>
              {indicator.indicator_name} ({indicator.indicator_code})
            </option>
          ))}
        </select>
        {activeIndicator ? (
          <button
            className="ml-auto inline-flex h-10 items-center rounded-md border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50 disabled:opacity-50"
            disabled={explainMutation.isPending}
            onClick={() => explainMutation.mutate()}
            type="button"
          >
            {explainMutation.isPending ? "Explaining…" : "Explain with AI"}
          </button>
        ) : null}
      </div>

      {aiError ? <p className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{aiError}</p> : null}
      {explanation ? (
        <section className="rounded-lg border border-brand-100 bg-brand-50 p-4">
          <h3 className="text-sm font-bold text-brand-700">AI explanation — review before acting</h3>
          <p className="mt-1 text-sm leading-6 text-neutral-800">{explanation.narrative}</p>
        </section>
      ) : null}

      <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
        <h3 className="mb-3 text-sm font-semibold text-neutral-900">
          {activeIndicator ? `${activeIndicator.indicator_name} — result trend` : "Result trend"}
        </h3>
        {resultsQuery.isLoading ? <p className="text-sm text-neutral-500">Loading results…</p> : <TrendChart values={results} />}
      </section>

      <DataTable<MEIndicatorValue>
        columns={columns}
        rows={results}
        empty="No results recorded for this indicator yet. Run a calculation or add a manual entry."
      />
    </div>
  );
}
