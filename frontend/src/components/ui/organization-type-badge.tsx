import type { OrganizationType } from "@/types/organizations";
import { getOrgTypeLabel } from "@/lib/stakeholder-labels";

const TYPE_COLORS: Record<OrganizationType, string> = {
  platform_operator: "bg-neutral-100 text-neutral-700 ring-neutral-200",
  federal_ministry: "bg-info-50 text-info-700 ring-blue-200",
  state_ministry: "bg-brand-50 text-brand-700 ring-teal-200",
  medical_facility: "bg-brand-50 text-brand-700 ring-brand-200",
  employer: "bg-warning-50 text-warning-700 ring-warning-100",
};

export function OrganizationTypeBadge({ type }: { type: OrganizationType }) {
  const colorClass = TYPE_COLORS[type] ?? "bg-neutral-50 text-neutral-600 ring-neutral-200";

  return (
    <span
      className={`inline-flex items-center rounded px-2 py-1 text-xs font-bold ring-1 ${colorClass}`}
    >
      {getOrgTypeLabel(type)}
    </span>
  );
}
