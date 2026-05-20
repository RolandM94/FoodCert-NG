"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Mail, UserPlus } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { InviteStatusBadge } from "@/components/ui/invite-status-badge";
import { MINISTRY_STAFF_ROLE_LABELS } from "@/lib/permissions/roles";
import { createStateInvite, fetchStateInvites, fetchStateUnits, revokeStateInvite, type StateInvitePayload } from "@/lib/api/state";
import type { MinistryStaffRole } from "@/types/auth";

const STATE_ROLES: { value: MinistryStaffRole; label: string; role: StateInvitePayload["role"] }[] = [
  { value: "state_super_admin", label: MINISTRY_STAFF_ROLE_LABELS.state_super_admin, role: "state_admin" },
  { value: "food_safety_officer", label: MINISTRY_STAFF_ROLE_LABELS.food_safety_officer, role: "state_admin" },
  { value: "certificate_verification_officer", label: MINISTRY_STAFF_ROLE_LABELS.certificate_verification_officer, role: "state_admin" },
  { value: "facility_accreditation_officer", label: MINISTRY_STAFF_ROLE_LABELS.facility_accreditation_officer, role: "state_admin" },
  { value: "policy_finance_officer", label: MINISTRY_STAFF_ROLE_LABELS.policy_finance_officer, role: "state_admin" },
  { value: "inspectorate_coordinator", label: MINISTRY_STAFF_ROLE_LABELS.inspectorate_coordinator, role: "state_admin" },
  { value: "lga_officer", label: MINISTRY_STAFF_ROLE_LABELS.lga_officer, role: "state_admin" },
];

