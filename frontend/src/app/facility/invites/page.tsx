"use client";

import { useEffect, useState } from "react";
import { AlertCircle, Clock3, RefreshCw, Send, Trash2, UserPlus } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import {
  createFacilityInvite,
  getCurrentMedicalFacility,
  listFacilityInvites,
  revokeFacilityInvite,
} from "@/lib/api/facilities";
import { fetchUnits } from "@/lib/api/organizations";
import type { FacilityInvite, MedicalFacility } from "@/types/facilities";
import type { OrganizationUnit } from "@/types/organizations";

const STAFF_TYPES = [
  ["doctor", "Doctor"],
  ["lab_staff", "Lab staff"],
  ["records_staff", "Medical records staff"],
  ["finance_user", "Finance / settlement user"],
  ["viewer", "Viewer"],
];

const ROLE_BY_STAFF_TYPE: Record<string, string> = {
  doctor: "doctor",
  lab_staff: "lab_staff",
  records_staff: "facility_admin",
  finance_user: "facility_admin",
  viewer: "facility_admin",
};

function label(value: string) {
  return value.replaceAll("_", " ");
}

function formatDate(value?: string) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function Page() {
  const [facility, setFacility] = useState<MedicalFacility | null>(null);
  const [invites, setInvites] = useState<FacilityInvite[]>([]);
  const [departments, setDepartments] = useState<OrganizationUnit[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [form, setForm] = useState({
    email: "",
    phone: "",
    staff_type: "doctor",
    department: "",
    message: "",
  });

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      const profile = await getCurrentMedicalFacility();
      const [inviteRows, unitRows] = await Promise.all([
        listFacilityInvites(profile.id),
        fetchUnits(profile.organization),
      ]);
      setFacility(profile);
      setInvites(inviteRows);
      setDepartments(unitRows.filter((unit) => unit.is_active));
    } catch {
      setError("Could not load facility invites.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  function update(field: string, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
    setSuccess("");
  }

  async function sendInvite(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!facility) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await createFacilityInvite(facility.id, {
        email: form.email,
        phone: form.phone,
        role: ROLE_BY_STAFF_TYPE[form.staff_type],
        staff_type: form.staff_type,
        department: form.department || null,
        message: form.message,
      });
      setForm({ email: "", phone: "", staff_type: "doctor", department: "", message: "" });
      setSuccess("Invite sent.");
      await loadData();
    } catch {
      setError("Could not send invite.");
    } finally {
      setBusy(false);
    }
  }

  async function revokeInvite(invite: FacilityInvite) {
    if (!facility) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const updated = await revokeFacilityInvite(facility.id, invite.id);
      setInvites((rows) => rows.map((row) => row.id === updated.id ? updated : row));
      setSuccess("Invite revoked.");
    } catch {
      setError("Could not revoke invite.");
    } finally {
      setBusy(false);
    }
  }

  const pendingCount = invites.filter((invite) => invite.status === "pending").length;
  const acceptedCount = invites.filter((invite) => invite.status === "accepted").length;
  const departmentScopedCount = invites.filter((invite) => Boolean(invite.unit)).length;

  return (
    <PortalShell role="facility_admin" title="Facility Invites" description="Invite and track doctors, lab staff, records staff, finance users, and department-scoped facility users.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading invites...</p> : null}

        <section className="grid gap-3 md:grid-cols-3">
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <UserPlus className="text-brand-deep" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-slate-500">Pending</p>
            <p className="text-2xl font-bold text-slate-950">{pendingCount}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <Clock3 className="text-brand-deep" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-slate-500">Accepted</p>
            <p className="text-2xl font-bold text-slate-950">{acceptedCount}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <RefreshCw className="text-brand-deep" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-slate-500">Department scoped</p>
            <p className="text-2xl font-bold text-slate-950">{departmentScopedCount}</p>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <UserPlus className="text-brand-deep" size={18} />
            <h2 className="text-sm font-bold text-slate-950">Send Invite</h2>
          </div>
          <form className="grid gap-3 md:grid-cols-3" onSubmit={sendInvite}>
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" required placeholder="Email" type="email" value={form.email} onChange={(event) => update("email", event.target.value)} />
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" placeholder="Phone" value={form.phone} onChange={(event) => update("phone", event.target.value)} />
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={form.staff_type} onChange={(event) => update("staff_type", event.target.value)}>
              {STAFF_TYPES.map(([value, text]) => <option key={value} value={value}>{text}</option>)}
            </select>
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={form.department} onChange={(event) => update("department", event.target.value)}>
              <option value="">No department restriction</option>
              {departments.map((department) => <option key={department.id} value={department.id}>{department.name}</option>)}
            </select>
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm md:col-span-2" placeholder="Message" value={form.message} onChange={(event) => update("message", event.target.value)} />
            <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep disabled:opacity-60 md:w-fit" disabled={busy} type="submit">
              <Send size={16} /> Send invite
            </button>
          </form>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 p-4">
            <h2 className="text-sm font-bold text-slate-950">Invite Register</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs font-bold uppercase text-slate-500">
                <tr><th className="p-3">Invitee</th><th className="p-3">Staff type</th><th className="p-3">Department</th><th className="p-3">Expires</th><th className="p-3">Status</th><th className="p-3">Action</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {invites.length ? invites.map((invite) => (
                  <tr key={invite.id}>
                    <td className="p-3"><p className="font-bold text-slate-950">{invite.email}</p><p className="text-xs text-slate-500">{invite.phone || "No phone"}</p></td>
                    <td className="p-3 capitalize">{label(invite.facility_staff_type || invite.role)}</td>
                    <td className="p-3">{invite.unit_name || "Not restricted"}</td>
                    <td className="p-3">{formatDate(invite.expires_at)}</td>
                    <td className="p-3"><StatusBadge status={invite.status} /></td>
                    <td className="p-3">
                      <button className="inline-flex h-8 items-center justify-center gap-2 rounded border border-slate-200 px-3 text-xs font-bold text-slate-700 disabled:opacity-60" disabled={busy || invite.status !== "pending"} type="button" onClick={() => void revokeInvite(invite)}>
                        <Trash2 size={14} /> Revoke
                      </button>
                    </td>
                  </tr>
                )) : (
                  <tr><td className="p-3 text-slate-500" colSpan={6}>No invites yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} />{error}</div> : null}
        {success ? <div className="rounded-lg bg-emerald-50 p-3 text-sm font-semibold text-emerald-800">{success}</div> : null}
      </div>
    </PortalShell>
  );
}
