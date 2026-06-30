"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { PortalShell } from "@/components/layout/portal-shell";
import { AnalyticsWorksheetBuilder } from "@/features/reports/analytics-worksheet-builder";

function StateDashboardWorksheetBuilderContent() {
  const searchParams = useSearchParams();
  const moduleSource = searchParams.get("module") ?? "";
  const datasetId = searchParams.get("dataset") ?? "";
  const prompt = searchParams.get("prompt") ?? "";
  const autoGenerateFromPrompt = searchParams.get("generate") === "1";

  return (
    <PortalShell
      role="state_admin"
      title="Worksheet Builder"
      description="Create reusable analytics worksheets from approved datasets, preview the result set, and save logic for downstream widgets and dashboards."
    >
      <AnalyticsWorksheetBuilder
        initialModuleSource={moduleSource}
        initialDatasetId={datasetId}
        initialPrompt={prompt}
        autoGenerateFromPrompt={autoGenerateFromPrompt}
        dashboardBuilderHref="/state/dashboard/dashboard-builder"
      />
    </PortalShell>
  );
}

export default function StateDashboardWorksheetBuilderPage() {
  return (
    <Suspense fallback={null}>
      <StateDashboardWorksheetBuilderContent />
    </Suspense>
  );
}
