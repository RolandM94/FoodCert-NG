"use client";

import { useState } from "react";
import { Send, X } from "lucide-react";
import type { UserRole } from "@/types/auth";
import type { OrganizationUnit } from "@/types/organizations";

const ROLE_OPTIONS: { value: UserRole; label: string }[] = [
  { value: "state_admin", label: "State Ministry Admin" },
  { value: "inspector", label: "Inspector" },
  { value: "facility_admin", label: "Facility Admin" },
  { value: "doctor", label: "Doctor" },
  { value: "lab_staff", label: "Lab Staff" },
  { value: "employer", label: "Employer / Branch Manager" },
  { value: "food_handler", label: "Food Handler" },
];

type InviteForm = {
  email: string;
  role: UserRole;
  unit?: string;
  unit_restricted: boolean;
  phone: string;
  message: string;
  expires_at?: string;
};

export function InviteUserModal({
  open,
  onClose,
  onSubmit,
  units,
  preselectUnit,
  error,
}: {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: InviteForm) => void;
  units?: OrganizationUnit[];
  preselectUnit?: string;
  error?: string | null;
}) {
  const [form, setForm] = useState<InviteForm>({
    email: "",
    role: "food_handler",
    unit: preselectUnit ?? undefined,
    unit_restricted: false,
    phone: "",
    message: "",
    expires_at: "",
  });

  if (!open) return null;

  const set = (field: keyof InviteForm, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
      <div className="w-full max-w-lg rounded-lg border border-slate-200 bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <h2 className="text-lg font-bold text-slate-950">Invite User</h2>
          <button className="rounded p-1 hover:bg-slate-50" onClick={onClose}>
            <X size={18} className="text-slate-500" />
          </button>
        </div>

        <form
          className="grid gap-4 p-6"
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit({
              ...form,
              unit_restricted: form.unit_restricted,
              expires_at: form.expires_at ? new Date(form.expires_at).toISOString() : undefined,
            });
          }}
        >
          <label className="grid gap-1 text-sm font-semibold text-slate-700">
            Email <span className="text-red-500">*</span>
            <input
              className="h-10 rounded border border-slate-200 bg-slate-50 px-3"
              type="email"
              required
              value={form.email}
              onChange={(e) => set("email", e.target.value)}
              placeholder="user@example.com"
            />
          </label>

          <label className="grid gap-1 text-sm font-semibold text-slate-700">
            Role <span className="text-red-500">*</span>
            <select
              className="h-10 rounded border border-slate-200 bg-white px-3"
              value={form.role}
              onChange={(e) => set("role", e.target.value)}
            >
              {ROLE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>

          {units && units.length > 0 && (
            <>
              <label className="grid gap-1 text-sm font-semibold text-slate-700">
                Unit
                <select
                  className="h-10 rounded border border-slate-200 bg-white px-3"
                  value={form.unit ?? ""}
                  onChange={(e) => set("unit", e.target.value)}
                >
                  <option value="">No specific unit</option>
                  {units.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name}
                    </option>
                  ))}
                </select>
              </label>
              {form.unit && (
                <label className="flex items-center gap-2 text-sm font-semibold text-slate-700">
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-slate-300 text-brand-green focus:ring-brand-green"
                    checked={form.unit_restricted}
                    onChange={(e) => setForm((prev) => ({ ...prev, unit_restricted: e.target.checked }))}
                  />
                  Restrict this user to the selected unit
                </label>
              )}
            </>
          )}

          <label className="grid gap-1 text-sm font-semibold text-slate-700">
            Phone (optional)
            <input
              className="h-10 rounded border border-slate-200 bg-slate-50 px-3"
              value={form.phone}
              onChange={(e) => set("phone", e.target.value)}
              placeholder="08030000000"
            />
          </label>

          <label className="grid gap-1 text-sm font-semibold text-slate-700">
            Message (optional)
            <textarea
              className="rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm"
              rows={2}
              value={form.message}
              onChange={(e) => set("message", e.target.value)}
              placeholder="Welcome message to the recipient"
            />
          </label>

          <label className="grid gap-1 text-sm font-semibold text-slate-700">
            Expiry date (optional)
            <input
              className="h-10 rounded border border-slate-200 bg-slate-50 px-3"
              type="datetime-local"
              value={form.expires_at ?? ""}
              onChange={(e) => set("expires_at", e.target.value)}
            />
          </label>

          {error && (
            <p className="rounded bg-red-50 px-3 py-2 text-sm font-semibold text-red-700">{error}</p>
          )}

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              className="inline-flex h-10 items-center gap-2 rounded border border-slate-200 px-4 text-sm font-semibold text-slate-600 hover:bg-slate-50"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="inline-flex h-10 items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep"
            >
              <Send aria-hidden="true" size={16} />
              Send Invite
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
