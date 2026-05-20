"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Mail, UserPlus } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { InviteEmployerUserModal } from "@/components/ui/invite-employer-user-modal";
import { InviteStatusBadge } from "@/components/ui/invite-status-badge";
import { listEmployers } from "@/lib/api/identity";
import { createEmployerInvite, listEmployerInvites, revokeEmployerInvite } from "@/lib/api/employer-management";
import { fetchUnits } from "@/lib/api/organizations";
import type { EmployerInvite } from "@/types/employer-management";

function label(value: string) {
  return value.replaceAll("_", " ");
}

function formatDate(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

function InviteRow({ invite, onRevoke, disabled }: { invite: EmployerInvite; onRevoke: (invite: EmployerInvite) => void; disabled?: boolean }) {
  return (
    <tr>
      <td className="border-b border-slate-50 py-4 pr-4">
        <p className="font-semibold text-slate-950">{invite.email}</p>
        <p className="mt-1 text-xs text-slate-500">{invite.phone || "No phone"}</p>
      </td>
      <td className="border-b border-slate-50 py-4 pr-4 text-sm font-semibold capitalize text-slate-700">{label(invite.employer_staff_role)}</td>
      <td className="border-b border-slate-50 py-4 pr-4 text-sm text-slate-600">{invite.unit_name || "Head office"}</td>
      <td className="border-b border-slate-50 py-4 pr-4"><InviteStatusBadge status={invite.status} /></td>
      <td className="border-b border-slate-50 py-4 pr-4 text-sm text-slate-600">{formatDate(invite.expires_at)}</td>
      <td className="border-b border-slate-50 py-4 text-right">
        <button
          className="h-9 rounded border border-slate-200 px-3 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          disabled={disabled || invite.status !== "pending"}
          onClick={() => onRevoke(invite)}
          type="button"
        >
          Revoke
        </button>
      </td>
    </tr>
  );
}

export default function Page() {
  const queryClient = useQueryClient();
  const [inviteOpen, setInviteOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");

  const employersQuery = useQuery({ queryKey: ["employers", "me"], queryFn: listEmployers });
  const employer = employersQuery.data?.[0];

  const unitsQuery = useQuery({
    queryKey: ["employer-units", employer?.organization],
    queryFn: () => fetchUnits(employer!.organization),
    enabled: Boolean(employer?.organization),
  });

  const invitesQuery = useQuery({
    queryKey: ["employer-invites", employer?.id, statusFilter],
    queryFn: () => listEmployerInvites(employer!.id, statusFilter ? { status: statusFilter } : undefined),
    enabled: Boolean(employer?.id),
  });

  const inviteMutation = useMutation({
    mutationFn: (payload: Parameters<typeof createEmployerInvite>[1]) => createEmployerInvite(employer!.id, payload),
    onSuccess: () => {
      setInviteOpen(false);
      queryClient.invalidateQueries({ queryKey: ["employer-invites", employer?.id] });
    },
  });

  const revokeMutation = useMutation({
    mutationFn: (invite: EmployerInvite) => revokeEmployerInvite(employer!.id, invite.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["employer-invites", employer?.id] }),
  });

  const invites = invitesQuery.data || [];
  const pending = invites.filter((invite) => invite.status === "pending").length;
  const accepted = invites.filter((invite) => invite.status === "accepted").length;

  return (
    <PortalShell role="employer" title="Employer Invites" description="Track internal user invitations, statuses, expiry dates, and revoked invites.">
      <div className="grid gap-6">
        <section className="grid gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-brand-deep">Invites</p>
            <p className="mt-2 text-3xl font-bold text-slate-950">{invites.length}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-brand-deep">Pending</p>
            <p className="mt-2 text-3xl font-bold text-amber-700">{pending}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-brand-deep">Accepted</p>
            <p className="mt-2 text-3xl font-bold text-brand-deep">{accepted}</p>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-2">
              <Mail className="text-brand-deep" size={18} />
              <h2 className="text-base font-bold text-slate-950">Invite List</h2>
            </div>
            <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep" onClick={() => setInviteOpen(true)} type="button">
              <UserPlus size={16} />
              Invite User
            </button>
          </div>
          <select className="mb-4 h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="accepted">Accepted</option>
            <option value="expired">Expired</option>
            <option value="revoked">Revoked</option>
          </select>
          {invitesQuery.isError ? <p className="rounded bg-rose-50 p-3 text-sm font-semibold text-rose-700">Could not load invites.</p> : null}
          <div className="overflow-x-auto">
            <table className="w-full min-w-[820px] text-left text-sm">
              <thead className="text-xs font-bold uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="border-b border-slate-100 py-2 pr-4">Recipient</th>
                  <th className="border-b border-slate-100 py-2 pr-4">Role</th>
                  <th className="border-b border-slate-100 py-2 pr-4">Unit</th>
                  <th className="border-b border-slate-100 py-2 pr-4">Status</th>
                  <th className="border-b border-slate-100 py-2 pr-4">Expires</th>
                  <th className="border-b border-slate-100 py-2 text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {invites.map((invite) => <InviteRow disabled={revokeMutation.isPending} invite={invite} key={invite.id} onRevoke={(target) => revokeMutation.mutate(target)} />)}
                {!invites.length && !invitesQuery.isFetching ? <tr><td className="py-8 text-center text-slate-500" colSpan={6}>No invites match the current filter.</td></tr> : null}
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
