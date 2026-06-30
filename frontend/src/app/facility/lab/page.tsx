import { LabRequestBoard } from "@/features/lab/lab-request-board";

export default function Page() {
  return (
    <LabRequestBoard
      title="Lab Workspace"
      description="Work through assigned sample collection, result entry, uploads, and doctor submission for facility lab requests."
      basePath="/facility/lab/requests"
    />
  );
}
