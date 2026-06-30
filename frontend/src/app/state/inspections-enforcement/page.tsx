"use client";

import { Suspense } from "react";
import { InspectionsEnforcementLayout } from "@/features/organizations/inspections-enforcement-layout";

export default function Page() {
  return (
    <Suspense fallback={null}>
      <InspectionsEnforcementLayout />
    </Suspense>
  );
}
