"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { PublishedDashboardView } from "@/features/reports/published-dashboard-view";

export default function StateDashboardPublishedPage({ params }: { params: { id: string } }) {
  return (
    <PortalShell
      role="state_admin"
      title="Published Dashboard"
      description="Review a published dashboard snapshot with interactive filters and governed sharing."
    >
      <PublishedDashboardView dashboardId={params.id} />
    </PortalShell>
  );
}
