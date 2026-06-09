"use client";

import { AlertTriangle, Save, Send } from "lucide-react";

import type { HealthDeclaration } from "@/types/assessments";

export const DECLARATION_FIELDS = [
  ["diarrhoea_vomiting_last_7_days", "Diarrhoea or vomiting in the last 7 days"],
  ["fever_more_than_one_week", "Fever lasting more than one week"],
  ["skin_trouble", "Skin trouble"],
  ["boils_styes_sepsis", "Boils, styes, or sepsis"],
  ["discharge_eye_ear_nose_mouth", "Discharge from eye, ear, nose, or mouth"],
  ["recurring_skin_or_ear_infection", "Recurring skin or ear infection"],
  ["recurring_bowel_disorder", "Recurring bowel disorder"],
  ["cholera_contact_last_5_days", "Contact with cholera case in the last 5 days"],
  ["diarrhoea_vomiting_contact_last_7_days", "Contact with diarrhoea or vomiting case in the last 7 days"],
  ["typhoid_paratyphoid_jaundice_contact_last_21_days", "Contact with typhoid, paratyphoid, or jaundice case in the last 21 days"],
  ["typhoid_or_paratyphoid_carrier", "Known typhoid or paratyphoid carrier"],
  ["previous_or_current_typhoid", "Previous or current typhoid"],
] as const;

export type DeclarationField = typeof DECLARATION_FIELDS[number][0];
export type DeclarationFormValue = Record<DeclarationField, boolean> & { certified_true: boolean };

export const EMPTY_DECLARATION_FORM = DECLARATION_FIELDS.reduce(
  (acc, [key]) => ({ ...acc, [key]: false }),
  { certified_true: false } as DeclarationFormValue
);

export function declarationToForm(declaration?: HealthDeclaration | null): DeclarationFormValue {
  if (!declaration) return EMPTY_DECLARATION_FORM;
  return DECLARATION_FIELDS.reduce(
    (acc, [key]) => ({ ...acc, [key]: Boolean(declaration[key]) }),
    { certified_true: Boolean(declaration.certified_true) } as DeclarationFormValue
  );
}

export function HealthDeclarationForm({
  value,
  declaration,
  disabled,
  busy,
  onChange,
  onSaveDraft,
  onSubmit,
}: {
  value: DeclarationFormValue;
  declaration?: HealthDeclaration | null;
  disabled?: boolean;
  busy?: boolean;
  onChange: (next: DeclarationFormValue) => void;
  onSaveDraft: () => void;
  onSubmit: () => void;
}) {
  const hasPositiveAnswer = DECLARATION_FIELDS.some(([field]) => value[field]);

  function updateField(field: keyof DeclarationFormValue, checked: boolean) {
    onChange({ ...value, [field]: checked });
  }

  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-bold text-neutral-900">Declaration Form</h2>
          <p className="mt-1 text-xs font-semibold text-neutral-500">Version {declaration?.version || 1}</p>
        </div>
        {declaration?.is_locked ? <span className="rounded bg-neutral-100 px-2 py-1 text-xs font-bold text-neutral-700">Locked</span> : null}
      </div>

      {(hasPositiveAnswer || declaration?.risk_flag) ? (
        <div className="mt-4 flex items-start gap-2 rounded border border-warning-100 bg-warning-50 p-3 text-sm font-semibold text-amber-900">
          <AlertTriangle className="mt-0.5 shrink-0" size={16} />
          This does not automatically disqualify you. A doctor will review your response.
        </div>
      ) : null}

      <div className="mt-4 grid gap-3">
        {DECLARATION_FIELDS.map(([field, label]) => (
          <label key={field} className="flex items-start gap-3 rounded border border-neutral-200 bg-neutral-50 p-3 text-sm font-semibold text-neutral-700">
            <input checked={value[field]} className="mt-1 h-4 w-4 rounded border-neutral-300" disabled={disabled || busy} type="checkbox" onChange={(event) => updateField(field, event.target.checked)} />
            <span>{label}</span>
          </label>
        ))}
        <label className="flex items-start gap-3 rounded border border-brand-200 bg-brand-50 p-3 text-sm font-semibold text-brand-900">
          <input checked={value.certified_true} className="mt-1 h-4 w-4 rounded border-brand-300" disabled={disabled || busy} type="checkbox" onChange={(event) => updateField("certified_true", event.target.checked)} />
          <span>I certify that the information provided is true.</span>
        </label>
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        <button className="inline-flex h-10 items-center gap-2 rounded border border-neutral-200 px-4 text-sm font-bold text-neutral-700 disabled:opacity-60" disabled={disabled || busy} type="button" onClick={onSaveDraft}>
          <Save size={16} /> Save draft
        </button>
        <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white disabled:opacity-60" disabled={disabled || busy || !value.certified_true} type="button" onClick={onSubmit}>
          <Send size={16} /> Submit declaration
        </button>
      </div>
    </div>
  );
}
