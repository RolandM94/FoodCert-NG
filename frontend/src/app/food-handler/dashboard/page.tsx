"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, BadgeCheck, CalendarDays, ClipboardList, FileCheck2, ShieldCheck } from "lucide-react";

import { AssessmentPrerequisiteChecklist } from "@/components/assessments/assessment-prerequisite-checklist";
import { AssessmentStatusBadge } from "@/components/assessments/assessment-status-badge";
import { AssessmentStepper } from "@/components/assessments/assessment-stepper";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { getAssessmentStatus, listAssessments } from "@/lib/api/assessments";
import { listCertificates } from "@/lib/api/certificates";
import { listFoodHandlers } from "@/lib/api/identity";
import type { AssessmentStatusSnapshot, MedicalAssessment } from "@/types/assessments";
import type { Certificate } from "@/types/certificates";
import type { FoodHandlerProfile } from "@/types/identity";

function dateLabel(value?: string) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium" }).format(new Date(value));
}

function latestByDate<T extends { created_at: string }>(rows: T[]) {
  return [...rows].sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at))[0];
}

export default function Page() {
  const [profile, setProfile] = useState<FoodHandlerProfile | null>(null);
  const [assessments, setAssessments] = useState<MedicalAssessment[]>([]);
  const [snapshot, setSnapshot] = useState<AssessmentStatusSnapshot | null>(null);
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [profiles, assessmentRows, certificateRows] = await Promise.all([
        listFoodHandlers(),
        listAssessments(),
        listCertificates(),
      ]);
      const latestAssessment = latestByDate(assessmentRows);
      setProfile(profiles[0] || null);
      setAssessments(assessmentRows);
      setCertificates(certificateRows);
      setSnapshot(latestAssessment ? await getAssessmentStatus(latestAssessment.id) : null);
    } catch {
      setError("Could not load dashboard.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const latestAssessment = useMemo(() => latestByDate(assessments), [assessments]);
  const latestCertificate = useMemo(() => latestByDate(certificates), [certificates]);

  return (
    <PortalShell role="food_handler" title="Certification Dashboard" description="Track profile, identity, assessment, fitness decision, and certificate status.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading dashboard...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} />{error}</div> : null}

        <section className="grid gap-3 md:grid-cols-4">
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><ShieldCheck className="text-brand-deep" size={18} /><p className="mt-2 text-xs font-bold uppercase text-slate-500">Profile</p><p className="text-sm font-bold text-slate-950">{profile?.full_name || "No profile"}</p><StatusBadge status={profile?.current_status || "profile_incomplete"} /></div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><ClipboardList className="text-brand-deep" size={18} /><p className="mt-2 text-xs font-bold uppercase text-slate-500">Assessment</p><div className="mt-2">{latestAssessment ? <AssessmentStatusBadge status={latestAssessment.status} /> : <StatusBadge status="not_started" />}</div></div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><FileCheck2 className="text-brand-deep" size={18} /><p className="mt-2 text-xs font-bold uppercase text-slate-500">Next action</p><p className="text-sm font-bold text-slate-950">{snapshot?.next_action.label || "Create assessment"}</p></div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><BadgeCheck className="text-brand-deep" size={18} /><p className="mt-2 text-xs font-bold uppercase text-slate-500">Certificate</p><StatusBadge status={latestCertificate?.effective_status || "not_issued"} /></div>
        </section>

        {snapshot ? (
          <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-sm font-bold text-slate-950">Current Assessment</h2>
                <p className="mt-1 text-sm text-slate-500">{latestAssessment?.facility_name || "Medical facility"} · {dateLabel(latestAssessment?.created_at)}</p>
              </div>
              {latestAssessment ? <Link className="rounded border border-slate-200 px-3 py-2 text-sm font-bold text-slate-700" href={`/food-handler/assessments/${latestAssessment.id}`}>Open</Link> : null}
            </div>
            <div className="mt-4"><AssessmentStepper steps={snapshot.steps} /></div>
          </section>
        ) : null}

        <section className="grid gap-4 lg:grid-cols-[1fr_0.8fr]">
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-bold text-slate-950">Prerequisites</h2>
            <div className="mt-4">
              {snapshot ? <AssessmentPrerequisiteChecklist blockers={snapshot.blockers} warnings={snapshot.warnings} /> : <p className="text-sm font-semibold text-slate-500">No active assessment.</p>}
            </div>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-bold text-slate-950">Certificate</h2>
            {latestCertificate ? (
              <dl className="mt-4 grid gap-3 text-sm">
                <div className="flex items-center justify-between gap-3"><dt className="text-slate-500">Number</dt><dd className="font-mono text-xs font-bold text-slate-950">{latestCertificate.certificate_number}</dd></div>
                <div className="flex items-center justify-between gap-3"><dt className="text-slate-500">Status</dt><dd><StatusBadge status={latestCertificate.effective_status} /></dd></div>
                <div className="flex items-center justify-between gap-3"><dt className="text-slate-500">Expiry</dt><dd className="font-bold text-slate-950">{dateLabel(latestCertificate.expiry_date)}</dd></div>
                <Link className="inline-flex w-fit items-center gap-2 rounded bg-brand-green px-3 py-2 text-sm font-bold text-white" href="/food-handler/certificate"><CalendarDays size={16} /> View certificate</Link>
              </dl>
            ) : <p className="mt-4 text-sm font-semibold text-slate-500">No certificate issued.</p>}
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
