"use client";

import { PerformanceIndicatorsShell } from "@/features/indicators/performance-indicators-shell";
import { PITargetsPanel } from "@/features/indicators/pi-targets-panel";

export default function FederalPITargetsPage() {
  return (
    <PerformanceIndicatorsShell
      role="federal_admin"
      title="Targets & Thresholds"
      description="Set national default targets and performance bands. States inherit these unless an override is allowed."
    >
      <PITargetsPanel />
    </PerformanceIndicatorsShell>
  );
}
