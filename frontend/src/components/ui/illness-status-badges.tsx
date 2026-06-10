const STATUS_STYLES: Record<string, string> = {
  none: "bg-neutral-50 text-neutral-600 ring-neutral-200",
  not_required: "bg-neutral-50 text-neutral-600 ring-neutral-200",
  pending: "bg-warning-50 text-warning-700 ring-warning-100",
  under_review: "bg-info-50 text-info-700 ring-blue-200",
  clearance_required: "bg-warning-50 text-warning-700 ring-warning-100",
  cleared: "bg-brand-50 text-brand-700 ring-brand-200",
  rejected: "bg-danger-50 text-danger-700 ring-danger-100",
  overdue: "bg-danger-50 text-danger-700 ring-danger-100",
  active: "bg-danger-50 text-danger-700 ring-danger-100",
};

const EXCLUSION_LABELS: Record<string, string> = {
  none: "No Active Exclusion",
  pending: "Excluded from Food Handling",
  under_review: "Medical Review Pending",
  clearance_required: "Public Health Clearance Required",
  cleared: "Exclusion Ended",
  rejected: "Not Cleared",
  active: "Excluded from Food Handling",
};

const RTW_LABELS: Record<string, string> = {
  none: "Not Required",
  not_required: "Not Required",
  pending: "Pending Medical Review",
  under_review: "Under Medical Review",
  clearance_required: "Pending Public Health Clearance",
  cleared: "Cleared to Return",
  rejected: "Not Cleared",
  overdue: "Overdue",
};

function StatusPill({ label, status }: { label: string; status: string }) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ${STATUS_STYLES[status] ?? STATUS_STYLES.none}`}>
      {label}
    </span>
  );
}

function labelFrom(value: string, labels: Record<string, string>) {
  return labels[value] ?? value.replaceAll("_", " ");
}

export function IllnessExclusionStatusBadge({ status }: { status?: string | null }) {
  const normalized = status || "none";
  return <StatusPill label={labelFrom(normalized, EXCLUSION_LABELS)} status={normalized} />;
}

export function ReturnToWorkStatusBadge({
  status,
  earliestReturnDate,
}: {
  status?: string | null;
  earliestReturnDate?: string | null;
}) {
  const isOverdue = Boolean(
    earliestReturnDate &&
    status &&
    !["cleared", "rejected"].includes(status) &&
    new Date(earliestReturnDate) < new Date(new Date().toDateString())
  );
  const normalized = isOverdue ? "overdue" : status || "not_required";
  return <StatusPill label={labelFrom(normalized, RTW_LABELS)} status={normalized} />;
}
