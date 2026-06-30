"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  BarChart3,
  CheckCircle2,
  Database,
  Eye,
  Filter,
  LineChart,
  Save,
  Sparkles,
  Table2,
  Trash2,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart as RechartsLineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  createAnalyticsWorksheet,
  generateAnalyticsWorksheet,
  getAnalyticsDatasetAiPrompt,
  getAnalyticsDatasetExamples,
  getAnalyticsDatasetSample,
  listAnalyticsDatasets,
  previewAnalyticsWorksheet,
  type AnalyticsDataset,
  type AnalyticsWorksheetFilter,
  type AnalyticsWorksheetMetric,
  type AnalyticsWorksheetPayload,
  type AnalyticsWorksheetPreview,
} from "@/lib/api/analytics";
import {
  buildDatasetAnalyticsFields,
  canAggregate,
  getDimensions,
  getMeasures,
  type AnalyticsChartType,
  type AnalyticsField,
} from "@/lib/analytics/fields";
import { buildAnalyticsInsightInput, getFieldCompatibilityReason, resolveDashboardScope, validateChartConfig } from "@/lib/analytics/validation";
import { getApiErrorMessage } from "@/lib/api/client";
import { getEmbeddedAnalyticsModuleMeta } from "@/features/reports/embedded-analytics-actions";

const AGGREGATION_OPTIONS = [
  { value: "count", label: "Count" },
  { value: "sum", label: "Sum" },
  { value: "avg", label: "Average" },
  { value: "min", label: "Minimum" },
  { value: "max", label: "Maximum" },
];

const FILTER_OPERATORS = [
  { value: "eq", label: "Equals" },
  { value: "contains", label: "Contains" },
  { value: "in", label: "In list" },
  { value: "gte", label: "Greater or equal" },
  { value: "lte", label: "Less or equal" },
];

const CHART_OPTIONS = [
  { value: "bar", label: "Bar", icon: BarChart3 },
  { value: "grouped_bar", label: "Grouped", icon: BarChart3 },
  { value: "line", label: "Line", icon: LineChart },
  { value: "pie", label: "Pie", icon: Database },
  { value: "donut", label: "Donut", icon: Database },
  { value: "table", label: "Table", icon: Table2 },
  { value: "kpi_card", label: "KPI", icon: Database },
  { value: "map", label: "Map", icon: Database },
];

const CHART_PALETTE = ["#4fd1c5", "#fbbf24", "#60a5fa", "#a78bfa", "#fb7185", "#34d399", "#f97316"];

function uniqueByField<T extends { field: string }>(rows: T[]) {
  return rows.filter((row, index, all) => all.findIndex((item) => item.field === row.field) === index);
}

function datasetFieldLabel(dataset: AnalyticsDataset | undefined, fieldName: string) {
  return dataset?.field_labels?.[fieldName] || fieldName.replaceAll("__", " / ").replaceAll("_", " ");
}

function normalizePreviewRows(rows: Array<Record<string, string | number | null>> | undefined) {
  if (!rows?.length) return [];
  return rows.map((row) => {
    const normalized: Record<string, string | number> = {};
    Object.entries(row).forEach(([key, value]) => {
      normalized[key] = typeof value === "number" ? value : Number(value ?? 0) || String(value ?? "");
    });
    return normalized;
  });
}

function formatMetricValue(value: string | number | null | undefined) {
  if (typeof value === "number") {
    return new Intl.NumberFormat("en-NG", { maximumFractionDigits: 2 }).format(value);
  }
  return value == null || value === "" ? "—" : String(value);
}

function decodeUserScope() {
  if (typeof window === "undefined") return { role: "" };
  try {
    const token = window.localStorage.getItem("foodcert_access_token");
    const userMeta = window.localStorage.getItem("foodcert_user_meta");
    const payload = token ? JSON.parse(atob(token.split(".")[1])) : {};
    const meta = userMeta ? JSON.parse(userMeta) : {};
    return {
      role: meta.role || payload.role || "",
      state_id: meta.state_id || payload.state_id || null,
      organization_id: meta.organization_id || payload.organization_id || null,
      facility_id: meta.facility_id || payload.facility_id || null,
      laboratory_id: meta.laboratory_id || payload.laboratory_id || null,
      id: meta.id || payload.user_id || payload.id || null,
    };
  } catch {
    return { role: "" };
  }
}

function isDateLikeField(field?: AnalyticsField) {
  return Boolean(field?.isTimeDimension || field?.dataType === "date");
}

function fieldMetaLine(field: AnalyticsField) {
  const parts = [field.entity.replaceAll("_", " "), field.dataType];
  if (field.fieldType === "measure" && field.defaultAggregation) {
    parts.push(field.defaultAggregation);
  }
  return parts.join(" • ");
}

type AnalyticsWorksheetBuilderProps = {
  initialModuleSource?: string;
  initialDatasetId?: string;
  initialPrompt?: string;
  autoGenerateFromPrompt?: boolean;
  dashboardBuilderHref?: string;
};

