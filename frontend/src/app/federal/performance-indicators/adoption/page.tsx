"use client";

import { PerformanceIndicatorsShell } from "@/features/indicators/performance-indicators-shell";
import { PIAdoptionPanel } from "@/features/indicators/pi-adoption-panel";

export default function FederalPIAdoptionPage() {
  return (
    <PerformanceIndicatorsShell
      role="federal_admin"
      title="State Adoption"
      description="Track which states have adopted or cloned each national indicator."
    >
      <PIAdoptionPanel />
    </PerformanceIndicatorsShell>
  );
}
