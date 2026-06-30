"use client";

import { useState } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Building2, ClipboardCheck, ShieldCheck, Activity, BarChart3,
  BadgeCheck,
} from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { DashboardCard } from "@/components/ui/dashboard-card";
import {
  approveStateFacilityApplication,
  fetchStateFacilities,
  fetchStateFacilityApplications,
  rejectStateFacilityApplication,
  reinstateStateFacilityApplication,
  suspendStateFacilityApplication,
} from "@/lib/api/state";
import { getApiErrorMessage } from "@/lib/api/client";
import type { FacilityAccreditationApplication, MedicalFacility } from "@/types/facilities";

type TabKey = "overview" | "facilities" | "accreditation";
type AccreditationAction = "approve" | "reject" | "suspend" | "reinstate";

const TABS: Record<TabKey, string> = {
  overview: "Overview",
  facilities: "Facilities",
  accreditation: "Accreditation",
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
const ACCREDITATION_QUEUE_CHIPS: { key: string; label: string }[] = [
  { key: "", label: "All Applications" },
  { key: "submitted", label: "Submitted" },
  { key: "under_review", label: "Under Review" },
  { key: "more_information_required", label: "Correction Requested" },
  { key: "approved", label: "Approved" },
  { key: "rejected", label: "Rejected" },
  { key: "suspended", label: "Suspended" },
  { key: "expired", label: "Expired" },
  { key: "reaccreditation_due", label: "Renewal Due" },
];

function dateLabel(v?: string) { if (!v) return "—"; return new Date(v).toLocaleDateString("en-NG", { dateStyle: "medium" }); }
function checklistScore(row: FacilityAccreditationApplication) {
  const keys: (keyof FacilityAccreditationApplication)[] = [
    "has_valid_facility_license",
    "has_reporting_policy",
    "has_medical_records_computers",
    "has_computer_operators",
    "has_standard_forms",
    "has_laboratory_request_forms",
    "has_patient_files",
    "has_qr_certificate_capability",
    "has_internet_access",
    "has_trained_records_staff",
    "has_trained_clinical_staff",
    "has_trained_non_clinical_staff",
    "has_laboratory_capacity",
    "has_valid_doctor_credentials",
    "has_valid_lab_staff_credentials",
    "has_infection_prevention_readiness",
    "has_confidentiality_policy",
  ];
  return `${keys.filter((key) => row[key]).length}/${keys.length}`;
}
function actionLabel(action: AccreditationAction) {
  return action === "reinstate" ? "Reinstate" : action.charAt(0).toUpperCase() + action.slice(1);
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

function AccreditationTab() {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState("");
  const [search, setSearch] = useState("");
  const [actionTarget, setActionTarget] = useState<{ row: FacilityAccreditationApplication; action: AccreditationAction } | null>(null);
  const [reviewNotes, setReviewNotes] = useState("");

  const applicationsQuery = useQuery({
    queryKey: ["state-facility-accreditation-queue", status, search],
    queryFn: () => fetchStateFacilityApplications({ status: status || undefined, search: search || undefined }),
  });

  const actionMutation = useMutation({
    mutationFn: async ({ row, action, notes }: { row: FacilityAccreditationApplication; action: AccreditationAction; notes: string }) => {
      if (action === "approve") return approveStateFacilityApplication(row.id, notes);
      if (action === "reject") return rejectStateFacilityApplication(row.id, notes);
      if (action === "suspend") return suspendStateFacilityApplication(row.id, notes);
      return reinstateStateFacilityApplication(row.id, notes);
    },
    onSuccess: () => {
      setActionTarget(null);
      setReviewNotes("");
      queryClient.invalidateQueries({ queryKey: ["state-facility-accreditation-queue"] });
      queryClient.invalidateQueries({ queryKey: ["state-facilities-overview"] });
      queryClient.invalidateQueries({ queryKey: ["state-facilities"] });
      queryClient.invalidateQueries({ queryKey: ["state-facility-apps-overview"] });
    },
  });

  const rows = applicationsQuery.data ?? [];
  const submitted = rows.filter((row) => row.application_status === "submitted").length;
  const underReview = rows.filter((row) => row.application_status === "under_review").length;
  const approved = rows.filter((row) => row.application_status === "approved").length;
  const renewal = rows.filter((row) => row.is_renewal || row.application_status === "reaccreditation_due").length;

  return (
    <div className="space-y-5">
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <DashboardCard icon={ClipboardCheck} label="Submitted" value={submitted} />
        <DashboardCard icon={Activity} label="Under Review" value={underReview} />
        <DashboardCard icon={ShieldCheck} label="Approved" value={approved} />
        <DashboardCard icon={BadgeCheck} label="Renewal Queue" value={renewal} />
      </section>

      <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-bold text-neutral-900">Accreditation review queue</p>
            <p className="mt-1 text-sm text-neutral-500">
              Review new applications, request correction through rejection notes where needed, and keep renewal cycles on track.
            </p>
          </div>
          <label className="grid gap-1 text-xs font-bold uppercase text-neutral-500">
            Search
            <input
              className="h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm normal-case font-normal text-neutral-700 lg:w-80"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Facility or reviewer"
            />
          </label>
        </div>
      </section>

      <div className="flex flex-wrap gap-2">
        {ACCREDITATION_QUEUE_CHIPS.map(({ key, label }) => (
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

      {applicationsQuery.isError ? (
        <p className="rounded bg-danger-50 p-3 text-sm font-semibold text-danger-700">Could not load accreditation applications.</p>
      ) : null}

      <DataTable<FacilityAccreditationApplication>
        columns={[
          {
            key: "facility",
            header: "Facility",
            render: (row) => (
              <div>
                <Link className="font-bold text-neutral-900 hover:text-brand-700" href={`/state/medical-facilities/${row.facility}`}>
                  {row.facility_name}
                </Link>
                <p className="text-xs text-neutral-500">{row.is_renewal ? "Re-accreditation" : "New accreditation"}</p>
              </div>
            ),
          },
          { key: "state", header: "State", render: (row) => row.facility_state || "Not set" },
          { key: "status", header: "Status", render: (row) => <StatusCell status={row.application_status} /> },
          { key: "checklist", header: "Checklist", render: (row) => <span className="font-bold text-neutral-900">{checklistScore(row)}</span> },
          { key: "reviewer", header: "Reviewer", render: (row) => row.reviewer_name || "Unassigned" },
          { key: "submitted", header: "Submitted", render: (row) => dateLabel(row.submitted_at || row.created_at) },
          { key: "reviewed", header: "Reviewed", render: (row) => dateLabel(row.reviewed_at) },
          { key: "comment", header: "Review note", render: (row) => row.review_comment || "No note recorded" },
          {
            key: "actions",
            header: "Action",
            render: (row) => {
              const canApprove = ["submitted", "under_review", "more_information_required", "reaccreditation_due"].includes(row.application_status);
              const canReject = ["submitted", "under_review", "more_information_required", "reaccreditation_due"].includes(row.application_status);
              const canSuspend = row.application_status === "approved";
              const canReinstate = ["suspended", "expired"].includes(row.application_status);
              return (
                <div className="flex flex-wrap gap-2">
                  {canApprove ? <button className="h-8 rounded border border-brand-200 px-3 text-xs font-bold text-brand-700" onClick={() => setActionTarget({ row, action: "approve" })} type="button">Approve</button> : null}
                  {canReject ? <button className="h-8 rounded border border-danger-100 px-3 text-xs font-bold text-danger-700" onClick={() => setActionTarget({ row, action: "reject" })} type="button">Reject</button> : null}
                  {canSuspend ? <button className="h-8 rounded border border-warning-200 px-3 text-xs font-bold text-warning-700" onClick={() => setActionTarget({ row, action: "suspend" })} type="button">Suspend</button> : null}
                  {canReinstate ? <button className="h-8 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700" onClick={() => setActionTarget({ row, action: "reinstate" })} type="button">Reinstate</button> : null}
                </div>
              );
            },
          },
        ]}
        rows={rows}
        empty={applicationsQuery.isLoading ? "Loading accreditation queue..." : "No accreditation applications match the current filter."}
      />

      {actionTarget ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-neutral-900/50 p-4">
          <div className="w-full max-w-md rounded-lg border border-neutral-200 bg-white shadow-xl">
            <div className="border-b border-neutral-100 px-6 py-4">
              <h2 className="text-lg font-bold text-neutral-900">{actionLabel(actionTarget.action)} facility application</h2>
              <p className="mt-1 text-sm text-neutral-500">{actionTarget.row.facility_name}</p>
            </div>
            <form
              className="grid gap-4 p-6"
              onSubmit={(event) => {
                event.preventDefault();
                actionMutation.mutate({ row: actionTarget.row, action: actionTarget.action, notes: reviewNotes });
              }}
            >
              <label className="grid gap-1 text-sm font-semibold text-neutral-700">
                Review notes
                <textarea
                  className="rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm"
                  rows={4}
                  value={reviewNotes}
                  onChange={(event) => setReviewNotes(event.target.value)}
                  placeholder="Add the basis for approval, correction, suspension, or reinstatement."
                />
              </label>
              {actionMutation.isError ? (
                <p className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">
                  {getApiErrorMessage(actionMutation.error, "Could not complete the accreditation action.")}
                </p>
              ) : null}
              <div className="flex justify-end gap-3">
                <button className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-600 hover:bg-neutral-50" onClick={() => setActionTarget(null)} type="button">Cancel</button>
                <button className="h-10 rounded bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60" disabled={actionMutation.isPending} type="submit">
                  {actionMutation.isPending ? "Saving..." : actionLabel(actionTarget.action)}
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
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
      description="Review facility applications, manage accreditation decisions, and monitor approved medical facilities across the state."
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
      {activeTab === "accreditation" && <AccreditationTab />}
    </PortalShell>
  );
}
