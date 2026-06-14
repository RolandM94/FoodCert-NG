"use client";

import { useState } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import {
  Building2, ClipboardCheck, ShieldCheck, Activity, BarChart3,
  BadgeCheck,
} from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { DashboardCard } from "@/components/ui/dashboard-card";
import {
  fetchStateFacilities, fetchStateFacilityApplications,
} from "@/lib/api/state";
import type { MedicalFacility } from "@/types/facilities";

type TabKey = "overview" | "facilities" | "accreditation" | "reports";

const TABS: Record<Exclude<TabKey, "accreditation" | "reports">, string> = {
  overview: "Overview",
  facilities: "Facilities",
};

const STATUS_CHIPS: { key: string; label: string }[] = [
  { key: "", label: "All" },
  { key: "approved", label: "Accredited" },
  { key: "submitted", label: "Pending" },
  { key: "suspended", label: "Suspended" },
  { key: "expired", label: "Expired" },
  { key: "reaccreditation_due", label: "Re-accreditation Due" },
];

const TYPE_OPTIONS = [
  ["", "All facility types"],
  ["hospital", "Hospital"],
  ["clinic", "Clinic"],
  ["diagnostic_centre", "Diagnostic centre"],
  ["primary_health_centre", "Primary health centre"],
  ["mobile_health_unit", "Mobile health unit"],
];

function dateLabel(v?: string) { if (!v) return "—"; return new Date(v).toLocaleDateString("en-NG", { dateStyle: "medium" }); }

// ── Overview Tab ──
function OverviewTab() {
  const { data: facilities = [] } = useQuery({ queryKey: ["state-facilities-overview"], queryFn: () => fetchStateFacilities({}) });
  const { data: applications = [] } = useQuery({ queryKey: ["state-facility-apps-overview"], queryFn: () => fetchStateFacilityApplications({}) });

  const total = facilities.length;
  const accredited = facilities.filter((f) => f.accreditation_status === "approved").length;
  const pending = facilities.filter((f) => f.accreditation_status === "submitted" || f.accreditation_status === "under_review").length;
  const suspended = facilities.filter((f) => f.accreditation_status === "suspended").length;
  const expired = facilities.filter((f) => f.accreditation_status === "expired").length;
  const reaccredDue = facilities.filter((f) => f.accreditation_status === "reaccreditation_due").length;
  const appCount = applications.length;

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <DashboardCard icon={Building2} label="Total Facilities" value={total} />
        <DashboardCard icon={ShieldCheck} label="Accredited" value={accredited} />
        <DashboardCard icon={ClipboardCheck} label="Applications" value={appCount} />
        <DashboardCard icon={Activity} label="Pending" value={pending} />
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        <DashboardCard icon={BadgeCheck} label="Suspended" value={suspended} />
        <DashboardCard icon={BarChart3} label="Expired" value={expired} />
        <DashboardCard icon={ShieldCheck} label="Re-accreditation Due" value={reaccredDue} />
      </div>
    </div>
  );
}

// ── Facilities Tab ──
function FacilitiesTab() {
  const [status, setStatus] = useState("");
  const [facilityType, setFacilityType] = useState("");
  const [search, setSearch] = useState("");

  const { data: facilities = [], isLoading, isError } = useQuery({
    queryKey: ["state-facilities", status, facilityType, search],
    queryFn: () => fetchStateFacilities({ status: status || undefined, facility_type: facilityType || undefined, search: search || undefined }),
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <label className="grid gap-1 text-xs font-bold uppercase text-neutral-500">
          Search
          <input className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm normal-case font-normal text-neutral-700" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Facility name" />
        </label>
        <label className="grid gap-1 text-xs font-bold uppercase text-neutral-500">
          Type
          <select className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm normal-case font-normal text-neutral-700" value={facilityType} onChange={(e) => setFacilityType(e.target.value)}>
            {TYPE_OPTIONS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </label>
      </div>

      {/* Filter chips */}
      <div className="flex flex-wrap gap-2">
        {STATUS_CHIPS.map(({ key, label }) => (
          <button
            key={key}
            className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${
              status === key ? "bg-brand-600 text-white" : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
            }`}
            onClick={() => setStatus(key)}
            type="button"
          >
            {label}
          </button>
        ))}
      </div>

      <section className="grid gap-3">
        <div className="flex items-center gap-2">
          <Building2 className="text-brand-700" size={18} />
          <h2 className="text-base font-bold text-neutral-900">Facility Registry</h2>
        </div>
        {isError ? <p className="rounded bg-danger-50 p-3 text-sm font-semibold text-danger-700">Could not load facilities.</p> : null}
        <DataTable<MedicalFacility>
          columns={[
            { key: "facility", header: "Facility", render: (row) => (
              <Link className="block hover:text-brand-700" href={`/state/medical-facilities/${row.id}`}>
                <p className="font-bold text-neutral-900 hover:text-brand-700">{row.facility_name}</p>
                <p className="text-xs text-neutral-500">{row.license_number}</p>
              </Link>
            ) },
            { key: "type", header: "Type", render: (row) => row.facility_type.replace(/_/g, " ") },
            { key: "lga", header: "LGA", render: (row) => row.lga_name || "Not set" },
            { key: "status", header: "Status", render: (row) => <StatusCell status={row.accreditation_status} /> },
            { key: "expiry", header: "Expiry", render: (row) => dateLabel(row.accreditation_expiry_date) },
            { key: "assessments", header: "Assessment ready", render: (row) => row.can_conduct_assessments ? "Yes" : "No" },
          ]}
          rows={facilities}
          empty={isLoading ? "Loading facilities..." : "No facilities match the current filters."}
        />
      </section>
    </div>
  );
}

// ── Main Layout ──
export function MedicalFacilitiesLayout() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tabParam = (searchParams.get("tab") ?? "overview") as TabKey;

  const activeTab = TABS[tabParam as keyof typeof TABS] ? tabParam as keyof typeof TABS : "overview";

  function setTab(tab: keyof typeof TABS) {
    router.replace(`/state/medical-facilities?tab=${tab}`);
  }

  return (
    <PortalShell
      role="state_admin"
      title="Medical Facilities"
      description="Browse facilities in your state. Open a facility to see its profile, recurring accreditation history, reports, and monitoring records."
    >
      <nav className="mb-6 flex gap-0 overflow-x-auto border-b border-neutral-200">
        {(Object.entries(TABS) as [keyof typeof TABS, string][]).map(([key, label]) => (
          <button
            key={key}
            className={`shrink-0 border-b-2 px-4 py-3 text-sm font-medium ${
              activeTab === key ? "border-brand-600 text-brand-700" : "border-transparent text-neutral-500 hover:text-neutral-800"
            }`}
            onClick={() => setTab(key)}
            type="button"
          >
            {label}
          </button>
        ))}
      </nav>

      {activeTab === "overview" && <OverviewTab />}
      {activeTab === "facilities" && <FacilitiesTab />}
    </PortalShell>
  );
}
