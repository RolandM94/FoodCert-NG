"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertTriangle, FileBadge, Filter, HeartPulse, Search, UsersRound } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { FitnessStatusBadge } from "@/components/ui/fitness-status-badge";
import { apiClient, unwrap } from "@/lib/api/client";
import type { OrganizationUnit } from "@/types/organizations";

type FoodHandlerRow = {
  id: string;
  full_name: string;
  phone: string;
  business_branch?: string;
  business_branch_name?: string;
  food_handler_category: string;
  fitness_status: string;
  fitness_label: string;
  certificate_number?: string;
  certificate_expiry_date?: string;
  certificate_status: string;
  typhoid_status: string;
  typhoid_expiry_date?: string;
  hepatitis_a_status: string;
  last_assessment_date?: string;
  return_to_work_status?: { clearance_status: string } | null;
};

const CATEGORY_OPTIONS = [
  { value: "", label: "All categories" },
  { value: "kitchen_staff", label: "Kitchen Staff" },
  { value: "food_preparer", label: "Food Preparer" },
  { value: "serving_catering", label: "Serving / Catering" },
  { value: "food_packer", label: "Food Packer" },
  { value: "bakery_worker", label: "Bakery Worker" },
  { value: "food_processing_operator", label: "Food Processing" },
  { value: "bartender", label: "Bartender" },
  { value: "dishwasher", label: "Dishwasher" },
  { value: "food_delivery", label: "Food Delivery" },
  { value: "street_vendor", label: "Street Vendor" },
  { value: "food_storage_handler", label: "Storage Handler" },
  { value: "concession_worker", label: "Concession Worker" },
];

