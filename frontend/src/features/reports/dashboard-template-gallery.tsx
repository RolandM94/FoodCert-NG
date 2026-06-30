"use client";

import Link from "next/link";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ArrowRight, LayoutTemplate, Loader2, Sparkles } from "lucide-react";

import { getApiErrorMessage } from "@/lib/api/client";
import { listDashboardTemplates, useDashboardTemplate } from "@/lib/api/analytics";

type DashboardTemplateGalleryProps = {
  initialModuleSource?: string;
  canvasBuilderHref?: string;
};

function formatModuleLabel(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

export function DashboardTemplateGallery({
  initialModuleSource = "",
  canvasBuilderHref = "/federal/dashboard/canvas-builder",
}: DashboardTemplateGalleryProps) {
  const templatesQuery = useQuery({
    queryKey: ["dashboard-templates"],
    queryFn: listDashboardTemplates,
  });

  const useTemplateMutation = useMutation({
    mutationFn: useDashboardTemplate,
  });

  if (templatesQuery.isLoading) {
    return (
      <div className="rounded-lg border border-neutral-200 bg-white p-10 text-center text-sm text-neutral-500">
        <Loader2 className="mx-auto mb-3 animate-spin text-brand-700" size={18} />
        Loading dashboard templates...
      </div>
    );
  }

  if (templatesQuery.isError) {
    return (
      <div className="rounded-lg border border-danger-200 bg-danger-50 px-4 py-3 text-sm font-medium text-danger-700">
        {getApiErrorMessage(templatesQuery.error, "Could not load dashboard templates.")}
      </div>
    );
  }

  const templates = templatesQuery.data ?? [];

  return (
    <div className="grid gap-5">
      <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
        <div className="flex items-center gap-2">
          <LayoutTemplate className="text-brand-700" size={18} />
          <h2 className="text-base font-bold text-neutral-900">Template Gallery</h2>
        </div>
        <p className="mt-2 text-sm text-neutral-500">
          Start from a prebuilt account-aware layout, then customize it in the canvas builder.
          {initialModuleSource ? ` Showing templates for ${formatModuleLabel(initialModuleSource)} workflows.` : ""}
        </p>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        {templates.map((template) => {
          const blockCount = Array.isArray(template.template_config?.blocks) ? template.template_config.blocks.length : 0;
          const globalFilters = Array.isArray(template.template_config?.global_filters) ? template.template_config.global_filters.length : 0;
          const isPending = useTemplateMutation.isPending && useTemplateMutation.variables === template.id;

          return (
            <div key={template.id} className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-bold text-neutral-900">{template.name}</p>
                  <p className="mt-1 text-sm text-neutral-500">{template.description}</p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${template.is_system_template ? "bg-brand-50 text-brand-800" : "bg-neutral-100 text-neutral-700"}`}>
                  {template.is_system_template ? "System" : "Custom"}
                </span>
              </div>

              <div className="mt-4 flex flex-wrap gap-2 text-xs">
                <span className="rounded-full bg-neutral-100 px-3 py-1 font-semibold text-neutral-700">{template.account_type.replaceAll("_", " ")}</span>
                <span className="rounded-full bg-neutral-100 px-3 py-1 font-semibold text-neutral-700">{template.scope_type.replaceAll("_", " ")}</span>
                <span className="rounded-full bg-neutral-100 px-3 py-1 font-semibold text-neutral-700">{blockCount} blocks</span>
                <span className="rounded-full bg-neutral-100 px-3 py-1 font-semibold text-neutral-700">{globalFilters} filters</span>
              </div>

              {Array.isArray(template.template_config?.blocks) && template.template_config.blocks.length ? (
                <div className="mt-4 rounded-md border border-neutral-200 bg-neutral-50 p-3">
                  <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Template includes</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {template.template_config.blocks.slice(0, 5).map((block, index) => (
                      <span key={`${template.id}-${index}`} className="rounded-full bg-white px-2 py-1 text-xs font-medium text-neutral-700">
                        {String((block as Record<string, unknown>).block_type ?? "block").replaceAll("_", " ")}
                      </span>
                    ))}
                  </div>
                </div>
              ) : null}

              <div className="mt-4 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={async () => {
                    const canvas = await useTemplateMutation.mutateAsync(template.id);
                    window.location.assign(`${canvasBuilderHref}?canvasId=${canvas.id}`);
                  }}
                  className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-700 px-4 text-sm font-semibold text-white"
                >
                  {isPending ? <Loader2 className="animate-spin" size={16} /> : <Sparkles size={16} />}
                  Use Template
                </button>
                <Link
                  href={canvasBuilderHref}
                  className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700"
                >
                  Open Blank Builder
                  <ArrowRight size={15} />
                </Link>
              </div>
            </div>
          );
        })}

        {!templates.length ? (
          <div className="rounded-lg border border-dashed border-neutral-300 bg-neutral-50 p-10 text-center text-sm text-neutral-500">
            No templates available for this account type yet.
          </div>
        ) : null}
      </section>
    </div>
  );
}
