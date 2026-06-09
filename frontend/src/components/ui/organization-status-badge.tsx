import { ORG_STATUS_COLORS } from "@/lib/stakeholder-labels";

function formatStatus(status: string): string {
  return status.replace(/_/g, " ").replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function OrganizationStatusBadge({ status }: { status?: string | null }) {
  if (!status) return null;

  const colorClass = ORG_STATUS_COLORS[status] ?? "bg-neutral-50 text-neutral-600 ring-neutral-200";

  return (
    <span
      className={`inline-flex items-center rounded px-2 py-1 text-xs font-bold ring-1 ${colorClass}`}
    >
      {formatStatus(status)}
    </span>
  );
}
