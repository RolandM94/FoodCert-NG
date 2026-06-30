"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { PortalShell } from "@/components/layout/portal-shell";
import { AnalyticsWidgetBuilder } from "@/features/reports/analytics-widget-builder";

function InspectorDashboardBuilderContent() {
  const searchParams = useSearchParams();
  const worksheetId = searchParams.get("worksheetId") ?? "";
  const moduleSource = searchParams.get("module") ?? "inspections";

  return (
    <PortalShell
      role="inspector"
      title="Dashboard Builder"
      description="Turn inspection worksheets into operational widgets for queues, risk tracking, and enforcement oversight."
    >
      <AnalyticsWidgetBuilder initialWorksheetId={worksheetId} initialModuleSource={moduleSource} />
    </PortalShell>
  );
}

export default function InspectorDashboardBuilderPage() {
  return (
    <Suspense fallback={null}>
      <InspectorDashboardBuilderContent />
    </Suspense>
  );
}
