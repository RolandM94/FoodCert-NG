"use client";

import { MapPin } from "lucide-react";
import type { OrganizationUnit } from "@/types/organizations";

export function BranchSelector({
  branches,
  value,
  onChange,
  restricted = false,
}: {
  branches: OrganizationUnit[];
  value?: string;
  onChange: (id: string | null) => void;
  restricted?: boolean;
}) {
  if (branches.length === 0) {
    return (
      <p className="text-xs text-neutral-400">No branches available.</p>
    );
  }

  if (restricted) {
    const branch = branches.find((b) => b.id === value);
    return (
      <span className="inline-flex items-center gap-1.5 rounded bg-neutral-100 px-3 py-1.5 text-xs font-semibold text-neutral-600">
        <MapPin size={12} />
        {branch?.name ?? "Branch"}
      </span>
    );
  }

  return (
    <label className="flex items-center gap-2 text-sm font-semibold text-neutral-700">
      <MapPin size={14} className="text-neutral-400" />
      <select
        className="h-9 rounded border border-neutral-200 bg-white px-2 text-xs"
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value || null)}
      >
        <option value="">All branches</option>
        {branches.map((b) => (
          <option key={b.id} value={b.id}>
            {b.name}
          </option>
        ))}
      </select>
    </label>
  );
}
