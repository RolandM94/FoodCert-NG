"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  ArrowRight,
  Database,
  FileSpreadsheet,
  LayoutDashboard,
  LayoutTemplate,
  Loader2,
  Plus,
  Sparkles,
} from "lucide-react";

import type { UserRole } from "@/types/auth";
import {
  type AnalyticsDataset,
  generateFullDashboard,
  listAnalyticsDatasets,
  listAnalyticsWorksheets,
  listDashboardCanvases,
  listDashboardTemplates,
  listPublishedDashboards,
} from "@/lib/api/analytics";
import { getApiErrorMessage } from "@/lib/api/client";

const INDICATOR_DATASET_CODES = new Set([
  "indicators",
  "indicator_targets",
  "indicator_results",
  "indicator_performance",
]);

type AnalyticsWorkspaceHomeProps = {
  role: UserRole;
  title?: string;
  description?: string;
  reportsHref: string;
  templatesHref: string;
  worksheetBuilderHref: string;
  dashboardBuilderHref: string;
  canvasBuilderHref: string;
  publishedBaseHref: string;
  datasetLibraryBaseHref: string;
};

type DatasetRegistryRow = {
  id: string;
  sourceDatasetId: string;
  name: string;
  code: string;
  moduleSource: string;
  fieldCount: number;
  privacyLevel: string;
  description: string;
  consolidatedLabels?: string[];
};

function sectionCount(value: number) {
  return (
    <span className="inline-flex min-w-6 items-center justify-center rounded-full bg-neutral-100 px-2 py-0.5 text-xs font-semibold text-neutral-500">
      {value}
    </span>
  );
}

