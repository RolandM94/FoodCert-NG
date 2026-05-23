"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AlertCircle, ArrowLeft, ClipboardCheck, FileCheck2, FlaskConical, Save, Send, ShieldAlert, Stethoscope, Syringe } from "lucide-react";
import { LabTestRequestForm, type LabTestRequestItem } from "@/components/assessments/lab-test-request-form";
import { LabResultReviewPanel } from "@/components/assessments/lab-result-review-panel";
import { AssessmentReportsPanel } from "@/components/assessments/assessment-reports-panel";
import { AssessmentAuditTimeline } from "@/components/assessments/assessment-audit-timeline";
import { PhysicalExamForm, EMPTY_PHYSICAL_EXAM_FORM, type PhysicalExamFormValue } from "@/components/assessments/physical-exam-form";
import { VaccinationReviewPanel, type VaccinationReviewValue } from "@/components/assessments/vaccination-review-panel";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import {
  getDoctorAssessment,
  getAssessmentAuditTimeline,
  requestDoctorDeclarationChanges,
  requestLabTests,
  saveDoctorFitnessDecisionDraft,
  saveDoctorPhysicalExamDraft,
  setDoctorFitnessDecision,
  submitDoctorPhysicalExam,
  validateDoctorDeclaration,
} from "@/lib/api/assessments";
import { reviewDoctorVaccination } from "@/lib/api/vaccinations";
import { requestRepeatLabTest, reviewLabRequest } from "@/lib/api/lab-tests";
import { getAssessmentReport, type AssessmentReportKind } from "@/lib/api/reports";
import type { AssessmentAuditTimelineItem, FitnessDecision, MedicalAssessment } from "@/types/assessments";
import type { GeneratedReport } from "@/types/reports";

const DECISION_OPTIONS: Array<{ value: FitnessDecision; label: string }> = [
  { value: "fit", label: "Fit for food handling" },
  { value: "temporarily_not_fit", label: "Temporarily not fit" },
  { value: "not_fit", label: "Not fit" },
  { value: "requires_vaccination", label: "Requires vaccination" },
  { value: "requires_lab_test", label: "Requires lab test" },
  { value: "requires_recheck", label: "Requires recheck" },
  { value: "requires_treatment", label: "Requires treatment" },
  { value: "requires_public_health_clearance", label: "Requires public health clearance" },
  { value: "return_to_work_on_date", label: "Return to work on date" },
];

