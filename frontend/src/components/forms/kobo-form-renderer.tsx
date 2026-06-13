"use client";

import { useMemo, useState } from "react";
import { Camera, FileUp, LocateFixed, Plus, QrCode, Trash2 } from "lucide-react";
import type { KoboValidationError } from "@/lib/forms/kobo-validation";
import { evaluateKoboLogic, type KoboLogic } from "@/lib/forms/kobo-logic";

export type KoboQuestionType =
  | "short_text"
  | "long_text"
  | "email"
  | "phone"
  | "url"
  | "number"
  | "decimal"
  | "currency"
  | "percentage"
  | "calculated_number"
  | "date"
  | "time"
  | "datetime"
  | "month_year"
  | "single_choice"
  | "multiple_choice"
  | "dropdown"
  | "yes_no"
  | "likert"
  | "rating"
  | "matrix"
  | "image_upload"
  | "file_upload"
  | "video_upload"
  | "audio_upload"
  | "signature"
  | "gps"
  | "qr_scan"
  | "repeat_group"
  | "calculated_field"
  | "instruction"
  | "section_header"
  | "consent"
  | "hidden"
  | "platform_field"
  | "food_handler_selector"
  | "employer_selector"
  | "branch_selector"
  | "medical_facility_selector"
  | "inspector_selector"
  | "certificate_qr_scan"
  | "accreditation_application_selector"
  | "inspection_record_selector"
  | "risk_rating"
  | "compliance_score";

export type KoboQuestion = {
  key: string;
  label: string;
  type: KoboQuestionType;
  required?: boolean;
  help_text?: string;
  options?: string[];
  questions?: KoboQuestion[];
  validation?: Record<string, unknown>;
  calculation?: string;
  placeholder?: string;
  default_value?: unknown;
};

export type KoboSection = {
  key: string;
  title: string;
  description?: string;
  questions: KoboQuestion[];
};

export type KoboSchema = {
  sections: KoboSection[];
};

type FormValues = Record<string, unknown>;
export type KoboMediaUploadContext = {
  fieldKey: string;
  questionKey: string;
  repeatGroupKey?: string;
  repeatItemId?: string;
};
export type KoboMediaUploadStatus = {
  state: "uploading" | "uploaded" | "failed";
  message?: string;
};

const selectorOptions = {
  food_handler_selector: ["Food handler record"],
  employer_selector: ["Employer record"],
  branch_selector: ["Branch / outlet record"],
  medical_facility_selector: ["Medical facility record"],
  inspector_selector: ["Inspector record"],
  accreditation_application_selector: ["Accreditation application"],
  inspection_record_selector: ["Inspection record"],
};

function asString(value: unknown) {
  return typeof value === "string" || typeof value === "number" ? String(value) : "";
}

function asArray(value: unknown) {
  return Array.isArray(value) ? value : [];
}

function emptyValue(question: KoboQuestion): unknown {
  if (question.default_value !== undefined) return question.default_value;
  if (question.type === "multiple_choice") return [];
  if (question.type === "yes_no" || question.type === "consent") return false;
  if (question.type === "gps") return { latitude: "", longitude: "" };
  if (question.type === "repeat_group") return [];
  if (["image_upload", "file_upload", "video_upload", "audio_upload"].includes(question.type)) return [];
  return "";
}

function FieldShell({ question, children, error }: { question: KoboQuestion; children: React.ReactNode; error?: string }) {
  if (question.type === "hidden") return null;
  if (question.type === "instruction" || question.type === "section_header") {
    return (
      <div className="rounded border border-info-100 bg-info-50 p-3">
        <p className="text-sm font-bold text-info-900">{question.label}</p>
        {question.help_text ? <p className="mt-1 text-sm text-info-800">{question.help_text}</p> : null}
      </div>
    );
  }
  return (
    <label className={`block rounded border bg-white p-3 text-sm ${error ? "border-danger-200 ring-1 ring-danger-100" : "border-neutral-200"}`}>
      <span className="font-semibold text-neutral-800">{question.label}{question.required ? <span className="text-danger-500"> *</span> : null}</span>
      {question.help_text ? <span className="mt-1 block text-xs text-neutral-500">{question.help_text}</span> : null}
      <span className="mt-2 block">{children}</span>
      {error ? <span className="mt-2 block text-xs font-semibold text-danger-700">{error}</span> : null}
    </label>
  );
}

