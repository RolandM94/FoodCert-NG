const STATUS_COLORS: Record<string, string> = {
  invited: "bg-info-50 text-info-700 ring-info-100",
  active: "bg-brand-50 text-brand-700 ring-brand-200",
  suspended: "bg-danger-50 text-danger-700 ring-danger-100",
  removed: "bg-neutral-100 text-neutral-500 ring-neutral-200",
  expired: "bg-neutral-100 text-neutral-500 ring-neutral-200",
  "pending-verification": "bg-warning-50 text-warning-700 ring-warning-100",
  pending_verification: "bg-warning-50 text-warning-700 ring-warning-100",
};

function formatStatus(status: string): string {
  return status.replace(/_/g, " ").replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function MembershipStatusBadge({ status }: { status?: string | null }) {
  if (!status) return null;

  const colorClass = STATUS_COLORS[status] ?? "bg-neutral-50 text-neutral-600 ring-neutral-200";

  return (
    <span
      className={`inline-flex items-center rounded px-2 py-1 text-xs font-bold ring-1 ${colorClass}`}
    >
      {formatStatus(status)}
    </span>
  );
}
