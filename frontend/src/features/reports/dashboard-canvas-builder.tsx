"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  ArrowDown,
  ArrowRight,
  ArrowUp,
  BrainCircuit,
  Filter,
  LayoutDashboard,
  Loader2,
  MessageSquareText,
  Plus,
  Rocket,
  Save,
  Sparkles,
  Trash2,
} from "lucide-react";

import { getApiErrorMessage } from "@/lib/api/client";
import {
  createDashboardBlock,
  createDashboardCanvas,
  deleteDashboardBlock,
  explainDashboardCanvas,
  generateDashboardCanvas,
  listAnalyticsWidgets,
  listAnalyticsWorksheets,
  listDashboardBlocks,
  listDashboardCanvases,
  listPublishedDashboards,
  publishDashboardCanvas,
  updateDashboardBlock,
  updateDashboardCanvas,
  type AnalyticsWidget,
  type AnalyticsWorksheet,
  type DashboardCanvasBlock,
  type PublishedDashboard,
} from "@/lib/api/analytics";
import { buildWidgetPreviewFromWorksheet, WidgetPreviewSurface } from "@/features/reports/analytics-widget-preview";
import {
  applicableWidgetIdsForFilter,
  buildFilterFieldOptions,
  type CompatibleFieldOption,
} from "@/features/reports/dashboard-filtering";
import { getEmbeddedAnalyticsModuleMeta } from "@/features/reports/embedded-analytics-actions";

type CanvasBlockDraft = {
  id?: string;
  clientId: string;
  widget?: string | null;
  block_type: "widget" | "text" | "filter" | "ai_insight";
  title: string;
  content: Record<string, unknown>;
  position: { w: number; h: number };
  visibility_rules: Record<string, unknown>;
  sort_order: number;
};

function draftFromApiBlock(block: DashboardCanvasBlock): CanvasBlockDraft {
  return {
    id: block.id,
    clientId: block.id,
    widget: block.widget ?? null,
    block_type: block.block_type as CanvasBlockDraft["block_type"],
    title: block.title,
    content: block.content ?? {},
    position: {
      w: Number((block.position?.w as number | undefined) ?? 6),
      h: Number((block.position?.h as number | undefined) ?? 320),
    },
    visibility_rules: block.visibility_rules ?? {},
    sort_order: block.sort_order,
  };
}

function widgetById(items: AnalyticsWidget[] | undefined, widgetId?: string | null) {
  return items?.find((item) => item.id === widgetId) ?? null;
}

function worksheetByWidget(widget: AnalyticsWidget | null, worksheets: AnalyticsWorksheet[] | undefined) {
  return widget ? worksheets?.find((item) => item.id === widget.worksheet) ?? null : null;
}

function nextClientId() {
  return `draft-${Math.random().toString(36).slice(2, 10)}`;
}

