"use client";

import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { AlertCircle, Building2, Clock, MapPin, Save, ShieldCheck } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { getCurrentMedicalFacility, updateCurrentMedicalFacility } from "@/lib/api/facilities";
import type { MedicalFacility } from "@/types/facilities";

const FACILITY_TYPES = [
  ["hospital", "Hospital"],
  ["clinic", "Clinic"],
  ["diagnostic_centre", "Diagnostic centre"],
  ["primary_health_centre", "Primary healthcare centre"],
  ["mobile_health_unit", "Mobile health unit"],
];

const OWNERSHIP_TYPES = [
  ["public", "Public"],
  ["private", "Private"],
  ["mission", "Mission"],
  ["ngo", "NGO"],
];

type FacilityProfileForm = {
  facility_name: string;
  facility_type: string;
  ownership_type: string;
  license_number: string;
  registration_number: string;
  address: string;
  ward: string;
  contact_person: string;
  phone: string;
  email: string;
  operating_hours: string;
  service_capacity: number;
  standard_assessment_price: string;
};

function buildForm(facility: MedicalFacility): FacilityProfileForm {
  return {
    facility_name: facility.facility_name || "",
    facility_type: facility.facility_type || "clinic",
    ownership_type: facility.ownership_type || "private",
    license_number: facility.license_number || "",
    registration_number: facility.registration_number || "",
    address: facility.address || "",
    ward: facility.ward || "",
    contact_person: facility.contact_person || "",
    phone: facility.phone || "",
    email: facility.email || "",
    operating_hours: facility.operating_hours || "",
    service_capacity: facility.service_capacity || 0,
    standard_assessment_price: facility.standard_assessment_price || "0.00",
  };
}

function formatDate(value?: string) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const [facility, setFacility] = useState<MedicalFacility | null>(null);
  const [form, setForm] = useState<FacilityProfileForm | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    getCurrentMedicalFacility()
      .then((profile) => {
        setFacility(profile);
        setForm(buildForm(profile));
      })
      .catch(() => setError("No facility profile could be loaded for this account."))
      .finally(() => setLoading(false));
  }, []);

  function update(field: keyof FacilityProfileForm, value: string | number) {
    setForm((current) => current ? { ...current, [field]: value } : current);
    setSuccess("");
  }

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!form) return;
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      const updated = await updateCurrentMedicalFacility(form);
      setFacility(updated);
      setForm(buildForm(updated));
      setSuccess("Facility profile updated.");
    } catch {
      setError("Could not save facility profile.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <PortalShell role="facility_admin" title="Facility profile" description="Maintain facility registration, license, and contact information.">
        <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading facility profile...</p>
      </PortalShell>
    );
  }

  if (!facility || !form) {
    return (
      <PortalShell role="facility_admin" title="Facility profile" description="Maintain facility registration, license, and contact information.">
        <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm font-semibold text-rose-800">{error || "Facility profile not found."}</div>
      </PortalShell>
    );
  }

  return (
    <PortalShell role="facility_admin" title="Facility profile" description="Maintain facility registration, license, and contact information.">
      <form className="grid gap-5" onSubmit={saveProfile}>
        <section className="grid gap-4 md:grid-cols-4">
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Accreditation</p>
            <div className="mt-2"><StatusBadge status={facility.accreditation_status} /></div>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Profile</p>
            <p className={`mt-2 text-sm font-bold ${facility.profile_complete ? "text-emerald-700" : "text-amber-700"}`}>{facility.profile_complete ? "Complete" : "Needs attention"}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Assessment ready</p>
            <p className={`mt-2 text-sm font-bold ${facility.can_conduct_assessments ? "text-emerald-700" : "text-slate-600"}`}>{facility.can_conduct_assessments ? "Yes" : "No"}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Accreditation expiry</p>
            <p className="mt-2 text-sm font-bold text-slate-800">{formatDate(facility.accreditation_expiry_date)}</p>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-5 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-brand-deep"><Building2 size={20} /></div>
            <div>
              <h2 className="text-sm font-bold text-slate-950">Facility Details</h2>
              <p className="text-xs text-slate-500">Registration and licensing details used for accreditation review.</p>
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Facility name
              <input required className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" value={form.facility_name} onChange={(event) => update("facility_name", event.target.value)} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Facility type
              <select className="h-11 rounded-lg border border-slate-200 bg-white px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" value={form.facility_type} onChange={(event) => update("facility_type", event.target.value)}>
                {FACILITY_TYPES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Ownership
              <select className="h-11 rounded-lg border border-slate-200 bg-white px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" value={form.ownership_type} onChange={(event) => update("ownership_type", event.target.value)}>
                {OWNERSHIP_TYPES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Facility license number
              <input required className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" value={form.license_number} onChange={(event) => update("license_number", event.target.value)} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Registration number
              <input className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" value={form.registration_number} onChange={(event) => update("registration_number", event.target.value)} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Standard assessment price
              <input className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" inputMode="decimal" value={form.standard_assessment_price} onChange={(event) => update("standard_assessment_price", event.target.value)} />
            </label>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-5 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-sky-50 text-sky-800"><MapPin size={20} /></div>
            <div>
              <h2 className="text-sm font-bold text-slate-950">Location and Contact</h2>
              <p className="text-xs text-slate-500">State and LGA are shown from the facility record; update them during formal profile correction where required.</p>
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              State
              <input readOnly className="h-11 rounded-lg border border-slate-200 bg-slate-100 px-3 text-slate-600" value={facility.state_name || "Not set"} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              LGA
              <input readOnly className="h-11 rounded-lg border border-slate-200 bg-slate-100 px-3 text-slate-600" value={facility.lga_name || "Not set"} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Ward
              <input className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" value={form.ward} onChange={(event) => update("ward", event.target.value)} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700 md:col-span-2">
              Address
              <input required className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" value={form.address} onChange={(event) => update("address", event.target.value)} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Contact person
              <input required className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" value={form.contact_person} onChange={(event) => update("contact_person", event.target.value)} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Phone
              <input required className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" value={form.phone} onChange={(event) => update("phone", event.target.value)} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Email
              <input required type="email" className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" value={form.email} onChange={(event) => update("email", event.target.value)} />
            </label>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-5 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50 text-amber-800"><Clock size={20} /></div>
            <div>
              <h2 className="text-sm font-bold text-slate-950">Operational Capacity</h2>
              <p className="text-xs text-slate-500">Used by accreditation reviewers and appointment planning.</p>
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Operating hours
              <input className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" placeholder="Mon-Fri 8:00-17:00" value={form.operating_hours} onChange={(event) => update("operating_hours", event.target.value)} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Daily service capacity
              <input className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" min={0} type="number" value={form.service_capacity} onChange={(event) => update("service_capacity", Number(event.target.value))} />
            </label>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex items-start gap-3">
            <ShieldCheck className="mt-0.5 shrink-0 text-brand-deep" size={18} />
            <p className="text-sm text-slate-600">Facility profile edits are audit logged. Accreditation approval, suspension, expiry, and certificate authority remain controlled by the State Ministry.</p>
          </div>
        </section>

        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} className="mt-0.5 shrink-0" />{error}</div> : null}
        {success ? <div className="rounded-lg bg-emerald-50 p-3 text-sm font-semibold text-emerald-800">{success}</div> : null}

        <button className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-brand-green px-6 text-sm font-bold text-white hover:bg-brand-deep disabled:opacity-60 sm:w-fit" disabled={saving} type="submit">
          <Save size={16} />
          {saving ? "Saving..." : "Save profile"}
        </button>
      </form>
    </PortalShell>
  );
}
