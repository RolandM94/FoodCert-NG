"use client";

import { useState, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import {
  Building2, MapPin, Phone, Mail, Search, UsersRound, BadgeCheck, Globe,
  GitBranch, ClipboardCheck, Activity, ChevronRight, X, Store,
} from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import {
  fetchDirectoryFoodHandlers, fetchDirectoryEmployers, fetchDirectoryBranches,
  fetchGlobalSearch,
} from "@/lib/api/directory";
import type { UserRole } from "@/types/auth";
import type { DirectoryFoodHandler, DirectoryEmployer, DirectoryBranch } from "@/lib/api/directory";

type TabKey = "overview" | "food-handlers" | "employers" | "certificates" | "global-search" | "exports";

const TABS: Record<UserRole, Record<TabKey, string>> = {
  state_admin: { overview: "Overview", "food-handlers": "Food Handlers", employers: "Employers", certificates: "Certificates", "global-search": "Global Search", exports: "Exports" },
  employer: { overview: "Overview", "food-handlers": "Food Handlers", employers: "Employers", certificates: "Certificates", "global-search": "Global Search", exports: "Exports" },
  facility_admin: { overview: "Overview", "food-handlers": "Food Handlers", employers: "Employers", certificates: "Certificates", "global-search": "Global Search", exports: "Exports" },
  federal_admin: { overview: "Overview", "food-handlers": "Food Handlers", employers: "Employers", certificates: "Certificates", "global-search": "Global Search", exports: "Exports" },
  super_admin: { overview: "Overview", "food-handlers": "Food Handlers", employers: "Employers", certificates: "Certificates", "global-search": "Global Search", exports: "Exports" },
  inspector: { overview: "Overview", "food-handlers": "Food Handlers", employers: "Employers", certificates: "Certificates", "global-search": "Global Search", exports: "Exports" },
  doctor: { overview: "Overview", "food-handlers": "Food Handlers", employers: "Employers", certificates: "Certificates", "global-search": "Global Search", exports: "Exports" },
  lab_staff: { overview: "Overview", "food-handlers": "Food Handlers", employers: "Employers", certificates: "Certificates", "global-search": "Global Search", exports: "Exports" },
  food_handler: { overview: "Overview", "food-handlers": "Food Handlers", employers: "Employers", certificates: "Certificates", "global-search": "Global Search", exports: "Exports" },
};

function formatDate(v?: string) { if (!v) return "—"; return new Date(v).toLocaleDateString("en-NG", { dateStyle: "medium" }); }

// ── Food Handlers Tab ──
function FoodHandlersTab() {
  const [search, setSearch] = useState("");
  const { data: list, isLoading } = useQuery({
    queryKey: ["directory-food-handlers", search],
    queryFn: () => fetchDirectoryFoodHandlers(search ? { q: search } : {}),
  });

  const items = Array.isArray(list) ? list : [];

  return (
    <div className="space-y-4">
      <div className="relative max-w-sm">
        <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" size={16} />
        <input className="h-10 w-full rounded-lg border border-neutral-200 bg-white pl-9 pr-3 text-sm outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100" placeholder="Search by name or ID..." type="search" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>
      <section className="overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-neutral-200 text-sm">
            <thead className="bg-neutral-50"><tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">Name</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">ID</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">NIN</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">Employer</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">Branch</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">State</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">Registered</th>
            </tr></thead>
            <tbody className="divide-y divide-neutral-100">
              {isLoading ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={8}>Loading...</td></tr>
              : items.length === 0 ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={8}>No food handlers found.</td></tr>
              : items.map((fh: DirectoryFoodHandler) => (
                <tr key={fh.id} className="hover:bg-neutral-50">
                  <td className="px-4 py-3 font-semibold text-neutral-900">{fh.full_name}</td>
                  <td className="px-4 py-3 text-xs font-mono text-neutral-500">{fh.system_identifier}</td>
                  <td className="px-4 py-3 text-xs font-mono text-neutral-500">{fh.masked_nin}</td>
                  <td className="px-4 py-3 text-neutral-700">{fh.employer_name || "—"}</td>
                  <td className="px-4 py-3 text-neutral-600">{fh.branch_name || "—"}</td>
                  <td className="px-4 py-3 text-neutral-600">{fh.state_name || "—"}</td>
                  <td className="px-4 py-3"><StatusBadge status={fh.current_status} /></td>
                  <td className="px-4 py-3 text-sm text-neutral-500">{formatDate(fh.created_at)}</td>
                </tr>
              ))}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

// ── Employers Tab ──
function EmployersTab({ onSelect }: { onSelect: (e: DirectoryEmployer) => void }) {
  const [search, setSearch] = useState("");
  const { data: list, isLoading } = useQuery({
    queryKey: ["directory-employers", search],
    queryFn: () => fetchDirectoryEmployers(search ? { q: search } : {}),
  });

  const items = Array.isArray(list) ? list : [];

  return (
    <div className="space-y-4">
      <div className="relative max-w-sm">
        <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" size={16} />
        <input className="h-10 w-full rounded-lg border border-neutral-200 bg-white pl-9 pr-3 text-sm outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100" placeholder="Search by business name..." type="search" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>
      <section className="overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-neutral-200 text-sm">
            <thead className="bg-neutral-50"><tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">Business Name</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">Category</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">Branches</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">Handlers</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">State</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">Compliance</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-neutral-500">Status</th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wide text-neutral-500">Actions</th>
            </tr></thead>
            <tbody className="divide-y divide-neutral-100">
              {isLoading ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={8}>Loading...</td></tr>
              : items.length === 0 ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={8}>No employers found.</td></tr>
              : items.map((e: DirectoryEmployer) => (
                <tr key={e.id} className="hover:bg-neutral-50 cursor-pointer" onClick={() => onSelect(e)}>
                  <td className="px-4 py-3 font-semibold text-neutral-900">{e.business_name}</td>
                  <td className="px-4 py-3 text-neutral-600 text-xs">{e.establishment_category?.replace(/_/g, " ")}</td>
                  <td className="px-4 py-3 text-neutral-700">{e.branch_count}</td>
                  <td className="px-4 py-3 text-neutral-700">{e.food_handler_count}</td>
                  <td className="px-4 py-3 text-neutral-600">{e.state_name || "—"}</td>
                  <td className="px-4 py-3"><StatusBadge status={e.compliance_status} /></td>
                  <td className="px-4 py-3"><StatusBadge status={e.is_active ? "active" : "inactive"} /></td>
                  <td className="px-4 py-3 text-right">
                    <span className="inline-flex items-center gap-1 text-xs font-medium text-brand-600">
                      View <ChevronRight size={14} />
                    </span>
                  </td>
                </tr>
              ))}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

// ── Employer Detail Drawer ──
type DetailTab = "profile" | "branches" | "food-handlers" | "certificates" | "inspections" | "notices" | "compliance";

const DETAIL_TABS: DetailTab[] = ["profile", "branches", "food-handlers", "certificates", "inspections", "notices", "compliance"];
const DETAIL_LABELS: Record<DetailTab, string> = {
  profile: "Profile", branches: "Branches / Outlets", "food-handlers": "Food Handlers",
  certificates: "Certificates", inspections: "Inspections", notices: "Notices", compliance: "Compliance",
};

function EmployerDetailDrawer({
  employer,
  onClose,
}: {
  employer: DirectoryEmployer;
  onClose: () => void;
}) {
  const [detailTab, setDetailTab] = useState<DetailTab>("profile");

  const { data: branches, isLoading: loadingBranches } = useQuery({
    queryKey: ["directory-branches", employer.id],
    queryFn: () => fetchDirectoryBranches({ employer: employer.id }),
    enabled: detailTab === "branches",
  });
  const branchItems = Array.isArray(branches) ? branches : [];

  const { data: foodHandlers, isLoading: loadingFH } = useQuery({
    queryKey: ["directory-food-handlers", employer.id],
    queryFn: () => fetchDirectoryFoodHandlers({ employer: employer.id }),
    enabled: detailTab === "food-handlers",
  });
  const fhItems = Array.isArray(foodHandlers) ? foodHandlers : [];

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/40" onClick={onClose} />
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-3xl overflow-y-auto border-l border-neutral-200 bg-white shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-neutral-200 px-6 py-4 sticky top-0 bg-white z-10">
          <div>
            <h2 className="text-lg font-semibold text-neutral-900">{employer.business_name}</h2>
            <p className="text-xs text-neutral-500">
              {employer.establishment_category?.replace(/_/g, " ")} &middot; {employer.state_name || "No state"} &middot; {employer.branch_count} branches &middot; {employer.food_handler_count} handlers
            </p>
          </div>
          <button className="rounded-lg p-1.5 hover:bg-neutral-100" onClick={onClose} aria-label="Close" type="button">
            <X size={18} className="text-neutral-500" />
          </button>
        </div>

        {/* Sub-tabs */}
        <nav className="flex gap-0 overflow-x-auto border-b border-neutral-200 bg-neutral-50 px-6">
          {DETAIL_TABS.map((key) => (
            <button
              key={key}
              className={`shrink-0 border-b-2 px-4 py-3 text-sm font-medium ${
                detailTab === key ? "border-brand-600 text-brand-700" : "border-transparent text-neutral-500 hover:text-neutral-800"
              }`}
              onClick={() => setDetailTab(key)}
              type="button"
            >
              {DETAIL_LABELS[key]}
            </button>
          ))}
        </nav>

        {/* Tab content */}
        <div className="p-6">
          {detailTab === "profile" && (
            <div className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <h4 className="text-xs font-bold uppercase text-neutral-500">Business Name</h4>
                  <p className="mt-1 text-sm font-semibold text-neutral-900">{employer.business_name}</p>
                </div>
                <div>
                  <h4 className="text-xs font-bold uppercase text-neutral-500">Registration Number</h4>
                  <p className="mt-1 text-sm text-neutral-700">{employer.business_registration_number || "—"}</p>
                </div>
                <div>
                  <h4 className="text-xs font-bold uppercase text-neutral-500">Category</h4>
                  <p className="mt-1 text-sm text-neutral-700">{employer.establishment_category?.replace(/_/g, " ") || "—"}</p>
                </div>
                <div>
                  <h4 className="text-xs font-bold uppercase text-neutral-500">Contact Person</h4>
                  <p className="mt-1 text-sm text-neutral-700">{employer.contact_person_name || "—"}</p>
                </div>
                <div>
                  <h4 className="text-xs font-bold uppercase text-neutral-500">Phone</h4>
                  <div className="mt-1 flex items-center gap-1 text-sm text-neutral-700"><Phone size={12} className="text-neutral-400" />{employer.contact_person_phone || "—"}</div>
                </div>
                <div>
                  <h4 className="text-xs font-bold uppercase text-neutral-500">Email</h4>
                  <div className="mt-1 flex items-center gap-1 text-sm text-neutral-700"><Mail size={12} className="text-neutral-400" />{employer.contact_person_email || "—"}</div>
                </div>
                <div className="sm:col-span-2">
                  <h4 className="text-xs font-bold uppercase text-neutral-500">Address</h4>
                  <p className="mt-1 text-sm text-neutral-700">{employer.address || "—"}</p>
                </div>
                <div>
                  <h4 className="text-xs font-bold uppercase text-neutral-500">Compliance</h4>
                  <p className="mt-1"><StatusBadge status={employer.compliance_status} /></p>
                </div>
                <div>
                  <h4 className="text-xs font-bold uppercase text-neutral-500">Subscription</h4>
                  <p className="mt-1"><StatusBadge status={employer.subscription_status} /></p>
                </div>
              </div>
            </div>
          )}

          {detailTab === "branches" && (
            <div className="space-y-4">
              {loadingBranches ? (
                <p className="text-sm text-neutral-500">Loading branches...</p>
              ) : branchItems.length === 0 ? (
                <div className="flex flex-col items-center justify-center gap-2 py-8 text-center">
                  <Store size={28} className="text-neutral-300" />
                  <p className="text-sm font-semibold text-neutral-500">No branches or outlets have been added for this employer.</p>
                </div>
              ) : (
                <section className="overflow-hidden rounded-xl border border-neutral-200 bg-white">
                  <table className="min-w-full divide-y divide-neutral-200 text-sm">
                    <thead className="bg-neutral-50"><tr>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Branch Name</th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Type</th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">State</th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">LGA</th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Handlers</th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Status</th>
                    </tr></thead>
                    <tbody className="divide-y divide-neutral-100">
                      {branchItems.map((b: DirectoryBranch) => (
                        <tr key={b.id} className="hover:bg-neutral-50">
                          <td className="px-4 py-3 font-semibold text-neutral-900">{b.name}</td>
                          <td className="px-4 py-3 text-xs text-neutral-500 uppercase">{b.unit_type?.replace(/_/g, " ")}</td>
                          <td className="px-4 py-3 text-neutral-600">{b.state_name || "—"}</td>
                          <td className="px-4 py-3 text-neutral-600">{b.lga_name || "—"}</td>
                          <td className="px-4 py-3 text-neutral-700">{b.food_handler_count}</td>
                          <td className="px-4 py-3"><StatusBadge status={b.status} /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </section>
              )}
            </div>
          )}

          {detailTab === "food-handlers" && (
            <div className="space-y-4">
              {loadingFH ? (
                <p className="text-sm text-neutral-500">Loading food handlers...</p>
              ) : fhItems.length === 0 ? (
                <div className="flex flex-col items-center justify-center gap-2 py-8 text-center">
                  <UsersRound size={28} className="text-neutral-300" />
                  <p className="text-sm font-semibold text-neutral-500">No food handlers found for this employer.</p>
                </div>
              ) : (
                <section className="overflow-hidden rounded-xl border border-neutral-200 bg-white">
                  <table className="min-w-full divide-y divide-neutral-200 text-sm">
                    <thead className="bg-neutral-50"><tr>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Name</th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">ID</th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Branch</th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">State</th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Status</th>
                    </tr></thead>
                    <tbody className="divide-y divide-neutral-100">
                      {fhItems.map((fh: DirectoryFoodHandler) => (
                        <tr key={fh.id} className="hover:bg-neutral-50">
                          <td className="px-4 py-3 font-semibold text-neutral-900">{fh.full_name}</td>
                          <td className="px-4 py-3 text-xs font-mono text-neutral-500">{fh.system_identifier}</td>
                          <td className="px-4 py-3 text-neutral-600">{fh.branch_name || "—"}</td>
                          <td className="px-4 py-3 text-neutral-600">{fh.state_name || "—"}</td>
                          <td className="px-4 py-3"><StatusBadge status={fh.current_status} /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </section>
              )}
            </div>
          )}

          {detailTab === "certificates" && (
            <div className="flex flex-col items-center justify-center gap-2 py-12 text-center">
              <BadgeCheck size={28} className="text-neutral-300" />
              <p className="text-sm font-semibold text-neutral-500">Certificates</p>
              <p className="text-xs text-neutral-400">Certificate records for this employer will be available soon.</p>
            </div>
          )}
          {detailTab === "inspections" && (
            <div className="flex flex-col items-center justify-center gap-2 py-12 text-center">
              <ClipboardCheck size={28} className="text-neutral-300" />
              <p className="text-sm font-semibold text-neutral-500">Inspections</p>
              <p className="text-xs text-neutral-400">Inspection records for this employer will be available soon.</p>
            </div>
          )}
          {detailTab === "notices" && (
            <div className="flex flex-col items-center justify-center gap-2 py-12 text-center">
              <Activity size={28} className="text-neutral-300" />
              <p className="text-sm font-semibold text-neutral-500">Notices</p>
              <p className="text-xs text-neutral-400">Enforcement notices will be available soon.</p>
            </div>
          )}
          {detailTab === "compliance" && (
            <div className="flex flex-col items-center justify-center gap-2 py-12 text-center">
              <ClipboardCheck size={28} className="text-neutral-300" />
              <p className="text-sm font-semibold text-neutral-500">Compliance Summary</p>
              <p className="text-xs text-neutral-400">Compliance reports will be available soon.</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

// ── Branches Tab ──
function BranchesTab() {
  const [search, setSearch] = useState("");
  const { data: list, isLoading } = useQuery({
    queryKey: ["directory-branches", search],
    queryFn: () => fetchDirectoryBranches(search ? { q: search } : {}),
  });

  const items = Array.isArray(list) ? list : [];

  return (
    <div className="space-y-4">
      <div className="relative max-w-sm">
        <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" size={16} />
        <input className="h-10 w-full rounded-lg border border-neutral-200 bg-white pl-9 pr-3 text-sm" placeholder="Search by branch name..." type="search" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>
      <section className="overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-neutral-200 text-sm">
            <thead className="bg-neutral-50"><tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Branch Name</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Employer</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Type</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Handlers</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">State</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">LGA</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Status</th>
            </tr></thead>
            <tbody className="divide-y divide-neutral-100">
              {isLoading ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={7}>Loading...</td></tr>
              : items.length === 0 ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={7}>No branches found.</td></tr>
              : items.map((b: DirectoryBranch) => (
                <tr key={b.id} className="hover:bg-neutral-50">
                  <td className="px-4 py-3 font-semibold text-neutral-900">{b.name}</td>
                  <td className="px-4 py-3 text-neutral-700">{b.employer_name || "—"}</td>
                  <td className="px-4 py-3 text-xs text-neutral-500 uppercase">{b.unit_type?.replace(/_/g, " ")}</td>
                  <td className="px-4 py-3 text-neutral-700">{b.food_handler_count}</td>
                  <td className="px-4 py-3 text-neutral-600">{b.state_name || "—"}</td>
                  <td className="px-4 py-3 text-neutral-600">{b.lga_name || "—"}</td>
                  <td className="px-4 py-3"><StatusBadge status={b.status} /></td>
                </tr>
              ))}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

// ── Global Search Tab ──
function GlobalSearchTab() {
  const [q, setQ] = useState("");
  const { data, isLoading, isFetched } = useQuery({
    queryKey: ["global-search", q],
    queryFn: () => fetchGlobalSearch(q),
    enabled: q.length >= 2,
  });

  return (
    <div className="space-y-4">
      <div className="relative">
        <Globe className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" size={18} />
        <input className="h-12 w-full rounded-lg border border-neutral-200 bg-white pl-10 pr-4 text-base outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100" placeholder="Search by name, certificate number, employer, branch, or ID..." type="search" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      {isLoading ? <p className="text-sm text-neutral-500">Searching...</p> : isFetched && data?.results ? (
        <div className="space-y-4">
          {data.results.food_handlers && data.results.food_handlers.length > 0 && (
            <div className="rounded-xl border border-neutral-200 bg-white p-4 shadow-sm">
              <h3 className="text-sm font-bold text-neutral-900 flex items-center gap-2"><UsersRound size={14} className="text-brand-600" />Food Handlers</h3>
              <div className="mt-2 space-y-1">
                {data.results.food_handlers.map((fh) => (
                  <div key={fh.id} className="flex justify-between text-sm text-neutral-700 py-1 border-b border-neutral-50 last:border-0">
                    <span className="font-medium">{fh.full_name}</span>
                    <span className="text-xs text-neutral-500">{fh.system_identifier} {fh.employer__business_name && `· ${fh.employer__business_name}`}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          {data.results.employers && data.results.employers.length > 0 && (
            <div className="rounded-xl border border-neutral-200 bg-white p-4 shadow-sm">
              <h3 className="text-sm font-bold text-neutral-900 flex items-center gap-2"><Building2 size={14} className="text-brand-600" />Employers</h3>
              <div className="mt-2 space-y-1">
                {data.results.employers.map((e) => (
                  <div key={e.id} className="text-sm text-neutral-700 py-1">{e.business_name} {e.state__name && <span className="text-xs text-neutral-500">· {e.state__name}</span>}</div>
                ))}
              </div>
            </div>
          )}
          {data.results.certificates && data.results.certificates.length > 0 && (
            <div className="rounded-xl border border-neutral-200 bg-white p-4 shadow-sm">
              <h3 className="text-sm font-bold text-neutral-900 flex items-center gap-2"><BadgeCheck size={14} className="text-brand-600" />Certificates</h3>
              <div className="mt-2 space-y-1">
                {data.results.certificates.map((c) => (
                  <div key={c.id} className="text-sm text-neutral-700 py-1 font-mono">{c.certificate_number} <StatusBadge status={c.status} /></div>
                ))}
              </div>
            </div>
          )}
          {(!data.results.food_handlers?.length && !data.results.employers?.length && !data.results.certificates?.length) && (
            <p className="text-sm text-neutral-500">No results found.</p>
          )}
        </div>
      ) : q.length < 2 ? (
        <p className="text-sm text-neutral-500">Enter at least 2 characters to search.</p>
      ) : null}
    </div>
  );
}


// ── Overview Tab ──
function OverviewTab() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <button className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm text-left hover:border-brand-200 hover:shadow transition-shadow" onClick={() => document.querySelector<HTMLButtonElement>('[data-tab="food-handlers"]')?.click()}>
        <UsersRound className="text-brand-600" size={20} />
        <h3 className="mt-3 text-sm font-bold text-neutral-900">Food Handlers</h3>
        <p className="mt-1 text-xs text-neutral-500">Search and browse food handler profiles, certificates, and compliance.</p>
      </button>
      <button className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm text-left hover:border-brand-200 hover:shadow transition-shadow" onClick={() => document.querySelector<HTMLButtonElement>('[data-tab="employers"]')?.click()}>
        <Building2 className="text-brand-600" size={20} />
        <h3 className="mt-3 text-sm font-bold text-neutral-900">Employers</h3>
        <p className="mt-1 text-xs text-neutral-500">Browse food businesses, branches, compliance summaries.</p>
      </button>
      <button className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm text-left hover:border-brand-200 hover:shadow transition-shadow" onClick={() => document.querySelector<HTMLButtonElement>('[data-tab="certificates"]')?.click()}>
        <BadgeCheck className="text-brand-600" size={20} />
        <h3 className="mt-3 text-sm font-bold text-neutral-900">Certificates</h3>
        <p className="mt-1 text-xs text-neutral-500">Search certificate registry by number, status, or holder.</p>
      </button>
      <button className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm text-left hover:border-brand-200 hover:shadow transition-shadow" onClick={() => document.querySelector<HTMLButtonElement>('[data-tab="global-search"]')?.click()}>
        <Globe className="text-brand-600" size={20} />
        <h3 className="mt-3 text-sm font-bold text-neutral-900">Global Search</h3>
        <p className="mt-1 text-xs text-neutral-500">Search across food handlers, employers, and certificates.</p>
      </button>
    </div>
  );
}

// ── Main Layout ──
export function DirectoryLayout({ role }: { role: UserRole }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tabParam = (searchParams.get("tab") ?? "overview") as TabKey;
  const tabs = TABS[role] ?? TABS.state_admin;
  const [selectedEmployer, setSelectedEmployer] = useState<DirectoryEmployer | null>(null);

  function setTab(tab: TabKey) {
    const prefix = role === "super_admin" ? "admin" : role.replace("_admin", "").replace("_staff", "");
    router.replace(`/${prefix}/directory?tab=${tab}`);
  }

  return (
    <PortalShell role={role} title="Directory & Registry" description="Search and browse food handlers, employers, branches, certificates, and compliance records.">
      <nav className="mb-6 flex gap-0 overflow-x-auto border-b border-neutral-200">
        {(Object.entries(tabs) as [TabKey, string][]).map(([key, label]) => (
          <button
            key={key}
            data-tab={key}
            className={`shrink-0 border-b-2 px-4 py-3 text-sm font-medium ${
              tabParam === key ? "border-brand-600 text-brand-700" : "border-transparent text-neutral-500 hover:text-neutral-800"
            }`}
            onClick={() => setTab(key)}
            type="button"
          >
            {label}
          </button>
        ))}
      </nav>

      {tabParam === "overview" && <OverviewTab />}
      {tabParam === "food-handlers" && <FoodHandlersTab />}
      {tabParam === "employers" && (
        <EmployersTab onSelect={setSelectedEmployer} />
      )}
      {tabParam === "certificates" && (
        <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
          <BadgeCheck size={32} className="text-neutral-300" />
          <p className="text-sm font-semibold text-neutral-500">Certificate Registry Search</p>
          <p className="text-xs text-neutral-400">Certificate search will be available in the next update.</p>
        </div>
      )}
      {tabParam === "global-search" && <GlobalSearchTab />}
      {tabParam === "exports" && (
        <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
          <Activity size={32} className="text-neutral-300" />
          <p className="text-sm font-semibold text-neutral-500">Exports</p>
          <p className="text-xs text-neutral-400">Export functionality will be available in the next update.</p>
        </div>
      )}

      {selectedEmployer && (
        <EmployerDetailDrawer employer={selectedEmployer} onClose={() => setSelectedEmployer(null)} />
      )}
    </PortalShell>
  );
}
