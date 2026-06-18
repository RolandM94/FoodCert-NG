"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getApiErrorMessage } from "@/lib/api/client";
import {
  getMEIndicator,
  getActiveEstablishmentCategories,
  getActiveHandlerCategories,
  getMEIndicatorCalculation,
  getMEIndicatorSourceRecords,
  listMEIndicatorValues,
  recalculateMEIndicator,
} from "@/lib/api/standards";
import { listMedicalFacilities } from "@/lib/api/facilities";
import { fetchStateLgas, fetchStates } from "@/lib/api/state";
import { MEIndicatorFormDrawer } from "@/features/standards/me-indicator-form-drawer";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import type { MEIndicatorValue } from "@/types/standards";

type DetailTab = "values" | "disaggregation" | "history" | "sources" | "calculation";
type SourceFilterState = {
  period_start: string;
  period_end: string;
  date_from: string;
  date_to: string;
  state_id: string;
  lga_id: string;
  facility_id: string;
  food_handler_category: string;
  establishment_type: string;
  certificate_status: string;
  offset: number;
  limit: number;
};

const DEFAULT_SOURCE_PAGE_SIZE = 25;
const certificateStatusOptions = ["active", "expired", "revoked", "suspended", "not_certified"];

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

function valueTimestamp(value: MEIndicatorValue) {
  return value.overridden_at || value.updated_at || value.created_at;
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

function formatRecordValue(value: unknown) {
  if (value == null || value === "") return "-";
  if (Array.isArray(value)) return value.length ? value.map((item) => String(item)).join(", ") : "-";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function isIsoDateLike(value: string) {
  return /^\d{4}-\d{2}-\d{2}(T.*)?$/.test(value);
}

function renderRecordCell(columnKey: string, value: unknown) {
  if (value == null || value === "") {
    return <span className="text-neutral-400">-</span>;
  }

  if (typeof value === "boolean") {
    return (
      <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${value ? "bg-brand-50 text-brand-700" : "bg-neutral-100 text-neutral-600"}`}>
        {value ? "Yes" : "No"}
      </span>
    );
  }

  const stringValue = formatRecordValue(value);
  const lowerKey = columnKey.toLowerCase();
  const lowerValue = stringValue.toLowerCase();

  if (lowerKey.includes("date") || lowerKey.includes("timestamp") || isIsoDateLike(stringValue)) {
    const parsed = new Date(stringValue);
    if (!Number.isNaN(parsed.getTime())) {
      return (
        <span className="whitespace-nowrap text-neutral-700">
          {stringValue.includes("T") ? parsed.toLocaleString() : parsed.toLocaleDateString()}
        </span>
      );
    }
  }

  if (
    lowerKey.includes("status") ||
    lowerKey === "result" ||
    lowerKey === "failure_reason" ||
    lowerKey === "category" ||
    lowerKey === "food_handler_category"
  ) {
    let className = "bg-neutral-100 text-neutral-700";
    if (["active", "approved", "valid", "cleared", "compliant"].includes(lowerValue)) className = "bg-brand-50 text-brand-700";
    else if (["expired", "revoked", "rejected", "failed", "invalid"].includes(lowerValue)) className = "bg-danger-50 text-danger-700";
    else if (["pending", "submitted", "under_review", "suspended"].includes(lowerValue)) className = "bg-warning-50 text-warning-700";
    else if (["not_certified"].includes(lowerValue)) className = "bg-neutral-100 text-neutral-700";

    return <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${className}`}>{nice(stringValue)}</span>;
  }

  if (Array.isArray(value)) {
    return (
      <div className="flex flex-wrap gap-1">
        {value.map((item, index) => (
          <span key={`${columnKey}-${index}`} className="inline-flex rounded-full bg-neutral-100 px-2 py-1 text-xs font-medium text-neutral-700">
            {String(item)}
          </span>
        ))}
      </div>
    );
  }

  return <span className="break-words text-neutral-700">{stringValue}</span>;
}

function buildSourceFilterParams(filters: SourceFilterState) {
  return Object.fromEntries(
    Object.entries(filters)
      .filter(([, value]) => value !== "" && value !== null && value !== undefined)
      .map(([key, value]) => [key, String(value)])
  );
}

export default function MEIndicatorDetailPage() {
  const params = useParams<{ id: string }>();
  const indicatorId = params.id;
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<DetailTab>("values");
  const [editOpen, setEditOpen] = useState(false);
  const [error, setError] = useState("");
  const [sourceFilters, setSourceFilters] = useState<SourceFilterState>({
    period_start: "",
    period_end: "",
    date_from: "",
    date_to: "",
    state_id: "",
    lga_id: "",
    facility_id: "",
    food_handler_category: "",
    establishment_type: "",
    certificate_status: "",
    offset: 0,
    limit: DEFAULT_SOURCE_PAGE_SIZE,
  });
  const [sourceDraftFilters, setSourceDraftFilters] = useState<SourceFilterState>({
    period_start: "",
    period_end: "",
    date_from: "",
    date_to: "",
    state_id: "",
    lga_id: "",
    facility_id: "",
    food_handler_category: "",
    establishment_type: "",
    certificate_status: "",
    offset: 0,
    limit: DEFAULT_SOURCE_PAGE_SIZE,
  });

  const indicatorQuery = useQuery({
    queryKey: ["standards-me-indicator", indicatorId],
    queryFn: () => getMEIndicator(indicatorId),
  });
  const valuesQuery = useQuery({
    queryKey: ["standards-me-indicator-values", indicatorId],
    queryFn: () => listMEIndicatorValues(indicatorId),
  });
  const calculationQuery = useQuery({
    queryKey: ["standards-me-indicator-calculation", indicatorId],
    queryFn: () => getMEIndicatorCalculation(indicatorId),
  });
  const statesQuery = useQuery({
    queryKey: ["states"],
    queryFn: fetchStates,
    staleTime: 5 * 60 * 1000,
  });
  const facilitiesQuery = useQuery({
    queryKey: ["medical-facilities"],
    queryFn: listMedicalFacilities,
    staleTime: 5 * 60 * 1000,
  });
  const handlerCategoriesQuery = useQuery({
    queryKey: ["active-handler-categories"],
    queryFn: getActiveHandlerCategories,
    staleTime: 5 * 60 * 1000,
  });
  const establishmentCategoriesQuery = useQuery({
    queryKey: ["active-establishment-categories"],
    queryFn: getActiveEstablishmentCategories,
    staleTime: 5 * 60 * 1000,
  });
  const lgasQuery = useQuery({
    queryKey: ["state-lgas", sourceDraftFilters.state_id],
    queryFn: () => fetchStateLgas(sourceDraftFilters.state_id),
    enabled: Boolean(sourceDraftFilters.state_id),
    staleTime: 5 * 60 * 1000,
  });
  const sourcesQuery = useQuery({
    queryKey: ["standards-me-indicator-source-records", indicatorId, sourceFilters],
    queryFn: () => getMEIndicatorSourceRecords(indicatorId, buildSourceFilterParams(sourceFilters)),
  });

  const indicator = indicatorQuery.data;
  const values = useMemo(() => (
    Array.isArray(valuesQuery.data) ? valuesQuery.data : []
  ), [valuesQuery.data]);
  const calculation = calculationQuery.data;
  const sourceRecords = sourcesQuery.data?.records ?? [];
  const sourceColumns = useMemo(() => (
    Array.from(new Set(sourceRecords.flatMap((row) => Object.keys(row)))).slice(0, 8)
  ), [sourceRecords]);
  const states = statesQuery.data ?? [];
  const lgas = lgasQuery.data ?? [];
  const facilities = useMemo(() => {
    const all = facilitiesQuery.data ?? [];
    return all.filter((facility) => {
      if (sourceDraftFilters.state_id && facility.state !== sourceDraftFilters.state_id) return false;
      if (sourceDraftFilters.lga_id && facility.lga !== sourceDraftFilters.lga_id) return false;
      return true;
    });
  }, [facilitiesQuery.data, sourceDraftFilters.lga_id, sourceDraftFilters.state_id]);
  const handlerCategories = handlerCategoriesQuery.data ?? [];
  const establishmentCategories = establishmentCategoriesQuery.data ?? [];
  const indicatorType = String(indicator?.formula_config?.indicator_type || "quantitative");
  const inputMode = indicator?.input_mode === "automated" ? "automatic" : (indicator?.input_mode ?? String(indicator?.formula_config?.input_mode ?? "manual"));
  const isQualitative = indicatorType === "qualitative";
  const approvedValues = values.filter((value) => value.approval_status === "approved");
  const latestApproved = approvedValues[0] ?? values[0];
  const overrideValues = useMemo(() => (
    values
      .filter((value) => value.value_source === "override" || Boolean(value.override_reason) || Boolean(value.overridden_at))
      .slice()
      .sort((a, b) => new Date(valueTimestamp(b)).getTime() - new Date(valueTimestamp(a)).getTime())
  ), [values]);
  const latestOverride = overrideValues[0];
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
  const activityTimeline = useMemo(() => {
    const valueEvents = allHistory.map((item) => ({
      id: `history-${item.id}`,
      kind: "value" as const,
      timestamp: item.created_at,
      periodLabel: `${item.value.period_start} to ${item.value.period_end}`,
      title: nice(item.action),
      subtitle: item.actor_name || "System",
      detail: item.comment || "",
      status: item.to_status || item.from_status || item.value.approval_status,
      numericValue: isQualitative ? null : displayValue(item.value, false),
      qualitativeValue: isQualitative ? displayValue(item.value, true) : null,
    }));
    const calculationEvents = (calculation?.logs || []).map((log) => ({
      id: `calc-${log.id}`,
      kind: "calculation" as const,
      timestamp: log.created_at,
      periodLabel: `${log.period_start} to ${log.period_end}`,
      title: log.calculation_status === "overridden" ? "Override applied" : nice(log.calculation_status),
      subtitle: log.calculated_by_name || "System",
      detail: log.error_message || `${log.source_record_count} source records used`,
      status: log.calculation_status,
      numericValue: log.calculated_value == null ? null : String(log.calculated_value),
      qualitativeValue: null,
    }));
    return [...valueEvents, ...calculationEvents].sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }, [allHistory, calculation?.logs, isQualitative]);
  const disaggregatedRows = values.flatMap((value) => value.disaggregated_values || []);

  useEffect(() => {
    setSourceFilters((current) => {
      if (current.period_start || current.period_end) return current;
      return {
        ...current,
        period_start: currentPeriod.period_start,
        period_end: currentPeriod.period_end,
      };
    });
    setSourceDraftFilters((current) => {
      if (current.period_start || current.period_end) return current;
      return {
        ...current,
        period_start: currentPeriod.period_start,
        period_end: currentPeriod.period_end,
      };
    });
  }, [currentPeriod.period_end, currentPeriod.period_start]);

  useEffect(() => {
    setSourceDraftFilters((current) => {
      if (!current.lga_id) return current;
      if (!current.state_id) return { ...current, lga_id: "", facility_id: "" };
      if (lgas.some((lga) => lga.id === current.lga_id)) return current;
      return { ...current, lga_id: "", facility_id: "" };
    });
  }, [lgas]);

  useEffect(() => {
    setSourceDraftFilters((current) => {
      if (!current.facility_id) return current;
      if (facilities.some((facility) => facility.id === current.facility_id)) return current;
      return { ...current, facility_id: "" };
    });
  }, [facilities]);

  const recalculateMutation = useMutation({
    mutationFn: async () => {
      return recalculateMEIndicator(indicatorId, {
        period_start: currentPeriod.period_start,
        period_end: currentPeriod.period_end,
      });
    },
    onSuccess: () => {
      setError("");
      queryClient.invalidateQueries({ queryKey: ["standards-me-indicator-values", indicatorId] });
      queryClient.invalidateQueries({ queryKey: ["standards-me-indicator", indicatorId] });
      queryClient.invalidateQueries({ queryKey: ["standards-me-indicator-calculation", indicatorId] });
      queryClient.invalidateQueries({ queryKey: ["standards-me-indicator-source-records", indicatorId] });
    },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to recalculate indicator.")),
  });

  const applySourceFilters = () => {
    setSourceFilters({ ...sourceDraftFilters, offset: 0 });
  };

  const resetSourceFilters = () => {
    const reset = {
      period_start: currentPeriod.period_start,
      period_end: currentPeriod.period_end,
      date_from: "",
      date_to: "",
      state_id: "",
      lga_id: "",
      facility_id: "",
      food_handler_category: "",
      establishment_type: "",
      certificate_status: "",
      offset: 0,
      limit: DEFAULT_SOURCE_PAGE_SIZE,
    };
    setSourceDraftFilters(reset);
    setSourceFilters(reset);
  };

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
              {(inputMode === "automatic" || inputMode === "hybrid") ? <button type="button" onClick={() => setActiveTab("calculation")} className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50">View Calculation</button> : null}
              {(inputMode === "automatic" || inputMode === "hybrid") ? <button type="button" onClick={() => setActiveTab("sources")} className="h-10 rounded border border-brand-200 px-4 text-sm font-semibold text-brand-700 hover:bg-brand-50">View Source Records</button> : null}
              {(inputMode === "automatic" || inputMode === "hybrid") ? (
                <button type="button" disabled={recalculateMutation.isPending} onClick={() => recalculateMutation.mutate()} className="h-10 rounded bg-brand-600 px-4 text-sm font-semibold text-white disabled:opacity-60">Recalculate</button>
              ) : null}
              <button type="button" onClick={() => exportIndicatorSnapshot(indicator.indicator_name, { indicator, values, calculation, sourceRecords })} className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50">Export</button>
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

        {(inputMode === "hybrid" || overrideValues.length > 0) ? (
          <section className="grid gap-4 xl:grid-cols-[minmax(0,1.1fr)_minmax(320px,0.9fr)]">
            <div className="rounded-lg border border-neutral-200 bg-white p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-base font-semibold text-neutral-950">Override activity</h2>
                  <p className="mt-1 text-sm text-neutral-500">Track when a manual override replaced a system-calculated KPI result.</p>
                </div>
                <span className="rounded-full bg-warning-50 px-2.5 py-1 text-xs font-semibold text-warning-700">{overrideValues.length} overrides</span>
              </div>
              {latestOverride ? (
                <div className="mt-4 grid gap-3 md:grid-cols-3">
                  <div className="rounded-md border border-neutral-200 p-4">
                    <p className="text-xs font-semibold uppercase text-neutral-500">Latest override</p>
                    <p className="mt-2 text-xl font-semibold text-neutral-950">{displayValue(latestOverride, isQualitative)}</p>
                    <p className="mt-1 text-xs text-neutral-500">{latestOverride.period_start} to {latestOverride.period_end}</p>
                  </div>
                  <div className="rounded-md border border-neutral-200 p-4">
                    <p className="text-xs font-semibold uppercase text-neutral-500">Original calculated</p>
                    <p className="mt-2 text-xl font-semibold text-neutral-950">{latestOverride.original_calculated_value ?? "-"}</p>
                    <p className="mt-1 text-xs text-neutral-500">
                      {latestOverride.overridden_at ? new Date(latestOverride.overridden_at).toLocaleString() : "Awaiting override timestamp"}
                    </p>
                  </div>
                  <div className="rounded-md border border-neutral-200 p-4">
                    <p className="text-xs font-semibold uppercase text-neutral-500">Overridden by</p>
                    <p className="mt-2 text-base font-semibold text-neutral-950">{latestOverride.overridden_by_name || latestOverride.created_by_name || "System"}</p>
                    <p className="mt-1 text-xs text-neutral-500">{latestOverride.override_reason || "No reason captured."}</p>
                  </div>
                </div>
              ) : (
                <p className="mt-4 text-sm text-neutral-500">This KPI supports hybrid entry, but no overrides have been applied yet.</p>
              )}
            </div>

            <div className="rounded-lg border border-neutral-200 bg-white p-5">
              <h2 className="text-base font-semibold text-neutral-950">Recent activity</h2>
              <div className="mt-4 space-y-3">
                {activityTimeline.slice(0, 4).map((event) => (
                  <div key={event.id} className="rounded-md border border-neutral-200 p-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <p className="text-sm font-semibold text-neutral-950">{event.title}</p>
                      <span className={`rounded-full px-2 py-1 text-xs font-semibold ${statusClass(event.status || "draft")}`}>{nice(event.status || "draft")}</span>
                    </div>
                    <p className="mt-1 text-xs text-neutral-500">{event.periodLabel} · {event.subtitle} · {new Date(event.timestamp).toLocaleString()}</p>
                    <p className="mt-2 text-sm text-neutral-700">
                      {event.qualitativeValue ?? event.numericValue ?? "-"}
                      {event.detail ? ` · ${event.detail}` : ""}
                    </p>
                  </div>
                ))}
                {!activityTimeline.length ? <p className="text-sm text-neutral-500">No KPI activity captured yet.</p> : null}
              </div>
            </div>
          </section>
        ) : null}

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
              ["calculation", "Calculation"],
              ["values", "Values"],
              ["disaggregation", "Disaggregation"],
              ["history", "History"],
              ["sources", "Source Records"],
            ].map(([key, label]) => (
              <button key={key} type="button" onClick={() => setActiveTab(key as DetailTab)} className={`border-b-2 px-3 py-3 text-sm font-semibold ${activeTab === key ? "border-brand-600 text-brand-700" : "border-transparent text-neutral-500"}`}>
                {label}
              </button>
            ))}
          </div>

          <div className="p-4">
            {activeTab === "calculation" ? (
              <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_360px]">
                <div className="rounded-md border border-neutral-200 p-4">
                  <h3 className="text-sm font-semibold text-neutral-950">Calculation definition</h3>
                  <dl className="mt-3 grid gap-3 text-sm md:grid-cols-2">
                    <div><dt className="text-xs font-semibold uppercase text-neutral-500">Formula</dt><dd className="mt-1 text-neutral-900">{calculation?.formula || "-"}</dd></div>
                    <div><dt className="text-xs font-semibold uppercase text-neutral-500">Source</dt><dd className="mt-1 text-neutral-900">{nice(calculation?.calculation_source || indicator.calculation_source || "manual")}</dd></div>
                    <div><dt className="text-xs font-semibold uppercase text-neutral-500">Policy standard</dt><dd className="mt-1 text-neutral-900">{calculation?.linked_policy_standard || indicator.policy_standard_code || "-"}</dd></div>
                    <div><dt className="text-xs font-semibold uppercase text-neutral-500">Rule parameter</dt><dd className="mt-1 text-neutral-900">{calculation?.policy_rule_parameter || indicator.rule_parameter_key || "-"}</dd></div>
                  </dl>
                  <div className="mt-4 grid gap-4 md:grid-cols-2">
                    <div className="rounded-md bg-neutral-50 p-3">
                      <p className="text-xs font-semibold uppercase text-neutral-500">Numerator definition</p>
                      <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-xs text-neutral-700">{JSON.stringify(calculation?.numerator_definition || indicator.numerator_definition || {}, null, 2)}</pre>
                    </div>
                    <div className="rounded-md bg-neutral-50 p-3">
                      <p className="text-xs font-semibold uppercase text-neutral-500">Denominator definition</p>
                      <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-xs text-neutral-700">{JSON.stringify(calculation?.denominator_definition || indicator.denominator_definition || {}, null, 2)}</pre>
                    </div>
                  </div>
                </div>
                <div className="rounded-md border border-neutral-200 p-4">
                  <h3 className="text-sm font-semibold text-neutral-950">Latest calculation</h3>
                  <dl className="mt-3 space-y-3 text-sm">
                    <div><dt className="text-xs font-semibold uppercase text-neutral-500">Last calculated</dt><dd className="mt-1 text-neutral-900">{calculation?.last_calculated_at ? new Date(calculation.last_calculated_at).toLocaleString() : "-"}</dd></div>
                    <div><dt className="text-xs font-semibold uppercase text-neutral-500">Latest value</dt><dd className="mt-1 text-neutral-900">{calculation?.latest_calculated_value ?? indicator.latest_value ?? "-"}</dd></div>
                    <div><dt className="text-xs font-semibold uppercase text-neutral-500">Achievement</dt><dd className="mt-1 text-neutral-900">{calculation?.achievement_value ?? indicator.achievement_value ?? "-"}</dd></div>
                  </dl>
                  <div className="mt-4">
                    <p className="text-xs font-semibold uppercase text-neutral-500">Recent logs</p>
                    <div className="mt-2 space-y-2">
                      {(calculation?.logs || []).map((log) => (
                        <div key={log.id} className="rounded-md border border-neutral-100 p-3">
                          <p className="text-sm font-semibold text-neutral-900">{log.period_start} to {log.period_end}</p>
                          <p className="mt-1 text-xs text-neutral-500">{nice(log.calculation_status)} · {log.calculated_by_name || "System"} · {new Date(log.created_at).toLocaleString()}</p>
                          <p className="mt-2 text-sm text-neutral-700">Value: {log.calculated_value ?? "-"}{log.error_message ? ` · ${log.error_message}` : ""}</p>
                        </div>
                      ))}
                      {!(calculation?.logs || []).length ? <p className="text-sm text-neutral-500">No calculation logs yet.</p> : null}
                    </div>
                  </div>
                </div>
              </div>
            ) : null}

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
                        <td className="py-3 pr-4">
                          <div className="space-y-1">
                            <span className="inline-flex rounded-full bg-neutral-100 px-2 py-1 text-xs font-semibold text-neutral-700">{nice(value.value_source)}</span>
                            {value.value_source === "override" ? (
                              <div className="text-xs text-warning-700">
                                {value.original_calculated_value != null ? `Original: ${value.original_calculated_value}` : "Original calculated value preserved"}
                                {value.override_reason ? ` · ${value.override_reason}` : ""}
                              </div>
                            ) : null}
                          </div>
                        </td>
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
                {activityTimeline.map((event) => (
                  <div className="rounded-md border border-neutral-200 p-3" key={event.id}>
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <p className="text-sm font-semibold text-neutral-950">{event.title}: {event.periodLabel}</p>
                      <span className={`rounded-full px-2 py-1 text-xs font-semibold ${statusClass(event.status || "draft")}`}>{nice(event.status || "draft")}</span>
                    </div>
                    <p className="mt-1 text-xs text-neutral-500">{event.subtitle} · {new Date(event.timestamp).toLocaleString()}</p>
                    {(event.qualitativeValue || event.numericValue) ? (
                      <p className="mt-2 text-sm font-medium text-neutral-800">{event.qualitativeValue ?? event.numericValue}</p>
                    ) : null}
                    {event.detail ? <p className="mt-2 text-sm text-neutral-600">{event.detail}</p> : null}
                  </div>
                ))}
                {!activityTimeline.length ? <p className="text-sm text-neutral-500">No history captured yet.</p> : null}
              </div>
            ) : null}

            {activeTab === "sources" ? (
              <div className="grid gap-4">
                <div className="rounded-md border border-neutral-200 bg-neutral-50 p-4">
                  <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                    <label className="grid gap-1 text-sm">
                      <span className="font-medium text-neutral-700">Period start</span>
                      <input type="date" value={sourceDraftFilters.period_start} onChange={(event) => setSourceDraftFilters((current) => ({ ...current, period_start: event.target.value }))} className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-brand-500" />
                    </label>
                    <label className="grid gap-1 text-sm">
                      <span className="font-medium text-neutral-700">Period end</span>
                      <input type="date" value={sourceDraftFilters.period_end} onChange={(event) => setSourceDraftFilters((current) => ({ ...current, period_end: event.target.value }))} className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-brand-500" />
                    </label>
                    <label className="grid gap-1 text-sm">
                      <span className="font-medium text-neutral-700">Created from</span>
                      <input type="date" value={sourceDraftFilters.date_from} onChange={(event) => setSourceDraftFilters((current) => ({ ...current, date_from: event.target.value }))} className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-brand-500" />
                    </label>
                    <label className="grid gap-1 text-sm">
                      <span className="font-medium text-neutral-700">Created to</span>
                      <input type="date" value={sourceDraftFilters.date_to} onChange={(event) => setSourceDraftFilters((current) => ({ ...current, date_to: event.target.value }))} className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-brand-500" />
                    </label>
                    <label className="grid gap-1 text-sm">
                      <span className="font-medium text-neutral-700">State</span>
                      <select
                        value={sourceDraftFilters.state_id}
                        onChange={(event) => setSourceDraftFilters((current) => ({
                          ...current,
                          state_id: event.target.value,
                          lga_id: "",
                          facility_id: "",
                        }))}
                        className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-brand-500"
                      >
                        <option value="">All states</option>
                        {states.map((state) => (
                          <option key={state.id} value={state.id}>{state.name}{state.is_fct ? " (FCT)" : ""}</option>
                        ))}
                      </select>
                    </label>
                    <label className="grid gap-1 text-sm">
                      <span className="font-medium text-neutral-700">LGA</span>
                      <select
                        value={sourceDraftFilters.lga_id}
                        onChange={(event) => setSourceDraftFilters((current) => ({
                          ...current,
                          lga_id: event.target.value,
                          facility_id: "",
                        }))}
                        disabled={!sourceDraftFilters.state_id}
                        className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-brand-500 disabled:bg-neutral-100"
                      >
                        <option value="">{sourceDraftFilters.state_id ? "All LGAs" : "Select a state first"}</option>
                        {lgas.map((lga) => (
                          <option key={lga.id} value={lga.id}>{lga.name}</option>
                        ))}
                      </select>
                    </label>
                    <label className="grid gap-1 text-sm">
                      <span className="font-medium text-neutral-700">Facility</span>
                      <select
                        value={sourceDraftFilters.facility_id}
                        onChange={(event) => setSourceDraftFilters((current) => ({ ...current, facility_id: event.target.value }))}
                        className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-brand-500"
                      >
                        <option value="">All facilities</option>
                        {facilities.map((facility) => (
                          <option key={facility.id} value={facility.id}>{facility.facility_name}</option>
                        ))}
                      </select>
                    </label>
                    <label className="grid gap-1 text-sm">
                      <span className="font-medium text-neutral-700">Certificate status</span>
                      <select value={sourceDraftFilters.certificate_status} onChange={(event) => setSourceDraftFilters((current) => ({ ...current, certificate_status: event.target.value }))} className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-brand-500">
                        <option value="">All statuses</option>
                        {certificateStatusOptions.map((option) => (
                          <option key={option} value={option}>{nice(option)}</option>
                        ))}
                      </select>
                    </label>
                    <label className="grid gap-1 text-sm">
                      <span className="font-medium text-neutral-700">Handler category</span>
                      <select value={sourceDraftFilters.food_handler_category} onChange={(event) => setSourceDraftFilters((current) => ({ ...current, food_handler_category: event.target.value }))} className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-brand-500">
                        <option value="">All handler categories</option>
                        {handlerCategories.map((category) => (
                          <option key={category.id} value={category.code}>{category.name}</option>
                        ))}
                      </select>
                    </label>
                    <label className="grid gap-1 text-sm">
                      <span className="font-medium text-neutral-700">Establishment type</span>
                      <select value={sourceDraftFilters.establishment_type} onChange={(event) => setSourceDraftFilters((current) => ({ ...current, establishment_type: event.target.value }))} className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-brand-500">
                        <option value="">All establishment types</option>
                        {establishmentCategories.map((category) => (
                          <option key={category.id} value={category.code}>{category.name}</option>
                        ))}
                      </select>
                    </label>
                    <label className="grid gap-1 text-sm">
                      <span className="font-medium text-neutral-700">Rows per page</span>
                      <select value={String(sourceDraftFilters.limit)} onChange={(event) => setSourceDraftFilters((current) => ({ ...current, limit: Number(event.target.value) }))} className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-brand-500">
                        {[10, 25, 50, 100].map((size) => (
                          <option key={size} value={size}>{size}</option>
                        ))}
                      </select>
                    </label>
                  </div>
                  <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                    <div className="flex flex-wrap gap-2">
                      <button type="button" onClick={applySourceFilters} className="h-10 rounded bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700">Apply filters</button>
                      <button type="button" onClick={resetSourceFilters} className="h-10 rounded border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50">Reset</button>
                    </div>
                    <div className="text-sm text-neutral-500">
                      {sourcesQuery.data ? (
                        <span>
                          {sourcesQuery.data.count === 0
                            ? "No source records"
                            : `Showing ${sourcesQuery.data.offset + 1}-${Math.min(sourcesQuery.data.offset + sourceRecords.length, sourcesQuery.data.count)} of ${sourcesQuery.data.count}`}
                        </span>
                      ) : null}
                    </div>
                  </div>
                </div>

                <div className="grid gap-3 md:grid-cols-3">
                  <div className="rounded-md border border-neutral-200 p-3">
                    <p className="text-xs font-semibold uppercase text-neutral-500">Computed value</p>
                    <p className="mt-2 text-lg font-semibold text-neutral-950">{sourcesQuery.data?.value ?? "-"}</p>
                  </div>
                  <div className="rounded-md border border-neutral-200 p-3">
                    <p className="text-xs font-semibold uppercase text-neutral-500">Numerator</p>
                    <p className="mt-2 text-lg font-semibold text-neutral-950">{sourcesQuery.data?.numerator ?? "-"}</p>
                  </div>
                  <div className="rounded-md border border-neutral-200 p-3">
                    <p className="text-xs font-semibold uppercase text-neutral-500">Denominator</p>
                    <p className="mt-2 text-lg font-semibold text-neutral-950">{sourcesQuery.data?.denominator ?? "-"}</p>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead className="text-left text-xs uppercase text-neutral-500">
                      <tr>
                        {sourceColumns.map((key) => (
                          <th key={key} className="py-2 pr-4">{nice(key)}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                        {sourceRecords.map((row, index) => (
                        <tr className="border-t border-neutral-100" key={`${index}-${String(row.id ?? row.certificate_id ?? row.food_handler_id ?? "record")}`}>
                          {sourceColumns.map((key) => (
                            <td key={key} className="max-w-[260px] py-3 pr-4 align-top">{renderRecordCell(key, row[key])}</td>
                          ))}
                        </tr>
                      ))}
                      {!sourceRecords.length ? <tr><td className="py-6 text-neutral-500" colSpan={Math.max(sourceColumns.length, 1)}>No source records available yet.</td></tr> : null}
                    </tbody>
                  </table>
                </div>

                <div className="flex flex-col gap-3 border-t border-neutral-200 pt-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="text-sm text-neutral-500">
                    Period: {sourcesQuery.data?.period_start ?? sourceFilters.period_start || "-"} to {sourcesQuery.data?.period_end ?? sourceFilters.period_end || "-"}
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      disabled={!sourcesQuery.data?.has_previous}
                      onClick={() => setSourceFilters((current) => ({ ...current, offset: Math.max(0, current.offset - current.limit) }))}
                      className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 disabled:opacity-50"
                    >
                      Previous
                    </button>
                    <button
                      type="button"
                      disabled={!sourcesQuery.data?.has_next}
                      onClick={() => setSourceFilters((current) => ({ ...current, offset: current.offset + current.limit }))}
                      className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 disabled:opacity-50"
                    >
                      Next
                    </button>
                  </div>
                </div>
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
