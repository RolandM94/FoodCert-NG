"use client";

import { PerformanceIndicatorsShell } from "@/features/indicators/performance-indicators-shell";
import { PIOverviewPanel } from "@/features/indicators/pi-overview-panel";

export default function StatePIOverviewPage() {
  return (
    <PerformanceIndicatorsShell
      role="state_admin"
      title="Performance Indicators"
      description="Adopted national indicators, state indicators, and performance results."
    >
      <PIOverviewPanel />
    </PerformanceIndicatorsShell>
  );
}
