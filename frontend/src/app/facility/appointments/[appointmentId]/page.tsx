"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  AlertCircle,
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  ClipboardList,
  FlaskConical,
  ShieldAlert,
  Stethoscope,
  UserRoundCheck,
} from "lucide-react";

import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import {
  checkInFacilityAssessment,
  flagFacilityAssessmentIdentityMismatch,
  getFacilityAppointment,
  getFacilityAssessment,
} from "@/lib/api/assessments";
import { getCurrentMedicalFacility } from "@/lib/api/facilities";
import type { Appointment, MedicalAssessment } from "@/types/assessments";
import type { MedicalFacility } from "@/types/facilities";

function formatDate(value?: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function formatDateOnly(value?: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium" }).format(new Date(value));
}

function label(value?: string | null) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

export default function Page() {
  const params = useParams<{ appointmentId: string }>();
  const [facility, setFacility] = useState<MedicalFacility | null>(null);
  const [appointment, setAppointment] = useState<Appointment | null>(null);
  const [assessment, setAssessment] = useState<MedicalAssessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [checkInNotes, setCheckInNotes] = useState("");
  const [mismatchReason, setMismatchReason] = useState("");

  useEffect(() => {
    async function loadData() {
      if (!params.appointmentId) return;
      setLoading(true);
      setError("");
      try {
        const profile = await getCurrentMedicalFacility();
        const appointmentRow = await getFacilityAppointment(profile.id, params.appointmentId);
        const assessmentRow = appointmentRow.assessment_id
          ? await getFacilityAssessment(profile.id, appointmentRow.assessment_id)
          : null;
        setFacility(profile);
        setAppointment(appointmentRow);
        setAssessment(assessmentRow);
      } catch {
        setError("Could not load appointment detail.");
      } finally {
        setLoading(false);
      }
    }

    void loadData();
  }, [params.appointmentId]);

  async function reloadAssessment() {
    if (!facility || !appointment) return;
    const appointmentRow = await getFacilityAppointment(facility.id, appointment.id);
    const assessmentRow = appointmentRow.assessment_id
      ? await getFacilityAssessment(facility.id, appointmentRow.assessment_id)
      : null;
    setAppointment(appointmentRow);
    setAssessment(assessmentRow);
  }

  async function handleCheckIn() {
    if (!facility || !appointment?.assessment_id) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await checkInFacilityAssessment(facility.id, appointment.assessment_id, { notes: checkInNotes });
      setCheckInNotes("");
      await reloadAssessment();
      setSuccess("Food handler identity verified and assessment checked in.");
    } catch {
      setError("Could not complete check-in. Confirm the assessment is linked to this appointment and your facility role has the required permissions.");
    } finally {
      setBusy(false);
    }
  }

  async function handleMismatch() {
    if (!facility || !appointment?.assessment_id || !mismatchReason.trim()) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await flagFacilityAssessmentIdentityMismatch(facility.id, appointment.assessment_id, { reason: mismatchReason });
      setMismatchReason("");
      await reloadAssessment();
      setSuccess("Identity mismatch flagged. Clinical processing is now paused for this assessment.");
    } catch {
      setError("Could not flag identity mismatch.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <PortalShell
      role="facility_admin"
      title="Appointment Detail"
      description="Track booking readiness, verify identity at arrival, and move the handler safely into the assessment workflow."
    >
      <div className="grid gap-5">
        <Link
          className="inline-flex w-fit items-center gap-2 rounded border border-neutral-200 bg-white px-3 py-2 text-sm font-bold text-neutral-700 shadow-sm"
          href="/facility/appointments"
        >
          <ArrowLeft size={16} /> Back to appointments
        </Link>

        {loading ? (
          <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">
            Loading appointment...
          </p>
        ) : null}

        {error ? (
          <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700">
            <AlertCircle size={16} />
            {error}
          </div>
        ) : null}

        {success ? <div className="rounded-lg bg-brand-50 p-3 text-sm font-semibold text-brand-800">{success}</div> : null}

        {appointment ? (
          <>
            <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
                <p className="text-xs font-bold uppercase text-neutral-500">Appointment ID</p>
                <p className="mt-2 font-mono text-sm font-bold text-neutral-900">{appointment.id}</p>
                <p className="mt-2 text-xs text-neutral-500">Facility: {facility?.facility_name || appointment.facility_name}</p>
              </div>
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
                <p className="text-xs font-bold uppercase text-neutral-500">Food Handler</p>
                <p className="mt-2 font-bold text-neutral-900">{appointment.food_handler_name}</p>
                <p className="text-xs text-neutral-500">{appointment.employer_name || "Individual applicant"}</p>
              </div>
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
                <p className="text-xs font-bold uppercase text-neutral-500">Appointment Time</p>
                <p className="mt-2 font-bold text-neutral-900">{formatDate(appointment.appointment_date)}</p>
                <StatusBadge status={appointment.status} />
              </div>
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
                <p className="text-xs font-bold uppercase text-neutral-500">Payment</p>
                <p className="mt-2 font-bold text-neutral-900 capitalize">{label(appointment.payment_status)}</p>
                <StatusBadge status={appointment.payment_status || "missing"} />
              </div>
            </section>

            <section className="grid gap-4 xl:grid-cols-[1.25fr_0.85fr_0.9fr_0.9fr]">
              <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                <div className="flex items-center gap-2 text-neutral-900">
                  <UserRoundCheck className="text-brand-700" size={18} />
                  <h2 className="text-sm font-bold">Identity Verification</h2>
                </div>
                <div className="mt-4 grid gap-3 text-sm text-neutral-700">
                  <div className="grid gap-1">
                    <span className="text-xs font-bold uppercase text-neutral-500">Name</span>
                    <span className="font-semibold text-neutral-900">{appointment.food_handler_name}</span>
                  </div>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div className="grid gap-1">
                      <span className="text-xs font-bold uppercase text-neutral-500">NIN</span>
                      <span className="font-semibold text-neutral-900">{appointment.food_handler_nin || "Not available"}</span>
                    </div>
                    <div className="grid gap-1">
                      <span className="text-xs font-bold uppercase text-neutral-500">Date of birth</span>
                      <span className="font-semibold text-neutral-900">{formatDateOnly(appointment.food_handler_date_of_birth)}</span>
                    </div>
                  </div>
                  <div className="grid gap-1">
                    <span className="text-xs font-bold uppercase text-neutral-500">Employer</span>
                    <span className="font-semibold text-neutral-900">{appointment.employer_name || "Individual applicant"}</span>
                  </div>
                  <div className="grid gap-1">
                    <span className="text-xs font-bold uppercase text-neutral-500">Identity status</span>
                    <div className="flex flex-wrap items-center gap-2">
                      <StatusBadge status={appointment.identity_verification_status || "pending"} />
                      {appointment.identity_verified_by_name ? (
                        <span className="text-xs text-neutral-500">Verified by {appointment.identity_verified_by_name}</span>
                      ) : null}
                    </div>
                  </div>
                  {appointment.food_handler_passport_photo ? (
                    <img
                      alt={`${appointment.food_handler_name} passport`}
                      className="h-24 w-24 rounded-lg border border-neutral-200 object-cover"
                      src={appointment.food_handler_passport_photo}
                    />
                  ) : (
                    <div className="rounded-lg border border-dashed border-neutral-200 px-3 py-6 text-xs text-neutral-500">
                      No passport photo uploaded.
                    </div>
                  )}
                </div>
              </div>

              <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                <div className="flex items-center gap-2 text-neutral-900">
                  <ClipboardList className="text-brand-700" size={18} />
                  <h2 className="text-sm font-bold">Declaration Readiness</h2>
                </div>
                <div className="mt-4 space-y-3 text-sm text-neutral-700">
                  <div className="flex items-center justify-between gap-3">
                    <span>Status</span>
                    <StatusBadge status={appointment.declaration_status || "pending"} />
                  </div>
                  <p className="text-neutral-500">
                    The appointment can proceed once the declaration has been completed and reviewed where required.
                  </p>
                </div>
              </div>

              <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                <div className="flex items-center gap-2 text-neutral-900">
                  <CheckCircle2 className="text-brand-700" size={18} />
                  <h2 className="text-sm font-bold">Check-In Control</h2>
                </div>
                <div className="mt-4 grid gap-3 text-sm text-neutral-700">
                  <div className="flex items-center justify-between gap-3">
                    <span>Checked in</span>
                    <span className="font-semibold text-neutral-900">{appointment.checked_in_at ? formatDate(appointment.checked_in_at) : "Not yet"}</span>
                  </div>
                  {appointment.checked_in_by_name ? (
                    <p className="text-xs text-neutral-500">Recorded by {appointment.checked_in_by_name}</p>
                  ) : null}
                  <textarea
                    className="min-h-[88px] rounded-lg border border-neutral-200 px-3 py-2 text-sm outline-none transition focus:border-brand-300"
                    placeholder="Optional check-in note"
                    value={checkInNotes}
                    onChange={(event) => setCheckInNotes(event.target.value)}
                  />
                  <button
                    className="inline-flex h-10 items-center justify-center rounded bg-brand-700 px-4 text-sm font-bold text-white disabled:opacity-60"
                    disabled={busy || !appointment.assessment_id}
                    type="button"
                    onClick={() => void handleCheckIn()}
                  >
                    Verify Identity And Check In
                  </button>
                </div>
              </div>

              <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                <div className="flex items-center gap-2 text-neutral-900">
                  <ShieldAlert className="text-brand-700" size={18} />
                  <h2 className="text-sm font-bold">Mismatch Escalation</h2>
                </div>
                <div className="mt-4 space-y-3 text-sm text-neutral-700">
                  <p className="text-neutral-500">
                    Flag a mismatch when the presented NIN, date of birth, or passport photo does not match the handler record.
                  </p>
                  <textarea
                    className="min-h-[96px] rounded-lg border border-neutral-200 px-3 py-2 text-sm outline-none transition focus:border-brand-300"
                    placeholder="Reason for mismatch"
                    value={mismatchReason}
                    onChange={(event) => setMismatchReason(event.target.value)}
                  />
                  <button
                    className="inline-flex h-10 items-center justify-center rounded border border-danger-200 bg-danger-50 px-4 text-sm font-bold text-danger-700 disabled:opacity-60"
                    disabled={busy || !appointment.assessment_id || !mismatchReason.trim()}
                    type="button"
                    onClick={() => void handleMismatch()}
                  >
                    Flag Identity Mismatch
                  </button>
                  {appointment.identity_mismatch_reason ? (
                    <div className="rounded-lg border border-danger-100 bg-danger-50 p-3 text-xs text-danger-700">
                      {appointment.identity_mismatch_reason}
                    </div>
                  ) : null}
                </div>
              </div>
            </section>

            <section className="grid gap-4 lg:grid-cols-2">
              <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                <div className="flex items-center gap-2 text-neutral-900">
                  <Stethoscope className="text-brand-700" size={18} />
                  <h2 className="text-sm font-bold">Clinical Assignment</h2>
                </div>
                <div className="mt-4 space-y-3 text-sm text-neutral-700">
                  <div className="flex items-center justify-between gap-3">
                    <span>Assigned doctor</span>
                    <span className="font-semibold text-neutral-900">{appointment.doctor_name || "Not assigned yet"}</span>
                  </div>
                  <div className="flex items-center justify-between gap-3">
                    <span>Assigned lab technician</span>
                    <span className="font-semibold text-neutral-900">Not assigned yet</span>
                  </div>
                </div>
              </div>

              <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                <div className="flex items-center gap-2 text-neutral-900">
                  <CalendarDays className="text-brand-700" size={18} />
                  <h2 className="text-sm font-bold">Assessment Link</h2>
                </div>
                <div className="mt-4 space-y-3 text-sm text-neutral-700">
                  <div className="flex items-center justify-between gap-3">
                    <span>Assessment status</span>
                    <StatusBadge status={appointment.assessment_status || "pending"} />
                  </div>
                  {appointment.assessment_id ? (
                    <Link
                      className="inline-flex items-center rounded border border-neutral-200 px-3 py-2 text-sm font-bold text-neutral-700"
                      href={`/facility/assessments/${appointment.assessment_id}`}
                    >
                      Open linked assessment
                    </Link>
                  ) : (
                    <p className="text-neutral-500">No assessment record has been linked to this appointment yet.</p>
                  )}
                </div>
              </div>
            </section>

            {assessment ? (
              <section className="grid gap-4 lg:grid-cols-2">
                <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                  <h2 className="text-sm font-bold text-neutral-900">Assessment Summary</h2>
                  <div className="mt-4 grid gap-3 text-sm text-neutral-700">
                    <div className="flex items-center justify-between gap-3">
                      <span>Assessment ID</span>
                      <span className="font-mono text-xs font-semibold text-neutral-900">{assessment.id}</span>
                    </div>
                    <div className="flex items-center justify-between gap-3">
                      <span>Workflow status</span>
                      <StatusBadge status={assessment.status} />
                    </div>
                    <div className="flex items-center justify-between gap-3">
                      <span>Declaration</span>
                      <StatusBadge status={assessment.declaration_status} />
                    </div>
                    <div className="flex items-center justify-between gap-3">
                      <span>Physical exam</span>
                      <StatusBadge status={assessment.physical_exam_status} />
                    </div>
                    <div className="flex items-center justify-between gap-3">
                      <span>Lab workflow</span>
                      <StatusBadge status={assessment.lab_status} />
                    </div>
                    <div className="flex items-center justify-between gap-3">
                      <span>Final decision</span>
                      <StatusBadge status={assessment.final_decision} />
                    </div>
                  </div>
                </div>

                <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                  <div className="flex items-center gap-2 text-neutral-900">
                    <FlaskConical className="text-brand-700" size={18} />
                    <h2 className="text-sm font-bold">Lab Progress</h2>
                  </div>
                  <div className="mt-4 grid gap-2">
                    {assessment.lab_tests?.length ? (
                      assessment.lab_tests.map((test) => (
                        <div className="flex items-center justify-between gap-3 rounded border border-neutral-100 bg-neutral-50 px-3 py-2" key={test.id}>
                          <div>
                            <p className="text-sm font-semibold text-neutral-900">{test.test_name || label(test.test_type)}</p>
                            <p className="text-xs text-neutral-500">{test.result_value || "Awaiting result"}</p>
                          </div>
                          <StatusBadge status={test.status} />
                        </div>
                      ))
                    ) : (
                      <p className="text-sm text-neutral-500">No lab tests have been attached yet.</p>
                    )}
                  </div>
                </div>
              </section>
            ) : null}
          </>
        ) : null}
      </div>
    </PortalShell>
  );
}
