"use client";

import { PerformanceIndicatorsShell } from "@/features/indicators/performance-indicators-shell";
import { PIAiPanel } from "@/features/indicators/pi-ai-panel";
import { PILibraryTable } from "@/features/indicators/pi-library-table";

export default function FederalPILibraryPage() {
  return (
    <PerformanceIndicatorsShell
      role="federal_admin"
      title="National Indicator Library"
      description="Create, publish, share, and manage the lifecycle of national indicators."
    >
      <div className="grid gap-5">
        <PIAiPanel />
        <PILibraryTable
          mode="federal"
          emptyMessage="No indicators yet. Seed the default library or build a KPI from Standards & Policy → Reporting & M&E."
        />
      </div>
    </PerformanceIndicatorsShell>
  );
}
