"use client";

import { AlertTriangle, CheckCircle2, Save } from "lucide-react";

export const EXAM_FIELDS = [
  ["fever", "Fever"],
  ["jaundice", "Jaundice"],
  ["skin_infection", "Skin infection"],
  ["boils_styes_sepsis", "Boils, styes, or sepsis"],
  ["discharge", "Discharge"],
  ["diarrhoea", "Diarrhoea"],
  ["vomiting", "Vomiting"],
  ["sore_throat_with_fever", "Sore throat with fever"],
  ["cough_or_flu", "Cough or flu"],
  ["known_typhoid_carrier_history", "Known typhoid carrier history"],
] as const;

export type PhysicalExamField = typeof EXAM_FIELDS[number][0];
export type PhysicalExamFormValue = Record<PhysicalExamField, boolean> & { other_notes: string };

export const EMPTY_PHYSICAL_EXAM_FORM = EXAM_FIELDS.reduce(
  (acc, [key]) => ({ ...acc, [key]: false }),
  { other_notes: "" } as PhysicalExamFormValue
);

export function PhysicalExamForm({
  value,
  disabled,
  busy,
  completed,
  onChange,
  onSaveDraft,
  onComplete,
}: {
  value: PhysicalExamFormValue;
  disabled?: boolean;
  busy?: boolean;
  completed?: boolean;
  onChange: (next: PhysicalExamFormValue) => void;
  onSaveDraft: () => void;
  onComplete: () => void;
}) {
  const riskFlag = EXAM_FIELDS.some(([field]) => value[field]);

  function updateField(field: keyof PhysicalExamFormValue, next: boolean | string) {
    onChange({ ...value, [field]: next });
  }

  return (
    <div className="grid gap-3">
      {riskFlag ? (
        <div className="flex items-start gap-2 rounded border border-amber-200 bg-amber-50 p-3 text-sm font-semibold text-amber-900">
          <AlertTriangle className="mt-0.5 shrink-0" size={16} />
          Clinical findings require doctor review. This is not a diagnosis or automatic disqualification.
        </div>
      ) : null}
      {EXAM_FIELDS.map(([field, text]) => (
        <label className="flex items-center justify-between gap-3 rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-700" key={field}>
          {text}
          <input checked={Boolean(value[field])} disabled={disabled || busy} type="checkbox" onChange={(event) => updateField(field, event.target.checked)} />
        </label>
      ))}
      <textarea className="min-h-24 rounded border border-slate-200 bg-slate-50 p-3 text-sm" disabled={disabled || busy} placeholder="Other notes" value={value.other_notes} onChange={(event) => updateField("other_notes", event.target.value)} />
      <div className="flex flex-wrap gap-2">
        <button className="inline-flex h-10 w-fit items-center gap-2 rounded border border-slate-200 px-4 text-sm font-bold text-slate-700 disabled:opacity-60" disabled={disabled || busy || completed} type="button" onClick={onSaveDraft}>
          <Save size={16} /> Save draft
        </button>
        <button className="inline-flex h-10 w-fit items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white disabled:opacity-60" disabled={disabled || busy || completed} type="button" onClick={onComplete}>
          <CheckCircle2 size={16} /> Complete exam
        </button>
      </div>
    </div>
  );
}
