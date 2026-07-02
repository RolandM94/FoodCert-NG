"use client";

import { PerformanceIndicatorsShell } from "@/features/indicators/performance-indicators-shell";
import { PILibraryTable } from "@/features/indicators/pi-library-table";

export default function StatePIAdoptedPage() {
  return (
    <PerformanceIndicatorsShell
      role="state_admin"
      title="Adopted National Indicators"
      description="Review federal standard indicators, adopt them as-is, or clone where allowed."
    >
      <PILibraryTable
        mode="state-adopt"
        filterParams={{ owner_type: "federal", lifecycle_status: "active" }}
        emptyMessage="No federal indicators are available to your state yet."
      />
    </PerformanceIndicatorsShell>
  );
}
