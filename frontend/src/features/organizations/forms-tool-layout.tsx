"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Activity, BadgeCheck, ClipboardCheck, ClipboardList,
  FileStack, Plus, Pencil,
  Eye, Save, Trash2, ListPlus, Type, Hash, Calendar, CheckSquare, Upload, MapPin, QrCode, Copy, ChevronUp, ChevronDown, Grip,
} from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { DashboardCard } from "@/components/ui/dashboard-card";
import { KoboFormRenderer, type KoboQuestionType } from "@/components/forms/kobo-form-renderer";
import type { KoboLogicRule } from "@/lib/forms/kobo-logic";
import {
  fetchFormTemplates, createFormTemplate, updateFormTemplate, saveFormTemplateDraft, publishFormTemplate, archiveFormTemplate, fetchFormTemplateVersions,
  fetchFormAssignments, createFormAssignment, cancelFormAssignment, fetchFormAssignmentSummary, sendFormAssignmentReminder,
  fetchFormResponses, reviewFormResponse, returnFormResponse, fetchFormResponseActivity,
  downloadFormAttachmentsExport, downloadFormResponsesExport, fetchFormsPermissions,
} from "@/lib/api/forms";
import { getApiErrorMessage } from "@/lib/api/client";
import type { FormTemplate } from "@/lib/api/forms";
import { FormsReportsTab } from "@/components/forms/forms-reports-tab";

const FormsPermsCtx = createContext<Set<string>>(new Set());
function useFormsPerms() { return useContext(FormsPermsCtx); }

type TabKey = "overview" | "templates" | "assignments" | "responses" | "exports" | "reports" | "settings";
type BuilderQuestion = {
  key: string;
  label: string;
  type: KoboQuestionType;
  required: boolean;
  help_text?: string;
  options?: string[];
  questions?: BuilderQuestion[];
  validation?: Record<string, unknown>;
};
type BuilderSection = {
  key: string;
  title: string;
  description?: string;
  questions: BuilderQuestion[];
};
type BuilderSchema = {
  sections: BuilderSection[];
};

const TABS: Record<TabKey, string> = {
  overview: "Overview", templates: "Templates", assignments: "Assignments",
  responses: "Responses", exports: "Exports", reports: "Reports", settings: "Settings",
};

const PURPOSE_LABELS: Record<string, string> = {
  inspection_checklist: "Inspection Checklist",
  employer_data_collection: "Employer Data Collection",
  employer_compliance: "Compliance Self-Assessment",
  facility_data_collection: "Facility Data Collection",
  facility_monthly_report: "Monthly Report",
  accreditation_checklist: "Accreditation Checklist",
  re_accreditation_checklist: "Re-accreditation Checklist",
  food_handler_survey: "Food Handler Survey",
  food_handler_declaration: "Food Handler Declaration",
  incident_report: "Incident Report",
  training_feedback: "Training Feedback",
  general_data_collection: "General Data Collection",
};

const MODULE_LABELS: Record<string, string> = {
  inspections: "Inspections",
  employers: "Employers",
  facilities: "Medical Facilities",
  accreditation: "Accreditation",
  food_handlers: "Food Handlers",
  reports: "Reports",
  compliance: "Compliance",
  training: "Training / Feedback",
  incidents: "Incident Reporting",
  general: "General",
};

const RESPONDENT_LABELS: Record<string, string> = {
  inspector: "Inspector",
  employer_admin: "Employer Admin",
  branch_manager: "Branch Manager",
  facility_admin: "Facility Admin",
  food_handler: "Food Handler",
  state_user: "State Officer",
};

const QUESTION_TYPES: Array<{ value: KoboQuestionType; label: string; icon: typeof Type }> = [
  { value: "short_text", label: "Short Text", icon: Type },
  { value: "long_text", label: "Long Text", icon: Type },
  { value: "email", label: "Email", icon: Type },
  { value: "phone", label: "Phone Number", icon: Type },
  { value: "url", label: "URL", icon: Type },
  { value: "number", label: "Number", icon: Hash },
  { value: "decimal", label: "Decimal", icon: Hash },
  { value: "currency", label: "Currency", icon: Hash },
  { value: "percentage", label: "Percentage", icon: Hash },
  { value: "calculated_number", label: "Calculated Number", icon: Hash },
  { value: "date", label: "Date", icon: Calendar },
  { value: "time", label: "Time", icon: Calendar },
  { value: "datetime", label: "Date & Time", icon: Calendar },
  { value: "month_year", label: "Month / Year", icon: Calendar },
  { value: "single_choice", label: "Single Choice", icon: CheckSquare },
  { value: "multiple_choice", label: "Multiple Choice", icon: CheckSquare },
  { value: "dropdown", label: "Dropdown", icon: CheckSquare },
  { value: "yes_no", label: "Yes / No", icon: CheckSquare },
  { value: "likert", label: "Likert Scale", icon: CheckSquare },
  { value: "rating", label: "Rating Scale", icon: CheckSquare },
  { value: "matrix", label: "Matrix Question", icon: CheckSquare },
  { value: "image_upload", label: "Image Upload", icon: Upload },
  { value: "file_upload", label: "File Upload", icon: Upload },
  { value: "video_upload", label: "Video Upload", icon: Upload },
  { value: "audio_upload", label: "Audio Upload", icon: Upload },
  { value: "gps", label: "GPS Location", icon: MapPin },
  { value: "signature", label: "Signature", icon: Pencil },
  { value: "qr_scan", label: "QR / Barcode Scan", icon: QrCode },
  { value: "repeat_group", label: "Repeat Group", icon: ListPlus },
  { value: "calculated_field", label: "Calculated Field", icon: Hash },
  { value: "instruction", label: "Instruction", icon: ListPlus },
  { value: "section_header", label: "Section Header", icon: ListPlus },
  { value: "consent", label: "Consent / Declaration", icon: CheckSquare },
  { value: "hidden", label: "Hidden Field", icon: Type },
  { value: "platform_field", label: "Auto-filled Platform Field", icon: Type },
  { value: "food_handler_selector", label: "Food Handler Selector", icon: Type },
  { value: "employer_selector", label: "Employer Selector", icon: Type },
  { value: "branch_selector", label: "Branch / Outlet Selector", icon: Type },
  { value: "medical_facility_selector", label: "Medical Facility Selector", icon: Type },
  { value: "inspector_selector", label: "Inspector Selector", icon: Type },
  { value: "certificate_qr_scan", label: "Certificate QR Scan", icon: QrCode },
  { value: "accreditation_application_selector", label: "Accreditation Application Selector", icon: Type },
  { value: "inspection_record_selector", label: "Inspection Record Selector", icon: Type },
  { value: "risk_rating", label: "Risk Rating", icon: CheckSquare },
  { value: "compliance_score", label: "Compliance Score", icon: Hash },
];
const OPTION_QUESTION_TYPES = ["single_choice", "multiple_choice", "dropdown", "likert", "rating", "matrix", "risk_rating"];
const BRANCHING_QUESTION_TYPES = ["single_choice", "multiple_choice", "dropdown", "yes_no", "risk_rating"];

function formatDate(v?: string) { if (!v) return "—"; return new Date(v).toLocaleDateString("en-NG", { dateStyle: "medium" }); }
function emptySchema(): BuilderSchema { return { sections: [] }; }
function questionFromRaw(question: unknown, questionIndex: number): BuilderQuestion {
  const field = question as Partial<BuilderQuestion>;
  const nestedQuestions = Array.isArray(field.questions) ? field.questions : [];
  return {
    key: field.key || `question_${questionIndex + 1}`,
    label: field.label || `Question ${questionIndex + 1}`,
    type: (field.type || "short_text") as KoboQuestionType,
    required: Boolean(field.required),
    help_text: field.help_text || "",
    options: Array.isArray(field.options) ? field.options.map(String) : [],
    questions: nestedQuestions.map((nested, nestedIndex) => questionFromRaw(nested, nestedIndex)),
    validation: field.validation || {},
  };
}
function schemaFromVersion(value?: Record<string, unknown>): BuilderSchema {
  const sections = Array.isArray(value?.sections) ? value.sections : [];
  return {
    sections: sections.map((section, sectionIndex) => {
      const item = section as Partial<BuilderSection>;
      const questions = Array.isArray(item.questions) ? item.questions : [];
      return {
        key: item.key || `section_${sectionIndex + 1}`,
        title: item.title || `Section ${sectionIndex + 1}`,
        description: item.description || "",
        questions: questions.map((question, questionIndex) => questionFromRaw(question, questionIndex)),
      };
    }),
  };
}

