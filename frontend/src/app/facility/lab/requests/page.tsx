import { LabRequestBoard } from "@/features/lab/lab-request-board";

export default function Page() {
  return (
    <LabRequestBoard
      title="Lab Requests"
      description="See assigned requests, collect samples, enter results, and move completed lab work to doctor review."
      basePath="/facility/lab/requests"
    />
  );
}