export function AnalyticsWorksheetBuilder({
  initialModuleSource = "",
  initialDatasetId = "",
  initialPrompt = "",
  autoGenerateFromPrompt = false,
  dashboardBuilderHref = "/federal/reports/dashboard-builder",
}: AnalyticsWorksheetBuilderProps) {
  const [selectedDatasetId, setSelectedDatasetId] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [metrics, setMetrics] = useState<AnalyticsWorksheetMetric[]>([]);
  const [dimensions, setDimensions] = useState<Array<{ field: string }>>([]);
  const [filters, setFilters] = useState<AnalyticsWorksheetFilter[]>([]);
  const [chartRecommendation, setChartRecommendation] = useState("table");
  const [preview, setPreview] = useState<AnalyticsWorksheetPreview | null>(null);
  const [savedWorksheetId, setSavedWorksheetId] = useState("");
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiSuggestionOpen, setAiSuggestionOpen] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [currentUserMeta, setCurrentUserMeta] = useState(() => decodeUserScope());
  const autoGenerationAttemptedRef = useRef(false);

  const datasetsQuery = useQuery({
    queryKey: ["analytics-datasets"],
    queryFn: listAnalyticsDatasets,
  });

  const selectedDataset = useMemo(
    () => datasetsQuery.data?.find((dataset) => dataset.id === selectedDatasetId),
    [datasetsQuery.data, selectedDatasetId],
  );
  const filteredDatasets = useMemo(() => {
    if (!initialModuleSource) {
      return datasetsQuery.data ?? [];
    }
    return (datasetsQuery.data ?? []).filter((dataset) => dataset.module_source === initialModuleSource);
  }, [datasetsQuery.data, initialModuleSource]);
  const moduleMeta = useMemo(
    () => (initialModuleSource ? getEmbeddedAnalyticsModuleMeta(initialModuleSource) : null),
    [initialModuleSource],
  );
  const metricsSignature = useMemo(() => JSON.stringify(metrics), [metrics]);
  const dimensionsSignature = useMemo(() => JSON.stringify(dimensions), [dimensions]);
  const filtersSignature = useMemo(() => JSON.stringify(filters), [filters]);

  const sampleQuery = useQuery({
    queryKey: ["analytics-dataset-sample", selectedDatasetId],
    queryFn: () => getAnalyticsDatasetSample(selectedDatasetId),
    enabled: Boolean(selectedDatasetId),
  });

  const examplesQuery = useQuery({
    queryKey: ["analytics-dataset-examples", selectedDatasetId],
    queryFn: () => getAnalyticsDatasetExamples(selectedDatasetId),
    enabled: Boolean(selectedDatasetId),
  });

  const aiPromptQuery = useQuery({
    queryKey: ["analytics-dataset-ai-prompt", selectedDatasetId],
    queryFn: () => getAnalyticsDatasetAiPrompt(selectedDatasetId),
    enabled: Boolean(selectedDatasetId),
  });

  const previewMutation = useMutation({
    mutationFn: (payload: AnalyticsWorksheetPayload) => previewAnalyticsWorksheet(payload),
    onSuccess: (response) => {
      setPreview(response);
      setError("");
    },
    onError: (mutationError) => {
      setError(getApiErrorMessage(mutationError, "Could not preview worksheet."));
    },
  });

  const saveMutation = useMutation({
    mutationFn: (payload: AnalyticsWorksheetPayload) => createAnalyticsWorksheet(payload),
    onSuccess: (response) => {
      setSavedWorksheetId(response.id);
      setSuccess("Worksheet saved and ready for widget or dashboard use.");
      setError("");
    },
    onError: (mutationError) => {
      setError(getApiErrorMessage(mutationError, "Could not save worksheet."));
    },
  });

  const aiSuggestionMutation = useMutation({
    mutationFn: generateAnalyticsWorksheet,
    onSuccess: () => {
      setAiSuggestionOpen(true);
      setError("");
    },
    onError: (mutationError) => {
      setError(getApiErrorMessage(mutationError, "Could not generate worksheet suggestion."));
    },
  });

  const sensitiveFields = new Set(selectedDataset?.sensitive_fields ?? []);
  const analyticsFields = useMemo<AnalyticsField[]>(
    () => (selectedDataset ? buildDatasetAnalyticsFields(selectedDataset) : []),
    [selectedDataset],
  );
  const dimensionFields = useMemo(() => getDimensions(analyticsFields), [analyticsFields]);
  const measureFields = useMemo(() => getMeasures(analyticsFields), [analyticsFields]);
  const chartData = useMemo(() => normalizePreviewRows(preview?.rows), [preview?.rows]);
  const previewColumnKeys = useMemo(() => Object.keys(preview?.rows?.[0] ?? {}), [preview?.rows]);
  const xAxisField = dimensions[0]?.field ?? preview?.dimensions?.[0] ?? "";
  const yAxisField =
    metrics.find((metric) => previewColumnKeys.includes(metric.field))?.field
    || previewColumnKeys.find((key) => key !== xAxisField)
    || "";
  const lineSeries = useMemo(
    () => (metrics.length ? metrics : (preview?.metrics?.filter((metric) => metric.field) ?? [])).slice(0, 3),
    [metrics, preview?.metrics],
  );
  const selectedDimensionFields = useMemo(
    () => dimensions.map((dimension) => analyticsFields.find((field) => field.fieldName === dimension.field)).filter(Boolean) as AnalyticsField[],
    [analyticsFields, dimensions],
  );
  const selectedMeasureFields = useMemo(
    () => metrics.map((metric) => analyticsFields.find((field) => field.fieldName === metric.field)).filter(Boolean) as AnalyticsField[],
    [analyticsFields, metrics],
  );
  const normalizedChartType = (chartRecommendation === "kpi_card" ? "kpi" : chartRecommendation) as AnalyticsChartType;
  const chartValidation = useMemo(
    () => validateChartConfig({ chartType: normalizedChartType, dimensions: selectedDimensionFields, measures: selectedMeasureFields, filters }),
    [filters, normalizedChartType, selectedDimensionFields, selectedMeasureFields],
  );
  const dashboardScope = useMemo(() => resolveDashboardScope(currentUserMeta), [currentUserMeta]);
  const insightInput = useMemo(
    () =>
      buildAnalyticsInsightInput({
        dimensions: selectedDimensionFields,
        measures: selectedMeasureFields,
        filters,
        chartType: normalizedChartType,
        role: dashboardScope.role,
        scope: dashboardScope,
        aggregatedData: preview?.rows ?? [],
      }),
    [dashboardScope, filters, normalizedChartType, preview?.rows, selectedDimensionFields, selectedMeasureFields],
  );
  const groupedBarSecondaryField = dimensions[1]?.field ?? preview?.dimensions?.[1] ?? "";
  const groupedBarMeasureField = metrics[0]?.field ?? preview?.metrics?.find((metric) => metric.field)?.field ?? "";
  const groupedBarData = useMemo(() => {
    if (!chartData.length || !xAxisField || !groupedBarSecondaryField || !groupedBarMeasureField) return [];
    const rows = new Map<string, Record<string, string | number>>();
    chartData.forEach((row) => {
      const xValue = String(row[xAxisField] ?? "Unknown");
      const seriesKey = String(row[groupedBarSecondaryField] ?? "Other");
      const metricValue = Number(row[groupedBarMeasureField] ?? 0);
      const current = rows.get(xValue) ?? { [xAxisField]: xValue };
      current[seriesKey] = metricValue;
      rows.set(xValue, current);
    });
    return Array.from(rows.values());
  }, [chartData, groupedBarMeasureField, groupedBarSecondaryField, xAxisField]);
  const groupedBarSeriesKeys = useMemo(() => {
    const keys = new Set<string>();
    groupedBarData.forEach((row) => {
      Object.keys(row).forEach((key) => {
        if (key !== xAxisField) keys.add(key);
      });
    });
    return Array.from(keys);
  }, [groupedBarData, xAxisField]);
  const pieMetricField = metrics[0]?.field ?? preview?.metrics?.[0]?.field ?? "";
  const userScopeLabel = useMemo(() => {
    if (dashboardScope.countryId && !dashboardScope.stateId) return "National scope";
    if (dashboardScope.stateId) return "State-scoped analytics";
    if (dashboardScope.employerId) return "Employer-scoped analytics";
    if (dashboardScope.facilityId) return "Facility-scoped analytics";
    if (dashboardScope.laboratoryId) return "Laboratory-scoped analytics";
    if (dashboardScope.inspectorId) return "Inspector-scoped analytics";
    return "Scoped analytics";
  }, [dashboardScope]);

  const buildPayload = useCallback((): AnalyticsWorksheetPayload | null => {
    if (!selectedDatasetId || !name.trim()) {
      setError("Choose a dataset and name the worksheet before continuing.");
      return null;
    }
    return {
      name: name.trim(),
      description: description.trim(),
      dataset: selectedDatasetId,
      scope_type: "private",
      metrics,
      dimensions,
      filters,
      aggregations: uniqueByField(metrics).map((metric) => metric.aggregation),
      derived_fields: [],
      query_rules: { limit: 12 },
      chart_recommendation: chartRecommendation,
      preview_output: preview ?? undefined,
    };
  }, [chartRecommendation, description, dimensions, filters, metrics, name, preview, selectedDatasetId]);

  function resetDatasetState(datasetId: string) {
    setSelectedDatasetId(datasetId);
    setMetrics([]);
    setDimensions([]);
    setFilters([]);
    setPreview(null);
    setSavedWorksheetId("");
    setError("");
    setSuccess("");
  }

  function fieldByName(fieldName: string) {
    return analyticsFields.find((field) => field.fieldName === fieldName);
  }

  function addMetric(field: string) {
    const analyticsField = fieldByName(field);
    if (!analyticsField || analyticsField.fieldType !== "measure") return;
    setMetrics((current) =>
      uniqueByField([
        ...current,
        {
          field,
          aggregation: analyticsField.defaultAggregation || "count",
          label: analyticsField.label,
        },
      ]),
    );
  }

  function addDimension(field: string) {
    const analyticsField = fieldByName(field);
    if (!analyticsField || analyticsField.fieldType !== "dimension") return;
    setDimensions((current) => uniqueByField([...current, { field }]));
  }

  function addFilter(field: string) {
    const analyticsField = fieldByName(field);
    if (!analyticsField?.isFilterable) return;
    setFilters((current) => [...current, { field, operator: "eq", value: "" }]);
  }

  function applyExample(index: number) {
    const example = examplesQuery.data?.examples[index];
    if (!example) return;
    setMetrics(example.metrics);
    setDimensions(example.dimensions);
    setFilters(example.filters);
    setChartRecommendation(example.chart_recommendation);
    if (!name.trim()) {
      setName(example.name);
    }
    if (!description.trim()) {
      setDescription(example.description);
    }
  }

  function applyAiSuggestionDraft(suggestion: Awaited<ReturnType<typeof generateAnalyticsWorksheet>>) {
    if (!suggestion) return;
    setName(suggestion.name);
    setDescription(suggestion.description);
    setMetrics(suggestion.metrics);
    setDimensions(suggestion.dimensions);
    setFilters(suggestion.filters);
    setChartRecommendation(suggestion.chart_recommendation);
    setSuccess("AI worksheet suggestion applied. Review and save when ready.");
    setAiSuggestionOpen(false);
  }

  function applyAiSuggestion() {
    const suggestion = aiSuggestionMutation.data;
    if (!suggestion) return;
    applyAiSuggestionDraft(suggestion);
  }

  useEffect(() => {
    if (selectedDatasetId || !filteredDatasets.length) {
      return;
    }
    if (initialDatasetId && filteredDatasets.some((dataset) => dataset.id === initialDatasetId)) {
      setSelectedDatasetId(initialDatasetId);
      return;
    }
    if (filteredDatasets.length === 1) {
      setSelectedDatasetId(filteredDatasets[0].id);
    }
  }, [filteredDatasets, initialDatasetId, selectedDatasetId]);

  useEffect(() => {
    if (initialPrompt && !aiPrompt) {
      setAiPrompt(initialPrompt);
    }
  }, [aiPrompt, initialPrompt]);

  useEffect(() => {
    setCurrentUserMeta(decodeUserScope());
  }, []);

  useEffect(() => {
    if (!autoGenerateFromPrompt || autoGenerationAttemptedRef.current || !selectedDatasetId || !initialPrompt.trim()) {
      return;
    }
    autoGenerationAttemptedRef.current = true;
    aiSuggestionMutation.mutate(
      { dataset: selectedDatasetId, prompt: initialPrompt.trim() },
      {
        onSuccess: (suggestion) => {
          applyAiSuggestionDraft(suggestion);
          setSuccess("AI worksheet draft loaded from your selected dataset. Review the logic, then save the workbook.");
          setError("");
        },
      },
    );
  }, [aiSuggestionMutation, autoGenerateFromPrompt, initialPrompt, selectedDatasetId]);

  useEffect(() => {
    if (!selectedDatasetId || !name.trim() || (!metrics.length && !dimensions.length)) {
      return;
    }
    const payload = buildPayload();
    if (!payload) {
      return;
    }
    const timeout = window.setTimeout(() => {
      previewMutation.mutate(payload);
    }, 450);
    return () => window.clearTimeout(timeout);
  }, [buildPayload, dimensions.length, dimensionsSignature, filtersSignature, metrics.length, metricsSignature, previewMutation, selectedDatasetId, name]);

  return (
    <div className="grid gap-4">
      {error ? <div className="rounded-lg border border-danger-200 bg-danger-50 px-4 py-3 text-sm font-medium text-danger-700">{error}</div> : null}
      {success ? <div className="rounded-lg border border-brand-200 bg-brand-50 px-4 py-3 text-sm font-medium text-brand-800">{success}</div> : null}
      {moduleMeta ? (
        <div className="rounded-lg border border-brand-200 bg-brand-50 px-4 py-3 text-sm text-brand-900">
          Building from <span className="font-semibold">{moduleMeta.label}</span> datasets only. Save the worksheet here, then continue into widget and canvas composition.
        </div>
      ) : null}

      <section className="overflow-hidden rounded-[18px] border border-neutral-200 bg-white shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-200 px-5 py-3.5">
          <div className="flex min-w-0 flex-wrap items-center gap-3">
            <button type="button" className="inline-flex items-center gap-2 text-sm font-semibold text-neutral-400">
              <ArrowLeft size={15} />
              Change data
            </button>
            <span className="hidden h-5 w-px bg-neutral-200 sm:block" />
            <input
              className="min-w-[300px] bg-transparent text-[15px] font-bold text-neutral-950 outline-none"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Untitled worksheet"
            />
            <span className="truncate text-sm text-neutral-400">{selectedDataset?.name || "Select dataset"}</span>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium text-brand-700">
              <CheckCircle2 size={15} />
              {savedWorksheetId ? "Saved" : saveMutation.isPending ? "Saving..." : "Draft"}
            </span>
            <Link
              href={savedWorksheetId ? `${dashboardBuilderHref}?worksheetId=${savedWorksheetId}` : "#"}
              className={`inline-flex h-10 items-center gap-2 rounded-xl border px-4 text-sm font-semibold ${
                savedWorksheetId
                  ? "border-neutral-200 bg-white text-neutral-700 shadow-sm"
                  : "pointer-events-none border-neutral-200 bg-neutral-50 text-neutral-300"
              }`}
            >
              Add to Canvas
            </Link>
            <button
              type="button"
              onClick={() => {
                const payload = buildPayload();
                if (payload) {
                  saveMutation.mutate(payload);
                }
              }}
              className="inline-flex h-10 items-center gap-2 rounded-xl border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700 shadow-sm"
            >
              <Save size={15} />
              Configure
            </button>
            <button
              type="button"
              disabled={!selectedDatasetId || !aiPrompt.trim() || aiSuggestionMutation.isPending}
              onClick={() => aiSuggestionMutation.mutate({ dataset: selectedDatasetId, prompt: aiPrompt.trim() })}
              className="inline-flex h-10 items-center gap-2 rounded-xl border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-300 disabled:opacity-50"
            >
              <Sparkles size={15} />
              AI Assist
            </button>
          </div>
        </div>

        <div className="border-b border-neutral-200 px-5 py-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-2 rounded-full border border-neutral-200 bg-white px-3 py-2 text-sm font-medium text-neutral-500 shadow-sm">
              <Filter size={14} />
              Add Filter
            </span>
            {filters.map((filter, index) => (
              <div key={`${filter.field}-${index}`} className="inline-flex items-center gap-2 rounded-full border border-brand-100 bg-brand-50 px-3 py-2 text-sm font-medium text-brand-700">
                <span>{datasetFieldLabel(selectedDataset, filter.field)}</span>
                <button type="button" onClick={() => setFilters((current) => current.filter((_, itemIndex) => itemIndex !== index))}>
                  x
                </button>
              </div>
            ))}
          </div>

          <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
            <button type="button" className="shrink-0 rounded-lg bg-neutral-100 px-4 py-2 text-sm font-medium text-neutral-700">
              Overview
            </button>
            {(examplesQuery.data?.examples ?? []).slice(0, 5).map((example, index) => (
              <button
                key={example.key}
                type="button"
                onClick={() => applyExample(index)}
                className={`shrink-0 rounded-lg px-4 py-2 text-sm font-medium ${
                  name === example.name ? "bg-brand-600 text-white" : "text-neutral-400 hover:bg-neutral-100"
                }`}
              >
                {example.name}
              </button>
            ))}
            <button type="button" className="shrink-0 rounded-lg px-3 py-2 text-sm font-medium text-neutral-400">
              +
            </button>
          </div>
        </div>

        <div className="grid min-h-[760px] xl:grid-cols-[250px_minmax(0,1fr)_310px]">
          <aside className="border-r border-neutral-200 bg-[#fbfbfd]">
            <div className="p-4">
              <p className="text-xs font-bold uppercase tracking-wide text-[#7b879f]">Data Fields</p>
              <select
                className="mt-2 h-10 w-full rounded-xl border border-neutral-200 bg-white px-3 text-sm text-neutral-900 shadow-sm"
                value={selectedDatasetId}
                onChange={(event) => resetDatasetState(event.target.value)}
              >
                <option value="">Select dataset</option>
                {filteredDatasets.map((dataset) => (
                  <option key={dataset.id} value={dataset.id}>
                    {dataset.name}
                  </option>
                ))}
              </select>
              <p className="mt-2 text-xs text-neutral-400">{selectedDataset?.description || "Choose a dataset to begin."}</p>
            </div>

            <div className="border-t border-neutral-200 px-4 py-3 text-xs text-neutral-500">
              Click a pill to add it to the worksheet.
            </div>

            <div className="space-y-4 p-4">
              <div className="rounded-2xl border border-[#ece8ff] bg-white p-3 shadow-sm">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wide text-[#5d35d5]">Dimensions</p>
                    <p className="mt-1 text-xs text-neutral-400">Grouping, drilldown, filter, and chart category fields</p>
                  </div>
                  <span className="text-xs font-semibold text-[#5d35d5]">{dimensions.length}</span>
                </div>
                <div className="mt-3 max-h-[340px] space-y-2 overflow-y-auto pr-1">
                  {dimensionFields.map((field) => {
                    const disabledReason = sensitiveFields.has(field.fieldName)
                      ? "Sensitive fields cannot be used in analytics worksheets."
                      : getFieldCompatibilityReason(field, normalizedChartType);
                    const disabled = Boolean(disabledReason);
                    const active = dimensions.some((item) => item.field === field.fieldName);
                    return (
                      <button
                        key={field.id}
                        type="button"
                        disabled={disabled}
                        onClick={() => addDimension(field.fieldName)}
                        className={`flex w-full items-center justify-between rounded-xl border px-3 py-2.5 text-left transition ${
                          active
                            ? "border-[#6d28d9] bg-gradient-to-r from-[#6d28d9] to-[#9333ea] text-white"
                            : disabled
                              ? "border-neutral-200 bg-neutral-50 text-neutral-300"
                              : "border-[#ddd8ff] bg-white text-[#5b21b6] hover:bg-[#f8f4ff]"
                        }`}
                        title={disabled ? disabledReason || undefined : field.description}
                      >
                        <div className="min-w-0">
                          <p className="truncate text-sm font-semibold">{field.label}</p>
                          <p className={`mt-0.5 truncate text-xs ${active ? "text-white/75" : "text-neutral-400"}`}>
                            {fieldMetaLine(field)}
                          </p>
                          <p className={`mt-1 truncate text-xs ${active ? "text-white/75" : disabled ? "text-neutral-300" : "text-neutral-400"}`}>
                            {disabledReason || field.description}
                          </p>
                        </div>
                        {active ? <span className="text-xs font-semibold">Added</span> : disabled ? <span className="text-[10px] font-semibold">Unavailable</span> : null}
                      </button>
                    );
                  })}
                  {!dimensionFields.length ? <p className="text-sm text-neutral-400">No compatible dimensions are available for this dataset and chart type.</p> : null}
                </div>
              </div>

              <div className="rounded-2xl border border-[#e4f4e8] bg-white p-3 shadow-sm">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wide text-[#2f855a]">Measures</p>
                    <p className="mt-1 text-xs text-neutral-400">Aggregated KPI, chart, and scorecard values</p>
                  </div>
                  <span className="text-xs font-semibold text-[#2f855a]">{metrics.length}</span>
                </div>
                <div className="mt-3 max-h-[260px] space-y-2 overflow-y-auto pr-1">
                  {measureFields.map((field) => {
                    const disabledReason = sensitiveFields.has(field.fieldName)
                      ? "Sensitive fields cannot be used in analytics worksheets."
                      : getFieldCompatibilityReason(field, normalizedChartType);
                    const disabled = Boolean(disabledReason);
                    const active = metrics.some((item) => item.field === field.fieldName);
                    return (
                      <button
                        key={field.id}
                        type="button"
                        disabled={disabled}
                        onClick={() => addMetric(field.fieldName)}
                        className={`flex w-full items-center justify-between rounded-xl border px-3 py-2.5 text-left transition ${
                          active
                            ? "border-[#49a86b] bg-[#4cad6d] text-white"
                            : disabled
                              ? "border-neutral-200 bg-neutral-50 text-neutral-300"
                              : "border-[#d7efde] bg-white text-[#2f855a] hover:bg-[#f5fdf7]"
                        }`}
                        title={disabled ? disabledReason || undefined : field.description}
                      >
                        <div className="min-w-0">
                          <p className="truncate text-sm font-semibold">{field.label}</p>
                          <p className={`mt-0.5 truncate text-xs ${active ? "text-white/75" : "text-neutral-400"}`}>
                            {fieldMetaLine(field)}
                          </p>
                          <p className={`mt-1 truncate text-xs ${active ? "text-white/75" : disabled ? "text-neutral-300" : "text-neutral-400"}`}>
                            {disabledReason || field.description}
                          </p>
                        </div>
                        {active ? <span className="text-xs font-semibold">Added</span> : disabled ? <span className="text-[10px] font-semibold">Unavailable</span> : null}
                      </button>
                    );
                  })}
                  {!measureFields.length ? <p className="text-sm text-neutral-400">No compatible measures are available for this dataset and chart type.</p> : null}
                </div>
              </div>

              <div className="rounded-2xl border border-neutral-200 bg-white p-3 shadow-sm">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Quick Filters</p>
                    <p className="mt-1 text-xs text-neutral-400">Optional constraints</p>
                  </div>
                  <span className="text-xs font-semibold text-neutral-500">{filters.length}</span>
                </div>
                <div className="mt-3 max-h-[220px] space-y-2 overflow-y-auto pr-1">
                  {dimensionFields.filter((field) => field.isFilterable).map((field) => {
                    const disabled = sensitiveFields.has(field.fieldName);
                    const active = filters.some((item) => item.field === field.fieldName);
                    return (
                      <button
                        key={field.id}
                        type="button"
                        disabled={disabled}
                        onClick={() => addFilter(field.fieldName)}
                        className={`flex w-full items-center justify-between rounded-xl border px-3 py-2.5 text-left transition ${
                          active
                            ? "border-brand-200 bg-brand-50 text-brand-700"
                            : "border-neutral-200 bg-white text-neutral-600 hover:bg-neutral-50"
                        }`}
                        >
                        <div className="min-w-0">
                          <p className="truncate text-sm font-semibold">{field.label}</p>
                          <p className="mt-0.5 truncate text-xs text-neutral-400">{fieldMetaLine(field)}</p>
                        </div>
                        {active ? <span className="text-xs font-semibold">Added</span> : null}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </aside>

          <section className="min-w-0 bg-white">
            <div className="flex items-center justify-between border-b border-neutral-200 px-4 py-3">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-[#8c96b2]">Live Preview</p>
              <div className="flex items-center gap-2 text-xs text-neutral-500">
                <span className="rounded-full border border-neutral-200 px-3 py-1">{dimensions.length || preview?.dimensions?.length || 0} groups</span>
                <span className="rounded-full border border-neutral-200 px-3 py-1">{preview?.total_rows ?? sampleQuery.data?.row_count ?? 0} rows</span>
                <button
                  type="button"
                  onClick={() => {
                    const payload = buildPayload();
                    if (payload) {
                      previewMutation.mutate(payload);
                    }
                  }}
                  className="inline-flex h-8 items-center gap-2 rounded-md border border-neutral-200 px-3 font-semibold text-neutral-600"
                >
                  <Eye size={14} />
                  {previewMutation.isPending ? "Refreshing" : "Refresh"}
                </button>
              </div>
            </div>

            <div className="bg-[radial-gradient(circle,_rgba(148,163,184,0.14)_1px,_transparent_1px)] bg-[length:14px_14px] p-4">
              <div className="rounded-[22px] border border-neutral-200 bg-white p-5 shadow-sm">
                <div className="mb-5">
                  <h2 className="text-[2rem] font-semibold text-neutral-900">{name || "Worksheet Preview"}</h2>
                  <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-neutral-500">
                    <span>{preview?.total_rows ?? 0} data points</span>
                    <span className="rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-semibold text-neutral-600">{userScopeLabel}</span>
                  </div>
                </div>

                {chartRecommendation === "kpi_card" ? (
                  <div className="grid gap-4 md:grid-cols-3">
                    {(preview?.metrics ?? []).slice(0, 3).map((metric) => (
                      <div key={`${metric.label}-${metric.aggregation}`} className="rounded-xl border border-neutral-200 bg-neutral-50 p-5">
                        <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">{metric.label}</p>
                        <p className="mt-3 text-3xl font-bold text-neutral-950">{formatMetricValue(metric.value)}</p>
                      </div>
                    ))}
                    {!preview?.metrics?.length ? <p className="text-sm text-neutral-500">Add a metric to generate KPI output.</p> : null}
                  </div>
                ) : chartRecommendation === "line" && chartData.length && xAxisField ? (
                  <div className="h-[560px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsLineChart data={chartData}>
                        <CartesianGrid stroke="#e5e7eb" strokeDasharray="3 3" />
                        <XAxis dataKey={xAxisField} tick={{ fontSize: 12 }} angle={-40} textAnchor="end" height={88} />
                        <YAxis tick={{ fontSize: 12 }} />
                        <Tooltip />
                        {lineSeries.map((metric, index) => (
                          metric.field ? (
                            <Line
                              key={`${metric.field}-${index}`}
                              type="monotone"
                              dataKey={metric.field}
                              stroke={CHART_PALETTE[index % CHART_PALETTE.length]}
                              strokeWidth={3}
                              dot={{ r: 3 }}
                            />
                          ) : null
                        ))}
                      </RechartsLineChart>
                    </ResponsiveContainer>
                  </div>
                ) : chartRecommendation === "grouped_bar" && groupedBarData.length && xAxisField ? (
                  <div className="h-[560px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={groupedBarData}>
                        <CartesianGrid stroke="#e5e7eb" strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey={xAxisField} tick={{ fontSize: 12 }} angle={-40} textAnchor="end" height={88} />
                        <YAxis tick={{ fontSize: 12 }} />
                        <Tooltip />
                        <Legend />
                        {groupedBarSeriesKeys.map((key, index) => (
                          <Bar key={key} dataKey={key} fill={CHART_PALETTE[index % CHART_PALETTE.length]} radius={[4, 4, 0, 0]} />
                        ))}
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : chartRecommendation === "bar" && chartData.length && xAxisField && yAxisField ? (
                  <div className="h-[560px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData}>
                        <CartesianGrid stroke="#e5e7eb" strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey={xAxisField} tick={{ fontSize: 12 }} angle={-40} textAnchor="end" height={88} />
                        <YAxis tick={{ fontSize: 12 }} />
                        <Tooltip />
                        <Bar dataKey={yAxisField} radius={[5, 5, 0, 0]} maxBarSize={22}>
                          {chartData.map((_, index) => (
                            <Cell key={index} fill={CHART_PALETTE[index % CHART_PALETTE.length]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (chartRecommendation === "pie" || chartRecommendation === "donut") && chartData.length && xAxisField && pieMetricField ? (
                  <div className="h-[560px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={chartData}
                          dataKey={pieMetricField}
                          nameKey={xAxisField}
                          cx="50%"
                          cy="50%"
                          innerRadius={chartRecommendation === "donut" ? 110 : 0}
                          outerRadius={160}
                          paddingAngle={2}
                        >
                          {chartData.map((_, index) => (
                            <Cell key={index} fill={CHART_PALETTE[index % CHART_PALETTE.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="overflow-x-auto rounded-xl border border-neutral-200">
                    <table className="min-w-full divide-y divide-neutral-200 text-sm">
                      <thead className="bg-neutral-50">
                        <tr>
                          {previewColumnKeys.length ? previewColumnKeys.map((key) => (
                            <th key={key} className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-neutral-500">
                              {datasetFieldLabel(selectedDataset, key)}
                            </th>
                          )) : null}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-neutral-100 bg-white">
                        {preview?.rows?.length ? preview.rows.map((row, index) => (
                          <tr key={index}>
                            {Object.entries(row).map(([key, value]) => (
                              <td key={key} className="px-4 py-3 text-neutral-700">{value == null || value === "" ? "—" : String(value)}</td>
                            ))}
                          </tr>
                        )) : (
                          <tr>
                            <td className="px-4 py-12 text-sm text-neutral-500" colSpan={Math.max(previewColumnKeys.length, 1)}>
                              {previewMutation.isPending ? "Refreshing preview..." : "Select a dataset, add a dimension and metric, then refresh preview."}
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </section>

          <aside className="border-l border-neutral-200 bg-[#fcfcff]">
            <div className="border-b border-neutral-200 px-4 py-4">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-[#5f6b86]">Configure</p>
            </div>
            <div className="space-y-4 p-4">
              <div>
                <label className="text-xs font-bold uppercase tracking-wide text-neutral-500">Title</label>
                <input
                  className="mt-2 h-11 w-full rounded-xl border border-neutral-200 bg-white px-3 text-sm text-neutral-900"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  placeholder="Worksheet title"
                />
              </div>

              <div>
                <label className="text-xs font-bold uppercase tracking-wide text-neutral-500">Description</label>
                <textarea
                  className="mt-2 min-h-24 w-full rounded-xl border border-neutral-200 bg-white px-3 py-3 text-sm text-neutral-900"
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                  placeholder="Comparative analysis of..."
                />
              </div>

              <div>
                <label className="text-xs font-bold uppercase tracking-wide text-neutral-500">Chart Type</label>
                <div className="mt-2 grid grid-cols-4 gap-2">
                  {CHART_OPTIONS.map((option) => {
                    const Icon = option.icon;
                    const active = chartRecommendation === option.value;
                    const optionValidation = validateChartConfig({
                      chartType: (option.value === "kpi_card" ? "kpi" : option.value) as AnalyticsChartType,
                      dimensions: selectedDimensionFields,
                      measures: selectedMeasureFields,
                      filters,
                    });
                    const disabled = !optionValidation.valid && !active;
                    return (
                      <button
                        key={option.value}
                        type="button"
                        disabled={disabled}
                        onClick={() => setChartRecommendation(option.value)}
                        className={`rounded-xl border p-3 text-center text-xs font-medium ${
                          active
                            ? "border-brand-300 bg-brand-50 text-brand-700 shadow-sm"
                            : disabled
                              ? "border-neutral-200 bg-white text-neutral-300"
                              : "border-neutral-200 bg-white text-neutral-400"
                        }`}
                        title={!optionValidation.valid ? optionValidation.errors[0] : undefined}
                      >
                        <Icon className="mx-auto mb-2" size={16} />
                        {option.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {!chartValidation.valid ? (
                <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
                  <p className="font-semibold">Chart validation</p>
                  <ul className="mt-2 list-disc space-y-1 pl-5">
                    {chartValidation.errors.map((errorText) => (
                      <li key={errorText}>{errorText}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {chartValidation.warnings.length ? (
                <div className="rounded-2xl border border-neutral-200 bg-white px-4 py-3 text-sm text-neutral-700">
                  <p className="font-semibold">Suggestions</p>
                  <ul className="mt-2 list-disc space-y-1 pl-5">
                    {chartValidation.warnings.map((warning) => (
                      <li key={warning}>{warning}</li>
                    ))}
                  </ul>
                  <p className="mt-3 text-xs text-neutral-500">
                    Suggested chart types: {chartValidation.suggestedChartTypes.join(", ")}.
                  </p>
                </div>
              ) : null}

              {chartValidation.suggestedChartTypes.length ? (
                <div className="rounded-2xl border border-neutral-200 bg-white px-4 py-3 text-sm text-neutral-700">
                  <p className="font-semibold">Recommended charts</p>
                  <p className="mt-2 text-neutral-500">{chartValidation.suggestedChartTypes.join(", ")}</p>
                </div>
              ) : null}

              <div className="rounded-2xl border border-[#eee8ff] bg-white">
                <div className="border-b border-[#f1ebff] bg-[#f6f1ff] px-4 py-3">
                  <p className="text-xs font-bold uppercase tracking-wide text-[#7c3aed]">X Axis (Category)</p>
                </div>
                <div className="flex flex-wrap gap-2 p-4">
                  {dimensions.length ? dimensions.map((dimension, index) => (
                    <span key={`${dimension.field}-${index}`} className="inline-flex items-center gap-2 rounded-lg bg-[#f6f1ff] px-3 py-2 text-sm font-semibold text-[#7c3aed]">
                      {datasetFieldLabel(selectedDataset, dimension.field)}
                      <button type="button" onClick={() => setDimensions((current) => current.filter((_, itemIndex) => itemIndex !== index))}>x</button>
                    </span>
                  )) : <p className="text-sm text-neutral-400">Add a dimension from the fields list.</p>}
                </div>
              </div>

              <div className="rounded-2xl border border-[#e8f7ea] bg-white">
                <div className="flex items-center justify-between border-b border-[#edf8ef] bg-[#f4fbf5] px-4 py-3">
                  <p className="text-xs font-bold uppercase tracking-wide text-[#2f855a]">Y Axis (Values)</p>
                  <button type="button" className="text-xs font-semibold text-[#52a16f]">+ Add series</button>
                </div>
                <div className="space-y-3 p-4">
                  {metrics.length ? metrics.map((metric, index) => (
                    <div key={`${metric.field}-${index}`} className="flex items-center gap-2 rounded-xl border border-neutral-200 px-3 py-3">
                      <span className="flex-1 truncate text-sm font-semibold text-[#2f855a]">{datasetFieldLabel(selectedDataset, metric.field)}</span>
                      <select
                        className="h-9 rounded-lg border border-neutral-200 bg-white px-2 text-xs font-semibold text-neutral-600"
                        value={metric.aggregation}
                        onChange={(event) => setMetrics((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, aggregation: event.target.value } : item))}
                      >
                        {AGGREGATION_OPTIONS.filter((option) => {
                          const analyticsField = fieldByName(metric.field);
                          return analyticsField ? canAggregate(analyticsField, option.value as never) : true;
                        }).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                      </select>
                      <button type="button" onClick={() => setMetrics((current) => current.filter((_, itemIndex) => itemIndex !== index))}>
                        <Trash2 className="text-neutral-400" size={14} />
                      </button>
                    </div>
                  )) : <p className="text-sm text-neutral-400">Add a metric from the field rail.</p>}
                </div>
              </div>

              <div className="rounded-2xl border border-dashed border-[#c7f0d6] bg-[#fbfffc] p-4">
                <button type="button" className="w-full text-sm font-semibold text-[#2f855a]">
                  Add calculated metric
                </button>
              </div>

              <div className="rounded-2xl border border-neutral-200 bg-white p-4">
                <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Filters</p>
                <div className="mt-3 space-y-3">
                  {filters.length ? filters.map((filter, index) => (
                    <div key={`${filter.field}-${index}`} className="space-y-2 rounded-xl border border-neutral-200 p-3">
                      <p className="text-sm font-semibold text-neutral-900">{datasetFieldLabel(selectedDataset, filter.field)}</p>
                      <select
                        className="h-9 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm"
                        value={filter.operator}
                        onChange={(event) => setFilters((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, operator: event.target.value } : item))}
                      >
                        {FILTER_OPERATORS.filter((option) => {
                          const filterField = fieldByName(filter.field);
                          if (isDateLikeField(filterField)) {
                            return ["eq", "gte", "lte", "in"].includes(option.value);
                          }
                          return true;
                        }).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                      </select>
                      {isDateLikeField(fieldByName(filter.field)) ? (
                        <select
                          className="h-9 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm"
                          value={typeof filter.value === "string" ? filter.value : ""}
                          onChange={(event) => setFilters((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, value: event.target.value } : item))}
                        >
                          <option value="">Custom date…</option>
                          <option value="today">Today</option>
                          <option value="this_week">This week</option>
                          <option value="this_month">This month</option>
                          <option value="this_quarter">This quarter</option>
                          <option value="this_year">This year</option>
                        </select>
                      ) : null}
                      <input
                        className="h-9 w-full rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm"
                        value={Array.isArray(filter.value) ? filter.value.join(", ") : String(filter.value)}
                        onChange={(event) => setFilters((current) => current.map((item, itemIndex) => itemIndex === index ? {
                          ...item,
                          value: filter.operator === "in"
                            ? event.target.value.split(",").map((value) => value.trim()).filter(Boolean)
                            : event.target.value,
                        } : item))}
                        placeholder="Value"
                      />
                    </div>
                  )) : <p className="text-sm text-neutral-400">No filters added yet.</p>}
                </div>
              </div>

              <div className="space-y-3 rounded-2xl border border-neutral-200 bg-white p-4">
                <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">AI Assist</p>
                <textarea
                  className="min-h-24 w-full rounded-xl border border-neutral-200 bg-neutral-50 px-3 py-3 text-sm"
                  value={aiPrompt}
                  onChange={(event) => setAiPrompt(event.target.value)}
                  placeholder="Describe the worksheet you want..."
                />
                {(aiPromptQuery.data?.ai_prompt_hints.analysis_rules ?? []).length ? (
                  <div className="space-y-2">
                    {aiPromptQuery.data?.ai_prompt_hints.analysis_rules.slice(0, 3).map((rule) => (
                      <p key={rule} className="text-xs text-neutral-500">{rule}</p>
                    ))}
                  </div>
                ) : null}
                <div className="rounded-xl border border-neutral-200 bg-neutral-50 p-3 text-xs text-neutral-600">
                  <p className="font-semibold text-neutral-800">AI insight context</p>
                  <p className="mt-1">Role: {String(insightInput.role || "unscoped")}</p>
                  <p className="mt-1">Scope: {userScopeLabel}</p>
                  <p className="mt-1">Dimensions: {insightInput.dimensions.map((field) => field.label).join(", ") || "None selected"}</p>
                  <p className="mt-1">Measures: {insightInput.measures.map((field) => field.label).join(", ") || "None selected"}</p>
                </div>
                {aiSuggestionOpen && aiSuggestionMutation.data ? (
                  <div className="rounded-xl border border-brand-200 bg-brand-50 p-3">
                    <p className="text-sm font-semibold text-brand-900">{aiSuggestionMutation.data.name}</p>
                    <p className="mt-1 text-xs text-brand-800">{aiSuggestionMutation.data.description}</p>
                    <button
                      type="button"
                      onClick={applyAiSuggestion}
                      className="mt-3 inline-flex h-9 items-center justify-center rounded-lg bg-brand-700 px-3 text-sm font-semibold text-white"
                    >
                      Apply Draft
                    </button>
                  </div>
                ) : null}
              </div>
            </div>
          </aside>
        </div>
      </section>
    </div>
  );
}
