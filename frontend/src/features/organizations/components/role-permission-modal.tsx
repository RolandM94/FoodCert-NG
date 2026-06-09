"use client";

import { useEffect, useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { X, Save, Loader2 } from "lucide-react";
import { PermissionGroup } from "@/features/organizations/components/permission-group";
import {
  fetchPermissions,
  fetchRolePermissions,
  createRole,
  updateRole,
  addRolePermission,
  removeRolePermission,
} from "@/lib/api/organizations";
import { getApiErrorMessage } from "@/lib/api/client";
import type { OrganizationType, Permission, StakeholderRole } from "@/types/organizations";

type Props = {
  open: boolean;
  mode: "create" | "edit";
  role?: StakeholderRole | null;
  organizationType: OrganizationType;
  onClose: () => void;
  onSaved: () => void;
};

const MODULE_LABELS: Record<string, string> = {
  organization: "Organization",
  unit: "Units / Offices / Branches",
  user: "Users",
  invite: "Invites",
  role: "Roles & Permissions",
  permission: "Permissions",
  employer: "Employers",
  facility: "Medical Facilities",
  certificate: "Certificates",
  inspection: "Inspections",
  payment: "Payments",
  settlement: "Settlements",
  report: "Reports",
  audit: "Audit Logs",
};

export function RolePermissionModal({ open, mode, role, organizationType, onClose, onSaved }: Props) {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: allPermissions } = useQuery({
    queryKey: ["permissions"],
    queryFn: async () => fetchPermissions(),
    enabled: open,
  });

  const { data: rolePermissions = [] } = useQuery({
    queryKey: ["role-permissions", role?.id],
    queryFn: () => fetchRolePermissions(role!.id),
    enabled: open && mode === "edit" && !!role?.id,
  });

  useEffect(() => {
    if (!open) return;
    if (mode === "edit" && role) {
      setName(role.name || "");
      setDescription(role.description || "");
      setSelectedIds(new Set(rolePermissions.map((p: Permission) => p.id)));
    } else {
      setName("");
      setDescription("");
      setSelectedIds(new Set());
    }
    setError(null);
    setSubmitting(false);
  }, [open, mode, role, rolePermissions]);

  const permissionsByModule = useMemo(() => {
    const perms = allPermissions ?? [];
    return perms.reduce<Record<string, Permission[]>>((acc, p) => {
      (acc[p.module] ??= []).push(p);
      return acc;
    }, {});
  }, [allPermissions]);

  const selectedCount = selectedIds.size;
  const totalCount = (allPermissions ?? []).length;
  const loadingPerms = !allPermissions && open;

  function toggle(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  async function handleSave() {
    if (!name.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      let savedRole: StakeholderRole;
      if (mode === "create") {
        savedRole = await createRole({
          name: name.trim(),
          code: name.trim().toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, ""),
          organization_type: organizationType,
          description: description.trim() || undefined,
          status: "active",
        });
      } else if (!role) {
        throw new Error("No role selected");
      } else {
        savedRole = await updateRole(role.id, {
          name: name.trim(),
          description: description.trim() || undefined,
        });
      }

      const existing = new Set(rolePermissions.map((p: Permission) => p.id));
      for (const id of selectedIds) {
        if (!existing.has(id)) {
          await addRolePermission(savedRole.id, id);
        }
      }
      for (const id of existing) {
        if (!selectedIds.has(id)) {
          await removeRolePermission(savedRole.id, id);
        }
      }

      queryClient.invalidateQueries({ queryKey: ["roles-by-type"] });
      onSaved();
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to save role."));
    } finally {
      setSubmitting(false);
    }
  }

  if (!open) return null;

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/40" onClick={onClose} />
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="w-full max-w-2xl overflow-hidden rounded-2xl bg-white shadow-md flex flex-col max-h-[90vh]">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-neutral-200 px-6 py-4">
            <h2 className="text-lg font-semibold text-neutral-900">
              {mode === "create" ? "Create Role" : "Edit Role"}
            </h2>
            <button
              className="rounded-lg p-1.5 hover:bg-neutral-100"
              onClick={onClose}
              aria-label="Close modal"
              type="button"
            >
              <X size={18} className="text-neutral-500" />
            </button>
          </div>

          {/* Body */}
          <div className="max-h-[60vh] overflow-y-auto px-6 py-4 space-y-4">
            {error && (
              <div className="rounded-lg border border-danger-100 bg-danger-50 px-4 py-3 text-sm font-semibold text-danger-700">
                {error}
              </div>
            )}

            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Role name <span className="text-danger-500">*</span>
              <input
                className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm text-neutral-900 placeholder:text-neutral-400 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-100"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. State Viewer"
                required
              />
              {!name.trim() && (
                <p className="text-xs text-danger-500">Role name is required.</p>
              )}
            </label>

            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Description
              <textarea
                className="rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-900 placeholder:text-neutral-400 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-100"
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Optional description"
              />
            </label>

            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-neutral-900">Permissions</h3>
              <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-bold text-brand-700">
                {selectedCount} / {totalCount} selected
              </span>
            </div>

            {loadingPerms ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 size={20} className="animate-spin text-neutral-400" />
              </div>
            ) : totalCount === 0 ? (
              <p className="py-4 text-center text-sm text-neutral-500">No permissions available.</p>
            ) : (
              <div className="space-y-3">
                {Object.entries(permissionsByModule).map(([mod, perms]) => (
                  <PermissionGroup
                    key={mod}
                    moduleLabel={MODULE_LABELS[mod] ?? mod}
                    permissions={perms}
                    selectedIds={selectedIds}
                    onToggle={toggle}
                    disabled={submitting}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-2 border-t border-neutral-200 px-6 py-4">
            <button
              className="inline-flex h-10 items-center gap-2 rounded-lg border border-neutral-200 px-4 text-sm font-medium text-neutral-700 hover:bg-neutral-50"
              onClick={onClose}
              type="button"
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              className="inline-flex h-10 items-center gap-2 rounded-lg bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
              onClick={handleSave}
              type="button"
              disabled={submitting || !name.trim()}
            >
              {submitting ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save size={16} />
                  Save
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