function formatDate(value?: string) {
  if (!value) return "Not set";
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

export default function Page() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<StateInvitePayload>({
    email: "",
    role: "state_admin",
    ministry_staff_role: "food_safety_officer",
    phone: "",
    message: "",
  });

  const unitsQuery = useQuery({ queryKey: ["state-units"], queryFn: fetchStateUnits });
  const invitesQuery = useQuery({ queryKey: ["state-invites"], queryFn: fetchStateInvites });

  const createMutation = useMutation({
    mutationFn: createStateInvite,
    onSuccess: () => {
      setOpen(false);
      setForm({ email: "", role: "state_admin", ministry_staff_role: "food_safety_officer", phone: "", message: "" });
      queryClient.invalidateQueries({ queryKey: ["state-invites"] });
    },
  });

  const revokeMutation = useMutation({
    mutationFn: revokeStateInvite,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["state-invites"] }),
  });

  const selectedRole = STATE_ROLES.find((role) => role.value === form.ministry_staff_role) || STATE_ROLES[0];

  return (
    <PortalShell role="state_admin" title="State Invites" description="Invite ministry officers, inspectors, and unit-scoped staff.">
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-2">
            <Mail className="text-brand-deep" size={18} />
            <h2 className="text-base font-bold text-slate-950">Invite List</h2>
          </div>
          <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep" onClick={() => setOpen(true)} type="button">
            <UserPlus size={16} />
            Invite User
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[920px] text-left text-sm">
            <thead className="text-xs font-bold uppercase tracking-wide text-slate-500">
              <tr>
                <th className="border-b border-slate-100 py-2 pr-4">Recipient</th>
                <th className="border-b border-slate-100 py-2 pr-4">Ministry Role</th>
                <th className="border-b border-slate-100 py-2 pr-4">Unit</th>
                <th className="border-b border-slate-100 py-2 pr-4">Status</th>
                <th className="border-b border-slate-100 py-2 pr-4">Expires</th>
                <th className="border-b border-slate-100 py-2 text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {(invitesQuery.data || []).map((invite) => (
                <tr key={invite.id}>
                  <td className="border-b border-slate-50 py-4 pr-4">
                    <p className="font-semibold text-slate-950">{invite.email}</p>
                    <p className="mt-1 text-xs text-slate-500">{invite.phone || "No phone"}</p>
                  </td>
                  <td className="border-b border-slate-50 py-4 pr-4 text-sm font-semibold text-slate-700">
                    {invite.ministry_staff_role ? MINISTRY_STAFF_ROLE_LABELS[invite.ministry_staff_role as MinistryStaffRole] : invite.role.replaceAll("_", " ")}
                  </td>
                  <td className="border-b border-slate-50 py-4 pr-4 text-sm text-slate-600">{invite.unit_name || "State-wide"}</td>
                  <td className="border-b border-slate-50 py-4 pr-4"><InviteStatusBadge status={invite.status} /></td>
                  <td className="border-b border-slate-50 py-4 pr-4 text-sm text-slate-600">{formatDate(invite.expires_at)}</td>
                  <td className="border-b border-slate-50 py-4 text-right">
                    <button
                      className="h-9 rounded border border-slate-200 px-3 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                      disabled={revokeMutation.isPending || invite.status !== "pending"}
                      onClick={() => revokeMutation.mutate(invite.id)}
                      type="button"
                    >
                      Revoke
                    </button>
                  </td>
                </tr>
              ))}
              {!invitesQuery.isFetching && !(invitesQuery.data || []).length ? <tr><td className="py-8 text-center text-slate-500" colSpan={6}>No invites have been sent yet.</td></tr> : null}
            </tbody>
          </table>
        </div>
      </section>

      {open ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
          <div className="w-full max-w-lg rounded-lg border border-slate-200 bg-white shadow-xl">
            <div className="border-b border-slate-100 px-6 py-4">
              <h2 className="text-lg font-bold text-slate-950">Invite State Ministry User</h2>
            </div>
            <form
              className="grid gap-4 p-6"
              onSubmit={(event) => {
                event.preventDefault();
                createMutation.mutate({ ...form, role: selectedRole.role });
              }}
            >
              <label className="grid gap-1 text-sm font-semibold text-slate-700">
                Email
                <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" required type="email" value={form.email} onChange={(event) => setForm((prev) => ({ ...prev, email: event.target.value }))} />
              </label>
              <label className="grid gap-1 text-sm font-semibold text-slate-700">
                Ministry role
                <select className="h-10 rounded border border-slate-200 bg-white px-3" value={form.ministry_staff_role} onChange={(event) => setForm((prev) => ({ ...prev, ministry_staff_role: event.target.value as MinistryStaffRole }))}>
                  {STATE_ROLES.map((role) => <option key={role.value} value={role.value}>{role.label}</option>)}
                </select>
              </label>
              <label className="grid gap-1 text-sm font-semibold text-slate-700">
                Unit
                <select className="h-10 rounded border border-slate-200 bg-white px-3" value={form.unit || ""} onChange={(event) => setForm((prev) => ({ ...prev, unit: event.target.value || undefined }))}>
                  <option value="">State-wide</option>
                  {(unitsQuery.data || []).map((unit) => <option key={unit.id} value={unit.id}>{unit.name}</option>)}
                </select>
              </label>
              <label className="grid gap-1 text-sm font-semibold text-slate-700">
                Phone
                <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" value={form.phone || ""} onChange={(event) => setForm((prev) => ({ ...prev, phone: event.target.value }))} />
              </label>
              <label className="grid gap-1 text-sm font-semibold text-slate-700">
                Message
                <textarea className="rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm" rows={2} value={form.message || ""} onChange={(event) => setForm((prev) => ({ ...prev, message: event.target.value }))} />
              </label>
              {createMutation.isError ? <p className="rounded bg-red-50 px-3 py-2 text-sm font-semibold text-red-700">Could not send invite. Check the selected role and unit.</p> : null}
              <div className="flex items-center justify-end gap-3 pt-2">
                <button className="h-10 rounded border border-slate-200 px-4 text-sm font-semibold text-slate-600 hover:bg-slate-50" onClick={() => setOpen(false)} type="button">Cancel</button>
                <button className="h-10 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep disabled:opacity-60" disabled={createMutation.isPending} type="submit">Send Invite</button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </PortalShell>
  );
}
