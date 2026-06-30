"use client";

import { FacilityTeamMemberDetailPage } from "@/features/facilities/facility-team-workspace";

export default function Page({ params }: { params: { memberId: string } }) {
  return <FacilityTeamMemberDetailPage memberId={params.memberId} />;
}
