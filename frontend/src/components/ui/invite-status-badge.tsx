const STATUS_COLORS: Record<string, string> = {
  pending: "bg-warning-50 text-warning-700 ring-warning-100",
  accepted: "bg-brand-50 text-brand-700 ring-brand-200",
  expired: "bg-neutral-50 text-neutral-500 ring-neutral-200",
  revoked: "bg-danger-50 text-danger-500 ring-danger-100",
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
