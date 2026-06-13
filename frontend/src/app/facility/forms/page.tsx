"use client";

import { AssignedFormsPortal } from "@/components/forms/assigned-forms-portal";
import { PortalShell } from "@/components/layout/portal-shell";

export default function Page() {
  return (
    <PortalShell role="facility_admin" title="Facility assigned forms" description="Complete data collection, accreditation, and reporting forms assigned to your facility.">
      <AssignedFormsPortal portal="facility" title="Facility assigned forms" description="Forms assigned by your State Ministry for accreditation, reporting, or data collection." />
    </PortalShell>
  );
}
