"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  AreaChart,
  ArrowRight,
  BrainCircuit,
  Bell,
  Download,
  LayoutDashboard,
  MapPinned,
  PanelTop,
  Save,
  Table2,
} from "lucide-react";

import { getApiErrorMessage } from "@/lib/api/client";
import {
  createAnalyticsWidget,
  createDashboardAlertRule,
  evaluateAllDashboardAlertRules,
  evaluateDashboardAlertRule,
  explainAnalyticsWidget,
  generateAnalyticsWidget,
  listAnalyticsDatasets,
  listDashboardAlertEvents,
  listDashboardAlertRules,
  listAnalyticsWidgets,
  listAnalyticsWorksheets,
  previewAnalyticsWidget,
  refreshAnalyticsWidget,
} from "@/lib/api/analytics";
import { getEmbeddedAnalyticsModuleMeta } from "@/features/reports/embedded-analytics-actions";
import { WidgetPreviewSurface } from "@/features/reports/analytics-widget-preview";

type ExportToggle = {
  format: string;
  checked: boolean;
  setChecked: (value: boolean) => void;
};

const WIDGET_TYPES = [
  { value: "kpi_card", label: "KPI Card", icon: PanelTop },
  { value: "grouped_kpi", label: "Grouped KPI", icon: PanelTop },
  { value: "bar_chart", label: "Bar Chart", icon: AreaChart },
  { value: "line_chart", label: "Line Chart", icon: AreaChart },
  { value: "table", label: "Table", icon: Table2 },
  { value: "map", label: "Map", icon: MapPinned },
  { value: "queue_card", label: "Queue Card", icon: Table2 },
  { value: "ai_insight", label: "AI Insight", icon: BrainCircuit },
];

