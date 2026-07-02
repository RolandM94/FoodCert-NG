"use client";

import { PerformanceIndicatorsShell } from "@/features/indicators/performance-indicators-shell";
import { PIResultsPanel } from "@/features/indicators/pi-results-panel";

export default function FederalPIResultsPage() {
  return (
    <PerformanceIndicatorsShell
      role="federal_admin"
      title="Indicator Results"
      description="Result history with targets, variance, performance bands, and AI explanation."
    >
      <PIResultsPanel />
    </PerformanceIndicatorsShell>
  );
}
