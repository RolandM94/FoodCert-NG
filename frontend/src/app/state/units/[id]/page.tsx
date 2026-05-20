"use client";

import { useParams } from "next/navigation";
import { UnitDetailPage } from "@/features/organizations/unit-detail-page";

export default function Page() {
  const params = useParams<{ id: string }>();
  return <UnitDetailPage backHref="/state/units" kind="state_unit" role="state_admin" unitId={params.id} />;
}
