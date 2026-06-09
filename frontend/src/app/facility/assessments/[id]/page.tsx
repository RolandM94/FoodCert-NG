"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AlertCircle, ArrowLeft, ClipboardCheck, FlaskConical, ShieldCheck, Syringe } from "lucide-react";
import { AssessmentAuditTimeline } from "@/components/assessments/assessment-audit-timeline";
import { AssessmentReportsPanel } from "@/components/assessments/assessment-reports-panel";
import { SubmitToStatePanel } from "@/components/assessments/submit-to-state-panel";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { getAssessmentAuditTimeline, getFacilityAssessment } from "@/lib/api/assessments";
import { respondFacilityCertificateClarification, submitFacilityAssessmentToState } from "@/lib/api/certificates";
import { getCurrentMedicalFacility } from "@/lib/api/facilities";
import { getAssessmentReport, type AssessmentReportKind } from "@/lib/api/reports";
import type { AssessmentAuditTimelineItem, MedicalAssessment } from "@/types/assessments";
import type { MedicalFacility } from "@/types/facilities";
import type { GeneratedReport } from "@/types/reports";

function label(value?: string) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

function formatDate(value?: string) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function Page() {
  const params = useParams<{ id: string }>();
  const [facility, setFacility] = useState<MedicalFacility | null>(null);
  const [assessment, setAssessment] = useState<MedicalAssessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [submissionNotes, setSubmissionNotes] = useState("");
  const [clarificationResponse, setClarificationResponse] = useState("");
  const [report, setReport] = useState<GeneratedReport | null>(null);
  const [timeline, setTimeline] = useState<AssessmentAuditTimelineItem[]>([]);

  const loadData = useCallback(async () => {
    if (!params.id) return;
    setLoading(true);
    setError("");
    try {
      const profile = await getCurrentMedicalFacility();
      const [row, timelineRows] = await Promise.all([
        getFacilityAssessment(profile.id, params.id),
        getAssessmentAuditTimeline(params.id),
      ]);
      setFacility(profile);
      setAssessment(row);
      setTimeline(timelineRows);
    } catch {
      setError("Could not load assessment detail.");
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  async function submitToState() {
    if (!facility || !assessment) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await submitFacilityAssessmentToState(facility.id, assessment.id, submissionNotes);
      setSubmissionNotes("");
      setSuccess("Assessment submitted to State validation.");
      await loadData();
    } catch {
      setError("Could not submit to State. Confirm the assessment is fit, signed, paid, and fully reviewed.");
    } finally {
      setBusy(false);
    }
  }

  async function respondToClarification() {
    if (!facility || !assessment || !clarificationResponse.trim()) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await respondFacilityCertificateClarification(facility.id, assessment.id, clarificationResponse);
      setClarificationResponse("");
      setSuccess("Clarification response sent back to State validation.");
      await loadData();
    } catch {
      setError("Could not send clarification response.");
    } finally {
      setBusy(false);
    }
  }

  async function loadReport(kind: AssessmentReportKind) {
    if (!assessment) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      setReport(await getAssessmentReport(assessment.id, kind));
      setSuccess("Assessment report generated.");
    } catch {
      setError("Could not generate this report for your role.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <PortalShell role="facility_admin" title="Assessment Detail" description="Review workflow status, task panels, and state submission readiness.">
      <div className="grid gap-5">
        <Link className="inline-flex w-fit items-center gap-2 rounded border border-neutral-200 bg-white px-3 py-2 text-sm font-bold text-neutral-700 shadow-sm" href="/facility/assessments">
          <ArrowLeft size={16} /> Back to queue
        </Link>

        {loading ? <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading assessment...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}
        {success ? <div className="rounded-lg bg-brand-50 p-3 text-sm font-semibold text-brand-800">{success}</div> : null}

        {assessment ? (
          <>
            <section className="grid gap-3 md:grid-cols-4">
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-neutral-500">Food handler</p><p className="mt-2 font-bold text-neutral-900">{assessment.food_handler_name}</p><p className="text-xs text-neutral-500">{assessment.food_handler_identifier}</p></div>
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-neutral-500">Employer</p><p className="mt-2 font-bold text-neutral-900">{assessment.employer_name || "Individual"}</p><p className="text-xs text-neutral-500">{assessment.branch_name || "No branch"}</p></div>
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-neutral-500">Appointment</p><p className="mt-2 font-bold text-neutral-900">{formatDate(assessment.appointment_date)}</p><StatusBadge status={assessment.appointment_status || "not_booked"} /></div>
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-neutral-500">Payment</p><p className="mt-2 font-bold text-neutral-900">{label(assessment.payment_status)}</p><StatusBadge status={assessment.payment_status || "missing"} /></div>
            </section>

            <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <h2 className="text-sm font-bold text-neutral-900">Workflow Stepper</h2>
              <div className="mt-4 grid gap-3 md:grid-cols-5">
                {[
                  ["Declaration", assessment.declaration_status, ClipboardCheck],
                  ["Physical exam", assessment.physical_exam_status, ShieldCheck],
                  ["Lab", assessment.lab_status, FlaskConical],
                  ["Vaccination", assessment.vaccination_status, Syringe],
                  ["Decision", assessment.final_decision, ClipboardCheck],
                ].map(([title, status, Icon]) => {
                  const StepIcon = Icon as typeof ClipboardCheck;
                  return (
                    <div className="rounded border border-neutral-200 bg-neutral-50 p-3" key={title as string}>
                      <StepIcon className="text-brand-700" size={18} />
                      <p className="mt-2 text-xs font-bold uppercase text-neutral-500">{title as string}</p>
                      <p className="text-sm font-bold capitalize text-neutral-900">{label(status as string)}</p>
                    </div>
                  );
                })}
              </div>
            </section>

            <section className="grid gap-4 lg:grid-cols-2">
              <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                <h2 className="text-sm font-bold text-neutral-900">Declaration</h2>
                {assessment.health_declaration ? (
                  <div className="mt-3 text-sm text-neutral-700">
                    <p>Risk flag: <span className="font-bold">{assessment.health_declaration.risk_flag ? "Yes" : "No"}</span></p>
                    <p>Submitted: {formatDate(assessment.health_declaration.submitted_at)}</p>
                    <p>Validated: {formatDate(assessment.health_declaration.validated_at)}</p>
                  </div>
                ) : <p className="mt-3 text-sm text-neutral-500">Declaration details are unavailable for this role or not submitted yet.</p>}
              </div>

              <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                <h2 className="text-sm font-bold text-neutral-900">Physical Examination</h2>
                {assessment.physical_examination ? (
                  <div className="mt-3 text-sm text-neutral-700">
                    <p>Examined by: {assessment.physical_examination.examined_by_name || "Not set"}</p>
                    <p>Examined at: {formatDate(assessment.physical_examination.examined_at)}</p>
                    <p>Notes: {assessment.physical_examination.other_notes || "No notes"}</p>
                  </div>
                ) : <p className="mt-3 text-sm text-neutral-500">No physical examination recorded.</p>}
              </div>

              <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                <h2 className="text-sm font-bold text-neutral-900">Lab Tests</h2>
                <div className="mt-3 grid gap-2">
                  {assessment.lab_tests?.length ? assessment.lab_tests.map((test) => (
                    <div className="rounded border border-neutral-100 bg-neutral-50 p-3" key={test.id}>
                      <p className="font-bold text-neutral-900">{test.test_name || label(test.test_type)}</p>
                      <StatusBadge status={test.status} />
                    </div>
                  )) : <p className="text-sm text-neutral-500">No lab tests recorded or visible.</p>}
                </div>
              </div>

              <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                <h2 className="text-sm font-bold text-neutral-900">Vaccination And State Submission</h2>
                <div className="mt-3 grid gap-2 text-sm text-neutral-700">
                  <p>Vaccination records: <span className="font-bold">{assessment.vaccinations?.length || 0}</span></p>
                  <p>Certificate submission: <span className="font-bold capitalize">{label(assessment.certificate_submission_status)}</span></p>
                  <p>Can request certificate: <span className="font-bold">{assessment.can_request_certificate ? "Yes" : "No"}</span></p>
                  <p>Facility: <span className="font-bold">{facility?.facility_name || assessment.facility_name}</span></p>
                </div>
              </div>

              <SubmitToStatePanel
                assessment={assessment}
                busy={busy}
                submissionNotes={submissionNotes}
                clarificationResponse={clarificationResponse}
                onSubmissionNotesChange={setSubmissionNotes}
                onClarificationResponseChange={setClarificationResponse}
                onSubmitToState={() => void submitToState()}
                onRespondToClarification={() => void respondToClarification()}
              />

              <div className="lg:col-span-2">
                <AssessmentReportsPanel
                  report={report}
                  busy={busy}
                  actions={[
                    { kind: "summary", label: "Summary" },
                    { kind: "return-to-work", label: "Return to work" },
                  ]}
                  onGenerate={(kind) => void loadReport(kind)}
                />
              </div>

              <div className="lg:col-span-2">
                <AssessmentAuditTimeline items={timeline} loading={loading} />
              </div>
            </section>
          </>
        ) : null}
      </div>
    </PortalShell>
  );
}
