"use client";

import { useState } from "react";
import { X, ShieldCheck, Ban, UserPlus, Trash2, RotateCw, ToggleLeft, ToggleRight } from "lucide-react";
import { MembershipStatusBadge } from "@/components/ui/membership-status-badge";
import type { OrganizationMembership, StakeholderRole, OrganizationUnit } from "@/types/organizations";

type MembershipAction =
  | "suspend"
  | "reactivate"
  | "remove"
  | "change-role"
  | "change-unit"
  | "toggle-restriction";

export function UserMembershipDetailDrawer({
  membership,
  roles,
  units,
  onClose,
  onAction,
}: {
  membership: OrganizationMembership;
  roles: StakeholderRole[];
  units: OrganizationUnit[];
  onClose: () => void;
  onAction: (action: MembershipAction, payload?: Record<string, unknown>) => void;
}) {
  const [selectedRole, setSelectedRole] = useState(membership.role);
  const [selectedUnit, setSelectedUnit] = useState(membership.unit ?? "");

  const isActive = membership.status === "active";
  const isSuspended = membership.status === "suspended";

  function formatDate(value?: string) {
    if (!value) return "N/A";
    return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
  }

  return (
    <>
      <div className="fixed inset-0 z-40 bg-slate-900/40" onClick={onClose} />
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-lg overflow-y-auto border-l border-slate-200 bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <h2 className="text-lg font-bold text-slate-950">Membership Details</h2>
          <button className="rounded p-1 hover:bg-slate-50" onClick={onClose}>
            <X size={18} className="text-slate-500" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wide text-slate-500">User</h3>
            <p className="mt-1 text-base font-bold text-slate-950">
              {membership.user_name || membership.user_email || membership.user}
            </p>
            {membership.user_email && (
              <p className="text-sm text-slate-600">{membership.user_email}</p>
            )}
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wide text-slate-500">Role</h3>
              <p className="mt-1 text-sm font-bold text-slate-800">
                {membership.role_name || membership.role_code || membership.role}
              </p>
            </div>
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wide text-slate-500">Status</h3>
              <div className="mt-1">
                <MembershipStatusBadge status={membership.status} />
              </div>
            </div>
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wide text-slate-500">Unit</h3>
              <p className="mt-1 text-sm font-bold text-slate-800">
                {membership.unit_name || "No unit"}
              </p>
            </div>
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wide text-slate-500">Unit Restricted</h3>
              <p className="mt-1 text-sm font-bold text-slate-800">
                {membership.unit_restricted ? "Yes" : "No"}
              </p>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wide text-slate-500">Joined</h3>
              <p className="mt-1 text-sm text-slate-700">{formatDate(membership.joined_at)}</p>
            </div>
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wide text-slate-500">Last Active</h3>
              <p className="mt-1 text-sm text-slate-700">{formatDate(membership.last_active_at)}</p>
            </div>
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wide text-slate-500">Invited By</h3>
              <p className="mt-1 text-sm text-slate-700">{membership.invited_by_name || "N/A"}</p>
            </div>
          </div>

          {isActive && (
            <>
              <div className="border-t border-slate-100 pt-5">
                <h3 className="text-sm font-bold text-slate-950 mb-3">Change Role</h3>
                <div className="flex gap-2">
                  <select
                    className="h-10 flex-1 rounded border border-slate-200 bg-white px-3 text-sm"
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                  >
                    {roles.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.name}
                      </option>
                    ))}
                  </select>
                  <button
                    className="inline-flex h-10 items-center gap-2 rounded bg-slate-950 px-4 text-sm font-bold text-white hover:bg-slate-800 disabled:opacity-60"
                    disabled={selectedRole === membership.role}
                    onClick={() => onAction("change-role", { role: selectedRole })}
                    type="button"
                  >
                    <RotateCw size={14} />
                    Change
                  </button>
                </div>
              </div>

              <div className="border-t border-slate-100 pt-5">
                <h3 className="text-sm font-bold text-slate-950 mb-3">Change Unit</h3>
                <div className="flex gap-2">
                  <select
                    className="h-10 flex-1 rounded border border-slate-200 bg-white px-3 text-sm"
                    value={selectedUnit}
                    onChange={(e) => setSelectedUnit(e.target.value)}
                  >
                    <option value="">No unit</option>
                    {units.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.name}
                      </option>
                    ))}
                  </select>
                  <button
                    className="inline-flex h-10 items-center gap-2 rounded bg-slate-950 px-4 text-sm font-bold text-white hover:bg-slate-800 disabled:opacity-60"
                    disabled={selectedUnit === (membership.unit ?? "")}
                    onClick={() => onAction("change-unit", { unit: selectedUnit || null })}
                    type="button"
                  >
                    <RotateCw size={14} />
                    Change
                  </button>
                </div>
              </div>

              <div className="flex flex-wrap gap-2 border-t border-slate-100 pt-5">
                <button
                  className="inline-flex h-10 items-center gap-2 rounded border border-slate-200 px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                  onClick={() => onAction("toggle-restriction")}
                  type="button"
                >
                  {membership.unit_restricted ? (
                    <ToggleRight size={16} className="text-brand-deep" />
                  ) : (
                    <ToggleLeft size={16} />
                  )}
                  {membership.unit_restricted ? "Remove Unit Restriction" : "Restrict to Unit"}
                </button>
              </div>
            </>
          )}

          <div className="flex flex-wrap gap-2 border-t border-slate-100 pt-5">
            {isActive && (
              <button
                className="inline-flex h-10 items-center gap-2 rounded border border-rose-200 px-4 text-sm font-semibold text-rose-600 hover:bg-rose-50"
                onClick={() => onAction("suspend")}
                type="button"
              >
                <Ban size={14} />
                Suspend
              </button>
            )}
            {isSuspended && (
              <button
                className="inline-flex h-10 items-center gap-2 rounded border border-emerald-200 px-4 text-sm font-semibold text-emerald-600 hover:bg-emerald-50"
                onClick={() => onAction("reactivate")}
                type="button"
              >
                <ShieldCheck size={14} />
                Reactivate
              </button>
            )}
            {(isActive || isSuspended) && (
              <button
                className="inline-flex h-10 items-center gap-2 rounded border border-red-200 px-4 text-sm font-semibold text-red-600 hover:bg-red-50"
                onClick={() => {
                  if (confirm("Remove this user from the organization? This cannot be undone.")) {
                    onAction("remove");
                  }
                }}
                type="button"
              >
                <Trash2 size={14} />
                Remove
              </button>
            )}
          </div>

          {membership.permissions && membership.permissions.length > 0 && (
            <div className="border-t border-slate-100 pt-5">
              <h3 className="text-sm font-bold text-slate-950 mb-2">Effective Permissions</h3>
              <div className="flex flex-wrap gap-1">
                {membership.permissions.map((code) => (
                  <span
                    key={code}
                    className="rounded bg-slate-100 px-2 py-1 text-xs font-mono text-slate-700"
                  >
                    {code}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
