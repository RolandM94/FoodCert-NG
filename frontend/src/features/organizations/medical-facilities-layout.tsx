"use client";

import { useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Building2, ClipboardCheck, ShieldCheck, Activity, BarChart3,
  BadgeCheck, Search, X, ChevronRight,
} from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { DashboardCard } from "@/components/ui/dashboard-card";
import {
  fetchStateFacilities, fetchStateFacilityApplications,
  approveStateFacilityApplication, reinstateStateFacilityApplication,
  rejectStateFacilityApplication, suspendStateFacilityApplication,
} from "@/lib/api/state";
import type { UserRole } from "@/types/auth";
import type { MedicalFacility, FacilityAccreditationApplication, AccreditationStatus } from "@/types/facilities";

type TabKey = "overview" | "facilities" | "accreditation" | "reports";

const TABS: Record<TabKey, string> = {
  overview: "Overview",
  facilities: "Facilities",
  accreditation: "Accreditation",
  reports: "Reports",
};

const STATUS_CHIPS: { key: string; label: string }[] = [
  { key: "", label: "All" },
  { key: "approved", label: "Accredited" },
  { key: "submitted", label: "Pending" },
  { key: "suspended", label: "Suspended" },
  { key: "expired", label: "Expired" },
  { key: "reaccreditation_due", label: "Re-accreditation Due" },
];

const APP_STATUS_CHIPS: { key: string; label: string }[] = [
  { key: "", label: "All" },
  { key: "submitted", label: "Pending Review" },
  { key: "under_review", label: "Under Review" },
  { key: "more_information_required", label: "More Info Required" },
  { key: "approved", label: "Approved" },
  { key: "rejected", label: "Rejected" },
];

