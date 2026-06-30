"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { PortalShell } from "@/components/layout/portal-shell";
import { DashboardCanvasBuilder } from "@/features/reports/dashboard-canvas-builder";

function EmployerCanvasBuilderContent() {
  const searchParams = useSearchParams();
  const widgetId = searchParams.get("widgetId") ?? "";
  const canvasId = searchParams.get("canvasId") ?? "";
  const moduleSource = searchParams.get("module") ?? "employers";

  return (
    <PortalShell
      role="employer"
      title="Dashboard Canvas Builder"
      description="Arrange employer widgets into an operational dashboard for branch and compliance oversight."
    >
      <DashboardCanvasBuilder initialWidgetId={widgetId} initialCanvasId={canvasId} initialModuleSource={moduleSource} />
    </PortalShell>
  );
}

export default function EmployerCanvasBuilderPage() {
  return (
    <Suspense fallback={null}>
      <EmployerCanvasBuilderContent />
    </Suspense>
  );
}