export function AnalyticsWidgetBuilder({
  initialWorksheetId = "",
  initialModuleSource = "",
}: {
  initialWorksheetId?: string;
  initialModuleSource?: string;
}) {
  const [worksheetId, setWorksheetId] = useState(initialWorksheetId);
  const [title, setTitle] = useState("");
  const [widgetType, setWidgetType] = useState("kpi_card");
  const [color, setColor] = useState("#16a34a");
  const [showLegend, setShowLegend] = useState(true);
  const [allowCsv, setAllowCsv] = useState(true);
  const [allowJson, setAllowJson] = useState(true);
  const [allowPng, setAllowPng] = useState(true);
  const [allowPdf, setAllowPdf] = useState(true);
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiReviewOpen, setAiReviewOpen] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [savedWidgetId, setSavedWidgetId] = useState("");
  const [livePreview, setLivePreview] = useState<Awaited<ReturnType<typeof previewAnalyticsWidget>> | null>(null);
  const [alertWidgetId, setAlertWidgetId] = useState("");
  const [alertName, setAlertName] = useState("");
  const [alertMetricKey, setAlertMetricKey] = useState("total_rows");
  const [alertOperator, setAlertOperator] = useState("gt");
  const [alertThreshold, setAlertThreshold] = useState("");
  const [alertChannels, setAlertChannels] = useState<string[]>(["in_app"]);
  const [alertRecipientIds, setAlertRecipientIds] = useState("");

  const worksheetsQuery = useQuery({
    queryKey: ["analytics-worksheets"],
    queryFn: listAnalyticsWorksheets,
  });
  const datasetsQuery = useQuery({
    queryKey: ["analytics-datasets"],
    queryFn: listAnalyticsDatasets,
  });

  const widgetsQuery = useQuery({
    queryKey: ["analytics-widgets"],
    queryFn: listAnalyticsWidgets,
  });
  const selectedAlertWidgetId = alertWidgetId || savedWidgetId || widgetsQuery.data?.[0]?.id || "";
  const alertRulesQuery = useQuery({
    queryKey: ["dashboard-alert-rules", selectedAlertWidgetId],
    queryFn: () => listDashboardAlertRules(selectedAlertWidgetId || undefined),
  });
  const alertEventsQuery = useQuery({
    queryKey: ["dashboard-alert-events", selectedAlertWidgetId],
    queryFn: () => listDashboardAlertEvents(selectedAlertWidgetId ? { widget: selectedAlertWidgetId } : undefined),
  });

  const selectedWorksheet = useMemo(
    () => worksheetsQuery.data?.find((worksheet) => worksheet.id === worksheetId),
    [worksheetId, worksheetsQuery.data],
  );
  const filteredWorksheets = useMemo(() => {
    const worksheets = worksheetsQuery.data ?? [];
    if (!initialModuleSource) {
      return worksheets;
    }
    const datasetCodes = new Set(
      (datasetsQuery.data ?? [])
        .filter((dataset) => dataset.module_source === initialModuleSource)
        .map((dataset) => dataset.code),
    );
    return worksheets.filter((worksheet) => datasetCodes.has(worksheet.dataset_code));
  }, [datasetsQuery.data, initialModuleSource, worksheetsQuery.data]);
  const moduleMeta = useMemo(
    () => (initialModuleSource ? getEmbeddedAnalyticsModuleMeta(initialModuleSource) : null),
    [initialModuleSource],
  );
  const selectedAlertWidget = useMemo(
    () => widgetsQuery.data?.find((widget) => widget.id === selectedAlertWidgetId) ?? null,
    [selectedAlertWidgetId, widgetsQuery.data],
  );
  const selectedAlertWorksheet = useMemo(
    () => worksheetsQuery.data?.find((worksheet) => worksheet.id === selectedAlertWidget?.worksheet) ?? null,
    [selectedAlertWidget, worksheetsQuery.data],
  );
  const alertMetricOptions = useMemo(() => {
    const metrics = selectedAlertWorksheet?.preview_output?.metrics ?? [];
    return [
      { value: "total_rows", label: "Total rows" },
      ...metrics.map((metric) => ({
        value: metric.field ? `metric:${metric.field}` : `label:${metric.label}`,
        label: metric.label,
      })),
    ];
  }, [selectedAlertWorksheet]);
  const exportToggles: ExportToggle[] = [
    { format: "csv", checked: allowCsv, setChecked: setAllowCsv },
    { format: "json", checked: allowJson, setChecked: setAllowJson },
    { format: "png", checked: allowPng, setChecked: setAllowPng },
    { format: "pdf", checked: allowPdf, setChecked: setAllowPdf },
  ];

  useEffect(() => {
    if (worksheetId || initialWorksheetId || !filteredWorksheets.length) return;
    setWorksheetId(filteredWorksheets[0].id);
  }, [filteredWorksheets, initialWorksheetId, worksheetId]);

  useEffect(() => {
    if (!title.trim() && selectedWorksheet) {
      setTitle(`${selectedWorksheet.name} Widget`);
    }
  }, [selectedWorksheet, title]);

  useEffect(() => {
    if (!selectedAlertWidgetId) return;
    if (!alertName.trim()) {
      const widgetTitle = widgetsQuery.data?.find((widget) => widget.id === selectedAlertWidgetId)?.title ?? "Widget";
      setAlertName(`${widgetTitle} Alert`);
    }
  }, [alertName, selectedAlertWidgetId, widgetsQuery.data]);

  useEffect(() => {
    if (!alertMetricOptions.find((item) => item.value === alertMetricKey)) {
      setAlertMetricKey(alertMetricOptions[0]?.value ?? "total_rows");
    }
  }, [alertMetricKey, alertMetricOptions]);

  const previewMutation = useMutation({
    mutationFn: previewAnalyticsWidget,
    onSuccess: (payload) => {
      setLivePreview(payload);
      setError("");
    },
    onError: (mutationError) => {
      setError(getApiErrorMessage(mutationError, "Could not preview widget."));
    },
  });

  const saveMutation = useMutation({
    mutationFn: createAnalyticsWidget,
    onSuccess: (widget) => {
      setSavedWidgetId(widget.id);
      setSuccess("Widget saved and ready for dashboard composition.");
      setError("");
      void widgetsQuery.refetch();
    },
    onError: (mutationError) => {
      setError(getApiErrorMessage(mutationError, "Could not save widget."));
    },
  });

  const aiSuggestionMutation = useMutation({
    mutationFn: generateAnalyticsWidget,
    onSuccess: () => {
      setAiReviewOpen(true);
      setError("");
    },
    onError: (mutationError) => {
      setError(getApiErrorMessage(mutationError, "Could not generate widget suggestion."));
    },
  });

  const explainMutation = useMutation({
    mutationFn: explainAnalyticsWidget,
    onError: (mutationError) => {
      setError(getApiErrorMessage(mutationError, "Could not explain widget."));
    },
  });
  const refreshMutation = useMutation({
    mutationFn: refreshAnalyticsWidget,
    onSuccess: (payload) => {
      setLivePreview(payload);
      setSuccess("Widget data refreshed from the worksheet source.");
      setError("");
    },
    onError: (mutationError) => {
      setError(getApiErrorMessage(mutationError, "Could not refresh widget data."));
    },
  });
  const createAlertMutation = useMutation({
    mutationFn: createDashboardAlertRule,
    onSuccess: async (rule) => {
      setAlertWidgetId(rule.widget);
      setAlertName("");
      setAlertThreshold("");
      setAlertRecipientIds("");
      setSuccess("Alert rule created. You can run it immediately or let the dashboard alert checks pick it up.");
      setError("");
      await alertRulesQuery.refetch();
    },
    onError: (mutationError) => {
      setError(getApiErrorMessage(mutationError, "Could not create alert rule."));
    },
  });
  const evaluateAlertMutation = useMutation({
    mutationFn: evaluateDashboardAlertRule,
    onSuccess: async () => {
      setSuccess("Alert rule evaluated.");
      setError("");
      await alertEventsQuery.refetch();
      await alertRulesQuery.refetch();
    },
    onError: (mutationError) => {
      setError(getApiErrorMessage(mutationError, "Could not evaluate alert rule."));
    },
  });
  const evaluateAllAlertsMutation = useMutation({
    mutationFn: evaluateAllDashboardAlertRules,
    onSuccess: async (result) => {
      setSuccess(`Evaluated ${result.evaluated} alert rule${result.evaluated === 1 ? "" : "s"} and triggered ${result.triggered}.`);
      setError("");
      await alertEventsQuery.refetch();
      await alertRulesQuery.refetch();
    },
    onError: (mutationError) => {
      setError(getApiErrorMessage(mutationError, "Could not run alert checks."));
    },
  });

  const buildPayload = useCallback(() => {
    if (!worksheetId || !title.trim()) {
      setError("Select a worksheet and title the widget before previewing or saving.");
      return null;
    }
    return {
      worksheet: worksheetId,
      title: title.trim(),
      widget_type: widgetType,
      scope_type: "private",
      visual_config: {
        color,
        showLegend,
      },
      filter_behavior: {
        inherits_global_filters: true,
      },
      refresh_behavior: {
        mode: "manual",
      },
      export_options: {
        csv: allowCsv,
        json: allowJson,
        png: allowPng,
        pdf: allowPdf,
      },
    };
  }, [allowCsv, allowJson, allowPdf, allowPng, color, showLegend, title, widgetType, worksheetId]);

  function applyAiSuggestion() {
    const suggestion = aiSuggestionMutation.data;
    if (!suggestion) return;
    setWorksheetId(suggestion.worksheet);
    setTitle(suggestion.title);
    setWidgetType(suggestion.widget_type);
    setColor(String(suggestion.visual_config.color ?? "#16a34a"));
    setShowLegend(Boolean(suggestion.visual_config.showLegend ?? false));
    setAllowCsv(Boolean(suggestion.export_options.csv));
    setAllowJson(Boolean(suggestion.export_options.json));
    setAllowPng(Boolean(suggestion.export_options.png));
    setAllowPdf(Boolean(suggestion.export_options.pdf));
    setSuccess("AI widget suggestion applied. Review the preview, then save when ready.");
    setAiReviewOpen(false);
  }

  useEffect(() => {
    if (!worksheetId || !title.trim()) return;
    const payload = buildPayload();
    if (!payload) return;
    const timeout = window.setTimeout(() => {
      previewMutation.mutate(payload);
    }, 350);
    return () => window.clearTimeout(timeout);
  }, [allowCsv, allowJson, allowPdf, allowPng, buildPayload, color, previewMutation, showLegend, title, widgetType, worksheetId]);

  return (
    <div className="grid gap-5">
      {error ? <div className="rounded-lg border border-danger-200 bg-danger-50 px-4 py-3 text-sm font-medium text-danger-700">{error}</div> : null}
      {success ? <div className="rounded-lg border border-brand-200 bg-brand-50 px-4 py-3 text-sm font-medium text-brand-800">{success}</div> : null}
      {moduleMeta ? (
        <div className="rounded-lg border border-brand-200 bg-brand-50 px-4 py-3 text-sm text-brand-900">
          Widget builder is focused on <span className="font-semibold">{moduleMeta.label}</span> worksheets so embedded module analytics stay on the shared engine.
        </div>
      ) : null}

      <div className="grid gap-5 xl:grid-cols-[320px_minmax(0,1fr)]">
        <section className="space-y-5 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm xl:sticky xl:top-24 xl:self-start">
          <div>
            <div className="flex items-center gap-2">
              <LayoutDashboard className="text-brand-700" size={18} />
              <h2 className="text-sm font-bold text-neutral-900">Widget setup</h2>
            </div>
            <p className="mt-1 text-sm text-neutral-500">Choose a worksheet, decide how to present it, and save a reusable widget.</p>
          </div>

          <div className="space-y-3">
            <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">Source worksheet</label>
            <select className="h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={worksheetId} onChange={(event) => setWorksheetId(event.target.value)}>
              <option value="">Select worksheet</option>
              {filteredWorksheets.map((worksheet) => (
                <option key={worksheet.id} value={worksheet.id}>
                  {worksheet.name}
                </option>
              ))}
            </select>
            {selectedWorksheet ? <p className="text-xs text-neutral-500">{selectedWorksheet.description || "No worksheet description."}</p> : null}
            {moduleMeta && !filteredWorksheets.length ? (
              <p className="text-xs text-neutral-500">No saved worksheets match this module yet. Start by saving a worksheet for this module’s dataset.</p>
            ) : null}
          </div>

          <div className="space-y-3">
            <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">Widget title</label>
            <input className="h-11 w-full rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm" value={title} onChange={(event) => setTitle(event.target.value)} placeholder="e.g. Certification coverage by state" />
          </div>

          <div className="space-y-3">
            <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">Widget type</label>
            <div className="grid grid-cols-2 gap-2">
              {WIDGET_TYPES.map((item) => {
                const Icon = item.icon;
                const active = widgetType === item.value;
                return (
                  <button
                    key={item.value}
                    type="button"
                    onClick={() => setWidgetType(item.value)}
                    className={`flex min-h-16 flex-col items-start gap-2 rounded-md border px-3 py-3 text-left text-sm font-semibold ${
                      active ? "border-brand-300 bg-brand-50 text-brand-700" : "border-neutral-200 bg-white text-neutral-700"
                    }`}
                  >
                    <Icon size={16} />
                    {item.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="space-y-3">
            <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">Visual options</label>
            <div className="grid gap-3">
              <input className="h-11 w-full rounded-md border border-neutral-200 bg-white px-3" type="color" value={color} onChange={(event) => setColor(event.target.value)} />
              <label className="flex items-center gap-3 rounded-md border border-neutral-200 px-3 py-2 text-sm text-neutral-700">
                <input checked={showLegend} onChange={(event) => setShowLegend(event.target.checked)} type="checkbox" />
                Show legend where applicable
              </label>
            </div>
          </div>

          <div className="space-y-3">
            <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">Export formats</label>
            <div className="grid gap-2">
              {exportToggles.map((toggle) => (
                <label key={toggle.format} className="flex items-center gap-3 rounded-md border border-neutral-200 px-3 py-2 text-sm text-neutral-700">
                  <input checked={toggle.checked} onChange={(event) => toggle.setChecked(event.target.checked)} type="checkbox" />
                  <span className="uppercase">{toggle.format}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="grid gap-3">
              <button
                type="button"
                onClick={() => {
                  const payload = buildPayload();
                  if (payload) previewMutation.mutate(payload);
              }}
              className="inline-flex h-11 items-center justify-center gap-2 rounded-md border border-brand-200 bg-brand-50 px-4 text-sm font-semibold text-brand-700"
              >
                Preview Widget
              </button>
              <button
                type="button"
                disabled={!savedWidgetId || refreshMutation.isPending}
                onClick={() => refreshMutation.mutate(savedWidgetId)}
                className="inline-flex h-11 items-center justify-center gap-2 rounded-md border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700 disabled:opacity-60"
              >
                {refreshMutation.isPending ? "Refreshing..." : "Refresh Widget Data"}
              </button>
              <button
                type="button"
                onClick={() => {
                  const payload = buildPayload();
                  if (payload) saveMutation.mutate(payload);
              }}
              className="inline-flex h-11 items-center justify-center gap-2 rounded-md bg-brand-700 px-4 text-sm font-semibold text-white"
            >
              <Save size={16} />
              Save Widget
            </button>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-neutral-50 p-3">
            <div className="flex items-center gap-2">
              <BrainCircuit className="text-brand-700" size={16} />
              <p className="text-sm font-semibold text-neutral-900">AI assistant</p>
            </div>
            <textarea
              className="mt-3 min-h-24 w-full rounded-md border border-neutral-200 bg-white px-3 py-3 text-sm"
              value={aiPrompt}
              onChange={(event) => setAiPrompt(event.target.value)}
              placeholder="Describe the widget you want, for example: turn this into a KPI summary for executives."
            />
            <div className="mt-3 grid gap-2">
              <button
                type="button"
                disabled={!worksheetId || !aiPrompt.trim() || aiSuggestionMutation.isPending}
                onClick={() => aiSuggestionMutation.mutate({ worksheet: worksheetId, prompt: aiPrompt.trim() })}
                className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-brand-200 bg-brand-50 px-4 text-sm font-semibold text-brand-700 disabled:opacity-50"
              >
                <BrainCircuit size={16} />
                {aiSuggestionMutation.isPending ? "Generating..." : "Generate Widget Draft"}
              </button>
              <button
                type="button"
                disabled={!savedWidgetId || explainMutation.isPending}
                onClick={() => {
                  const insightContext = selectedWorksheet ? {
                    dimensions: (selectedWorksheet.dimensions || []).map((d) => ({ fieldName: d.field, label: d.field, fieldType: "dimension" })),
                    measures: (selectedWorksheet.metrics || []).map((m) => ({ fieldName: m.field, label: m.label || m.field, fieldType: "measure", defaultAggregation: m.aggregation })),
                    chartType: selectedWorksheet.chart_recommendation || "table",
                    filters: (selectedWorksheet.filters || []).map((f) => ({ field: f.field, operator: f.operator, value: f.value })),
                    role: "analytics",
                    aggregatedData: selectedWorksheet.preview_output?.rows || [],
                  } : undefined;
                  explainMutation.mutate({ widget: savedWidgetId, prompt: aiPrompt.trim() || "Explain this widget", insightContext });
                }}
                className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700 disabled:opacity-50"
              >
                {explainMutation.isPending ? "Explaining..." : "Explain Saved Widget"}
              </button>
            </div>
            {aiReviewOpen && aiSuggestionMutation.data ? (
              <div className="mt-3 rounded-md border border-brand-200 bg-white p-3">
                <p className="text-sm font-semibold text-neutral-900">{aiSuggestionMutation.data.title}</p>
                <p className="mt-1 text-xs uppercase tracking-wide text-neutral-500">{aiSuggestionMutation.data.widget_type.replaceAll("_", " ")}</p>
                <div className="mt-3 space-y-1">
                  {aiSuggestionMutation.data.reasoning.map((line) => (
                    <p key={line} className="text-xs text-neutral-600">{line}</p>
                  ))}
                </div>
                <button
                  type="button"
                  onClick={applyAiSuggestion}
                  className="mt-3 inline-flex h-9 items-center justify-center rounded-md bg-brand-700 px-3 text-sm font-semibold text-white"
                >
                  Apply Draft
                </button>
              </div>
            ) : null}
            {explainMutation.data ? (
              <div className="mt-3 rounded-md border border-neutral-200 bg-white p-3">
                <p className="text-sm font-semibold text-neutral-900">{explainMutation.data.summary}</p>
                <div className="mt-2 space-y-1">
                  {explainMutation.data.insights.map((line) => (
                    <p key={line} className="text-xs text-neutral-600">{line}</p>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        </section>

        <div className="grid gap-5">
          <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-sm font-bold text-neutral-900">Widget preview</h2>
                <p className="mt-1 text-sm text-neutral-500">Widget previews are rendered from worksheet output and saved presentation settings.</p>
              </div>
              <div className="flex flex-wrap gap-2">
                {(livePreview?.export_formats ?? previewMutation.data?.export_formats ?? []).map((format) => (
                  <span key={format} className="inline-flex items-center gap-1 rounded-full bg-neutral-100 px-3 py-1 text-xs font-semibold text-neutral-700">
                    <Download size={12} />
                    {format.toUpperCase()}
                  </span>
                ))}
              </div>
            </div>
            <div className="mt-4">
              <WidgetPreviewSurface preview={livePreview?.preview ?? previewMutation.data?.preview ?? null} />
            </div>
          </section>

          <section className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_340px]">
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <h2 className="text-sm font-bold text-neutral-900">Worksheet source summary</h2>
              {selectedWorksheet ? (
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-md bg-neutral-50 p-3">
                    <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Dataset</p>
                    <p className="mt-1 text-sm font-semibold text-neutral-950">{selectedWorksheet.dataset_code}</p>
                  </div>
                  <div className="rounded-md bg-neutral-50 p-3">
                    <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Chart recommendation</p>
                    <p className="mt-1 text-sm font-semibold text-neutral-950">{selectedWorksheet.chart_recommendation || "table"}</p>
                  </div>
                  <div className="rounded-md bg-neutral-50 p-3">
                    <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Metrics</p>
                    <p className="mt-1 text-sm font-semibold text-neutral-950">{selectedWorksheet.metrics.length}</p>
                  </div>
                  <div className="rounded-md bg-neutral-50 p-3">
                    <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Dimensions</p>
                    <p className="mt-1 text-sm font-semibold text-neutral-950">{selectedWorksheet.dimensions.length}</p>
                  </div>
                </div>
              ) : (
                <p className="mt-4 text-sm text-neutral-500">Select a worksheet to inspect its preview shape and downstream widget compatibility.</p>
              )}
            </div>

            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-sm font-bold text-neutral-900">Saved widgets</h2>
                <span className="rounded bg-neutral-100 px-2.5 py-1 text-xs font-semibold text-neutral-600">{widgetsQuery.data?.length ?? 0}</span>
              </div>
              <div className="mt-4 space-y-3">
                {(widgetsQuery.data ?? []).slice(0, 6).map((widget) => (
                  <div key={widget.id} className="rounded-md border border-neutral-200 p-3">
                    <p className="text-sm font-semibold text-neutral-900">{widget.title}</p>
                    <p className="mt-1 text-xs uppercase tracking-wide text-neutral-500">{widget.widget_type.replaceAll("_", " ")}</p>
                    <p className="mt-2 text-xs text-neutral-500">{widget.worksheet_name}</p>
                  </div>
                ))}
                {!widgetsQuery.data?.length ? <p className="text-sm text-neutral-500">No widgets saved yet.</p> : null}
              </div>
            </div>
          </section>

          <section className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px]">
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Bell className="text-brand-700" size={16} />
                  <h2 className="text-sm font-bold text-neutral-900">Widget alerts</h2>
                </div>
                <button
                  type="button"
                  onClick={() => evaluateAllAlertsMutation.mutate()}
                  disabled={evaluateAllAlertsMutation.isPending}
                  className="inline-flex h-9 items-center justify-center rounded-md border border-neutral-200 bg-white px-3 text-sm font-semibold text-neutral-700 disabled:opacity-60"
                >
                  Run all checks
                </button>
              </div>
              <p className="mt-1 text-sm text-neutral-500">Create threshold rules from saved widget metrics and notify the right people when a widget moves outside bounds.</p>

              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <div className="space-y-2 sm:col-span-2">
                  <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">Widget</label>
                  <select className="h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={selectedAlertWidgetId} onChange={(event) => setAlertWidgetId(event.target.value)}>
                    {(widgetsQuery.data ?? []).map((widget) => (
                      <option key={widget.id} value={widget.id}>
                        {widget.title}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2 sm:col-span-2">
                  <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">Alert name</label>
                  <input className="h-11 w-full rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm" value={alertName} onChange={(event) => setAlertName(event.target.value)} />
                </div>
                <div className="space-y-2">
                  <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">Metric</label>
                  <select className="h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={alertMetricKey} onChange={(event) => setAlertMetricKey(event.target.value)}>
                    {alertMetricOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">Condition</label>
                  <select className="h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={alertOperator} onChange={(event) => setAlertOperator(event.target.value)}>
                    <option value="gt">Greater than</option>
                    <option value="gte">Greater than or equal</option>
                    <option value="lt">Less than</option>
                    <option value="lte">Less than or equal</option>
                    <option value="eq">Equal</option>
                    <option value="neq">Not equal</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">Threshold</label>
                  <input className="h-11 w-full rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm" value={alertThreshold} onChange={(event) => setAlertThreshold(event.target.value)} placeholder="e.g. 80" />
                </div>
                <div className="space-y-2 sm:col-span-2">
                  <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">Recipient user IDs</label>
                  <input
                    className="h-11 w-full rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm"
                    value={alertRecipientIds}
                    onChange={(event) => setAlertRecipientIds(event.target.value)}
                    placeholder="Optional, comma-separated"
                  />
                </div>
                <div className="space-y-2 sm:col-span-2">
                  <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">Channels</label>
                  <div className="grid gap-2 sm:grid-cols-2">
                    {["in_app", "email", "sms", "whatsapp"].map((channel) => (
                      <label key={channel} className="flex items-center gap-3 rounded-md border border-neutral-200 px-3 py-2 text-sm text-neutral-700">
                        <input
                          type="checkbox"
                          checked={alertChannels.includes(channel)}
                          onChange={(event) =>
                            setAlertChannels((current) => (
                              event.target.checked ? Array.from(new Set([...current, channel])) : current.filter((item) => item !== channel)
                            ))
                          }
                        />
                        {channel.replaceAll("_", " ")}
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-4">
                <button
                  type="button"
                  disabled={!selectedAlertWidgetId || !alertName.trim() || !alertThreshold.trim() || createAlertMutation.isPending}
                  onClick={() =>
                    createAlertMutation.mutate({
                      widget: selectedAlertWidgetId,
                      name: alertName.trim(),
                      description: "",
                      metric_key: alertMetricKey,
                      metric_label: alertMetricOptions.find((item) => item.value === alertMetricKey)?.label ?? alertMetricKey,
                      operator: alertOperator,
                      threshold_value: alertThreshold.trim(),
                      notification_channels: alertChannels,
                      recipient_user_ids: alertRecipientIds.split(",").map((value) => value.trim()).filter(Boolean),
                    })
                  }
                  className="inline-flex h-10 items-center justify-center rounded-md bg-brand-700 px-4 text-sm font-semibold text-white disabled:opacity-60"
                >
                  Create Alert
                </button>
              </div>
            </div>

            <div className="grid gap-5">
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
                <div className="flex items-center justify-between gap-3">
                  <h2 className="text-sm font-bold text-neutral-900">Alert rules</h2>
                  <span className="rounded bg-neutral-100 px-2.5 py-1 text-xs font-semibold text-neutral-600">{alertRulesQuery.data?.length ?? 0}</span>
                </div>
                <div className="mt-4 space-y-3">
                  {(alertRulesQuery.data ?? []).slice(0, 6).map((rule) => (
                    <div key={rule.id} className="rounded-md border border-neutral-200 p-3">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-semibold text-neutral-900">{rule.name}</p>
                          <p className="mt-1 text-xs text-neutral-500">
                            {rule.metric_label || rule.metric_key} {rule.operator} {rule.threshold_value}
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={() => evaluateAlertMutation.mutate(rule.id)}
                          disabled={evaluateAlertMutation.isPending}
                          className="inline-flex h-8 items-center justify-center rounded-md border border-neutral-200 bg-white px-3 text-xs font-semibold text-neutral-700 disabled:opacity-60"
                        >
                          Run
                        </button>
                      </div>
                      <p className="mt-2 text-xs text-neutral-500">
                        Triggered {rule.trigger_count} time{rule.trigger_count === 1 ? "" : "s"}
                        {rule.last_triggered_at ? ` • Last triggered ${new Date(rule.last_triggered_at).toLocaleString()}` : ""}
                      </p>
                    </div>
                  ))}
                  {!alertRulesQuery.data?.length ? <p className="text-sm text-neutral-500">No alert rules yet for this widget.</p> : null}
                </div>
              </div>

              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
                <h2 className="text-sm font-bold text-neutral-900">Alert history</h2>
                <div className="mt-4 space-y-3">
                  {(alertEventsQuery.data ?? []).slice(0, 6).map((event) => (
                    <div key={event.id} className="rounded-md border border-neutral-200 p-3">
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-sm font-semibold text-neutral-900">{event.rule_name}</p>
                        <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${event.status === "triggered" ? "bg-danger-50 text-danger-700" : event.status === "resolved" ? "bg-emerald-50 text-emerald-700" : "bg-neutral-100 text-neutral-700"}`}>
                          {event.status.replaceAll("_", " ")}
                        </span>
                      </div>
                      <p className="mt-2 text-sm text-neutral-600">{event.message}</p>
                      <p className="mt-2 text-xs text-neutral-500">
                        {event.observed_value ?? "—"} vs {event.threshold_value ?? "—"} • {new Date(event.created_at).toLocaleString()}
                      </p>
                    </div>
                  ))}
                  {!alertEventsQuery.data?.length ? <p className="text-sm text-neutral-500">No alert history yet.</p> : null}
                </div>
              </div>
            </div>
          </section>

          {savedWidgetId ? (
            <section className="rounded-lg border border-brand-200 bg-brand-50 p-5 shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Next Step</p>
                  <h2 className="mt-2 text-lg font-bold text-brand-950">Widget ready for dashboard composition</h2>
                  <p className="mt-2 text-sm text-brand-900">Carry this widget into the dashboard canvas builder in the next workspace.</p>
                </div>
                <Link
                  href={`/federal/dashboard/canvas-builder?widgetId=${savedWidgetId}`}
                  className="inline-flex h-11 items-center gap-2 rounded-md bg-brand-700 px-4 text-sm font-semibold text-white"
                >
                  Continue to Canvas Builder
                  <ArrowRight size={16} />
                </Link>
              </div>
            </section>
          ) : null}
        </div>
      </div>
    </div>
  );
}