function CanvasBlockCard({
  block,
  widgets,
  worksheets,
  filterFieldOptions,
  widgetCompatibilityByField,
  onChange,
  onRemove,
  onMoveUp,
  onMoveDown,
}: {
  block: CanvasBlockDraft;
  widgets: AnalyticsWidget[];
  worksheets: AnalyticsWorksheet[];
  filterFieldOptions: CompatibleFieldOption[];
  widgetCompatibilityByField: Record<string, string[]>;
  onChange: (next: CanvasBlockDraft) => void;
  onRemove: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
}) {
  const widget = widgetById(widgets, block.widget);
  const worksheet = worksheetByWidget(widget, worksheets);
  const widgetPreview = widget ? buildWidgetPreviewFromWorksheet(widget, worksheet) : null;
  const selectedFilterField = String(block.content.field ?? "");
  const selectedFieldOption = filterFieldOptions.find((option) => option.field === selectedFilterField);
  const applicableWidgetTitles = selectedFieldOption?.widgetTitles ?? [];
  const widgetAffectedByFilters = widget
    ? Object.entries(widgetCompatibilityByField)
        .filter(([, widgetIds]) => widgetIds.includes(widget.id))
        .map(([field]) => field)
    : [];

  return (
    <div
      className="rounded-lg border border-neutral-200 bg-white shadow-sm"
      style={{ gridColumn: `span ${block.position.w} / span ${block.position.w}` }}
    >
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-200 px-4 py-3">
        <div>
          <p className="text-sm font-bold text-neutral-900">{block.title || "Untitled block"}</p>
          <p className="mt-1 text-xs uppercase tracking-wide text-neutral-500">{block.block_type.replaceAll("_", " ")}</p>
        </div>
        <div className="flex items-center gap-2">
          <button type="button" onClick={onMoveUp} className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-neutral-200 text-neutral-600"><ArrowUp size={14} /></button>
          <button type="button" onClick={onMoveDown} className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-neutral-200 text-neutral-600"><ArrowDown size={14} /></button>
          <button type="button" onClick={onRemove} className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-neutral-200 text-danger-700"><Trash2 size={14} /></button>
        </div>
      </div>

      <div className="grid gap-4 p-4 lg:grid-cols-[240px_minmax(0,1fr)]">
        <div className="space-y-3">
          <input
            className="h-10 w-full rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm"
            value={block.title}
            onChange={(event) => onChange({ ...block, title: event.target.value })}
            placeholder="Block title"
          />
          <div className="grid grid-cols-2 gap-3">
            <select
              className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm"
              value={block.position.w}
              onChange={(event) => onChange({ ...block, position: { ...block.position, w: Number(event.target.value) } })}
            >
              <option value={3}>1/4 width</option>
              <option value={4}>1/3 width</option>
              <option value={6}>1/2 width</option>
              <option value={8}>2/3 width</option>
              <option value={12}>Full width</option>
            </select>
            <select
              className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm"
              value={block.position.h}
              onChange={(event) => onChange({ ...block, position: { ...block.position, h: Number(event.target.value) } })}
            >
              <option value={220}>Compact</option>
              <option value={320}>Standard</option>
              <option value={420}>Tall</option>
            </select>
          </div>

          {block.block_type === "widget" ? (
            <select
              className="h-10 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm"
              value={block.widget ?? ""}
              onChange={(event) => onChange({ ...block, widget: event.target.value || null })}
            >
              <option value="">Select widget</option>
              {widgets.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.title}
                </option>
              ))}
            </select>
          ) : null}

          {block.block_type === "text" ? (
            <textarea
              className="min-h-32 w-full rounded-md border border-neutral-200 bg-neutral-50 px-3 py-3 text-sm"
              value={String(block.content.body ?? "")}
              onChange={(event) => onChange({ ...block, content: { ...block.content, body: event.target.value } })}
              placeholder="Write narrative guidance, context, or interpretation."
            />
          ) : null}

          {block.block_type === "filter" ? (
            <div className="space-y-3">
              <input
                className="h-10 w-full rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={String(block.content.label ?? "")}
                onChange={(event) => onChange({ ...block, content: { ...block.content, label: event.target.value } })}
                placeholder="Filter label"
              />
              <select
                className="h-10 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm"
                value={selectedFilterField}
                onChange={(event) => onChange({ ...block, content: { ...block.content, field: event.target.value } })}
              >
                <option value="">Select compatible field</option>
                {filterFieldOptions.map((option) => (
                  <option key={option.field} value={option.field}>
                    {option.label} ({option.widgetIds.length})
                  </option>
                ))}
              </select>
              <select
                className="h-10 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm"
                value={String(block.content.mode ?? "select")}
                onChange={(event) => onChange({ ...block, content: { ...block.content, mode: event.target.value } })}
              >
                <option value="select">Dropdown</option>
                <option value="segmented">Segmented control</option>
                <option value="date_range">Date range</option>
              </select>
              <div className="rounded-md border border-neutral-200 bg-white p-3 text-xs text-neutral-600">
                <p className="font-semibold text-neutral-800">
                  {selectedFieldOption ? `${selectedFieldOption.widgetIds.length} compatible widget${selectedFieldOption.widgetIds.length === 1 ? "" : "s"}` : "No field selected"}
                </p>
                {applicableWidgetTitles.length ? (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {applicableWidgetTitles.map((title) => (
                      <span key={title} className="rounded-full bg-brand-50 px-2 py-1 font-medium text-brand-800">
                        {title}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="mt-2">Pick a field sourced from the current widgets and worksheets.</p>
                )}
              </div>
            </div>
          ) : null}

          {block.block_type === "ai_insight" ? (
            <textarea
              className="min-h-32 w-full rounded-md border border-neutral-200 bg-neutral-50 px-3 py-3 text-sm"
              value={String(block.content.prompt ?? "")}
              onChange={(event) => onChange({ ...block, content: { ...block.content, prompt: event.target.value } })}
              placeholder="Describe the insight the dashboard should surface here."
            />
          ) : null}
        </div>

        <div style={{ minHeight: block.position.h }}>
          {block.block_type === "widget" ? (
            <div className="space-y-3">
              <WidgetPreviewSurface preview={widgetPreview} />
              <div className="rounded-md border border-neutral-200 bg-neutral-50 px-3 py-2 text-xs text-neutral-600">
                <span className="font-semibold text-neutral-800">Compatible filters:</span>{" "}
                {widgetAffectedByFilters.length ? widgetAffectedByFilters.map((field) => field.replaceAll("_", " ")).join(", ") : "none yet"}
              </div>
            </div>
          ) : null}
          {block.block_type === "text" ? (
            <div className="flex h-full min-h-[180px] items-center rounded-lg border border-neutral-200 bg-neutral-50 p-5 text-sm text-neutral-700">
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-brand-700"><MessageSquareText size={16} /><span className="font-semibold">Narrative block</span></div>
                <p>{String(block.content.body || "Add context, caveats, or executive commentary for the dashboard audience.")}</p>
              </div>
            </div>
          ) : null}
          {block.block_type === "filter" ? (
            <div className="flex h-full min-h-[180px] items-center rounded-lg border border-dashed border-neutral-300 bg-white p-5">
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-brand-700"><Filter size={16} /><span className="font-semibold">{String(block.content.label || "Global filter")}</span></div>
                <p className="text-sm text-neutral-600">Field: {String(block.content.field || "not selected")}</p>
                <p className="text-sm text-neutral-500">Mode: {String(block.content.mode || "select")}</p>
                <p className="text-sm text-neutral-500">
                  Applies to {applicableWidgetTitles.length} widget{applicableWidgetTitles.length === 1 ? "" : "s"}.
                </p>
              </div>
            </div>
          ) : null}
          {block.block_type === "ai_insight" ? (
            <div className="flex h-full min-h-[180px] items-center rounded-lg border border-neutral-200 bg-brand-50 p-5">
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-brand-800"><Sparkles size={16} /><span className="font-semibold">AI insight block</span></div>
                <p className="text-sm text-brand-900">{String(block.content.prompt || "Add a saved AI insight prompt for this part of the dashboard.")}</p>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export function DashboardCanvasBuilder({
  initialWidgetId = "",
  initialCanvasId = "",
  initialModuleSource = "",
}: {
  initialWidgetId?: string;
  initialCanvasId?: string;
  initialModuleSource?: string;
}) {
  const [selectedCanvasId, setSelectedCanvasId] = useState(initialCanvasId);
  const [canvasName, setCanvasName] = useState("");
  const [canvasDescription, setCanvasDescription] = useState("");
  const [blocks, setBlocks] = useState<CanvasBlockDraft[]>([]);
  const [deletedBlockIds, setDeletedBlockIds] = useState<string[]>([]);
  const [publishVersionLabel, setPublishVersionLabel] = useState("");
  const [publishVisibility, setPublishVisibility] = useState("organization");
  const [publishRoleAccess, setPublishRoleAccess] = useState("");
  const [publishUserIds, setPublishUserIds] = useState("");
  const [publishAllowExport, setPublishAllowExport] = useState(true);
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiReviewOpen, setAiReviewOpen] = useState(false);
  const [publishedDashboard, setPublishedDashboard] = useState<PublishedDashboard | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const canvasesQuery = useQuery({ queryKey: ["dashboard-canvases"], queryFn: listDashboardCanvases });
  const widgetsQuery = useQuery({ queryKey: ["analytics-widgets"], queryFn: listAnalyticsWidgets });
  const worksheetsQuery = useQuery({ queryKey: ["analytics-worksheets"], queryFn: listAnalyticsWorksheets });
  const blocksQuery = useQuery({
    queryKey: ["dashboard-blocks", selectedCanvasId],
    queryFn: () => listDashboardBlocks(selectedCanvasId),
    enabled: Boolean(selectedCanvasId),
  });
  const publishedDashboardsQuery = useQuery({
    queryKey: ["published-dashboards", selectedCanvasId],
    queryFn: () => listPublishedDashboards(selectedCanvasId),
    enabled: Boolean(selectedCanvasId),
  });
  const widgets = useMemo(() => {
    const rows = widgetsQuery.data ?? [];
    if (!initialModuleSource) {
      return rows;
    }
    const allowedWorksheetIds = new Set(
      (worksheetsQuery.data ?? [])
        .filter((worksheet) => {
          const dataset = worksheet.dataset_code;
          return (initialModuleSource === "reports" && dataset.startsWith("indicator"))
            || dataset === initialModuleSource
            || (initialModuleSource === "facilities" && dataset === "medical_facilities")
            || (initialModuleSource === "inspections" && dataset === "inspections")
            || (initialModuleSource === "employers" && dataset === "employers")
            || (initialModuleSource === "certificates" && dataset === "certificates");
        })
        .map((worksheet) => worksheet.id),
    );
    return rows.filter((widget) => allowedWorksheetIds.has(widget.worksheet));
  }, [initialModuleSource, widgetsQuery.data, worksheetsQuery.data]);
  const worksheets = useMemo(() => worksheetsQuery.data ?? [], [worksheetsQuery.data]);
  const moduleMeta = useMemo(
    () => (initialModuleSource ? getEmbeddedAnalyticsModuleMeta(initialModuleSource) : null),
    [initialModuleSource],
  );

  const selectedCanvas = useMemo(
    () => canvasesQuery.data?.find((item) => item.id === selectedCanvasId) ?? null,
    [canvasesQuery.data, selectedCanvasId],
  );

  useEffect(() => {
    if (selectedCanvas) {
      setCanvasName(selectedCanvas.name);
      setCanvasDescription(selectedCanvas.description);
    }
  }, [selectedCanvas]);

  useEffect(() => {
    if (!selectedCanvasId) {
      setCanvasName("");
      setCanvasDescription("");
      setBlocks([]);
      setDeletedBlockIds([]);
      setPublishedDashboard(null);
    }
  }, [selectedCanvasId]);

  useEffect(() => {
    if (initialCanvasId) {
      setSelectedCanvasId(initialCanvasId);
    }
  }, [initialCanvasId]);

  useEffect(() => {
    if (blocksQuery.data) {
      setBlocks(blocksQuery.data.map(draftFromApiBlock));
      setDeletedBlockIds([]);
    }
  }, [blocksQuery.data]);

  const saveCanvasMutation = useMutation({
    mutationFn: async () => {
      const canvasPayload = {
        name: canvasName.trim() || "Untitled dashboard canvas",
        description: canvasDescription.trim(),
        scope_type: "private",
        layout_config: { columns: 12, responsive: true },
        global_filters: blocks
          .filter((block) => block.block_type === "filter")
          .map((block) => ({
            label: block.content.label ?? block.title,
            field: block.content.field ?? "",
            mode: block.content.mode ?? "select",
          })),
      };

      const canvas = selectedCanvasId
        ? await updateDashboardCanvas(selectedCanvasId, canvasPayload)
        : await createDashboardCanvas(canvasPayload);

      for (const blockId of deletedBlockIds) {
        await deleteDashboardBlock(blockId);
      }

      const persistedBlocks: CanvasBlockDraft[] = [];
      for (const [index, block] of blocks.entries()) {
        const payload = {
          canvas: canvas.id,
          widget: block.widget ?? null,
          block_type: block.block_type,
          title: block.title,
          content: block.content,
          position: block.position,
          visibility_rules: block.visibility_rules,
          sort_order: index,
        };
        if (block.id) {
          const updated = await updateDashboardBlock(block.id, payload);
          persistedBlocks.push(draftFromApiBlock(updated));
        } else {
          const created = await createDashboardBlock(payload);
          persistedBlocks.push(draftFromApiBlock(created));
        }
      }

      return { canvas, blocks: persistedBlocks };
    },
    onSuccess: async ({ canvas, blocks: savedBlocks }) => {
      setSelectedCanvasId(canvas.id);
      setBlocks(savedBlocks);
      setDeletedBlockIds([]);
      setSuccess("Dashboard canvas saved with the current block layout.");
      setError("");
      await canvasesQuery.refetch();
    },
    onError: (mutationError) => {
      setError(getApiErrorMessage(mutationError, "Could not save dashboard canvas."));
    },
  });

  const publishCanvasMutation = useMutation({
    mutationFn: async () => {
      const { canvas } = await saveCanvasMutation.mutateAsync();
      const shareSettings: Record<string, unknown> = {};
      const allowedRoles = publishRoleAccess.split(",").map((value) => value.trim()).filter(Boolean);
      const selectedUserIds = publishUserIds.split(",").map((value) => value.trim()).filter(Boolean);

      if (allowedRoles.length) {
        shareSettings.allowed_roles = allowedRoles;
      }
      if (selectedUserIds.length) {
        shareSettings.user_ids = selectedUserIds;
      }
      shareSettings.allow_export = publishAllowExport;

      return publishDashboardCanvas(canvas.id, {
        version_label: publishVersionLabel.trim() || undefined,
        visibility_scope: publishVisibility,
        share_settings: shareSettings,
      });
    },
    onSuccess: async (published) => {
      setPublishedDashboard(published);
      setSuccess(`Published ${published.version_label || "dashboard snapshot"} and saved a read-only version.`);
      setError("");
      await publishedDashboardsQuery.refetch();
    },
    onError: (mutationError) => {
      setError(getApiErrorMessage(mutationError, "Could not publish this dashboard."));
    },
  });

  const aiSuggestionMutation = useMutation({
    mutationFn: generateDashboardCanvas,
    onSuccess: () => {
      setAiReviewOpen(true);
      setError("");
    },
    onError: (mutationError) => {
      setError(getApiErrorMessage(mutationError, "Could not generate dashboard suggestion."));
    },
  });

  const explainCanvasMutation = useMutation({
    mutationFn: ({ id, prompt }: { id: string; prompt?: string }) => explainDashboardCanvas(id, { prompt }),
    onError: (mutationError) => {
      setError(getApiErrorMessage(mutationError, "Could not explain dashboard canvas."));
    },
  });

  useEffect(() => {
    if (initialWidgetId && widgets.length && !blocks.length) {
      const widget = widgets.find((item) => item.id === initialWidgetId);
      if (widget) {
        setBlocks([
          {
            clientId: nextClientId(),
            widget: widget.id,
            block_type: "widget",
            title: widget.title,
            content: {},
            position: { w: 6, h: 320 },
            visibility_rules: {},
            sort_order: 0,
          },
        ]);
      }
    }
  }, [blocks.length, initialWidgetId, widgets]);
  const filterFieldOptions = useMemo(() => {
    const widgetIdsOnCanvas = new Set(blocks.filter((block) => block.block_type === "widget" && block.widget).map((block) => block.widget as string));
    const canvasWidgets = widgets.filter((widget) => widgetIdsOnCanvas.has(widget.id));
    return buildFilterFieldOptions(canvasWidgets, worksheets);
  }, [blocks, widgets, worksheets]);
  const widgetCompatibilityByField = useMemo(
    () =>
      Object.fromEntries(
        filterFieldOptions.map((option) => [option.field, applicableWidgetIdsForFilter(option.field, filterFieldOptions)]),
      ),
    [filterFieldOptions],
  );

  const addBlock = useCallback((blockType: CanvasBlockDraft["block_type"], preferredWidgetId?: string | null) => {
    const defaultWidget = blockType === "widget" ? (preferredWidgetId ?? widgets[0]?.id ?? null) : null;
    setBlocks((current) => [
      ...current,
      {
        clientId: nextClientId(),
        widget: defaultWidget,
        block_type: blockType,
        title:
          blockType === "widget"
            ? widgets.find((item) => item.id === defaultWidget)?.title ?? "Widget block"
            : blockType === "text"
              ? "Narrative"
              : blockType === "filter"
                ? "Global Filter"
                : "AI Insight",
        content:
          blockType === "text"
            ? { body: "" }
            : blockType === "filter"
              ? { label: "Filter", field: "", mode: "select" }
              : blockType === "ai_insight"
                ? { prompt: "" }
                : {},
        position: { w: blockType === "widget" ? 6 : 12, h: blockType === "widget" ? 320 : 220 },
        visibility_rules: {},
        sort_order: current.length,
      },
    ]);
  }, [widgets]);

  function applyAiDashboardSuggestion() {
    const suggestion = aiSuggestionMutation.data;
    if (!suggestion) return;
    setCanvasName(suggestion.name);
    setCanvasDescription(suggestion.description);
    setBlocks(
      suggestion.blocks.map((block, index) => ({
        clientId: nextClientId(),
        widget: block.widget ?? null,
        block_type: block.block_type as CanvasBlockDraft["block_type"],
        title: block.title,
        content: block.content,
        position: {
          w: Number((block.position.w as number | undefined) ?? 12),
          h: Number((block.position.h as number | undefined) ?? 220),
        },
        visibility_rules: block.visibility_rules,
        sort_order: index,
      })),
    );
    setDeletedBlockIds([]);
    setAiReviewOpen(false);
    setSuccess("AI dashboard layout applied. Review the composition, then save or publish when ready.");
  }

  return (
    <div className="grid gap-5">
      {error ? <div className="rounded-lg border border-danger-200 bg-danger-50 px-4 py-3 text-sm font-medium text-danger-700">{error}</div> : null}
      {success ? <div className="rounded-lg border border-brand-200 bg-brand-50 px-4 py-3 text-sm font-medium text-brand-800">{success}</div> : null}
      {moduleMeta ? (
        <div className="rounded-lg border border-brand-200 bg-brand-50 px-4 py-3 text-sm text-brand-900">
          Canvas composition is scoped to <span className="font-semibold">{moduleMeta.label}</span> widgets so module dashboards keep reusing the same analytics engine.
        </div>
      ) : null}

      <div className="grid gap-5 xl:grid-cols-[300px_minmax(0,1fr)]">
        <section className="space-y-5 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm xl:sticky xl:top-24 xl:self-start">
          <div>
            <div className="flex items-center gap-2">
              <LayoutDashboard className="text-brand-700" size={18} />
              <h2 className="text-sm font-bold text-neutral-900">Canvas setup</h2>
            </div>
            <p className="mt-1 text-sm text-neutral-500">Compose widgets and utility blocks into a responsive dashboard canvas.</p>
          </div>

          <div className="space-y-3">
            <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">Saved canvas</label>
            <select className="h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={selectedCanvasId} onChange={(event) => setSelectedCanvasId(event.target.value)}>
              <option value="">New canvas</option>
              {(canvasesQuery.data ?? []).map((canvas) => (
                <option key={canvas.id} value={canvas.id}>
                  {canvas.name}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-3">
            <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">Canvas title</label>
            <input className="h-11 w-full rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm" value={canvasName} onChange={(event) => setCanvasName(event.target.value)} placeholder="e.g. National compliance command center" />
            <textarea className="min-h-24 w-full rounded-md border border-neutral-200 bg-neutral-50 px-3 py-3 text-sm" value={canvasDescription} onChange={(event) => setCanvasDescription(event.target.value)} placeholder="Describe the purpose and audience for this dashboard canvas." />
          </div>

          <div className="space-y-3">
            <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">Add block</label>
            <div className="grid gap-2">
              <button type="button" onClick={() => addBlock("widget")} className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 px-3 text-sm font-semibold text-neutral-700"><Plus size={14} /> Widget block</button>
              <button type="button" onClick={() => addBlock("text")} className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 px-3 text-sm font-semibold text-neutral-700"><Plus size={14} /> Text block</button>
              <button type="button" onClick={() => addBlock("filter")} className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 px-3 text-sm font-semibold text-neutral-700"><Plus size={14} /> Filter block</button>
              <button type="button" onClick={() => addBlock("ai_insight")} className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 px-3 text-sm font-semibold text-neutral-700"><Plus size={14} /> AI insight block</button>
            </div>
          </div>

          <button
            type="button"
            onClick={() => saveCanvasMutation.mutate()}
            className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-brand-700 px-4 text-sm font-semibold text-white"
          >
            {saveCanvasMutation.isPending ? <Loader2 className="animate-spin" size={16} /> : <Save size={16} />}
            Save Canvas
          </button>

          <div className="space-y-3 rounded-lg border border-neutral-200 bg-neutral-50 p-3">
            <div>
              <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Publish snapshot</p>
              <p className="mt-1 text-xs text-neutral-500">Create a read-only dashboard version with governed visibility and sharing.</p>
            </div>
            <input
              className="h-10 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm"
              value={publishVersionLabel}
              onChange={(event) => setPublishVersionLabel(event.target.value)}
              placeholder="Version label"
            />
            <select
              className="h-10 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm"
              value={publishVisibility}
              onChange={(event) => setPublishVisibility(event.target.value)}
            >
              <option value="organization">Organization</option>
              <option value="role_based">Role based</option>
              <option value="selected_users">Selected users</option>
              <option value="federal_only">Federal only</option>
              <option value="state_only">State only</option>
              <option value="public">Public</option>
              <option value="private">Private</option>
            </select>
            <input
              className="h-10 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm"
              value={publishRoleAccess}
              onChange={(event) => setPublishRoleAccess(event.target.value)}
              placeholder="Optional roles, comma-separated"
            />
            <input
              className="h-10 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm"
              value={publishUserIds}
              onChange={(event) => setPublishUserIds(event.target.value)}
              placeholder="Optional user IDs, comma-separated"
            />
            <label className="flex items-center gap-3 rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-700">
              <input
                type="checkbox"
                checked={publishAllowExport}
                onChange={(event) => setPublishAllowExport(event.target.checked)}
                className="h-4 w-4 rounded border-neutral-300"
              />
              Allow exports in the published view
            </label>
            <button
              type="button"
              onClick={() => publishCanvasMutation.mutate()}
              className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-md border border-brand-200 bg-white px-4 text-sm font-semibold text-brand-800"
            >
              {publishCanvasMutation.isPending ? <Loader2 className="animate-spin" size={16} /> : <Rocket size={16} />}
              Publish Dashboard
            </button>
            {publishedDashboard ? (
              <Link
                href={`/federal/reports/published/${publishedDashboard.id}`}
                className="inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-brand-700 px-4 text-sm font-semibold text-white"
              >
                Open Published View
                <ArrowRight size={15} />
              </Link>
            ) : null}
          </div>

          <div className="space-y-3 rounded-lg border border-neutral-200 bg-neutral-50 p-3">
            <div className="flex items-center gap-2">
              <BrainCircuit className="text-brand-700" size={16} />
              <p className="text-sm font-semibold text-neutral-900">AI assistant</p>
            </div>
            <textarea
              className="min-h-24 w-full rounded-md border border-neutral-200 bg-white px-3 py-3 text-sm"
              value={aiPrompt}
              onChange={(event) => setAiPrompt(event.target.value)}
              placeholder="Describe the dashboard you want, for example: create an executive compliance overview with summary, filters, and insights."
            />
            <div className="grid gap-2">
              <button
                type="button"
                disabled={!aiPrompt.trim() || aiSuggestionMutation.isPending}
                onClick={() =>
                  aiSuggestionMutation.mutate({
                    prompt: aiPrompt.trim(),
                    widget_ids: blocks.filter((block) => block.block_type === "widget" && block.widget).map((block) => block.widget as string),
                  })
                }
                className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-brand-200 bg-brand-50 px-4 text-sm font-semibold text-brand-700 disabled:opacity-50"
              >
                <BrainCircuit size={16} />
                {aiSuggestionMutation.isPending ? "Generating..." : "Generate Layout Draft"}
              </button>
              <button
                type="button"
                disabled={!selectedCanvasId || explainCanvasMutation.isPending}
                onClick={() => explainCanvasMutation.mutate({ id: selectedCanvasId, prompt: aiPrompt.trim() || "Explain this dashboard" })}
                className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700 disabled:opacity-50"
              >
                {explainCanvasMutation.isPending ? "Explaining..." : "Explain Current Canvas"}
              </button>
            </div>
            {aiReviewOpen && aiSuggestionMutation.data ? (
              <div className="rounded-md border border-brand-200 bg-white p-3">
                <p className="text-sm font-semibold text-neutral-900">{aiSuggestionMutation.data.name}</p>
                <p className="mt-1 text-sm text-neutral-600">{aiSuggestionMutation.data.description}</p>
                <div className="mt-3 space-y-1">
                  {aiSuggestionMutation.data.reasoning.map((line) => (
                    <p key={line} className="text-xs text-neutral-600">{line}</p>
                  ))}
                </div>
                <button
                  type="button"
                  onClick={applyAiDashboardSuggestion}
                  className="mt-3 inline-flex h-9 items-center justify-center rounded-md bg-brand-700 px-3 text-sm font-semibold text-white"
                >
                  Apply Draft
                </button>
              </div>
            ) : null}
            {explainCanvasMutation.data ? (
              <div className="rounded-md border border-neutral-200 bg-white p-3">
                <p className="text-sm font-semibold text-neutral-900">{explainCanvasMutation.data.summary}</p>
                <div className="mt-2 space-y-1">
                  {explainCanvasMutation.data.insights.map((line) => (
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
                <h2 className="text-sm font-bold text-neutral-900">Canvas layout</h2>
                <p className="mt-1 text-sm text-neutral-500">Arrange blocks in a 12-column responsive grid and tune each block’s footprint.</p>
              </div>
              <div className="flex items-center gap-2 text-xs text-neutral-500">
                <span className="rounded bg-neutral-100 px-2 py-1 font-semibold">{blocks.length} blocks</span>
              </div>
            </div>

            <div className="mt-4 grid gap-4 md:grid-cols-12">
              {blocks.length ? blocks.map((block, index) => (
                <CanvasBlockCard
                  key={block.clientId}
                  block={block}
                  widgets={widgets}
                  worksheets={worksheets}
                  filterFieldOptions={filterFieldOptions}
                  widgetCompatibilityByField={widgetCompatibilityByField}
                  onChange={(next) => setBlocks((current) => current.map((item) => item.clientId === block.clientId ? { ...next, sort_order: index } : item))}
                  onRemove={() => {
                    setBlocks((current) => current.filter((item) => item.clientId !== block.clientId));
                    if (block.id) {
                      setDeletedBlockIds((current) => [...current, block.id!]);
                    }
                  }}
                  onMoveUp={() => setBlocks((current) => {
                    if (index === 0) return current;
                    const next = [...current];
                    [next[index - 1], next[index]] = [next[index], next[index - 1]];
                    return next.map((item, itemIndex) => ({ ...item, sort_order: itemIndex }));
                  })}
                  onMoveDown={() => setBlocks((current) => {
                    if (index === current.length - 1) return current;
                    const next = [...current];
                    [next[index + 1], next[index]] = [next[index], next[index + 1]];
                    return next.map((item, itemIndex) => ({ ...item, sort_order: itemIndex }));
                  })}
                />
              )) : (
                <div className="col-span-12 rounded-lg border border-dashed border-neutral-300 bg-neutral-50 p-10 text-center text-sm text-neutral-500">
                  Add a widget, text block, filter block, or AI insight block to start composing the dashboard.
                </div>
              )}
            </div>
          </section>

          <section className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]">
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <h2 className="text-sm font-bold text-neutral-900">Saved widgets available</h2>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                {widgets.slice(0, 8).map((widget) => (
                  <button
                    key={widget.id}
                    type="button"
                    onClick={() => addBlock("widget", widget.id)}
                    className="rounded-md border border-neutral-200 p-3 text-left hover:border-brand-300 hover:bg-brand-50/50"
                  >
                    <p className="text-sm font-semibold text-neutral-900">{widget.title}</p>
                    <p className="mt-1 text-xs uppercase tracking-wide text-neutral-500">{widget.widget_type.replaceAll("_", " ")}</p>
                    <p className="mt-2 text-xs text-neutral-500">{widget.worksheet_name}</p>
                  </button>
                ))}
                {!widgets.length ? <p className="text-sm text-neutral-500">No widgets saved yet. Build widgets first, then return here.</p> : null}
              </div>
            </div>

            <section className="rounded-lg border border-brand-200 bg-brand-50 p-5 shadow-sm">
              <div className="flex items-center gap-2">
                <LayoutDashboard className="text-brand-700" size={18} />
                <h2 className="text-sm font-bold text-brand-900">Published versions</h2>
              </div>
              <p className="mt-2 text-sm text-brand-900">Every publish action preserves a snapshot so the shared dashboard stays stable even if the draft canvas changes later.</p>
              <div className="mt-4 space-y-2">
                {(publishedDashboardsQuery.data ?? []).slice(0, 5).map((item) => (
                  <Link
                    key={item.id}
                    href={`/federal/reports/published/${item.id}`}
                    className="flex items-center justify-between rounded-md border border-brand-200 bg-white px-3 py-2 text-sm text-neutral-800"
                  >
                    <span className="font-medium">{item.version_label || "Published version"}</span>
                    <ArrowRight size={15} className="text-neutral-400" />
                  </Link>
                ))}
                {!publishedDashboardsQuery.isLoading && !(publishedDashboardsQuery.data ?? []).length ? (
                  <p className="text-sm text-brand-900">No published versions yet for this canvas.</p>
                ) : null}
              </div>
              <div className="mt-4">
                <Link href="/federal/reports" className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-700 px-4 text-sm font-semibold text-white">
                  Back to reports workspace
                  <ArrowRight size={16} />
                </Link>
              </div>
            </section>
          </section>
        </div>
      </div>
    </div>
  );
}
