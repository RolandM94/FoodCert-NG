import { DoctorAssessmentBoard } from "@/features/doctor/doctor-assessment-board";

export default function Page() {
  return (
    <DoctorAssessmentBoard
      title="Doctor Declarations"
      description="Review and validate submitted health declarations before physical examination begins."
      initialFilter="declaration"
      basePath="/facility/doctor/assessments"
    />
  );
}
