import { StatusBadge } from "@/components/status/status-badge";

export function AssessmentStatusBadge({ status, label }: { status?: string | null; label?: string | null }) {
  return <StatusBadge status={label || status} />;
}
