"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle } from "lucide-react";

import { AssessmentStatusBadge } from "@/components/assessments/assessment-status-badge";
import { HealthDeclarationForm, type DeclarationFormValue } from "@/components/assessments/health-declaration-form";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { getAssessmentDeclaration, listAssessments, saveDeclarationDraft, submitDeclarationVersion } from "@/lib/api/assessments";
import type { HealthDeclaration, MedicalAssessment } from "@/types/assessments";

function latestAssessment(rows: MedicalAssessment[]) {
  return [...rows].sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at))[0];
}

export default function Page() {
  const [assessments, setAssessments] = useState<MedicalAssessment[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [declaration, setDeclaration] = useState<HealthDeclaration | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const selectedAssessment = useMemo(
    () => assessments.find((row) => row.id === selectedId) || latestAssessment(assessments),
    [assessments, selectedId]
  );

  const loadAssessments = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const rows = await listAssessments();
      setAssessments(rows);
      setSelectedId((current) => current || latestAssessment(rows)?.id || "");
    } catch {
      setError("Could not load assessments.");
    } finally {
      setLoading(false);
    }
  }, []);

  const loadDeclaration = useCallback(async (assessmentId: string) => {
    setDeclaration(null);
    try {
      const row = await getAssessmentDeclaration(assessmentId);
      setDeclaration(row);
    } catch {
      setDeclaration(null);
    }
  }, []);

  useEffect(() => {
    void loadAssessments();
  }, [loadAssessments]);

  useEffect(() => {
    if (selectedAssessment?.id) void loadDeclaration(selectedAssessment.id);
  }, [loadDeclaration, selectedAssessment?.id]);

  async function saveDraft(payload: DeclarationFormValue) {
    if (!selectedAssessment) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const row = await saveDeclarationDraft(selectedAssessment.id, payload);
      setDeclaration(row);
      setSuccess("Draft saved.");
      await loadAssessments();
    } catch {
      setError("Draft could not be saved. Submitted or validated declarations may be locked.");
    } finally {
      setBusy(false);
    }
  }

  async function submitForm(payload: DeclarationFormValue) {
    if (!selectedAssessment) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const row = await submitDeclarationVersion(selectedAssessment.id, payload);
      setDeclaration(row);
      setSuccess("Declaration submitted.");
      await loadAssessments();
    } catch {
      setError("Declaration could not be submitted. Confirm the assessment is open and all required fields are complete.");
    } finally {
      setBusy(false);
    }
  }

  const locked = Boolean(declaration?.is_locked || selectedAssessment?.declaration_status === "validated" || selectedAssessment?.declaration_status === "submitted");

  return (
    <PortalShell role="food_handler" title="Health Declaration" description="Save a draft, submit for doctor review, and track declaration corrections.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading declaration...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}
        {success ? <div className="rounded-lg bg-brand-50 p-3 text-sm font-semibold text-brand-800">{success}</div> : null}

        <section className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-bold text-neutral-900">Assessment</h2>
            {assessments.length ? (
              <select className="mt-4 h-10 w-full rounded border border-neutral-200 bg-white px-3 text-sm" value={selectedAssessment?.id || ""} onChange={(event) => setSelectedId(event.target.value)}>
                {assessments.map((assessment) => (
                  <option key={assessment.id} value={assessment.id}>{assessment.facility_name || "Medical facility"} · {assessment.status.replaceAll("_", " ")}</option>
                ))}
              </select>
            ) : <p className="mt-4 text-sm font-semibold text-neutral-500">No assessment found.</p>}

            {selectedAssessment ? (
              <dl className="mt-4 grid gap-3 text-sm">
                <div className="flex items-center justify-between gap-3"><dt className="text-neutral-500">Workflow</dt><dd><AssessmentStatusBadge status={selectedAssessment.status} /></dd></div>
                <div className="flex items-center justify-between gap-3"><dt className="text-neutral-500">Declaration</dt><dd><StatusBadge status={selectedAssessment.declaration_status} /></dd></div>
                <div className="flex items-center justify-between gap-3"><dt className="text-neutral-500">Version</dt><dd className="font-bold text-neutral-900">{declaration?.version || 1}</dd></div>
                {declaration?.clarification_reason ? <div className="rounded bg-warning-50 p-3 text-xs font-semibold text-amber-900">{declaration.clarification_reason}</div> : null}
                <Link className="inline-flex w-fit rounded border border-neutral-200 px-3 py-2 text-sm font-bold text-neutral-700" href={`/food-handler/assessments/${selectedAssessment.id}`}>Open assessment</Link>
              </dl>
            ) : null}
          </div>

          <HealthDeclarationForm
            declaration={declaration}
            disabled={locked || !selectedAssessment}
            busy={busy}
            onSaveDraft={(payload) => void saveDraft(payload)}
            onSubmit={(payload) => void submitForm(payload)}
          />
        </section>
      </div>
    </PortalShell>
  );
}
