"use client";

import { FormTemplateWorkspace } from "@/components/assessments/form-template-workspace";
import { PortalShell } from "@/components/layout/portal-shell";

export default function Page() {
  return (
    <PortalShell role="federal_admin" title="National assessment forms" description="Create and publish national dynamic forms used by medical verification workflows.">
      <FormTemplateWorkspace role="federal_admin" scope="national" title="National form library" />
    </PortalShell>
  );
}
