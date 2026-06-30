"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Save, Send } from "lucide-react";

import type { AssessmentFormQuestion, AssessmentFormSnapshot, HealthDeclaration } from "@/types/assessments";

export type DeclarationFormValue = {
  response_data: Record<string, unknown>;
  certified_true: boolean;
};

export const EMPTY_DECLARATION_FORM: DeclarationFormValue = {
  response_data: {},
  certified_true: false,
};

function emptyValue(question: AssessmentFormQuestion) {
  if (["multiple_choice", "symptom_checklist", "exposure_history"].includes(question.question_type)) return [];
  if (["yes_no", "checkbox"].includes(question.question_type)) return false;
  if (question.question_type === "blood_pressure") return { systolic: "", diastolic: "" };
  return "";
}

function conditionMatches(condition: Record<string, unknown> | undefined, values: Record<string, unknown>, currentAnswer?: unknown): boolean {
  if (!condition || !Object.keys(condition).length) return true;
  if (Array.isArray(condition.all)) {
    return condition.all.every((item) => conditionMatches(item as Record<string, unknown>, values, currentAnswer));
  }
  if (Array.isArray(condition.any)) {
    return condition.any.some((item) => conditionMatches(item as Record<string, unknown>, values, currentAnswer));
  }
  const useCurrentAnswer = Boolean(condition.use_current_answer);
  const answer = useCurrentAnswer ? currentAnswer : values[String(condition.question || "")];
  const operator = String(condition.operator || "equals");
  const expected = condition.value;

  if (operator === "exists") return answer !== undefined && answer !== null && answer !== "";
  if (operator === "is_truthy") return Boolean(answer);
  if (operator === "is_falsy") return !Boolean(answer);
  if (operator === "equals") return answer === expected;
  if (operator === "not_equals") return answer !== expected;
  if (operator === "contains") return Array.isArray(answer) ? answer.includes(expected) : String(answer || "").includes(String(expected || ""));
  if (operator === "in") return Array.isArray(expected) && expected.includes(answer);
  if (operator === "not_in") return Array.isArray(expected) && !expected.includes(answer);

  const actualNumber = Number(answer);
  const expectedNumber = Number(expected);
  if (Number.isNaN(actualNumber) || Number.isNaN(expectedNumber)) return false;
  if (operator === "greater_than") return actualNumber > expectedNumber;
  if (operator === "greater_than_or_equal") return actualNumber >= expectedNumber;
  if (operator === "less_than") return actualNumber < expectedNumber;
  if (operator === "less_than_or_equal") return actualNumber <= expectedNumber;
  return false;
}

function questionInput(question: AssessmentFormQuestion, value: unknown, onChange: (value: unknown) => void, disabled: boolean) {
  const baseClass = "min-h-10 rounded border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-900 outline-none transition focus:border-brand-500 disabled:bg-neutral-100 disabled:text-neutral-500";
  const options = question.options || [];

  if (["long_text", "clinical_note", "doctor_only_note", "lab_only_note"].includes(question.question_type)) {
    return <textarea className={`${baseClass} min-h-24`} disabled={disabled} onChange={(event) => onChange(event.target.value)} value={String(value ?? "")} />;
  }

  if (["yes_no", "checkbox"].includes(question.question_type)) {
    const binaryOptions: Array<{ label: string; value: boolean }> = [
      { label: "Yes", value: true },
      { label: "No", value: false },
    ];
    return (
      <div className="inline-flex rounded-md border border-neutral-200 bg-white p-1">
        {binaryOptions.map((option) => (
          <button
            key={option.label}
            className={`h-9 rounded px-3 text-sm font-semibold transition ${value === option.value ? "bg-brand-600 text-white" : "text-neutral-600 hover:bg-neutral-50"}`}
            disabled={disabled}
            onClick={() => onChange(option.value)}
            type="button"
          >
            {option.label}
          </button>
        ))}
      </div>
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
              onChange={(event) => onChange(event.target.checked ? [...selected, option] : selected.filter((item) => item !== option))}
              type="checkbox"
            />
            {option}
          </label>
        ))}
      </div>
    );
  }

  if (question.question_type === "blood_pressure") {
    const reading = (value && typeof value === "object" ? value : {}) as Record<string, string | number>;
    return (
      <div className="grid gap-2 sm:grid-cols-2">
        <input className={baseClass} disabled={disabled} inputMode="numeric" onChange={(event) => onChange({ ...reading, systolic: Number(event.target.value) || "" })} placeholder="Systolic" value={String(reading.systolic ?? "")} />
        <input className={baseClass} disabled={disabled} inputMode="numeric" onChange={(event) => onChange({ ...reading, diastolic: Number(event.target.value) || "" })} placeholder="Diastolic" value={String(reading.diastolic ?? "")} />
      </div>
    );
  }

  const type = question.question_type === "date" || question.question_type === "vaccination_date"
    ? "date"
    : question.question_type === "time"
      ? "time"
      : question.question_type === "datetime"
        ? "datetime-local"
        : ["number", "temperature", "weight", "height", "pulse_rate", "vaccine_dose"].includes(question.question_type)
          ? "number"
          : "text";

  return (
    <input
      className={baseClass}
      disabled={disabled}
      onChange={(event) => onChange(type === "number" ? (event.target.value === "" ? "" : Number(event.target.value)) : event.target.value)}
      placeholder={question.placeholder || question.label}
      type={type}
      value={String(value ?? "")}
    />
  );
}

function schemaFromDeclaration(declaration?: HealthDeclaration | null): AssessmentFormSnapshot | null {
  const schema = declaration?.merged_schema;
  if (!schema || typeof schema !== "object" || !("sections" in schema)) return null;
  return schema as AssessmentFormSnapshot;
}

