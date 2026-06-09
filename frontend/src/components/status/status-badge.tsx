import { titleCaseStatus } from "@/lib/formatters/status";

const toneByStatus: Record<string, string> = {
  active: "bg-brand-50 text-brand-800 ring-brand-200",
  approved: "bg-brand-50 text-brand-800 ring-brand-200",
  cleared: "bg-brand-50 text-brand-800 ring-brand-200",
  valid: "bg-brand-50 text-brand-800 ring-brand-200",
  fit: "bg-brand-50 text-brand-800 ring-brand-200",
  pending: "bg-warning-50 text-warning-700 ring-warning-100",
  pending_validation: "bg-warning-50 text-warning-700 ring-warning-100",
  under_review: "bg-info-50 text-info-700 ring-info-100",
  submitted: "bg-info-50 text-info-700 ring-info-100",
  warning: "bg-warning-50 text-warning-700 ring-warning-100",
  rejected: "bg-danger-50 text-danger-700 ring-danger-100",
  revoked: "bg-danger-50 text-danger-700 ring-danger-100",
  suspended: "bg-danger-50 text-danger-700 ring-danger-100",
  expired: "bg-neutral-100 text-neutral-700 ring-neutral-200",
  temporarily_excluded: "bg-warning-50 text-warning-700 ring-warning-100",
  temporarily_not_fit: "bg-warning-50 text-warning-700 ring-warning-100"
};

export function StatusBadge({ status }: { status?: string | null }) {
  const key = status ?? "unknown";
  return (
    <span className={`inline-flex w-fit items-center rounded-md px-2 py-1 text-xs font-medium ${toneByStatus[key] ?? "bg-neutral-50 text-neutral-700 ring-neutral-200"}`}>
      {titleCaseStatus(status)}
    </span>
  );
}
