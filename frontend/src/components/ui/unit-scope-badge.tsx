"use client";

import { MapPin, Network } from "lucide-react";

const UNIT_TYPE_LABELS: Record<string, string> = {
  headquarters: "Headquarters",
  directorate: "Directorate",
  department: "Department",
  unit: "Unit",
  branch: "Branch",
  lab_department: "Lab Dept",
  clinical_department: "Clinical Dept",
  records_department: "Records Dept",
  lga_office: "LGA Office",
  regional_office: "Regional Office",
  other: "Other",
};

const UNIT_TYPE_COLORS: Record<string, string> = {
  headquarters: "bg-purple-50 text-purple-700 ring-purple-200",
  directorate: "bg-blue-50 text-blue-700 ring-blue-200",
  department: "bg-cyan-50 text-cyan-700 ring-cyan-200",
  unit: "bg-slate-50 text-slate-700 ring-slate-200",
  branch: "bg-amber-50 text-amber-700 ring-amber-200",
  lab_department: "bg-teal-50 text-teal-700 ring-teal-200",
  clinical_department: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  records_department: "bg-indigo-50 text-indigo-700 ring-indigo-200",
  lga_office: "bg-orange-50 text-orange-700 ring-orange-200",
  regional_office: "bg-rose-50 text-rose-700 ring-rose-200",
  other: "bg-slate-50 text-slate-700 ring-slate-200",
};

export function UnitScopeBadge({
  orgName,
  unitName,
  unitType,
  stateName,
}: {
  orgName?: string;
  unitName?: string;
  unitType?: string;
  stateName?: string;
}) {
  if (!unitName && !orgName) return null;

  const colorClass = UNIT_TYPE_COLORS[unitType ?? ""] ?? UNIT_TYPE_COLORS.other;
  const typeLabel = UNIT_TYPE_LABELS[unitType ?? ""] ?? unitType;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ring-1 ${colorClass}`}
      title={[orgName, unitName, stateName].filter(Boolean).join(" / ")}
    >
      <Network aria-hidden="true" size={12} />
      {orgName && <span className="max-w-[120px] truncate">{orgName}</span>}
      {unitName && (
        <>
          <span className="opacity-60">/</span>
          <span className="max-w-[100px] truncate">{unitName}</span>
        </>
      )}
      {typeLabel && (
        <span className="ml-1 rounded bg-white/50 px-1 text-[10px]">{typeLabel}</span>
      )}
      {stateName && (
        <>
          <MapPin aria-hidden="true" size={10} className="ml-1 opacity-60" />
          <span className="truncate text-[10px] opacity-70">{stateName}</span>
        </>
      )}
    </span>
  );
}
