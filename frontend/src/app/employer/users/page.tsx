"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ShieldCheck, UserPlus, UsersRound } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { InviteEmployerUserModal } from "@/components/ui/invite-employer-user-modal";
import { listEmployers } from "@/lib/api/identity";
import { createEmployerInvite, listEmployerUsers, updateEmployerUser } from "@/lib/api/employer-management";
import { fetchUnits } from "@/lib/api/organizations";
import type { EmployerStaffRole, EmployerUser } from "@/types/employer-management";
import type { UserStatus } from "@/types/auth";

function label(value: string) {
  return value.replaceAll("_", " ");
}

function RoleBadge({ role }: { role: EmployerStaffRole }) {
  const tone = role === "branch_manager" ? "bg-sky-50 text-sky-700 ring-sky-200" : role === "finance_user" ? "bg-amber-50 text-amber-700 ring-amber-200" : "bg-emerald-50 text-brand-deep ring-emerald-200";
  return <span className={`rounded px-2 py-1 text-xs font-bold capitalize ring-1 ${tone}`}>{label(role)}</span>;
}

function StatusBadge({ status }: { status: UserStatus }) {
  const tone = status === "active" ? "bg-emerald-50 text-brand-deep ring-emerald-200" : status === "inactive" ? "bg-slate-100 text-slate-700 ring-slate-200" : "bg-rose-50 text-rose-700 ring-rose-200";
  return <span className={`rounded px-2 py-1 text-xs font-bold capitalize ring-1 ${tone}`}>{status}</span>;
}

function UserRow({
  user,
  onStatus,
}: {
  user: EmployerUser;
  onStatus: (user: EmployerUser, status: UserStatus) => void;
}) {
  return (
    <tr>
      <td className="border-b border-slate-50 py-4 pr-4">
        <p className="font-semibold text-slate-950">{user.full_name || user.email}</p>
        <p className="mt-1 text-xs text-slate-500">{user.email}</p>
      </td>
      <td className="border-b border-slate-50 py-4 pr-4"><RoleBadge role={user.employer_staff_role} /></td>
      <td className="border-b border-slate-50 py-4 pr-4 text-sm text-slate-600">{user.unit_name || "Head office"}</td>
      <td className="border-b border-slate-50 py-4 pr-4"><StatusBadge status={user.status} /></td>
      <td className="border-b border-slate-50 py-4 text-right">
        <button
          className="h-9 rounded border border-slate-200 px-3 text-sm font-bold text-slate-700 hover:bg-slate-50"
          onClick={() => onStatus(user, user.status === "active" ? "inactive" : "active")}
          type="button"
        >
          {user.status === "active" ? "Deactivate" : "Activate"}
        </button>
      </td>
    </tr>
  );
}

export default function Page() {
  const queryClient = useQueryClient();
  const [inviteOpen, setInviteOpen] = useState(false);
  const [roleFilter, setRoleFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const employersQuery = useQuery({ queryKey: ["employers", "me"], queryFn: listEmployers });
  const employer = employersQuery.data?.[0];

  const unitsQuery = useQuery({
    queryKey: ["employer-units", employer?.organization],
    queryFn: () => fetchUnits(employer!.organization),
    enabled: Boolean(employer?.organization),
  });

  const filters = useMemo(() => {
    const next: Record<string, string> = {};
    if (roleFilter) next.employer_staff_role = roleFilter;
    if (statusFilter) next.status = statusFilter;
    return next;
  }, [roleFilter, statusFilter]);

  const usersQuery = useQuery({
    queryKey: ["employer-users", employer?.id, filters],
    queryFn: () => listEmployerUsers(employer!.id, filters),
    enabled: Boolean(employer?.id),
  });

  const inviteMutation = useMutation({
    mutationFn: (payload: Parameters<typeof createEmployerInvite>[1]) => createEmployerInvite(employer!.id, payload),
    onSuccess: () => {
      setInviteOpen(false);
      queryClient.invalidateQueries({ queryKey: ["employer-users", employer?.id] });
      queryClient.invalidateQueries({ queryKey: ["employer-invites", employer?.id] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ user, status }: { user: EmployerUser; status: UserStatus }) => updateEmployerUser(employer!.id, user.id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["employer-users", employer?.id] }),
  });

  const users = usersQuery.data || [];
  const activeUsers = users.filter((user) => user.status === "active").length;
  const branchManagers = users.filter((user) => user.employer_staff_role === "branch_manager").length;

  return (
    <PortalShell role="employer" title="Employer Users" description="Manage internal users, branch managers, compliance officers, and finance users.">
      <div className="grid gap-6">
        <section className="grid gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-brand-deep">Internal Users</p>
            <p className="mt-2 text-3xl font-bold text-slate-950">{users.length}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-brand-deep">Active</p>
            <p className="mt-2 text-3xl font-bold text-brand-deep">{activeUsers}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-brand-deep">Branch Managers</p>
            <p className="mt-2 text-3xl font-bold text-sky-700">{branchManagers}</p>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-2">
              <UsersRound className="text-brand-deep" size={18} />
              <h2 className="text-base font-bold text-slate-950">User List</h2>
            </div>
            <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep" onClick={() => setInviteOpen(true)} type="button">
              <UserPlus size={16} />
              Invite User
            </button>
          </div>
          <div className="mb-4 grid gap-3 md:grid-cols-2">
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={roleFilter} onChange={(event) => setRoleFilter(event.target.value)}>
              <option value="">All roles</option>
              <option value="compliance_officer">Compliance officer</option>
              <option value="branch_manager">Branch manager</option>
              <option value="finance_user">Finance user</option>
              <option value="employer_admin">Employer admin</option>
            </select>
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              <option value="">All statuses</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="suspended">Suspended</option>
            </select>
          </div>
          {usersQuery.isError ? <p className="rounded bg-rose-50 p-3 text-sm font-semibold text-rose-700">Could not load employer users.</p> : null}
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="text-xs font-bold uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="border-b border-slate-100 py-2 pr-4">User</th>
                  <th className="border-b border-slate-100 py-2 pr-4">Role</th>
                  <th className="border-b border-slate-100 py-2 pr-4">Unit</th>
                  <th className="border-b border-slate-100 py-2 pr-4">Status</th>
                  <th className="border-b border-slate-100 py-2 text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => <UserRow key={user.id} user={user} onStatus={(target, status) => updateMutation.mutate({ user: target, status })} />)}
                {!users.length && !usersQuery.isFetching ? (
                  <tr><td className="py-8 text-center text-slate-500" colSpan={5}><ShieldCheck className="mx-auto mb-2 text-slate-300" size={24} />No users match the current filters.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>
      </div>
      <InviteEmployerUserModal
        disabled={inviteMutation.isPending}
        error={inviteMutation.isError ? "Could not send invite. Check role and branch selection." : null}
        onClose={() => setInviteOpen(false)}
        onSubmit={(payload) => inviteMutation.mutate(payload)}
        open={inviteOpen}
        units={unitsQuery.data || []}
      />
    </PortalShell>
  );
}
