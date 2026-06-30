"use client";

import { useParams } from "next/navigation";
import { DoctorAssessmentWorkspace } from "@/features/doctor/doctor-assessment-workspace";

export default function Page() {
  const params = useParams<{ assessmentId: string }>();
  return <DoctorAssessmentWorkspace assessmentId={params.assessmentId} backHref="/facility/doctor" />;
}
