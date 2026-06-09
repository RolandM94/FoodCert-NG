"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertCircle, Copy, FilePlus2, Plus, RefreshCw, Save, Send } from "lucide-react";
import { StatusBadge } from "@/components/status/status-badge";
import {
  createAssessmentFormQuestion,
  createAssessmentFormSection,
  createAssessmentFormTemplate,
  duplicateAssessmentFormTemplate,
  listAssessmentFormTemplates,
  transitionAssessmentFormTemplate,
} from "@/lib/api/assessments";
import { getCurrentMedicalFacility } from "@/lib/api/facilities";
import type { AssessmentFormTemplate, AssessmentFormType, AssessmentPrivacyClassification, AssessmentQuestionType, AssessmentRespondentRole } from "@/types/assessments";
import type { UserRole } from "@/types/auth";

const FORM_TYPES: AssessmentFormType[] = ["health_declaration", "facility_intake", "doctor_clinical_review", "lab_result", "vaccination_review", "return_to_work", "illness_report", "state_validation_checklist", "inspection_support"];
const QUESTION_TYPES: AssessmentQuestionType[] = ["short_text", "long_text", "number", "date", "yes_no", "single_choice", "multiple_choice", "checkbox", "dropdown", "email", "phone", "file_upload", "temperature", "blood_pressure", "pulse_rate", "symptom_checklist", "vaccination_date", "lab_result_status", "clinical_note", "doctor_only_note", "lab_only_note"];
const PRIVACY: AssessmentPrivacyClassification[] = ["medical_sensitive", "restricted_medical", "internal_administrative", "regulatory_restricted", "employer_safe_summary", "inspector_safe_summary", "public_safe"];
const RESPONDENTS: AssessmentRespondentRole[] = ["food_handler", "doctor", "lab_staff", "facility_staff", "state_user", "inspector"];

function label(value: string) {
  return value.replaceAll("_", " ");
}

function getTokenStateId() {
  if (typeof window === "undefined") return "";
  try {
    const token = localStorage.getItem("foodcert_access_token");
    return token ? JSON.parse(atob(token.split(".")[1])).state_id || "" : "";
  } catch {
    return "";
  }
}

