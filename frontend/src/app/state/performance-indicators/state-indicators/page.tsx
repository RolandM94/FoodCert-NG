"use client";

import { PerformanceIndicatorsShell } from "@/features/indicators/performance-indicators-shell";
import { PILibraryTable } from "@/features/indicators/pi-library-table";

export default function StatePIOwnPage() {
  return (
    <PerformanceIndicatorsShell
      role="state_admin"
      title="State Indicators"
      description="State-owned indicators, including clones of federal standards."
    >
      <PILibraryTable
        mode="state-own"
        filterParams={{ owner_type: "state" }}
        emptyMessage="No state indicators yet. Clone a federal indicator from Adopted National Indicators to get started."
      />
    </PerformanceIndicatorsShell>
  );
}
