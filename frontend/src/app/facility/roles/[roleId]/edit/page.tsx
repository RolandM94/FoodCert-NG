"use client";

import { FacilityRoleEditorPage } from "@/features/facilities/facility-team-workspace";

export default function Page({ params }: { params: { roleId: string } }) {
  return <FacilityRoleEditorPage roleId={params.roleId} />;
}
