"use client";

import Link from "next/link";
import { ArrowRight, LayoutDashboard, Sparkles } from "lucide-react";

const MODULE_META: Record<string, { label: string; description: string }> = {
  certificates: {
    label: "Certificates",
    description: "Use the shared analytics engine to turn certificate oversight data into reusable worksheets, widgets, and published dashboards.",
  },
  employers: {
    label: "Employers",
    description: "Reuse employer compliance data inside the same worksheet, widget, and dashboard flow used across Federal reporting.",
  },
  facilities: {
    label: "Medical Facilities",
    description: "Build widgets from facility operations and accreditation data without leaving the shared dashboard engine.",
  },
  inspections: {
    label: "Inspections",
    description: "Carry inspection and enforcement activity into the reusable dashboard builder instead of maintaining a separate analytics surface.",
  },
  reports: {
    label: "Reporting & M&E",
    description: "Build reporting templates and monitoring views with the same worksheet and dashboard engine used everywhere else.",
  },
};

export function getEmbeddedAnalyticsModuleMeta(moduleSource: string) {
  return MODULE_META[moduleSource] ?? {
    label: moduleSource.replaceAll("_", " "),
    description: "This workspace uses the shared analytics, widget, and dashboard engine.",
  };
}

export function EmbeddedAnalyticsActions({
  moduleSource,
  addToDashboardHref,
  openInDashboardBuilderHref,
}: {
  moduleSource: string;
  addToDashboardHref?: string;
  openInDashboardBuilderHref?: string;
}) {
  const meta = getEmbeddedAnalyticsModuleMeta(moduleSource);

  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="min-w-0">
          <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Embedded analytics</p>
          <h2 className="mt-2 text-base font-bold text-neutral-950">{meta.label} uses the shared dashboard engine</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-neutral-600">{meta.description}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {addToDashboardHref ? (
            <Link
              href={addToDashboardHref}
              className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700"
            >
              <Sparkles size={16} />
              Add to Dashboard
            </Link>
          ) : null}
          {openInDashboardBuilderHref ? (
            <Link
              href={openInDashboardBuilderHref}
              className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-700 px-4 text-sm font-semibold text-white"
            >
              <LayoutDashboard size={16} />
              Open in Dashboard Builder
              <ArrowRight size={16} />
            </Link>
          ) : null}
        </div>
      </div>
    </section>
  );
}