export function KoboFormRenderer({
  schema,
  values,
  onChange,
  readOnly = false,
  errors = [],
  logic,
  onMediaUpload,
  mediaUploadStatuses = {},
}: {
  schema: KoboSchema;
  values: FormValues;
  onChange?: (values: FormValues) => void;
  readOnly?: boolean;
  errors?: KoboValidationError[];
  logic?: KoboLogic;
  onMediaUpload?: (question: KoboQuestion, file: File, context: KoboMediaUploadContext) => Promise<unknown>;
  mediaUploadStatuses?: Record<string, KoboMediaUploadStatus>;
}) {
  const [gpsBusy, setGpsBusy] = useState<string | null>(null);
  const currentValues = useMemo(() => {
    const next = { ...values };
    for (const section of schema.sections || []) {
      for (const question of section.questions || []) {
        if (!(question.key in next)) next[question.key] = emptyValue(question);
      }
    }
    return next;
  }, [schema.sections, values]);

  function setValue(key: string, value: unknown) {
    onChange?.({ ...currentValues, [key]: value });
  }
  function errorFor(key: string) {
    return errors.find((error) => error.key === key)?.message;
  }
  const logicState = useMemo(() => evaluateKoboLogic(logic, currentValues), [logic, currentValues]);

  function renderQuestion(question: KoboQuestion, value: unknown, setQuestionValue: (value: unknown) => void, context?: KoboMediaUploadContext) {
    const inputClass = "h-10 w-full rounded border border-neutral-200 bg-white px-3 text-sm disabled:bg-neutral-50";
    const textAreaClass = "min-h-24 w-full rounded border border-neutral-200 bg-white px-3 py-2 text-sm disabled:bg-neutral-50";

    if (question.type === "long_text") {
      return <textarea className={textAreaClass} disabled={readOnly} placeholder={question.placeholder || question.label} value={asString(value)} onChange={(event) => setQuestionValue(event.target.value)} />;
    }
    if (["short_text", "email", "phone", "url", "platform_field"].includes(question.type)) {
      const type = question.type === "email" ? "email" : question.type === "url" ? "url" : question.type === "phone" ? "tel" : "text";
      return <input className={inputClass} disabled={readOnly} placeholder={question.placeholder || question.label} type={type} value={asString(value)} onChange={(event) => setQuestionValue(event.target.value)} />;
    }
    if (["number", "decimal", "currency", "percentage", "compliance_score"].includes(question.type)) {
      return <input className={inputClass} disabled={readOnly} inputMode="decimal" placeholder={question.placeholder || question.label} type="number" value={asString(value)} onChange={(event) => setQuestionValue(event.target.value === "" ? "" : Number(event.target.value))} />;
    }
    if (["date", "time", "datetime", "month_year"].includes(question.type)) {
      const type = question.type === "datetime" ? "datetime-local" : question.type === "month_year" ? "month" : question.type;
      return <input className={inputClass} disabled={readOnly} type={type} value={asString(value)} onChange={(event) => setQuestionValue(event.target.value)} />;
    }
    if (question.type === "yes_no" || question.type === "consent") {
      return (
        <div className="flex flex-wrap gap-2">
          {[["yes", true], ["no", false]].map(([label, optionValue]) => (
            <button className={`h-9 rounded border px-3 text-sm font-semibold ${value === optionValue ? "border-brand-300 bg-brand-50 text-brand-800" : "border-neutral-200 text-neutral-700"}`} disabled={readOnly} key={String(optionValue)} type="button" onClick={() => setQuestionValue(optionValue)}>{label === "yes" ? "Yes" : "No"}</button>
          ))}
        </div>
      );
    }
    if (["single_choice", "dropdown", "likert", "rating", "risk_rating"].includes(question.type)) {
      const options = question.options?.length ? question.options : question.type === "risk_rating" ? ["Low", "Medium", "High", "Critical"] : [];
      return (
        <select className={inputClass} disabled={readOnly} value={asString(value)} onChange={(event) => setQuestionValue(event.target.value)}>
          <option value="">Select</option>
          {options.map((option) => <option key={option} value={option}>{option}</option>)}
        </select>
      );
    }
    if (question.type === "multiple_choice") {
      const selected = asArray(value).map(String);
      return (
        <div className="grid gap-2 sm:grid-cols-2">
          {(question.options || []).map((option) => (
            <label className="inline-flex items-center gap-2 rounded border border-neutral-200 px-3 py-2" key={option}>
              <input checked={selected.includes(option)} disabled={readOnly} type="checkbox" onChange={(event) => setQuestionValue(event.target.checked ? [...selected, option] : selected.filter((item) => item !== option))} />
              <span>{option}</span>
            </label>
          ))}
        </div>
      );
    }
    if (question.type === "matrix") {
      return <textarea className={textAreaClass} disabled={readOnly} placeholder="Matrix response notes" value={asString(value)} onChange={(event) => setQuestionValue(event.target.value)} />;
    }
    if (["image_upload", "file_upload", "video_upload", "audio_upload"].includes(question.type)) {
      const files = asArray(value);
      const mediaContext = context || { fieldKey: question.key, questionKey: question.key };
      const status = mediaUploadStatuses[mediaContext.fieldKey];
      const accept = question.type === "image_upload"
        ? "image/*"
        : question.type === "video_upload"
          ? "video/*"
          : question.type === "audio_upload"
            ? "audio/*"
            : typeof question.validation?.allowed_file_types === "string"
              ? question.validation.allowed_file_types.split(",").map((item) => `.${item.trim().replace(/^\./, "")}`).join(",")
              : undefined;
      return (
        <div className="space-y-2">
          <label className="inline-flex h-10 cursor-pointer items-center gap-2 rounded border border-neutral-200 px-3 text-sm font-semibold text-neutral-700 hover:bg-neutral-50">
            {question.type === "image_upload" ? <Camera size={15} /> : <FileUp size={15} />}
            <span>{question.type === "image_upload" ? "Choose image" : question.type === "video_upload" ? "Choose video" : question.type === "audio_upload" ? "Choose audio" : "Choose file"}</span>
            <input className="hidden" disabled={readOnly || status?.state === "uploading"} type="file" accept={accept} capture={question.type === "image_upload" ? "environment" : undefined} multiple onChange={async (event) => {
              const selectedFiles = Array.from(event.target.files || []);
              if (!selectedFiles.length) return;
              const uploaded = [];
              for (const file of selectedFiles) {
                if (onMediaUpload) {
                  uploaded.push(await onMediaUpload(question, file, mediaContext));
                } else {
                  uploaded.push({ file_name: file.name, file_size: file.size, mime_type: file.type, sync_status: "local_only" });
                }
              }
              setQuestionValue([...files, ...uploaded]);
              event.target.value = "";
            }} />
          </label>
          {status?.state === "uploading" ? <p className="text-xs font-semibold text-brand-700">Uploading...</p> : null}
          {status?.state === "failed" ? <p className="text-xs font-semibold text-danger-700">{status.message || "Upload failed. Try again."}</p> : null}
          {files.length ? (
            <div className="space-y-1">
              {files.map((file, index) => {
                const record = file && typeof file === "object" ? file as Record<string, unknown> : {};
                const fileName = String(record.file_name || record.name || file || `File ${index + 1}`);
                const syncStatus = String(record.sync_status || (record.id ? "uploaded" : ""));
                return (
                  <div className="flex items-center justify-between gap-2 rounded bg-neutral-50 px-2 py-1 text-xs text-neutral-600" key={`${fileName}-${index}`}>
                    <span>{fileName}{syncStatus ? ` · ${syncStatus}` : ""}</span>
                    <button className="font-bold text-danger-700 disabled:opacity-50" disabled={readOnly} type="button" onClick={() => setQuestionValue(files.filter((_, itemIndex) => itemIndex !== index))}>Remove</button>
                  </div>
                );
              })}
            </div>
          ) : null}
        </div>
      );
    }
    if (question.type === "gps") {
      const coords = typeof value === "object" && value ? value as { latitude?: string; longitude?: string } : {};
      return (
        <div className="grid gap-2 sm:grid-cols-[1fr_1fr_auto]">
          <input className={inputClass} disabled={readOnly} placeholder="Latitude" value={coords.latitude || ""} onChange={(event) => setQuestionValue({ ...coords, latitude: event.target.value })} />
          <input className={inputClass} disabled={readOnly} placeholder="Longitude" value={coords.longitude || ""} onChange={(event) => setQuestionValue({ ...coords, longitude: event.target.value })} />
          <button className="inline-flex h-10 items-center gap-2 rounded border border-brand-200 px-3 text-sm font-bold text-brand-700 disabled:opacity-50" disabled={readOnly || gpsBusy === question.key || typeof navigator === "undefined" || !navigator.geolocation} type="button" onClick={() => {
            setGpsBusy(question.key);
            navigator.geolocation.getCurrentPosition(
              (position) => {
                setQuestionValue({ latitude: String(position.coords.latitude), longitude: String(position.coords.longitude) });
                setGpsBusy(null);
              },
              () => setGpsBusy(null),
            );
          }}><LocateFixed size={15} /> GPS</button>
        </div>
      );
    }
    if (question.type === "signature") {
      return <input className={inputClass} disabled={readOnly} placeholder="Typed signature / signatory name" value={asString(value)} onChange={(event) => setQuestionValue(event.target.value)} />;
    }
    if (question.type === "qr_scan" || question.type === "certificate_qr_scan") {
      return <div className="flex gap-2"><input className={inputClass} disabled={readOnly} placeholder="QR / barcode value" value={asString(value)} onChange={(event) => setQuestionValue(event.target.value)} /><span className="inline-flex h-10 w-10 items-center justify-center rounded border border-neutral-200 text-neutral-500"><QrCode size={16} /></span></div>;
    }
    if (question.type === "calculated_field" || question.type === "calculated_number") {
      return <input className={inputClass} disabled value={asString(value || question.calculation || "Calculated automatically")} />;
    }
    if (question.type === "repeat_group") {
      const items = asArray(value) as FormValues[];
      const nested = question.questions?.length ? question.questions : [{ key: "item", label: "Item", type: "short_text" as KoboQuestionType }];
      return (
        <div className="space-y-3">
          {items.length === 0 ? <p className="rounded border border-dashed border-neutral-200 bg-neutral-50 p-3 text-xs text-neutral-500">No items added yet.</p> : null}
          {items.map((item, itemIndex) => (
            <div className="rounded border border-neutral-200 bg-neutral-50 p-3" key={itemIndex}>
              <div className="mb-3 flex items-center justify-between">
                <p className="text-xs font-bold uppercase text-neutral-500">Item {itemIndex + 1}</p>
                <div className="flex items-center gap-2">
                  <button className="inline-flex h-8 items-center rounded border border-neutral-200 px-2 text-xs font-bold text-neutral-600" disabled={readOnly} type="button" onClick={() => setQuestionValue([...items.slice(0, itemIndex + 1), { ...item }, ...items.slice(itemIndex + 1)])}>Duplicate</button>
                  <button className="inline-flex h-8 w-8 items-center justify-center rounded border border-neutral-200 text-neutral-500" disabled={readOnly} type="button" onClick={() => setQuestionValue(items.filter((_, index) => index !== itemIndex))} title="Remove item"><Trash2 size={14} /></button>
                </div>
              </div>
              <div className="space-y-2">
                {nested.map((nestedQuestion) => (
                  <FieldShell key={nestedQuestion.key} question={nestedQuestion} error={errorFor(`${question.key}.${itemIndex}.${nestedQuestion.key}`)}>
                    {renderQuestion(nestedQuestion, item[nestedQuestion.key], (nestedValue) => {
                      const next = [...items];
                      next[itemIndex] = { ...item, [nestedQuestion.key]: nestedValue };
                      setQuestionValue(next);
                    }, { fieldKey: `${question.key}.${itemIndex}.${nestedQuestion.key}`, questionKey: nestedQuestion.key, repeatGroupKey: question.key, repeatItemId: String(itemIndex) })}
                  </FieldShell>
                ))}
              </div>
            </div>
          ))}
          <button className="inline-flex h-9 items-center gap-2 rounded border border-brand-200 px-3 text-sm font-bold text-brand-700 disabled:opacity-50" disabled={readOnly} type="button" onClick={() => setQuestionValue([...items, {}])}><Plus size={15} /> Add item</button>
        </div>
      );
    }
    if (question.type in selectorOptions) {
      const options = selectorOptions[question.type as keyof typeof selectorOptions];
      return <select className={inputClass} disabled={readOnly} value={asString(value)} onChange={(event) => setQuestionValue(event.target.value)}><option value="">Select record</option>{options.map((option) => <option key={option}>{option}</option>)}</select>;
    }
    return <input className={inputClass} disabled={readOnly} value={asString(value)} onChange={(event) => setQuestionValue(event.target.value)} />;
  }

  return (
    <div className="space-y-5">
      {(schema.sections || []).map((section) => (
        logicState.hiddenSections.has(section.key) ? null : <section className="rounded border border-neutral-200 bg-white p-4" key={section.key}>
          <h3 className="text-base font-bold text-neutral-900">{section.title}</h3>
          {section.description ? <p className="mt-1 text-sm text-neutral-500">{section.description}</p> : null}
          <div className="mt-4 space-y-3">
            {(section.questions || []).map((question) => {
              if (logicState.hiddenQuestions.has(question.key)) return null;
              const visibleQuestion = { ...question, required: question.required || logicState.requiredQuestions.has(question.key) };
              return (
                <FieldShell key={question.key} question={visibleQuestion} error={errorFor(question.key)}>
                  {renderQuestion(visibleQuestion, currentValues[question.key], (value) => setValue(question.key, value), { fieldKey: question.key, questionKey: question.key })}
                </FieldShell>
              );
            })}
          </div>
        </section>
      ))}
      {logicState.warnings.length ? (
        <div className="rounded border border-warning-100 bg-warning-50 p-3 text-sm font-semibold text-warning-700">
          {logicState.warnings.map((warning) => <p key={`${warning.target_key}-${warning.message}`}>{warning.message}</p>)}
        </div>
      ) : null}
    </div>
  );
}
