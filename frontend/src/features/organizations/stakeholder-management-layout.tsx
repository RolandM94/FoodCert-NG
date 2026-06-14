"use client";

import { useState, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowUpDown, Building2, LayoutGrid, List, MapPin, Minus, MoreVertical, Network, Search, ShieldCheck, UserPlus, UsersRound, X,
  Pencil, Plus,
} from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { OrganizationStatusBadge } from "@/components/ui/organization-status-badge";
import { OrganizationTypeBadge } from "@/components/ui/organization-type-badge";
import { MembershipStatusBadge } from "@/components/ui/membership-status-badge";
import { UserMembershipDetailDrawer } from "@/components/ui/user-membership-detail-drawer";
import { InviteUserModal } from "@/components/ui/invite-user-modal";
import { OrganizationUnitForm } from "@/components/ui/organization-unit-form";
import { DashboardCard } from "@/components/ui/dashboard-card";
import { RolePermissionModal } from "@/features/organizations/components/role-permission-modal";
import {
  fetchStakeholderContext, fetchStakeholderSummary,
  fetchMemberships, fetchMembership,
  suspendMembership, reactivateMembership, removeMembership,
  changeMembershipRole, changeMembershipUnit, toggleMembershipUnitRestriction,
  fetchUnits, createUnit, updateUnit, deleteUnit, createInvite,
  fetchRolesByOrganizationType, fetchPermissions,
} from "@/lib/api/organizations";
import { getApiErrorMessage } from "@/lib/api/client";
import type { UserRole } from "@/types/auth";
import type { StakeholderContext } from "@/lib/api/organizations";
import type { OrganizationMembership, OrganizationUnit, StakeholderRole, OrganizationType } from "@/types/organizations";

type TabKey = "overview" | "stakeholders" | "roles" | "units" | "invites" | "audit";

const TAB_LABELS: Record<UserRole, Record<TabKey, string>> = {
  state_admin: { overview: "Overview", stakeholders: "Stakeholders", roles: "Roles", units: "Departments", invites: "Invites", audit: "Audit Logs" },
  employer: { overview: "Overview", stakeholders: "Stakeholders", roles: "Roles", units: "Branches", invites: "Invites", audit: "Audit Logs" },
  facility_admin: { overview: "Overview", stakeholders: "Stakeholders", roles: "Roles", units: "Departments", invites: "Invites", audit: "Audit Logs" },
  federal_admin: { overview: "Overview", stakeholders: "Stakeholders", roles: "Roles", units: "Departments", invites: "Invites", audit: "Audit Logs" },
  super_admin: { overview: "Overview", stakeholders: "Stakeholders", roles: "Roles", units: "Teams", invites: "Invites", audit: "Audit Logs" },
  inspector: { overview: "Overview", stakeholders: "Stakeholders", roles: "Roles", units: "Departments", invites: "Invites", audit: "Audit Logs" },
  doctor: { overview: "Overview", stakeholders: "Stakeholders", roles: "Roles", units: "Departments", invites: "Invites", audit: "Audit Logs" },
  lab_staff: { overview: "Overview", stakeholders: "Stakeholders", roles: "Roles", units: "Departments", invites: "Invites", audit: "Audit Logs" },
  food_handler: { overview: "Overview", stakeholders: "Stakeholders", roles: "Roles", units: "Units", invites: "Invites", audit: "Audit Logs" },
};

const PRIMARY_TABS: TabKey[] = ["stakeholders", "roles", "units"];

