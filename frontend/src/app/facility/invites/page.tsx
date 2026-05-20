"use client";

import { OrganizationInvitesPage } from "@/features/organizations/organization-invites-page";

export default function Page() {
  return (
    <OrganizationInvitesPage
      role="facility_admin"
      title="Facility Invites"
      description="Invite doctors, lab staff, records staff, and department-scoped users."
    />
  );
}
