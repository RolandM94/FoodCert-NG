"use client";

import { AssessmentFormResponseWorkspace } from "@/components/assessments/assessment-form-response-workspace";
import { PortalShell } from "@/components/layout/portal-shell";

export default function Page() {
  return (
    <PortalShell role="food_handler" title="Assigned forms" description="Complete questionnaires assigned for your medical verification assessment.">
      <AssessmentFormResponseWorkspace role="food_handler" title="My assigned questionnaires" mode="complete" />
    </PortalShell>
  );
}
