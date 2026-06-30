"use client";

import { Suspense } from "react";
import { MedicalFacilitiesLayout } from "@/features/organizations/medical-facilities-layout";

export default function Page() {
  return (
    <Suspense fallback={null}>
      <MedicalFacilitiesLayout />
    </Suspense>
  );
}
