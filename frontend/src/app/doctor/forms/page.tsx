"use client";

import { AssessmentFormResponseWorkspace } from "@/components/assessments/assessment-form-response-workspace";
import { PortalShell } from "@/components/layout/portal-shell";

export default function Page() {
  return (
    <PortalShell role="doctor" title="Form review" description="Review submitted dynamic assessment forms, risk flags, and correction requests for assigned assessments.">
      <AssessmentFormResponseWorkspace role="doctor" title="Clinical form review" mode="review" />
    </PortalShell>
  );
}
