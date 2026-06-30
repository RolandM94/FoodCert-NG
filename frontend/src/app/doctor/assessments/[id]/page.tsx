"use client";

import { useParams } from "next/navigation";
import { DoctorAssessmentWorkspace } from "@/features/doctor/doctor-assessment-workspace";

export default function Page() {
  const params = useParams<{ id: string }>();
  return <DoctorAssessmentWorkspace assessmentId={params.id} backHref="/doctor/assessments" />;
}
