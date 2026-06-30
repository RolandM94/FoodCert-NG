"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";

import { PortalShell } from "@/components/layout/portal-shell";
import { AnalyticsWidgetBuilder } from "@/features/reports/analytics-widget-builder";

function FederalDashboardBuilderContent() {
  const searchParams = useSearchParams();
  const worksheetId = searchParams.get("worksheetId") ?? "";
  const moduleSource = searchParams.get("module") ?? "";

  return (
    <PortalShell
      role="federal_admin"
      title="Widget Builder"
      description="Turn saved worksheets into KPI cards, charts, tables, maps, queue cards, and AI insight widgets for dashboard composition."
    >
      <AnalyticsWidgetBuilder initialWorksheetId={worksheetId} initialModuleSource={moduleSource} />
    </PortalShell>
  );
}

export default function FederalDashboardBuilderPage() {
  return (
    <Suspense fallback={null}>
      <FederalDashboardBuilderContent />
    </Suspense>
  );
}
