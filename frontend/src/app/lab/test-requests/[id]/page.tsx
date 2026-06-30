"use client";

import { useParams } from "next/navigation";
import { LabRequestWorkspace } from "@/features/lab/lab-request-workspace";

export default function Page() {
  const params = useParams<{ id: string }>();
  return <LabRequestWorkspace requestId={params.id} backHref="/lab/test-requests" />;
}
