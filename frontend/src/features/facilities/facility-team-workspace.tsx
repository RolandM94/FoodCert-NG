"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertCircle, ArrowLeft, Plus, Search, ShieldCheck, UserCog, Users, UserX } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { getApiErrorMessage } from "@/lib/api/client";
import {
  createFacilityInvite,
  createFacilityRole,
  getFacilityRole,
  getCurrentMedicalFacility,
  listFacilityRoles,
  listFacilityStaff,
  reactivateFacilityStaff,
  suspendFacilityStaff,
  updateFacilityRole,
  updateFacilityStaff,
} from "@/lib/api/facilities";

const PROFESSIONAL_CATEGORIES = [
  "admin",
  "doctor",
  "lab_technician",
  "lab_scientist",
  "lab_supervisor",
  "front_desk",
  "finance",
  "records",
  "compliance",
  "viewer",
] as const;

function niceLabel(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (s) => s.toUpperCase());
}

function statusTone(status?: string) {
  if (status === "active") return "bg-success-50 text-success-700 ring-success-200";
  if (status === "suspended" || status === "removed") return "bg-danger-50 text-danger-700 ring-danger-200";
  return "bg-warning-50 text-warning-700 ring-warning-200";
}

function TeamNav({ current }: { current: "team" | "invite" | "roles" }) {
  const items = [
    { key: "team", label: "Team members", href: "/facility/team" },
    { key: "invite", label: "Invite member", href: "/facility/team/invite" },
    { key: "roles", label: "Roles", href: "/facility/roles" },
  ] as const;
  return (
    <div className="mb-6 flex flex-wrap gap-2">
      {items.map((item) => (
        <Link
          key={item.key}
          href={item.href}
          className={`inline-flex h-10 items-center rounded-full px-4 text-sm font-semibold ${
            current === item.key ? "bg-brand-600 text-white" : "bg-white text-neutral-700 ring-1 ring-neutral-200 hover:bg-neutral-50"
          }`}
        >
          {item.label}
        </Link>
      ))}
    </div>
  );
}