function formatDate(value?: string) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function Page() {
  const params = useParams<{ id: string }>();
  const [assessment, setAssessment] = useState<MedicalAssessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [clarificationReason, setClarificationReason] = useState("");
  const [vaccination, setVaccination] = useState<VaccinationReviewValue>({
    vaccine_type: "typhoid",
    action: "mark_valid",
    status: "valid",
    vaccine_name: "",
    brand_name: "",
    batch_number: "",
    vaccinator_name: "",
    vaccination_facility_name: "",
    vaccination_facility_address: "",
    dose_number: "1",
    date_administered: "",
    expiry_date: "",
    reminder_date: "",
    notes: "",
  });
  const [exam, setExam] = useState<PhysicalExamFormValue>(EMPTY_PHYSICAL_EXAM_FORM);
  const [includeRequiredLabTests, setIncludeRequiredLabTests] = useState(true);
  const [additionalLabTests, setAdditionalLabTests] = useState<LabTestRequestItem[]>([]);
  const [repeatReasons, setRepeatReasons] = useState<Record<string, string>>({});
  const [labReviewNotes, setLabReviewNotes] = useState<Record<string, { doctor_review_notes: string; doctor_recommendation: string }>>({});
  const [report, setReport] = useState<GeneratedReport | null>(null);
  const [timeline, setTimeline] = useState<AssessmentAuditTimelineItem[]>([]);
  const [decision, setDecision] = useState({
    final_decision: "fit" as FitnessDecision,
    return_to_work_date: "",
    doctor_notes: "",
    digital_signature_confirmation: false,
  });

  const loadData = useCallback(async () => {
    if (!params.id) return;
    setLoading(true);
    setError("");
    try {
      const row = await getDoctorAssessment(params.id);
      const timelineRows = await getAssessmentAuditTimeline(params.id);
      setAssessment(row);
      setTimeline(timelineRows);
      if (row.physical_examination) {
        setExam({
          fever: row.physical_examination.fever,
          jaundice: row.physical_examination.jaundice,
          skin_infection: row.physical_examination.skin_infection,
          boils_styes_sepsis: row.physical_examination.boils_styes_sepsis,
          discharge: row.physical_examination.discharge,
          diarrhoea: row.physical_examination.diarrhoea,
          vomiting: row.physical_examination.vomiting,
          sore_throat_with_fever: row.physical_examination.sore_throat_with_fever,
          cough_or_flu: row.physical_examination.cough_or_flu,
          known_typhoid_carrier_history: row.physical_examination.known_typhoid_carrier_history,
          other_notes: row.physical_examination.other_notes,
        });
      }
      setDecision({
        final_decision: row.final_decision === "pending" ? (row.decision_draft && row.decision_draft !== "pending" ? row.decision_draft : "fit") : row.final_decision,
        return_to_work_date: row.return_to_work_date || row.decision_draft_return_to_work_date || "",
        doctor_notes: row.doctor_notes || row.decision_draft_notes || "",
        digital_signature_confirmation: Boolean(row.signed_at),
      });
    } catch {
      setError("Could not load assigned assessment.");
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  async function validateDeclaration() {
    if (!assessment) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await validateDoctorDeclaration(assessment.id);
      setSuccess("Declaration validated.");
      await loadData();
    } catch {
      setError("Could not validate declaration. It may already be locked or not assigned to you.");
    } finally {
      setBusy(false);
    }
  }

  async function requestChanges() {
    if (!assessment || !clarificationReason.trim()) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await requestDoctorDeclarationChanges(assessment.id, clarificationReason);
      setClarificationReason("");
      setSuccess("Declaration changes requested.");
      await loadData();
    } catch {
      setError("Could not request declaration changes.");
    } finally {
      setBusy(false);
    }
  }

  async function saveExam() {
    if (!assessment) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await saveDoctorPhysicalExamDraft(assessment.id, exam);
      setSuccess("Physical examination draft saved.");
      await loadData();
    } catch {
      setError("Could not save physical examination draft.");
    } finally {
      setBusy(false);
    }
  }

  async function completeExam() {
    if (!assessment) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await submitDoctorPhysicalExam(assessment.id, exam);
      setSuccess("Physical examination completed.");
      await loadData();
    } catch {
      setError("Could not complete physical examination.");
    } finally {
      setBusy(false);
    }
  }

  async function saveVaccinationReview() {
    if (!assessment) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await reviewDoctorVaccination(assessment.id, {
        ...vaccination,
        dose_number: Number(vaccination.dose_number || 1),
        date_administered: vaccination.date_administered || null,
        expiry_date: vaccination.expiry_date || null,
        reminder_date: vaccination.reminder_date || null,
        doctor_clearance: vaccination.status === "doctor_cleared" || vaccination.action === "mark_valid",
      });
      setSuccess("Vaccination review saved.");
      await loadData();
    } catch {
      setError("Could not save vaccination review.");
    } finally {
      setBusy(false);
    }
  }

  async function requestAssessmentLabTests() {
    if (!assessment) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await requestLabTests(assessment.id, additionalLabTests, includeRequiredLabTests);
      setAdditionalLabTests([]);
      setIncludeRequiredLabTests(true);
      setSuccess("Lab tests requested.");
      await loadData();
    } catch {
      setError("Could not request lab tests.");
    } finally {
      setBusy(false);
    }
  }

  async function requestRepeat(labTestId: string) {
    const reason = repeatReasons[labTestId]?.trim();
    if (!reason) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await requestRepeatLabTest(labTestId, { reason });
      setRepeatReasons((current) => ({ ...current, [labTestId]: "" }));
      setSuccess("Repeat lab test requested.");
      await loadData();
    } catch {
      setError("Could not request repeat lab test.");
    } finally {
      setBusy(false);
    }
  }

  async function reviewLabResult(labTestId: string) {
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await reviewLabRequest(labTestId, labReviewNotes[labTestId] || {});
      setSuccess("Lab result reviewed.");
      await loadData();
    } catch {
      setError("Could not review lab result.");
    } finally {
      setBusy(false);
    }
  }

  async function submitDecision() {
    if (!assessment) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await setDoctorFitnessDecision(assessment.id, {
        final_decision: decision.final_decision,
        return_to_work_date: decision.return_to_work_date || undefined,
        doctor_notes: decision.doctor_notes,
        digital_signature_confirmation: decision.digital_signature_confirmation,
      });
      setSuccess("Final decision signed and medical report generated.");
      await loadData();
    } catch {
      setError("Could not sign final decision. Check readiness, illness clearance, and digital confirmation.");
    } finally {
      setBusy(false);
    }
  }

  async function saveDecisionDraft() {
    if (!assessment) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await saveDoctorFitnessDecisionDraft(assessment.id, {
        final_decision: decision.final_decision,
        return_to_work_date: decision.return_to_work_date || undefined,
        doctor_notes: decision.doctor_notes,
      });
      setSuccess("Decision draft saved.");
      await loadData();
    } catch {
      setError("Could not save decision draft.");
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
      setError("Could not generate this assessment report for your role.");
    } finally {
      setBusy(false);
    }
  }

  const readinessItems = assessment ? [
    { label: "Payment confirmed", ready: assessment.payment_status === "success" || assessment.payment_status === "paid" || assessment.payment_status === "completed" },
    { label: "Declaration validated", ready: assessment.declaration_status === "validated" },
    { label: "Physical exam completed", ready: assessment.physical_exam_status === "completed" },
    { label: "Lab reviewed", ready: assessment.lab_status === "reviewed" },
    { label: "Vaccination reviewed", ready: assessment.vaccination_status === "reviewed" },
  ] : [];

  return (
    <PortalShell role="doctor" title="Assessment Review" description="Validate health declaration risk, complete physical examination, and prepare next workflow steps.">
      <div className="grid gap-5">
        <Link className="inline-flex w-fit items-center gap-2 rounded border border-slate-200 bg-white px-3 py-2 text-sm font-bold text-slate-700 shadow-sm" href="/doctor/assessments">
          <ArrowLeft size={16} /> Back to assigned cases
        </Link>

        {loading ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading assessment...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} />{error}</div> : null}
        {success ? <div className="rounded-lg bg-emerald-50 p-3 text-sm font-semibold text-emerald-800">{success}</div> : null}

        {assessment ? (
          <>
            <section className="grid gap-3 md:grid-cols-4">
              <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-slate-500">Food handler</p><p className="mt-2 font-bold text-slate-950">{assessment.food_handler_name}</p><p className="text-xs text-slate-500">{assessment.food_handler_identifier}</p></div>
              <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-slate-500">Declaration</p><StatusBadge status={assessment.declaration_status} /></div>
              <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-slate-500">Physical exam</p><StatusBadge status={assessment.physical_exam_status} /></div>
              <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-slate-500">Payment</p><StatusBadge status={assessment.payment_status || "missing"} /></div>
            </section>

            <section className="grid gap-4 lg:grid-cols-2">
              <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                <div className="mb-4 flex items-center gap-2">
                  <ShieldAlert className="text-brand-deep" size={18} />
                  <h2 className="text-sm font-bold text-slate-950">Declaration Review</h2>
                </div>
                {assessment.health_declaration ? (
                  <div className="grid gap-3">
                    <div className={`rounded border p-3 text-sm font-bold ${assessment.health_declaration.risk_flag ? "border-amber-200 bg-amber-50 text-amber-900" : "border-emerald-200 bg-emerald-50 text-emerald-900"}`}>
                      Risk flag: {assessment.health_declaration.risk_flag ? "Yes" : "No"}
                    </div>
                    <div className="grid gap-2 rounded border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700 sm:grid-cols-2">
                      <p>Version: <span className="font-bold">{assessment.health_declaration.version}</span></p>
                      <p>Lock state: <span className="font-bold">{assessment.health_declaration.is_locked ? "Locked" : "Editable when reopened"}</span></p>
                    </div>
                    <p className="text-sm text-slate-600">Submitted: {formatDate(assessment.health_declaration.submitted_at)}</p>
                    <p className="text-sm text-slate-600">Validated: {formatDate(assessment.health_declaration.validated_at)}</p>
                    {assessment.health_declaration.reopen_reason ? <p className="rounded bg-amber-50 p-3 text-sm text-amber-900">Reopened: {assessment.health_declaration.reopen_reason}</p> : null}
                    {assessment.health_declaration.clarification_reason ? <p className="rounded bg-slate-50 p-3 text-sm text-slate-700">Clarification: {assessment.health_declaration.clarification_reason}</p> : null}
                    <textarea className="min-h-24 rounded border border-slate-200 bg-slate-50 p-3 text-sm" placeholder="Reason for requesting changes" value={clarificationReason} onChange={(event) => setClarificationReason(event.target.value)} />
                    <div className="flex flex-wrap gap-2">
                      <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white disabled:opacity-60" disabled={busy || Boolean(assessment.health_declaration.validated_at)} type="button" onClick={() => void validateDeclaration()}><ClipboardCheck size={16} /> Validate</button>
                      <button className="inline-flex h-10 items-center gap-2 rounded border border-slate-200 px-4 text-sm font-bold text-slate-700 disabled:opacity-60" disabled={busy || Boolean(assessment.health_declaration.validated_at) || !clarificationReason.trim()} type="button" onClick={() => void requestChanges()}><Send size={16} /> Request changes</button>
                    </div>
                  </div>
                ) : <p className="text-sm text-slate-500">No declaration submitted yet.</p>}
              </div>

              <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                <div className="mb-4 flex items-center gap-2">
                  <Stethoscope className="text-brand-deep" size={18} />
                  <h2 className="text-sm font-bold text-slate-950">Physical Examination</h2>
                </div>
                <PhysicalExamForm
                  value={exam}
                  busy={busy}
                  completed={assessment.physical_examination?.is_completed}
                  onChange={setExam}
                  onSaveDraft={() => void saveExam()}
                  onComplete={() => void completeExam()}
                />
              </div>

              <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm lg:col-span-2">
                <div className="mb-4 flex items-center gap-2">
                  <FlaskConical className="text-brand-deep" size={18} />
                  <h2 className="text-sm font-bold text-slate-950">Lab Requests</h2>
                </div>
                <div className="grid gap-4 lg:grid-cols-2">
                  <LabResultReviewPanel
                    tests={assessment.lab_tests}
                    busy={busy}
                    reviewNotes={labReviewNotes}
                    repeatReasons={repeatReasons}
                    onReviewNotesChange={(testId, value) => setLabReviewNotes((current) => ({ ...current, [testId]: value }))}
                    onRepeatReasonChange={(testId, reason) => setRepeatReasons((current) => ({ ...current, [testId]: reason }))}
                    onReview={(testId) => void reviewLabResult(testId)}
                    onRepeat={(testId) => void requestRepeat(testId)}
                  />
                  <LabTestRequestForm
                    additionalTests={additionalLabTests}
                    includeRequired={includeRequiredLabTests}
                    busy={busy}
                    onAdditionalTestsChange={setAdditionalLabTests}
                    onIncludeRequiredChange={setIncludeRequiredLabTests}
                    onSubmit={() => void requestAssessmentLabTests()}
                  />
                </div>
              </div>

              <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm lg:col-span-2">
                <div className="mb-4 flex items-center gap-2">
                  <Syringe className="text-brand-deep" size={18} />
                  <h2 className="text-sm font-bold text-slate-950">Vaccination Review</h2>
                </div>
                <VaccinationReviewPanel records={assessment.vaccinations} value={vaccination} busy={busy} onChange={setVaccination} onSubmit={() => void saveVaccinationReview()} />
              </div>

              <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm lg:col-span-2">
                <div className="mb-4 flex items-center gap-2">
                  <FileCheck2 className="text-brand-deep" size={18} />
                  <h2 className="text-sm font-bold text-slate-950">Final Decision & Medical Report</h2>
                </div>
                <div className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
                  <div className="grid gap-2">
                    {readinessItems.map((item) => (
                      <div className="flex items-center justify-between gap-3 rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-700" key={item.label}>
                        <span>{item.label}</span>
                        <StatusBadge status={item.ready ? "ready" : "pending"} />
                      </div>
                    ))}
                    {assessment.signed_at ? (
                      <div className="rounded border border-emerald-200 bg-emerald-50 p-3 text-sm font-semibold text-emerald-900">
                        Signed {formatDate(assessment.signed_at)}
                        {assessment.digital_signature_hash ? <p className="mt-1 break-all text-xs text-emerald-800">Hash: {assessment.digital_signature_hash}</p> : null}
                      </div>
                    ) : null}
                    {!assessment.signed_at && assessment.decision_draft_saved_at ? (
                      <div className="rounded border border-sky-200 bg-sky-50 p-3 text-sm font-semibold text-sky-900">
                        Draft saved {formatDate(assessment.decision_draft_saved_at)}
                        <p className="mt-1 capitalize text-xs text-sky-800">Draft decision: {assessment.decision_draft?.replaceAll("_", " ")}</p>
                      </div>
                    ) : null}
                    <div className="rounded border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
                      Certificate request: <span className="font-bold">{assessment.can_request_certificate ? "Eligible" : "Not eligible yet"}</span>
                    </div>
                  </div>
                  <div className="grid gap-3">
                    <select
                      className="h-10 rounded border border-slate-200 bg-white px-3 text-sm"
                      disabled={Boolean(assessment.signed_at)}
                      value={decision.final_decision}
                      onChange={(event) => setDecision((current) => ({ ...current, final_decision: event.target.value as FitnessDecision }))}
                    >
                      {DECISION_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                    </select>
                    {["return_to_work_on_date", "temporarily_not_fit", "requires_public_health_clearance"].includes(decision.final_decision) ? (
                      <label className="grid gap-1 text-xs font-bold uppercase text-slate-500">Return date<input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm normal-case text-slate-700" disabled={Boolean(assessment.signed_at)} type="date" value={decision.return_to_work_date} onChange={(event) => setDecision((current) => ({ ...current, return_to_work_date: event.target.value }))} /></label>
                    ) : null}
                    {["temporarily_not_fit", "requires_public_health_clearance", "return_to_work_on_date"].includes(decision.final_decision) ? (
                      <div className="rounded border border-amber-200 bg-amber-50 p-3 text-sm font-semibold text-amber-900">
                        This decision will restrict food-handling duties and open return-to-work follow-up after sign-off.
                      </div>
                    ) : null}
                    <textarea className="min-h-24 rounded border border-slate-200 bg-slate-50 p-3 text-sm" disabled={Boolean(assessment.signed_at)} placeholder="Clinical decision notes" value={decision.doctor_notes} onChange={(event) => setDecision((current) => ({ ...current, doctor_notes: event.target.value }))} />
                    <label className="flex items-start gap-3 rounded border border-slate-200 bg-slate-50 p-3 text-sm font-semibold text-slate-700">
                      <input checked={decision.digital_signature_confirmation} disabled={Boolean(assessment.signed_at)} type="checkbox" onChange={(event) => setDecision((current) => ({ ...current, digital_signature_confirmation: event.target.checked }))} />
                      I confirm this is my final digital medical sign-off for this assessment.
                    </label>
                    <div className="flex flex-wrap gap-2">
                      <button className="inline-flex h-10 w-fit items-center gap-2 rounded border border-slate-200 px-4 text-sm font-bold text-slate-700 disabled:opacity-60" disabled={busy || Boolean(assessment.signed_at)} type="button" onClick={() => void saveDecisionDraft()}><Save size={16} /> Save draft</button>
                      <button className="inline-flex h-10 w-fit items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white disabled:opacity-60" disabled={busy || Boolean(assessment.signed_at) || !decision.digital_signature_confirmation} type="button" onClick={() => void submitDecision()}><FileCheck2 size={16} /> Sign decision</button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="lg:col-span-2">
                <AssessmentReportsPanel report={report} busy={busy} onGenerate={(kind) => void loadReport(kind)} />
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
