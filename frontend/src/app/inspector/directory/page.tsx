"use client";

import { Suspense } from "react";
import { DirectoryLayout } from "@/features/organizations/directory-layout";

function InspectorDirectoryContent() {
  return <DirectoryLayout role="inspector" />;
}

export default function Page() {
  return (
    <Suspense fallback={null}>
      <InspectorDirectoryContent />
    </Suspense>
  );
}
