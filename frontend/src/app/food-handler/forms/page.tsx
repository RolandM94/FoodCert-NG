"use client";

import { AssignedFormsPortal } from "@/components/forms/assigned-forms-portal";
import { PortalShell } from "@/components/layout/portal-shell";

export default function Page() {
  return (
    <PortalShell role="food_handler" title="Assigned forms" description="Complete surveys, declarations, and questionnaires assigned to you.">
      <AssignedFormsPortal portal="food-handler" title="My assigned forms" description="Surveys, declarations, and questionnaires assigned for your profile." />
    </PortalShell>
  );
}
