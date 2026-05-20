"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Mail, UserPlus } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { InviteStatusBadge } from "@/components/ui/invite-status-badge";
import { InviteUserModal } from "@/components/ui/invite-user-modal";
import { createInvite, fetchInvites, fetchUnits, revokeInvite } from "@/lib/api/organizations";
import type { UserRole } from "@/types/auth";
import type { UserInvite } from "@/types/organizations";

function formatDate(value?: string) {
  if (!value) return "Not set";
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

function getOrganizationId() {
  const token = typeof window !== "undefined" ? localStorage.getItem("foodcert_access_token") : null;
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.organization_id || payload.organization || null;
  } catch {
    return null;
  }
}

function InviteRow({ invite, disabled, onRevoke }: { invite: UserInvite; disabled?: boolean; onRevoke: (invite: UserInvite) => void }) {
  return (
    <tr>
      <td className="border-b border-slate-50 py-4 pr-4">
        <p className="font-semibold text-slate-950">{invite.email}</p>
        <p className="mt-1 text-xs text-slate-500">{invite.phone || "No phone"}</p>
      </td>
      <td className="border-b border-slate-50 py-4 pr-4 text-sm font-semibold capitalize text-slate-700">{invite.role.replaceAll("_", " ")}</td>
      <td className="border-b border-slate-50 py-4 pr-4 text-sm text-slate-600">{invite.unit_name || "Organization-wide"}</td>
      <td className="border-b border-slate-50 py-4 pr-4 text-sm text-slate-600">{invite.invited_by_name || invite.invited_by_email || "Unknown"}</td>
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

export function OrganizationInvitesPage({
  role,
  title,
  description,
}: {
  role: UserRole;
  title: string;
  description: string;
}) {
  const queryClient = useQueryClient();
  const [orgId, setOrgId] = useState<string | null>(null);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => setOrgId(getOrganizationId()), []);

  const unitsQuery = useQuery({
    queryKey: ["organization-units", orgId],
    queryFn: () => fetchUnits(orgId!),
    enabled: Boolean(orgId),
  });

  const invitesQuery = useQuery({
    queryKey: ["organization-invites", orgId],
    queryFn: () => fetchInvites(orgId!),
    enabled: Boolean(orgId),
  });

  const inviteMutation = useMutation({
    mutationFn: (payload: { email: string; role: UserRole; unit?: string; phone?: string; message?: string; expires_at?: string }) => createInvite(orgId!, payload),
    onSuccess: () => {
      setInviteOpen(false);
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["organization-invites", orgId] });
    },
    onError: () => setError("Could not send invite. Check role, unit, and permissions."),
  });

  const revokeMutation = useMutation({
    mutationFn: (invite: UserInvite) => revokeInvite(orgId!, invite.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["organization-invites", orgId] }),
  });

  const invites = invitesQuery.data || [];

  return (
    <PortalShell role={role} title={title} description={description}>
      <div className="grid gap-6">
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

          {invitesQuery.isError ? <p className="rounded bg-rose-50 p-3 text-sm font-semibold text-rose-700">Could not load invites.</p> : null}
          <div className="overflow-x-auto">
            <table className="w-full min-w-[900px] text-left text-sm">
              <thead className="text-xs font-bold uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="border-b border-slate-100 py-2 pr-4">Recipient</th>
                  <th className="border-b border-slate-100 py-2 pr-4">Role</th>
                  <th className="border-b border-slate-100 py-2 pr-4">Unit</th>
                  <th className="border-b border-slate-100 py-2 pr-4">Invited By</th>
                  <th className="border-b border-slate-100 py-2 pr-4">Status</th>
                  <th className="border-b border-slate-100 py-2 pr-4">Expires</th>
                  <th className="border-b border-slate-100 py-2 text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {invites.map((invite) => <InviteRow disabled={revokeMutation.isPending} invite={invite} key={invite.id} onRevoke={(target) => revokeMutation.mutate(target)} />)}
                {!invites.length && !invitesQuery.isFetching ? <tr><td className="py-8 text-center text-slate-500" colSpan={7}>No invites have been sent yet.</td></tr> : null}
              </tbody>
            </table>
          </div>
        </section>
      </div>
      <InviteUserModal
        error={error}
        onClose={() => setInviteOpen(false)}
        onSubmit={(payload) => inviteMutation.mutate(payload)}
        open={inviteOpen}
        units={unitsQuery.data || []}
      />
    </PortalShell>
  );
}
