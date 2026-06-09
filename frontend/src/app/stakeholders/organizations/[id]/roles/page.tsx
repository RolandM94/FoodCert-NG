"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { ChevronDown, Plus, ShieldCheck } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import {
  createRole,
  fetchOrganization,
  fetchPermissions,
  fetchRole,
  fetchRolesByOrganizationType,
} from "@/lib/api/organizations";
import { getApiErrorMessage } from "@/lib/api/client";
import type { Organization, Permission, StakeholderRole } from "@/types/organizations";

const ORG_TYPE_LABELS: Record<string, string> = {
  platform_operator: "Platform Operator",
  federal_ministry: "Federal Ministry",
  state_ministry: "State Ministry",
  medical_facility: "Medical Facility",
  employer: "Employer",
};

function statusClass(status: string) {
  if (status === "active") return "bg-brand-50 text-brand-700 ring-brand-200";
  if (status === "deprecated") return "bg-warning-50 text-warning-700 ring-warning-100";
  return "bg-neutral-50 text-neutral-600 ring-neutral-200";
}

export default function OrganizationRolesPage() {
  const params = useParams<{ id: string }>();
  const organizationId = params.id;
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [roles, setRoles] = useState<StakeholderRole[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [expandedRole, setExpandedRole] = useState<StakeholderRole | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ name: "", code: "", description: "" });

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const org = await fetchOrganization(organizationId);
        const [roleRows, permissionRows] = await Promise.all([
          fetchRolesByOrganizationType(org.organization_type),
          fetchPermissions(),
        ]);
        if (!mounted) return;
        setOrganization(org);
        setRoles(roleRows);
        setPermissions(permissionRows);
      } catch (err) {
        if (mounted) setError(getApiErrorMessage(err, "Could not load roles."));
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, [organizationId]);

  const permissionsByModule = useMemo(() => {
    return permissions.reduce<Record<string, Permission[]>>((groups, permission) => {
      groups[permission.module] = groups[permission.module] || [];
      groups[permission.module].push(permission);
      return groups;
    }, {});
  }, [permissions]);

  async function toggleRole(role: StakeholderRole) {
    if (expandedRole?.id === role.id) {
      setExpandedRole(null);
      return;
    }
    setError("");
    try {
      setExpandedRole(await fetchRole(role.id));
    } catch (err) {
      setError(getApiErrorMessage(err, "Could not load role details."));
    }
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!organization) return;
    setSaving(true);
    setError("");
    try {
      const created = await createRole({
        name: form.name,
        code: form.code,
        organization_type: organization.organization_type,
        description: form.description,
        status: "active",
      });
      setRoles((current) => [...current, created].sort((a, b) => a.name.localeCompare(b.name)));
      setExpandedRole(created);
      setForm({ name: "", code: "", description: "" });
      setShowCreate(false);
    } catch (err) {
      setError(getApiErrorMessage(err, "Could not create role."));
    } finally {
      setSaving(false);
    }
  }

  const rolePermissionCodes = new Set(expandedRole?.permissions?.map((permission) => permission.code) || []);

  return (
    <PortalShell
      role="super_admin"
      title="Organization Roles"
      description="View role templates, custom roles, and permission coverage for this organization type."
    >
      <div className="space-y-5">
        {error ? (
          <div className="rounded border border-danger-100 bg-danger-50 px-4 py-3 text-sm font-semibold text-danger-700">
            {error}
          </div>
        ) : null}

        <div className="flex flex-col justify-between gap-3 border-b border-neutral-200 pb-4 sm:flex-row sm:items-end">
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Organization type</p>
            <h2 className="mt-1 text-lg font-bold text-neutral-900">
              {organization ? ORG_TYPE_LABELS[organization.organization_type] : "Loading"}
            </h2>
            <p className="mt-1 text-sm text-neutral-600">{organization?.name ?? "Fetching organization profile."}</p>
          </div>
          <button
            className="inline-flex w-fit items-center gap-2 rounded bg-brand-600 px-3 py-2 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60"
            disabled={!organization || loading}
            onClick={() => setShowCreate((value) => !value)}
            type="button"
          >
            <Plus aria-hidden="true" size={16} />
            Custom role
          </button>
        </div>

        {showCreate ? (
          <form className="grid gap-3 rounded border border-neutral-200 bg-white p-4 shadow-sm md:grid-cols-3" onSubmit={handleCreate}>
            <label className="text-sm font-semibold text-neutral-700">
              Role name
              <input
                className="mt-1 w-full rounded border border-neutral-200 px-3 py-2 text-sm"
                onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                required
                value={form.name}
              />
            </label>
            <label className="text-sm font-semibold text-neutral-700">
              Code
              <input
                className="mt-1 w-full rounded border border-neutral-200 px-3 py-2 text-sm"
                onChange={(event) => setForm((current) => ({ ...current, code: event.target.value }))}
                pattern="[a-z0-9_]+"
                required
                value={form.code}
              />
            </label>
            <label className="text-sm font-semibold text-neutral-700">
              Description
              <input
                className="mt-1 w-full rounded border border-neutral-200 px-3 py-2 text-sm"
                onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
                value={form.description}
              />
            </label>
            <div className="md:col-span-3">
              <button className="rounded bg-neutral-900 px-3 py-2 text-sm font-bold text-white disabled:opacity-60" disabled={saving} type="submit">
                {saving ? "Creating..." : "Create role"}
              </button>
            </div>
          </form>
        ) : null}

        <div className="overflow-hidden rounded border border-neutral-200 bg-white shadow-sm">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="bg-neutral-50 text-xs uppercase text-neutral-500">
              <tr>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Permissions</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {loading ? (
                <tr><td className="px-4 py-6 text-neutral-500" colSpan={5}>Loading roles...</td></tr>
              ) : roles.map((role) => (
                <tr key={role.id}>
                  <td className="px-4 py-3">
                    <div className="font-bold text-neutral-900">{role.name}</div>
                    <div className="text-xs text-neutral-500">{role.code}</div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded bg-neutral-100 px-2 py-1 text-xs font-bold text-neutral-700">
                      {role.is_system_role ? "System" : "Custom"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-neutral-700">{role.permission_count}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex rounded px-2 py-1 text-xs font-bold ring-1 ${statusClass(role.status)}`}>
                      {role.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      className="inline-flex items-center gap-1 rounded border border-neutral-200 px-3 py-2 text-sm font-semibold text-neutral-700 hover:bg-neutral-50"
                      onClick={() => toggleRole(role)}
                      type="button"
                    >
                      <ChevronDown aria-hidden="true" size={15} />
                      Permissions
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {expandedRole ? (
          <section className="rounded border border-neutral-200 bg-white p-4 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <ShieldCheck aria-hidden="true" className="text-brand-700" size={18} />
              <div>
                <h3 className="text-base font-bold text-neutral-900">{expandedRole.name}</h3>
                <p className="text-sm text-neutral-600">{expandedRole.description || "No description provided."}</p>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              {Object.entries(permissionsByModule).map(([module, modulePermissions]) => (
                <div className="rounded border border-neutral-100 p-3" key={module}>
                  <h4 className="text-xs font-bold uppercase tracking-wide text-neutral-500">{module}</h4>
                  <div className="mt-3 space-y-2">
                    {modulePermissions.map((permission) => (
                      <div className="flex items-start justify-between gap-3 text-sm" key={permission.id}>
                        <span className="text-neutral-700">{permission.name}</span>
                        <span className={`shrink-0 rounded px-2 py-1 text-xs font-bold ${rolePermissionCodes.has(permission.code) ? "bg-brand-50 text-brand-700" : "bg-neutral-50 text-neutral-400"}`}>
                          {rolePermissionCodes.has(permission.code) ? "Allowed" : "Off"}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>
        ) : null}
      </div>
    </PortalShell>
  );
}
