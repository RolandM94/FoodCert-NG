"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { getApiErrorMessage } from "@/lib/api/client";
import {
  createIndicatorTarget,
  createIndicatorThreshold,
  deleteIndicatorTarget,
  deleteIndicatorThreshold,
  listIndicatorTargets,
  listIndicatorThresholds,
  listPerformanceIndicators,
} from "@/lib/api/performance-indicators";
import type { IndicatorTarget, IndicatorThreshold } from "@/types/standards";

const SCOPE_OPTIONS = ["national", "state", "lga", "employer", "facility", "branch"];
const SEVERITY_OPTIONS = ["good", "warning", "critical"] as const;

export function PITargetsPanel({ readOnlyScopes = [] }: { readOnlyScopes?: string[] }) {
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [targetForm, setTargetForm] = useState({ scope_type: "national", scope_id: "", target_value: "", target_unit: "" });
  const [bandForm, setBandForm] = useState({ band_name: "", severity: "good" as string, min_value: "", max_value: "", color: "#16A34A", action_recommendation: "" });

  const indicatorsQuery = useQuery({ queryKey: ["pi-targets-indicators"], queryFn: () => listPerformanceIndicators() });
  const indicators = useMemo(() => (Array.isArray(indicatorsQuery.data) ? indicatorsQuery.data : []), [indicatorsQuery.data]);
  const activeId = selectedId || indicators[0]?.id || "";

  const targetsQuery = useQuery({
    queryKey: ["pi-targets", activeId],
    queryFn: () => listIndicatorTargets({ indicator: activeId }),
    enabled: Boolean(activeId),
  });
  const thresholdsQuery = useQuery({
    queryKey: ["pi-thresholds", activeId],
    queryFn: () => listIndicatorThresholds({ indicator: activeId }),
    enabled: Boolean(activeId),
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["pi-targets", activeId] });
    queryClient.invalidateQueries({ queryKey: ["pi-thresholds", activeId] });
  };

  const addTarget = useMutation({
    mutationFn: () => createIndicatorTarget({ indicator: activeId, ...targetForm, scope_type: targetForm.scope_type as IndicatorTarget["scope_type"] }),
    onSuccess: () => { setTargetForm({ scope_type: "national", scope_id: "", target_value: "", target_unit: "" }); setError(null); invalidate(); },
    onError: (err) => setError(getApiErrorMessage(err, "Could not save the target.")),
  });
  const addBand = useMutation({
    mutationFn: () => createIndicatorThreshold({
      indicator: activeId,
      scope_type: "national",
      band_name: bandForm.band_name,
      severity: bandForm.severity as IndicatorThreshold["severity"],
      min_value: bandForm.min_value || null,
      max_value: bandForm.max_value || null,
      color: bandForm.color,
      label: bandForm.band_name,
      action_recommendation: bandForm.action_recommendation,
    }),
    onSuccess: () => { setBandForm({ band_name: "", severity: "good", min_value: "", max_value: "", color: "#16A34A", action_recommendation: "" }); setError(null); invalidate(); },
    onError: (err) => setError(getApiErrorMessage(err, "Could not save the threshold band.")),
  });
  const removeTarget = useMutation({
    mutationFn: (id: string) => deleteIndicatorTarget(id),
    onSuccess: invalidate,
    onError: (err) => setError(getApiErrorMessage(err, "Could not delete the target.")),
  });
  const removeBand = useMutation({
    mutationFn: (id: string) => deleteIndicatorThreshold(id),
    onSuccess: invalidate,
    onError: (err) => setError(getApiErrorMessage(err, "Could not delete the threshold band.")),
  });

  const canEdit = readOnlyScopes.length === 0;

  const targetColumns: DataTableColumn<IndicatorTarget>[] = [
    { key: "scope", header: "Scope", render: (row) => `${row.scope_type}${row.scope_id ? `:${row.scope_id}` : ""}` },
    { key: "value", header: "Target", render: (row) => <span className="tabular-nums">{row.target_value} {row.target_unit}</span> },
    { key: "source", header: "Source", render: (row) => row.source.replace(/_/g, " ") },
    { key: "active", header: "Active", render: (row) => (row.is_active ? "Yes" : "No") },
    {
      key: "actions",
      header: "",
      render: (row) =>
        canEdit ? (
          <button
            className="inline-flex h-8 items-center rounded-md bg-danger-50 px-2.5 text-xs font-semibold text-danger-700 hover:bg-danger-100"
            onClick={() => removeTarget.mutate(row.id)}
            type="button"
          >
            Remove
          </button>
        ) : null,
    },
  ];

  const bandColumns: DataTableColumn<IndicatorThreshold>[] = [
    { key: "band", header: "Band", render: (row) => row.band_name },
    { key: "severity", header: "Severity", render: (row) => row.severity },
    { key: "range", header: "Range", render: (row) => `${row.min_value ?? "−∞"} → ${row.max_value ?? "+∞"}` },
    { key: "action", header: "Recommended action", render: (row) => row.action_recommendation || "—" },
    {
      key: "actions",
      header: "",
      render: (row) =>
        canEdit ? (
          <button
            className="inline-flex h-8 items-center rounded-md bg-danger-50 px-2.5 text-xs font-semibold text-danger-700 hover:bg-danger-100"
            onClick={() => removeBand.mutate(row.id)}
            type="button"
          >
            Remove
          </button>
        ) : null,
    },
  ];

  return (
    <div className="grid gap-5">
      <div className="flex flex-wrap items-center gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
        <label className="text-sm font-semibold text-neutral-700" htmlFor="pi-targets-indicator">Indicator</label>
        <select
          id="pi-targets-indicator"
          className="h-10 min-w-64 rounded-md border border-neutral-200 bg-white px-3 text-sm"
          value={activeId}
          onChange={(event) => setSelectedId(event.target.value)}
        >
          {indicators.map((indicator) => (
            <option key={indicator.id} value={indicator.id}>{indicator.indicator_name} ({indicator.indicator_code})</option>
          ))}
        </select>
      </div>

      {error ? <p className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</p> : null}

      <section className="grid gap-3">
        <h3 className="text-sm font-semibold text-neutral-900">Targets</h3>
        <DataTable<IndicatorTarget> columns={targetColumns} rows={Array.isArray(targetsQuery.data) ? targetsQuery.data : []} empty="No targets set yet." />
        {canEdit ? (
          <div className="flex flex-wrap items-end gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <label className="grid gap-1 text-xs font-semibold text-neutral-600">
              Scope
              <select className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm" value={targetForm.scope_type} onChange={(event) => setTargetForm((prev) => ({ ...prev, scope_type: event.target.value }))}>
                {SCOPE_OPTIONS.map((scope) => <option key={scope} value={scope}>{scope}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-xs font-semibold text-neutral-600">
              Scope ID (optional)
              <input className="h-10 rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm" value={targetForm.scope_id} onChange={(event) => setTargetForm((prev) => ({ ...prev, scope_id: event.target.value }))} />
            </label>
            <label className="grid gap-1 text-xs font-semibold text-neutral-600">
              Target value
              <input className="h-10 rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm" value={targetForm.target_value} onChange={(event) => setTargetForm((prev) => ({ ...prev, target_value: event.target.value }))} />
            </label>
            <label className="grid gap-1 text-xs font-semibold text-neutral-600">
              Unit
              <input className="h-10 rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm" placeholder="%" value={targetForm.target_unit} onChange={(event) => setTargetForm((prev) => ({ ...prev, target_unit: event.target.value }))} />
            </label>
            <button
              className="inline-flex h-10 items-center rounded-md bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
              disabled={addTarget.isPending || !targetForm.target_value || !activeId}
              onClick={() => addTarget.mutate()}
              type="button"
            >
              Add target
            </button>
          </div>
        ) : null}
      </section>

      <section className="grid gap-3">
        <h3 className="text-sm font-semibold text-neutral-900">Threshold bands</h3>
        <DataTable<IndicatorThreshold> columns={bandColumns} rows={Array.isArray(thresholdsQuery.data) ? thresholdsQuery.data : []} empty="No threshold bands configured yet." />
        {canEdit ? (
          <div className="flex flex-wrap items-end gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <label className="grid gap-1 text-xs font-semibold text-neutral-600">
              Band name
              <input className="h-10 rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm" placeholder="Green" value={bandForm.band_name} onChange={(event) => setBandForm((prev) => ({ ...prev, band_name: event.target.value }))} />
            </label>
            <label className="grid gap-1 text-xs font-semibold text-neutral-600">
              Severity
              <select className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm" value={bandForm.severity} onChange={(event) => setBandForm((prev) => ({ ...prev, severity: event.target.value }))}>
                {SEVERITY_OPTIONS.map((severity) => <option key={severity} value={severity}>{severity}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-xs font-semibold text-neutral-600">
              Min value
              <input className="h-10 rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm" value={bandForm.min_value} onChange={(event) => setBandForm((prev) => ({ ...prev, min_value: event.target.value }))} />
            </label>
            <label className="grid gap-1 text-xs font-semibold text-neutral-600">
              Max value
              <input className="h-10 rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm" value={bandForm.max_value} onChange={(event) => setBandForm((prev) => ({ ...prev, max_value: event.target.value }))} />
            </label>
            <label className="grid gap-1 text-xs font-semibold text-neutral-600">
              Recommended action
              <input className="h-10 w-64 rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm" value={bandForm.action_recommendation} onChange={(event) => setBandForm((prev) => ({ ...prev, action_recommendation: event.target.value }))} />
            </label>
            <button
              className="inline-flex h-10 items-center rounded-md bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
              disabled={addBand.isPending || !bandForm.band_name || !activeId}
              onClick={() => addBand.mutate()}
              type="button"
            >
              Add band
            </button>
          </div>
        ) : null}
      </section>
    </div>
  );
}
