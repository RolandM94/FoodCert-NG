"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AlertCircle, ArrowLeft, BadgeCheck, CalendarDays, ClipboardList, FileCheck2, FlaskConical, ShieldCheck, Stethoscope, Syringe } from "lucide-react";

import { AssessmentPrerequisiteChecklist } from "@/components/assessments/assessment-prerequisite-checklist";
import { AssessmentReportsPanel } from "@/components/assessments/assessment-reports-panel";
import { AssessmentStatusBadge } from "@/components/assessments/assessment-status-badge";
import { AssessmentStepper } from "@/components/assessments/assessment-stepper";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { getAssessment, getAssessmentStatus } from "@/lib/api/assessments";
import { requestCertificate } from "@/lib/api/certificates";
import { getAssessmentReport, type AssessmentReportKind } from "@/lib/api/reports";
import type { AssessmentStatusSnapshot, MedicalAssessment } from "@/types/assessments";
import type { GeneratedReport } from "@/types/reports";

function dateLabel(value?: string) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function Page() {
  const params = useParams<{ id: string }>();
  const [assessment, setAssessment] = useState<MedicalAssessment | null>(null);
  const [snapshot, setSnapshot] = useState<AssessmentStatusSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [report, setReport] = useState<GeneratedReport | null>(null);

  const loadData = useCallback(async () => {
    if (!params.id) return;
    setLoading(true);
    setError("");
    try {
      const [row, statusRow] = await Promise.all([getAssessment(params.id), getAssessmentStatus(params.id)]);
      setAssessment(row);
      setSnapshot(statusRow);
    } catch {
      setError("Could not load assessment.");
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  async function submitCertificateRequest() {
    if (!assessment) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await requestCertificate(assessment.id);
      setSuccess("Certificate request submitted.");
      await loadData();
    } catch {
      setError("Certificate request could not be submitted yet.");
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
      setError("Could not generate this report yet.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <PortalShell role="food_handler" title="Assessment Detail" description="Review current workflow status, appointment details, safe health-review progress, and certificate readiness.">
      <div className="grid gap-5">
        <Link className="inline-flex w-fit items-center gap-2 rounded border border-neutral-200 bg-white px-3 py-2 text-sm font-bold text-neutral-700 shadow-sm" href="/food-handler/assessments">
          <ArrowLeft size={16} /> Back to assessments
        </Link>
        {loading ? <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading assessment...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}
        {success ? <div className="rounded-lg bg-brand-50 p-3 text-sm font-semibold text-brand-800">{success}</div> : null}

        {assessment && snapshot ? (
          <>
            <section className="grid gap-3 md:grid-cols-4">
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><Stethoscope className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Status</p><div className="mt-2"><AssessmentStatusBadge status={snapshot.current_status} label={snapshot.current_status_label} /></div></div>
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><CalendarDays className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Appointment</p><p className="text-sm font-bold text-neutral-900">{dateLabel(assessment.appointment_date || assessment.assessment_date)}</p></div>
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><ClipboardList className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Next action</p><p className="text-sm font-bold text-neutral-900">{snapshot.next_action.label}</p></div>
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><BadgeCheck className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Certificate</p><StatusBadge status={assessment.certificate_submission_status || "not_submitted"} /></div>
            </section>

            <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <h2 className="text-sm font-bold text-neutral-900">Progress</h2>
              <div className="mt-4"><AssessmentStepper steps={snapshot.steps} /></div>
            </section>

            <section className="grid gap-4 lg:grid-cols-[1fr_0.8fr]">
              <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                <h2 className="text-sm font-bold text-neutral-900">Prerequisites</h2>
                <div className="mt-4"><AssessmentPrerequisiteChecklist blockers={snapshot.blockers} warnings={snapshot.warnings} /></div>
              </div>
              <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                <h2 className="text-sm font-bold text-neutral-900">Assessment</h2>
                <dl className="mt-4 grid gap-3 text-sm">
                  <div className="flex items-center justify-between gap-3"><dt className="text-neutral-500">Facility</dt><dd className="font-bold text-neutral-900">{assessment.facility_name || "Medical facility"}</dd></div>
                  <div className="flex items-center justify-between gap-3"><dt className="text-neutral-500">Doctor</dt><dd className="font-bold text-neutral-900">{assessment.doctor_name || "Not assigned"}</dd></div>
                  <div className="flex items-center justify-between gap-3"><dt className="text-neutral-500">Payment</dt><dd><StatusBadge status={assessment.payment_status || "missing"} /></dd></div>
                  <div className="flex items-center justify-between gap-3"><dt className="text-neutral-500">Decision</dt><dd><StatusBadge status={assessment.final_decision} /></dd></div>
                </dl>
              </div>
            </section>

            <section className="grid gap-3 md:grid-cols-4">
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><ClipboardList className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Declaration</p><StatusBadge status={assessment.declaration_status} /></div>
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><ShieldCheck className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Physical exam</p><StatusBadge status={assessment.physical_exam_status} /></div>
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><FlaskConical className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Lab review</p><StatusBadge status={assessment.lab_status} /></div>
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><Syringe className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Vaccination</p><StatusBadge status={assessment.vaccination_status} /></div>
            </section>

            <AssessmentReportsPanel
              report={report}
              busy={busy}
              actions={[
                { kind: "summary", label: "Summary" },
                { kind: "return-to-work", label: "Return to work" },
              ]}
              onGenerate={(kind) => void loadReport(kind)}
            />

            {assessment.can_request_certificate ? (
              <section className="rounded-lg border border-brand-200 bg-brand-50 p-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h2 className="text-sm font-bold text-brand-900">Certificate Ready</h2>
                    <p className="mt-1 text-sm text-brand-800">Final fit decision was signed {dateLabel(assessment.signed_at)}.</p>
                  </div>
                  <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white disabled:opacity-60" disabled={busy} type="button" onClick={() => void submitCertificateRequest()}>
                    <FileCheck2 size={16} /> Request certificate
                  </button>
                </div>
              </section>
            ) : null}
          </>
        ) : null}
      </div>
    </PortalShell>
  );
}
