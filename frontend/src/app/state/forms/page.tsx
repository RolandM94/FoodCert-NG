"use client";

import { FormTemplateWorkspace } from "@/components/assessments/form-template-workspace";
import { PortalShell } from "@/components/layout/portal-shell";

export default function Page() {
  return (
    <PortalShell role="state_admin" title="State assessment forms" description="Manage state-specific forms and review facility supplementary forms before they are used in assessments.">
      <FormTemplateWorkspace role="state_admin" scope="state" title="State and facility form review" />
    </PortalShell>
  );
}
