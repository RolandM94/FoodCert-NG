"use client";

import { useParams } from "next/navigation";
import { UnitDetailPage } from "@/features/organizations/unit-detail-page";

export default function Page() {
  const params = useParams<{ id: string }>();
  return <UnitDetailPage backHref="/employer/branches" kind="branch" role="employer" unitId={params.id} />;
}
