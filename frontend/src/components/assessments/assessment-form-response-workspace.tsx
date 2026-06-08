"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertCircle, ClipboardCheck, RefreshCw, RotateCcw } from "lucide-react";
import { DynamicFormRenderer } from "@/components/assessments/dynamic-form-renderer";
import { StatusBadge } from "@/components/status/status-badge";
import {
  assignAssessmentForms,
  getAssessmentRequirements,
  listAssessmentFormResponses,
  listAssessments,
  reopenAssessmentFormResponse,
  saveAssessmentFormResponse,
  submitAssessmentFormResponse,
  validateAssessmentFormResponse,
} from "@/lib/api/assessments";
import type { AssessmentFormResponse, AssessmentRequirementResolution, MedicalAssessment } from "@/types/assessments";
import type { UserRole } from "@/types/auth";

function label(value?: string) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

function visibleForRole(role: UserRole, response: AssessmentFormResponse) {
  if (role === "food_handler") return response.respondent_role === "food_handler";
  if (role === "doctor") return response.respondent_role === "doctor" || response.risk_flags.length || ["submitted", "resubmitted", "under_review"].includes(response.status);
  if (role === "lab_staff") return response.respondent_role === "lab_staff" || response.form_type === "lab_result";
  return true;
}

export function AssessmentFormResponseWorkspace({
  role,
  title,
  mode,
}: {
  role: UserRole;
  title: string;
  mode: "complete" | "review";
}) {
  const [assessments, setAssessments] = useState<MedicalAssessment[]>([]);
  const [assessmentId, setAssessmentId] = useState("");
  const [responses, setResponses] = useState<AssessmentFormResponse[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [requirements, setRequirements] = useState<AssessmentRequirementResolution | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [reopenReason, setReopenReason] = useState("");

  const selected = useMemo(() => responses.find((item) => item.id === selectedId) || responses[0], [responses, selectedId]);
  const completion = useMemo(() => {
    const required = responses.filter((item) => item.is_required);
    const done = required.filter((item) => ["submitted", "resubmitted", "under_review", "validated", "locked"].includes(item.status));
    return { done: done.length, total: required.length };
  }, [responses]);

  async function loadAssessments() {
    setLoading(true);
    setError("");
    try {
      const rows = await listAssessments();
      setAssessments(rows);
      const current = assessmentId || rows[0]?.id || "";
      setAssessmentId(current);
      if (current) await loadResponses(current);
    } catch {
      setError("Could not load assessments and assigned forms.");
    } finally {
      setLoading(false);
    }
  }

  async function loadResponses(id: string) {
    setError("");
    const [forms, requirementRow] = await Promise.all([
      listAssessmentFormResponses({ assessment: id }),
      getAssessmentRequirements(id).catch(() => null),
    ]);
    const visible = forms.filter((item) => visibleForRole(role, item));
    setResponses(visible);
    setRequirements(requirementRow);
    setSelectedId(visible[0]?.id || "");
  }

  useEffect(() => {
    void loadAssessments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function assignForms() {
    if (!assessmentId) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await assignAssessmentForms(assessmentId);
      await loadResponses(assessmentId);
      setSuccess("Requirements resolved and forms assigned.");
    } catch {
      setError("Could not assign forms for this assessment.");
    } finally {
      setBusy(false);
    }
  }

  async function save(values: Record<string, unknown>, submit = false) {
    if (!selected) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const saved = await saveAssessmentFormResponse(selected.id, values);
      const updated = submit ? await submitAssessmentFormResponse(saved.id) : saved;
      setResponses((rows) => rows.map((item) => item.id === updated.id ? updated : item));
      setSuccess(submit ? "Form submitted." : "Draft saved.");
    } catch {
      setError(submit ? "Could not submit this form. Check required fields and validation rules." : "Could not save draft.");
    } finally {
      setBusy(false);
    }
  }

  async function validate() {
    if (!selected) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const updated = await validateAssessmentFormResponse(selected.id);
      setResponses((rows) => rows.map((item) => item.id === updated.id ? updated : item));
      setSuccess("Response validated.");
    } catch {
      setError("Could not validate this response.");
    } finally {
      setBusy(false);
    }
  }

  async function reopen() {
    if (!selected || !reopenReason.trim()) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const opened = await reopenAssessmentFormResponse(selected.id, reopenReason);
      setReopenReason("");
      await loadResponses(opened.assessment);
      setSelectedId(opened.id);
      setSuccess("Response reopened for correction.");
    } catch {
      setError("Could not reopen this response.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[360px_1fr]">
      <section className="grid h-fit gap-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-base font-bold text-slate-950">{title}</h2>
          <button className="inline-flex h-9 items-center gap-2 rounded border border-slate-200 px-3 text-xs font-bold text-slate-700" onClick={() => void loadAssessments()} type="button"><RefreshCw size={14} /> Refresh</button>
        </div>
        <select
          className="h-10 rounded border border-slate-200 bg-white px-3 text-sm"
          onChange={(event) => {
            setAssessmentId(event.target.value);
            void loadResponses(event.target.value);
          }}
          value={assessmentId}
        >
          {assessments.map((assessment) => <option key={assessment.id} value={assessment.id}>{assessment.food_handler_name || assessment.id} · {label(assessment.status)}</option>)}
        </select>
        <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-green px-3 text-sm font-bold text-white disabled:bg-slate-300" disabled={busy || !assessmentId} onClick={() => void assignForms()} type="button"><ClipboardCheck size={16} /> Resolve assigned forms</button>
        <div className="rounded border border-slate-200 bg-slate-50 p-3">
          <p className="text-xs font-bold uppercase text-slate-500">Required completion</p>
          <p className="mt-1 text-2xl font-bold text-slate-950">{completion.done}/{completion.total}</p>
        </div>
        {requirements ? (
          <div className="grid gap-2 text-sm">
            <p className="font-bold text-slate-950">Requirement checklist</p>
            {requirements.required_forms.map((item) => <div className="flex items-center justify-between gap-2 rounded border border-slate-200 bg-white px-3 py-2" key={item.id}><span>{item.name}</span><StatusBadge status={item.mandatory ? "mandatory" : "optional"} /></div>)}
            {requirements.required_lab_tests.map((item) => <div className="rounded border border-slate-200 bg-white px-3 py-2" key={item}>Lab: {label(item)}</div>)}
            {requirements.required_vaccinations.map((item) => <div className="rounded border border-slate-200 bg-white px-3 py-2" key={item}>Vaccination: {label(item)}</div>)}
          </div>
        ) : null}
        <div className="grid gap-2">
          {responses.map((response) => (
            <button className={`rounded border px-3 py-2 text-left text-sm ${selected?.id === response.id ? "border-brand-green bg-emerald-50" : "border-slate-200 bg-white"}`} key={response.id} onClick={() => setSelectedId(response.id)} type="button">
              <span className="block font-bold text-slate-950">{response.template_name || response.question_snapshot.name}</span>
              <span className="mt-1 flex items-center gap-2 text-xs text-slate-500">v{response.version} · {label(response.respondent_role)} · <StatusBadge status={response.status} /></span>
            </button>
          ))}
          {!responses.length && !loading ? <p className="text-sm text-slate-500">No assigned forms match this view.</p> : null}
        </div>
      </section>

      <section className="grid gap-4">
        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} />{error}</div> : null}
        {success ? <div className="rounded-lg bg-emerald-50 p-3 text-sm font-semibold text-emerald-800">{success}</div> : null}
        {selected ? (
          <>
            <DynamicFormRenderer
              busy={busy}
              mode={mode}
              onSave={(values) => void save(values)}
              onSubmit={(values) => void save(values, true)}
              onValidate={() => void validate()}
              response={selected}
            />
            {mode === "review" ? (
              <section className="grid gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
                <h3 className="text-sm font-bold text-slate-950">Correction workflow</h3>
                <textarea className="min-h-20 rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm" onChange={(event) => setReopenReason(event.target.value)} placeholder="Reason for reopening this response" value={reopenReason} />
                <button className="inline-flex h-10 w-fit items-center gap-2 rounded border border-amber-200 px-3 text-sm font-bold text-amber-800 disabled:opacity-50" disabled={busy || !reopenReason.trim()} onClick={() => void reopen()} type="button"><RotateCcw size={16} /> Reopen response</button>
              </section>
            ) : null}
          </>
        ) : null}
      </section>
    </div>
  );
}