// ── Overview Tab ──
function OverviewTab() {
  const { data: templates } = useQuery({ queryKey: ["form-templates"], queryFn: async () => fetchFormTemplates() });
  const { data: assignments } = useQuery({ queryKey: ["form-assignments"], queryFn: async () => fetchFormAssignments() });
  const { data: responses } = useQuery({ queryKey: ["form-responses"], queryFn: async () => fetchFormResponses() });
  const tl = Array.isArray(templates) ? templates : [];
  const al = Array.isArray(assignments) ? assignments : [];
  const rl = Array.isArray(responses) ? responses : [];

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <DashboardCard icon={FileStack} label="Templates" value={tl.length} />
        <DashboardCard icon={ClipboardList} label="Assignments" value={al.length} />
        <DashboardCard icon={ClipboardCheck} label="Submitted" value={rl.filter(r => r.status==="submitted").length} />
        <DashboardCard icon={Activity} label="Overdue" value={al.filter(a => a.status==="overdue").length} />
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-bold text-neutral-900">Recent Templates</h3>
          <div className="mt-3 space-y-2">
            {tl.slice(0,5).map(t => (
              <div key={t.id} className="flex justify-between text-sm border-b border-neutral-50 pb-2">
                <span className="font-medium text-neutral-800">{t.title}</span>
                <StatusBadge status={t.status} />
              </div>
            ))}
            {tl.length === 0 && <p className="text-sm text-neutral-500">No templates yet.</p>}
          </div>
        </section>
        <section className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-bold text-neutral-900">Recent Responses</h3>
          <div className="mt-3 space-y-2">
            {rl.slice(0,5).map(r => (
              <div key={r.id} className="flex justify-between text-sm border-b border-neutral-50 pb-2">
                <span className="font-medium text-neutral-800">{r.template_title}</span>
                <span className="text-xs text-neutral-500">{r.respondent_name} · {formatDate(r.submitted_at)}</span>
              </div>
            ))}
            {rl.length === 0 && <p className="text-sm text-neutral-500">No responses yet.</p>}
          </div>
        </section>
      </div>
    </div>
  );
}

