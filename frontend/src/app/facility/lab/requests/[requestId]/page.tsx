"use client";

import { useParams } from "next/navigation";
import { LabRequestWorkspace } from "@/features/lab/lab-request-workspace";

export default function Page() {
  const params = useParams<{ requestId: string }>();
  return <LabRequestWorkspace requestId={params.requestId} backHref="/facility/lab/requests" />;
}
