"use client";

import { useEffect, useMemo, useState } from "react";
import { Check, Save, Send } from "lucide-react";
import { StatusBadge } from "@/components/status/status-badge";
import type { AssessmentFormResponse } from "@/types/assessments";

type Question = AssessmentFormResponse["question_snapshot"]["sections"][number]["questions"][number];

function emptyValue(question: Question) {
  if (["multiple_choice", "symptom_checklist", "exposure_history"].includes(question.question_type)) return [];
  if (["yes_no", "checkbox"].includes(question.question_type)) return false;
  if (question.question_type === "blood_pressure") return { systolic: "", diastolic: "" };
  return "";
}

function questionInput(question: Question, value: unknown, onChange: (value: unknown) => void, disabled: boolean) {
  const baseClass = "min-h-10 rounded border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-900 disabled:bg-neutral-100";
  const options = question.options || [];
  if (question.question_type === "long_text" || question.question_type === "clinical_note" || question.question_type === "doctor_only_note" || question.question_type === "lab_only_note") {
    return <textarea className={`${baseClass} min-h-24`} disabled={disabled} onChange={(event) => onChange(event.target.value)} value={String(value ?? "")} />;
  }
  if (question.question_type === "yes_no" || question.question_type === "checkbox") {
    return (
      <label className="inline-flex items-center gap-2 text-sm font-semibold text-neutral-700">
        <input checked={Boolean(value)} disabled={disabled} onChange={(event) => onChange(event.target.checked)} type="checkbox" />
        Confirmed
      </label>
    );
  }
  if (["single_choice", "dropdown", "lab_result_status"].includes(question.question_type)) {
    return (
      <select className={baseClass} disabled={disabled} onChange={(event) => onChange(event.target.value)} value={String(value ?? "")}>
        <option value="">Select</option>
        {options.map((option) => <option key={option} value={option}>{option}</option>)}
      </select>
    );
  }
  if (["multiple_choice", "symptom_checklist", "exposure_history"].includes(question.question_type)) {
    const selected = Array.isArray(value) ? value.map(String) : [];
    return (
      <div className="grid gap-2">
        {options.map((option) => (
          <label className="inline-flex items-center gap-2 text-sm text-neutral-700" key={option}>
            <input
              checked={selected.includes(option)}
              disabled={disabled}
              onChange={(event) => {
                onChange(event.target.checked ? [...selected, option] : selected.filter((item) => item !== option));
              }}
              type="checkbox"
            />
            {option}
          </label>
        ))}
      </div>
    );
  }
  if (question.question_type === "blood_pressure") {
    const reading = (value && typeof value === "object" ? value : {}) as Record<string, string>;
    return (
      <div className="grid gap-2 sm:grid-cols-2">
        <input className={baseClass} disabled={disabled} inputMode="numeric" onChange={(event) => onChange({ ...reading, systolic: Number(event.target.value) })} placeholder="Systolic" value={reading.systolic ?? ""} />
        <input className={baseClass} disabled={disabled} inputMode="numeric" onChange={(event) => onChange({ ...reading, diastolic: Number(event.target.value) })} placeholder="Diastolic" value={reading.diastolic ?? ""} />
      </div>
    );
  }
  const type = question.question_type === "date" || question.question_type === "vaccination_date" ? "date" : question.question_type === "time" ? "time" : question.question_type === "datetime" ? "datetime-local" : ["number", "temperature", "weight", "height", "pulse_rate", "vaccine_dose"].includes(question.question_type) ? "number" : "text";
  return <input className={baseClass} disabled={disabled} onChange={(event) => onChange(type === "number" ? Number(event.target.value) : event.target.value)} placeholder={question.placeholder || question.label} type={type} value={String(value ?? "")} />;
}

export function DynamicFormRenderer({
  response,
  mode,
  busy,
  onSave,
  onSubmit,
  onValidate,
}: {
  response: AssessmentFormResponse;
  mode: "complete" | "review";
  busy?: boolean;
  onSave?: (values: Record<string, unknown>) => void;
  onSubmit?: (values: Record<string, unknown>) => void;
  onValidate?: () => void;
}) {
  const initialValues = useMemo(() => {
    const values = { ...(response.response_data || {}) };
    for (const section of response.question_snapshot.sections || []) {
      for (const question of section.questions) {
        if (!(question.key in values)) values[question.key] = emptyValue(question);
      }
    }
    return values;
  }, [response]);
  const [values, setValues] = useState<Record<string, unknown>>(initialValues);

  useEffect(() => {
    setValues(initialValues);
  }, [initialValues]);

  const locked = response.is_locked || ["submitted", "resubmitted", "under_review", "validated", "locked"].includes(response.status);
  const readOnly = mode === "review" || locked;

  return (
    <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-neutral-200 p-4">
        <div>
          <h2 className="text-base font-bold text-neutral-900">{response.template_name || response.question_snapshot.name}</h2>
          <p className="mt-1 text-xs font-semibold text-neutral-500">v{response.template_version} · {response.respondent_role.replaceAll("_", " ")}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge status={response.status} />
          {response.risk_flags?.map((flag) => <StatusBadge key={flag} status={flag} />)}
        </div>
      </div>
      <div className="grid gap-5 p-4">
        {response.question_snapshot.sections?.map((section) => (
          <div className="grid gap-3" key={section.key}>
            <div>
              <h3 className="text-sm font-bold text-neutral-900">{section.title}</h3>
              {section.description ? <p className="mt-1 text-sm text-neutral-500">{section.description}</p> : null}
            </div>
            <div className="grid gap-3">
              {section.questions.map((question) => (
                <label className="grid gap-1 rounded border border-neutral-200 bg-neutral-50 p-3" key={question.key}>
                  <span className="text-sm font-bold text-neutral-800">{question.label}{question.required ? <span className="text-danger-500"> *</span> : null}</span>
                  {question.help_text ? <span className="text-xs text-neutral-500">{question.help_text}</span> : null}
                  {questionInput(question, values[question.key], (value) => setValues((current) => ({ ...current, [question.key]: value })), readOnly)}
                </label>
              ))}
            </div>
          </div>
        ))}
        <div className="flex flex-wrap gap-2">
          {mode === "complete" ? (
            <>
              <button className="inline-flex h-10 items-center gap-2 rounded border border-neutral-200 px-3 text-sm font-bold text-neutral-700 disabled:opacity-50" disabled={busy || locked} onClick={() => onSave?.(values)} type="button"><Save size={16} /> Save draft</button>
              <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-600 px-3 text-sm font-bold text-white disabled:bg-neutral-300" disabled={busy || locked} onClick={() => onSubmit?.(values)} type="button"><Send size={16} /> Submit</button>
            </>
          ) : (
            <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-700 px-3 text-sm font-bold text-white disabled:bg-neutral-300" disabled={busy || !["submitted", "resubmitted", "under_review"].includes(response.status)} onClick={onValidate} type="button"><Check size={16} /> Validate</button>
          )}
        </div>
      </div>
    </section>
  );
}
