import { DoctorAssessmentBoard } from "@/features/doctor/doctor-assessment-board";

export default function Page() {
  return (
    <DoctorAssessmentBoard
      title="Doctor Reviews"
      description="Review lab-ready assessments, inspect system recommendations, and finalize medical decisions."
      initialFilter="review"
      basePath="/facility/doctor/assessments"
    />
  );
}