function datasetLabel(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function WorkspaceCard({
  tone,
  icon: Icon,
  title,
  description,
  meta,
  footer,
  href,
}: {
  tone: "teal" | "violet" | "sky";
  icon: typeof FileSpreadsheet;
  title: string;
  description: string;
  meta?: ReactNode;
  footer?: ReactNode;
  href?: string;
}) {
  const tones = {
    teal: "border-t-teal-400 bg-teal-50/30",
    violet: "border-t-violet-500 bg-violet-50/30",
    sky: "border-t-sky-400 bg-sky-50/30",
  };
  const iconTones = {
    teal: "bg-teal-50 text-teal-600",
    violet: "bg-violet-50 text-violet-600",
    sky: "bg-sky-50 text-sky-600",
  };

  const content = (
    <article className={`grid min-h-[212px] gap-4 rounded-lg border border-neutral-200 border-t-4 p-4 shadow-sm ${tones[tone]}`}>
      <div className={`flex h-9 w-9 items-center justify-center rounded-md ${iconTones[tone]}`}>
        <Icon size={18} />
      </div>
      <div className="min-w-0">
        <h3 className="text-base font-bold text-neutral-950">{title}</h3>
        <p className="mt-2 line-clamp-2 text-sm leading-6 text-neutral-500">{description}</p>
      </div>
      {meta ? <div className="flex flex-wrap gap-2 text-xs">{meta}</div> : <div />}
      {footer ? <div className="mt-auto text-xs text-neutral-400">{footer}</div> : null}
    </article>
  );

  if (!href) {
    return content;
  }

  return (
    <Link className="block" href={href}>
      {content}
    </Link>
  );
}

export function AnalyticsWorkspaceHome({
  role,
  title = "Home",
  description = "Build workbooks, create canvases, and publish dashboards from shared platform datasets.",
  reportsHref,
  templatesHref,
  worksheetBuilderHref,
  dashboardBuilderHref,
  canvasBuilderHref,
  publishedBaseHref,
  datasetLibraryBaseHref,
}: AnalyticsWorkspaceHomeProps) {
  const router = useRouter();
  const [prompt, setPrompt] = useState("");

  const datasetsQuery = useQuery({
    queryKey: ["analytics-datasets"],
    queryFn: listAnalyticsDatasets,
  });
  const worksheetsQuery = useQuery({
    queryKey: ["analytics-worksheets"],
    queryFn: listAnalyticsWorksheets,
  });
  const canvasesQuery = useQuery({
    queryKey: ["dashboard-canvases"],
    queryFn: listDashboardCanvases,
  });
  const publishedQuery = useQuery({
    queryKey: ["published-dashboards"],
    queryFn: () => listPublishedDashboards(),
  });
  const templatesQuery = useQuery({
    queryKey: ["dashboard-templates"],
    queryFn: listDashboardTemplates,
  });

  const datasets = useMemo(() => datasetsQuery.data ?? [], [datasetsQuery.data]);
  const datasetRegistryRows = useMemo<DatasetRegistryRow[]>(() => {
    const indicatorDatasets = datasets.filter((dataset) => INDICATOR_DATASET_CODES.has(dataset.code));
    const nonIndicatorDatasets = datasets.filter((dataset) => !INDICATOR_DATASET_CODES.has(dataset.code));

    const rows: DatasetRegistryRow[] = nonIndicatorDatasets.map((dataset: AnalyticsDataset) => ({
      id: dataset.id,
      sourceDatasetId: dataset.id,
      name: dataset.name,
      code: dataset.code,
      moduleSource: dataset.module_source,
      fieldCount: dataset.available_fields.length,
      privacyLevel: dataset.privacy_level,
      description: dataset.description,
    }));

    if (indicatorDatasets.length) {
      const primaryIndicatorDataset =
        indicatorDatasets.find((dataset) => dataset.code === "indicators") ?? indicatorDatasets[0];

      rows.push({
        id: "indicators-consolidated",
        sourceDatasetId: primaryIndicatorDataset.id,
        name: "Indicators",
        code: primaryIndicatorDataset.code,
        moduleSource: primaryIndicatorDataset.module_source,
        fieldCount: primaryIndicatorDataset.available_fields.length,
        privacyLevel: primaryIndicatorDataset.privacy_level,
        description:
          "Unified indicator registry that consolidates definitions, targets, results, and performance views for all platform indicators.",
        consolidatedLabels: indicatorDatasets
          .map((dataset) => dataset.name)
          .filter((label) => label !== "Indicators"),
      });
    }

    return rows.sort((a, b) => a.name.localeCompare(b.name));
  }, [datasets]);
  const worksheets = useMemo(
    () => [...(worksheetsQuery.data ?? [])].sort((a, b) => b.updated_at.localeCompare(a.updated_at)),
    [worksheetsQuery.data],
  );
  const canvases = useMemo(
    () => [...(canvasesQuery.data ?? [])].sort((a, b) => b.updated_at.localeCompare(a.updated_at)),
    [canvasesQuery.data],
  );
  const published = useMemo(() => publishedQuery.data ?? [], [publishedQuery.data]);
  const templates = templatesQuery.data ?? [];
  const publishedByCanvas = useMemo(
    () => Object.fromEntries(published.map((item) => [item.canvas, item])),
    [published],
  );

  const generateDashboardMutation = useMutation({
    mutationFn: generateFullDashboard,
    onSuccess: (data) => {
      const params = new URLSearchParams();
      params.set("prompt", prompt.trim());
      params.set("generate", "1");
      params.set("autoFill", JSON.stringify(data));
      router.push(`${canvasBuilderHref}?${params.toString()}`);
    },
  });

  const busy = datasetsQuery.isLoading || worksheetsQuery.isLoading || canvasesQuery.isLoading;
  const error =
    (datasetsQuery.isError && getApiErrorMessage(datasetsQuery.error, "Could not load analytics datasets."))
    || (worksheetsQuery.isError && getApiErrorMessage(worksheetsQuery.error, "Could not load workbooks."))
    || (canvasesQuery.isError && getApiErrorMessage(canvasesQuery.error, "Could not load canvases."))
    || (publishedQuery.isError && getApiErrorMessage(publishedQuery.error, "Could not load published dashboards."))
    || (templatesQuery.isError && getApiErrorMessage(templatesQuery.error, "Could not load templates."))
    || (generateDashboardMutation.isError && getApiErrorMessage(generateDashboardMutation.error, "AI dashboard generation failed."))
    || "";

  const promptPlaceholder = role === "federal_admin"
    ? "Ask AI, for example: show certificate coverage by state and facility type"
    : role === "state_admin"
      ? "Ask AI, for example: compare LGA certificate validation queues this month"
      : role === "employer"
        ? "Ask AI, for example: track expiring certificates by branch"
        : "Ask AI, for example: monitor lab turnaround and certificate output";

  function openWorkbookBuilder() {
    const params = new URLSearchParams();
    if (prompt.trim()) {
      params.set("prompt", prompt.trim());
      params.set("generate", "1");
    }
    router.push(params.size ? `${worksheetBuilderHref}?${params.toString()}` : worksheetBuilderHref);
  }

  function triggerFullGenerate() {
    if (!prompt.trim()) return;
    generateDashboardMutation.mutate({ prompt: prompt.trim() });
  }

  return (
    <div className="grid gap-8">
      <section className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-neutral-950">{title}</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-neutral-500">{description}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700" href={templatesHref}>
            <LayoutTemplate size={16} />
            Templates
          </Link>
          <Link className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-semibold text-white" href={worksheetBuilderHref}>
            <Plus size={16} />
            New Workbook
          </Link>
          <Link className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700" href={canvasBuilderHref}>
            <Plus size={16} />
            New Canvas
          </Link>
          <Link className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700" href={reportsHref}>
            <FileSpreadsheet size={16} />
            Reports
          </Link>
        </div>
      </section>

      <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
        <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_132px_160px]">
          <div className="flex items-center gap-3 rounded-md border border-neutral-200 bg-neutral-50 px-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-brand-50 text-brand-700">
              <Sparkles size={16} />
            </div>
            <input
              className="h-12 w-full bg-transparent text-sm text-neutral-900 outline-none"
              placeholder={promptPlaceholder}
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && prompt.trim()) {
                  openWorkbookBuilder();
                }
              }}
            />
          </div>
          <button
            type="button"
            onClick={openWorkbookBuilder}
            disabled={!prompt.trim()}
            className="inline-flex h-12 items-center justify-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-neutral-200 disabled:text-neutral-400"
          >
            Build Workbook
            <ArrowRight size={16} />
          </button>
          <button
            type="button"
            onClick={triggerFullGenerate}
            disabled={!prompt.trim() || generateDashboardMutation.isPending}
            className="inline-flex h-12 items-center justify-center gap-2 rounded-md border border-brand-600 bg-white px-4 text-sm font-semibold text-brand-700 disabled:cursor-not-allowed disabled:border-neutral-200 disabled:text-neutral-400"
          >
            {generateDashboardMutation.isPending ? (
              <Loader2 className="animate-spin" size={16} />
            ) : (
              <Sparkles size={16} />
            )}
            Dashboard
          </button>
        </div>
        <p className="mt-3 text-sm text-neutral-400">Describe what you need. AI auto-selects the right dataset from the library.</p>
      </section>

      {busy ? (
        <section className="rounded-lg border border-neutral-200 bg-white p-6 text-sm text-neutral-500 shadow-sm">
          <div className="flex items-center gap-2">
            <Loader2 className="animate-spin text-brand-700" size={16} />
            Loading analytics workspace...
          </div>
        </section>
      ) : null}

      {error ? (
        <section className="rounded-lg border border-danger-200 bg-danger-50 px-4 py-3 text-sm font-medium text-danger-700">
          {error}
        </section>
      ) : null}

      <section className="grid gap-4">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="text-teal-500" size={18} />
            <h3 className="text-2xl font-bold text-neutral-950">Workbooks</h3>
            {sectionCount(worksheets.length)}
          </div>
          <Link className="text-sm font-semibold text-neutral-400 hover:text-brand-700" href={worksheetBuilderHref}>+ New</Link>
        </div>
        <div className="grid gap-4 xl:grid-cols-4 md:grid-cols-2">
          {worksheets.slice(0, 4).map((worksheet) => (
            <WorkspaceCard
              key={worksheet.id}
              tone="teal"
              icon={FileSpreadsheet}
              title={worksheet.name}
              description={worksheet.description || "Reusable analytic workbook ready for widget and dashboard composition."}
              meta={
                <>
                  <span className="rounded-full bg-teal-50 px-2 py-1 font-semibold text-teal-600">{datasetLabel(worksheet.chart_recommendation)}</span>
                  <span className="text-neutral-400">{worksheet.metrics.length} metrics</span>
                  <span className="text-neutral-400">{worksheet.dimensions.length} dimensions</span>
                </>
              }
              footer={`Updated ${new Date(worksheet.updated_at).toLocaleDateString("en-NG", { dateStyle: "medium" })}`}
              href={`${dashboardBuilderHref}?worksheetId=${worksheet.id}`}
            />
          ))}
          {!worksheets.length ? (
            <WorkspaceCard
              tone="teal"
              icon={FileSpreadsheet}
              title="No workbooks yet"
              description="Start with a dataset, define your metrics and dimensions, then save the workbook for widgets and canvases."
              href={worksheetBuilderHref}
            />
          ) : null}
        </div>
      </section>

      <section className="grid gap-4">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <LayoutDashboard className="text-violet-500" size={18} />
            <h3 className="text-2xl font-bold text-neutral-950">Canvases</h3>
            {sectionCount(canvases.length)}
          </div>
          <Link className="text-sm font-semibold text-neutral-400 hover:text-brand-700" href={canvasBuilderHref}>+ New</Link>
        </div>
        <div className="grid gap-4 xl:grid-cols-4 md:grid-cols-2">
          {canvases.slice(0, 4).map((canvas) => {
            const publishedDashboard = publishedByCanvas[canvas.id];
            const canvasHref = publishedDashboard
              ? `${publishedBaseHref}/${publishedDashboard.id}`
              : `${canvasBuilderHref}?canvasId=${canvas.id}`;
            return (
              <WorkspaceCard
                key={canvas.id}
                tone="violet"
                icon={LayoutDashboard}
                title={canvas.name}
                description={canvas.description || "Editable canvas for dashboard composition and publishing."}
                meta={
                  <>
                    <span className="rounded-full bg-neutral-100 px-2 py-1 font-semibold text-neutral-700">
                      {Array.isArray(canvas.global_filters) ? `${canvas.global_filters.length} filters` : "0 filters"}
                    </span>
                    {publishedDashboard ? (
                      <span className="rounded-full bg-brand-50 px-2 py-1 font-semibold text-brand-700">Published</span>
                    ) : null}
                  </>
                }
                footer={
                  publishedDashboard ? (
                    "Published and ready to view"
                  ) : (
                    `Updated ${new Date(canvas.updated_at).toLocaleDateString("en-NG", { dateStyle: "medium" })}`
                  )
                }
                href={canvasHref}
              />
            );
          })}
          {!canvases.length ? (
            <WorkspaceCard
              tone="violet"
              icon={LayoutDashboard}
              title="No canvases yet"
              description="Arrange saved widgets, filters, and narrative blocks into a dashboard canvas."
              href={canvasBuilderHref}
            />
          ) : null}
        </div>
      </section>

      <section className="grid gap-4">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Database className="text-sky-500" size={18} />
            <h3 className="text-2xl font-bold text-neutral-950">My Datasets</h3>
            {sectionCount(datasetRegistryRows.length)}
          </div>
          <span className="text-sm font-semibold text-neutral-400">{templates.length} templates available</span>
        </div>
        <section className="overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-sm">
          <div className="border-b border-neutral-200 px-4 py-3">
            <p className="text-sm font-semibold text-neutral-900">Dataset registry</p>
            <p className="mt-1 text-sm text-neutral-500">Inspect datasets in table form, select one, then move into workbook design and canvas publishing.</p>
          </div>
          {datasetRegistryRows.length ? (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[820px] text-left text-sm">
                <thead className="bg-neutral-50 text-xs font-bold uppercase tracking-wide text-neutral-500">
                  <tr>
                    <th className="px-4 py-3">Dataset</th>
                    <th className="px-4 py-3">Module</th>
                    <th className="px-4 py-3">Fields</th>
                    <th className="px-4 py-3">Privacy</th>
                    <th className="px-4 py-3">Description</th>
                    <th className="px-4 py-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200">
                  {datasetRegistryRows.map((dataset) => {
                    return (
                      <tr
                        key={dataset.id}
                        className="bg-white hover:bg-neutral-50"
                      >
                        <td className="px-4 py-3">
                          <div>
                            <p className="font-semibold text-neutral-900">{dataset.name}</p>
                            <p className="mt-1 text-xs text-neutral-500">
                              {dataset.code}
                              {dataset.consolidatedLabels?.length ? ` | ${dataset.consolidatedLabels.length + 1} linked datasets` : ""}
                            </p>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className="rounded-full bg-sky-50 px-2 py-1 text-xs font-semibold text-sky-700">
                            {datasetLabel(dataset.moduleSource)}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-neutral-600">{dataset.fieldCount}</td>
                        <td className="px-4 py-3 text-neutral-600">{datasetLabel(dataset.privacyLevel)}</td>
                        <td className="max-w-md px-4 py-3 text-neutral-500">{dataset.description}</td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex justify-end gap-2">
                            <Link
                              href={`${datasetLibraryBaseHref}/${dataset.sourceDatasetId}`}
                              className="inline-flex h-9 items-center justify-center rounded-md bg-brand-50 px-3 text-xs font-semibold text-brand-700 hover:bg-brand-100"
                            >
                              Open
                            </Link>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="px-4 py-10 text-sm text-neutral-500">Approved datasets will appear here once this account has analytics access.</div>
          )}
        </section>

      </section>
    </div>
  );
}
