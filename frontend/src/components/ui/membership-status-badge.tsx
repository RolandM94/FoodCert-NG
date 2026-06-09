const STATUS_COLORS: Record<string, string> = {
  invited: "bg-sky-50 text-sky-700 ring-sky-200",
  active: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  suspended: "bg-rose-50 text-rose-700 ring-rose-200",
  removed: "bg-slate-100 text-slate-500 ring-slate-200",
  expired: "bg-slate-100 text-slate-500 ring-slate-200",
  "pending-verification": "bg-amber-50 text-amber-700 ring-amber-200",
  pending_verification: "bg-amber-50 text-amber-700 ring-amber-200",
};

function formatStatus(status: string): string {
  return status.replace(/_/g, " ").replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function MembershipStatusBadge({ status }: { status?: string | null }) {
  if (!status) return null;

  const colorClass = STATUS_COLORS[status] ?? "bg-slate-50 text-slate-600 ring-slate-200";

  return (
    <span
      className={`inline-flex items-center rounded px-2 py-1 text-xs font-bold ring-1 ${colorClass}`}
    >
      {formatStatus(status)}
    </span>
  );
}
