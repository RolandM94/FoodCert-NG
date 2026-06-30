"use client";

import { useParams } from "next/navigation";
import { LabRequestWorkspace } from "@/features/lab/lab-request-workspace";

export default function Page() {
  const params = useParams<{ resultId: string }>();
  return <LabRequestWorkspace requestId={params.resultId} backHref="/facility/lab/results" />;
}
