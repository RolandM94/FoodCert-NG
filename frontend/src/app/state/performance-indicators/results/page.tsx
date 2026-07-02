"use client";

import { PerformanceIndicatorsShell } from "@/features/indicators/performance-indicators-shell";
import { PIResultsPanel } from "@/features/indicators/pi-results-panel";

export default function StatePIResultsPage() {
  return (
    <PerformanceIndicatorsShell
      role="state_admin"
      title="Indicator Results"
      description="Result history for adopted and state-owned indicators."
    >
      <PIResultsPanel />
    </PerformanceIndicatorsShell>
  );
}
