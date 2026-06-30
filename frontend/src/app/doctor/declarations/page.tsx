import { DoctorAssessmentBoard } from "@/features/doctor/doctor-assessment-board";

export default function Page() {
  return (
    <DoctorAssessmentBoard
      title="Declaration Queue"
      description="Review submitted health declarations, validate safe cases, and send corrections back where doctor clarification is needed."
      initialFilter="declaration"
    />
  );
}