const APP_TYPE_CHIPS: { key: string; label: string }[] = [
  { key: "", label: "All Types" },
  { key: "new", label: "New Accreditation" },
  { key: "renewal", label: "Re-accreditation" },
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

type ActionName = "approve" | "reject" | "suspend" | "reinstate";

function checklistScore(row: FacilityAccreditationApplication) {
  const keys: (keyof FacilityAccreditationApplication)[] = [
    "has_reporting_policy", "has_medical_records_computers", "has_computer_operators",
    "has_standard_forms", "has_laboratory_request_forms", "has_patient_files",
    "has_qr_certificate_capability", "has_internet_access", "has_trained_records_staff",
    "has_trained_clinical_staff", "has_trained_non_clinical_staff",
  ];
  return `${keys.filter((k) => row[k]).length}/${keys.length}`;
}

function allowedActions(status: AccreditationStatus): ActionName[] {
  if (status === "submitted" || status === "under_review") return ["approve", "reject"];
  if (status === "approved") return ["suspend"];
  if (status === "suspended") return ["reinstate"];
  return [];
}

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
            { key: "facility", header: "Facility", render: (row) => <div><p className="font-bold text-neutral-900">{row.facility_name}</p><p className="text-xs text-neutral-500">{row.license_number}</p></div> },
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

// ── Accreditation Tab ──
function AccreditationTab() {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState("");
  const [appType, setAppType] = useState("");
  const [search, setSearch] = useState("");
  const [actionTarget, setActionTarget] = useState<{ application: FacilityAccreditationApplication; action: ActionName } | null>(null);
  const [comment, setComment] = useState("");

  const { data: rawApps = [], isLoading, isError } = useQuery({
    queryKey: ["state-facility-applications", status],
    queryFn: () => fetchStateFacilityApplications({ status: status || undefined }),
  });

  const applications = appType
    ? rawApps.filter((a) => appType === "renewal" ? a.is_renewal : !a.is_renewal)
    : rawApps;

  const actionMutation = useMutation({
    mutationFn: ({ application, action, reviewComment }: { application: FacilityAccreditationApplication; action: ActionName; reviewComment: string }) => {
      if (action === "approve") return approveStateFacilityApplication(application.id, reviewComment);
      if (action === "reject") return rejectStateFacilityApplication(application.id, reviewComment);
      if (action === "suspend") return suspendStateFacilityApplication(application.id, reviewComment);
      return reinstateStateFacilityApplication(application.id, reviewComment);
    },
    onSuccess: () => {
      setActionTarget(null); setComment("");
      queryClient.invalidateQueries({ queryKey: ["state-facility-applications"] });
      queryClient.invalidateQueries({ queryKey: ["state-facilities"] });
      queryClient.invalidateQueries({ queryKey: ["state-facilities-overview"] });
      queryClient.invalidateQueries({ queryKey: ["state-facility-apps-overview"] });
    },
  });

  const requiresComment = actionTarget?.action === "reject" || actionTarget?.action === "suspend";

  return (
    <div className="space-y-4">
      {/* Filter chips - App type */}
      <div className="flex flex-wrap gap-2">
        {APP_TYPE_CHIPS.map(({ key, label }) => (
          <button key={key} className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${appType === key ? "bg-brand-600 text-white" : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"}`} onClick={() => setAppType(key)} type="button">{label}</button>
        ))}
      </div>
      {/* Filter chips - Status */}
      <div className="flex flex-wrap gap-2">
        {APP_STATUS_CHIPS.map(({ key, label }) => (
          <button key={key} className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${status === key ? "bg-brand-600 text-white" : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"}`} onClick={() => setStatus(key)} type="button">{label}</button>
        ))}
      </div>

      <section className="grid gap-3">
        <div className="flex items-center gap-2">
          <ClipboardCheck className="text-brand-700" size={18} />
          <h2 className="text-base font-bold text-neutral-900">Accreditation Queue</h2>
        </div>
        {isError ? <p className="rounded bg-danger-50 p-3 text-sm font-semibold text-danger-700">Could not load applications.</p> : null}
        <DataTable<FacilityAccreditationApplication>
          columns={[
            { key: "facility", header: "Facility", render: (row) => <div><p className="font-bold text-neutral-900">{row.facility_name}</p><span className={`inline-block mt-1 rounded px-2 py-0.5 text-[10px] font-bold ${row.is_renewal ? "bg-warning-100 text-warning-700" : "bg-info-100 text-info-700"}`}>{row.is_renewal ? "Re-accreditation" : "New"}</span></div> },
            { key: "checklist", header: "Checklist", render: (row) => <span className={row.checklist_complete ? "font-bold text-brand-700" : "font-bold text-warning-700"}>{checklistScore(row)}</span> },
            { key: "status", header: "Status", render: (row) => <StatusCell status={row.application_status} /> },
            { key: "submitted", header: "Submitted", render: (row) => dateLabel(row.submitted_at || row.created_at) },
            { key: "reviewer", header: "Reviewer", render: (row) => row.reviewer_name || "Not reviewed" },
            { key: "actions", header: "Actions", render: (row) => (
              <div className="flex flex-wrap gap-2">
                {allowedActions(row.application_status).map((action) => (
                  <button className="h-8 rounded border border-neutral-200 px-3 text-xs font-bold capitalize text-neutral-700 hover:bg-neutral-50" key={action} onClick={() => setActionTarget({ application: row, action })} type="button">{action}</button>
                ))}
              </div>
            )},
          ]}
          rows={applications}
          empty={isLoading ? "Loading applications..." : "No applications match the current filters."}
        />
      </section>

      {actionTarget ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-md rounded-2xl border border-neutral-200 bg-white shadow-md">
            <div className="border-b border-neutral-200 px-6 py-4">
              <h2 className="text-lg font-semibold capitalize text-neutral-900">{actionTarget.action} facility accreditation</h2>
              <p className="mt-1 text-sm text-neutral-500">{actionTarget.application.facility_name}</p>
            </div>
            <form className="grid gap-4 p-6" onSubmit={(e) => { e.preventDefault(); actionMutation.mutate({ application: actionTarget.application, action: actionTarget.action, reviewComment: comment }); }}>
              <label className="grid gap-1 text-sm font-semibold text-neutral-700">
                Review comment {requiresComment ? <span className="text-danger-500">*</span> : null}
                <textarea className="rounded-lg border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm" required={requiresComment} rows={3} value={comment} onChange={(e) => setComment(e.target.value)} />
              </label>
              {actionMutation.isError ? <p className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">Could not complete this action.</p> : null}
              <div className="flex justify-end gap-3">
                <button className="h-10 rounded-lg border border-neutral-200 px-4 text-sm font-medium text-neutral-600 hover:bg-neutral-50" onClick={() => setActionTarget(null)} type="button">Cancel</button>
                <button className="h-10 rounded-lg bg-brand-600 px-4 text-sm font-medium capitalize text-white hover:bg-brand-700 disabled:opacity-60" disabled={actionMutation.isPending} type="submit">{actionTarget.action}</button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </div>
  );
}

// ── Reports Tab ──
function ReportsTab() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <BarChart3 size={32} className="text-neutral-300" />
      <p className="text-sm font-semibold text-neutral-500">Facility Reports</p>
      <p className="text-xs text-neutral-400">Export facility master list, accreditation reports, and assessment volume by LGA. Available soon.</p>
    </div>
  );
}

// ── Main Layout ──
export function MedicalFacilitiesLayout() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tabParam = (searchParams.get("tab") ?? "overview") as TabKey;

  const activeTab = TABS[tabParam] ? tabParam : "overview";

  function setTab(tab: TabKey) {
    router.replace(`/state/medical-facilities?tab=${tab}`);
  }

  return (
    <PortalShell
      role="state_admin"
      title="Medical Facilities"
      description="Manage facility registration, accreditation, re-accreditation, monitoring, and reporting for your state."
    >
      <nav className="mb-6 flex gap-0 overflow-x-auto border-b border-neutral-200">
        {(Object.entries(TABS) as [TabKey, string][]).map(([key, label]) => (
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
      {activeTab === "accreditation" && <AccreditationTab />}
      {activeTab === "reports" && <ReportsTab />}
    </PortalShell>
  );
}