export function FormTemplateWorkspace({
  role,
  scope,
  title,
}: {
  role: UserRole;
  scope: "national" | "state" | "facility";
  title: string;
}) {
  const [templates, setTemplates] = useState<AssessmentFormTemplate[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [facilityId, setFacilityId] = useState("");
  const [form, setForm] = useState({ name: "", description: "", form_type: scope === "facility" ? "facility_intake" : "health_declaration", is_mandatory: scope !== "facility", requires_approval: scope === "facility" });
  const [section, setSection] = useState({ key: "main", title: "Main", description: "" });
  const [question, setQuestion] = useState({ key: "", label: "", question_type: "yes_no", privacy_classification: "medical_sensitive", respondent_role: scope === "facility" ? "food_handler" : "food_handler", required: true, options: "" });

  const selected = useMemo(() => templates.find((item) => item.id === selectedId) || templates[0], [selectedId, templates]);

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      if (scope === "facility" && !facilityId) {
        const facility = await getCurrentMedicalFacility();
        setFacilityId(facility.id);
      }
      const rows = await listAssessmentFormTemplates();
      const filtered = rows.filter((item) => item.scope === scope || (scope === "state" && item.scope === "facility"));
      setTemplates(filtered);
      if (!selectedId && filtered[0]) setSelectedId(filtered[0].id);
    } catch {
      setError("Could not load assessment form templates.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function createTemplate() {
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const stateId = getTokenStateId();
      const created = await createAssessmentFormTemplate({
        ...form,
        scope,
        state: scope === "state" ? stateId || undefined : undefined,
        facility: scope === "facility" ? facilityId : undefined,
      });
      setTemplates((rows) => [created, ...rows]);
      setSelectedId(created.id);
      setSuccess("Template created.");
    } catch {
      setError("Could not create template.");
    } finally {
      setBusy(false);
    }
  }

  async function addSection() {
    if (!selected) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await createAssessmentFormSection({ template: selected.id, ...section, sort_order: selected.sections.length + 1 });
      setSuccess("Section added.");
      await loadData();
    } catch {
      setError("Could not add section.");
    } finally {
      setBusy(false);
    }
  }

  async function addQuestion() {
    const targetSection = selected?.sections[0];
    if (!targetSection) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await createAssessmentFormQuestion({
        section: targetSection.id,
        ...question,
        required: Boolean(question.required),
        options: question.options.split(",").map((item) => item.trim()).filter(Boolean),
        sort_order: targetSection.questions.length + 1,
      });
      setQuestion((current) => ({ ...current, key: "", label: "", options: "" }));
      setSuccess("Question added.");
      await loadData();
    } catch {
      setError("Could not add question. Check field type, options, key uniqueness, and privacy rules.");
    } finally {
      setBusy(false);
    }
  }

  async function transition(action: "submit-for-approval" | "approve" | "reject" | "request-changes" | "publish" | "activate" | "retire") {
    if (!selected) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const payload = action === "reject" || action === "request-changes" ? { reason: "Reviewed from form workspace." } : {};
      const updated = await transitionAssessmentFormTemplate(selected.id, action, payload);
      setTemplates((rows) => rows.map((item) => item.id === updated.id ? updated : item));
      setSuccess(`${label(action)} completed.`);
    } catch {
      setError(`Could not ${label(action)} this template.`);
    } finally {
      setBusy(false);
    }
  }

  async function duplicate() {
    if (!selected) return;
    setBusy(true);
    setError("");
    try {
      const copy = await duplicateAssessmentFormTemplate(selected.id);
      setTemplates((rows) => [copy, ...rows]);
      setSelectedId(copy.id);
      setSuccess("Template duplicated as a new draft version.");
    } catch {
      setError("Could not duplicate template.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[360px_1fr]">
      <section className="grid h-fit gap-4 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-base font-bold text-neutral-900">{title}</h2>
          <button className="inline-flex h-9 items-center gap-2 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700" onClick={() => void loadData()} type="button"><RefreshCw size={14} /> Refresh</button>
        </div>
        <div className="grid gap-2">
          <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} placeholder="Template name" value={form.name} />
          <textarea className="min-h-20 rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm" onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} placeholder="Purpose and review context" value={form.description} />
          <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" disabled={scope === "facility"} onChange={(event) => setForm((current) => ({ ...current, form_type: event.target.value }))} value={form.form_type}>
            {FORM_TYPES.map((type) => <option key={type} value={type}>{label(type)}</option>)}
          </select>
          <label className="inline-flex items-center gap-2 text-sm font-semibold text-neutral-700"><input checked={form.is_mandatory} disabled={scope === "facility"} onChange={(event) => setForm((current) => ({ ...current, is_mandatory: event.target.checked }))} type="checkbox" /> Mandatory</label>
          <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-600 px-3 text-sm font-bold text-white disabled:bg-neutral-300" disabled={busy || !form.name.trim()} onClick={() => void createTemplate()} type="button"><FilePlus2 size={16} /> Create template</button>
        </div>
        <div className="grid gap-2">
          {templates.map((template) => (
            <button className={`rounded border px-3 py-2 text-left text-sm ${selected?.id === template.id ? "border-brand-600 bg-brand-50" : "border-neutral-200 bg-white"}`} key={template.id} onClick={() => setSelectedId(template.id)} type="button">
              <span className="block font-bold text-neutral-900">{template.name}</span>
              <span className="mt-1 flex items-center gap-2 text-xs text-neutral-500">v{template.version} · {label(template.scope)} · <StatusBadge status={template.status} /></span>
            </button>
          ))}
          {!templates.length && !loading ? <p className="text-sm text-neutral-500">No templates found.</p> : null}
        </div>
      </section>

      <section className="grid gap-4">
        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}
        {success ? <div className="rounded-lg bg-brand-50 p-3 text-sm font-semibold text-brand-800">{success}</div> : null}

        {selected ? (
          <>
            <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-bold text-neutral-900">{selected.name}</h2>
                  <p className="mt-1 text-sm text-neutral-500">{selected.description || "No description"}</p>
                  <div className="mt-2 flex flex-wrap gap-2"><StatusBadge status={selected.status} /><StatusBadge status={selected.form_type} />{selected.review_comment ? <StatusBadge status="changes_requested" /> : null}</div>
                </div>
                <div className="flex flex-wrap gap-2">
                  <button className="inline-flex h-9 items-center gap-2 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700" disabled={busy} onClick={() => void duplicate()} type="button"><Copy size={14} /> Duplicate</button>
                  {selected.status === "draft" || selected.status === "rejected" || selected.status === "changes_requested" ? <button className="inline-flex h-9 items-center gap-2 rounded bg-brand-600 px-3 text-xs font-bold text-white" disabled={busy} onClick={() => void transition("submit-for-approval")} type="button"><Send size={14} /> Submit</button> : null}
                  {["pending_approval"].includes(selected.status) && role === "state_admin" ? <button className="inline-flex h-9 items-center rounded bg-brand-700 px-3 text-xs font-bold text-white" disabled={busy} onClick={() => void transition("approve")} type="button">Approve</button> : null}
                  {["pending_approval"].includes(selected.status) && role === "state_admin" ? <button className="inline-flex h-9 items-center rounded border border-warning-100 px-3 text-xs font-bold text-warning-700" disabled={busy} onClick={() => void transition("request-changes")} type="button">Request changes</button> : null}
                  {["pending_approval"].includes(selected.status) && role === "state_admin" ? <button className="inline-flex h-9 items-center rounded border border-danger-100 px-3 text-xs font-bold text-danger-700" disabled={busy} onClick={() => void transition("reject")} type="button">Reject</button> : null}
                  {["approved"].includes(selected.status) ? <button className="inline-flex h-9 items-center rounded bg-brand-700 px-3 text-xs font-bold text-white" disabled={busy} onClick={() => void transition("publish")} type="button">Publish</button> : null}
                  {["published"].includes(selected.status) ? <button className="inline-flex h-9 items-center rounded bg-brand-600 px-3 text-xs font-bold text-white" disabled={busy} onClick={() => void transition("activate")} type="button">Activate</button> : null}
                </div>
              </div>
            </section>

            {["draft", "rejected", "changes_requested"].includes(selected.status) ? (
              <section className="grid gap-4 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm lg:grid-cols-2">
                <div className="grid gap-2">
                  <h3 className="text-sm font-bold text-neutral-900">Add section</h3>
                  <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" onChange={(event) => setSection((current) => ({ ...current, key: event.target.value }))} placeholder="section_key" value={section.key} />
                  <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" onChange={(event) => setSection((current) => ({ ...current, title: event.target.value }))} placeholder="Section title" value={section.title} />
                  <button className="inline-flex h-10 items-center justify-center gap-2 rounded border border-neutral-200 px-3 text-sm font-bold text-neutral-700" disabled={busy || !section.key.trim() || !section.title.trim()} onClick={() => void addSection()} type="button"><Plus size={16} /> Add section</button>
                </div>
                <div className="grid gap-2">
                  <h3 className="text-sm font-bold text-neutral-900">Add question</h3>
                  <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" onChange={(event) => setQuestion((current) => ({ ...current, key: event.target.value }))} placeholder="question_key" value={question.key} />
                  <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" onChange={(event) => setQuestion((current) => ({ ...current, label: event.target.value }))} placeholder="Question label" value={question.label} />
                  <div className="grid gap-2 sm:grid-cols-3">
                    <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" onChange={(event) => setQuestion((current) => ({ ...current, question_type: event.target.value }))} value={question.question_type}>{QUESTION_TYPES.map((type) => <option key={type} value={type}>{label(type)}</option>)}</select>
                    <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" onChange={(event) => setQuestion((current) => ({ ...current, privacy_classification: event.target.value }))} value={question.privacy_classification}>{PRIVACY.map((value) => <option key={value} value={value}>{label(value)}</option>)}</select>
                    <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" onChange={(event) => setQuestion((current) => ({ ...current, respondent_role: event.target.value }))} value={question.respondent_role}>{RESPONDENTS.map((value) => <option key={value} value={value}>{label(value)}</option>)}</select>
                  </div>
                  <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" onChange={(event) => setQuestion((current) => ({ ...current, options: event.target.value }))} placeholder="Options, comma separated" value={question.options} />
                  <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-600 px-3 text-sm font-bold text-white disabled:bg-neutral-300" disabled={busy || !selected.sections.length || !question.key.trim() || !question.label.trim()} onClick={() => void addQuestion()} type="button"><Save size={16} /> Add question</button>
                </div>
              </section>
            ) : null}

            <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <h3 className="text-sm font-bold text-neutral-900">Preview</h3>
              <div className="mt-4 grid gap-4">
                {selected.sections.map((item) => (
                  <div className="rounded border border-neutral-200 bg-neutral-50 p-3" key={item.id}>
                    <h4 className="text-sm font-bold text-neutral-900">{item.title}</h4>
                    <div className="mt-3 grid gap-2">
                      {item.questions.map((field) => <div className="rounded border border-neutral-200 bg-white p-3 text-sm" key={field.id}><p className="font-bold text-neutral-800">{field.label}</p><p className="mt-1 text-xs text-neutral-500">{label(field.question_type)} · {label(field.privacy_classification)} · {label(field.respondent_role)}</p></div>)}
                      {!item.questions.length ? <p className="text-sm text-neutral-500">No questions in this section.</p> : null}
                    </div>
                  </div>
                ))}
                {!selected.sections.length ? <p className="text-sm text-neutral-500">Add a section to start building this template.</p> : null}
              </div>
            </section>
          </>
        ) : null}
      </section>
    </div>
  );
}