export default function Page() {
  const router = useRouter();
  const [employerId, setEmployerId] = useState<string | null>(null);
  const [branches, setBranches] = useState<OrganizationUnit[]>([]);
  const [handlers, setHandlers] = useState<FoodHandlerRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [branchFilter, setBranchFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [fitnessFilter, setFitnessFilter] = useState("");
  const [certificateFilter, setCertificateFilter] = useState("");
  const [expiryWindow, setExpiryWindow] = useState("");
  const [updatingHandler, setUpdatingHandler] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("foodcert_access_token");
    if (!token) { router.push("/login"); return; }

    apiClient.get("/employers/me/")
      .then((res) => {
        const profile = unwrap(res.data) as { id: string; organization?: string };
        setEmployerId(profile.id);
        if (profile.organization) {
          apiClient.get(`/organizations/${profile.organization}/units/`)
            .then((unitRes) => {
              const units = unwrap(unitRes.data) as OrganizationUnit[];
              setBranches(units.filter((unit) => unit.unit_type === "branch"));
            })
            .catch(() => {});
        }
      })
      .catch(() => setError("No employer profile found."))
      .finally(() => setLoading(false));
  }, [router]);

  useEffect(() => {
    if (!employerId) return;
    setLoading(true);
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (branchFilter) params.set("branch", branchFilter);
    if (categoryFilter) params.set("category", categoryFilter);
    if (fitnessFilter) params.set("fitness_status", fitnessFilter);
    if (certificateFilter) params.set("certificate_status", certificateFilter);
    if (expiryWindow) params.set("expiry_window", expiryWindow);

    apiClient.get(`/employers/${employerId}/food-handlers/?${params.toString()}`)
      .then((res) => setHandlers(unwrap(res.data) as FoodHandlerRow[]))
      .catch(() => setError("Failed to load food handlers."))
      .finally(() => setLoading(false));
  }, [employerId, search, branchFilter, categoryFilter, fitnessFilter, certificateFilter, expiryWindow]);

  async function handleBranchChange(handlerId: string, branchId: string) {
    if (!employerId) return;
    setUpdatingHandler(handlerId);
    setError("");
    try {
      const res = await apiClient.patch(`/employers/${employerId}/food-handlers/${handlerId}/branch/`, {
        business_branch: branchId || null,
      });
      const updated = unwrap(res.data) as FoodHandlerRow;
      setHandlers((current) => current.map((handler) => handler.id === handlerId ? updated : handler));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not reassign branch.");
    } finally {
      setUpdatingHandler(null);
    }
  }

  return (
    <PortalShell role="employer" title="Food Handlers" description="View and manage all food handlers linked to your business.">
      <div className="mb-5 grid gap-3 lg:grid-cols-[minmax(220px,1fr)_repeat(5,auto)]">
        <label className="flex h-10 min-w-[200px] items-center gap-2 rounded border border-neutral-200 bg-white px-3">
          <Search size={14} className="text-neutral-400" />
          <input
            className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-neutral-400"
            placeholder="Search by name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </label>
        <label className="flex items-center gap-2 text-sm font-semibold text-neutral-700">
          <Filter size={14} className="text-neutral-400" />
          <select className="h-10 rounded border border-neutral-200 bg-white px-2 text-xs" value={branchFilter} onChange={(e) => setBranchFilter(e.target.value)}>
            <option value="">All branches</option>
            {branches.map((branch) => <option key={branch.id} value={branch.id}>{branch.name}</option>)}
          </select>
        </label>
        <select className="h-10 rounded border border-neutral-200 bg-white px-2 text-xs font-semibold text-neutral-700" value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
          {CATEGORY_OPTIONS.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
        <select aria-label="Fitness status" className="h-10 rounded border border-neutral-200 bg-white px-2 text-xs font-semibold text-neutral-700" value={fitnessFilter} onChange={(e) => setFitnessFilter(e.target.value)}>
          <option value="">All fitness statuses</option>
          <option value="fit_to_handle_food">Fit to Handle Food</option>
          <option value="certification_pending">Certification Pending</option>
          <option value="certificate_expiring_soon">Certificate Expiring Soon</option>
          <option value="certificate_expired">Certificate Expired</option>
          <option value="temporarily_not_fit">Temporarily Not Fit</option>
          <option value="excluded_from_food_handling">Excluded</option>
          <option value="return_to_work_pending">RTW Pending</option>
          <option value="vaccination_due">Vaccination Due</option>
        </select>
        <select aria-label="Certificate status" className="h-10 rounded border border-neutral-200 bg-white px-2 text-xs font-semibold text-neutral-700" value={certificateFilter} onChange={(e) => setCertificateFilter(e.target.value)}>
          <option value="">All certificates</option>
          <option value="active">Active</option>
          <option value="expired">Expired</option>
          <option value="revoked">Revoked</option>
          <option value="suspended">Suspended</option>
          <option value="pending_validation">Pending Validation</option>
          <option value="no_certificate">No Certificate</option>
        </select>
        <select aria-label="Expiry window" className="h-10 rounded border border-neutral-200 bg-white px-2 text-xs font-semibold text-neutral-700" value={expiryWindow} onChange={(e) => setExpiryWindow(e.target.value)}>
          <option value="">Any expiry</option>
          <option value="7">Expiring in 7 days</option>
          <option value="30">Expiring in 30 days</option>
          <option value="90">Expiring in 90 days</option>
        </select>
      </div>

      {!loading && handlers.length > 0 && (
        <div className="mb-5 grid gap-3 sm:grid-cols-4">
          {[
            [handlers.length, "Total"],
            [handlers.filter((h) => h.fitness_status === "fit_to_handle_food").length, "Fit"],
            [handlers.filter((h) => ["certificate_expired", "certificate_expiring_soon"].includes(h.fitness_status)).length, "Certificate Issue"],
            [handlers.filter((h) => ["temporarily_not_fit", "excluded_from_food_handling", "return_to_work_pending"].includes(h.fitness_status)).length, "Excluded / RTW"],
          ].map(([count, label]) => (
            <div key={label as string} className="rounded-lg border border-neutral-200 bg-white p-3 text-center">
              <p className="text-xl font-bold text-neutral-900">{count as number}</p>
              <p className="text-xs font-semibold text-neutral-500">{label as string}</p>
            </div>
          ))}
        </div>
      )}

      {loading && <div className="rounded-lg border border-neutral-200 bg-white p-8 text-center text-sm text-neutral-500">Loading food handlers...</div>}
      {error && !loading && <div className="rounded-lg border border-danger-100 bg-danger-50 p-4 text-sm font-semibold text-danger-700">{error}</div>}

      {!loading && !error && handlers.length === 0 && (
        <div className="rounded-lg border border-neutral-200 bg-white p-10 text-center">
          <UsersRound size={32} className="mx-auto text-neutral-300" />
          <p className="mt-3 text-sm font-semibold text-neutral-500">No food handlers found</p>
          <p className="mt-1 text-xs text-neutral-400">Adjust filters, invite food handlers, or link existing certified handlers.</p>
        </div>
      )}

      {!loading && !error && handlers.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white shadow-sm">
          <table className="w-full min-w-[1160px] text-sm">
            <thead>
              <tr className="border-b border-neutral-100 bg-neutral-50 text-left">
                <th className="px-4 py-3 text-xs font-bold uppercase text-neutral-500">Handler</th>
                <th className="px-4 py-3 text-xs font-bold uppercase text-neutral-500">Branch</th>
                <th className="px-4 py-3 text-xs font-bold uppercase text-neutral-500">Category</th>
                <th className="px-4 py-3 text-xs font-bold uppercase text-neutral-500">Fitness</th>
                <th className="px-4 py-3 text-xs font-bold uppercase text-neutral-500">Certificate</th>
                <th className="px-4 py-3 text-xs font-bold uppercase text-neutral-500">Typhoid</th>
                <th className="px-4 py-3 text-xs font-bold uppercase text-neutral-500">Hep. A</th>
                <th className="px-4 py-3 text-xs font-bold uppercase text-neutral-500">Last Assessment</th>
                <th className="px-4 py-3 text-xs font-bold uppercase text-neutral-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-50">
              {handlers.map((h) => (
                <tr key={h.id} className="hover:bg-neutral-50/50">
                  <td className="px-4 py-3">
                    <p className="font-semibold text-neutral-900">{h.full_name}</p>
                    <p className="text-xs text-neutral-500">{h.phone}</p>
                  </td>
                  <td className="px-4 py-3"><span className="text-xs text-neutral-600">{h.business_branch_name || "—"}</span></td>
                  <td className="px-4 py-3"><span className="text-xs text-neutral-600 capitalize">{h.food_handler_category?.replace(/_/g, " ") || "—"}</span></td>
                  <td className="px-4 py-3"><FitnessStatusBadge status={h.fitness_status} /></td>
                  <td className="px-4 py-3">
                    {h.certificate_number ? (
                      <div>
                        <p className="text-xs font-mono text-neutral-700">{h.certificate_number}</p>
                        {h.certificate_expiry_date && <p className="text-[10px] text-neutral-400">Exp: {new Date(h.certificate_expiry_date).toLocaleDateString()}</p>}
                      </div>
                    ) : <span className="text-xs text-neutral-400">—</span>}
                  </td>
                  <td className="px-4 py-3"><FitnessStatusBadge status={h.typhoid_status} /></td>
                  <td className="px-4 py-3"><FitnessStatusBadge status={h.hepatitis_a_status} /></td>
                  <td className="px-4 py-3"><span className="text-xs text-neutral-500">{h.last_assessment_date ? new Date(h.last_assessment_date).toLocaleDateString() : "—"}</span></td>
                  <td className="px-4 py-3">
                    <div className="flex min-w-[220px] flex-wrap items-center gap-2">
                      <button className="inline-flex h-8 items-center gap-1.5 rounded border border-neutral-200 px-2 text-xs font-bold text-neutral-700 hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-50" disabled={!h.certificate_number} onClick={() => h.certificate_number && router.push(`/verify/${encodeURIComponent(h.certificate_number)}`)} type="button">
                        <FileBadge size={13} /> Verify
                      </button>
                      <button className="inline-flex h-8 items-center gap-1.5 rounded border border-neutral-200 px-2 text-xs font-bold text-neutral-700 hover:bg-neutral-50" onClick={() => router.push(`/employer/illness-reports?handler=${h.id}`)} type="button">
                        <HeartPulse size={13} /> Report
                      </button>
                      <select aria-label={`Assign branch for ${h.full_name}`} className="h-8 max-w-[150px] rounded border border-neutral-200 bg-white px-2 text-xs font-semibold text-neutral-600" disabled={updatingHandler === h.id} onChange={(e) => handleBranchChange(h.id, e.target.value)} value={h.business_branch || ""}>
                        <option value="">No branch</option>
                        {branches.map((branch) => <option key={branch.id} value={branch.id}>{branch.name}</option>)}
                      </select>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {branches.length === 0 && !loading ? (
        <p className="mt-4 flex items-center gap-2 text-xs font-semibold text-warning-700">
          <AlertTriangle size={14} /> Add branches before assigning handlers to specific locations.
        </p>
      ) : null}
    </PortalShell>
  );
}
