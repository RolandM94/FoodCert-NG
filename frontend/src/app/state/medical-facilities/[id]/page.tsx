"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, BarChart3, Building2, ClipboardCheck, Clock3, FileText, ShieldCheck } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchStateFacility, fetchStateFacilityApplications } from "@/lib/api/state";
import { listGeneratedReportsWithParams } from "@/lib/api/reports";
import type { FacilityAccreditationApplication, MedicalFacility } from "@/types/facilities";
import type { GeneratedReport } from "@/types/reports";

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

function text(value?: string | number | null) {
  if (value === null || value === undefined || value === "") return "Not set";
  return String(value);
}

function daysUntil(value?: string | null) {
  if (!value) return null;
  const today = new Date();
  const target = new Date(value);
  today.setHours(0, 0, 0, 0);
  target.setHours(0, 0, 0, 0);
  return Math.round((target.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
}

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

function reportBelongsToFacility(report: GeneratedReport, facilityId: string) {
  const filters = report.filters ?? {};
  const nestedFilters = typeof filters.filters === "object" && filters.filters !== null ? filters.filters as Record<string, unknown> : {};
  return filters.facility === facilityId || nestedFilters.facility === facilityId;
}

function StatCard({ icon: Icon, label, value }: { icon: typeof Building2; label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <Icon className="text-brand-700" size={18} />
      <p className="mt-3 text-xs font-bold uppercase tracking-wide text-neutral-500">{label}</p>
      <p className="mt-1 text-xl font-bold text-neutral-950">{value}</p>
    </div>
  );
}

function ReadinessPill({ label, ready, detail }: { label: string; ready: boolean; detail: string }) {
  return (
    <div className={`rounded-lg border px-4 py-3 ${ready ? "border-brand-200 bg-brand-50" : "border-warning-200 bg-warning-50"}`}>
      <div className="flex items-center justify-between gap-3">
        <p className={`text-sm font-bold ${ready ? "text-brand-900" : "text-warning-900"}`}>{label}</p>
        <span className={`rounded-full px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide ${ready ? "bg-white text-brand-700" : "bg-white text-warning-700"}`}>
          {ready ? "Ready" : "Attention"}
        </span>
      </div>
      <p className={`mt-2 text-sm ${ready ? "text-brand-800" : "text-warning-800"}`}>{detail}</p>
    </div>
  );
}

function AccreditationDecisionSummary({
  facility,
  latestApplication,
}: {
  facility: MedicalFacility;
  latestApplication?: FacilityAccreditationApplication;
}) {
  const expiryDelta = daysUntil(facility.accreditation_expiry_date);
  const expiryLabel = expiryDelta === null
    ? "Expiry date has not been set."
    : expiryDelta < 0
      ? `Expired ${Math.abs(expiryDelta)} day${Math.abs(expiryDelta) === 1 ? "" : "s"} ago.`
      : expiryDelta === 0
        ? "Expires today."
        : `Expires in ${expiryDelta} day${expiryDelta === 1 ? "" : "s"}.`;

  const readinessItems = [
    {
      label: "Public booking eligibility",
      ready: facility.can_conduct_assessments,
      detail: facility.can_conduct_assessments
        ? "Facility can receive bookings and process assessments under the current approval state."
        : "Facility should not receive new bookings until accreditation and activity conditions are restored.",
    },
    {
      label: "Profile completeness",
      ready: facility.profile_complete,
      detail: facility.profile_complete
        ? "Core operational and accreditation profile details are complete."
        : "State should request missing profile records before relying on this facility in production.",
    },
    {
      label: "Accreditation validity",
      ready: expiryDelta === null ? facility.accreditation_status === "approved" : expiryDelta >= 0,
      detail: expiryLabel,
    },
  ];

  return (
    <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2">
          <ShieldCheck className="text-brand-700" size={18} />
          <h2 className="text-base font-bold text-neutral-900">Accreditation decision summary</h2>
        </div>
        <dl className="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-xs font-bold uppercase tracking-wide text-neutral-500">Current status</dt>
            <dd className="mt-1"><StatusBadge status={facility.accreditation_status} /></dd>
          </div>
          <div>
            <dt className="text-xs font-bold uppercase tracking-wide text-neutral-500">Approval owner</dt>
            <dd className="mt-1 text-sm font-semibold text-neutral-900">{facility.approved_by_name || latestApplication?.reviewer_name || "Not assigned"}</dd>
          </div>
          <div>
            <dt className="text-xs font-bold uppercase tracking-wide text-neutral-500">Accreditation start</dt>
            <dd className="mt-1 text-sm font-semibold text-neutral-900">{dateLabel(facility.accreditation_start_date)}</dd>
          </div>
          <div>
            <dt className="text-xs font-bold uppercase tracking-wide text-neutral-500">Accreditation expiry</dt>
            <dd className="mt-1 text-sm font-semibold text-neutral-900">{dateLabel(facility.accreditation_expiry_date)}</dd>
          </div>
          <div>
            <dt className="text-xs font-bold uppercase tracking-wide text-neutral-500">Assessment package price</dt>
            <dd className="mt-1 text-sm font-semibold text-neutral-900">
              {facility.standard_assessment_price ? `NGN ${Number(facility.standard_assessment_price).toLocaleString("en-NG")}` : "Not set"}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-bold uppercase tracking-wide text-neutral-500">Latest decision note</dt>
            <dd className="mt-1 text-sm text-neutral-700">{latestApplication?.review_comment || "No decision note recorded yet."}</dd>
          </div>
        </dl>
      </div>

      <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2">
          <Clock3 className="text-brand-700" size={18} />
          <h2 className="text-base font-bold text-neutral-900">Operational readiness</h2>
        </div>
        <div className="mt-4 grid gap-3">
          {readinessItems.map((item) => (
            <ReadinessPill key={item.label} detail={item.detail} label={item.label} ready={item.ready} />
          ))}
        </div>
      </div>
    </section>
  );
}

function AccreditationTimeline({ applications }: { applications: FacilityAccreditationApplication[] }) {
  const timeline = applications.flatMap((application) => {
    const events = [
      {
        id: `${application.id}-created`,
        label: application.is_renewal ? "Re-accreditation initiated" : "Application created",
        date: application.created_at,
        tone: "neutral",
        detail: application.checklist_complete
          ? `Checklist complete at ${checklistScore(application)}.`
          : `Checklist still in progress at ${checklistScore(application)}.`,
      },
      application.submitted_at
        ? {
            id: `${application.id}-submitted`,
            label: "Submitted to State",
            date: application.submitted_at,
            tone: "brand",
            detail: "Application entered the State accreditation review queue.",
          }
        : null,
      application.reviewed_at
        ? {
            id: `${application.id}-reviewed`,
            label: application.application_status.replaceAll("_", " "),
            date: application.reviewed_at,
            tone: ["approved"].includes(application.application_status) ? "brand" : ["rejected", "suspended", "expired"].includes(application.application_status) ? "danger" : "warning",
            detail: application.review_comment || "Reviewed without an additional comment.",
          }
        : null,
    ].filter(Boolean) as Array<{ id: string; label: string; date: string; tone: "neutral" | "brand" | "warning" | "danger"; detail: string }>;
    return events;
  }).sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-2">
        <ClipboardCheck className="text-brand-700" size={18} />
        <h2 className="text-base font-bold text-neutral-900">Accreditation timeline</h2>
      </div>
      {timeline.length === 0 ? (
        <p className="mt-4 text-sm text-neutral-500">No accreditation events have been recorded for this facility yet.</p>
      ) : (
        <div className="mt-4 space-y-4">
          {timeline.map((event) => (
            <div key={event.id} className="flex gap-4">
              <div className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${event.tone === "brand" ? "bg-brand-600" : event.tone === "warning" ? "bg-warning-500" : event.tone === "danger" ? "bg-danger-500" : "bg-neutral-300"}`} />
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-sm font-bold text-neutral-900 capitalize">{event.label}</p>
                  <span className="text-xs font-semibold text-neutral-500">{dateLabel(event.date)}</span>
                </div>
                <p className="mt-1 text-sm text-neutral-600">{event.detail}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

function FacilityProfile({ facility }: { facility: MedicalFacility }) {
  const fields = [
    ["Facility type", facility.facility_type.replaceAll("_", " ")],
    ["Ownership", facility.ownership_type],
    ["License number", facility.license_number],
    ["Registration number", facility.registration_number],
    ["State", facility.state_name],
    ["LGA", facility.lga_name],
    ["Ward", facility.ward],
    ["Contact person", facility.contact_person],
    ["Phone", facility.phone],
    ["Email", facility.email],
    ["Operating hours", facility.operating_hours],
    ["Service capacity", facility.service_capacity],
    ["Address", facility.address],
  ];

  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-2">
        <Building2 className="text-brand-700" size={18} />
        <h2 className="text-base font-bold text-neutral-900">Facility information</h2>
      </div>
      <dl className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {fields.map(([label, value]) => (
          <div key={label} className={label === "Address" ? "lg:col-span-3" : ""}>
            <dt className="text-xs font-bold uppercase tracking-wide text-neutral-500">{label}</dt>
            <dd className="mt-1 text-sm font-semibold capitalize text-neutral-900">{text(value)}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

export default function StateFacilityDetailPage() {
  const params = useParams<{ id: string }>();
  const facilityId = params.id;

  const facilityQuery = useQuery({
    queryKey: ["state-facility-detail", facilityId],
    queryFn: () => fetchStateFacility(facilityId),
  });

  const applicationsQuery = useQuery({
    queryKey: ["state-facility-detail-applications", facilityId],
    queryFn: () => fetchStateFacilityApplications({}),
  });

  const reportsQuery = useQuery({
    queryKey: ["state-facility-detail-reports", facilityId],
    queryFn: () => listGeneratedReportsWithParams({ report_type: "facility_performance" }),
  });

  const facility = facilityQuery.data;
  const applications = (applicationsQuery.data ?? [])
    .filter((application) => application.facility === facilityId)
    .sort((a, b) => new Date(b.submitted_at || b.created_at).getTime() - new Date(a.submitted_at || a.created_at).getTime());
  const reports = (reportsQuery.data ?? [])
    .filter((report) => reportBelongsToFacility(report, facilityId))
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  const latestApplication = applications[0];

  return (
    <PortalShell
      role="state_admin"
      title={facility?.facility_name ?? "Facility detail"}
      description="Review the facility profile, accreditation cycles, reports, and monitoring history in one place."
    >
      <div className="mb-6">
        <div className="flex flex-wrap gap-3">
          <Link className="inline-flex items-center gap-2 rounded border border-neutral-200 bg-white px-3 py-2 text-sm font-bold text-neutral-700 shadow-sm hover:bg-neutral-50" href="/state/medical-facilities?tab=facilities">
            <ArrowLeft size={16} /> Medical Facilities
          </Link>
          <Link className="inline-flex items-center gap-2 rounded border border-neutral-200 bg-white px-3 py-2 text-sm font-bold text-neutral-700 shadow-sm hover:bg-neutral-50" href="/state/medical-facilities?tab=accreditation">
            <ClipboardCheck size={16} /> Accreditation Queue
          </Link>
        </div>
      </div>

      {facilityQuery.isError ? (
        <p className="rounded bg-danger-50 p-3 text-sm font-semibold text-danger-700">Could not load this facility.</p>
      ) : null}

      {!facility ? (
        <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading facility...</p>
      ) : (
        <div className="space-y-6">
          <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-brand-700">State facility record</p>
                <h1 className="mt-1 text-2xl font-bold text-neutral-950">{facility.facility_name}</h1>
                <p className="mt-2 max-w-3xl text-sm text-neutral-600">{facility.address || "No address has been recorded."}</p>
              </div>
              <StatusBadge status={facility.accreditation_status} />
            </div>
          </section>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard icon={ShieldCheck} label="Current accreditation" value={facility.accreditation_status.replaceAll("_", " ")} />
            <StatCard icon={ClipboardCheck} label="Accreditation cycles" value={applications.length} />
            <StatCard icon={FileText} label="Facility reports" value={reports.length} />
            <StatCard icon={BarChart3} label="Assessment ready" value={facility.can_conduct_assessments ? "Yes" : "No"} />
          </div>

          <AccreditationDecisionSummary facility={facility} latestApplication={latestApplication} />

          <FacilityProfile facility={facility} />

          <AccreditationTimeline applications={applications} />

          <section className="grid gap-3">
            <div className="flex items-center gap-2">
              <ClipboardCheck className="text-brand-700" size={18} />
              <h2 className="text-base font-bold text-neutral-900">Accreditation history</h2>
            </div>
            <DataTable<FacilityAccreditationApplication>
              columns={[
                { key: "cycle", header: "Cycle", render: (row) => row.is_renewal ? "Re-accreditation" : "New accreditation" },
                { key: "status", header: "Status", render: (row) => <StatusCell status={row.application_status} /> },
                { key: "checklist", header: "Checklist", render: (row) => <span className={row.checklist_complete ? "font-bold text-brand-700" : "font-bold text-warning-700"}>{checklistScore(row)}</span> },
                { key: "submitted", header: "Submitted", render: (row) => dateLabel(row.submitted_at || row.created_at) },
                { key: "reviewed", header: "Reviewed", render: (row) => dateLabel(row.reviewed_at) },
                { key: "reviewer", header: "Reviewer", render: (row) => row.reviewer_name || "Not reviewed" },
                { key: "comment", header: "Decision note", render: (row) => row.review_comment || "No note" },
              ]}
              rows={applications}
              empty={applicationsQuery.isLoading ? "Loading accreditation history..." : "No accreditation history has been recorded for this facility."}
            />
          </section>

          <section className="grid gap-3">
            <div className="flex items-center gap-2">
              <FileText className="text-brand-700" size={18} />
              <h2 className="text-base font-bold text-neutral-900">Report history</h2>
            </div>
            <DataTable<GeneratedReport>
              columns={[
                { key: "type", header: "Report", render: (row) => row.report_type.replaceAll("_", " ") },
                { key: "format", header: "Format", render: (row) => row.file_format.toUpperCase() },
                { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
                { key: "generated_by", header: "Generated by", render: (row) => row.generated_by_name || "System" },
                { key: "created", header: "Created", render: (row) => dateLabel(row.created_at) },
                { key: "file", header: "File", render: (row) => row.file_url ? <a className="font-bold text-brand-700 hover:underline" href={row.file_url} rel="noreferrer" target="_blank">Open</a> : "No file" },
              ]}
              rows={reports}
              empty={reportsQuery.isLoading ? "Loading reports..." : "No generated reports have been linked to this facility yet."}
            />
          </section>
        </div>
      )}
    </PortalShell>
  );
}
