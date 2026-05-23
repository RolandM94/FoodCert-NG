"use client";

import { useEffect, useState } from "react";
import { AlertCircle, RefreshCw, Send, UserPlus, UsersRound } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import {
  createFacilityInvite,
  getCurrentMedicalFacility,
  listFacilityInvites,
  listFacilityStaff,
  reactivateFacilityStaff,
  suspendFacilityStaff,
} from "@/lib/api/facilities";
import { fetchUnits } from "@/lib/api/organizations";
import type { FacilityInvite, FacilityStaffProfile, MedicalFacility } from "@/types/facilities";
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

export default function Page() {
  const [facility, setFacility] = useState<MedicalFacility | null>(null);
  const [staff, setStaff] = useState<FacilityStaffProfile[]>([]);
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
    professional_registration_number: "",
    message: "",
  });

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      const profile = await getCurrentMedicalFacility();
      const [staffRows, inviteRows, unitRows] = await Promise.all([
        listFacilityStaff(profile.id),
        listFacilityInvites(profile.id),
        fetchUnits(profile.organization),
      ]);
      setFacility(profile);
      setStaff(staffRows);
      setInvites(inviteRows);
      setDepartments(unitRows.filter((unit) => unit.is_active));
    } catch {
      setError("Could not load facility staff.");
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

  async function inviteStaff(event: React.FormEvent<HTMLFormElement>) {
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
        professional_registration_number: form.professional_registration_number,
        message: form.message,
      });
      setForm({ email: "", phone: "", staff_type: "doctor", department: "", professional_registration_number: "", message: "" });
      setSuccess("Invite sent.");
      await loadData();
    } catch {
      setError("Could not send invite.");
    } finally {
      setBusy(false);
    }
  }

  async function toggleStaff(profile: FacilityStaffProfile) {
    if (!facility) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const updated = profile.is_active
        ? await suspendFacilityStaff(facility.id, profile.id)
        : await reactivateFacilityStaff(facility.id, profile.id);
      setStaff((rows) => rows.map((row) => row.id === updated.id ? updated : row));
      setSuccess(profile.is_active ? "Staff suspended." : "Staff reactivated.");
    } catch {
      setError("Could not update staff status.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <PortalShell role="facility_admin" title="Staff" description="Manage facility doctors, lab staff, records staff, finance users, and viewers.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading staff...</p> : null}

        <section className="grid gap-3 md:grid-cols-3">
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <UsersRound className="text-brand-deep" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-slate-500">Active staff</p>
            <p className="text-2xl font-bold text-slate-950">{staff.filter((row) => row.is_active).length}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <UserPlus className="text-brand-deep" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-slate-500">Pending invites</p>
            <p className="text-2xl font-bold text-slate-950">{invites.filter((row) => row.status === "pending").length}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <RefreshCw className="text-brand-deep" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-slate-500">Departments</p>
            <p className="text-2xl font-bold text-slate-950">{departments.length}</p>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <UserPlus className="text-brand-deep" size={18} />
            <h2 className="text-sm font-bold text-slate-950">Invite Staff</h2>
          </div>
          <form className="grid gap-3 md:grid-cols-3" onSubmit={inviteStaff}>
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" required placeholder="Email" type="email" value={form.email} onChange={(event) => update("email", event.target.value)} />
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" placeholder="Phone" value={form.phone} onChange={(event) => update("phone", event.target.value)} />
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={form.staff_type} onChange={(event) => update("staff_type", event.target.value)}>
              {STAFF_TYPES.map(([value, text]) => <option key={value} value={value}>{text}</option>)}
            </select>
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={form.department} onChange={(event) => update("department", event.target.value)}>
              <option value="">No department</option>
              {departments.map((department) => <option key={department.id} value={department.id}>{department.name}</option>)}
            </select>
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" placeholder="Professional registration no." value={form.professional_registration_number} onChange={(event) => update("professional_registration_number", event.target.value)} />
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" placeholder="Message" value={form.message} onChange={(event) => update("message", event.target.value)} />
            <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep disabled:opacity-60 md:w-fit" disabled={busy} type="submit">
              <Send size={16} /> Send invite
            </button>
          </form>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 p-4">
            <h2 className="text-sm font-bold text-slate-950">Staff Directory</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs font-bold uppercase text-slate-500">
                <tr><th className="p-3">Staff</th><th className="p-3">Role</th><th className="p-3">Department</th><th className="p-3">Professional no.</th><th className="p-3">Status</th><th className="p-3">Action</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {staff.length ? staff.map((row) => (
                  <tr key={row.id}>
                    <td className="p-3"><p className="font-bold text-slate-950">{row.user_name || row.user_email}</p><p className="text-xs text-slate-500">{row.user_email}</p></td>
                    <td className="p-3 capitalize">{label(row.staff_type)}</td>
                    <td className="p-3">{row.department_name || "Not assigned"}</td>
                    <td className="p-3">{row.professional_registration_number || "Not set"}</td>
                    <td className="p-3"><StatusBadge status={row.is_active ? "active" : "suspended"} /></td>
                    <td className="p-3"><button className="rounded border border-slate-200 px-3 py-1.5 text-xs font-bold text-slate-700 disabled:opacity-60" disabled={busy} type="button" onClick={() => void toggleStaff(row)}>{row.is_active ? "Suspend" : "Reactivate"}</button></td>
                  </tr>
                )) : (
                  <tr><td className="p-3 text-slate-500" colSpan={6}>No staff profiles yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 p-4">
            <h2 className="text-sm font-bold text-slate-950">Pending Invites</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs font-bold uppercase text-slate-500">
                <tr><th className="p-3">Email</th><th className="p-3">Role</th><th className="p-3">Department</th><th className="p-3">Status</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {invites.length ? invites.map((invite) => (
                  <tr key={invite.id}>
                    <td className="p-3 font-semibold text-slate-900">{invite.email}</td>
                    <td className="p-3 capitalize">{label(invite.facility_staff_type || invite.role)}</td>
                    <td className="p-3">{invite.unit_name || "Not assigned"}</td>
                    <td className="p-3"><StatusBadge status={invite.status} /></td>
                  </tr>
                )) : (
                  <tr><td className="p-3 text-slate-500" colSpan={4}>No invites yet.</td></tr>
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
