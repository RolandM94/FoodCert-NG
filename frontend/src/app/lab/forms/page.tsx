"use client";

import { AssessmentFormResponseWorkspace } from "@/components/assessments/assessment-form-response-workspace";
import { PortalShell } from "@/components/layout/portal-shell";

export default function Page() {
  return (
    <PortalShell role="lab_staff" title="Structured lab result forms" description="Complete structured lab result forms assigned to assessments.">
      <AssessmentFormResponseWorkspace role="lab_staff" title="Lab result forms" mode="complete" />
    </PortalShell>
  );
}
