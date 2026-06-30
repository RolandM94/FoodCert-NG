"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { DashboardTemplateGallery } from "@/features/reports/dashboard-template-gallery";

export default function EmployerTemplatesPage() {
  return (
    <PortalShell
      role="employer"
      title="Dashboard Templates"
      description="Browse and use pre-built dashboard templates for employer compliance, branch oversight, and food handler certification tracking."
    >
      <DashboardTemplateGallery initialModuleSource="employers" canvasBuilderHref="/employer/reports/canvas-builder" />
    </PortalShell>
  );
}
