"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Activity, Building2, ClipboardCheck, FlaskConical, FolderCheck, GitBranch,
  Mail, MapPin, Network, Phone, RefreshCw, Search, ShieldCheck, UserPlus, UsersRound,
} from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { OrganizationStatusBadge } from "@/components/ui/organization-status-badge";
import { OrganizationTypeBadge } from "@/components/ui/organization-type-badge";
import { MembershipStatusBadge } from "@/components/ui/membership-status-badge";
import { UserMembershipDetailDrawer } from "@/components/ui/user-membership-detail-drawer";
import { InviteUserModal } from "@/components/ui/invite-user-modal";
import { InviteStatusBadge } from "@/components/ui/invite-status-badge";
import { OrganizationUnitTree } from "@/components/ui/organization-unit-tree";
import { OrganizationUnitDetail } from "@/components/ui/organization-unit-detail";
import { OrganizationUnitForm } from "@/components/ui/organization-unit-form";
import { DashboardCard } from "@/components/ui/dashboard-card";
import {
  fetchStakeholderContext, fetchStakeholderSummary,
  fetchMemberships, fetchMembership,
  suspendMembership, reactivateMembership, removeMembership,
  changeMembershipRole, changeMembershipUnit, toggleMembershipUnitRestriction,
  fetchUnits, createUnit, updateUnit, deleteUnit, createInvite,
  fetchInvites, revokeInvite, resendInvite,
  fetchRolesByOrganizationType, fetchRole, fetchPermissions,
} from "@/lib/api/organizations";
import { getApiErrorMessage } from "@/lib/api/client";
import { getUnitLabel, getUserLabel, UNIT_TYPE_LABELS } from "@/lib/stakeholder-labels";
import type { UserRole } from "@/types/auth";
import type { StakeholderContext } from "@/lib/api/organizations";
import type { OrganizationMembership, OrganizationUnit, StakeholderRole, UserInvite, Permission, OrganizationType } from "@/types/organizations";

type TabKey = "overview" | "stakeholders" | "roles" | "units" | "invites" | "audit";

const TAB_LABELS: Record<UserRole, Record<TabKey, string>> = {
  state_admin: { overview: "Overview", stakeholders: "Officers", roles: "Roles & Permissions", units: "Units & Offices", invites: "Invites", audit: "Audit Logs" },
  employer: { overview: "Overview", stakeholders: "Team Members", roles: "Roles & Permissions", units: "Branches / Outlets", invites: "Invites", audit: "Audit Logs" },
  facility_admin: { overview: "Overview", stakeholders: "Staff", roles: "Roles & Permissions", units: "Departments", invites: "Invites", audit: "Audit Logs" },
  federal_admin: { overview: "Overview", stakeholders: "Federal Users", roles: "Roles & Permissions", units: "Departments / Directorates", invites: "Invites", audit: "Audit Logs" },
  super_admin: { overview: "Overview", stakeholders: "Platform Users", roles: "Roles & Permissions", units: "Teams / Units", invites: "Invites", audit: "Audit Logs" },
  inspector: { overview: "Overview", stakeholders: "Officers", roles: "Roles & Permissions", units: "Units & Offices", invites: "Invites", audit: "Audit Logs" },
  doctor: { overview: "Overview", stakeholders: "Staff", roles: "Roles & Permissions", units: "Departments", invites: "Invites", audit: "Audit Logs" },
  lab_staff: { overview: "Overview", stakeholders: "Staff", roles: "Roles & Permissions", units: "Departments", invites: "Invites", audit: "Audit Logs" },
  food_handler: { overview: "Overview", stakeholders: "Users", roles: "Roles & Permissions", units: "Units", invites: "Invites", audit: "Audit Logs" },
};

function formatDate(value?: string) {
  if (!value) return "N/A";
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

function getOrgId() {
  const token = typeof window !== "undefined" ? localStorage.getItem("foodcert_access_token") : null;
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.organization_id || payload.organization || null;
  } catch { return null; }
}

