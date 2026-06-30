"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { PortalShell } from "@/components/layout/portal-shell";
import { AnalyticsWidgetBuilder } from "@/features/reports/analytics-widget-builder";

function EmployerDashboardBuilderContent() {
  const searchParams = useSearchParams();
  const worksheetId = searchParams.get("worksheetId") ?? "";
  const moduleSource = searchParams.get("module") ?? "employers";

  return (
    <PortalShell
      role="employer"
      title="Dashboard Builder"
      description="Turn employer worksheets into reusable KPI cards, charts, tables, and queue widgets for compliance monitoring."
    >
      <AnalyticsWidgetBuilder initialWorksheetId={worksheetId} initialModuleSource={moduleSource} />
    </PortalShell>
  );
}

export default function EmployerDashboardBuilderPage() {
  return (
    <Suspense fallback={null}>
      <EmployerDashboardBuilderContent />
    </Suspense>
  );
}
