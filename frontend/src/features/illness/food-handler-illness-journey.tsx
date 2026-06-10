"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, CalendarDays, FileText, HeartPulse } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { IllnessExclusionStatusBadge, ReturnToWorkStatusBadge } from "@/components/ui/illness-status-badges";
import { listIllnessReports } from "@/lib/api/illness";
import type { IllnessReport } from "@/types/illness";

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

function latestActive(rows: IllnessReport[]) {
  return rows.find((row) => !["cleared", "rejected"].includes(row.clearance_status)) || rows[0] || null;
}

function nextStep(report: IllnessReport | null) {
  if (!report) return "Report symptoms if you feel unwell or follow your certification workflow.";
  if (report.clearance_status === "cleared") return "You have been cleared to return to food handling duties.";
  if (report.clearance_status === "rejected") return "Follow up with an approved medical facility before returning to food handling duties.";
  if (report.clearance_required) return "Visit an approved medical facility or doctor for return-to-work clearance.";
  return "Remain away from food handling duties until the exclusion period and medical review are complete.";
}

export function FoodHandlerIllnessJourney({ mode }: { mode: "illness" | "return-to-work" }) {
  const reportsQuery = useQuery({
    queryKey: ["food-handler-illness-reports"],
    queryFn: listIllnessReports,
  });
  const reports = reportsQuery.data || [];
  const current = latestActive(reports);

  return (
    <PortalShell
      role="food_handler"
      title={mode === "illness" ? "Illness Status" : "Return-to-Work"}
      description={mode === "illness" ? "View your illness exclusion status and required next steps." : "Track your return-to-work clearance outcome and earliest return date."}
    >
      <div className="grid gap-5">
        {reportsQuery.isLoading ? <div className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600">Loading illness status...</div> : null}
        {reportsQuery.isError ? <div className="rounded-lg border border-danger-100 bg-danger-50 p-4 text-sm font-semibold text-danger-700">Could not load illness status.</div> : null}

        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Current status</p>
              <h2 className="mt-2 text-xl font-bold text-neutral-900">
                {current ? "Illness / return-to-work case" : "No active illness exclusion"}
              </h2>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-neutral-600">{nextStep(current)}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <IllnessExclusionStatusBadge status={current?.clearance_status} />
              <ReturnToWorkStatusBadge status={current?.clearance_status} earliestReturnDate={current?.earliest_return_date} />
            </div>
          </div>
        </section>

        {current ? (
          <section className="grid gap-4 md:grid-cols-3">
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <HeartPulse className="text-brand-700" size={18} />
              <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Symptom category</p>
              <p className="mt-1 text-sm font-bold capitalize text-neutral-900">{current.suspected_condition?.replaceAll("_", " ") || "Not specified"}</p>
            </div>
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <CalendarDays className="text-brand-700" size={18} />
              <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Earliest return</p>
              <p className="mt-1 text-sm font-bold text-neutral-900">{dateLabel(current.earliest_return_date)}</p>
            </div>
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <FileText className="text-brand-700" size={18} />
              <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Clearance reference</p>
              <p className="mt-1 text-sm font-bold text-neutral-900">{current.return_to_work_certificate_number || "Not issued"}</p>
            </div>
          </section>
        ) : (
          <section className="rounded-lg border border-neutral-200 bg-white p-8 text-center shadow-sm">
            <HeartPulse className="mx-auto text-neutral-300" size={32} />
            <p className="mt-3 text-sm font-semibold text-neutral-500">No active exclusion or return-to-work case.</p>
            <Link className="mt-4 inline-flex rounded bg-brand-600 px-4 py-2 text-sm font-bold text-white" href="/food-handler/illness">
              Open illness page
            </Link>
          </section>
        )}

        {reports.length ? (
          <section className="overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-sm">
            <div className="border-b border-neutral-200 p-4">
              <h2 className="text-sm font-bold text-neutral-900">Case history</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[780px] text-sm">
                <thead className="bg-neutral-50 text-left text-xs font-bold uppercase text-neutral-500">
                  <tr><th className="p-3">Reported</th><th className="p-3">Category</th><th className="p-3">Exclusion</th><th className="p-3">Return-to-work</th><th className="p-3">Earliest return</th><th className="p-3">Cleared at</th></tr>
                </thead>
                <tbody className="divide-y divide-neutral-100">
                  {reports.map((report) => (
                    <tr key={report.id}>
                      <td className="p-3 text-neutral-600">{dateLabel(report.created_at)}</td>
                      <td className="p-3 capitalize text-neutral-700">{report.suspected_condition?.replaceAll("_", " ") || "Not specified"}</td>
                      <td className="p-3"><IllnessExclusionStatusBadge status={report.clearance_status} /></td>
                      <td className="p-3"><ReturnToWorkStatusBadge status={report.clearance_status} earliestReturnDate={report.earliest_return_date} /></td>
                      <td className="p-3 text-neutral-600">{dateLabel(report.earliest_return_date)}</td>
                      <td className="p-3 text-neutral-600">{dateLabel(report.cleared_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ) : null}

        <section className="rounded-lg border border-info-100 bg-info-50 p-4 text-sm font-semibold text-info-700">
          <div className="flex items-start gap-2">
            <AlertTriangle className="mt-0.5 shrink-0" size={16} />
            <p>If you are excluded, do not handle food until you are cleared. Employers and medical reviewers receive the operational outcome needed for duty assignment.</p>
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
