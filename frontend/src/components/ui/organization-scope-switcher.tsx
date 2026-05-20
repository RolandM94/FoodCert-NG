"use client";

import { MapPin, Network } from "lucide-react";
import type { OrganizationUnit } from "@/types/organizations";

export function OrganizationScopeSwitcher({
  branches,
  departments,
  currentBranchId,
  currentDeptId,
  onBranchChange,
  onDeptChange,
  restricted = false,
  restrictedLabel,
}: {
  branches?: OrganizationUnit[];
  departments?: OrganizationUnit[];
  currentBranchId?: string;
  currentDeptId?: string;
  onBranchChange?: (id: string | null) => void;
  onDeptChange?: (id: string | null) => void;
  restricted?: boolean;
  restrictedLabel?: string;
}) {
  const showBranches = branches && branches.length > 0;
  const showDepts = departments && departments.length > 0;

  if (!showBranches && !showDepts) return null;

  return (
    <div className="flex items-center gap-2 text-sm">
      {restricted && restrictedLabel ? (
        <span className="inline-flex items-center gap-1.5 rounded bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-600">
          <Network size={12} />
          {restrictedLabel}
        </span>
      ) : (
        <>
          {showBranches && (
            <label className="flex items-center gap-1.5 rounded bg-white border border-slate-200 px-2 py-1.5">
              <MapPin size={12} className="text-slate-400" />
              <select
                className="bg-transparent text-xs font-semibold text-slate-700 outline-none max-w-[160px] truncate"
                value={currentBranchId ?? ""}
                onChange={(e) => onBranchChange?.(e.target.value || null)}
              >
                <option value="">All branches</option>
                {branches.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </select>
            </label>
          )}
          {showDepts && (
            <label className="flex items-center gap-1.5 rounded bg-white border border-slate-200 px-2 py-1.5">
              <Network size={12} className="text-slate-400" />
              <select
                className="bg-transparent text-xs font-semibold text-slate-700 outline-none max-w-[160px] truncate"
                value={currentDeptId ?? ""}
                onChange={(e) => onDeptChange?.(e.target.value || null)}
              >
                <option value="">All departments</option>
                {departments.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            </label>
          )}
        </>
      )}
    </div>
  );
}
