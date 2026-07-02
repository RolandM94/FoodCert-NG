"use client";

import { PerformanceIndicatorsShell } from "@/features/indicators/performance-indicators-shell";
import { PIOverviewPanel } from "@/features/indicators/pi-overview-panel";

export default function FederalPIOverviewPage() {
  return (
    <PerformanceIndicatorsShell
      role="federal_admin"
      title="Performance Indicators"
      description="National KPI definitions, targets, thresholds, adoption, and results."
    >
      <PIOverviewPanel />
    </PerformanceIndicatorsShell>
  );
}
