"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { AlertCircle, ClipboardCheck, FlaskConical, RefreshCw, Stethoscope } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { listDoctorAssessments } from "@/lib/api/assessments";
import type { MedicalAssessment } from "@/types/assessments";

const TASK_FILTERS = [
  ["all", "All assigned"],
  ["declaration", "Declaration review"],
  ["physical", "Physical exam"],
  ["lab", "Lab review"],
  ["decision", "Decision pending"],
];

function label(value?: string) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

export default function Page() {
  const [assessments, setAssessments] = useState<MedicalAssessment[]>([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      setAssessments(await listDoctorAssessments());
    } catch {
      setError("Could not load assigned assessments.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  const filtered = useMemo(() => assessments.filter((row) => {
    if (filter === "declaration") return row.declaration_status === "submitted";
    if (filter === "physical") return row.declaration_status === "validated" && row.physical_exam_status !== "completed";
    if (filter === "lab") return row.lab_status !== "reviewed";
    if (filter === "decision") return row.physical_exam_status === "completed" && row.final_decision === "pending";
    return true;
  }), [assessments, filter]);

  return (
    <PortalShell role="doctor" title="Assessments" description="Review assigned declarations, complete physical exams, and move food handler assessments toward lab and decision steps.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading assigned assessments...</p> : null}

        <section className="grid gap-3 md:grid-cols-4">
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><Stethoscope className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Assigned</p><p className="text-2xl font-bold text-neutral-900">{assessments.length}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><ClipboardCheck className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Declaration</p><p className="text-2xl font-bold text-neutral-900">{assessments.filter((row) => row.declaration_status === "submitted").length}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><FlaskConical className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Lab pending</p><p className="text-2xl font-bold text-neutral-900">{assessments.filter((row) => row.lab_status !== "reviewed").length}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><RefreshCw className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Decision</p><p className="text-2xl font-bold text-neutral-900">{assessments.filter((row) => row.final_decision === "pending").length}</p></div>
        </section>

        <section className="flex flex-wrap items-center gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={filter} onChange={(event) => setFilter(event.target.value)}>
            {TASK_FILTERS.map(([value, text]) => <option key={value} value={value}>{text}</option>)}
          </select>
          <button className="inline-flex h-10 items-center gap-2 rounded border border-neutral-200 px-3 text-sm font-bold text-neutral-700" type="button" onClick={() => void loadData()}><RefreshCw size={16} /> Refresh</button>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
          <div className="border-b border-neutral-200 p-4">
            <h2 className="text-sm font-bold text-neutral-900">Assigned Cases</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-neutral-50 text-xs font-bold uppercase text-neutral-500">
                <tr><th className="p-3">Food handler</th><th className="p-3">Declaration</th><th className="p-3">Exam</th><th className="p-3">Lab</th><th className="p-3">Decision</th><th className="p-3">Action</th></tr>
              </thead>
              <tbody className="divide-y divide-neutral-200">
                {filtered.length ? filtered.map((assessment) => (
                  <tr key={assessment.id}>
                    <td className="p-3"><p className="font-bold text-neutral-900">{assessment.food_handler_name}</p><p className="text-xs text-neutral-500">{assessment.employer_name || "Individual"} · {assessment.food_handler_identifier}</p></td>
                    <td className="p-3"><StatusBadge status={assessment.declaration_status} /></td>
                    <td className="p-3"><StatusBadge status={assessment.physical_exam_status} /></td>
                    <td className="p-3"><StatusBadge status={assessment.lab_status} /></td>
                    <td className="p-3 capitalize">{label(assessment.final_decision)}</td>
                    <td className="p-3"><Link className="rounded border border-neutral-200 px-3 py-1.5 text-xs font-bold text-neutral-700" href={`/doctor/assessments/${assessment.id}`}>Open</Link></td>
                  </tr>
                )) : (
                  <tr><td className="p-3 text-neutral-500" colSpan={6}>No assigned assessments match this view.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}
      </div>
    </PortalShell>
  );
}
