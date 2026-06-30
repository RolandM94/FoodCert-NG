"use client";

import { FormTemplateWorkspace } from "@/components/assessments/form-template-workspace";
import { PortalShell } from "@/components/layout/portal-shell";

export default function FacilityAssessmentFormsPage() {
  return (
    <PortalShell
      role="facility_admin"
      title="Assessment Form Templates"
      description="Adopt approved declaration templates, add facility-specific follow-up fields, and prepare local assessment workflows."
    >
      <FormTemplateWorkspace role="facility_admin" scope="facility" title="Facility Assessment Forms" />
    </PortalShell>
  );
}
