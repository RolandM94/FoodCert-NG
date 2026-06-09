"use client";

import { useParams } from "next/navigation";
import { OrganizationInvitesPage } from "@/features/organizations/organization-invites-page";

export default function OrganizationInvitesPageRoute() {
  const params = useParams<{ id: string }>();

  return (
    <OrganizationInvitesPage
      role="super_admin"
      title="Invites"
      description="Send and manage invitations for this organization. Assign roles and units during the invitation process."
      organizationId={params.id}
    />
  );
}
