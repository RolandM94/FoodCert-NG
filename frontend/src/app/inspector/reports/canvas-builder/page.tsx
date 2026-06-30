"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { PortalShell } from "@/components/layout/portal-shell";
import { DashboardCanvasBuilder } from "@/features/reports/dashboard-canvas-builder";

function InspectorCanvasBuilderContent() {
  const searchParams = useSearchParams();
  const widgetId = searchParams.get("widgetId") ?? "";
  const canvasId = searchParams.get("canvasId") ?? "";
  const moduleSource = searchParams.get("module") ?? "inspections";

  return (
    <PortalShell
      role="inspector"
      title="Dashboard Canvas Builder"
      description="Arrange inspection widgets into a focused operational dashboard that still runs on the shared analytics engine."
    >
      <DashboardCanvasBuilder initialWidgetId={widgetId} initialCanvasId={canvasId} initialModuleSource={moduleSource} />
    </PortalShell>
  );
}

export default function InspectorCanvasBuilderPage() {
  return (
    <Suspense fallback={null}>
      <InspectorCanvasBuilderContent />
    </Suspense>
  );
}