function formatDate(value?: string) {
  if (!value) return "N/A";
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

function initials(name?: string, email?: string) {
  const source = (name || email || "User").trim();
  const parts = source.split(/\s+/).filter(Boolean);
  if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  return source.slice(0, 2).toUpperCase();
}

function roleTone(role?: string) {
  const text = (role || "").toLowerCase();
  if (text.includes("admin") || text.includes("super")) return "bg-info-50 text-info-700 ring-info-200";
  if (text.includes("default")) return "bg-brand-50 text-brand-700 ring-brand-200";
  return "bg-brand-50 text-brand-700 ring-brand-200";
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
        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-bold text-neutral-900">Organization Profile</h3>
          <div className="mt-3 grid gap-2 text-sm">
            <div className="flex items-center gap-2 text-neutral-600">
              <Building2 size={14} className="text-neutral-400 shrink-0" />
              <span className="font-semibold text-neutral-800">{context.organization.name}</span>
            </div>
            <div className="flex items-center gap-2 pt-1">
              <OrganizationTypeBadge type={context.organization.organization_type as OrganizationType} />
              <OrganizationStatusBadge status={context.organization.status} />
            </div>
            {context.organization.state_name && (
              <div className="flex items-center gap-2 text-neutral-600">
                <MapPin size={14} className="text-neutral-400" />
                <span>{context.organization.state_name}{context.organization.lga_name ? `, ${context.organization.lga_name}` : ""}</span>
              </div>
            )}
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-bold text-neutral-900">Recent Activity</h3>
          {isLoading ? (
            <p className="mt-3 text-sm text-neutral-500">Loading...</p>
          ) : recent.length === 0 ? (
            <p className="mt-3 text-sm text-neutral-500">No recent activity.</p>
          ) : (
            <div className="mt-3 space-y-2">
              {recent.map((r) => (
                <div key={r.id} className="flex items-center justify-between text-sm border-b border-neutral-50 pb-2 last:border-0">
                  <span className="font-medium text-neutral-800">{r.user_name}</span>
                  <span className="text-neutral-500 text-xs flex items-center gap-1">
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
  const [sortBy, setSortBy] = useState<"name" | "department" | "role">("name");
  const [rowLimit, setRowLimit] = useState(10);
  const [selected, setSelected] = useState<OrganizationMembership | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<OrganizationMembership | null>(null);
  const [inviteOpen, setInviteOpen] = useState(false);
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
  }).sort((a, b) => {
    if (sortBy === "department") return (a.unit_name || "").localeCompare(b.unit_name || "");
    if (sortBy === "role") return (a.role_name || "").localeCompare(b.role_name || "");
    return (a.user_name || a.user_email || "").localeCompare(b.user_name || b.user_email || "");
  });

  const displayed = filtered.slice(0, rowLimit);
  const pendingInvites = memberships.filter((m) => m.status === "invited").length;
  const activeMembers = memberships.filter((m) => m.status === "active").length;
  const suspendedMembers = memberships.filter((m) => m.status === "suspended").length;
  const unitMemberCounts = units.reduce<Record<string, number>>((acc, unit) => {
    acc[unit.id] = unit.member_count ?? memberships.filter((m) => m.unit === unit.id).length;
    return acc;
  }, {});

  const chips = [
    { key: "", label: `Team Members (${activeMembers || memberships.length})` },
    { key: "suspended", label: `Suspended (${suspendedMembers})` },
    { key: "invited", label: `Pending Invites (${pendingInvites})` },
  ];

  return (
    <div className="space-y-5">
      {error ? <div className="rounded border border-danger-100 bg-danger-50 px-4 py-3 text-sm font-semibold text-danger-700">{error}</div> : null}
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <p className="max-w-xl text-sm leading-6 text-neutral-500">
          Stakeholders are team members who manage operational work within this organization. Shared access is handled separately for people who only need limited participation.
        </p>
        <div className="flex flex-wrap gap-3">
          <button className="inline-flex h-10 items-center gap-2 rounded-full bg-brand-600 px-5 text-sm font-bold text-white shadow-sm hover:bg-brand-700" onClick={() => setInviteOpen(true)} type="button">
            <Plus size={17} />Add New Stakeholder
          </button>
          <button className="inline-flex h-10 items-center gap-2 rounded-full bg-brand-50 px-5 text-sm font-bold text-brand-700 ring-1 ring-brand-100 hover:bg-brand-100" onClick={() => setInviteOpen(true)} type="button">
            <Plus size={17} />Add multiple stakeholder
          </button>
        </div>
      </div>

      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-wrap gap-2">
          {chips.map((chip) => (
            <button
              className={`h-10 rounded-full px-4 text-sm font-medium transition-colors ${statusFilter === chip.key ? "bg-brand-50 text-brand-700 ring-1 ring-brand-200" : "bg-neutral-100 text-neutral-500 hover:bg-neutral-200"}`}
              key={chip.key}
              onClick={() => setStatusFilter(chip.key)}
              type="button"
            >
              {chip.label}
            </button>
          ))}
          <div className="flex h-10 overflow-hidden rounded-lg border border-neutral-200 bg-white">
            <button className="grid w-10 place-items-center text-neutral-400" type="button" title="Grid view"><LayoutGrid size={16} /></button>
            <button className="grid w-10 place-items-center bg-brand-50 text-brand-700" type="button" title="List view"><List size={17} /></button>
          </div>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <label className="relative">
            <Search className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400" size={17} />
            <input className="h-11 w-full rounded-lg border border-neutral-200 bg-white pl-11 pr-4 text-sm outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-600/20 sm:w-72" placeholder="Search stakeholder" type="search" value={search} onChange={(e) => setSearch(e.target.value)} />
          </label>
          <label className="relative">
            <ArrowUpDown className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-neutral-900" size={16} />
            <select className="h-11 appearance-none rounded-lg border border-neutral-200 bg-white pl-9 pr-8 text-sm font-medium text-neutral-800" value={sortBy} onChange={(e) => setSortBy(e.target.value as typeof sortBy)}>
              <option value="name">Sort</option>
              <option value="department">Department</option>
              <option value="role">Role</option>
            </select>
          </label>
          <label className="flex h-11 overflow-hidden rounded-lg border border-neutral-200 bg-white text-sm">
            <span className="grid place-items-center border-r border-neutral-200 px-3 text-neutral-600">Rows</span>
            <select className="appearance-none bg-white px-3 text-neutral-800 outline-none" value={rowLimit} onChange={(e) => setRowLimit(Number(e.target.value))}>
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
            </select>
          </label>
        </div>
      </div>

      <section className="overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-neutral-200 text-sm">
          <thead className="bg-brand-100">
            <tr>
              <th className="w-16 px-6 py-3 text-left text-xs font-bold text-neutral-800">No.</th>
              <th className="px-6 py-3 text-left text-xs font-bold text-neutral-800">Name</th>
              <th className="px-6 py-3 text-left text-xs font-bold text-neutral-800">{context.labels.unit}</th>
              <th className="px-6 py-3 text-left text-xs font-bold text-neutral-800">Role</th>
              <th className="px-6 py-3 text-left text-xs font-bold text-neutral-800">Access Scope</th>
              <th className="w-16 px-6 py-3 text-right text-xs font-bold text-neutral-800"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {isLoading ? <tr><td className="px-6 py-10 text-center text-neutral-500" colSpan={6}>Loading stakeholders...</td></tr>
            : displayed.length === 0 ? <tr><td className="px-6 py-10 text-center text-neutral-500" colSpan={6}>No stakeholders found.</td></tr>
            : displayed.map((m, index) => (
              <tr key={m.id} className="hover:bg-neutral-50">
                <td className="px-6 py-4 text-neutral-900">{index + 1}</td>
                <td className="px-6 py-4">
                  <button className="flex items-center gap-4 text-left" onClick={() => loadDetail(m)} type="button">
                    <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-brand-50 text-sm font-bold text-neutral-700">{initials(m.user_name, m.user_email)}</span>
                    <span>
                      <span className="block font-semibold text-neutral-900">{m.user_name || m.user_email || "Unnamed stakeholder"}</span>
                      <span className="block text-xs text-neutral-400">{m.user_email || "No email"}</span>
                    </span>
                  </button>
                </td>
                <td className="px-6 py-4">
                  <p className="max-w-xs truncate font-medium text-neutral-900">{m.unit_name || "—"}</p>
                  <p className="text-xs text-neutral-400">{m.unit ? `${unitMemberCounts[m.unit] ?? 0} members` : "No unit assigned"}</p>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex rounded-full px-3 py-1 text-xs font-medium ring-1 ${roleTone(m.role_name)}`}>{m.role_name || "Default"}</span>
                </td>
                <td className="px-6 py-4">
                  {m.unit_restricted ? (
                    <span className="inline-flex rounded-lg border border-brand-100 bg-white px-3 py-1.5 text-xs font-medium text-brand-700">Restricted to {m.unit_name || "unit"}</span>
                  ) : (
                    <span className="text-sm text-neutral-400">Organization-wide</span>
                  )}
                </td>
                <td className="px-6 py-4 text-right">
                  <button className="inline-grid h-8 w-8 place-items-center rounded-full text-neutral-500 hover:bg-neutral-100 hover:text-neutral-900" onClick={() => loadDetail(m)} title="Open stakeholder details" type="button">
                    <MoreVertical size={17} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      {selected && (
        <UserMembershipDetailDrawer
          membership={selectedDetail || selected}
          roles={roles}
          units={units}
          onClose={() => { setSelected(null); setSelectedDetail(null); }}
          onAction={handleAction}
        />
      )}
      <InviteUserModal
        open={inviteOpen}
        onClose={() => setInviteOpen(false)}
        units={units}
        onSubmit={(data) => inviteMutation.mutate(data)}
        error={error}
      />
    </div>
  );
}

// ── Roles Tab ──
function RolesTab({ context }: { context: StakeholderContext }) {
  const queryClient = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<"create"|"edit">("create");
  const [editingRole, setEditingRole] = useState<StakeholderRole | null>(null);

  const { data: roles = [], isLoading } = useQuery({
    queryKey: ["roles-by-type", context.organization.organization_type],
    queryFn: () => fetchRolesByOrganizationType(context.organization.organization_type as OrganizationType),
    enabled: Boolean(context.organization.organization_type),
  });
  const { data: permissions } = useQuery({
    queryKey: ["permissions"],
    queryFn: async () => fetchPermissions(),
  });

  const totalPermissions = (permissions ?? []).length;

  function openCreate() {
    setEditingRole(null);
    setModalMode("create");
    setModalOpen(true);
  }
  function openEdit(role: StakeholderRole) {
    setEditingRole(role);
    setModalMode("edit");
    setModalOpen(true);
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button
          className="inline-flex h-10 items-center gap-2 rounded-lg bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700"
          onClick={openCreate}
          type="button"
        >
          <Plus size={16} />Create Role
        </button>
      </div>
      <section className="overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-neutral-200 text-sm">
          <thead className="bg-neutral-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">No.</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">Role Name</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">Description</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">Permissions</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">Status</th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wide text-neutral-500">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {isLoading ? (
              <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={6}>Loading roles...</td></tr>
            ) : roles.length === 0 ? (
              <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={6}>No roles defined yet.</td></tr>
            ) : (
              roles.map((r, i) => (
                <tr key={r.id} className="hover:bg-neutral-50">
                  <td className="px-4 py-3 text-xs text-neutral-500">{String(i + 1).padStart(2, "0")}</td>
                  <td className="px-4 py-3">
                    <span className="font-semibold text-neutral-900">{r.name}</span>
                    <span className="ml-2 text-xs text-neutral-400">{r.code}</span>
                  </td>
                  <td className="px-4 py-3 text-sm text-neutral-600 max-w-[200px] truncate">
                    {r.description || "—"}
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-bold text-brand-700">
                      {r.permission_count} / {totalPermissions}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ${
                      r.status === "active" ? "bg-brand-100 text-brand-700"
                      : r.status === "deprecated" ? "bg-warning-100 text-warning-700"
                      : "bg-neutral-100 text-neutral-600"
                    }`}>
                      {r.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      className="inline-flex items-center gap-1 rounded-lg border border-neutral-200 px-3 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-50"
                      onClick={() => openEdit(r)}
                      type="button"
                    >
                      <Pencil size={14} />Edit
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>

      <RolePermissionModal
        open={modalOpen}
        mode={modalMode}
        role={editingRole}
        organizationType={context.organization.organization_type as OrganizationType}
        onClose={() => { setModalOpen(false); setEditingRole(null); }}
        onSaved={() => {
          setModalOpen(false);
          setEditingRole(null);
          queryClient.invalidateQueries({ queryKey: ["roles-by-type"] });
        }}
      />
    </div>
  );
}

// ── Units Tab ──
function UnitsTab({ context, organizationId }: { context: StakeholderContext; organizationId: string }) {
  const queryClient = useQueryClient();
  const { data: units = [] } = useQuery({ queryKey: ["units", organizationId], queryFn: () => fetchUnits(organizationId), enabled: Boolean(organizationId) });
  const { data: memberships = [] } = useQuery({ queryKey: ["memberships", organizationId], queryFn: () => fetchMemberships(organizationId), enabled: Boolean(organizationId) });
  const [search, setSearch] = useState("");
  const [unitType, setUnitType] = useState("department");
  const [sortBy, setSortBy] = useState<"name" | "members" | "units">("name");
  const [rowLimit, setRowLimit] = useState(10);
  const [mode, setMode] = useState<"create"|"edit"|null>(null);
  const [editing, setEditing] = useState<OrganizationUnit | null>(null);
  const [selectedUnit, setSelectedUnit] = useState<OrganizationUnit | null>(null);
  const [drawerTab, setDrawerTab] = useState<"department" | "unit">("department");
  const [drawerSearch, setDrawerSearch] = useState("");
  const [inviteOpen, setInviteOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createMut = useMutation({ mutationFn: (d: Record<string, unknown>) => createUnit(organizationId, d as { name: string; unit_type: string }), onSuccess: () => { setMode(null); queryClient.invalidateQueries({ queryKey: ["units", organizationId] }); } });
  const updateMut = useMutation({ mutationFn: ({ uid, d }: { uid: string; d: Record<string, unknown> }) => updateUnit(organizationId, uid, d as Record<string, string | null>), onSuccess: () => { setMode(null); setEditing(null); queryClient.invalidateQueries({ queryKey: ["units", organizationId] }); } });
  const deleteMut = useMutation({ mutationFn: (uid: string) => deleteUnit(organizationId, uid), onSuccess: () => { setSelectedUnit(null); queryClient.invalidateQueries({ queryKey: ["units", organizationId] }); } });
  const inviteMut = useMutation({
    mutationFn: (d: { email: string; role: UserRole; unit?: string; unit_restricted?: boolean; phone?: string; message?: string; expires_at?: string }) => createInvite(organizationId, d),
    onSuccess: () => { setInviteOpen(false); setError(null); queryClient.invalidateQueries({ queryKey: ["memberships", organizationId] }); },
    onError: (err) => setError(getApiErrorMessage(err, "Could not send invite.")),
  });
  const childrenByParent = units.reduce<Record<string, number>>((acc, unit) => {
    if (unit.parent) acc[unit.parent] = (acc[unit.parent] ?? 0) + 1;
    return acc;
  }, {});
  const membersByUnit = memberships.reduce<Record<string, OrganizationMembership[]>>((acc, membership) => {
    if (!membership.unit) return acc;
    acc[membership.unit] = [...(acc[membership.unit] ?? []), membership];
    return acc;
  }, {});
  const typeOptions = [
    { value: "", label: `All ${context.labels.units}` },
    { value: "department", label: "Department" },
    { value: "unit", label: "Unit" },
    { value: "branch", label: "Branch" },
    { value: "directorate", label: "Directorate" },
    { value: "office", label: "Office" },
  ];

  const filtered = units
    .filter((unit) => !unitType || unit.unit_type === unitType)
    .filter((unit) => {
      if (!search) return true;
      const q = search.toLowerCase();
      return `${unit.name} ${unit.description} ${unit.manager_name ?? ""}`.toLowerCase().includes(q);
    })
    .sort((a, b) => {
      if (sortBy === "members") return (b.member_count ?? 0) - (a.member_count ?? 0);
      if (sortBy === "units") return (childrenByParent[b.id] ?? 0) - (childrenByParent[a.id] ?? 0);
      return a.name.localeCompare(b.name);
    });
  const displayed = filtered.slice(0, rowLimit);
  const selectedTypeLabel = typeOptions.find((option) => option.value === unitType)?.label ?? context.labels.unit;

  function openCreate(type: "department" | "unit") {
    setEditing({
      id: "",
      organization: organizationId,
      name: "",
      unit_type: type,
      description: "",
      address: "",
      phone: "",
      email: "",
      is_active: true,
      member_count: 0,
      open_assessment_count: 0,
      pending_lab_test_count: 0,
      records_ready_count: 0,
      created_at: "",
      updated_at: "",
    });
    setMode("create");
    setError(null);
  }

  function openChildUnitCreate(parent: OrganizationUnit) {
    setEditing({
      id: "",
      organization: organizationId,
      name: "",
      unit_type: "unit",
      parent: parent.id,
      parent_name: parent.name,
      description: "",
      address: "",
      phone: "",
      email: "",
      is_active: true,
      member_count: 0,
      open_assessment_count: 0,
      pending_lab_test_count: 0,
      records_ready_count: 0,
      created_at: "",
      updated_at: "",
    });
    setMode("create");
    setSelectedUnit(parent);
    setError(null);
  }

  function openUnitDrawer(unit: OrganizationUnit) {
    setSelectedUnit(unit);
    setMode(null);
    setEditing(null);
    setDrawerTab("department");
    setDrawerSearch("");
  }

  const selectedMembers = selectedUnit ? membersByUnit[selectedUnit.id] ?? [] : [];
  const selectedChildren = selectedUnit ? units.filter((unit) => unit.parent === selectedUnit.id) : [];
  const drawerRows = drawerTab === "department" ? selectedMembers.filter((member) => {
    if (!drawerSearch) return true;
    return `${member.user_name ?? ""} ${member.user_email ?? ""} ${member.role_name ?? ""}`.toLowerCase().includes(drawerSearch.toLowerCase());
  }) : selectedChildren.filter((unit) => {
    if (!drawerSearch) return true;
    return `${unit.name} ${unit.description}`.toLowerCase().includes(drawerSearch.toLowerCase());
  });

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <p className="max-w-xl text-sm leading-6 text-neutral-500">
          Departments and units define how stakeholders are grouped for operational ownership, reporting, and scoped access across the platform.
        </p>
        <div className="flex flex-wrap gap-3">
          <button className="inline-flex h-10 items-center gap-2 rounded-full border border-brand-200 bg-white px-5 text-sm font-bold text-brand-700 hover:bg-brand-50" onClick={() => openCreate("unit")} type="button">
            <Plus size={17} />Create Unit
          </button>
          <button className="inline-flex h-10 items-center gap-2 rounded-full bg-brand-600 px-5 text-sm font-bold text-white shadow-sm hover:bg-brand-700" onClick={() => openCreate("department")} type="button">
            <Plus size={17} />Create department
          </button>
        </div>
      </div>

      {mode && !selectedUnit ? (
        <OrganizationUnitForm
          parentOptions={units.filter((unit)=>unit.id!==editing?.id).map((unit)=>({ id: unit.id, name: unit.name }))}
          initial={editing ?? undefined}
          onSubmit={(data) => {
            if (mode === "edit" && editing?.id) updateMut.mutate({ uid: editing.id, d: data });
            else createMut.mutate(data);
          }}
          onCancel={() => { setMode(null); setEditing(null); }}
          submitLabel={mode === "edit" ? "Save Changes" : `Create ${editing?.unit_type === "department" ? "Department" : "Unit"}`}
          error={error}
        />
      ) : null}

      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-wrap gap-3">
          <select className="h-10 min-w-44 rounded-lg border border-neutral-200 bg-neutral-100 px-3 text-sm font-medium text-neutral-900" value={unitType} onChange={(event) => setUnitType(event.target.value)}>
            {typeOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
          <div className="flex h-10 overflow-hidden rounded-lg border border-neutral-200 bg-white">
            <button className="grid w-10 place-items-center text-neutral-400" type="button" title="Grid view"><LayoutGrid size={16} /></button>
            <button className="grid w-10 place-items-center bg-brand-50 text-brand-700" type="button" title="List view"><List size={17} /></button>
          </div>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <label className="relative">
            <Search className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400" size={17} />
            <input className="h-11 w-full rounded-lg border border-neutral-200 bg-white pl-11 pr-4 text-sm outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-600/20 sm:w-80" placeholder={`Search ${selectedTypeLabel.toLowerCase()}s`} type="search" value={search} onChange={(event) => setSearch(event.target.value)} />
          </label>
          <select className="h-11 rounded-lg border border-neutral-200 bg-neutral-100 px-3 text-sm font-medium text-neutral-800" value={sortBy} onChange={(event) => setSortBy(event.target.value as typeof sortBy)}>
            <option value="name">Sort</option>
            <option value="members">Members</option>
            <option value="units">Units</option>
          </select>
          <label className="flex h-11 overflow-hidden rounded-lg border border-neutral-200 bg-white text-sm">
            <span className="grid place-items-center border-r border-neutral-200 px-3 text-neutral-600">Rows</span>
            <select className="appearance-none bg-white px-3 text-neutral-800 outline-none" value={rowLimit} onChange={(event) => setRowLimit(Number(event.target.value))}>
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
            </select>
          </label>
        </div>
      </div>

      <section className="overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-neutral-200 text-sm">
          <thead className="bg-brand-50">
            <tr>
              <th className="w-12 px-4 py-3 text-left"><input className="h-4 w-4 rounded border-neutral-300" type="checkbox" /></th>
              <th className="w-16 px-4 py-3 text-left text-xs font-medium text-neutral-800">No.</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-neutral-800">{selectedTypeLabel}</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-neutral-800">Members</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-neutral-800">Unit</th>
              <th className="w-16 px-4 py-3 text-right text-xs font-medium text-neutral-800"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {displayed.length === 0 ? (
              <tr><td className="px-4 py-10 text-center text-neutral-500" colSpan={6}>No {selectedTypeLabel.toLowerCase()} records found.</td></tr>
            ) : displayed.map((unit, index) => {
              const members = membersByUnit[unit.id] ?? [];
              return (
                <tr key={unit.id} className="hover:bg-neutral-50">
                  <td className="px-4 py-4"><input className="h-4 w-4 rounded border-neutral-300" type="checkbox" /></td>
                  <td className="px-4 py-4 text-neutral-500">{index + 1}</td>
                  <td className="px-4 py-4">
                    <button className="text-left font-medium text-neutral-900 hover:text-brand-700" onClick={() => openUnitDrawer(unit)} type="button">
                      {unit.name}
                    </button>
                    {unit.description ? <p className="mt-1 max-w-md truncate text-xs text-neutral-400">{unit.description}</p> : null}
                  </td>
                  <td className="px-4 py-4">
                    {members.length > 0 ? (
                      <div className="flex max-w-xl flex-wrap gap-2">
                        {members.slice(0, 3).map((member) => (
                          <span className="inline-flex items-center gap-1 rounded-full bg-neutral-100 px-2 py-1 text-xs text-neutral-700" key={member.id}>
                            <span className="grid h-5 w-5 place-items-center rounded-full bg-brand-50 text-[10px] font-bold text-neutral-600">{initials(member.user_name, member.user_email)}</span>
                            {member.user_name || member.user_email}
                          </span>
                        ))}
                        {members.length > 3 ? <span className="rounded-full bg-neutral-100 px-2 py-1 text-xs text-neutral-500">+ {members.length - 3} others</span> : null}
                      </div>
                    ) : <span className="text-neutral-400">—</span>}
                  </td>
                  <td className="px-4 py-4 text-neutral-500">{childrenByParent[unit.id] ?? 0} units</td>
                  <td className="px-4 py-4 text-right">
                    <button className="inline-grid h-8 w-8 place-items-center rounded-full text-neutral-500 hover:bg-neutral-100 hover:text-neutral-900" onClick={() => openUnitDrawer(unit)} type="button">
                      <MoreVertical size={17} />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </section>
      <div className="flex items-center justify-between text-sm text-neutral-600">
        <span>Page 1 of 1</span>
        <div className="flex items-center gap-2">
          <button className="grid h-9 w-9 place-items-center rounded-lg border border-neutral-100 text-neutral-300" disabled type="button">‹</button>
          <button className="grid h-9 w-9 place-items-center rounded-lg border border-brand-300 text-brand-700" type="button">1</button>
          <button className="grid h-9 w-9 place-items-center rounded-lg border border-neutral-100 text-neutral-300" disabled type="button">›</button>
        </div>
      </div>

      {selectedUnit ? (
        <div className="fixed inset-0 z-40 flex justify-end bg-neutral-950/10">
          <aside className="flex h-full w-full max-w-md flex-col border-l border-neutral-200 bg-white shadow-2xl">
            <header className="flex h-16 items-center justify-between border-b border-neutral-200 px-5">
              <div className="flex items-center gap-3">
                <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand-50 text-brand-700">
                  <Building2 size={18} />
                </span>
                <h2 className="text-sm font-semibold text-neutral-900">{selectedUnit.unit_type === "unit" ? "Unit Information" : "Department Information"}</h2>
              </div>
              <button className="grid h-8 w-8 place-items-center rounded-full text-neutral-500 hover:bg-neutral-100" onClick={() => { setSelectedUnit(null); setMode(null); setEditing(null); }} type="button">
                <X size={18} />
              </button>
            </header>

            <div className="flex-1 overflow-y-auto p-5">
              <div className="flex min-h-28 items-end rounded-lg bg-gradient-to-br from-brand-500 to-brand-800 p-4 text-white">
                <div>
                  <p className="text-sm font-semibold">{selectedUnit.name}</p>
                  {selectedUnit.description ? <p className="mt-1 line-clamp-2 text-xs text-white/80">{selectedUnit.description}</p> : null}
                </div>
              </div>

              <div className="mt-4 flex flex-wrap items-center gap-3">
                <button className="inline-flex h-10 items-center gap-2 rounded-full bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700" onClick={() => openChildUnitCreate(selectedUnit)} type="button">
                  <Plus size={16} />Add Unit
                </button>
                <button className="text-sm font-semibold text-brand-700 hover:text-brand-800" onClick={() => setInviteOpen(true)} type="button">
                  + Add team member
                </button>
              </div>

              {mode && editing ? (
                <div className="mt-5">
                  <OrganizationUnitForm
                    parentOptions={units.filter((unit)=>unit.id!==editing.id).map((unit)=>({ id: unit.id, name: unit.name }))}
                    initial={editing}
                    onSubmit={(data) => {
                      if (mode === "edit" && editing.id) updateMut.mutate({ uid: editing.id, d: data });
                      else createMut.mutate(data);
                    }}
                    onCancel={() => { setMode(null); setEditing(null); }}
                    submitLabel={mode === "edit" ? "Save Changes" : "Create Unit"}
                    error={error}
                  />
                </div>
              ) : (
                <>
                  <nav className="mt-5 flex gap-5 border-b border-neutral-200">
                    <button className={`border-b-2 pb-3 text-sm font-medium ${drawerTab === "department" ? "border-brand-600 text-neutral-900" : "border-transparent text-neutral-500"}`} onClick={() => setDrawerTab("department")} type="button">
                      Department
                    </button>
                    <button className={`border-b-2 pb-3 text-sm font-medium ${drawerTab === "unit" ? "border-brand-600 text-neutral-900" : "border-transparent text-neutral-500"}`} onClick={() => setDrawerTab("unit")} type="button">
                      Unit
                    </button>
                  </nav>

                  <label className="relative mt-5 block">
                    <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" size={16} />
                    <input className="h-10 w-full rounded-lg border border-neutral-100 bg-neutral-100 pl-9 pr-3 text-sm outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-600/20" placeholder="Search" type="search" value={drawerSearch} onChange={(event) => setDrawerSearch(event.target.value)} />
                  </label>

                  <div className="mt-3 space-y-2">
                    {drawerTab === "department" ? (
                      drawerRows.length === 0 ? (
                        <p className="rounded-lg bg-neutral-50 p-4 text-sm text-neutral-500">No team members are assigned to this department yet.</p>
                      ) : (drawerRows as OrganizationMembership[]).map((member) => (
                        <div className="flex items-center justify-between gap-3 rounded-lg bg-neutral-50 p-3" key={member.id}>
                          <div className="flex min-w-0 items-center gap-3">
                            <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-neutral-200 text-xs font-bold text-neutral-600">{initials(member.user_name, member.user_email)}</span>
                            <div className="min-w-0">
                              <p className="truncate text-sm font-medium text-neutral-900">{member.user_name || member.user_email}</p>
                              <p className="text-xs text-neutral-400">{member.user_email || "N/A"}</p>
                            </div>
                          </div>
                          <div className="flex shrink-0 items-center gap-2">
                            <span className={`rounded-full px-3 py-1 text-xs font-medium ring-1 ${roleTone(member.role_name)}`}>{member.role_name || "Default"}</span>
                            <button className="grid h-7 w-7 place-items-center rounded-full border border-neutral-200 text-neutral-400" type="button"><Minus size={14} /></button>
                          </div>
                        </div>
                      ))
                    ) : (
                      drawerRows.length === 0 ? (
                        <p className="rounded-lg bg-neutral-50 p-4 text-sm text-neutral-500">No units have been created under this department yet.</p>
                      ) : (drawerRows as OrganizationUnit[]).map((unit) => (
                        <div className="flex items-center justify-between gap-3 rounded-lg bg-neutral-50 p-3" key={unit.id}>
                          <div className="min-w-0">
                            <p className="truncate text-sm font-medium text-neutral-900">{unit.name}</p>
                            <p className="text-xs text-neutral-400">{unit.member_count ?? 0} members</p>
                          </div>
                          <button className="grid h-8 w-8 place-items-center rounded-full text-neutral-500 hover:bg-neutral-100" onClick={() => openUnitDrawer(unit)} type="button">
                            <MoreVertical size={16} />
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </>
              )}
            </div>

            <footer className="flex items-center justify-between gap-3 border-t border-neutral-200 bg-white p-5">
              <button className="h-10 rounded-full border border-danger-200 px-4 text-sm font-semibold text-danger-600 hover:bg-danger-50" onClick={() => { if (confirm(`Delete ${selectedUnit.name}?`)) deleteMut.mutate(selectedUnit.id); }} type="button">
                Delete {selectedUnit.unit_type === "unit" ? "unit" : "department"}
              </button>
              <button className="h-10 rounded-full bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700" onClick={() => { setEditing(selectedUnit); setMode("edit"); }} type="button">
                Edit {selectedUnit.unit_type === "unit" ? "unit" : "department"}
              </button>
            </footer>
          </aside>
        </div>
      ) : null}

      <InviteUserModal open={inviteOpen} onClose={() => setInviteOpen(false)} units={units} onSubmit={(data) => inviteMut.mutate(data)} error={error} />
    </div>
  );
}

// ── Audit Tab ──
function AuditTab() {
  const [filter, setFilter] = useState("all");
  const logs: { id: string; action: string; actor: string; target: string; timestamp: string }[] = [];

  return (
    <div className="space-y-4">
      <div className="flex gap-3">
        <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All actions</option><option value="org">Organization</option><option value="user">Users</option><option value="role">Roles</option>
        </select>
      </div>
      <section className="overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-neutral-200 text-sm"><thead className="bg-neutral-50"><tr>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase text-neutral-500">Action</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase text-neutral-500">Actor</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase text-neutral-500">Target</th>
          <th className="px-4 py-3 text-left text-xs font-bold uppercase text-neutral-500">Timestamp</th>
        </tr></thead><tbody>
          {logs.length === 0 ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={4}>Audit logs will appear here once backend integration is enabled.</td></tr>
          : logs.map((l) => <tr key={l.id} className="hover:bg-neutral-50"><td className="px-4 py-3 font-semibold text-neutral-800">{l.action}</td><td className="px-4 py-3 text-neutral-600">{l.actor}</td><td className="px-4 py-3 text-neutral-600">{l.target}</td><td className="px-4 py-3 text-neutral-500">{l.timestamp}</td></tr>)}
        </tbody></table>
      </section>
    </div>
  );
}

// ── Main Layout ──
export function StakeholderManagementLayout({ role }: { role: UserRole }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  const { data: context, isLoading } = useQuery({
    queryKey: ["stakeholder-context"],
    queryFn: () => fetchStakeholderContext().catch((err) => { setError(getApiErrorMessage(err, "Could not load context.")); throw err; }),
    enabled: true,
    retry: false,
  });

  const tabParam = searchParams.get("tab") ?? "stakeholders";
  const tabs = TAB_LABELS[role] ?? TAB_LABELS.employer;
  const activeTab: TabKey = PRIMARY_TABS.includes(tabParam as TabKey) && tabParam in tabs ? tabParam as TabKey : "stakeholders";

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
    <PortalShell role={role} title="Stakeholders" description="Manage team members, roles, departments, and shared access for this organization.">
      {error ? <div className="mb-4 rounded border border-danger-100 bg-danger-50 px-4 py-3 text-sm font-semibold text-danger-700">{error}</div> : null}

      {/* Tabs */}
      <nav className="mb-6 flex gap-0 overflow-x-auto border-b border-neutral-200">
        {(Object.entries(tabs) as [TabKey, string][]).filter(([k]) => PRIMARY_TABS.includes(k) && hasPermission(k)).map(([key, label]) => (
          <button
            key={key}
            className={`shrink-0 border-b-2 px-4 py-3 text-sm font-medium ${
              activeTab === key
                ? "border-brand-600 text-brand-700"
                : "border-transparent text-neutral-500 hover:text-neutral-800"
            }`}
            onClick={() => setTab(key)}
            type="button"
          >
            {label}
          </button>
        ))}
      </nav>

      {/* Tab content */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20"><p className="text-neutral-500">Loading...</p></div>
      ) : !context ? (
        <div className="flex items-center justify-center py-20"><p className="text-neutral-500">No organization context available.</p></div>
      ) : (
        <div>
          {activeTab === "overview" && <OverviewTab context={context} />}
          {activeTab === "stakeholders" && <StakeholdersTab context={context} organizationId={context.organization.id} />}
          {activeTab === "roles" && <RolesTab context={context} />}
          {activeTab === "units" && <UnitsTab context={context} organizationId={context.organization.id} />}
          {activeTab === "audit" && <AuditTab />}
        </div>
      )}
    </PortalShell>
  );
}
