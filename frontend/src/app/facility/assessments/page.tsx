"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, ClipboardList, Filter, RefreshCw, Stethoscope, UserRoundCheck } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { assignFacilityAssessmentDoctor, listFacilityAssessments } from "@/lib/api/assessments";
import { getCurrentMedicalFacility, listFacilityStaff } from "@/lib/api/facilities";
import type { MedicalAssessment } from "@/types/assessments";
import type { FacilityStaffProfile, MedicalFacility } from "@/types/facilities";

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

function label(value?: string) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

export default function Page() {
  const searchParams = useSearchParams();
  const initialQueue = searchParams.get("queue");
  const [facility, setFacility] = useState<MedicalFacility | null>(null);
  const [assessments, setAssessments] = useState<MedicalAssessment[]>([]);
  const [doctors, setDoctors] = useState<FacilityStaffProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [filters, setFilters] = useState({
    status: "",
    doctor: "",
    lab_status: "",
    payment_status: "",
    decision_status: "",
    assessment_type: initialQueue === "return-to-work" ? "return_to_work" : "",
  });

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const profile = await getCurrentMedicalFacility();
      const params = Object.fromEntries(Object.entries(filters).filter(([, value]) => value));
      const [rows, staffRows] = await Promise.all([
        listFacilityAssessments(profile.id, params),
        listFacilityStaff(profile.id),
      ]);
      setFacility(profile);
      setAssessments(rows);
      setDoctors(staffRows.filter((row) => row.is_active && row.staff_type === "doctor"));
    } catch {
      setError("Could not load assessment queue.");
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const metrics = useMemo(() => ({
    total: assessments.length,
    unassigned: assessments.filter((row) => !row.doctor).length,
    labPending: assessments.filter((row) => row.lab_status === "pending" || row.lab_status === "submitted").length,
    stateReady: assessments.filter((row) => row.can_request_certificate).length,
  }), [assessments]);

  function updateFilter(field: keyof typeof filters, value: string) {
    setFilters((current) => ({ ...current, [field]: value }));
  }

  async function assignDoctor(assessment: MedicalAssessment, doctorId: string) {
    if (!facility || !doctorId) return;
    setBusyId(assessment.id);
    setError("");
    setSuccess("");
    try {
      const updated = await assignFacilityAssessmentDoctor(facility.id, assessment.id, doctorId);
      setAssessments((rows) => rows.map((row) => row.id === updated.id ? updated : row));
      setSuccess("Doctor assigned.");
    } catch {
      setError("Could not assign doctor.");
    } finally {
      setBusyId("");
    }
  }

  return (
    <PortalShell role="facility_admin" title="Assessments" description="Coordinate paid assessments, doctor review, lab review, vaccination review, and state submission readiness.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading assessments...</p> : null}

        <section className="grid gap-3 md:grid-cols-4">
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><ClipboardList className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Queue</p><p className="text-2xl font-bold text-neutral-900">{metrics.total}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><UserRoundCheck className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Unassigned</p><p className="text-2xl font-bold text-neutral-900">{metrics.unassigned}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><Stethoscope className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Lab pending</p><p className="text-2xl font-bold text-neutral-900">{metrics.labPending}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><RefreshCw className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">State ready</p><p className="text-2xl font-bold text-neutral-900">{metrics.stateReady}</p></div>
        </section>

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
            <h2 className="text-sm font-bold text-neutral-900">Assessment Queue</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-neutral-50 text-xs font-bold uppercase text-neutral-500">
                <tr><th className="p-3">Food handler</th><th className="p-3">Payment</th><th className="p-3">Workflow</th><th className="p-3">Doctor</th><th className="p-3">State</th><th className="p-3">Action</th></tr>
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
                    <td className="p-3"><StatusBadge status={assessment.status} /></td>
                    <td className="p-3"><Link className="rounded border border-neutral-200 px-3 py-1.5 text-xs font-bold text-neutral-700" href={`/facility/assessments/${assessment.id}`}>Open</Link></td>
                  </tr>
                )) : (
                  <tr><td className="p-3 text-neutral-500" colSpan={6}>No assessments match the current filters.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}
        {success ? <div className="rounded-lg bg-brand-50 p-3 text-sm font-semibold text-brand-800">{success}</div> : null}
      </div>
    </PortalShell>
  );
}
