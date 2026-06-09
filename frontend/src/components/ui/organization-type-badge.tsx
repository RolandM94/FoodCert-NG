import type { OrganizationType } from "@/types/organizations";
import { getOrgTypeLabel } from "@/lib/stakeholder-labels";

const TYPE_COLORS: Record<OrganizationType, string> = {
  platform_operator: "bg-purple-50 text-purple-700 ring-purple-200",
  federal_ministry: "bg-blue-50 text-blue-700 ring-blue-200",
  state_ministry: "bg-teal-50 text-teal-700 ring-teal-200",
  medical_facility: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  employer: "bg-amber-50 text-amber-700 ring-amber-200",
};

export function OrganizationTypeBadge({ type }: { type: OrganizationType }) {
  const colorClass = TYPE_COLORS[type] ?? "bg-slate-50 text-slate-600 ring-slate-200";

  return (
    <span
      className={`inline-flex items-center rounded px-2 py-1 text-xs font-bold ring-1 ${colorClass}`}
    >
      {getOrgTypeLabel(type)}
    </span>
  );
}
