"use client";

import { CheckCircle2, Repeat2 } from "lucide-react";

import { StatusBadge } from "@/components/status/status-badge";
import type { LabTest } from "@/types/assessments";

const REVIEW_OPTIONS = [
  ["cleared", "Clear result"],
  ["repeat_test", "Repeat test"],
  ["temporarily_not_fit", "Recommend temporarily not fit"],
  ["public_health_clearance", "Require public health clearance"],
] as const;

export function LabResultReviewPanel({
  tests,
  busy,
  reviewNotes,
  repeatReasons,
  onReviewNotesChange,
  onRepeatReasonChange,
  onReview,
  onRepeat,
}: {
  tests?: LabTest[];
  busy?: boolean;
  reviewNotes: Record<string, { doctor_review_notes: string; doctor_recommendation: string }>;
  repeatReasons: Record<string, string>;
  onReviewNotesChange: (testId: string, value: { doctor_review_notes: string; doctor_recommendation: string }) => void;
  onRepeatReasonChange: (testId: string, reason: string) => void;
  onReview: (testId: string) => void;
  onRepeat: (testId: string) => void;
}) {
  if (!tests?.length) {
    return <p className="text-sm text-slate-500">No lab tests requested yet.</p>;
  }

  return (
    <div className="grid gap-2">
      {tests.map((test) => {
        const reviewValue = reviewNotes[test.id] || {
          doctor_review_notes: test.doctor_review_notes || "",
          doctor_recommendation: test.doctor_recommendation || (test.is_flagged ? "repeat_test" : "cleared"),
        };
        const canReview = ["positive", "negative", "inconclusive", "repeat_required", "submitted_to_doctor"].includes(test.status);
        return (
          <div className={`rounded border p-3 ${test.is_flagged ? "border-amber-200 bg-amber-50" : "border-slate-200 bg-slate-50"}`} key={test.id}>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="font-bold capitalize text-slate-950">{test.test_name || test.test_type.replaceAll("_", " ")}</p>
              <StatusBadge status={test.status} />
            </div>
            {test.parent_lab_test ? <p className="mt-1 text-xs font-semibold text-amber-700">Repeat test</p> : null}
            {test.is_flagged ? <p className="mt-1 text-xs font-semibold text-amber-800">Flagged for doctor review</p> : null}
            {test.result_document_url ? <a className="mt-2 inline-flex text-xs font-bold text-brand-deep" href={test.result_document_url}>Open uploaded result</a> : null}
            {test.repeat_reason ? <p className="mt-1 text-xs text-slate-600">{test.repeat_reason}</p> : null}
            {test.status === "reviewed" ? (
              <div className="mt-3 rounded border border-emerald-200 bg-emerald-50 p-2 text-xs font-semibold text-emerald-900">
                Reviewed: {test.doctor_recommendation?.replaceAll("_", " ") || "cleared"}
              </div>
            ) : null}
            {canReview ? (
              <div className="mt-3 grid gap-2">
                <select className="h-9 rounded border border-slate-200 bg-white px-2 text-xs" disabled={busy} value={reviewValue.doctor_recommendation} onChange={(event) => onReviewNotesChange(test.id, { ...reviewValue, doctor_recommendation: event.target.value })}>
                  {REVIEW_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select>
                <textarea className="min-h-16 rounded border border-slate-200 bg-white p-2 text-xs" disabled={busy} placeholder="Doctor review notes" value={reviewValue.doctor_review_notes} onChange={(event) => onReviewNotesChange(test.id, { ...reviewValue, doctor_review_notes: event.target.value })} />
                <div className="flex flex-wrap gap-2">
                  <button className="inline-flex h-8 w-fit items-center gap-1 rounded bg-brand-green px-3 text-xs font-bold text-white disabled:opacity-60" disabled={busy} type="button" onClick={() => onReview(test.id)}>
                    <CheckCircle2 size={14} /> Review
                  </button>
                  {["positive", "inconclusive", "repeat_required"].includes(test.status) ? (
                    <>
                      <textarea className="min-h-8 rounded border border-slate-200 bg-white p-2 text-xs" disabled={busy} placeholder="Reason for repeat test" value={repeatReasons[test.id] || ""} onChange={(event) => onRepeatReasonChange(test.id, event.target.value)} />
                      <button className="inline-flex h-8 w-fit items-center gap-1 rounded border border-amber-300 px-3 text-xs font-bold text-amber-800 disabled:opacity-60" disabled={busy || !repeatReasons[test.id]?.trim()} type="button" onClick={() => onRepeat(test.id)}>
                        <Repeat2 size={14} /> Repeat
                      </button>
                    </>
                  ) : null}
                </div>
              </div>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
