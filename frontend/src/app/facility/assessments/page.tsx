"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, ClipboardList, Download, Filter, HeartPulse, RefreshCw, Stethoscope, UserRoundCheck } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { assignFacilityAssessmentDoctor, assignFacilityAssessmentLab, listFacilityAssessments } from "@/lib/api/assessments";
import { getAssessmentReport } from "@/lib/api/reports";
import { getCurrentMedicalFacility, listFacilityStaff, listFacilityTemporaryUnfitReports } from "@/lib/api/facilities";
import { fetchUnits } from "@/lib/api/organizations";
import type { MedicalAssessment } from "@/types/assessments";
import type { FacilityStaffProfile, FacilityTemporaryUnfitReport, MedicalFacility } from "@/types/facilities";
import type { OrganizationUnit } from "@/types/organizations";

const ASSESSMENT_STATUSES = [
  ["", "All statuses"],
  ["payment_pending", "Payment pending"],
  ["payment_confirmed", "Payment confirmed"],
  ["appointment_booked", "Appointment booked"],
  ["declaration_submitted", "Declaration submitted"],
  ["declaration_validated", "Declaration validated"],
  ["physical_exam_completed", "Physical exam completed"],
  ["lab_tests_pending", "Lab pending"],
  ["lab_results_reviewed", "Lab reviewed"],
  ["vaccination_reviewed", "Vaccination reviewed"],
  ["fit", "Fit"],
  ["temporarily_not_fit", "Temporarily not fit"],
  ["not_fit", "Not fit"],
  ["submitted_for_state_validation", "Submitted to state"],
];

const STEP_ORDER = ["declaration_status", "physical_exam_status", "lab_status", "vaccination_status", "final_decision"] as const;
const QUEUE_OPTIONS = [
  {
    value: "all",
    label: "All Assessments",
    description: "Standard, renewal, high-risk, and return-to-work cases in one queue.",
    assessmentType: "",
  },
  {
    value: "return-to-work",
    label: "Return-to-Work",
    description: "Temporary exclusion follow-up and clearance-focused assessment cases.",
    assessmentType: "return_to_work",
  },
  {
    value: "temporary-unfit",
    label: "Temporarily Unfit",
    description: "Review temporary unfit decisions, open the linked assessment, and download permitted return-to-work report views.",
    assessmentType: "",
  },
] as const;

type ActiveQueue = (typeof QUEUE_OPTIONS)[number]["value"];

function label(value?: string) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

function formatDate(value?: string) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium" }).format(new Date(value));
}

