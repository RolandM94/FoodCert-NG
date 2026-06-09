"use client";

import { ChevronRight, ChevronDown, Pencil, Trash2, UserPlus } from "lucide-react";
import { useState } from "react";
import type { OrganizationUnit } from "@/types/organizations";

const UNIT_TYPE_LABELS: Record<string, string> = {
  headquarters: "HQ",
  directorate: "Directorate",
  department: "Dept",
  unit: "Unit",
  branch: "Branch",
  lab_department: "Lab",
  clinical_department: "Clinical",
  records_department: "Records",
  lga_office: "LGA",
  regional_office: "Region",
  other: "Other",
};

function UnitNode({
  unit,
  units,
  onSelect,
  onEdit,
  onDelete,
  onInvite,
  selectedId,
  depth = 0,
}: {
  unit: OrganizationUnit;
  units: OrganizationUnit[];
  onSelect: (u: OrganizationUnit) => void;
  onEdit?: (u: OrganizationUnit) => void;
  onDelete?: (u: OrganizationUnit) => void;
  onInvite?: (u: OrganizationUnit) => void;
  selectedId?: string;
  depth?: number;
}) {
  const children = units.filter((u) => u.parent === unit.id);
  const [expanded, setExpanded] = useState(depth < 2);
  const [showActions, setShowActions] = useState(false);
  const hasChildren = children.length > 0;
  const isSelected = selectedId === unit.id;
  const isInactive = !unit.is_active;

  return (
    <li>
      <div
        className={`flex items-center gap-1 rounded px-2 py-1.5 cursor-pointer group ${
          isSelected ? "bg-brand-50 text-brand-700 ring-1 ring-brand-200" : "hover:bg-neutral-50"
        } ${isInactive ? "opacity-60" : ""}`}
        style={{ marginLeft: `${depth * 20}px` }}
        onClick={() => onSelect(unit)}
        onMouseEnter={() => setShowActions(true)}
        onMouseLeave={() => setShowActions(false)}
      >
        <button
          className={`flex h-5 w-5 items-center justify-center rounded ${hasChildren ? "text-neutral-500" : "text-neutral-300"}`}
          onClick={(e) => {
            e.stopPropagation();
            setExpanded(!expanded);
          }}
          disabled={!hasChildren}
        >
          {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </button>
        <span className="ml-1 flex-1 truncate text-sm font-medium">{unit.name}</span>
        <span className="rounded bg-neutral-100 px-1.5 py-0.5 text-[10px] font-semibold text-neutral-500 uppercase">
          {UNIT_TYPE_LABELS[unit.unit_type] ?? unit.unit_type}
        </span>
        {showActions && (
          <div className="flex items-center gap-0.5">
            {onInvite && (
              <button
                className="rounded p-1 hover:bg-brand-100 text-neutral-400 hover:text-brand-600"
                title="Invite user to this unit"
                onClick={(e) => {
                  e.stopPropagation();
                  onInvite(unit);
                }}
              >
                <UserPlus size={13} />
              </button>
            )}
            {onEdit && (
              <button
                className="rounded p-1 hover:bg-neutral-100 text-neutral-400 hover:text-neutral-700"
                title="Edit unit"
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(unit);
                }}
              >
                <Pencil size={13} />
              </button>
            )}
            {onDelete && (
              <button
                className="rounded p-1 hover:bg-danger-50 text-neutral-400 hover:text-danger-500"
                title="Deactivate unit"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(unit);
                }}
              >
                <Trash2 size={13} />
              </button>
            )}
          </div>
        )}
      </div>
      {expanded && hasChildren && (
        <ul>
          {children.map((child) => (
            <UnitNode
              key={child.id}
              unit={child}
              units={units}
              onSelect={onSelect}
              onEdit={onEdit}
              onDelete={onDelete}
              onInvite={onInvite}
              selectedId={selectedId}
              depth={depth + 1}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

export function OrganizationUnitTree({
  units,
  selectedId,
  onSelect,
  onEdit,
  onDelete,
  onInvite,
}: {
  units: OrganizationUnit[];
  selectedId?: string;
  onSelect: (unit: OrganizationUnit) => void;
  onEdit?: (unit: OrganizationUnit) => void;
  onDelete?: (unit: OrganizationUnit) => void;
  onInvite?: (unit: OrganizationUnit) => void;
}) {
  const roots = units.filter((u) => !u.parent);

  if (units.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-10 text-center">
        <p className="text-sm font-semibold text-neutral-500">No units created yet</p>
        <p className="text-xs text-neutral-400 max-w-xs">
          Create your first unit to organize users, branches, departments, or offices.
        </p>
      </div>
    );
  }

  return (
    <nav className="max-h-[60vh] overflow-y-auto rounded-lg border border-neutral-200 bg-white p-2">
      <ul className="space-y-0.5">
        {roots.map((root) => (
          <UnitNode
            key={root.id}
            unit={root}
            units={units}
            onSelect={onSelect}
            onEdit={onEdit}
            onDelete={onDelete}
            onInvite={onInvite}
            selectedId={selectedId}
          />
        ))}
      </ul>
    </nav>
  );
}
