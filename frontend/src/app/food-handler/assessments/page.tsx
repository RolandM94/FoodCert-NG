"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { AlertCircle, CalendarDays, ClipboardList, FileCheck2, RefreshCw, Stethoscope } from "lucide-react";

import { AssessmentStatusBadge } from "@/components/assessments/assessment-status-badge";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { getAssessmentStatus, listAssessments } from "@/lib/api/assessments";
import type { AssessmentStatusSnapshot, MedicalAssessment } from "@/types/assessments";

function dateLabel(value?: string) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium" }).format(new Date(value));
}

function pickLatest(rows: MedicalAssessment[]) {
  return [...rows].sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at))[0];
}

export default function Page() {
  const [assessments, setAssessments] = useState<MedicalAssessment[]>([]);
  const [snapshots, setSnapshots] = useState<Record<string, AssessmentStatusSnapshot>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const rows = await listAssessments();
      setAssessments(rows);
      const latestRows = rows.slice(0, 6);
      const statusRows = await Promise.all(latestRows.map((row) => getAssessmentStatus(row.id)));
      setSnapshots(Object.fromEntries(statusRows.map((snapshot) => [snapshot.assessment, snapshot])));
    } catch {
      setError("Could not load assessments.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const latest = pickLatest(assessments);
  const latestSnapshot = latest ? snapshots[latest.id] : undefined;

  return (
    <PortalShell role="food_handler" title="Assessments" description="Track medical assessment progress, appointment status, reviews, decisions, and certificate readiness.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading assessments...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} />{error}</div> : null}

        <section className="grid gap-3 md:grid-cols-4">
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <ClipboardList className="text-brand-deep" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-slate-500">Assessments</p>
            <p className="text-2xl font-bold text-slate-950">{assessments.length}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <Stethoscope className="text-brand-deep" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-slate-500">Current status</p>
            <div className="mt-2">{latest ? <AssessmentStatusBadge status={latest.status} /> : <StatusBadge status="not_started" />}</div>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <CalendarDays className="text-brand-deep" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-slate-500">Appointment</p>
            <p className="text-sm font-bold text-slate-950">{dateLabel(latest?.appointment_date || latest?.assessment_date)}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <FileCheck2 className="text-brand-deep" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-slate-500">Next action</p>
            <p className="text-sm font-bold text-slate-950">{latestSnapshot?.next_action.label || "Not started"}</p>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 p-4">
            <h2 className="text-sm font-bold text-slate-950">Assessment History</h2>
            <button className="inline-flex h-9 items-center gap-2 rounded border border-slate-200 px-3 text-xs font-bold text-slate-700" type="button" onClick={() => void loadData()}>
              <RefreshCw size={14} /> Refresh
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs font-bold uppercase text-slate-500">
                <tr><th className="p-3">Facility</th><th className="p-3">Appointment</th><th className="p-3">Workflow</th><th className="p-3">Decision</th><th className="p-3">Action</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {assessments.map((assessment) => (
                  <tr key={assessment.id}>
                    <td className="p-3"><p className="font-bold text-slate-950">{assessment.facility_name || "Medical facility"}</p><p className="text-xs text-slate-500">{dateLabel(assessment.created_at)}</p></td>
                    <td className="p-3"><p className="text-sm font-semibold text-slate-700">{dateLabel(assessment.appointment_date || assessment.assessment_date)}</p><StatusBadge status={assessment.appointment_status || "not_booked"} /></td>
                    <td className="p-3"><AssessmentStatusBadge status={assessment.status} /></td>
                    <td className="p-3"><StatusBadge status={assessment.final_decision} /></td>
                    <td className="p-3"><Link className="rounded border border-slate-200 px-3 py-1.5 text-xs font-bold text-slate-700" href={`/food-handler/assessments/${assessment.id}`}>Open</Link></td>
                  </tr>
                ))}
                {!assessments.length && !loading ? <tr><td className="p-3 text-slate-500" colSpan={5}>No assessments found.</td></tr> : null}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