function downloadJson(filename: string, payload: unknown) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function FacilityAssessmentsPageContent() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const initialQueue = searchParams.get("queue");
  const [facility, setFacility] = useState<MedicalFacility | null>(null);
  const [assessments, setAssessments] = useState<MedicalAssessment[]>([]);
  const [unfitReports, setUnfitReports] = useState<FacilityTemporaryUnfitReport[]>([]);
  const [doctors, setDoctors] = useState<FacilityStaffProfile[]>([]);
  const [labStaff, setLabStaff] = useState<FacilityStaffProfile[]>([]);
  const [labUnits, setLabUnits] = useState<OrganizationUnit[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [reassignReason, setReassignReason] = useState<Record<string, string>>({});
  const [filters, setFilters] = useState({
    status: "",
    doctor: "",
    lab_status: "",
    payment_status: "",
    decision_status: "",
    assessment_type: initialQueue === "return-to-work" ? "return_to_work" : "",
  });

  const activeQueue: ActiveQueue = initialQueue === "return-to-work"
    ? "return-to-work"
    : initialQueue === "temporary-unfit"
      ? "temporary-unfit"
      : "all";

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const profile = await getCurrentMedicalFacility();
      setFacility(profile);

      if (activeQueue === "temporary-unfit") {
        const reportRows = await listFacilityTemporaryUnfitReports(profile.id);
        setUnfitReports(reportRows);
      } else {
        const params = Object.fromEntries(Object.entries(filters).filter(([, value]) => value));
        const [rows, staffRows, unitRows] = await Promise.all([
          listFacilityAssessments(profile.id, params),
          listFacilityStaff(profile.id),
          fetchUnits(profile.organization),
        ]);
        setAssessments(rows);
        setDoctors(staffRows.filter((row) => row.is_active && row.staff_type === "doctor"));
        setLabStaff(staffRows.filter((row) => row.is_active && row.staff_type === "lab_staff"));
        setLabUnits(unitRows.filter((row) => row.unit_type === "lab_department" && row.is_active));
      }
    } catch {
      setError(activeQueue === "temporary-unfit" ? "Could not load temporary unfit reports." : "Could not load assessment queue.");
    } finally {
      setLoading(false);
    }
  }, [filters, activeQueue]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const metrics = useMemo(() => ({
    total: assessments.length,
    unassigned: assessments.filter((row) => !row.doctor).length,
    labPending: assessments.filter((row) => row.lab_status === "pending" || row.lab_status === "submitted").length,
    stateReady: assessments.filter((row) => row.can_request_certificate).length,
  }), [assessments]);

  const queueCounts = useMemo<Record<ActiveQueue, number>>(() => ({
    all: metrics.total,
    "return-to-work": assessments.filter((row) => row.assessment_type === "return_to_work").length,
    "temporary-unfit": unfitReports.length,
  }), [assessments, metrics.total, unfitReports.length]);

  function updateFilter(field: keyof typeof filters, value: string) {
    setFilters((current) => ({ ...current, [field]: value }));
  }

  function setQueue(queue: ActiveQueue) {
    const params = new URLSearchParams(searchParams.toString());
    if (queue === "return-to-work") {
      params.set("queue", "return-to-work");
    } else if (queue === "temporary-unfit") {
      params.set("queue", "temporary-unfit");
    } else {
      params.delete("queue");
    }
    const query = params.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  async function assignDoctor(assessment: MedicalAssessment, doctorId: string) {
    if (!facility || !doctorId) return;
    setBusyId(assessment.id);
    setError("");
    setSuccess("");
    try {
      const updated = await assignFacilityAssessmentDoctor(facility.id, assessment.id, doctorId, reassignReason[assessment.id] || "");
      setAssessments((rows) => rows.map((row) => row.id === updated.id ? updated : row));
      setReassignReason((current) => ({ ...current, [assessment.id]: "" }));
      setSuccess("Doctor assigned.");
    } catch {
      setError("Could not assign doctor. Reassignment after doctor work starts requires a reason.");
    } finally {
      setBusyId("");
    }
  }

  async function assignLab(assessment: MedicalAssessment, payload: { lab_staff?: string | null; lab_unit?: string | null }) {
    if (!facility || (!payload.lab_staff && !payload.lab_unit)) return;
    setBusyId(assessment.id);
    setError("");
    setSuccess("");
    try {
      const updated = await assignFacilityAssessmentLab(facility.id, assessment.id, {
        ...payload,
        reason: reassignReason[assessment.id] || "",
      });
      setAssessments((rows) => rows.map((row) => row.id === updated.id ? updated : row));
      setReassignReason((current) => ({ ...current, [assessment.id]: "" }));
      setSuccess("Lab assignment updated.");
    } catch {
      setError("Could not assign lab owner. Reassignment after work starts requires a reason, and lab assignment can only happen after physical examination is completed.");
    } finally {
      setBusyId("");
    }
  }

  async function downloadReport(row: FacilityTemporaryUnfitReport) {
    setBusyId(row.assessment_id);
    setError("");
    try {
      const report = await getAssessmentReport(row.assessment_id, "return-to-work");
      downloadJson(`${row.food_handler_name.replaceAll(/\s+/g, "-").toLowerCase()}-temporary-unfit-report.json`, report);
    } catch {
      setError("Could not download the temporary unfit report.");
    } finally {
      setBusyId("");
    }
  }

  const showAssessmentsTab = activeQueue !== "temporary-unfit";

  return (
    <PortalShell role="facility_admin" title="Assessments" description="Coordinate paid assessments, doctor review, lab review, vaccination review, and state submission readiness.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading assessments...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}
        {success ? <div className="rounded-lg bg-brand-50 p-3 text-sm font-semibold text-brand-800">{success}</div> : null}

{showAssessmentsTab ? (
        <>
          <section className="grid gap-3 md:grid-cols-4">
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><ClipboardList className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Queue</p><p className="text-2xl font-bold text-neutral-900">{metrics.total}</p></div>
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><UserRoundCheck className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Unassigned</p><p className="text-2xl font-bold text-neutral-900">{metrics.unassigned}</p></div>
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><Stethoscope className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Lab pending</p><p className="text-2xl font-bold text-neutral-900">{metrics.labPending}</p></div>
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><RefreshCw className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">State ready</p><p className="text-2xl font-bold text-neutral-900">{metrics.stateReady}</p></div>
          </section>
        </>
      ) : (
        <>
          <section className="grid gap-3 md:grid-cols-3">
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <HeartPulse className="text-brand-700" size={18} />
              <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Open temporary unfit cases</p>
              <p className="text-2xl font-bold text-neutral-900">{unfitReports.length}</p>
            </div>
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <p className="text-xs font-bold uppercase text-neutral-500">Facility</p>
              <p className="mt-2 text-lg font-bold text-neutral-900">{facility?.facility_name || "Current facility"}</p>
            </div>
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <p className="text-xs font-bold uppercase text-neutral-500">Report registry</p>
              <p className="mt-2 text-lg font-bold text-neutral-900">{unfitReports.filter((row) => row.report_id).length} generated</p>
            </div>
          </section>
        </>
      )}

        {showAssessmentsTab ? (
          <section className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <div>
              <p className="text-sm font-bold text-neutral-900">Assessment form templates</p>
              <p className="mt-1 text-sm text-neutral-500">Adopt state-approved declaration templates and extend them with facility-specific follow-up fields.</p>
            </div>
            <Link className="inline-flex h-10 items-center rounded bg-brand-600 px-4 text-sm font-bold text-white" href="/facility/assessments/forms">
              Open template workspace
            </Link>
          </section>
        ) : null}

        <section className="overflow-x-auto">
          <div className="inline-flex min-w-full flex-wrap gap-2 rounded-2xl border border-neutral-200 bg-white p-2 shadow-sm sm:min-w-0">
            {QUEUE_OPTIONS.map((queue) => (
              <button
                key={queue.value}
                type="button"
                onClick={() => setQueue(queue.value)}
                className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium whitespace-nowrap transition ${
                  activeQueue === queue.value
                    ? "bg-brand-50 text-brand-800 ring-1 ring-brand-200"
                    : "bg-neutral-50 text-neutral-600 hover:bg-neutral-100"
                }`}
              >
                <span>{queue.label}</span>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                    activeQueue === queue.value
                      ? "bg-white text-brand-700"
                      : "bg-white text-neutral-500"
                  }`}
                >
                  {queueCounts[queue.value]}
                </span>
              </button>
            ))}
          </div>
        </section>

        {showAssessmentsTab ? (
        <>
          <section className="flex flex-wrap items-center gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <Filter size={18} className="text-brand-700" />
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={filters.status} onChange={(event) => updateFilter("status", event.target.value)}>
              {ASSESSMENT_STATUSES.map(([value, text]) => <option key={value} value={value}>{text}</option>)}
            </select>
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={filters.doctor} onChange={(event) => updateFilter("doctor", event.target.value)}>
              <option value="">All doctors</option>
              {doctors.map((profile) => <option key={profile.user} value={profile.user}>{profile.user_name || profile.user_email}</option>)}
            </select>
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={filters.payment_status} onChange={(event) => updateFilter("payment_status", event.target.value)}>
              <option value="">All payments</option><option value="success">Paid</option><option value="pending">Pending</option><option value="missing">Missing</option>
            </select>
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={filters.assessment_type} onChange={(event) => updateFilter("assessment_type", event.target.value)}>
              <option value="">All assessment types</option>
              <option value="standard">Standard</option>
              <option value="renewal">Renewal</option>
              <option value="return_to_work">Return-to-work</option>
              <option value="high_risk">High-risk</option>
            </select>
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={filters.lab_status} onChange={(event) => updateFilter("lab_status", event.target.value)}>
              <option value="">All lab states</option><option value="pending">Pending</option><option value="submitted">Submitted</option><option value="reviewed">Reviewed</option>
            </select>
            <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-600 px-3 text-sm font-bold text-white" type="button" onClick={() => void loadData()}><RefreshCw size={16} /> Apply</button>
          </section>

          <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
            <div className="border-b border-neutral-200 p-4">
              <h2 className="text-sm font-bold text-neutral-900">
                {activeQueue === "return-to-work" ? "Return-to-Work Queue" : "Assessment Queue"}
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-neutral-50 text-xs font-bold uppercase text-neutral-500">
                  <tr><th className="p-3">Food handler</th><th className="p-3">Payment</th><th className="p-3">Workflow</th><th className="p-3">Doctor</th><th className="p-3">Lab Assignment</th><th className="p-3">State</th><th className="p-3">Action</th></tr>
                </thead>
                <tbody className="divide-y divide-neutral-200">
                  {assessments.length ? assessments.map((assessment) => (
                    <tr key={assessment.id}>
                      <td className="p-3"><p className="font-bold text-neutral-900">{assessment.food_handler_name}</p><p className="text-xs text-neutral-500">{assessment.food_handler_identifier} · {assessment.employer_name || "Individual"} · {assessment.branch_name || "No branch"}</p></td>
                      <td className="p-3"><StatusBadge status={assessment.payment_status || "missing"} /></td>
                      <td className="p-3">
                        <div className="flex flex-wrap gap-1">
                          {STEP_ORDER.map((step) => <span className="rounded bg-neutral-100 px-2 py-1 text-[11px] font-bold capitalize text-neutral-600" key={step}>{label(assessment[step] as string)}</span>)}
                        </div>
                      </td>
                      <td className="p-3">
                        <select className="h-9 rounded border border-neutral-200 bg-white px-2 text-xs" disabled={busyId === assessment.id} value={assessment.doctor || ""} onChange={(event) => void assignDoctor(assessment, event.target.value)}>
                          <option value="">Unassigned</option>
                          {doctors.map((profile) => <option key={profile.user} value={profile.user}>{profile.user_name || profile.user_email}</option>)}
                        </select>
                      </td>
                      <td className="min-w-[280px] p-3">
                        <div className="grid gap-2">
                          <select
                            className="h-9 rounded border border-neutral-200 bg-white px-2 text-xs"
                            disabled={busyId === assessment.id || assessment.physical_exam_status !== "completed"}
                            value={assessment.assigned_lab_unit || ""}
                            onChange={(event) => void assignLab(assessment, { lab_unit: event.target.value || null, lab_staff: assessment.assigned_lab_staff || null })}
                          >
                            <option value="">Select lab unit</option>
                            {labUnits.map((unit) => <option key={unit.id} value={unit.id}>{unit.name}</option>)}
                          </select>
                          <select
                            className="h-9 rounded border border-neutral-200 bg-white px-2 text-xs"
                            disabled={busyId === assessment.id || assessment.physical_exam_status !== "completed"}
                            value={assessment.assigned_lab_staff || ""}
                            onChange={(event) => void assignLab(assessment, { lab_staff: event.target.value || null, lab_unit: assessment.assigned_lab_unit || null })}
                          >
                            <option value="">Select lab staff</option>
                            {labStaff.map((profile) => <option key={profile.user} value={profile.user}>{profile.user_name || profile.user_email}</option>)}
                          </select>
                          <input
                            className="h-9 rounded border border-neutral-200 bg-neutral-50 px-2 text-xs"
                            disabled={busyId === assessment.id}
                            placeholder="Reason if reassigning after work started"
                            value={reassignReason[assessment.id] || ""}
                            onChange={(event) => setReassignReason((current) => ({ ...current, [assessment.id]: event.target.value }))}
                          />
                          <p className="text-[11px] text-neutral-500">
                            {assessment.assigned_lab_staff_name || assessment.assigned_lab_unit_name
                              ? `Current: ${assessment.assigned_lab_staff_name || "No named staff"}${assessment.assigned_lab_unit_name ? ` · ${assessment.assigned_lab_unit_name}` : ""}`
                              : assessment.physical_exam_status === "completed"
                                ? "Ready for lab assignment"
                                : "Complete physical exam before assigning lab work"}
                          </p>
                        </div>
                      </td>
                      <td className="p-3"><StatusBadge status={assessment.status} /></td>
                      <td className="p-3"><Link className="rounded border border-neutral-200 px-3 py-1.5 text-xs font-bold text-neutral-700" href={`/facility/assessments/${assessment.id}`}>Open</Link></td>
                    </tr>
                  )) : (
                    <tr><td className="p-3 text-neutral-500" colSpan={7}>No assessments match the current filters.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </>
      ) : (
          <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
            <div className="flex items-center justify-between gap-3 border-b border-neutral-200 p-4">
              <div>
                <h2 className="text-sm font-bold text-neutral-900">Temporary unfit registry</h2>
                <p className="text-xs text-neutral-500">Only team members with temporary unfit report access can use this workspace.</p>
              </div>
              <button className="inline-flex h-9 items-center gap-2 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700" type="button" onClick={() => void loadData()}>
                <RefreshCw size={14} /> Refresh
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-neutral-50 text-xs font-bold uppercase text-neutral-500">
                  <tr>
                    <th className="p-3">Food handler</th>
                    <th className="p-3">Employer</th>
                    <th className="p-3">Decision</th>
                    <th className="p-3">Return-to-work date</th>
                    <th className="p-3">Report</th>
                    <th className="p-3">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200">
                  {unfitReports.length ? unfitReports.map((row) => (
                    <tr key={row.assessment_id}>
                      <td className="p-3">
                        <p className="font-bold text-neutral-900">{row.food_handler_name}</p>
                        <p className="text-xs text-neutral-500">Signed {formatDate(row.signed_at)}</p>
                      </td>
                      <td className="p-3 text-neutral-700">{row.employer_name || "Individual"}</td>
                      <td className="p-3">
                        <StatusBadge status={row.final_decision} />
                        <p className="mt-1 text-xs text-neutral-500 capitalize">{label(row.status)}</p>
                      </td>
                      <td className="p-3 text-neutral-700">{formatDate(row.return_to_work_date)}</td>
                      <td className="p-3">
                        {row.report_id ? <StatusBadge status={row.report_status || "generated"} /> : <span className="text-xs font-semibold text-neutral-500">Not generated yet</span>}
                      </td>
                      <td className="p-3">
                        <div className="flex flex-wrap gap-2">
                          <Link className="rounded border border-neutral-200 px-3 py-1.5 text-xs font-bold text-neutral-700" href={`/facility/assessments/${row.assessment_id}`}>
                            Open
                          </Link>
                          <button
                            className="inline-flex items-center gap-1 rounded border border-brand-200 px-3 py-1.5 text-xs font-bold text-brand-700 disabled:opacity-60"
                            disabled={busyId === row.assessment_id}
                            onClick={() => void downloadReport(row)}
                            type="button"
                          >
                            <Download size={14} /> Download
                          </button>
                        </div>
                      </td>
                    </tr>
                  )) : (
                    <tr><td className="p-3 text-neutral-500" colSpan={6}>No temporary unfit reports are registered for this facility yet.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
      )}
      </div>
    </PortalShell>
  );
}

export default function Page() {
  return (
    <Suspense fallback={null}>
      <FacilityAssessmentsPageContent />
    </Suspense>
  );
}
