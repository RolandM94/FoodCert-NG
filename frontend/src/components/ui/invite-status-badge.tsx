const STATUS_COLORS: Record<string, string> = {
  pending: "bg-amber-50 text-amber-700 ring-amber-200",
  accepted: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  expired: "bg-slate-50 text-slate-500 ring-slate-200",
  revoked: "bg-red-50 text-red-600 ring-red-200",
};

const STATUS_LABELS: Record<string, string> = {
  pending: "Pending",
  accepted: "Accepted",
  expired: "Expired",
  revoked: "Revoked",
};

export function InviteStatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ${
        STATUS_COLORS[status] ?? STATUS_COLORS.pending
      }`}
    >
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}
