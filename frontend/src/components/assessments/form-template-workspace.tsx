"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertCircle, Copy, FilePlus2, GitBranch, Layers3, Lock, Plus, RefreshCw, Save, Send, Sparkles } from "lucide-react";
import { StatusBadge } from "@/components/status/status-badge";
import {
  adoptAssessmentFormTemplate,
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

function scopeTone(scope: string) {
  if (scope === "national") return "bg-violet-50 text-violet-700 border-violet-200";
  if (scope === "state") return "bg-sky-50 text-sky-700 border-sky-200";
  return "bg-emerald-50 text-emerald-700 border-emerald-200";
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

  const localTemplates = useMemo(() => templates.filter((item) => item.scope === scope), [scope, templates]);
  const parentTemplates = useMemo(() => {
    if (scope === "national") return [];
    if (scope === "state") return templates.filter((item) => item.scope === "national");
    return templates.filter((item) => item.scope === "national" || item.scope === "state");
  }, [scope, templates]);
  const selected = useMemo(() => templates.find((item) => item.id === selectedId) || localTemplates[0] || parentTemplates[0], [selectedId, templates, localTemplates, parentTemplates]);
  const canAdoptSelected = Boolean(
    selected &&
    scope !== "national" &&
    selected.scope !== scope &&
    ["published", "active"].includes(selected.status)
  );
  const inheritedSectionCount = selected?.sections.filter((item) => item.locked).length || 0;
  const inheritedQuestionCount = selected?.sections.reduce((count, item) => count + item.questions.filter((questionItem) => questionItem.locked).length, 0) || 0;
  const stateAdoptedTemplates = useMemo(() => (
    scope === "state"
      ? templates.filter((item) => item.scope === "state" && item.parent_template)
      : []
  ), [scope, templates]);
  const availableFederalTemplates = useMemo(() => (
    scope === "state"
      ? templates.filter((item) => item.scope === "national" && ["published", "active"].includes(item.status))
      : []
  ), [scope, templates]);
  const publishedStateTemplates = useMemo(() => (
    scope === "state"
      ? templates.filter((item) => item.scope === "state" && ["published", "active"].includes(item.status))
      : []
  ), [scope, templates]);

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      if (scope === "facility" && !facilityId) {
        const facility = await getCurrentMedicalFacility();
        setFacilityId(facility.id);
      }
      const rows = await listAssessmentFormTemplates();
      const stateId = getTokenStateId();
      const filtered = rows.filter((item) => {
        if (scope === "national") return item.scope === "national";
        if (scope === "state") {
          return item.scope === "national" || (item.scope === "state" && (!stateId || item.state === stateId));
        }
        return item.scope === "national" || (item.scope === "state" && (!stateId || item.state === stateId)) || (item.scope === "facility" && item.facility === facilityId);
      });
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

  async function adoptTemplate() {
    if (!selected) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const adopted = await adoptAssessmentFormTemplate(selected.id);
      setSelectedId(adopted.id);
      setSuccess(`Template adopted into ${label(scope)} workspace.`);
      await loadData();
    } catch {
      setError("Could not adopt this parent template.");
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
        {parentTemplates.length ? (
          <div className="grid gap-2">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.18em] text-neutral-500">
              <GitBranch size={14} />
              Parent Templates
            </div>
            {parentTemplates.map((template) => (
              <button className={`rounded border px-3 py-2 text-left text-sm ${selected?.id === template.id ? "border-brand-600 bg-brand-50" : "border-neutral-200 bg-white"}`} key={template.id} onClick={() => setSelectedId(template.id)} type="button">
                <span className="block font-bold text-neutral-900">{template.name}</span>
                <span className="mt-1 flex flex-wrap items-center gap-2 text-xs text-neutral-500">
                  <span className={`rounded border px-2 py-0.5 font-bold ${scopeTone(template.scope)}`}>{label(template.scope)}</span>
                  <span>v{template.version}</span>
                  <StatusBadge status={template.status} />
                </span>
              </button>
            ))}
          </div>
        ) : null}
        <div className="grid gap-2">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.18em] text-neutral-500">
            <Layers3 size={14} />
            {scope === "national" ? "Federal Templates" : "Local Templates"}
          </div>
          {localTemplates.map((template) => (
            <button className={`rounded border px-3 py-2 text-left text-sm ${selected?.id === template.id ? "border-brand-600 bg-brand-50" : "border-neutral-200 bg-white"}`} key={template.id} onClick={() => setSelectedId(template.id)} type="button">
              <span className="block font-bold text-neutral-900">{template.name}</span>
              <span className="mt-1 flex flex-wrap items-center gap-2 text-xs text-neutral-500">
                <span>v{template.version}</span>
                <StatusBadge status={template.status} />
                {template.parent_template ? <span className="rounded bg-neutral-100 px-2 py-0.5 font-bold text-neutral-600">Inherited base</span> : null}
              </span>
            </button>
          ))}
          {!localTemplates.length && !loading ? <p className="text-sm text-neutral-500">No local templates yet.</p> : null}
        </div>
      </section>

      <section className="grid gap-4">
        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}
        {success ? <div className="rounded-lg bg-brand-50 p-3 text-sm font-semibold text-brand-800">{success}</div> : null}

        {scope === "state" ? (
          <section className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-700">Federal Policy Adoption</p>
                  <h2 className="mt-1 text-lg font-bold text-neutral-900">State declaration adoption workspace</h2>
                  <p className="mt-2 max-w-3xl text-sm text-neutral-500">
                    Adopt published Federal declaration templates, extend them with State-specific questions, route them for internal approval, and publish the active State implementation version for facilities.
                  </p>
                </div>
                <div className="rounded-full bg-neutral-100 px-4 py-2 text-sm font-semibold text-neutral-700">
                  {publishedStateTemplates.length} active/published state versions
                </div>
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <div className="rounded-lg border border-neutral-200 bg-neutral-50 px-4 py-3">
                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-neutral-500">Federal templates</p>
                  <p className="mt-2 text-2xl font-bold text-neutral-900">{availableFederalTemplates.length}</p>
                  <p className="mt-1 text-sm text-neutral-500">Published national declaration bases available for State adoption.</p>
                </div>
                <div className="rounded-lg border border-neutral-200 bg-neutral-50 px-4 py-3">
                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-neutral-500">Adopted by State</p>
                  <p className="mt-2 text-2xl font-bold text-neutral-900">{stateAdoptedTemplates.length}</p>
                  <p className="mt-1 text-sm text-neutral-500">Templates already derived from a Federal source into this State workspace.</p>
                </div>
                <div className="rounded-lg border border-neutral-200 bg-neutral-50 px-4 py-3">
                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-neutral-500">Locked inherited fields</p>
                  <p className="mt-2 text-2xl font-bold text-neutral-900">{inheritedQuestionCount}</p>
                  <p className="mt-1 text-sm text-neutral-500">Inherited Federal questions remain protected inside the selected template chain.</p>
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="grid gap-4">
                <div>
                  <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.18em] text-brand-700">
                    <Plus size={14} />
                    State Can Extend
                  </div>
                  <ul className="mt-2 grid gap-2 text-sm text-neutral-600">
                    <li className="rounded border border-brand-100 bg-brand-50 px-3 py-2">Add State outbreak questions, surveillance consent, and local administrative fields.</li>
                    <li className="rounded border border-brand-100 bg-brand-50 px-3 py-2">Route drafts through internal approval before publish and activation.</li>
                    <li className="rounded border border-brand-100 bg-brand-50 px-3 py-2">Publish the active State implementation version for facility adoption.</li>
                  </ul>
                </div>
                <div>
                  <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.18em] text-warning-700">
                    <Lock size={14} />
                    Federal Rules Stay Locked
                  </div>
                  <ul className="mt-2 grid gap-2 text-sm text-neutral-600">
                    <li className="rounded border border-warning-100 bg-warning-50 px-3 py-2">Federal fields cannot be deleted, hidden, renamed, or downgraded from required.</li>
                    <li className="rounded border border-warning-100 bg-warning-50 px-3 py-2">Federal validation, meaning, and risk logic remain unchanged in inherited sections.</li>
                    <li className="rounded border border-warning-100 bg-warning-50 px-3 py-2">Locked sections and questions in adopted templates show the inherited national baseline.</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>
        ) : null}

        {selected ? (
          <>
            <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-bold text-neutral-900">{selected.name}</h2>
                  <p className="mt-1 text-sm text-neutral-500">{selected.description || "No description"}</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <StatusBadge status={selected.status} />
                    <StatusBadge status={selected.form_type} />
                    <span className={`rounded border px-2 py-1 text-xs font-bold ${scopeTone(selected.scope)}`}>{label(selected.scope)}</span>
                    {selected.parent_template ? <span className="rounded bg-neutral-100 px-2 py-1 text-xs font-bold text-neutral-700">Inherited from parent</span> : null}
                    {selected.review_comment ? <StatusBadge status="changes_requested" /> : null}
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {canAdoptSelected ? <button className="inline-flex h-9 items-center gap-2 rounded bg-emerald-600 px-3 text-xs font-bold text-white" disabled={busy} onClick={() => void adoptTemplate()} type="button"><Sparkles size={14} /> Adopt into {label(scope)}</button> : null}
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

            <section className="grid gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm lg:grid-cols-4">
              <div className="rounded border border-neutral-200 bg-neutral-50 p-3">
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-neutral-500">Base chain</p>
                <p className="mt-2 text-sm font-bold text-neutral-900">{selected.parent_template ? "Inherited template" : "Origin template"}</p>
              </div>
              <div className="rounded border border-neutral-200 bg-neutral-50 p-3">
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-neutral-500">Sections</p>
                <p className="mt-2 text-sm font-bold text-neutral-900">{selected.sections.length}</p>
              </div>
              <div className="rounded border border-neutral-200 bg-neutral-50 p-3">
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-neutral-500">Inherited sections</p>
                <p className="mt-2 text-sm font-bold text-neutral-900">{inheritedSectionCount}</p>
              </div>
              <div className="rounded border border-neutral-200 bg-neutral-50 p-3">
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-neutral-500">Locked fields</p>
                <p className="mt-2 text-sm font-bold text-neutral-900">{inheritedQuestionCount}</p>
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
                    <div className="flex items-center justify-between gap-3">
                      <h4 className="text-sm font-bold text-neutral-900">{item.title}</h4>
                      {item.locked ? <span className="inline-flex items-center gap-1 rounded bg-neutral-100 px-2 py-1 text-[11px] font-bold text-neutral-700"><Lock size={12} /> Locked</span> : null}
                    </div>
                    <div className="mt-3 grid gap-2">
                      {item.questions.map((field) => (
                        <div className="rounded border border-neutral-200 bg-white p-3 text-sm" key={field.id}>
                          <div className="flex items-center justify-between gap-3">
                            <p className="font-bold text-neutral-800">{field.label}</p>
                            {field.locked ? <span className="inline-flex items-center gap-1 rounded bg-neutral-100 px-2 py-1 text-[11px] font-bold text-neutral-700"><Lock size={12} /> Inherited</span> : null}
                          </div>
                          <p className="mt-1 text-xs text-neutral-500">{label(field.question_type)} · {label(field.privacy_classification)} · {label(field.respondent_role)}</p>
                        </div>
                      ))}
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
