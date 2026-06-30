"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { DashboardTemplateGallery } from "@/features/reports/dashboard-template-gallery";

export default function StateDashboardTemplatesPage() {
  return (
    <PortalShell
      role="state_admin"
      title="Dashboard Templates"
      description="Browse and use pre-built dashboard templates for state-level oversight, compliance monitoring, and operational reporting."
    >
      <DashboardTemplateGallery initialModuleSource="reports" canvasBuilderHref="/state/dashboard/canvas-builder" />
    </PortalShell>
  );
}
