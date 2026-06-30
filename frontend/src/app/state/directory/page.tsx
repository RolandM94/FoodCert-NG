"use client";

import { Suspense } from "react";
import { DirectoryLayout } from "@/features/organizations/directory-layout";

export default function Page() {
  return (
    <Suspense fallback={null}>
      <DirectoryLayout role="state_admin" />
    </Suspense>
  );
}
