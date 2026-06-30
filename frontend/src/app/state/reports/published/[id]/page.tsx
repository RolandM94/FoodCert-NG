"use client";

import { useParams } from "next/navigation";
import { PortalShell } from "@/components/layout/portal-shell";
import { PublishedDashboardView } from "@/features/reports/published-dashboard-view";

export default function StatePublishedDashboardPage() {
  const params = useParams<{ id: string }>();

  return (
    <PortalShell
      role="state_admin"
      title="Published Dashboard"
      description="Read-only published snapshot of a dashboard canvas."
    >
      <PublishedDashboardView dashboardId={params.id} />
    </PortalShell>
  );
}