// ── Overview Tab ──
function OverviewTab({ context }: { context: StakeholderContext }) {
  const { data: summary, isLoading } = useQuery({
    queryKey: ["stakeholder-summary"],
    queryFn: fetchStakeholderSummary,
  });

  const s = summary?.summary;
  const recent = summary?.recent_activity ?? [];

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <DashboardCard icon={UsersRound} label="Total Members" value={s?.total_users ?? "-"} />
        <DashboardCard icon={ShieldCheck} label="Active" value={s?.active_users ?? "-"} />
        <DashboardCard icon={UserPlus} label="Pending Invites" value={s?.pending_invites ?? "-"} />
        <DashboardCard icon={Network} label={context.labels.units} value={s?.total_units ?? "-"} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-bold text-slate-950">Organization Profile</h3>
          <div className="mt-3 grid gap-2 text-sm">
            <div className="flex items-center gap-2 text-slate-600">
              <Building2 size={14} className="text-slate-400 shrink-0" />
              <span className="font-semibold text-slate-800">{context.organization.name}</span>
            </div>
            <div className="flex items-center gap-2 pt-1">
              <OrganizationTypeBadge type={context.organization.organization_type as OrganizationType} />
              <OrganizationStatusBadge status={context.organization.status} />
            </div>
            {context.organization.state_name && (
              <div className="flex items-center gap-2 text-slate-600">
                <MapPin size={14} className="text-slate-400" />
                <span>{context.organization.state_name}{context.organization.lga_name ? `, ${context.organization.lga_name}` : ""}</span>
              </div>
            )}
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-bold text-slate-950">Recent Activity</h3>
          {isLoading ? (
            <p className="mt-3 text-sm text-slate-500">Loading...</p>
          ) : recent.length === 0 ? (
            <p className="mt-3 text-sm text-slate-500">No recent activity.</p>
          ) : (
            <div className="mt-3 space-y-2">
              {recent.map((r) => (
                <div key={r.id} className="flex items-center justify-between text-sm border-b border-slate-50 pb-2 last:border-0">
                  <span className="font-medium text-slate-800">{r.user_name}</span>
                  <span className="text-slate-500 text-xs flex items-center gap-1">
                    <MembershipStatusBadge status={r.status} />
                    <span>{formatDate(r.updated_at)}</span>
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

// ── Stakeholders Tab ──
function StakeholdersTab({ context, organizationId }: { context: StakeholderContext; organizationId: string }) {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [selected, setSelected] = useState<OrganizationMembership | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<OrganizationMembership | null>(null);
  const [error, setError] = useState<string | null>(null);

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
    queryKey: ["roles-by-type", context.organization.organization_type],
    queryFn: () => fetchRolesByOrganizationType(context.organization.organization_type as OrganizationType),
    enabled: Boolean(context.organization.organization_type),
  });

  const loadDetail = useCallback(async (m: OrganizationMembership) => {
    setSelected(m); setError(null);
    try { setSelectedDetail(await fetchMembership(organizationId, m.id)); }
    catch { setSelected(m); }
  }, [organizationId]);

  const inviteMutation = useMutation({
    mutationFn: (data: { email: string; role: UserRole; unit?: string; unit_restricted?: boolean; phone?: string; message?: string; expires_at?: string }) =>
      createInvite(organizationId, data),
    onSuccess: () => { setError(null); queryClient.invalidateQueries({ queryKey: ["memberships", organizationId] }); },
    onError: (err) => setError(getApiErrorMessage(err, "Could not send invite.")),
  });

  async function handleAction(action: string, payload?: Record<string, unknown>) {
    if (!selected) return; setError(null);
    try {
      switch (action) {
        case "suspend": await suspendMembership(organizationId, selected.id); break;
        case "reactivate": await reactivateMembership(organizationId, selected.id); break;
        case "remove": await removeMembership(organizationId, selected.id); setSelected(null); setSelectedDetail(null); break;
        case "change-role": if (payload?.role) await changeMembershipRole(organizationId, selected.id, payload.role as string); break;
        case "change-unit": await changeMembershipUnit(organizationId, selected.id, (payload?.unit as string) || null, payload?.unit_restricted as boolean | undefined); break;
        case "toggle-restriction": await toggleMembershipUnitRestriction(organizationId, selected.id); break;
      }
      queryClient.invalidateQueries({ queryKey: ["memberships", organizationId] });
      if (selected) setSelectedDetail(await fetchMembership(organizationId, selected.id));
    } catch (err) { setError(getApiErrorMessage(err, `Failed to ${action}.`)); }
  }

  const filtered = memberships.filter((m) => {
    if (search) { const q = search.toLowerCase(); if (!(m.user_name||m.user_email||"").toLowerCase().includes(q) && !m.role_name?.toLowerCase().includes(q)) return false; }
    if (statusFilter && m.status !== statusFilter) return false;
    return true;
  });

  return (
    <div className="space-y-4">
      {error ? <div className="rounded border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">{error}</div> : null}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-1 gap-2">
          <label className="relative flex-1 max-w-sm">
            <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <input className="h-10 w-full rounded border border-slate-200 bg-white pl-9 pr-3 text-sm outline-none focus:border-brand-green focus:ring-2 focus:ring-brand-green/20" placeholder="Search..." type="search" value={search} onChange={(e) => setSearch(e.target.value)} />
          </label>
          <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All statuses</option>
            <option value="active">Active</option><option value="invited">Invited</option><option value="suspended">Suspended</option><option value="removed">Removed</option>
          </select>
        </div>
        <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep" onClick={() => setSelected(null)} type="button">
          <UserPlus size={16} />{context.labels.invite_button}
        </button>
      </div>
      <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-slate-200 text-sm"><thead className="bg-slate-50"><tr>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Name</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Email</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Role</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Unit</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Restricted</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Status</th>
          <th className="px-4 py-3 text-right text-xs font-bold uppercase tracking-wide text-slate-500">Actions</th>
        </tr></thead><tbody className="divide-y divide-slate-100">
          {isLoading ? <tr><td className="px-4 py-8 text-center text-slate-500" colSpan={7}>Loading...</td></tr>
          : filtered.length === 0 ? <tr><td className="px-4 py-8 text-center text-slate-500" colSpan={7}>No members found.</td></tr>
          : filtered.map((m) => (
            <tr key={m.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 font-semibold text-slate-950">{m.user_name || "—"}</td>
              <td className="px-4 py-3 text-slate-600">{m.user_email || "—"}</td>
              <td className="px-4 py-3 text-slate-700">{m.role_name || "—"}</td>
              <td className="px-4 py-3 text-slate-600">{m.unit_name || "—"}</td>
              <td className="px-4 py-3">{m.unit_restricted ? <span className="rounded-full bg-amber-50 px-2 py-0.5 text-xs font-bold text-amber-700 ring-1 ring-amber-200">Yes</span> : <span className="text-xs text-slate-400">No</span>}</td>
              <td className="px-4 py-3"><MembershipStatusBadge status={m.status} /></td>
              <td className="px-4 py-3 text-right"><button className="rounded border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" onClick={() => loadDetail(m)} type="button">Details</button></td>
            </tr>
          ))}</tbody></table>
      </section>
      <UserMembershipDetailDrawer membership={selectedDetail || selected || {} as OrganizationMembership} roles={roles} units={units} onClose={() => { setSelected(null); setSelectedDetail(null); }} onAction={handleAction} />
      <InviteUserModal open={false} onClose={() => {}} units={units} onSubmit={(data) => inviteMutation.mutate(data)} error={error} />
    </div>
  );
}

// ── Roles Tab ──
function RolesTab({ context, organizationId }: { context: StakeholderContext; organizationId: string }) {
  const [expandedRole, setExpandedRole] = useState<StakeholderRole | null>(null);
  const [error, setError] = useState("");

  const { data: roles = [], isLoading } = useQuery({
    queryKey: ["roles-by-type", context.organization.organization_type],
    queryFn: () => fetchRolesByOrganizationType(context.organization.organization_type as OrganizationType),
    enabled: Boolean(context.organization.organization_type),
  });
  const { data: permissions } = useQuery({
    queryKey: ["permissions"],
    queryFn: () => fetchPermissions(),
  });

  const permissionsByModule = useMemo(() => (permissions ?? []).reduce<Record<string, Permission[]>>((g, p) => { (g[p.module]??=[]).push(p); return g; }, {}), [permissions]);

  async function toggleRole(role: StakeholderRole) {
    if (expandedRole?.id === role.id) { setExpandedRole(null); return; }
    setError("");
    try { setExpandedRole(await fetchRole(role.id)); }
    catch (err) { setError(getApiErrorMessage(err, "Could not load role details.")); }
  }

  const rolePermissionCodes = new Set(expandedRole?.permissions?.map((p) => p.code) ?? []);

  return (
    <div className="space-y-4">
      {error ? <div className="rounded border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">{error}</div> : null}
      <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-slate-200 text-sm"><thead className="bg-slate-50"><tr>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Role</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Type</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Permissions</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Status</th>
          <th className="px-4 py-3 text-right text-xs font-bold uppercase tracking-wide text-slate-500">Actions</th>
        </tr></thead><tbody className="divide-y divide-slate-100">
          {isLoading ? <tr><td className="px-4 py-6 text-slate-500" colSpan={5}>Loading...</td></tr>
          : roles.map((r) => (
            <tr key={r.id}>
              <td className="px-4 py-3"><div className="font-bold text-slate-950">{r.name}</div><div className="text-xs text-slate-500">{r.code}</div></td>
              <td className="px-4 py-3"><span className="rounded bg-slate-100 px-2 py-1 text-xs font-bold text-slate-700">{r.is_system_role ? "System" : "Custom"}</span></td>
              <td className="px-4 py-3 text-slate-700">{r.permission_count}</td>
              <td className="px-4 py-3"><span className={`inline-flex rounded px-2 py-1 text-xs font-bold ring-1 ${r.status === "active" ? "bg-emerald-50 text-emerald-700 ring-emerald-200" : r.status === "deprecated" ? "bg-amber-50 text-amber-700 ring-amber-200" : "bg-slate-50 text-slate-600 ring-slate-200"}`}>{r.status}</span></td>
              <td className="px-4 py-3 text-right"><button className="rounded border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" onClick={() => toggleRole(r)} type="button">Permissions</button></td>
            </tr>))}
        </tbody></table>
      </section>
      {expandedRole ? (
        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h3 className="text-base font-bold text-slate-950">{expandedRole.name}</h3>
          <p className="text-sm text-slate-600">{expandedRole.description || "No description."}</p>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            {Object.entries(permissionsByModule).map(([mod, modPerms]: [string, Permission[]]) => (
              <div className="rounded border border-slate-100 p-3" key={mod}>
                <h4 className="text-xs font-bold uppercase tracking-wide text-slate-500">{mod}</h4>
                <div className="mt-3 space-y-2">
                  {modPerms.map((p) => (
                    <div className="flex items-start justify-between gap-3 text-sm" key={p.id}>
                      <span className="text-slate-700">{p.name}</span>
                      <span className={`shrink-0 rounded px-2 py-1 text-xs font-bold ${rolePermissionCodes.has(p.code)?"bg-emerald-50 text-emerald-700":"bg-slate-50 text-slate-400"}`}>{rolePermissionCodes.has(p.code)?"Allowed":"Off"}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}

// ── Units Tab ──
function UnitsTab({ context, organizationId }: { context: StakeholderContext; organizationId: string }) {
  const queryClient = useQueryClient();
  const { data: units = [] } = useQuery({ queryKey: ["units", organizationId], queryFn: () => fetchUnits(organizationId), enabled: Boolean(organizationId) });
  const [selected, setSelected] = useState<OrganizationUnit | null>(null);
  const [mode, setMode] = useState<"view"|"create"|"edit">("view");
  const [editing, setEditing] = useState<OrganizationUnit | null>(null);
  const [error, setError] = useState<string | null>(null);

  const createMut = useMutation({ mutationFn: (d: Record<string, unknown>) => createUnit(organizationId, d as { name: string; unit_type: string }), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["units", organizationId] }) });
  const updateMut = useMutation({ mutationFn: ({ uid, d }: { uid: string; d: Record<string, unknown> }) => updateUnit(organizationId, uid, d as Record<string, string | null>), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["units", organizationId] }) });
  const deleteMut = useMutation({ mutationFn: (uid: string) => deleteUnit(organizationId, uid), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["units", organizationId] }) });

  return (
    <div className="grid gap-5 lg:grid-cols-[280px_1fr]">
      <div>
        <button className="mb-3 inline-flex w-full h-10 items-center justify-center gap-2 rounded bg-brand-green text-sm font-bold text-white hover:bg-brand-deep" onClick={() => { setEditing(null); setMode("create"); setSelected(null); setError(null); }}>
          <Activity size={16} />New {context.labels.unit}
        </button>
        <OrganizationUnitTree units={units} selectedId={selected?.id} onSelect={(u) => { setSelected(u); setMode("view"); setEditing(null); setError(null); }}
          onEdit={(u) => { setEditing(u); setMode("edit"); setError(null); }}
          onDelete={(u) => { if (confirm("Deactivate this unit?")) deleteMut.mutate(u.id); setSelected(null); setMode("view"); }}
        />
      </div>
      <div className="space-y-4">
        {mode === "create" && <OrganizationUnitForm parentOptions={units.map((u)=>({id:u.id,name:u.name}))} onSubmit={(d) => { createMut.mutate(d); setMode("view"); }} onCancel={() => setMode("view")} error={error} submitLabel={`Create ${context.labels.unit}`} />}
        {mode === "edit" && editing && <OrganizationUnitForm parentOptions={units.filter((u)=>u.id!==editing.id).map((u)=>({id:u.id,name:u.name}))} initial={editing} onSubmit={(d) => { updateMut.mutate({uid:editing.id,d}); setMode("view"); }} onCancel={() => setMode("view")} submitLabel="Save Changes" error={error} />}
        {mode === "view" && selected && <OrganizationUnitDetail unit={selected} memberCount={selected.member_count ?? 0} />}
        {mode === "view" && !selected && units.length > 0 && <div className="flex flex-col items-center justify-center gap-3 py-16 text-center"><p className="text-sm font-semibold text-slate-500">Select a {context.labels.unit} to view details</p></div>}
      </div>
    </div>
  );
}

// ── Invites Tab ──
function InvitesTab({ context, organizationId }: { context: StakeholderContext; organizationId: string }) {
  const queryClient = useQueryClient();
  const { data: invites = [] } = useQuery({ queryKey: ["organization-invites", organizationId], queryFn: () => fetchInvites(organizationId), enabled: Boolean(organizationId) });
  const { data: units = [] } = useQuery({ queryKey: ["units", organizationId], queryFn: () => fetchUnits(organizationId), enabled: Boolean(organizationId) });
  const [inviteOpen, setInviteOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createMut = useMutation({
    mutationFn: (d: { email: string; role: UserRole; unit?: string; unit_restricted?: boolean; phone?: string; message?: string; expires_at?: string }) => createInvite(organizationId, d),
    onSuccess: () => { setInviteOpen(false); setError(null); queryClient.invalidateQueries({ queryKey: ["organization-invites", organizationId] }); },
    onError: (err) => setError(getApiErrorMessage(err, "Could not send invite.")),
  });
  const revokeMut = useMutation({
    mutationFn: (invite: UserInvite) => revokeInvite(organizationId, invite.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["organization-invites", organizationId] }),
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep" onClick={() => setInviteOpen(true)} type="button"><UserPlus size={16} />{context.labels.invite_button}</button>
      </div>
      <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-slate-200 text-sm"><thead className="bg-slate-50"><tr>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase text-slate-500">Recipient</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase text-slate-500">Role</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase text-slate-500">Unit</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase text-slate-500">Invited By</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase text-slate-500">Status</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase text-slate-500">Expires</th>
          <th className="px-4 py-3 text-right text-xs font-bold uppercase text-slate-500">Action</th>
        </tr></thead><tbody className="divide-y divide-slate-100">
          {invites.length === 0 ? <tr><td className="px-4 py-8 text-center text-slate-500" colSpan={7}>No invites yet.</td></tr>
          : invites.map((i) => (
            <tr key={i.id}>
              <td className="px-4 py-3 font-semibold text-slate-950">{i.email}</td>
              <td className="px-4 py-3 text-sm capitalize text-slate-700">{i.role.replace(/_/g, " ")}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{i.unit_name || "—"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{i.invited_by_name || "—"}</td>
              <td className="px-4 py-3"><InviteStatusBadge status={i.status} /></td>
              <td className="px-4 py-3 text-sm text-slate-600">{formatDate(i.expires_at)}</td>
              <td className="px-4 py-3 text-right"><button className="h-9 rounded border border-slate-200 px-3 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-50" disabled={i.status !== "pending"} onClick={() => revokeMut.mutate(i)} type="button">Revoke</button></td>
            </tr>))}
        </tbody></table>
      </section>
      <InviteUserModal open={inviteOpen} onClose={() => setInviteOpen(false)} units={units} onSubmit={(d) => createMut.mutate(d)} error={error} />
    </div>
  );
}

// ── Audit Tab ──
function AuditTab({ context, organizationId }: { context: StakeholderContext; organizationId: string }) {
  const [filter, setFilter] = useState("all");
  const logs: { id: string; action: string; actor: string; target: string; timestamp: string }[] = [];

  return (
    <div className="space-y-4">
      <div className="flex gap-3">
        <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All actions</option><option value="org">Organization</option><option value="user">Users</option><option value="role">Roles</option>
        </select>
      </div>
      <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-slate-200 text-sm"><thead className="bg-slate-50"><tr>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase text-slate-500">Action</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase text-slate-500">Actor</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase text-slate-500">Target</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase text-slate-500">Timestamp</th>
        </tr></thead><tbody>
          {logs.length === 0 ? <tr><td className="px-4 py-8 text-center text-slate-500" colSpan={4}>Audit logs will appear here once backend integration is enabled.</td></tr>
          : logs.map((l) => <tr key={l.id} className="hover:bg-slate-50"><td className="px-4 py-3 font-semibold text-slate-800">{l.action}</td><td className="px-4 py-3 text-slate-600">{l.actor}</td><td className="px-4 py-3 text-slate-600">{l.target}</td><td className="px-4 py-3 text-slate-500">{l.timestamp}</td></tr>)}
        </tbody></table>
      </section>
    </div>
  );
}

// ── Main Layout ──
export function StakeholderManagementLayout({ role }: { role: UserRole }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [orgId, setOrgId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => setOrgId(getOrgId()), []);

  const { data: context, isLoading } = useQuery({
    queryKey: ["stakeholder-context"],
    queryFn: () => fetchStakeholderContext().catch((err) => { setError(getApiErrorMessage(err, "Could not load context.")); throw err; }),
    enabled: true,
    retry: false,
  });

  const tabParam = searchParams.get("tab") ?? "overview";
  const tabs = TAB_LABELS[role] ?? TAB_LABELS.employer;
  const activeTab: TabKey = (tabParam in tabs ? tabParam : "overview") as TabKey;

  function setTab(tab: TabKey) {
    router.replace(`/${role === "super_admin" ? "admin" : role.replace("_admin","").replace("_staff","")}/stakeholder-management?tab=${tab}`);
  }

  const hasPermission = (tab: TabKey) => {
    if (!context) return true;
    if (tab === "roles" && !context.permissions.can_view_roles) return false;
    if (tab === "units" && !context.permissions.can_view_units) return false;
    if (tab === "invites" && !context.permissions.can_view_invites) return false;
    if (tab === "audit" && !context.permissions.can_view_audit_logs) return false;
    return true;
  };

  return (
    <PortalShell role={role} title="Stakeholder Management" description="Manage organization members, roles, structure, invites, and audit history.">
      {error ? <div className="mb-4 rounded border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">{error}</div> : null}

      {/* Context header */}
      {context && (
        <div className="mb-4 flex flex-wrap items-center gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <span className="font-bold text-slate-950">{context.organization.name}</span>
          <OrganizationTypeBadge type={context.organization.organization_type as OrganizationType} />
          <OrganizationStatusBadge status={context.organization.status} />
          {context.membership.unit_name && (
            <span className="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">
              {context.membership.unit_name}{context.membership.unit_restricted ? " (restricted)" : ""}
            </span>
          )}
        </div>
      )}

      {/* Tabs */}
      <nav className="mb-6 flex gap-1 overflow-x-auto border-b border-slate-200 pb-2">
        {(Object.entries(tabs) as [TabKey, string][]).filter(([k]) => hasPermission(k)).map(([key, label]) => (
          <button
            key={key}
            className={`shrink-0 rounded px-4 py-2 text-sm font-semibold ${activeTab === key ? "bg-emerald-50 text-brand-deep ring-1 ring-emerald-200" : "text-slate-600 hover:bg-slate-50"}`}
            onClick={() => setTab(key)}
            type="button"
          >
            {label}
          </button>
        ))}
      </nav>

      {/* Tab content */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20"><p className="text-slate-500">Loading...</p></div>
      ) : !context ? (
        <div className="flex items-center justify-center py-20"><p className="text-slate-500">No organization context available.</p></div>
      ) : (
        <div>
          {activeTab === "overview" && <OverviewTab context={context} />}
          {activeTab === "stakeholders" && <StakeholdersTab context={context} organizationId={context.organization.id} />}
          {activeTab === "roles" && <RolesTab context={context} organizationId={context.organization.id} />}
          {activeTab === "units" && <UnitsTab context={context} organizationId={context.organization.id} />}
          {activeTab === "invites" && <InvitesTab context={context} organizationId={context.organization.id} />}
          {activeTab === "audit" && <AuditTab context={context} organizationId={context.organization.id} />}
        </div>
      )}
    </PortalShell>
  );
}
