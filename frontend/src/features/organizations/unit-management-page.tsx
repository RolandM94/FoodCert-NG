"use client";

import { useState } from "react";
import { Plus, Trash2, UserPlus } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { OrganizationUnitTree } from "@/components/ui/organization-unit-tree";
import { OrganizationUnitForm } from "@/components/ui/organization-unit-form";
import { OrganizationUnitDetail } from "@/components/ui/organization-unit-detail";
import { InviteUserModal } from "@/components/ui/invite-user-modal";
import type { UserRole } from "@/types/auth";
import type { OrganizationUnit } from "@/types/organizations";

type Mode = "view" | "create" | "edit";

export function UnitManagementPage({
  role,
  title,
  description,
  units,
  onCreateUnit,
  onUpdateUnit,
  onDeleteUnit,
  onInviteUser,
  unitTypeFilter,
  canEdit = true,
}: {
  role: UserRole;
  title: string;
  description: string;
  units: OrganizationUnit[];
  onCreateUnit: (data: Record<string, unknown>) => void;
  onUpdateUnit: (unitId: string, data: Record<string, unknown>) => void;
  onDeleteUnit: (unitId: string) => void;
  onInviteUser: (data: { email: string; role: UserRole; unit?: string; phone?: string; message?: string; expires_at?: string }) => void;
  unitTypeFilter?: string[];
  canEdit?: boolean;
}) {
  const filteredUnits = unitTypeFilter
    ? units.filter((u) => unitTypeFilter.includes(u.unit_type))
    : units;

  const [selectedUnit, setSelectedUnit] = useState<OrganizationUnit | null>(null);
  const [mode, setMode] = useState<Mode>("view");
  const [editingUnit, setEditingUnit] = useState<OrganizationUnit | null>(null);
  const [inviteTarget, setInviteTarget] = useState<OrganizationUnit | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSelect = (unit: OrganizationUnit) => {
    setSelectedUnit(unit);
    setMode("view");
    setEditingUnit(null);
    setError(null);
  };

  const handleDelete = (unit: OrganizationUnit) => {
    setSelectedUnit(null);
    setMode("view");
    setError(null);
    onDeleteUnit(unit.id);
  };

  const handleEdit = (unit: OrganizationUnit) => {
    setEditingUnit(unit);
    setMode("edit");
    setError(null);
  };

  const handleCreate = () => {
    setEditingUnit(null);
    setMode("create");
    setError(null);
  };

  const handleInviteOpen = (unit: OrganizationUnit) => {
    setInviteTarget(unit);
    setError(null);
  };

  const searchParams = typeof window !== "undefined" ? new URLSearchParams(window.location.search) : null;
  const branchFromUrl = searchParams?.get("branch");

  return (
    <PortalShell role={role} title={title} description={description}>
      <div className="grid gap-5 lg:grid-cols-[280px_1fr]">
        {/* Left panel: unit tree */}
        <div>
          {canEdit && (
            <button
              className="mb-3 inline-flex w-full h-10 items-center justify-center gap-2 rounded bg-brand-600 text-sm font-bold text-white hover:bg-brand-700"
              onClick={handleCreate}
            >
              <Plus aria-hidden="true" size={16} />
              New
            </button>
          )}
          <OrganizationUnitTree
            units={filteredUnits}
            selectedId={selectedUnit?.id ?? branchFromUrl ?? undefined}
            onSelect={handleSelect}
            onEdit={canEdit ? handleEdit : undefined}
            onDelete={canEdit ? handleDelete : undefined}
            onInvite={canEdit ? handleInviteOpen : undefined}
          />
        </div>

        {/* Main panel */}
        <div className="space-y-4">
          {mode === "create" && (
            <OrganizationUnitForm
              parentOptions={filteredUnits.map((u) => ({ id: u.id, name: u.name }))}
              onSubmit={(data) => {
                setError(null);
                onCreateUnit(data);
              }}
              onCancel={() => {
                setMode("view");
                setError(null);
              }}
              error={error}
            />
          )}

          {mode === "edit" && editingUnit && (
            <OrganizationUnitForm
              parentOptions={filteredUnits
                .filter((u) => u.id !== editingUnit.id)
                .map((u) => ({ id: u.id, name: u.name }))}
              initial={editingUnit}
              submitLabel="Save Changes"
              onSubmit={(data) => {
                setError(null);
                onUpdateUnit(editingUnit.id, data);
              }}
              onCancel={() => {
                setMode("view");
                setError(null);
              }}
              error={error}
            />
          )}

          {mode === "view" && selectedUnit && (
            <>
              <OrganizationUnitDetail
                unit={selectedUnit}
                memberCount={selectedUnit.member_count ?? 0}
              />
              {canEdit && (
                <div className="flex gap-2">
                  <button
                    className="inline-flex h-10 items-center gap-2 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-600 hover:bg-neutral-50"
                    onClick={() => handleEdit(selectedUnit)}
                  >
                    Edit
                  </button>
                  <button
                    className="inline-flex h-10 items-center gap-2 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-600 hover:bg-neutral-50"
                    onClick={() => handleInviteOpen(selectedUnit)}
                  >
                    <UserPlus size={14} />
                    Invite
                  </button>
                  <button
                    className="inline-flex h-10 items-center gap-2 rounded border border-danger-100 px-4 text-sm font-semibold text-danger-500 hover:bg-danger-50"
                    onClick={() => {
                      if (confirm("Deactivate this unit? Members will be unassigned.")) {
                        handleDelete(selectedUnit);
                      }
                    }}
                  >
                    <Trash2 size={14} />
                    Deactivate
                  </button>
                </div>
              )}
            </>
          )}

          {mode === "view" && !selectedUnit && filteredUnits.length > 0 && (
            <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
              <p className="text-sm font-semibold text-neutral-500">Select a unit to view details</p>
              <p className="text-xs text-neutral-400">Choose from the tree on the left or create a new one.</p>
            </div>
          )}
        </div>
      </div>

      <InviteUserModal
        open={inviteTarget !== null}
        onClose={() => setInviteTarget(null)}
        units={filteredUnits}
        preselectUnit={inviteTarget?.id}
        onSubmit={(data) => {
          setError(null);
          onInviteUser(data);
          setInviteTarget(null);
        }}
        error={error}
      />
    </PortalShell>
  );
}
