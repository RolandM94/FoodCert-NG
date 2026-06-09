"use client";

import { Check } from "lucide-react";
import type { Permission } from "@/types/organizations";

export function PermissionGroup({
  moduleLabel,
  permissions,
  selectedIds,
  onToggle,
  disabled,
}: {
  moduleLabel: string;
  permissions: Permission[];
  selectedIds: Set<string>;
  onToggle: (permissionId: string) => void;
  disabled?: boolean;
}) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4">
      <h4 className="text-xs font-bold uppercase tracking-wide text-neutral-500">
        {moduleLabel}
      </h4>
      <div className="mt-3 flex flex-wrap gap-2">
        {permissions.map((p) => {
          const selected = selectedIds.has(p.id);
          return (
            <button
              key={p.id}
              type="button"
              disabled={disabled}
              className={`inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
                selected
                  ? "border-brand-200 bg-brand-50 text-brand-700"
                  : "border-neutral-200 bg-white text-neutral-700 hover:bg-neutral-50"
              } disabled:opacity-50 disabled:cursor-not-allowed`}
              onClick={() => onToggle(p.id)}
              title={p.description || undefined}
            >
              <span
                className={`flex h-5 w-5 shrink-0 items-center justify-center rounded ${
                  selected ? "bg-brand-600 text-white" : "border-2 border-neutral-300"
                }`}
              >
                {selected && <Check size={12} />}
              </span>
              <span>{p.name}</span>
              {p.is_sensitive && (
                <span className="rounded bg-warning-50 px-1.5 py-0.5 text-[10px] font-bold text-warning-700 ml-auto">
                  Sensitive
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
