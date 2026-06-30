"use client";

import { FormTemplateWorkspace } from "@/components/assessments/form-template-workspace";
import { PortalShell } from "@/components/layout/portal-shell";

export default function StateAssessmentFormsPage() {
  return (
    <PortalShell
      role="state_admin"
      title="Assessment Form Templates"
      description="Adopt federal declaration templates, extend them for state requirements, and manage review-ready assessment forms."
    >
      <FormTemplateWorkspace role="state_admin" scope="state" title="State Assessment Forms" />
    </PortalShell>
  );
}