export function FacilityTeamPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);

  const facilityQuery = useQuery({ queryKey: ["current-facility"], queryFn: getCurrentMedicalFacility });
  const facilityId = facilityQuery.data?.id;
  const staffQuery = useQuery({
    queryKey: ["facility-staff", facilityId],
    queryFn: () => listFacilityStaff(facilityId!),
    enabled: Boolean(facilityId),
  });

  const suspendMutation = useMutation({
    mutationFn: (memberId: string) => suspendFacilityStaff(facilityId!, memberId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["facility-staff", facilityId] }),
    onError: (err) => setError(getApiErrorMessage(err, "Could not suspend team member.")),
  });
  const reactivateMutation = useMutation({
    mutationFn: (memberId: string) => reactivateFacilityStaff(facilityId!, memberId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["facility-staff", facilityId] }),
    onError: (err) => setError(getApiErrorMessage(err, "Could not reactivate team member.")),
  });

  const rows = useMemo(() => {
    const list = staffQuery.data ?? [];
    if (!search.trim()) return list;
    const query = search.toLowerCase();
    return list.filter((row) =>
      [row.user_name, row.user_email, row.role_name, row.professional_category, row.department_name]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(query))
    );
  }, [search, staffQuery.data]);

  return (
    <PortalShell role="facility_admin" title="Facility Team" description="Manage medical facility team members, assignments, invite flow, and operational access.">
      <TeamNav current="team" />
      {error ? <div className="mb-4 rounded-lg border border-danger-100 bg-danger-50 px-4 py-3 text-sm font-semibold text-danger-700">{error}</div> : null}
      <div className="mb-5 grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm"><p className="text-sm text-neutral-500">Total team</p><p className="mt-2 text-2xl font-bold text-neutral-900">{staffQuery.data?.length ?? 0}</p></div>
        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm"><p className="text-sm text-neutral-500">Active</p><p className="mt-2 text-2xl font-bold text-neutral-900">{staffQuery.data?.filter((row) => row.status === "active").length ?? 0}</p></div>
        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm"><p className="text-sm text-neutral-500">Pending activation</p><p className="mt-2 text-2xl font-bold text-neutral-900">{staffQuery.data?.filter((row) => row.status !== "active").length ?? 0}</p></div>
      </div>
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <label className="relative">
          <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" />
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search team members" className="h-10 w-full rounded-lg border border-neutral-200 bg-white pl-9 pr-3 text-sm sm:w-80" />
        </label>
        <Link href="/facility/team/invite" className="inline-flex h-10 items-center gap-2 rounded-lg bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700"><Plus size={16} /> Invite team member</Link>
      </div>
      <section className="overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-neutral-200 text-sm">
          <thead className="bg-neutral-50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-neutral-700">Member</th>
              <th className="px-4 py-3 text-left font-semibold text-neutral-700">Role</th>
              <th className="px-4 py-3 text-left font-semibold text-neutral-700">Professional category</th>
              <th className="px-4 py-3 text-left font-semibold text-neutral-700">Department</th>
              <th className="px-4 py-3 text-left font-semibold text-neutral-700">Status</th>
              <th className="px-4 py-3 text-right font-semibold text-neutral-700">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {staffQuery.isLoading ? <tr><td className="px-4 py-10 text-center text-neutral-500" colSpan={6}>Loading facility team...</td></tr> : null}
            {!staffQuery.isLoading && rows.length === 0 ? <tr><td className="px-4 py-10 text-center text-neutral-500" colSpan={6}>No team members found.</td></tr> : null}
            {rows.map((member) => (
              <tr key={member.id}>
                <td className="px-4 py-4">
                  <Link href={`/facility/team/${member.id}`} className="block">
                    <p className="font-semibold text-neutral-900">{member.user_name || member.user_email}</p>
                    <p className="text-xs text-neutral-500">{member.user_email}</p>
                  </Link>
                </td>
                <td className="px-4 py-4 text-neutral-700">{member.role_name || niceLabel(member.staff_type)}</td>
                <td className="px-4 py-4 text-neutral-700">{niceLabel(member.professional_category)}</td>
                <td className="px-4 py-4 text-neutral-700">{member.department_name || "Unassigned"}</td>
                <td className="px-4 py-4"><span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ring-1 ${statusTone(member.status)}`}>{niceLabel(member.status)}</span></td>
                <td className="px-4 py-4">
                  <div className="flex justify-end gap-2">
                    <Link href={`/facility/team/${member.id}`} className="inline-flex h-9 items-center rounded-lg border border-neutral-200 px-3 text-xs font-semibold text-neutral-700">Open</Link>
                    {member.is_active ? (
                      <button type="button" onClick={() => suspendMutation.mutate(member.id)} className="inline-flex h-9 items-center rounded-lg border border-danger-200 px-3 text-xs font-semibold text-danger-700">Suspend</button>
                    ) : (
                      <button type="button" onClick={() => reactivateMutation.mutate(member.id)} className="inline-flex h-9 items-center rounded-lg border border-success-200 px-3 text-xs font-semibold text-success-700">Activate</button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </PortalShell>
  );
}

export function FacilityInvitePage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    email: "",
    phone: "",
    role: "facility_admin",
    staff_type: "facility_admin",
    facility_role: "",
    professional_category: "admin",
    professional_registration_number: "",
    license_issuing_body: "",
    message: "",
  });
  const [error, setError] = useState<string | null>(null);
  const facilityQuery = useQuery({ queryKey: ["current-facility"], queryFn: getCurrentMedicalFacility });
  const facilityId = facilityQuery.data?.id;
  const rolesQuery = useQuery({
    queryKey: ["facility-roles", facilityId],
    queryFn: () => listFacilityRoles(facilityId!),
    enabled: Boolean(facilityId),
  });
  const mutation = useMutation({
    mutationFn: () => createFacilityInvite(facilityId!, { ...form, facility_role: form.facility_role || null }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["facility-invites", facilityId] });
      setError(null);
      setForm({
        email: "",
        phone: "",
        role: "facility_admin",
        staff_type: "facility_admin",
        facility_role: "",
        professional_category: "admin",
        professional_registration_number: "",
        license_issuing_body: "",
        message: "",
      });
    },
    onError: (err) => setError(getApiErrorMessage(err, "Could not send team invite.")),
  });

  const needsLicense = ["doctor", "lab_technician", "lab_scientist", "lab_supervisor"].includes(form.professional_category);
  const selectedRole = (rolesQuery.data ?? []).find((role) => role.id === form.facility_role);

  return (
    <PortalShell role="facility_admin" title="Invite Team Member" description="Invite doctors, laboratory staff, front desk, finance, records, compliance, and operational facility users.">
      <TeamNav current="invite" />
      <div className="max-w-3xl rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-neutral-900">New facility invite</h2>
            <p className="mt-1 text-sm text-neutral-500">Choose the role, professional category, and licensing details before sending the invite.</p>
          </div>
          <Link href="/facility/team" className="inline-flex items-center gap-2 text-sm font-semibold text-neutral-600"><ArrowLeft size={16} /> Back to team</Link>
        </div>
        {error ? <div className="mb-4 rounded-lg border border-danger-100 bg-danger-50 px-4 py-3 text-sm font-semibold text-danger-700">{error}</div> : null}
        {mutation.isSuccess ? <div className="mb-4 rounded-lg border border-success-100 bg-success-50 px-4 py-3 text-sm font-semibold text-success-700">Invite sent successfully.</div> : null}
        <div className="grid gap-4 md:grid-cols-2">
          <label className="grid gap-2 text-sm font-semibold text-neutral-700">Email<input value={form.email} onChange={(e) => setForm((c) => ({ ...c, email: e.target.value }))} className="h-11 rounded-lg border border-neutral-200 px-3 text-sm font-normal" /></label>
          <label className="grid gap-2 text-sm font-semibold text-neutral-700">Phone<input value={form.phone} onChange={(e) => setForm((c) => ({ ...c, phone: e.target.value }))} className="h-11 rounded-lg border border-neutral-200 px-3 text-sm font-normal" /></label>
          <label className="grid gap-2 text-sm font-semibold text-neutral-700">Professional category
            <select value={form.professional_category} onChange={(e) => setForm((c) => ({ ...c, professional_category: e.target.value }))} className="h-11 rounded-lg border border-neutral-200 px-3 text-sm font-normal bg-white">
              {PROFESSIONAL_CATEGORIES.map((category) => <option key={category} value={category}>{niceLabel(category)}</option>)}
            </select>
          </label>
          <label className="grid gap-2 text-sm font-semibold text-neutral-700">Platform role
            <select value={form.role} onChange={(e) => setForm((c) => ({ ...c, role: e.target.value }))} className="h-11 rounded-lg border border-neutral-200 px-3 text-sm font-normal bg-white">
              <option value="facility_admin">Facility admin</option>
              <option value="doctor">Doctor</option>
              <option value="lab_staff">Lab staff</option>
            </select>
          </label>
          <label className="grid gap-2 text-sm font-semibold text-neutral-700">Team role
            <select value={form.facility_role} onChange={(e) => setForm((c) => ({ ...c, facility_role: e.target.value }))} className="h-11 rounded-lg border border-neutral-200 px-3 text-sm font-normal bg-white">
              <option value="">Select facility role</option>
              {(rolesQuery.data ?? []).map((role) => <option key={role.id} value={role.id}>{role.name}</option>)}
            </select>
          </label>
          <label className="grid gap-2 text-sm font-semibold text-neutral-700">Staff type
            <select value={form.staff_type} onChange={(e) => setForm((c) => ({ ...c, staff_type: e.target.value }))} className="h-11 rounded-lg border border-neutral-200 px-3 text-sm font-normal bg-white">
              <option value="facility_admin">Facility admin</option>
              <option value="doctor">Doctor</option>
              <option value="lab_staff">Lab staff</option>
              <option value="records_staff">Records staff</option>
              <option value="finance_user">Finance</option>
              <option value="viewer">Viewer</option>
            </select>
          </label>
          {needsLicense ? (
            <>
              <label className="grid gap-2 text-sm font-semibold text-neutral-700">Licence number<input value={form.professional_registration_number} onChange={(e) => setForm((c) => ({ ...c, professional_registration_number: e.target.value }))} className="h-11 rounded-lg border border-neutral-200 px-3 text-sm font-normal" /></label>
              <label className="grid gap-2 text-sm font-semibold text-neutral-700">Licence issuing body<input value={form.license_issuing_body} onChange={(e) => setForm((c) => ({ ...c, license_issuing_body: e.target.value }))} className="h-11 rounded-lg border border-neutral-200 px-3 text-sm font-normal" /></label>
            </>
          ) : null}
          <label className="md:col-span-2 grid gap-2 text-sm font-semibold text-neutral-700">Message<textarea value={form.message} onChange={(e) => setForm((c) => ({ ...c, message: e.target.value }))} rows={4} className="rounded-lg border border-neutral-200 px-3 py-2 text-sm font-normal" /></label>
        </div>
        {selectedRole ? (
          <div className="mt-5 rounded-lg border border-brand-100 bg-brand-50 p-4">
            <div className="flex items-start gap-3">
              <ShieldCheck size={18} className="mt-0.5 text-brand-700" />
              <div>
                <p className="text-sm font-semibold text-brand-900">{selectedRole.name}</p>
                <p className="mt-1 text-sm text-brand-800">{selectedRole.description || "Custom facility role."}</p>
                <p className="mt-2 text-xs font-medium text-brand-700">Professional category: {niceLabel(selectedRole.professional_category)}</p>
              </div>
            </div>
          </div>
        ) : null}
        <div className="mt-6 flex justify-end gap-3">
          <Link href="/facility/team" className="inline-flex h-10 items-center rounded-lg border border-neutral-200 px-4 text-sm font-semibold text-neutral-700">Cancel</Link>
          <button type="button" disabled={mutation.isPending || !form.email || (needsLicense && (!form.professional_registration_number || !form.license_issuing_body))} onClick={() => mutation.mutate()} className="inline-flex h-10 items-center gap-2 rounded-lg bg-brand-600 px-4 text-sm font-semibold text-white disabled:opacity-60">{mutation.isPending ? "Sending..." : "Send invite"}</button>
        </div>
      </div>
    </PortalShell>
  );
}

export function FacilityTeamMemberDetailPage({ memberId }: { memberId: string }) {
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const facilityQuery = useQuery({ queryKey: ["current-facility"], queryFn: getCurrentMedicalFacility });
  const facilityId = facilityQuery.data?.id;
  const staffQuery = useQuery({ queryKey: ["facility-staff", facilityId], queryFn: () => listFacilityStaff(facilityId!), enabled: Boolean(facilityId) });
  const rolesQuery = useQuery({ queryKey: ["facility-roles", facilityId], queryFn: () => listFacilityRoles(facilityId!), enabled: Boolean(facilityId) });
  const member = (staffQuery.data ?? []).find((row) => row.id === memberId);
  const mutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => updateFacilityStaff(facilityId!, memberId, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["facility-staff", facilityId] }),
    onError: (err) => setError(getApiErrorMessage(err, "Could not update team member.")),
  });

  if (!member) {
    return <PortalShell role="facility_admin" title="Team Member" description="Manage the selected facility stakeholder."><TeamNav current="team" /><div className="rounded-lg border border-neutral-200 bg-white p-6 text-sm text-neutral-500">Loading team member details...</div></PortalShell>;
  }

  return (
    <PortalShell role="facility_admin" title="Team Member Detail" description="Review membership status, professional category, role assignment, and activation state.">
      <TeamNav current="team" />
      {error ? <div className="mb-4 rounded-lg border border-danger-100 bg-danger-50 px-4 py-3 text-sm font-semibold text-danger-700">{error}</div> : null}
      <div className="mb-4 flex items-center justify-between">
        <Link href="/facility/team" className="inline-flex items-center gap-2 text-sm font-semibold text-neutral-600"><ArrowLeft size={16} /> Back to team</Link>
        <div className="flex gap-2">
          {member.is_active ? (
            <button type="button" onClick={() => mutation.mutate({ is_active: false, status: "suspended" })} className="inline-flex h-10 items-center rounded-lg border border-danger-200 px-4 text-sm font-semibold text-danger-700">Suspend</button>
          ) : (
            <button type="button" onClick={() => mutation.mutate({ is_active: true, status: "active" })} className="inline-flex h-10 items-center rounded-lg border border-success-200 px-4 text-sm font-semibold text-success-700">Activate</button>
          )}
        </div>
      </div>
      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="grid h-12 w-12 place-items-center rounded-full bg-brand-50 text-brand-700"><Users size={20} /></div>
            <div><h2 className="text-lg font-bold text-neutral-900">{member.user_name || member.user_email}</h2><p className="text-sm text-neutral-500">{member.user_email}</p></div>
          </div>
          <dl className="mt-6 grid gap-4 sm:grid-cols-2">
            <div><dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Role</dt><dd className="mt-1 text-sm font-medium text-neutral-900">{member.role_name || niceLabel(member.staff_type)}</dd></div>
            <div><dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Professional category</dt><dd className="mt-1 text-sm font-medium text-neutral-900">{niceLabel(member.professional_category)}</dd></div>
            <div><dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Department</dt><dd className="mt-1 text-sm font-medium text-neutral-900">{member.department_name || "Unassigned"}</dd></div>
            <div><dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Status</dt><dd className="mt-1"><span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ring-1 ${statusTone(member.status)}`}>{niceLabel(member.status)}</span></dd></div>
            <div><dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Accepted at</dt><dd className="mt-1 text-sm font-medium text-neutral-900">{member.accepted_at ? new Date(member.accepted_at).toLocaleString("en-NG") : "Pending acceptance"}</dd></div>
            <div><dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Registration</dt><dd className="mt-1 text-sm font-medium text-neutral-900">{member.professional_registration_number || "Not provided"}</dd></div>
          </dl>
        </section>
        <section className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
          <h3 className="text-sm font-bold text-neutral-900">Quick reassignment</h3>
          <p className="mt-1 text-sm text-neutral-500">Move the team member to a different facility role without leaving this screen.</p>
          <div className="mt-4 space-y-3">
            {(rolesQuery.data ?? []).map((role) => (
              <button key={role.id} type="button" onClick={() => mutation.mutate({ role: role.id, professional_category: role.professional_category })} className={`w-full rounded-lg border px-4 py-3 text-left ${member.role === role.id ? "border-brand-300 bg-brand-50" : "border-neutral-200 bg-white hover:bg-neutral-50"}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-neutral-900">{role.name}</p>
                    <p className="text-xs text-neutral-500">{niceLabel(role.professional_category)} · {(role.permissions ?? []).length} permissions</p>
                  </div>
                  {member.role === role.id ? <ShieldCheck size={16} className="text-brand-700" /> : <UserCog size={16} className="text-neutral-400" />}
                </div>
              </button>
            ))}
          </div>
        </section>
      </div>
    </PortalShell>
  );
}

export function FacilityRolesPage() {
  const facilityQuery = useQuery({ queryKey: ["current-facility"], queryFn: getCurrentMedicalFacility });
  const facilityId = facilityQuery.data?.id;
  const rolesQuery = useQuery({ queryKey: ["facility-roles", facilityId], queryFn: () => listFacilityRoles(facilityId!), enabled: Boolean(facilityId) });

  return (
    <PortalShell role="facility_admin" title="Facility Roles" description="Configure default and custom facility workspace roles, permission coverage, and protected clinical access boundaries.">
      <TeamNav current="roles" />
      <div className="mb-5 flex justify-end">
        <Link href="/facility/roles/new" className="inline-flex h-10 items-center gap-2 rounded-lg bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700"><Plus size={16} /> New role</Link>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        {(rolesQuery.data ?? []).map((role) => (
          <article key={role.id} className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-bold text-neutral-900">{role.name}</h2>
                <p className="mt-1 text-sm text-neutral-500">{role.description || "Facility role."}</p>
              </div>
              <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${role.is_system_default ? "bg-brand-50 text-brand-700" : "bg-neutral-100 text-neutral-700"}`}>{role.is_system_default ? "Default" : "Custom"}</span>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <span className="rounded-full bg-neutral-100 px-3 py-1 text-xs font-semibold text-neutral-700">{niceLabel(role.professional_category)}</span>
              <span className="rounded-full bg-neutral-100 px-3 py-1 text-xs font-semibold text-neutral-700">{(role.permissions ?? []).length} permissions</span>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {(role.permissions ?? []).slice(0, 6).map((permission) => (
                <span key={permission.id} className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">{permission.permission_key}</span>
              ))}
            </div>
            <div className="mt-5 flex justify-end">
              <Link href={role.is_system_default ? `/facility/roles/${role.id}/edit` : `/facility/roles/${role.id}/edit`} className="inline-flex h-10 items-center rounded-lg border border-neutral-200 px-4 text-sm font-semibold text-neutral-700">Open role</Link>
            </div>
          </article>
        ))}
      </div>
    </PortalShell>
  );
}

export function FacilityRoleEditorPage({ roleId }: { roleId?: string }) {
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [professionalCategory, setProfessionalCategory] = useState("admin");
  const [selectedPermissionKeys, setSelectedPermissionKeys] = useState<string[]>([]);

  const facilityQuery = useQuery({ queryKey: ["current-facility"], queryFn: getCurrentMedicalFacility });
  const facilityId = facilityQuery.data?.id;
  const roleQuery = useQuery({
    queryKey: ["facility-role", facilityId, roleId],
    queryFn: () => getFacilityRole(facilityId!, roleId!),
    enabled: Boolean(facilityId && roleId),
  });
  const permissionsQuery = useQuery({ queryKey: ["org-permissions"], queryFn: () => import("@/lib/api/organizations").then((m) => m.fetchPermissions()) });

  const protectedPermissionRules: Record<string, string[]> = {
    "declaration.validate": ["doctor"],
    "physical_exam.create": ["doctor"],
    "doctor_review.final_decision": ["doctor"],
    "lab_results.create": ["lab_technician", "lab_scientist", "lab_supervisor"],
    "lab_results.submit": ["lab_technician", "lab_scientist", "lab_supervisor"],
  };

  useEffect(() => {
    if (roleQuery.data) {
      setName(roleQuery.data.name);
      setDescription(roleQuery.data.description || "");
      setProfessionalCategory(roleQuery.data.professional_category);
      setSelectedPermissionKeys((roleQuery.data.permissions ?? []).filter((p) => p.allowed).map((p) => p.permission_key));
    }
  }, [roleQuery.data]);

  const mutation = useMutation({
    mutationFn: async () => {
      const payload = { name, description, professional_category: professionalCategory, permission_keys: selectedPermissionKeys };
      if (roleId) {
        return updateFacilityRole(facilityId!, roleId, payload);
      }
      return createFacilityRole(facilityId!, payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["facility-roles", facilityId] });
      setError(null);
    },
    onError: (err) => setError(getApiErrorMessage(err, "Could not save facility role.")),
  });

  const permissions = permissionsQuery.data ?? [];
  const groupedPermissions = permissions.reduce<Record<string, typeof permissions>>((acc, permission) => {
    (acc[permission.module] ??= []).push(permission);
    return acc;
  }, {});

  function togglePermission(permissionKey: string) {
    const allowedCategories = protectedPermissionRules[permissionKey];
    if (allowedCategories && !allowedCategories.includes(professionalCategory)) return;
    setSelectedPermissionKeys((current) => current.includes(permissionKey) ? current.filter((key) => key !== permissionKey) : [...current, permissionKey]);
  }

  return (
    <PortalShell role="facility_admin" title={roleId ? "Edit Facility Role" : "New Facility Role"} description="Create custom facility roles and assign only the permissions that fit the declared professional category.">
      <TeamNav current="roles" />
      {error ? <div className="mb-4 rounded-lg border border-danger-100 bg-danger-50 px-4 py-3 text-sm font-semibold text-danger-700">{error}</div> : null}
      <div className="grid gap-6 xl:grid-cols-[0.7fr_1.3fr]">
        <section className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-bold text-neutral-900">Role setup</h2>
          <div className="mt-5 space-y-4">
            <label className="grid gap-2 text-sm font-semibold text-neutral-700">Role name<input value={name} onChange={(e) => setName(e.target.value)} className="h-11 rounded-lg border border-neutral-200 px-3 text-sm font-normal" /></label>
            <label className="grid gap-2 text-sm font-semibold text-neutral-700">Professional category
              <select value={professionalCategory} onChange={(e) => setProfessionalCategory(e.target.value)} className="h-11 rounded-lg border border-neutral-200 px-3 text-sm font-normal bg-white">
                {PROFESSIONAL_CATEGORIES.map((category) => <option key={category} value={category}>{niceLabel(category)}</option>)}
              </select>
            </label>
            <label className="grid gap-2 text-sm font-semibold text-neutral-700">Description<textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={4} className="rounded-lg border border-neutral-200 px-3 py-2 text-sm font-normal" /></label>
          </div>
          <div className="mt-6 rounded-lg border border-warning-200 bg-warning-50 p-4 text-sm text-warning-900">
            <div className="flex gap-3">
              <AlertCircle size={18} className="mt-0.5 shrink-0" />
              <p>Protected clinical permissions stay disabled unless the selected professional category is allowed to hold them.</p>
            </div>
          </div>
          <div className="mt-6 flex justify-end gap-3">
            <Link href="/facility/roles" className="inline-flex h-10 items-center rounded-lg border border-neutral-200 px-4 text-sm font-semibold text-neutral-700">Cancel</Link>
            <button type="button" onClick={() => mutation.mutate()} disabled={mutation.isPending || !name.trim()} className="inline-flex h-10 items-center rounded-lg bg-brand-600 px-4 text-sm font-semibold text-white disabled:opacity-60">{mutation.isPending ? "Saving..." : "Save role"}</button>
          </div>
        </section>
        <section className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-bold text-neutral-900">Permissions</h2>
          <div className="mt-5 space-y-5">
            {Object.entries(groupedPermissions).map(([module, items]) => (
              <div key={module}>
                <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-neutral-500">{niceLabel(module)}</h3>
                <div className="grid gap-3 md:grid-cols-2">
                  {items.map((permission) => {
                    const allowedCategories = protectedPermissionRules[permission.code];
                    const blocked = allowedCategories && !allowedCategories.includes(professionalCategory);
                    const selected = selectedPermissionKeys.includes(permission.code);
                    return (
                      <button
                        key={permission.id}
                        type="button"
                        disabled={Boolean(blocked)}
                        onClick={() => togglePermission(permission.code)}
                        className={`rounded-lg border p-4 text-left ${selected ? "border-brand-300 bg-brand-50" : "border-neutral-200 bg-white"} ${blocked ? "cursor-not-allowed opacity-50" : "hover:bg-neutral-50"}`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="text-sm font-semibold text-neutral-900">{permission.name}</p>
                            <p className="mt-1 text-xs text-neutral-500">{permission.code}</p>
                          </div>
                          {selected ? <ShieldCheck size={16} className="text-brand-700" /> : blocked ? <UserX size={16} className="text-danger-600" /> : null}
                        </div>
                        {blocked ? <p className="mt-2 text-xs font-medium text-danger-700">Allowed for: {allowedCategories.join(", ")}</p> : null}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
