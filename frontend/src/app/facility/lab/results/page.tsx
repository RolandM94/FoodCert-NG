import { LabResultsBoard } from "@/features/lab/lab-results-board";

export default function Page() {
  return (
    <LabResultsBoard
      title="Lab Results"
      description="Track result submission status, flagged outcomes, repeat requests, and doctor-reviewed cases."
      basePath="/facility/lab/results"
    />
  );
}
