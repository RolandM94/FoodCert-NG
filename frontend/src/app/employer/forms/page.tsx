"use client";

import { AssignedFormsPortal } from "@/components/forms/assigned-forms-portal";
import { PortalShell } from "@/components/layout/portal-shell";

export default function Page() {
  return (
    <PortalShell role="employer" title="Assigned forms" description="Complete data collection and compliance forms assigned to your business.">
      <AssignedFormsPortal portal="employer" title="Employer assigned forms" description="Forms assigned by your State Ministry or the FoodCert platform." />
    </PortalShell>
  );
}
