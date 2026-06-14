"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, BarChart3, Building2, ClipboardCheck, FileText, ShieldCheck } from "lucide-react";
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

  return (
    <PortalShell
      role="state_admin"
      title={facility?.facility_name ?? "Facility detail"}
      description="Review the facility profile, accreditation cycles, reports, and monitoring history in one place."
    >
      <div className="mb-6">
        <Link className="inline-flex items-center gap-2 rounded border border-neutral-200 bg-white px-3 py-2 text-sm font-bold text-neutral-700 shadow-sm hover:bg-neutral-50" href="/state/medical-facilities?tab=facilities">
          <ArrowLeft size={16} /> Medical Facilities
        </Link>
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

          <FacilityProfile facility={facility} />

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
