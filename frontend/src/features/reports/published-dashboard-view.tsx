"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Copy, Download, ExternalLink, FileSpreadsheet, Filter, ImageDown, Loader2, MessageSquareText, Sparkles } from "lucide-react";

import { WidgetPreviewSurface } from "@/features/reports/analytics-widget-preview";
import {
  applyFiltersToPreview,
  filterOptionsFromPublishedBlocks,
  type FilterStateValue,
} from "@/features/reports/dashboard-filtering";
import {
  exportPublishedDashboard,
  getPublishedDashboard,
  recordPublishedDashboardShareEvent,
  type AnalyticsWidgetPreviewResponse,
  type PublishedDashboardSnapshotBlock,
} from "@/lib/api/analytics";
import { getApiErrorMessage } from "@/lib/api/client";
import { downloadExcelCompatibleFile, downloadJson, exportElementToPng, printElementToPdf } from "@/lib/export/browser";
import { downloadCsv } from "@/lib/export/csv";
import { ROLE_LABELS } from "@/lib/permissions/roles";

function normalizeFilename(name: string, fallback: string) {
  const cleaned = name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  return cleaned || fallback;
}

function FilterBlock({
  block,
  options,
  value,
  onChange,
}: {
  block: PublishedDashboardSnapshotBlock;
  options: string[];
  value: FilterStateValue | undefined;
  onChange: (next: FilterStateValue) => void;
}) {
  const label = String(block.content.label ?? block.title ?? "Filter");
  const field = String(block.content.field ?? "");
  const mode = String(block.content.mode ?? "select");
  const width = Number((block.position as { w?: number } | undefined)?.w ?? 12);

  return (
    <div
      className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"
      style={{ gridColumn: `span ${width} / span ${width}` }}
    >
      <div className="flex items-center gap-2 text-sm font-semibold text-neutral-900">
        <Filter className="text-brand-700" size={16} />
        {label}
      </div>
      <p className="mt-1 text-xs text-neutral-500">{field || "No field configured yet"}</p>

      {mode === "date_range" ? (
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <input
            type="date"
            className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm"
            value={typeof value === "string" ? "" : value?.from ?? ""}
            onChange={(event) => onChange({ ...(typeof value === "string" ? {} : value), from: event.target.value })}
          />
          <input
            type="date"
            className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm"
            value={typeof value === "string" ? "" : value?.to ?? ""}
            onChange={(event) => onChange({ ...(typeof value === "string" ? {} : value), to: event.target.value })}
          />
        </div>
      ) : mode === "segmented" && options.length ? (
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => onChange("")}
            className={`rounded-md px-3 py-2 text-sm font-medium ${value === "" || value == null ? "bg-brand-700 text-white" : "border border-neutral-200 bg-white text-neutral-700"}`}
          >
            All
          </button>
          {options.map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => onChange(option)}
              className={`rounded-md px-3 py-2 text-sm font-medium ${value === option ? "bg-brand-700 text-white" : "border border-neutral-200 bg-white text-neutral-700"}`}
            >
              {option}
            </button>
          ))}
        </div>
      ) : (
        <select
          className="mt-4 h-10 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm"
          value={typeof value === "string" ? value : ""}
          onChange={(event) => onChange(event.target.value)}
        >
          <option value="">All values</option>
          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      )}
    </div>
  );
}

