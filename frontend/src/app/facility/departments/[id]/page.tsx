"use client";

import { useParams } from "next/navigation";
import { UnitDetailPage } from "@/features/organizations/unit-detail-page";

export default function Page() {
  const params = useParams<{ id: string }>();
  return <UnitDetailPage backHref="/facility/departments" kind="department" role="facility_admin" unitId={params.id} />;
}
