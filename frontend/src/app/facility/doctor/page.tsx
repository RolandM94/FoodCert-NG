import { DoctorAssessmentBoard } from "@/features/doctor/doctor-assessment-board";

export default function Page() {
  return (
    <DoctorAssessmentBoard
      title="Doctor Workspace"
      description="Manage assigned facility cases from declaration review through physical exam, lab request, and final decision."
      basePath="/facility/doctor/assessments"
    />
  );
}
