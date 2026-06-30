import { DoctorAssessmentBoard } from "@/features/doctor/doctor-assessment-board";

export default function Page() {
  return (
    <DoctorAssessmentBoard
      title="Clinical Reviews"
      description="Work through completed physical exams, lab result reviews, vaccination follow-up, and final decision sign-off."
      initialFilter="review"
    />
  );
}