export function declarationToForm(declaration?: HealthDeclaration | null): DeclarationFormValue {
  const schema = schemaFromDeclaration(declaration);
  const responseData = { ...(declaration?.response_data || {}) };
  if (schema?.sections) {
    for (const section of schema.sections) {
      for (const question of section.questions) {
        if (!(question.key in responseData)) responseData[question.key] = emptyValue(question);
      }
    }
  }
  return {
    response_data: responseData,
    certified_true: Boolean(declaration?.certified_true),
  };
}

export function HealthDeclarationForm({
  declaration,
  disabled,
  busy,
  onSaveDraft,
  onSubmit,
}: {
  declaration?: HealthDeclaration | null;
  disabled?: boolean;
  busy?: boolean;
  onSaveDraft: (payload: DeclarationFormValue) => void;
  onSubmit: (payload: DeclarationFormValue) => void;
}) {
  const schema = useMemo(() => schemaFromDeclaration(declaration), [declaration]);
  const initialForm = useMemo(() => declarationToForm(declaration), [declaration]);
  const [value, setValue] = useState<DeclarationFormValue>(initialForm);

  useEffect(() => {
    setValue(initialForm);
  }, [initialForm]);

  const visibleSections = useMemo(() => {
    if (!schema?.sections) return [];
    return schema.sections
      .map((section) => ({
        ...section,
        questions: section.questions.filter((question) => conditionMatches(question.conditional_logic?.visible_if as Record<string, unknown> | undefined, value.response_data)),
      }))
      .filter((section) => conditionMatches(section.visibility_rules as Record<string, unknown> | undefined, value.response_data) && section.questions.length);
  }, [schema, value.response_data]);

  const hasPositiveAnswer = Object.entries(value.response_data).some(([key, fieldValue]) => key !== "certified_true" && fieldValue === true);

  function updateField(field: string, nextValue: unknown) {
    setValue((current) => ({
      ...current,
      response_data: {
        ...current.response_data,
        [field]: nextValue,
      },
    }));
  }

  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-bold text-neutral-900">{schema?.name || "Declaration Form"}</h2>
          <p className="mt-1 text-xs font-semibold text-neutral-500">Version {declaration?.version || schema?.template_version || 1}</p>
        </div>
        <div className="flex items-center gap-2">
          {declaration?.form_response_status ? (
            <span className="rounded bg-brand-50 px-2 py-1 text-xs font-bold capitalize text-brand-700">{declaration.form_response_status.replaceAll("_", " ")}</span>
          ) : null}
          {declaration?.is_locked ? <span className="rounded bg-neutral-100 px-2 py-1 text-xs font-bold text-neutral-700">Locked</span> : null}
        </div>
      </div>

      {(hasPositiveAnswer || declaration?.risk_flag) ? (
        <div className="mt-4 flex items-start gap-2 rounded border border-warning-100 bg-warning-50 p-3 text-sm font-semibold text-amber-900">
          <AlertTriangle className="mt-0.5 shrink-0" size={16} />
          One or more answers may require doctor review before the assessment can move forward.
        </div>
      ) : null}

      {!visibleSections.length ? (
        <div className="mt-4 rounded border border-dashed border-neutral-200 bg-neutral-50 p-4 text-sm text-neutral-500">
          No declaration fields are available for this assessment yet.
        </div>
      ) : (
        <div className="mt-4 grid gap-5">
          {visibleSections.map((section) => (
            <section className="grid gap-3 rounded-lg border border-neutral-200 bg-neutral-50/60 p-4" key={section.key}>
              <div>
                <h3 className="text-sm font-bold text-neutral-900">{section.title}</h3>
                {section.description ? <p className="mt-1 text-sm text-neutral-500">{section.description}</p> : null}
              </div>
              <div className="grid gap-3">
                {section.questions.map((question) => (
                  <label className="grid gap-1 rounded-md border border-neutral-200 bg-white p-3" key={question.key}>
                    <span className="text-sm font-bold text-neutral-800">
                      {question.label}
                      {question.required ? <span className="text-danger-500"> *</span> : null}
                    </span>
                    {question.help_text ? <span className="text-xs text-neutral-500">{question.help_text}</span> : null}
                    {questionInput(question, value.response_data[question.key], (nextValue) => updateField(question.key, nextValue), Boolean(disabled || busy))}
                  </label>
                ))}
              </div>
            </section>
          ))}

          <label className="flex items-start gap-3 rounded border border-brand-200 bg-brand-50 p-3 text-sm font-semibold text-brand-900">
            <input
              checked={value.certified_true}
              className="mt-1 h-4 w-4 rounded border-brand-300"
              disabled={disabled || busy}
              type="checkbox"
              onChange={(event) => setValue((current) => ({ ...current, certified_true: event.target.checked }))}
            />
            <span>I certify that the information provided is true and complete.</span>
          </label>
        </div>
      )}

      <div className="mt-5 flex flex-wrap gap-2">
        <button className="inline-flex h-10 items-center gap-2 rounded border border-neutral-200 px-4 text-sm font-bold text-neutral-700 disabled:opacity-60" disabled={disabled || busy || !schema} type="button" onClick={() => onSaveDraft(value)}>
          <Save size={16} /> Save draft
        </button>
        <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white disabled:opacity-60" disabled={disabled || busy || !schema || !value.certified_true} type="button" onClick={() => onSubmit(value)}>
          <Send size={16} /> Submit declaration
        </button>
      </div>
    </div>
  );
}
