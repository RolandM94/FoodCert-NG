import { FileCheck2, Send } from "lucide-react";
import { StatusBadge } from "@/components/status/status-badge";
import type { MedicalAssessment } from "@/types/assessments";

type ReadinessItem = {
  label: string;
  ready: boolean;
};

type SubmitToStatePanelProps = {
  assessment: MedicalAssessment;
  busy: boolean;
  submissionNotes: string;
  clarificationResponse: string;
  onSubmissionNotesChange: (value: string) => void;
  onClarificationResponseChange: (value: string) => void;
  onSubmitToState: () => void;
  onRespondToClarification: () => void;
};

function label(value?: string) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

export function SubmitToStatePanel({
  assessment,
  busy,
  submissionNotes,
  clarificationResponse,
  onSubmissionNotesChange,
  onClarificationResponseChange,
  onSubmitToState,
  onRespondToClarification,
}: SubmitToStatePanelProps) {
  const readinessItems: ReadinessItem[] = [
    { label: "Fit final decision", ready: assessment.final_decision === "fit" },
    { label: "Doctor signed", ready: Boolean(assessment.signed_at) },
    { label: "Payment confirmed", ready: ["success", "paid", "completed"].includes(assessment.payment_status || "") },
    { label: "Declaration validated", ready: assessment.declaration_status === "validated" },
    { label: "Physical exam completed", ready: assessment.physical_exam_status === "completed" },
    { label: "Lab reviewed", ready: assessment.lab_status === "reviewed" },
    { label: "Vaccination reviewed", ready: assessment.vaccination_status === "reviewed" },
  ];
  const awaitingClarification = assessment.certificate_submission_status === "correction_requested";
  const blockedStatus = ["pending_validation", "approved", "certificate_issued"].includes(assessment.certificate_submission_status || "");

  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm lg:col-span-2">
      <div className="mb-4 flex items-center gap-2">
        <FileCheck2 className="text-brand-700" size={18} />
        <h2 className="text-sm font-bold text-neutral-900">State Certificate Validation</h2>
      </div>
      <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="grid gap-2">
          {readinessItems.map((item) => (
            <div className="flex items-center justify-between gap-3 rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm font-semibold text-neutral-700" key={item.label}>
              <span>{item.label}</span>
              <StatusBadge status={item.ready ? "ready" : "pending"} />
            </div>
          ))}
        </div>
        <div className="grid gap-3">
          <div className="rounded border border-neutral-200 bg-neutral-50 p-3 text-sm text-neutral-700">
            Current State status: <span className="font-bold capitalize">{label(assessment.certificate_submission_status)}</span>
          </div>
          {awaitingClarification ? (
            <>
              <textarea className="min-h-24 rounded border border-neutral-200 bg-neutral-50 p-3 text-sm" placeholder="Response to State clarification" value={clarificationResponse} onChange={(event) => onClarificationResponseChange(event.target.value)} />
              <button className="inline-flex h-10 w-fit items-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white disabled:opacity-60" disabled={busy || !clarificationResponse.trim()} type="button" onClick={onRespondToClarification}><Send size={16} /> Send response</button>
            </>
          ) : (
            <>
              <textarea className="min-h-20 rounded border border-neutral-200 bg-neutral-50 p-3 text-sm" placeholder="Submission notes for State reviewer" value={submissionNotes} onChange={(event) => onSubmissionNotesChange(event.target.value)} />
              <button className="inline-flex h-10 w-fit items-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white disabled:opacity-60" disabled={busy || !assessment.can_request_certificate || blockedStatus} type="button" onClick={onSubmitToState}><Send size={16} /> Submit to State</button>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
