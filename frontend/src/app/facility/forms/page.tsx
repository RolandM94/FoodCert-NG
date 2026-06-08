"use client";

import { FormTemplateWorkspace } from "@/components/assessments/form-template-workspace";
import { PortalShell } from "@/components/layout/portal-shell";

export default function Page() {
  return (
    <PortalShell role="facility_admin" title="Facility supplementary forms" description="Create supplementary intake forms and submit them for State Ministry review.">
      <FormTemplateWorkspace role="facility_admin" scope="facility" title="Facility form builder" />
    </PortalShell>
  );
}
