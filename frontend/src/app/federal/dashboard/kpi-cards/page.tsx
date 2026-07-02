"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { KpiCardLibrary } from "@/components/kpi/kpi-card-library";

export default function FederalKpiCardLibraryPage() {
  return (
    <PortalShell
      role="federal_admin"
      title="KPI Card Library"
      description="Browse the shared KPI card catalog, create widgets from cards, and draft new cards with AI."
    >
      <KpiCardLibrary showInstantiate addLabel="" onAddToSurface={undefined} />
    </PortalShell>
  );
}
