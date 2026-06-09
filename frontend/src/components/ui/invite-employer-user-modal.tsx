"use client";

import { useEffect, useState } from "react";
import { Send, X } from "lucide-react";
import type { EmployerStaffRole } from "@/types/employer-management";
import type { OrganizationUnit } from "@/types/organizations";

const roles: Array<{ value: EmployerStaffRole; label: string }> = [
  { value: "compliance_officer", label: "Compliance Officer" },
  { value: "branch_manager", label: "Branch Manager" },
  { value: "finance_user", label: "Finance User" },
];

export function InviteEmployerUserModal({
  open,
  onClose,
  onSubmit,
  units,
  defaultUnit,
  error,
  disabled,
}: {
  open: boolean;
  onClose: () => void;
  onSubmit: (payload: { email: string; phone?: string; employer_staff_role: EmployerStaffRole; unit?: string; message?: string }) => void;
  units: OrganizationUnit[];
  defaultUnit?: string;
  error?: string | null;
  disabled?: boolean;
}) {
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [staffRole, setStaffRole] = useState<EmployerStaffRole>("compliance_officer");
  const [unit, setUnit] = useState(defaultUnit || "");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (defaultUnit) {
      setStaffRole("branch_manager");
      setUnit(defaultUnit);
    }
  }, [defaultUnit]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-neutral-900/50 p-4">
      <div className="w-full max-w-lg rounded-lg border border-neutral-200 bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-neutral-100 px-6 py-4">
          <h2 className="text-lg font-bold text-neutral-900">Invite Employer User</h2>
          <button className="rounded p-1 hover:bg-neutral-50" onClick={onClose} type="button">
            <X size={18} className="text-neutral-500" />
          </button>
        </div>

        <form
          className="grid gap-4 p-6"
          onSubmit={(event) => {
            event.preventDefault();
            onSubmit({
              email,
              phone,
              employer_staff_role: staffRole,
              unit: staffRole === "branch_manager" ? unit : undefined,
              message,
            });
          }}
        >
          <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
            Email
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3" required type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
          </label>

          <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
            Role
            <select className="h-10 rounded border border-neutral-200 bg-white px-3" value={staffRole} onChange={(event) => setStaffRole(event.target.value as EmployerStaffRole)}>
              {roles.map((role) => <option key={role.value} value={role.value}>{role.label}</option>)}
            </select>
          </label>

          {staffRole === "branch_manager" ? (
            <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
              Branch
              <select className="h-10 rounded border border-neutral-200 bg-white px-3" required value={unit} onChange={(event) => setUnit(event.target.value)}>
                <option value="">Select branch</option>
                {units.map((option) => <option key={option.id} value={option.id}>{option.name}</option>)}
              </select>
            </label>
          ) : null}

          <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
            Phone
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3" value={phone} onChange={(event) => setPhone(event.target.value)} />
          </label>

          <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
            Message
            <textarea className="rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm" rows={3} value={message} onChange={(event) => setMessage(event.target.value)} />
          </label>

          {error ? <p className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</p> : null}

          <div className="flex items-center justify-end gap-3">
            <button className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50" onClick={onClose} type="button">Cancel</button>
            <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60" disabled={disabled} type="submit">
              <Send size={16} />
              {disabled ? "Sending..." : "Send Invite"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
