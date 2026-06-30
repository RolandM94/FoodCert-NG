"use client";

import { useParams } from "next/navigation";
import { PortalShell } from "@/components/layout/portal-shell";
import { PublishedDashboardView } from "@/features/reports/published-dashboard-view";

export default function EmployerPublishedDashboardPage() {
  const params = useParams<{ id: string }>();

  return (
    <PortalShell
      role="employer"
      title="Published Dashboard"
      description="Read-only published snapshot of a dashboard canvas."
    >
      <PublishedDashboardView dashboardId={params.id} />
    </PortalShell>
  );
}