function ReadOnlyBlock({
  block,
  preview,
  onExportCsv,
  onExportXlsx,
  onExportPng,
  exportPending,
  registerRef,
}: {
  block: PublishedDashboardSnapshotBlock;
  preview: AnalyticsWidgetPreviewResponse["preview"] | null;
  onExportCsv: () => void;
  onExportXlsx: () => void;
  onExportPng: () => void;
  exportPending: boolean;
  registerRef: (element: HTMLDivElement | null) => void;
}) {
  const width = Number((block.position as { w?: number } | undefined)?.w ?? (block.block_type === "widget" ? 6 : 12));
  const canExportTable = block.block_type === "widget" && Array.isArray(preview?.rows) && preview.rows.length > 0;
  const canExportPng = block.block_type === "widget";

  return (
    <div
      ref={registerRef}
      className="rounded-lg border border-neutral-200 bg-white shadow-sm"
      style={{ gridColumn: `span ${width} / span ${width}` }}
      data-dashboard-block-id={block.id}
    >
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-200 px-4 py-3">
        <p className="text-sm font-bold text-neutral-900">{block.title || block.widget_title || "Untitled block"}</p>
        {block.block_type === "widget" ? (
          <div className="flex flex-wrap gap-2">
            {canExportTable ? (
              <>
                <button
                  type="button"
                  onClick={onExportCsv}
                  disabled={exportPending}
                  className="inline-flex h-8 items-center gap-2 rounded-md border border-neutral-200 bg-white px-3 text-xs font-semibold text-neutral-700 disabled:opacity-60"
                >
                  <Download size={13} />
                  CSV
                </button>
                <button
                  type="button"
                  onClick={onExportXlsx}
                  disabled={exportPending}
                  className="inline-flex h-8 items-center gap-2 rounded-md border border-neutral-200 bg-white px-3 text-xs font-semibold text-neutral-700 disabled:opacity-60"
                >
                  <FileSpreadsheet size={13} />
                  Excel
                </button>
              </>
            ) : null}
            {canExportPng ? (
              <button
                type="button"
                onClick={onExportPng}
                disabled={exportPending}
                className="inline-flex h-8 items-center gap-2 rounded-md border border-neutral-200 bg-white px-3 text-xs font-semibold text-neutral-700 disabled:opacity-60"
              >
                <ImageDown size={13} />
                PNG
              </button>
            ) : null}
          </div>
        ) : null}
      </div>
      <div className="p-4">
        {block.block_type === "widget" ? <WidgetPreviewSurface preview={preview} /> : null}
        {block.block_type === "text" ? (
          <div className="rounded-lg border border-neutral-200 bg-neutral-50 p-5 text-sm text-neutral-700">
            <div className="mb-3 flex items-center gap-2 text-brand-700">
              <MessageSquareText size={16} />
              <span className="font-semibold">Narrative</span>
            </div>
            <p>{String(block.content.body || "No narrative provided.")}</p>
          </div>
        ) : null}
        {block.block_type === "ai_insight" ? (
          <div className="rounded-lg border border-brand-100 bg-brand-50 p-5 text-sm text-brand-900">
            <div className="mb-3 flex items-center gap-2">
              <Sparkles size={16} />
              <span className="font-semibold">Saved AI insight prompt</span>
            </div>
            <p>{String(block.content.prompt || "No saved prompt for this insight block.")}</p>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export function PublishedDashboardView({ dashboardId }: { dashboardId: string }) {
  const [filters, setFilters] = useState<Record<string, FilterStateValue>>({});
  const [copied, setCopied] = useState(false);
  const [actionError, setActionError] = useState("");
  const [actionSuccess, setActionSuccess] = useState("");
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const blockRefs = useRef<Record<string, HTMLDivElement | null>>({});
  const printRef = useRef<HTMLDivElement | null>(null);

  const dashboardQuery = useQuery({
    queryKey: ["published-dashboard", dashboardId],
    queryFn: () => getPublishedDashboard(dashboardId),
  });

  const exportMutation = useMutation({
    mutationFn: exportPublishedDashboard,
    onError: (error) => {
      setActionError(getApiErrorMessage(error, "Could not export this dashboard."));
    },
  });

  const shareMutation = useMutation({
    mutationFn: recordPublishedDashboardShareEvent,
    onError: () => {
      setActionError("The link was copied, but the share activity could not be logged.");
    },
  });

  const dashboard = dashboardQuery.data;

  const filterOptions = useMemo(() => (dashboard ? filterOptionsFromPublishedBlocks(dashboard.snapshot.blocks) : {}), [dashboard]);

  useEffect(() => {
    if (!dashboard) return;
    const nextFilters: Record<string, FilterStateValue> = {};
    for (const block of dashboard.snapshot.blocks.filter((item) => item.block_type === "filter")) {
      const field = String(block.content.field ?? "");
      if (!field) continue;
      const scalarValue = searchParams.get(`f_${field}`);
      const from = searchParams.get(`f_${field}_from`);
      const to = searchParams.get(`f_${field}_to`);
      if (scalarValue) {
        nextFilters[field] = scalarValue;
      } else if (from || to) {
        nextFilters[field] = { from: from ?? "", to: to ?? "" };
      }
    }
    setFilters(nextFilters);
  }, [dashboard, searchParams]);

  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString());
    Array.from(params.keys())
      .filter((key) => key.startsWith("f_"))
      .forEach((key) => params.delete(key));
    Object.entries(filters).forEach(([field, value]) => {
      if (value == null || value === "") return;
      if (typeof value === "string") {
        params.set(`f_${field}`, value);
      } else {
        if (value.from) params.set(`f_${field}_from`, value.from);
        if (value.to) params.set(`f_${field}_to`, value.to);
      }
    });
    const nextUrl = params.toString() ? `${pathname}?${params.toString()}` : pathname;
    router.replace(nextUrl, { scroll: false });
  }, [filters, pathname, router, searchParams]);

  async function handleCopyLink() {
    await navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    shareMutation.mutate({ dashboardId, event: "link_copied" });
    window.setTimeout(() => setCopied(false), 1500);
  }

  async function handleDashboardPdfExport() {
    setActionError("");
    const response = await exportMutation.mutateAsync({ dashboardId, format: "pdf" });
    if (!printRef.current) return;
    printElementToPdf(response.title || "Published dashboard", printRef.current);
  }

  async function handleDashboardJsonExport() {
    setActionError("");
    const response = await exportMutation.mutateAsync({ dashboardId, format: "json" });
    if (response.background) {
      setActionSuccess(`Large export queued in the background. Job ${response.job_id} is processing.`);
      return;
    }
    downloadJson(
      response.filename || `${normalizeFilename(response.title ?? "published-dashboard", "published-dashboard")}.json`,
      response.payload ?? {},
    );
  }

  async function handleBlockCsvExport(blockId: string) {
    setActionError("");
    const response = await exportMutation.mutateAsync({ dashboardId, format: "csv", block_id: blockId });
    if (response.background) {
      setActionSuccess(`Large export queued in the background. Job ${response.job_id} is processing.`);
      return;
    }
    const rows = Array.isArray(response.payload?.rows) ? (response.payload.rows as Array<Record<string, unknown>>) : [];
    const columns = Array.from(new Set(rows.flatMap((row) => Object.keys(row))));
    downloadCsv(
      response.filename || `${normalizeFilename(response.title ?? "widget", "widget")}.csv`,
      rows,
      columns.map((column) => ({
        header: column,
        value: (row: Record<string, unknown>) => row[column] as string | number | boolean | null | undefined,
      })),
    );
  }

  async function handleBlockXlsxExport(blockId: string) {
    setActionError("");
    const response = await exportMutation.mutateAsync({ dashboardId, format: "xlsx", block_id: blockId });
    if (response.background) {
      setActionSuccess(`Large export queued in the background. Job ${response.job_id} is processing.`);
      return;
    }
    const rows = Array.isArray(response.payload?.rows) ? (response.payload.rows as Array<Record<string, unknown>>) : [];
    downloadExcelCompatibleFile(
      response.filename || `${normalizeFilename(response.title ?? "widget", "widget")}.xlsx`,
      rows,
    );
  }

  async function handleBlockPngExport(blockId: string) {
    setActionError("");
    const response = await exportMutation.mutateAsync({ dashboardId, format: "png", block_id: blockId });
    const element = blockRefs.current[blockId];
    if (!element) {
      setActionError("Could not find the widget on the page for PNG export.");
      return;
    }
    await exportElementToPng(element, response.filename || `${normalizeFilename(response.title ?? "widget", "widget")}.png`);
  }

  if (dashboardQuery.isLoading) {
    return (
      <div className="rounded-lg border border-neutral-200 bg-white p-10 text-center text-sm text-neutral-500">
        <Loader2 className="mx-auto mb-3 animate-spin text-brand-700" size={18} />
        Loading published dashboard...
      </div>
    );
  }

  if (dashboardQuery.isError || !dashboard) {
    return (
      <div className="rounded-lg border border-danger-200 bg-danger-50 px-4 py-3 text-sm font-medium text-danger-700">
        {getApiErrorMessage(dashboardQuery.error, "Could not load this published dashboard.")}
      </div>
    );
  }

  const allowedRoles = (dashboard.share_settings?.allowed_roles ?? null) as string[] | null;
  const sharedRoles = Array.isArray(allowedRoles)
    ? allowedRoles.map((role) => ROLE_LABELS[role as keyof typeof ROLE_LABELS] ?? role)
    : [];
  const exportEnabled = dashboard.share_settings?.allow_export !== false;

  return (
    <div className="grid gap-5">
      {actionError ? <div className="rounded-lg border border-danger-200 bg-danger-50 px-4 py-3 text-sm font-medium text-danger-700">{actionError}</div> : null}
      {actionSuccess ? <div className="rounded-lg border border-brand-200 bg-brand-50 px-4 py-3 text-sm font-medium text-brand-800">{actionSuccess}</div> : null}

      <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Published dashboard</p>
            <h2 className="mt-1 text-xl font-bold text-neutral-950">{dashboard.snapshot.canvas.name}</h2>
            <p className="mt-2 max-w-3xl text-sm text-neutral-600">{dashboard.snapshot.canvas.description || "Read-only published snapshot of the saved dashboard canvas."}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={handleCopyLink}
              className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700"
            >
              <Copy size={15} />
              {copied ? "Link copied" : "Share link"}
            </button>
            <button
              type="button"
              disabled={!exportEnabled || exportMutation.isPending}
              onClick={handleDashboardPdfExport}
              className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-700 px-4 text-sm font-semibold text-white disabled:opacity-60"
            >
              <Download size={15} />
              Export PDF
            </button>
            <button
              type="button"
              disabled={!exportEnabled || exportMutation.isPending}
              onClick={handleDashboardJsonExport}
              className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700 disabled:opacity-60"
            >
              <Download size={15} />
              Export JSON
            </button>
            <Link
              href="/federal/dashboard/canvas-builder"
              className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700"
            >
              <ExternalLink size={15} />
              Open builder
            </Link>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-2 text-xs">
          <span className="rounded-full bg-brand-50 px-3 py-1 font-semibold text-brand-800">{dashboard.version_label || "Published version"}</span>
          <span className="rounded-full bg-neutral-100 px-3 py-1 font-semibold text-neutral-700">{dashboard.visibility_scope.replaceAll("_", " ")}</span>
          <span className={`rounded-full px-3 py-1 font-semibold ${exportEnabled ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"}`}>
            {exportEnabled ? "Export enabled" : "Export restricted"}
          </span>
          {dashboard.published_at ? <span className="rounded-full bg-neutral-100 px-3 py-1 font-semibold text-neutral-700">Published {new Date(dashboard.published_at).toLocaleString()}</span> : null}
          {sharedRoles.map((role) => (
            <span key={role} className="rounded-full bg-emerald-50 px-3 py-1 font-semibold text-emerald-700">
              {role}
            </span>
          ))}
        </div>
      </section>

      <div ref={printRef} className="grid gap-5">
        <section className="grid gap-4 md:grid-cols-12">
          {dashboard.snapshot.blocks.map((block) => {
            if (block.block_type === "filter") {
              const field = String(block.content.field ?? "");
              return (
                <FilterBlock
                  key={block.id}
                  block={block}
                  options={filterOptions[field] ?? []}
                  value={filters[field]}
                  onChange={(next) => setFilters((current) => ({ ...current, [field]: next }))}
                />
              );
            }

            const preview = applyFiltersToPreview(block.preview, filters);
            return (
              <ReadOnlyBlock
                key={block.id}
                block={block}
                preview={preview}
                exportPending={exportMutation.isPending}
                onExportCsv={() => handleBlockCsvExport(block.id)}
                onExportXlsx={() => handleBlockXlsxExport(block.id)}
                onExportPng={() => handleBlockPngExport(block.id)}
                registerRef={(element) => {
                  blockRefs.current[block.id] = element;
                }}
              />
            );
          })}
        </section>
      </div>
    </div>
  );
}
