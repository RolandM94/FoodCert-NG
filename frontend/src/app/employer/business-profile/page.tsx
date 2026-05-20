"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Save, AlertCircle, Building2 } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { apiClient, unwrap } from "@/lib/api/client";

type EmployerProfile = {
  id: string;
  business_name: string;
  business_registration_number: string;
  business_type: string;
  establishment_category: string;
  contact_person_name: string;
  contact_person_phone: string;
  contact_person_email: string;
  address: string;
  state?: string;
  state_name?: string;
  lga?: string;
  lga_name?: string;
  ward: string;
  number_of_food_handlers: number;
  compliance_status: string;
  subscription_status: string;
  is_active: boolean;
};

const CATEGORIES = [
  { value: "restaurant_cafe", label: "Restaurant / Cafe" },
  { value: "bakery", label: "Bakery / Pastry Shop" },
  { value: "abattoir_butcher", label: "Abattoir / Butcher Shop" },
  { value: "grocery_supermarket", label: "Grocery / Supermarket" },
  { value: "food_truck_street_vendor", label: "Food Truck / Street Vendor" },
  { value: "catering", label: "Catering Service" },
  { value: "school_cafeteria", label: "School Cafeteria" },
  { value: "hospital_kitchen", label: "Hospital Kitchen" },
  { value: "bar_pub", label: "Bar / Pub" },
  { value: "food_processing_plant", label: "Food Processing Plant" },
  { value: "hotel_resort", label: "Hotel / Resort" },
  { value: "corporate_dining", label: "Corporate Dining" },
  { value: "food_market_stall", label: "Food Market / Stall" },
  { value: "farm_feed_processing", label: "Farm / Feed Processing" },
  { value: "daycare", label: "Daycare Centre" },
  { value: "other", label: "Other" },
];

export default function Page() {
  const router = useRouter();
  const [profile, setProfile] = useState<EmployerProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [form, setForm] = useState<Partial<EmployerProfile>>({});

  useEffect(() => {
    const token = localStorage.getItem("foodcert_access_token");
    if (!token) { router.push("/login"); return; }

    apiClient.get("/employers/me/")
      .then((res) => {
        const data = unwrap(res.data) as EmployerProfile;
        setProfile(data);
        setForm({
          business_name: data.business_name,
          business_registration_number: data.business_registration_number,
          establishment_category: data.establishment_category,
          contact_person_name: data.contact_person_name,
          contact_person_phone: data.contact_person_phone,
          contact_person_email: data.contact_person_email,
          address: data.address,
          ward: data.ward,
          number_of_food_handlers: data.number_of_food_handlers,
        });
      })
      .catch(() => setError("Failed to load profile. Are you registered as an employer?"))
      .finally(() => setLoading(false));
  }, [router]);

  function update(field: string, value: string | number) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setSuccess("");
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!profile) return;
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      const res = await apiClient.patch(`/employers/${profile.id}/`, form);
      const updated = unwrap(res.data) as EmployerProfile;
      setProfile(updated);
      setSuccess("Profile updated successfully.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save profile.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <PortalShell role="employer" title="Business Profile" description="Loading..."><p className="text-slate-500 text-sm">Loading profile...</p></PortalShell>;
  }

  if (!profile) {
    return <PortalShell role="employer" title="Business Profile" description=""><p className="text-red-600 text-sm">{error || "No employer profile found."}</p></PortalShell>;
  }

  return (
    <PortalShell role="employer" title="Business Profile" description="Manage your business details, contact information, and establishment category.">
      <form className="grid gap-5" onSubmit={handleSave}>
        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3 mb-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-brand-deep">
              <Building2 size={20} />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-950">Business Details</h2>
              <p className="text-xs text-slate-500">Establishment category: {CATEGORIES.find((c) => c.value === profile.establishment_category)?.label || profile.establishment_category}</p>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Business name <span className="text-red-500">*</span>
              <input className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" required value={form.business_name || ""} onChange={(e) => update("business_name", e.target.value)} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Registration number
              <input className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" value={form.business_registration_number || ""} onChange={(e) => update("business_registration_number", e.target.value)} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Category <span className="text-red-500">*</span>
              <select className="h-11 rounded-lg border border-slate-200 bg-white px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" value={form.establishment_category || ""} onChange={(e) => update("establishment_category", e.target.value)}>
                {CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
              </select>
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Est. food handlers
              <input className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" type="number" min={0} value={form.number_of_food_handlers ?? 0} onChange={(e) => update("number_of_food_handlers", Number(e.target.value))} />
            </label>
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-sm font-bold text-slate-950 mb-4">Contact Information</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Contact person
              <input className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" value={form.contact_person_name || ""} onChange={(e) => update("contact_person_name", e.target.value)} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Contact phone <span className="text-red-500">*</span>
              <input className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" required value={form.contact_person_phone || ""} onChange={(e) => update("contact_person_phone", e.target.value)} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Contact email
              <input className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" type="email" value={form.contact_person_email || ""} onChange={(e) => update("contact_person_email", e.target.value)} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Address <span className="text-red-500">*</span>
              <input className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" required value={form.address || ""} onChange={(e) => update("address", e.target.value)} />
            </label>
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-sm font-bold text-slate-950 mb-4">Status</h2>
          <div className="grid gap-3 sm:grid-cols-3 text-sm">
            <div>
              <span className="text-xs font-bold uppercase text-slate-500">Compliance</span>
              <p className="text-sm font-semibold text-slate-800 capitalize">{profile.compliance_status?.replace(/_/g, " ") || "N/A"}</p>
            </div>
            <div>
              <span className="text-xs font-bold uppercase text-slate-500">Subscription</span>
              <p className="text-sm font-semibold text-slate-800 capitalize">{profile.subscription_status?.replace(/_/g, " ") || "N/A"}</p>
            </div>
            <div>
              <span className="text-xs font-bold uppercase text-slate-500">Account</span>
              <p className={`text-sm font-semibold ${profile.is_active ? "text-emerald-700" : "text-red-600"}`}>{profile.is_active ? "Active" : "Inactive"}</p>
            </div>
          </div>
        </div>

        {error && <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} className="mt-0.5 shrink-0" /><span>{error}</span></div>}
        {success && <div className="rounded-lg bg-emerald-50 p-3 text-sm font-semibold text-emerald-800">{success}</div>}

        <button className="inline-flex h-11 w-full sm:w-auto items-center justify-center gap-2 rounded-lg bg-brand-green px-6 text-sm font-bold text-white hover:bg-brand-deep disabled:opacity-60" disabled={saving} type="submit">
          <Save size={16} />
          {saving ? "Saving..." : "Save changes"}
        </button>
      </form>
    </PortalShell>
  );
}
