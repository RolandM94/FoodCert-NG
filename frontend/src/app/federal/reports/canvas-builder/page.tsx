"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";

import { PortalShell } from "@/components/layout/portal-shell";
import { DashboardCanvasBuilder } from "@/features/reports/dashboard-canvas-builder";

function FederalCanvasBuilderContent() {
  const searchParams = useSearchParams();
  const widgetId = searchParams.get("widgetId") ?? "";
  const canvasId = searchParams.get("canvasId") ?? "";
  const moduleSource = searchParams.get("module") ?? "";

  return (
    <PortalShell
      role="federal_admin"
      title="Canvas Builder"
      description="Arrange saved widgets, text, filters, and AI insight blocks into a responsive dashboard canvas."
    >
      <DashboardCanvasBuilder initialWidgetId={widgetId} initialCanvasId={canvasId} initialModuleSource={moduleSource} />
    </PortalShell>
  );
}

export default function FederalCanvasBuilderPage() {
  return (
    <Suspense fallback={null}>
      <FederalCanvasBuilderContent />
    </Suspense>
  );
}
