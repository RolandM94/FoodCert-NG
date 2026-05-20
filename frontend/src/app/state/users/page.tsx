"use client";

import { useQuery } from "@tanstack/react-query";
import { Users } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { fetchStateUsers } from "@/lib/api/state";
import { MINISTRY_STAFF_ROLE_LABELS, ROLE_LABELS } from "@/lib/permissions/roles";
import type { MinistryStaffRole } from "@/types/auth";

function fullName(first?: string, last?: string, email?: string) {
  const name = [first, last].filter(Boolean).join(" ");
  return name || email || "Unnamed user";
}

export default function Page() {
  const usersQuery = useQuery({ queryKey: ["state-users"], queryFn: fetchStateUsers });
  const users = usersQuery.data || [];

  return (
    <PortalShell role="state_admin" title="State users" description="Manage state ministry users, inspectors, and scoped access.">
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <Users className="text-brand-deep" size={18} />
          <h2 className="text-base font-bold text-slate-950">Ministry Users</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead className="text-xs font-bold uppercase tracking-wide text-slate-500">
              <tr>
                <th className="border-b border-slate-100 py-2 pr-4">User</th>
                <th className="border-b border-slate-100 py-2 pr-4">Platform Role</th>
                <th className="border-b border-slate-100 py-2 pr-4">Ministry Role</th>
                <th className="border-b border-slate-100 py-2 pr-4">Unit</th>
                <th className="border-b border-slate-100 py-2 pr-4">Scope</th>
                <th className="border-b border-slate-100 py-2 pr-4">Status</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => {
                const ministryRole = user.ministry_profile?.sub_role;
                return (
                  <tr key={user.id}>
                    <td className="border-b border-slate-50 py-4 pr-4">
                      <p className="font-semibold text-slate-950">{fullName(user.first_name, user.last_name, user.email)}</p>
                      <p className="mt-1 text-xs text-slate-500">{user.email}</p>
                    </td>
                    <td className="border-b border-slate-50 py-4 pr-4 text-sm font-semibold text-slate-700">{ROLE_LABELS[user.role]}</td>
                    <td className="border-b border-slate-50 py-4 pr-4 text-sm text-slate-600">
                      {ministryRole ? MINISTRY_STAFF_ROLE_LABELS[ministryRole as MinistryStaffRole] : "State-wide admin"}
                    </td>
                    <td className="border-b border-slate-50 py-4 pr-4 text-sm text-slate-600">{user.ministry_profile?.unit_name || user.unit_name || "No unit"}</td>
                    <td className="border-b border-slate-50 py-4 pr-4 text-sm text-slate-600">{user.ministry_profile?.lga_name || user.state_name || "State"}</td>
                    <td className="border-b border-slate-50 py-4 pr-4">
                      <span className="rounded bg-emerald-50 px-2 py-1 text-xs font-bold capitalize text-emerald-700">{user.status}</span>
                    </td>
                  </tr>
                );
              })}
              {!usersQuery.isFetching && !users.length ? <tr><td className="py-8 text-center text-slate-500" colSpan={6}>No state ministry users found.</td></tr> : null}
            </tbody>
          </table>
        </div>
      </section>
    </PortalShell>
  );
}