// ── Templates Tab ──
function TemplatesTab() {
  const perms = useFormsPerms();
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [activeSectionKey, setActiveSectionKey] = useState<string>("");
  const [schema, setSchema] = useState<BuilderSchema>(emptySchema());
  const [questionLogicDrafts, setQuestionLogicDrafts] = useState<Record<string, { value: string; target_key: string; action: KoboLogicRule["action"] }>>({});
  const [logicRules, setLogicRules] = useState<KoboLogicRule[]>([]);
  const [form, setForm] = useState({
    title: "",
    description: "",
    purpose: "general_data_collection",
    target_respondent_type: "inspector",
    primary_module: "general",
    default_context_type: "",
    language: "en",
    allow_offline: false,
  });

  const { data: templates, isLoading } = useQuery({ queryKey: ["form-templates"], queryFn: async () => fetchFormTemplates() });
  const items = Array.isArray(templates) ? templates : [];
  const selected = items.find((item) => item.id === selectedId) ?? null;
  const { data: versions } = useQuery({
    queryKey: ["form-template-versions", selectedId],
    queryFn: async () => selectedId ? fetchFormTemplateVersions(selectedId) : [],
    enabled: Boolean(selectedId),
  });
  const latestVersion = Array.isArray(versions) && versions.length > 0 ? versions[0] : null;
  const activeSection = schema.sections.find((section) => section.key === activeSectionKey) ?? schema.sections[0] ?? null;

  useEffect(() => {
    if (!selectedId) return;
    const next = schemaFromVersion(latestVersion?.schema_json);
    setSchema(next);
    setLogicRules(Array.isArray(latestVersion?.logic_json?.rules) ? latestVersion.logic_json.rules as KoboLogicRule[] : []);
    setActiveSectionKey(next.sections[0]?.key || "");
  }, [selectedId, latestVersion?.id, latestVersion?.schema_json, latestVersion?.logic_json]);

  const createMut = useMutation({
    mutationFn: () => createFormTemplate({
      title: form.title,
      description: form.description,
      purpose: form.purpose,
      target_respondent_type: form.target_respondent_type,
      primary_module: form.primary_module,
      default_context_type: form.default_context_type,
      language: form.language,
      settings_json: { allow_offline: form.allow_offline },
    }),
    onSuccess: (created) => {
      setShowForm(false);
      setSelectedId(created.id);
      setSchema(emptySchema());
      setActiveSectionKey("");
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["form-templates"] });
    },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to create template.")),
  });
  const updateMut = useMutation({
    mutationFn: () => selected ? updateFormTemplate(selected.id, {
      title: form.title,
      description: form.description,
      purpose: form.purpose,
      target_respondent_type: form.target_respondent_type,
      primary_module: form.primary_module,
      default_context_type: form.default_context_type,
      language: form.language,
      settings_json: { allow_offline: form.allow_offline },
    }) : Promise.reject(new Error("Select a template first.")),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["form-templates"] });
    },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to save template details.")),
  });
  const saveDraftMut = useMutation({
    mutationFn: () => selected ? saveFormTemplateDraft(selected.id, {
      schema_json: schema,
      logic_json: { rules: logicRules },
      settings_json: { allow_offline: form.allow_offline },
    }) : Promise.reject(new Error("Select a template first.")),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["form-template-versions", selectedId] });
    },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to save draft schema.")),
  });
  const publishMut = useMutation({
    mutationFn: (id: string) => publishFormTemplate(id, {
      schema_json: schema.sections.length ? schema : latestVersion?.schema_json,
      logic_json: { rules: logicRules },
      settings_json: { allow_offline: form.allow_offline },
    }),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["form-templates"] });
      queryClient.invalidateQueries({ queryKey: ["form-template-versions", selectedId] });
    },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to publish template.")),
  });
  const archiveMut = useMutation({
    mutationFn: (id: string) => archiveFormTemplate(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["form-templates"] }),
  });

  function selectTemplate(template: FormTemplate) {
    setSelectedId(template.id);
    setForm({
      title: template.title,
      description: template.description || "",
      purpose: template.purpose,
      target_respondent_type: template.target_respondent_type || "inspector",
      primary_module: template.primary_module || template.module_context || "general",
      default_context_type: template.default_context_type || "",
      language: template.language || "en",
      allow_offline: Boolean(template.settings_json?.allow_offline),
    });
    setSchema(emptySchema());
    setActiveSectionKey("");
    setError(null);
  }

  function loadLatestVersion() {
    const next = schemaFromVersion(latestVersion?.schema_json);
    setSchema(next);
    setLogicRules(Array.isArray(latestVersion?.logic_json?.rules) ? latestVersion.logic_json.rules as KoboLogicRule[] : []);
    setActiveSectionKey(next.sections[0]?.key || "");
  }

  const questionOptions = schema.sections.flatMap((section) => section.questions.map((question) => ({ key: question.key, label: `${section.title}: ${question.label}` })));

  function addCanvasSection() {
    const sectionNumber = schema.sections.length + 1;
    const key = `section_${sectionNumber}`;
    const uniqueKey = schema.sections.some((section) => section.key === key) ? `${key}_${sectionNumber}` : key;
    setSchema((current) => ({ ...current, sections: [...current.sections, { key: uniqueKey, title: "", description: "", questions: [] }] }));
    setActiveSectionKey(uniqueKey);
  }

  function removeSection(key: string) {
    setSchema((current) => ({ ...current, sections: current.sections.filter((section) => section.key !== key) }));
    if (activeSectionKey === key) setActiveSectionKey("");
  }

  function updateSection(key: string, updates: Partial<BuilderSection>) {
    setSchema((current) => ({
      ...current,
      sections: current.sections.map((section) => section.key === key ? { ...section, ...updates } : section),
    }));
  }

  function addBlankQuestion() {
    const section = activeSection || schema.sections[0];
    if (!section) {
      const sectionKey = "section_1";
      setSchema({ sections: [{ key: sectionKey, title: "", description: "", questions: [{ key: "question_1", label: "", type: "short_text", required: false, help_text: "", options: [], questions: [], validation: {} }] }] });
      setActiveSectionKey(sectionKey);
      return;
    }
    const key = `question_${section.questions.length + 1}`;
    const uniqueKey = section.questions.some((question) => question.key === key) ? `${key}_${section.questions.length + 1}` : key;
    setSchema((current) => ({
      ...current,
      sections: current.sections.map((item) => item.key === section.key ? {
        ...item,
        questions: [...item.questions, { key: uniqueKey, label: "", type: "short_text", required: false, help_text: "", options: [], questions: [], validation: {} }],
      } : item),
    }));
    setActiveSectionKey(section.key);
  }

  function addRepeatGroup() {
    const section = activeSection || schema.sections[0];
    if (!section) {
      const sectionKey = "section_1";
      setSchema({ sections: [{ key: sectionKey, title: "", description: "", questions: [{ key: "group_1", label: "", type: "repeat_group", required: false, help_text: "", options: [], questions: [], validation: {} }] }] });
      setActiveSectionKey(sectionKey);
      return;
    }
    const key = `group_${section.questions.length + 1}`;
    const uniqueKey = section.questions.some((question) => question.key === key) ? `${key}_${section.questions.length + 1}` : key;
    setSchema((current) => ({
      ...current,
      sections: current.sections.map((item) => item.key === section.key ? {
        ...item,
        questions: [...item.questions, { key: uniqueKey, label: "", type: "repeat_group", required: false, help_text: "", options: [], questions: [], validation: {} }],
      } : item),
    }));
    setActiveSectionKey(section.key);
  }


  function removeQuestion(sectionKey: string, questionKey: string) {
    setSchema((current) => ({
      ...current,
      sections: current.sections.map((section) => section.key === sectionKey ? { ...section, questions: section.questions.filter((question) => question.key !== questionKey) } : section),
    }));
  }

  function updateQuestion(sectionKey: string, questionKey: string, updates: Partial<BuilderQuestion>) {
    setSchema((current) => ({
      ...current,
      sections: current.sections.map((section) => section.key === sectionKey ? {
        ...section,
        questions: section.questions.map((question) => question.key === questionKey ? { ...question, ...updates } : question),
      } : section),
    }));
  }

  function updateQuestionOption(sectionKey: string, questionKey: string, optionIndex: number, value: string) {
    setSchema((current) => ({
      ...current,
      sections: current.sections.map((section) => section.key === sectionKey ? {
        ...section,
        questions: section.questions.map((question) => question.key === questionKey ? {
          ...question,
          options: (question.options || []).map((option, index) => index === optionIndex ? value : option),
        } : question),
      } : section),
    }));
  }

  function addQuestionOption(sectionKey: string, questionKey: string) {
    setSchema((current) => ({
      ...current,
      sections: current.sections.map((section) => section.key === sectionKey ? {
        ...section,
        questions: section.questions.map((question) => question.key === questionKey ? {
          ...question,
          options: [...(question.options || []), ""],
        } : question),
      } : section),
    }));
  }

  function removeQuestionOption(sectionKey: string, questionKey: string, optionIndex: number) {
    setSchema((current) => ({
      ...current,
      sections: current.sections.map((section) => section.key === sectionKey ? {
        ...section,
        questions: section.questions.map((question) => question.key === questionKey ? {
          ...question,
          options: (question.options || []).filter((_, index) => index !== optionIndex),
        } : question),
      } : section),
    }));
  }

  function addNestedGroupQuestion(sectionKey: string, groupKey: string) {
    setSchema((current) => ({
      ...current,
      sections: current.sections.map((section) => section.key === sectionKey ? {
        ...section,
        questions: section.questions.map((question) => {
          if (question.key !== groupKey) return question;
          const questions = question.questions || [];
          const key = `field_${questions.length + 1}`;
          const uniqueKey = questions.some((item) => item.key === key) ? `${key}_${questions.length + 1}` : key;
          return {
            ...question,
            questions: [...questions, { key: uniqueKey, label: "", type: "short_text", required: false, help_text: "", options: [], questions: [], validation: {} }],
          };
        }),
      } : section),
    }));
  }

  function updateNestedGroupQuestion(sectionKey: string, groupKey: string, nestedKey: string, updates: Partial<BuilderQuestion>) {
    setSchema((current) => ({
      ...current,
      sections: current.sections.map((section) => section.key === sectionKey ? {
        ...section,
        questions: section.questions.map((question) => question.key === groupKey ? {
          ...question,
          questions: (question.questions || []).map((nested) => nested.key === nestedKey ? { ...nested, ...updates } : nested),
        } : question),
      } : section),
    }));
  }

  function removeNestedGroupQuestion(sectionKey: string, groupKey: string, nestedKey: string) {
    setSchema((current) => ({
      ...current,
      sections: current.sections.map((section) => section.key === sectionKey ? {
        ...section,
        questions: section.questions.map((question) => question.key === groupKey ? {
          ...question,
          questions: (question.questions || []).filter((nested) => nested.key !== nestedKey),
        } : question),
      } : section),
    }));
  }

  function addQuestionLogicRule(question: BuilderQuestion) {
    const draft = questionLogicDrafts[question.key];
    if (!draft?.value || !draft.target_key) return;
    const rule: KoboLogicRule = {
      target_type: "question",
      target_key: draft.target_key,
      action: draft.action || "show",
      match: "all",
      conditions: [{ question_key: question.key, operator: "equals", value: draft.value }],
    };
    setLogicRules((current) => [...current, rule]);
    setQuestionLogicDrafts((current) => ({ ...current, [question.key]: { value: "", target_key: "", action: "show" } }));
  }

  function duplicateQuestion(sectionKey: string, question: BuilderQuestion) {
    setSchema((current) => ({
      ...current,
      sections: current.sections.map((section) => {
        if (section.key !== sectionKey) return section;
        const baseKey = `${question.key}_copy`;
        const copyCount = section.questions.filter((item) => item.key.startsWith(baseKey)).length;
        return {
          ...section,
          questions: [
            ...section.questions,
            {
              ...question,
              key: copyCount ? `${baseKey}_${copyCount + 1}` : baseKey,
              label: `${question.label} copy`,
            },
          ],
        };
      }),
    }));
  }

  return (
    <div className="-mx-6 -mt-6 bg-neutral-50 px-6 pb-8">
      <div className="sticky top-0 z-10 -mx-6 border-b border-neutral-200 bg-white/95 px-6 py-4 backdrop-blur">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="min-w-0">
            <div className="flex items-center gap-3">
              <select
                className="h-10 max-w-[420px] rounded border border-transparent bg-white px-0 text-lg font-semibold text-neutral-900 outline-none hover:border-neutral-200 hover:px-3"
                onChange={(event) => {
                  const template = items.find((item) => item.id === event.target.value);
                  if (template) selectTemplate(template);
                }}
                value={selected?.id || ""}
              >
                <option value="">{isLoading ? "Loading templates..." : "Select a form template"}</option>
                {items.map((template) => <option key={template.id} value={template.id}>{template.title}</option>)}
              </select>
              {selected ? <StatusBadge status={selected.status} /> : null}
            </div>
            <p className="mt-1 text-sm text-neutral-500">Build questions, manage sections, preview respondent flow, then save or publish.</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {perms.has("forms.template.create") ? <button className="inline-flex h-10 items-center gap-2 rounded-full border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700 shadow-sm hover:bg-neutral-50" onClick={() => setShowForm(true)} type="button"><Plus size={16} />New</button> : null}
            <button className="inline-flex h-10 items-center gap-2 rounded-full border border-neutral-200 bg-white px-4 text-sm font-semibold text-brand-700 shadow-sm hover:bg-brand-50 disabled:opacity-50" disabled={!selected || updateMut.isPending || saveDraftMut.isPending} onClick={() => { updateMut.mutate(); saveDraftMut.mutate(); }} type="button"><Save size={16} />Save</button>
            {perms.has("forms.template.publish") ? <button className="inline-flex h-10 items-center gap-2 rounded-full bg-brand-600 px-5 text-sm font-semibold text-white shadow-sm hover:bg-brand-700 disabled:opacity-50" disabled={!selected || selected.status !== "draft" || !schema.sections.length || publishMut.isPending} onClick={() => selected && publishMut.mutate(selected.id)} type="button"><BadgeCheck size={16} />Publish</button> : null}
          </div>
        </div>
      </div>

      {showForm && (
        <div className="mt-6 space-y-3 rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-bold text-neutral-900">New Template</h3>
          {error && <p className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</p>}
          <div className="grid gap-3 lg:grid-cols-2">
            <input className="h-10 w-full rounded border border-neutral-200 px-3 text-sm" placeholder="Template title" value={form.title} onChange={e => setForm(p => ({...p, title: e.target.value}))} />
            <select className="h-10 w-full rounded border border-neutral-200 px-3 text-sm" value={form.purpose} onChange={e => setForm(p => ({...p, purpose: e.target.value}))}>{Object.entries(PURPOSE_LABELS).map(([k,v]) => <option key={k} value={k}>{v}</option>)}</select>
            <select className="h-10 w-full rounded border border-neutral-200 px-3 text-sm" value={form.primary_module} onChange={e => setForm(p => ({...p, primary_module: e.target.value}))}>{Object.entries(MODULE_LABELS).map(([k,v]) => <option key={k} value={k}>{v}</option>)}</select>
            <select className="h-10 w-full rounded border border-neutral-200 px-3 text-sm" value={form.target_respondent_type} onChange={e => setForm(p => ({...p, target_respondent_type: e.target.value}))}>{Object.entries(RESPONDENT_LABELS).map(([k,v]) => <option key={k} value={k}>{v}</option>)}</select>
          </div>
          <textarea className="w-full rounded border border-neutral-200 px-3 py-2 text-sm" rows={2} placeholder="Description" value={form.description} onChange={e => setForm(p => ({...p, description: e.target.value}))} />
          <div className="flex gap-2">
            <button className="h-10 rounded-full bg-brand-600 px-5 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-60" disabled={!form.title || createMut.isPending} onClick={() => createMut.mutate()} type="button">{createMut.isPending ? "Creating..." : "Create"}</button>
            <button className="h-10 rounded-full border border-neutral-200 px-5 text-sm font-semibold text-neutral-700 hover:bg-neutral-50" onClick={() => setShowForm(false)} type="button">Cancel</button>
          </div>
        </div>
      )}

      {error && !showForm ? <p className="mt-6 rounded border border-danger-100 bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</p> : null}

      {!selected ? (
        <div className="mt-6 rounded-lg border border-dashed border-neutral-300 bg-white p-10 text-center">
          <h3 className="text-base font-bold text-neutral-900">Choose a template to start building</h3>
          <p className="mt-2 text-sm text-neutral-500">Existing templates will open into the question canvas. New templates can be created from the top-right button.</p>
          <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {items.map((template) => (
              <button className="rounded border border-neutral-200 p-4 text-left hover:border-brand-200 hover:bg-brand-50" key={template.id} onClick={() => selectTemplate(template)} type="button">
                <span className="block font-bold text-neutral-900">{template.title}</span>
                <span className="mt-1 block text-xs text-neutral-500">{PURPOSE_LABELS[template.purpose] ?? template.purpose}</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="mt-8 grid gap-8 xl:grid-cols-[minmax(0,1fr)_360px]">
          <main className="space-y-4">
            {activeSection ? (
              <section className="overflow-hidden rounded-lg bg-white shadow-sm">
                <div className="flex items-center justify-between bg-[#c9ead7] px-4 py-3">
                  <p className="text-sm font-bold text-neutral-900">Section {schema.sections.findIndex((section) => section.key === activeSection.key) + 1}</p>
                  <div className="flex items-center gap-3 text-xs font-semibold text-neutral-700">
                    <button className="inline-flex items-center gap-1 hover:text-neutral-900" type="button">Collapse <ChevronUp size={14} /></button>
                    <Grip size={15} className="text-neutral-400" />
                  </div>
                </div>
                <div className="p-5">
                  <input className="w-full border-0 bg-transparent p-0 text-xl font-bold text-neutral-900 outline-none placeholder:text-neutral-300" placeholder="Section Name" value={activeSection.title} onChange={(event) => updateSection(activeSection.key, { title: event.target.value })} />
                  <textarea className="mt-3 min-h-16 w-full resize-none rounded border border-transparent bg-transparent p-0 text-sm text-neutral-700 outline-none placeholder:text-slate-400 hover:border-neutral-200 hover:bg-white hover:p-3 focus:border-brand-200 focus:bg-white focus:p-3" placeholder="Description" value={activeSection.description || ""} onChange={(event) => updateSection(activeSection.key, { description: event.target.value })} />
                </div>
              </section>
            ) : (
              <section className="rounded-lg border border-dashed border-neutral-300 bg-white p-10 text-center text-sm text-neutral-500">Add a section from the canvas below to begin.</section>
            )}

            {activeSection?.questions.map((question, index) => {
              const QuestionIcon = QUESTION_TYPES.find((type) => type.value === question.type)?.icon ?? Type;
              return (
                <section className="rounded-lg bg-white p-5 shadow-sm" key={question.key}>
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2 text-sm font-semibold text-slate-400">
                      <Grip size={15} />
                      <span>Question {index + 1}</span>
                    </div>
                    <div className="flex items-center gap-2 text-neutral-600">
                      <ChevronUp size={15} />
                      <ChevronDown size={15} />
                    </div>
                  </div>
                  <div className="mt-5 grid gap-2 lg:grid-cols-[minmax(0,1fr)_280px]">
                    <div className="flex h-14 items-center gap-3 rounded-lg border border-neutral-200 px-4 focus-within:border-brand-300 focus-within:ring-2 focus-within:ring-brand-100">
                      <QuestionIcon size={17} className="shrink-0 text-brand-600" />
                      <input className="min-w-0 flex-1 border-0 bg-transparent p-0 text-sm font-medium text-neutral-900 outline-none placeholder:text-slate-400" placeholder="Type question here" value={question.label} onChange={(event) => updateQuestion(activeSection.key, question.key, { label: event.target.value })} />
                    </div>
                    <select className="h-14 rounded-lg border border-neutral-200 px-4 text-sm font-medium text-neutral-900 outline-none focus:border-brand-300 focus:ring-2 focus:ring-brand-100" value={question.type} onChange={(event) => updateQuestion(activeSection.key, question.key, { type: event.target.value as KoboQuestionType })}>
                      {QUESTION_TYPES.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
                    </select>
                  </div>
                  <input className="mt-3 h-10 w-full rounded-lg border border-neutral-200 px-4 text-sm text-neutral-600 outline-none focus:border-brand-300 focus:ring-2 focus:ring-brand-100" placeholder="Add helper text (optional)" value={question.help_text || ""} onChange={(event) => updateQuestion(activeSection.key, question.key, { help_text: event.target.value })} />
                  {OPTION_QUESTION_TYPES.includes(question.type) ? (
                    <div className="mt-6 space-y-3">
                      {(question.options?.length ? question.options : [""]).map((option, optionIndex) => (
                        <div className="flex items-center gap-3" key={`${question.key}-option-${optionIndex}`}>
                          <Grip size={15} className="text-neutral-300" />
                          <div className="grid min-w-0 flex-1 grid-cols-[40px_minmax(0,1fr)_44px] overflow-hidden rounded-lg border border-neutral-200 bg-white">
                            <span className="flex items-center justify-center border-r border-neutral-200 text-sm text-slate-400">{optionIndex + 1}</span>
                            <input className="h-12 min-w-0 border-0 px-4 text-sm outline-none" placeholder={`Option ${optionIndex + 1}`} value={option} onChange={(event) => updateQuestionOption(activeSection.key, question.key, optionIndex, event.target.value)} />
                            <button className="flex items-center justify-center text-slate-400 hover:text-danger-700" onClick={() => removeQuestionOption(activeSection.key, question.key, optionIndex)} type="button">x</button>
                          </div>
                        </div>
                      ))}
                      <button className="ml-7 flex h-12 w-[calc(100%-1.75rem)] items-center gap-3 rounded-lg border border-dashed border-neutral-300 px-4 text-sm font-medium text-neutral-500 hover:border-brand-300 hover:text-brand-700" onClick={() => addQuestionOption(activeSection.key, question.key)} type="button"><Plus size={15} /> Add option</button>
                    </div>
                  ) : null}
                  {question.type === "repeat_group" ? (
                    <div className="mt-5 rounded-lg border border-brand-100 bg-brand-50/40 p-4">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div>
                          <p className="text-sm font-bold text-brand-800">Repeating Group</p>
                          <p className="mt-1 text-xs text-neutral-500">Fields added here repeat together for each item the respondent enters.</p>
                        </div>
                        <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-brand-700">{question.questions?.length || 0} group fields</span>
                      </div>
                      <div className="mt-4 space-y-3">
                        {(question.questions || []).map((nested, nestedIndex) => (
                          <div className="rounded-lg border border-neutral-200 bg-white p-3" key={nested.key}>
                            <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
                              <Grip size={14} />
                              <span>Group field {nestedIndex + 1}</span>
                            </div>
                            <div className="mt-3 grid gap-2 lg:grid-cols-[minmax(0,1fr)_220px_auto]">
                              <input className="h-11 rounded border border-neutral-200 px-3 text-sm outline-none focus:border-brand-300 focus:ring-2 focus:ring-brand-100" placeholder="Field label" value={nested.label} onChange={(event) => updateNestedGroupQuestion(activeSection.key, question.key, nested.key, { label: event.target.value })} />
                              <select className="h-11 rounded border border-neutral-200 px-3 text-sm outline-none focus:border-brand-300 focus:ring-2 focus:ring-brand-100" value={nested.type} onChange={(event) => updateNestedGroupQuestion(activeSection.key, question.key, nested.key, { type: event.target.value as KoboQuestionType })}>
                                {QUESTION_TYPES.filter((type) => type.value !== "repeat_group").map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
                              </select>
                              <button className="inline-flex h-11 w-11 items-center justify-center rounded border border-neutral-200 text-neutral-400 hover:text-danger-700" onClick={() => removeNestedGroupQuestion(activeSection.key, question.key, nested.key)} title="Delete group field" type="button"><Trash2 size={15} /></button>
                            </div>
                            <input className="mt-2 h-10 w-full rounded border border-neutral-200 px-3 text-sm outline-none focus:border-brand-300 focus:ring-2 focus:ring-brand-100" placeholder="Helper text (optional)" value={nested.help_text || ""} onChange={(event) => updateNestedGroupQuestion(activeSection.key, question.key, nested.key, { help_text: event.target.value })} />
                            <label className="mt-3 inline-flex items-center gap-2 text-xs font-medium text-neutral-500">Required<input className="accent-brand-600" checked={nested.required} onChange={(event) => updateNestedGroupQuestion(activeSection.key, question.key, nested.key, { required: event.target.checked })} type="checkbox" /></label>
                          </div>
                        ))}
                        <button className="flex h-12 w-full items-center justify-center gap-2 rounded-lg border border-dashed border-brand-300 bg-white text-sm font-semibold text-brand-700 hover:bg-brand-50" onClick={() => addNestedGroupQuestion(activeSection.key, question.key)} type="button"><Plus size={15} /> Add group field</button>
                      </div>
                    </div>
                  ) : null}
                  {BRANCHING_QUESTION_TYPES.includes(question.type) ? (
                    <div className="mt-5 rounded-lg border border-neutral-200 bg-neutral-50 p-4">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <p className="text-xs font-bold uppercase text-neutral-500">Skip logic</p>
                        <span className="text-xs text-neutral-400">{logicRules.filter((rule) => rule.conditions[0]?.question_key === question.key).length} rules</span>
                      </div>
                      <div className="mt-3 grid gap-2 lg:grid-cols-[minmax(0,1fr)_150px_minmax(0,1fr)_auto]">
                        <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={questionLogicDrafts[question.key]?.value || ""} onChange={(event) => setQuestionLogicDrafts((current) => ({ ...current, [question.key]: { value: event.target.value, target_key: current[question.key]?.target_key || "", action: current[question.key]?.action || "show" } }))}>
                          <option value="">When answer is...</option>
                          {(question.options || ["Yes", "No"]).map((option) => <option key={option} value={option}>{option}</option>)}
                        </select>
                        <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={questionLogicDrafts[question.key]?.action || "show" as KoboLogicRule["action"]} onChange={(event) => setQuestionLogicDrafts((current) => ({ ...current, [question.key]: { value: current[question.key]?.value || "", target_key: current[question.key]?.target_key || "", action: event.target.value as KoboLogicRule["action"] } }))}>
                          <option value="show">Show</option>
                          <option value="hide">Hide</option>
                          <option value="require">Require</option>
                        </select>
                        <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={questionLogicDrafts[question.key]?.target_key || ""} onChange={(event) => setQuestionLogicDrafts((current) => ({ ...current, [question.key]: { value: current[question.key]?.value || "", target_key: event.target.value, action: current[question.key]?.action || "show" } }))}>
                          <option value="">Target question</option>
                          {questionOptions.filter((target) => target.key !== question.key).map((target) => <option key={target.key} value={target.key}>{target.label}</option>)}
                        </select>
                        <button className="h-10 rounded-full border border-brand-200 px-4 text-xs font-bold text-brand-700 disabled:opacity-50" disabled={!questionLogicDrafts[question.key]?.value || !questionLogicDrafts[question.key]?.target_key} onClick={() => addQuestionLogicRule(question)} type="button">Add</button>
                      </div>
                      {logicRules.filter((rule) => rule.conditions[0]?.question_key === question.key).map((rule, ruleIndex) => (
                        <div className="mt-2 rounded border border-neutral-200 bg-white px-3 py-2 text-xs text-neutral-600" key={`${question.key}-logic-${ruleIndex}`}>
                          If answer is <b>{String(rule.conditions[0]?.value ?? "")}</b>, {rule.action} <b>{rule.target_key}</b>
                        </div>
                      ))}
                    </div>
                  ) : null}
                  <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-neutral-200 pt-4">
                    <button className="inline-flex items-center gap-2 text-sm font-medium text-neutral-800 hover:text-brand-700" type="button"><Upload size={15} /> Add Image</button>
                    <div className="flex flex-wrap items-center gap-4 text-xs font-medium text-neutral-400">
                      {BRANCHING_QUESTION_TYPES.includes(question.type) ? <span>Skip logic</span> : null}
                      {question.type === "repeat_group" ? <span className="font-semibold text-brand-700">Repeating group</span> : null}
                      <label className="inline-flex items-center gap-2">Required<input className="accent-brand-600" checked={question.required} onChange={(event) => updateQuestion(activeSection.key, question.key, { required: event.target.checked })} type="checkbox" /></label>
                      <button className="text-neutral-500 hover:text-brand-700" onClick={() => duplicateQuestion(activeSection.key, question)} title="Duplicate question" type="button"><Copy size={15} /></button>
                      <button className="text-neutral-500 hover:text-danger-700" onClick={() => removeQuestion(activeSection.key, question.key)} title="Delete question" type="button"><Trash2 size={15} /></button>
                    </div>
                  </div>
                </section>
              );
            })}

            <div className="grid overflow-hidden rounded-lg border border-dashed border-brand-400 bg-brand-50/40 text-brand-700 md:grid-cols-3">
              <button className="inline-flex h-14 items-center justify-center gap-2 border-b border-dashed border-brand-300 text-sm font-semibold hover:bg-brand-50 md:border-b-0 md:border-r" onClick={addCanvasSection} type="button"><ListPlus size={16} /> Add Section</button>
              <button className="inline-flex h-14 items-center justify-center gap-2 border-b border-dashed border-brand-300 text-sm font-semibold hover:bg-brand-50 md:border-b-0 md:border-r" onClick={addBlankQuestion} type="button"><Plus size={16} /> Add Question</button>
              <button className="inline-flex h-14 items-center justify-center gap-2 text-sm font-semibold hover:bg-brand-50" onClick={addRepeatGroup} type="button"><ListPlus size={16} /> Add Repeating Group</button>
            </div>
          </main>

          <aside className="space-y-4 xl:sticky xl:top-24 xl:self-start">
            <section className="rounded-lg bg-white p-4 shadow-sm">
              <h3 className="text-sm font-bold text-neutral-900">Sections</h3>
              <div className="mt-4 space-y-3">
                {schema.sections.map((section, index) => (
                  <button className={`flex w-full items-center gap-3 rounded-lg border p-3 text-left text-sm ${activeSection?.key === section.key ? "border-brand-200 bg-brand-50" : "border-neutral-200 bg-neutral-50 hover:bg-white"}`} key={section.key} onClick={() => setActiveSectionKey(section.key)} type="button">
                    <Grip size={15} className="text-neutral-400" />
                    <span className="min-w-0 flex-1 font-medium text-neutral-900">{section.title || `Section ${index + 1}`}</span>
                    <span className="text-xs text-neutral-400">{section.questions.length}</span>
                    <span className="text-neutral-400 hover:text-danger-700" onClick={(event) => { event.stopPropagation(); removeSection(section.key); }} title="Remove section"><Trash2 size={13} /></span>
                  </button>
                ))}
                <button className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg border border-dashed border-brand-300 bg-brand-50/50 text-sm font-semibold text-brand-700 hover:bg-brand-50" onClick={addCanvasSection} type="button"><ListPlus size={15} /> Add Section</button>
              </div>
            </section>

            <section className="rounded-lg bg-white p-4 shadow-sm">
              <h3 className="text-sm font-bold text-neutral-900">Form Information</h3>
              <div className="mt-4 border-b border-neutral-200">
                <span className="inline-flex border-b-2 border-brand-600 pb-2 text-sm font-semibold text-neutral-900">Overview</span>
              </div>
              <div className="mt-4 space-y-3">
                <input className="w-full border-0 bg-transparent p-0 text-base font-bold text-neutral-900 outline-none" value={form.title} onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))} />
                <textarea className="w-full resize-none rounded border border-neutral-200 px-3 py-2 text-sm text-neutral-700" rows={2} value={form.description} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} />
                <div className="rounded-lg bg-neutral-50 p-3">
                  <p className="font-medium text-neutral-900">{PURPOSE_LABELS[form.purpose] ?? form.purpose}</p>
                  <div className="mt-4 grid grid-cols-3 divide-x divide-neutral-200 text-center">
                    <div><p className="text-xs text-slate-400">Sections</p><p className="mt-1 font-bold text-neutral-900">{schema.sections.length}</p></div>
                    <div><p className="text-xs text-slate-400">Questions</p><p className="mt-1 font-bold text-neutral-900">{schema.sections.reduce((sum, section) => sum + section.questions.length, 0)}</p></div>
                    <div><p className="text-xs text-slate-400">Version</p><p className="mt-1 font-bold text-neutral-900">v{selected.current_version}</p></div>
                  </div>
                </div>
                <div className="grid gap-2">
                  <select className="h-10 rounded border border-neutral-200 px-3 text-sm" value={form.purpose} onChange={(event) => setForm((current) => ({ ...current, purpose: event.target.value }))}>{Object.entries(PURPOSE_LABELS).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select>
                  <select className="h-10 rounded border border-neutral-200 px-3 text-sm" value={form.primary_module} onChange={(event) => setForm((current) => ({ ...current, primary_module: event.target.value }))}>{Object.entries(MODULE_LABELS).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select>
                  <select className="h-10 rounded border border-neutral-200 px-3 text-sm" value={form.target_respondent_type} onChange={(event) => setForm((current) => ({ ...current, target_respondent_type: event.target.value }))}>{Object.entries(RESPONDENT_LABELS).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select>
                  <input className="h-10 rounded border border-neutral-200 px-3 text-sm" placeholder="Context type" value={form.default_context_type} onChange={(event) => setForm((current) => ({ ...current, default_context_type: event.target.value }))} />
                  <label className="inline-flex items-center gap-2 text-sm font-medium text-neutral-700"><input checked={form.allow_offline} onChange={(event) => setForm((current) => ({ ...current, allow_offline: event.target.checked }))} type="checkbox" /> Offline response support</label>
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  {latestVersion ? <button className="h-9 rounded-full border border-neutral-200 px-4 text-xs font-bold text-neutral-700 hover:bg-neutral-50" onClick={loadLatestVersion} type="button">Load saved</button> : null}
                  {selected.status === "published" ? <button className="h-9 rounded-full border border-neutral-200 px-4 text-xs font-bold text-neutral-700 hover:bg-neutral-50" disabled={archiveMut.isPending} onClick={() => archiveMut.mutate(selected.id)} type="button">Archive</button> : null}
                </div>
              </div>
            </section>

            <section className="rounded-lg bg-white p-4 shadow-sm">
              <div className="mb-3 flex items-center gap-2"><Eye size={15} className="text-neutral-500" /><h3 className="text-sm font-bold text-neutral-900">Preview</h3></div>
              {schema.sections.length === 0 ? <p className="text-sm text-neutral-500">No sections to preview.</p> : <KoboFormRenderer schema={schema} values={{}} logic={{ rules: logicRules }} readOnly />}
            </section>
          </aside>
        </div>
      )}
    </div>
  );
}

// ── Assignments Tab ──
function AssignmentsTab() {
  const perms = useFormsPerms();
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedAssignmentId, setSelectedAssignmentId] = useState<string | null>(null);
  const [form, setForm] = useState({ title: "", template: "", purpose: "general_data_collection", assigned_to_type: "organization", due_date: "" });

  const { data: templates } = useQuery({ queryKey: ["form-templates"], queryFn: async () => fetchFormTemplates() });
  const { data: assignments, isLoading } = useQuery({ queryKey: ["form-assignments"], queryFn: async () => fetchFormAssignments() });
  const tl = Array.isArray(templates) ? templates : [];
  const al = Array.isArray(assignments) ? assignments : [];
  const selectedAssignment = selectedAssignmentId ? al.find((assignment) => assignment.id === selectedAssignmentId) ?? null : null;
  const { data: assignmentSummary } = useQuery({
    queryKey: ["form-assignment-summary", selectedAssignmentId],
    queryFn: async () => selectedAssignmentId ? fetchFormAssignmentSummary(selectedAssignmentId) : Promise.reject(new Error("Select an assignment.")),
    enabled: Boolean(selectedAssignmentId),
  });

  const createMut = useMutation({
    mutationFn: () => createFormAssignment({ ...form, assigned_to_id: "0" }),
    onSuccess: () => { setShowForm(false); setForm({ title: "", template: "", purpose: "general_data_collection", assigned_to_type: "organization", due_date: "" }); setError(null); queryClient.invalidateQueries({ queryKey: ["form-assignments"] }); },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to create assignment.")),
  });
  const cancelMut = useMutation({
    mutationFn: (id: string) => cancelFormAssignment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["form-assignments"] });
      queryClient.invalidateQueries({ queryKey: ["form-assignment-summary", selectedAssignmentId] });
    },
  });
  const reminderMut = useMutation({
    mutationFn: (id: string) => sendFormAssignmentReminder(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["form-assignments"] });
      queryClient.invalidateQueries({ queryKey: ["form-assignment-summary", selectedAssignmentId] });
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        {perms.has("forms.assignment.create") ? <button className="inline-flex h-10 items-center gap-2 rounded-lg bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700" onClick={() => setShowForm(true)} type="button"><Plus size={16} />Create Assignment</button> : null}
      </div>

      {showForm && (
        <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm space-y-3">
          <h3 className="text-sm font-bold text-neutral-900">New Assignment</h3>
          {error && <p className="text-sm font-semibold text-danger-700 bg-danger-50 rounded px-3 py-2">{error}</p>}
          <input className="h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm" placeholder="Assignment title" value={form.title} onChange={e => setForm(p => ({...p, title: e.target.value}))} />
          <select className="h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm" value={form.template} onChange={e => setForm(p => ({...p, template: e.target.value, purpose: tl.find(t=>t.id===e.target.value)?.purpose || p.purpose}))}>
            <option value="">Select template</option>
            {tl.filter(t => t.status==="published").map(t => <option key={t.id} value={t.id}>{t.title} (v{t.current_version})</option>)}
          </select>
          <select className="h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm" value={form.purpose} onChange={e => setForm(p => ({...p, purpose: e.target.value}))}>
            {Object.entries(PURPOSE_LABELS).map(([k,v]) => <option key={k} value={k}>{v}</option>)}
          </select>
          <div className="flex gap-2">
            <button className="h-10 rounded-lg bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60" disabled={!form.title || !form.template || createMut.isPending} onClick={() => createMut.mutate()} type="button">{createMut.isPending ? "Creating..." : "Save"}</button>
            <button className="h-10 rounded-lg border border-neutral-200 px-4 text-sm font-medium text-neutral-700 hover:bg-neutral-50" onClick={() => setShowForm(false)} type="button">Cancel</button>
          </div>
        </div>
      )}

      <section className="overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-neutral-200 text-sm">
          <thead className="bg-neutral-50"><tr>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Title</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Template</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Due</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Responses</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Status</th>
            <th className="px-4 py-3 text-right text-xs font-medium uppercase text-neutral-500">Actions</th>
          </tr></thead>
          <tbody className="divide-y divide-neutral-100">
            {isLoading ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={6}>Loading...</td></tr>
            : al.length === 0 ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={6}>No assignments yet.</td></tr>
            : al.map(a => (
              <tr key={a.id} className="hover:bg-neutral-50">
                <td className="px-4 py-3 font-semibold text-neutral-900">{a.title}</td>
                <td className="px-4 py-3 text-neutral-700">{a.template_title}</td>
                <td className="px-4 py-3 text-neutral-500 text-xs">{formatDate(a.due_date)}</td>
                <td className="px-4 py-3 text-neutral-700">
                  <div className="min-w-32">
                    <div className="flex justify-between text-xs text-neutral-600"><span>{a.response_count}/{a.total_recipients || a.response_count}</span><span>{a.completion_rate || 0}%</span></div>
                    <div className="mt-1 h-2 overflow-hidden rounded bg-neutral-100"><span className="block h-full bg-brand-500" style={{ width: `${Math.min(a.completion_rate || 0, 100)}%` }} /></div>
                    {a.status_summary?.overdue ? <p className="mt-1 text-xs font-semibold text-danger-700">{a.status_summary.overdue} overdue</p> : null}
                  </div>
                </td>
                <td className="px-4 py-3"><StatusBadge status={a.status} /></td>
                <td className="px-4 py-3 text-right space-x-1">
                  <button className="h-8 rounded border border-brand-200 px-3 text-xs font-bold text-brand-700 hover:bg-brand-50" onClick={() => setSelectedAssignmentId(a.id)} type="button">Track</button>
                  <button className="h-8 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700 hover:bg-neutral-50 disabled:opacity-50" disabled={reminderMut.isPending} onClick={() => reminderMut.mutate(a.id)} type="button">Reminder</button>
                  {(a.status === "active" || a.status === "in_progress") && <button className="h-8 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700 hover:bg-neutral-50" onClick={() => cancelMut.mutate(a.id)} type="button">Cancel</button>}
                </td>
              </tr>
            ))}</tbody>
        </table>
      </section>

      {(assignmentSummary || selectedAssignment) ? (
        <section className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-xs font-bold uppercase text-neutral-500">Assignment Dashboard</p>
              <h3 className="mt-1 text-base font-bold text-neutral-900">{assignmentSummary?.title || selectedAssignment?.title}</h3>
            </div>
            <StatusBadge status={assignmentSummary?.status || selectedAssignment?.status || "loading"} />
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {[
              ["Recipients", assignmentSummary?.status_summary?.total_recipients ?? selectedAssignment?.total_recipients ?? 0],
              ["Submitted", assignmentSummary?.status_summary?.submitted ?? selectedAssignment?.status_summary?.submitted ?? 0],
              ["Reviewed", assignmentSummary?.status_summary?.reviewed ?? selectedAssignment?.status_summary?.reviewed ?? 0],
              ["Overdue", assignmentSummary?.status_summary?.overdue ?? selectedAssignment?.status_summary?.overdue ?? 0],
            ].map(([label, value]) => (
              <div className="rounded border border-neutral-200 bg-neutral-50 p-3" key={label}>
                <p className="text-xs font-bold uppercase text-neutral-500">{label}</p>
                <p className="mt-1 text-2xl font-bold text-neutral-900">{value}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 grid gap-4 lg:grid-cols-2">
            <div>
              <p className="text-xs font-bold uppercase text-neutral-500">Recipients</p>
              <div className="mt-2 max-h-56 overflow-auto rounded border border-neutral-200">
                {(assignmentSummary?.recipients || []).length ? assignmentSummary?.recipients.map((recipient) => (
                  <div className="flex items-center justify-between border-b border-neutral-100 px-3 py-2 text-sm last:border-0" key={recipient.id}>
                    <span className="font-medium text-neutral-800">{recipient.organization_name || recipient.recipient_id}</span>
                    <StatusBadge status={recipient.status} />
                  </div>
                )) : <p className="p-3 text-sm text-neutral-500">No recipient records yet.</p>}
              </div>
            </div>
            <div>
              <p className="text-xs font-bold uppercase text-neutral-500">Responses</p>
              <div className="mt-2 max-h-56 overflow-auto rounded border border-neutral-200">
                {(assignmentSummary?.responses || []).length ? assignmentSummary?.responses.map((item) => (
                  <div className="flex items-center justify-between border-b border-neutral-100 px-3 py-2 text-sm last:border-0" key={item.id}>
                    <span>
                      <span className="block font-medium text-neutral-800">{item.respondent_name || item.respondent_email || "Respondent"}</span>
                      <span className="text-xs text-neutral-500">Saved {formatDate(item.last_saved_at)} · Submitted {formatDate(item.submitted_at)}</span>
                    </span>
                    <StatusBadge status={item.status} />
                  </div>
                )) : <p className="p-3 text-sm text-neutral-500">No response records yet.</p>}
              </div>
            </div>
          </div>
        </section>
      ) : null}
    </div>
  );
}

// ── Responses Tab ──
function ResponsesTab() {
  const perms = useFormsPerms();
  const queryClient = useQueryClient();
  const [selectedResponseId, setSelectedResponseId] = useState<string | null>(null);
  const { data: responses, isLoading } = useQuery({ queryKey: ["form-responses"], queryFn: async () => fetchFormResponses() });
  const items = Array.isArray(responses) ? responses : [];
  const { data: activity } = useQuery({
    queryKey: ["form-response-activity", selectedResponseId],
    queryFn: async () => selectedResponseId ? fetchFormResponseActivity(selectedResponseId) : Promise.reject(new Error("Select a response.")),
    enabled: Boolean(selectedResponseId),
  });

  const reviewMut = useMutation({
    mutationFn: ({ id, notes }: { id: string; notes?: string }) => reviewFormResponse(id, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["form-responses"] });
      queryClient.invalidateQueries({ queryKey: ["form-response-activity", selectedResponseId] });
    },
  });
  const returnMut = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) => returnFormResponse(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["form-responses"] });
      queryClient.invalidateQueries({ queryKey: ["form-response-activity", selectedResponseId] });
    },
  });

  return (
    <div className="space-y-4">
      <section className="overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-neutral-200 text-sm">
          <thead className="bg-neutral-50"><tr>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Form</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Assignment</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Respondent</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Submitted</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Sync</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Status</th>
            <th className="px-4 py-3 text-right text-xs font-medium uppercase text-neutral-500">Actions</th>
          </tr></thead>
          <tbody className="divide-y divide-neutral-100">
            {isLoading ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={7}>Loading...</td></tr>
            : items.length === 0 ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={7}>No responses yet.</td></tr>
            : items.map(r => (
              <tr key={r.id} className="hover:bg-neutral-50">
                <td className="px-4 py-3 font-semibold text-neutral-900">{r.template_title || r.template}</td>
                <td className="px-4 py-3 text-neutral-600 text-xs">{r.assignment_title}</td>
                <td className="px-4 py-3 text-neutral-700">{r.respondent_name || r.respondent_email}</td>
                <td className="px-4 py-3 text-neutral-500 text-xs">{formatDate(r.submitted_at)}</td>
                <td className="px-4 py-3"><StatusBadge status={r.sync_status || "online"} /></td>
                <td className="px-4 py-3"><StatusBadge status={r.status} /></td>
                <td className="px-4 py-3 text-right space-x-1">
                  <button className="h-8 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700 hover:bg-neutral-50" onClick={() => setSelectedResponseId(r.id)} type="button">Activity</button>
                  {r.status === "submitted" && perms.has("forms.response.review") && (
                    <>
                      <button className="h-8 rounded border border-brand-200 px-3 text-xs font-bold text-brand-700 hover:bg-brand-50 mr-1" onClick={() => reviewMut.mutate({ id: r.id })} type="button">Review</button>
                      <button className="h-8 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700 hover:bg-neutral-50" onClick={() => returnMut.mutate({ id: r.id })} type="button">Return</button>
                    </>
                  )}
                </td>
              </tr>
            ))}</tbody>
        </table>
      </section>
      {selectedResponseId ? (
        <section className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-bold uppercase text-neutral-500">Response Activity</p>
          <div className="mt-3 space-y-2">
            {(activity || []).length ? activity?.map((item) => (
              <div className="rounded border border-neutral-200 bg-neutral-50 p-3 text-sm" key={item.id}>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-bold text-neutral-900">{item.action.replaceAll("_", " ")}</p>
                  <span className="text-xs text-neutral-500">{new Date(item.created_at).toLocaleString("en-NG")}</span>
                </div>
                <p className="mt-1 text-xs text-neutral-500">{item.actor_name || "System"}{item.device_id ? ` · ${item.device_id}` : ""}</p>
              </div>
            )) : <p className="text-sm text-neutral-500">No activity recorded for this response yet.</p>}
          </div>
        </section>
      ) : null}
    </div>
  );
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function ExportsTab() {
  const [filters, setFilters] = useState({ assignment: "", template: "", status: "", sync_status: "", date_from: "", date_to: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const { data: assignments } = useQuery({ queryKey: ["form-assignments"], queryFn: async () => fetchFormAssignments() });
  const { data: templates } = useQuery({ queryKey: ["form-templates"], queryFn: async () => fetchFormTemplates() });
  const al = Array.isArray(assignments) ? assignments : [];
  const tl = Array.isArray(templates) ? templates : [];

  function exportParams() {
    return Object.fromEntries(Object.entries(filters).filter(([, value]) => Boolean(value)));
  }

  async function runExport(format: "csv" | "json" | "pdf") {
    setError("");
    setSuccess("");
    try {
      const blob = await downloadFormResponsesExport({ format, ...exportParams() });
      downloadBlob(blob, `form-responses.${format}`);
      setSuccess(`${format.toUpperCase()} export downloaded.`);
    } catch (err) {
      setError(getApiErrorMessage(err, "Could not download export."));
    }
  }

  async function runAttachmentExport() {
    setError("");
    setSuccess("");
    try {
      const blob = await downloadFormAttachmentsExport(exportParams());
      downloadBlob(blob, "form-attachments.zip");
      setSuccess("Attachment ZIP downloaded.");
    } catch (err) {
      setError(getApiErrorMessage(err, "Could not download attachments."));
    }
  }

  return (
    <div className="space-y-4">
      <section className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold text-neutral-900">Export Response Data</h3>
            <p className="mt-1 text-sm text-neutral-500">Download filtered form response data with repeat groups flattened into usable columns.</p>
          </div>
          <FileStack className="text-brand-600" size={22} />
        </div>
        {error ? <p className="mt-3 rounded border border-danger-100 bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</p> : null}
        {success ? <p className="mt-3 rounded border border-brand-100 bg-brand-50 px-3 py-2 text-sm font-semibold text-brand-800">{success}</p> : null}
        <div className="mt-4 grid gap-3 lg:grid-cols-3">
          <select className="h-10 rounded border border-neutral-200 px-3 text-sm" value={filters.assignment} onChange={(event) => setFilters((current) => ({ ...current, assignment: event.target.value }))}>
            <option value="">All assignments</option>
            {al.map((assignment) => <option key={assignment.id} value={assignment.id}>{assignment.title}</option>)}
          </select>
          <select className="h-10 rounded border border-neutral-200 px-3 text-sm" value={filters.template} onChange={(event) => setFilters((current) => ({ ...current, template: event.target.value }))}>
            <option value="">All templates</option>
            {tl.map((template) => <option key={template.id} value={template.id}>{template.title}</option>)}
          </select>
          <select className="h-10 rounded border border-neutral-200 px-3 text-sm" value={filters.status} onChange={(event) => setFilters((current) => ({ ...current, status: event.target.value }))}>
            <option value="">All statuses</option>
            {["draft", "in_progress", "submitted", "returned", "reviewed", "approved", "rejected", "overdue", "sync_failed"].map((status) => <option key={status} value={status}>{status.replaceAll("_", " ")}</option>)}
          </select>
          <select className="h-10 rounded border border-neutral-200 px-3 text-sm" value={filters.sync_status} onChange={(event) => setFilters((current) => ({ ...current, sync_status: event.target.value }))}>
            <option value="">All sync statuses</option>
            {["online", "available_offline", "sync_pending", "syncing", "synced", "sync_failed", "conflict"].map((status) => <option key={status} value={status}>{status.replaceAll("_", " ")}</option>)}
          </select>
          <input className="h-10 rounded border border-neutral-200 px-3 text-sm" type="date" value={filters.date_from} onChange={(event) => setFilters((current) => ({ ...current, date_from: event.target.value }))} />
          <input className="h-10 rounded border border-neutral-200 px-3 text-sm" type="date" value={filters.date_to} onChange={(event) => setFilters((current) => ({ ...current, date_to: event.target.value }))} />
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <button className="h-10 rounded bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700" onClick={() => runExport("csv")} type="button">CSV</button>
          <button className="h-10 rounded border border-brand-200 px-4 text-sm font-bold text-brand-700 hover:bg-brand-50" onClick={() => runExport("json")} type="button">JSON</button>
          <button className="h-10 rounded border border-neutral-200 px-4 text-sm font-bold text-neutral-700 hover:bg-neutral-50" onClick={() => runExport("pdf")} type="button">PDF Summary</button>
          <button className="h-10 rounded border border-neutral-200 px-4 text-sm font-bold text-neutral-700 hover:bg-neutral-50" onClick={runAttachmentExport} type="button">Attachment ZIP</button>
        </div>
      </section>
    </div>
  );
}

function SettingsTab() {
  const supportedWorkflows = [
    { label: "Builder", value: `${QUESTION_TYPES.length} field types` },
    { label: "Validation", value: "Required fields, ranges, lengths, regex, options" },
    { label: "Logic", value: "Show, hide, require, score, and warning rules" },
    { label: "Offline", value: "Draft storage, offline package, queued sync" },
    { label: "Media", value: "Image, file, video, audio, and signature uploads" },
    { label: "Review", value: "Submitted, reviewed, returned, approved, rejected" },
  ];

  return (
    <div className="space-y-4">
      <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold text-neutral-900">Forms Engine Configuration</h3>
            <p className="mt-1 text-sm text-neutral-500">Operational reference for deployed form capabilities.</p>
          </div>
          <StatusBadge status="active" />
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {supportedWorkflows.map((item) => (
            <div key={item.label} className="rounded border border-neutral-200 bg-neutral-50 p-3">
              <p className="text-xs font-bold uppercase text-neutral-500">{item.label}</p>
              <p className="mt-1 text-sm font-semibold text-neutral-900">{item.value}</p>
            </div>
          ))}
        </div>
      </section>
      <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <h3 className="text-sm font-bold text-neutral-900">Enabled Form Purposes</h3>
        <div className="mt-4 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
          {Object.entries(PURPOSE_LABELS).map(([key, label]) => (
            <div key={key} className="flex items-center justify-between rounded border border-neutral-200 px-3 py-2 text-sm">
              <span className="font-medium text-neutral-800">{label}</span>
              <span className="text-xs text-neutral-500">{key.replaceAll("_", " ")}</span>
            </div>
          ))}
        </div>
      </section>
      <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <h3 className="text-sm font-bold text-neutral-900">Supported Modules</h3>
        <div className="mt-4 flex flex-wrap gap-2">
          {Object.values(MODULE_LABELS).map((label) => (
            <span key={label} className="rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700">{label}</span>
          ))}
        </div>
      </section>
    </div>
  );
}

// ── Main Layout ──
export function FormsToolLayout() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tabParam = (searchParams.get("tab") ?? "overview") as TabKey;
  const activeTab = TABS[tabParam] ? tabParam : "overview";
  const permsQuery = useQuery({ queryKey: ["forms-permissions"], queryFn: fetchFormsPermissions, staleTime: 60_000 });
  const permsSet = new Set(permsQuery.data?.permissions || []);

  function setTab(tab: TabKey) { router.replace(`/state/forms?tab=${tab}`); }

  return (
    <FormsPermsCtx.Provider value={permsSet}>
      <PortalShell role="state_admin" title="Forms Tool" description="Create, assign, and track form templates, responses, and reports across all modules.">
        <nav className="mb-6 flex gap-0 overflow-x-auto border-b border-neutral-200">
          {(Object.entries(TABS) as [TabKey, string][]).map(([key, label]) => (
            <button key={key} className={`shrink-0 border-b-2 px-4 py-3 text-sm font-medium ${activeTab===key?"border-brand-600 text-brand-700":"border-transparent text-neutral-500 hover:text-neutral-800"}`} onClick={() => setTab(key)} type="button">{label}</button>
          ))}
        </nav>
        {activeTab === "overview" && <OverviewTab />}
        {activeTab === "templates" && <TemplatesTab />}
        {activeTab === "assignments" && <AssignmentsTab />}
        {activeTab === "responses" && <ResponsesTab />}
        {activeTab === "exports" && <ExportsTab />}
        {activeTab === "reports" && <FormsReportsTab />}
        {activeTab === "settings" && <SettingsTab />}
      </PortalShell>
    </FormsPermsCtx.Provider>
  );
}
