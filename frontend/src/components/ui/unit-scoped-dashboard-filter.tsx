"use client";

import { Search } from "lucide-react";
import { BranchSelector } from "./branch-selector";
import type { OrganizationUnit } from "@/types/organizations";

export function UnitScopedDashboardFilter({
  searchPlaceholder = "Search records",
  searchValue,
  onSearchChange,
  branches,
  branchValue,
  onBranchChange,
  deptValue,
  onDeptChange,
  restricted = false,
}: {
  searchPlaceholder?: string;
  searchValue?: string;
  onSearchChange?: (v: string) => void;
  branches?: OrganizationUnit[];
  branchValue?: string;
  onBranchChange?: (id: string | null) => void;
  deptValue?: string;
  onDeptChange?: (id: string | null) => void;
  restricted?: boolean;
}) {
  return (
    <div className="flex flex-wrap items-center gap-3 rounded-lg border border-neutral-200 bg-white p-3">
      {onSearchChange && (
        <label className="flex items-center gap-2 rounded bg-neutral-50 px-3 h-9 flex-1 min-w-[200px]">
          <Search size={14} className="text-neutral-400" />
          <input
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-neutral-400"
            placeholder={searchPlaceholder}
            value={searchValue ?? ""}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </label>
      )}
      {branches && branches.length > 0 && (
        <BranchSelector branches={branches} value={branchValue} onChange={onBranchChange ?? (() => {})} restricted={restricted} />
      )}
      {onDeptChange && (
        <label className="flex items-center gap-2 text-sm font-semibold text-neutral-700">
          <select
            className="h-9 rounded border border-neutral-200 bg-white px-2 text-xs"
            value={deptValue ?? ""}
            onChange={(e) => onDeptChange(e.target.value || null)}
          >
            <option value="">All departments</option>
            <option value="clinical_department">Clinical</option>
            <option value="lab_department">Laboratory</option>
            <option value="records_department">Records</option>
          </select>
        </label>
      )}
    </div>
  );
}
