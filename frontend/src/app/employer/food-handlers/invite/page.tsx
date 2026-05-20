"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Send, AlertCircle, MapPin } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { apiClient, unwrap } from "@/lib/api/client";

type Branch = {
  id: string;
  name: string;
};

export default function Page() {
  const router = useRouter();
  const [employerId, setEmployerId] = useState<string | null>(null);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [form, setForm] = useState({
    email: "",
    phone: "",
    food_handler_category: "kitchen_staff",
    branch: "",
    message: "",
  });

  const categories = [
    { value: "kitchen_staff", label: "Kitchen Staff" },
    { value: "food_preparer", label: "Food Preparer" },
    { value: "serving_catering", label: "Serving / Catering" },
    { value: "food_packer", label: "Food Packer" },
    { value: "bakery_worker", label: "Bakery Worker" },
    { value: "bartender", label: "Bartender" },
    { value: "food_delivery", label: "Food Delivery" },
    { value: "street_vendor", label: "Street Vendor" },
    { value: "dishwasher", label: "Dishwasher" },
  ];

  useEffect(() => {
    const token = localStorage.getItem("foodcert_access_token");
    if (!token) { router.push("/login"); return; }
    apiClient.get("/employers/me/")
      .then((res) => {
        const profile = unwrap(res.data) as { id: string; organization: string };
        setEmployerId(profile.id);
        return apiClient.get(`/organizations/${profile.organization}/units/`);
      })
      .then((res) => {
        const units = unwrap(res.data) as Branch[];
        setBranches(units.filter((u: Record<string, unknown>) => u.unit_type === "branch"));
      })
      .catch(() => {});
  }, [router]);

  function update(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setError("");
    setSuccess("");
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!employerId) return;
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      const res = await apiClient.post(`/employers/${employerId}/invite-food-handler/`, {
        email: form.email,
        phone: form.phone,
        unit: form.branch || undefined,
      });
      unwrap(res.data);
      setSuccess(`Invitation sent to ${form.email || form.phone}.`);
      setForm({ email: "", phone: "", food_handler_category: "kitchen_staff", branch: "", message: "" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send invitation.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <PortalShell role="employer" title="Invite Food Handler" description="Send an invitation to a food handler. They will receive a link to register and join your business.">
      <form className="max-w-xl rounded-lg border border-slate-200 bg-white p-6 shadow-sm" onSubmit={handleSubmit}>
        <div className="grid gap-4">
          <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
            Email
            <input className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3" type="email" required value={form.email} onChange={(e) => update("email", e.target.value)} placeholder="handler@example.com" />
          </label>
          <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
            Phone
            <input className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3" value={form.phone} onChange={(e) => update("phone", e.target.value)} placeholder="08030000000" />
          </label>
          <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
            Category
            <select className="h-11 rounded-lg border border-slate-200 bg-white px-3" value={form.food_handler_category} onChange={(e) => update("food_handler_category", e.target.value)}>
              {categories.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
            </select>
          </label>
          {branches.length > 0 && (
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              <span className="flex items-center gap-1.5"><MapPin size={14} /> Branch</span>
              <select className="h-11 rounded-lg border border-slate-200 bg-white px-3" value={form.branch} onChange={(e) => update("branch", e.target.value)}>
                <option value="">All branches (no assignment)</option>
                {branches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
              </select>
            </label>
          )}
          <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
            Message (optional)
            <textarea className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm" rows={2} value={form.message} onChange={(e) => update("message", e.target.value)} placeholder="Welcome message..." />
          </label>
        </div>

        {error && <div className="mt-4 flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} className="mt-0.5 shrink-0" /><span>{error}</span></div>}
        {success && <div className="mt-4 rounded-lg bg-emerald-50 p-3 text-sm font-semibold text-emerald-800">{success}</div>}

        <button className="mt-5 inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-brand-green text-sm font-bold text-white hover:bg-brand-deep disabled:opacity-60" disabled={loading} type="submit">
          <Send size={16} />
          {loading ? "Sending..." : "Send Invitation"}
        </button>
      </form>
    </PortalShell>
  );
}
