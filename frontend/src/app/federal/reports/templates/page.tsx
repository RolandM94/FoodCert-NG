"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { DashboardTemplateGallery } from "@/features/reports/dashboard-template-gallery";

export default function FederalDashboardTemplatesPage() {
  return (
    <PortalShell
      role="federal_admin"
      title="Dashboard Templates"
      description="Browse prebuilt federal dashboard templates and clone one into your own editable canvas."
    >
      <DashboardTemplateGallery canvasBuilderHref="/federal/reports/canvas-builder" />
    </PortalShell>
  );
}
