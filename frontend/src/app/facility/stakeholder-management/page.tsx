"use client";

import { Suspense } from "react";
import { StakeholderManagementLayout } from "@/features/organizations/stakeholder-management-layout";

export default function Page() {
  return (
    <Suspense fallback={null}>
      <StakeholderManagementLayout role="facility_admin" />
    </Suspense>
  );
}
