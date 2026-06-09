"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Search, UserPlus, ChevronRight } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { MembershipStatusBadge } from "@/components/ui/membership-status-badge";
import { UserMembershipDetailDrawer } from "@/components/ui/user-membership-detail-drawer";
import { InviteUserModal } from "@/components/ui/invite-user-modal";
import {
  fetchMemberships,
  fetchMembership,
  suspendMembership,
  reactivateMembership,
  removeMembership,
  changeMembershipRole,
  changeMembershipUnit,
  toggleMembershipUnitRestriction,
  fetchUnits,
  fetchRolesByOrganizationType,
  fetchOrganization,
  createInvite,
} from "@/lib/api/organizations";
import { getApiErrorMessage } from "@/lib/api/client";
import type { UserRole } from "@/types/auth";
import type { OrganizationMembership, Organization, StakeholderRole, OrganizationUnit } from "@/types/organizations";

function formatDate(value?: string) {
  if (!value) return "N/A";
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

export default function OrganizationUsersPage() {
  const params = useParams<{ id: string }>();
  const organizationId = params.id;
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedMembership, setSelectedMembership] = useState<OrganizationMembership | null>(null);
  const [selectedMembershipDetail, setSelectedMembershipDetail] = useState<OrganizationMembership | null>(null);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: organization } = useQuery({
    queryKey: ["organization", organizationId],
    queryFn: () => fetchOrganization(organizationId),
    enabled: Boolean(organizationId),
  });

  const { data: memberships = [], isLoading } = useQuery({
    queryKey: ["memberships", organizationId],
    queryFn: () => fetchMemberships(organizationId),
    enabled: Boolean(organizationId),
  });

  const { data: units = [] } = useQuery({
    queryKey: ["units", organizationId],
    queryFn: () => fetchUnits(organizationId),
    enabled: Boolean(organizationId),
  });

  const { data: roles = [] } = useQuery({
    queryKey: ["roles-by-type", organization?.organization_type],
    queryFn: () => fetchRolesByOrganizationType(organization!.organization_type),
    enabled: Boolean(organization?.organization_type),
  });

  const loadDetail = useCallback(async (membership: OrganizationMembership) => {
    setSelectedMembership(membership);
    setError(null);
    try {
      const detail = await fetchMembership(organizationId, membership.id);
      setSelectedMembershipDetail(detail);
    } catch {
      setSelectedMembership(membership);
    }
  }, [organizationId]);

  const inviteMutation = useMutation({
    mutationFn: (data: { email: string; role: UserRole; unit?: string; unit_restricted?: boolean; phone?: string; message?: string; expires_at?: string }) =>
      createInvite(organizationId, data),
    onSuccess: () => {
      setInviteOpen(false);
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["memberships", organizationId] });
    },
    onError: (err) => setError(getApiErrorMessage(err, "Could not send invite.")),
  });

  async function handleAction(action: string, payload?: Record<string, unknown>) {
    if (!selectedMembership) return;
    setError(null);
    try {
      switch (action) {
        case "suspend":
          await suspendMembership(organizationId, selectedMembership.id);
          break;
        case "reactivate":
          await reactivateMembership(organizationId, selectedMembership.id);
          break;
        case "remove":
          await removeMembership(organizationId, selectedMembership.id);
          setSelectedMembership(null);
          setSelectedMembershipDetail(null);
          break;
        case "change-role":
          if (payload?.role) await changeMembershipRole(organizationId, selectedMembership.id, payload.role as string);
          break;
        case "change-unit":
          await changeMembershipUnit(organizationId, selectedMembership.id, (payload?.unit as string) || null, payload?.unit_restricted as boolean | undefined);
          break;
        case "toggle-restriction":
          await toggleMembershipUnitRestriction(organizationId, selectedMembership.id);
          break;
      }
      queryClient.invalidateQueries({ queryKey: ["memberships", organizationId] });
      if (selectedMembership) {
        const detail = await fetchMembership(organizationId, selectedMembership.id);
        setSelectedMembershipDetail(detail);
      }
    } catch (err) {
      setError(getApiErrorMessage(err, `Failed to ${action}.`));
    }
  }

  const filtered = memberships.filter((m) => {
    if (search) {
      const q = search.toLowerCase();
      const name = (m.user_name || m.user_email || "").toLowerCase();
      if (!name.includes(q) && !m.role_name?.toLowerCase().includes(q)) return false;
    }
    if (statusFilter && m.status !== statusFilter) return false;
    return true;
  });

  return (
    <PortalShell
      role="super_admin"
      title="Users & Memberships"
      description="Manage organization members, assign roles, change units, and control access restrictions."
    >
      <div className="space-y-4">
        {error ? (
          <div className="rounded border border-danger-100 bg-danger-50 px-4 py-3 text-sm font-semibold text-danger-700">
            {error}
          </div>
        ) : null}

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-1 gap-2">
            <label className="relative flex-1 max-w-sm">
              <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" size={16} />
              <input
                className="h-10 w-full rounded border border-neutral-200 bg-white pl-9 pr-3 text-sm outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-600/20"
                placeholder="Search by name, email, or role..."
                type="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </label>
            <select
              className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm text-neutral-700"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All statuses</option>
              <option value="active">Active</option>
              <option value="invited">Invited</option>
              <option value="suspended">Suspended</option>
              <option value="removed">Removed</option>
            </select>
          </div>
          <button
            className="inline-flex h-10 items-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700"
            onClick={() => setInviteOpen(true)}
            type="button"
          >
            <UserPlus size={16} />
            Invite User
          </button>
        </div>

        <section className="overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-neutral-200 text-sm">
              <thead className="bg-neutral-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-neutral-500">Name</th>
                  <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-neutral-500">Email</th>
                  <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-neutral-500">Role</th>
                  <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-neutral-500">Unit</th>
                  <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-neutral-500">Restricted</th>
                  <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-neutral-500">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-neutral-500">Last Active</th>
                  <th className="px-4 py-3 text-right text-xs font-bold uppercase tracking-wide text-neutral-500">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {isLoading ? (
                  <tr>
                    <td className="px-4 py-8 text-center text-neutral-500" colSpan={8}>
                      Loading memberships...
                    </td>
                  </tr>
                ) : filtered.length === 0 ? (
                  <tr>
                    <td className="px-4 py-8 text-center text-neutral-500" colSpan={8}>
                      {memberships.length === 0 ? "No members in this organization yet." : "No members match your search."}
                    </td>
                  </tr>
                ) : (
                  filtered.map((m) => (
                    <tr key={m.id} className="hover:bg-neutral-50">
                      <td className="px-4 py-3 font-semibold text-neutral-900">{m.user_name || "—"}</td>
                      <td className="px-4 py-3 text-neutral-600">{m.user_email || "—"}</td>
                      <td className="px-4 py-3 text-neutral-700">{m.role_name || "—"}</td>
                      <td className="px-4 py-3 text-neutral-600">{m.unit_name || "—"}</td>
                      <td className="px-4 py-3">
                        {m.unit_restricted ? (
                          <span className="rounded-full bg-warning-50 px-2 py-0.5 text-xs font-bold text-warning-700 ring-1 ring-warning-100">Yes</span>
                        ) : (
                          <span className="text-xs text-neutral-400">No</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <MembershipStatusBadge status={m.status} />
                      </td>
                      <td className="px-4 py-3 text-sm text-neutral-500">{formatDate(m.last_active_at)}</td>
                      <td className="px-4 py-3 text-right">
                        <button
                          className="inline-flex items-center gap-1 rounded border border-neutral-200 px-3 py-2 text-sm font-semibold text-neutral-700 hover:bg-neutral-50"
                          onClick={() => loadDetail(m)}
                          type="button"
                        >
                          <ChevronRight size={14} />
                          Details
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

        <p className="text-xs text-neutral-400">
          Showing {filtered.length} of {memberships.length} memberships for organization {organizationId}.
        </p>
      </div>

      <UserMembershipDetailDrawer
        membership={selectedMembershipDetail || selectedMembership || {} as OrganizationMembership}
        roles={roles}
        units={units}
        onClose={() => {
          setSelectedMembership(null);
          setSelectedMembershipDetail(null);
        }}
        onAction={handleAction}
      />

      <InviteUserModal
        open={inviteOpen}
        onClose={() => setInviteOpen(false)}
        units={units}
        onSubmit={(data) => inviteMutation.mutate(data)}
        error={error}
      />
    </PortalShell>
  );
}
