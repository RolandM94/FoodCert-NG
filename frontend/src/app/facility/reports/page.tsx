"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, Download, FileText, RefreshCw, Send } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { getCurrentMedicalFacility } from "@/lib/api/facilities";
import { generateFacilityPerformanceReport, listGeneratedReportsWithParams } from "@/lib/api/reports";
import type { MedicalFacility } from "@/types/facilities";
import type { GeneratedReport, ReportFormat } from "@/types/reports";

const FORMAT_OPTIONS: Array<[ReportFormat, string]> = [
  ["json", "JSON"],
  ["csv", "CSV"],
  ["pdf", "PDF"],
  ["excel", "Excel"],
];

function label(value?: string) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

function formatDate(value?: string) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function Page() {
  const [facility, setFacility] = useState<MedicalFacility | null>(null);
  const [reports, setReports] = useState<GeneratedReport[]>([]);
  const [fileFormat, setFileFormat] = useState<ReportFormat>("json");
  const [filters, setFilters] = useState({ date_from: "", date_to: "", lab_status: "", assessment_status: "" });
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const reportFilters = useMemo(() => Object.fromEntries(Object.entries(filters).filter(([, value]) => value)), [filters]);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const profile = await getCurrentMedicalFacility();
      const rows = await listGeneratedReportsWithParams({ report_type: "facility_performance" });
      setFacility(profile);
      setReports(rows);
    } catch {
      setError("Could not load facility reports.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  async function generate() {
    if (!facility) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const report = await generateFacilityPerformanceReport(facility.id, fileFormat, reportFilters);
      setReports((current) => [report, ...current.filter((row) => row.id !== report.id)]);
      setSuccess("Facility performance report generated.");
    } catch {
      setError("Could not generate facility performance report.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <PortalShell role="facility_admin" title="Reports" description="Generate role-aware facility reports and export finance-safe operational summaries.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading reports...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} />{error}</div> : null}
        {success ? <div className="rounded-lg bg-emerald-50 p-3 text-sm font-semibold text-emerald-800">{success}</div> : null}

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <FileText className="text-brand-deep" size={18} />
            <h2 className="text-sm font-bold text-slate-950">Report builder</h2>
          </div>
          <div className="grid gap-3 lg:grid-cols-[170px_170px_190px_210px_150px_auto]">
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" type="date" value={filters.date_from} onChange={(event) => setFilters((current) => ({ ...current, date_from: event.target.value }))} />
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" type="date" value={filters.date_to} onChange={(event) => setFilters((current) => ({ ...current, date_to: event.target.value }))} />
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={filters.lab_status} onChange={(event) => setFilters((current) => ({ ...current, lab_status: event.target.value }))}>
              <option value="">All lab states</option><option value="pending">Pending</option><option value="submitted">Submitted</option><option value="reviewed">Reviewed</option>
            </select>
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={filters.assessment_status} onChange={(event) => setFilters((current) => ({ ...current, assessment_status: event.target.value }))}>
              <option value="">All assessment states</option><option value="payment_confirmed">Payment confirmed</option><option value="fit">Fit</option><option value="submitted_for_state_validation">Submitted to State</option>
            </select>
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={fileFormat} onChange={(event) => setFileFormat(event.target.value as ReportFormat)}>
              {FORMAT_OPTIONS.map(([value, text]) => <option key={value} value={value}>{text}</option>)}
            </select>
            <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white disabled:opacity-60" disabled={busy || !facility} type="button" onClick={() => void generate()}><Send size={16} /> Generate</button>
          </div>
          <p className="mt-3 text-xs font-semibold text-slate-500">Facility finance exports include settlement and operational counts only. Clinical notes, declaration answers, and lab result values are excluded.</p>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between gap-3 border-b border-slate-200 p-4">
            <div>
              <h2 className="text-sm font-bold text-slate-950">Recent generated reports</h2>
              <p className="text-xs text-slate-500">{facility?.facility_name || "Current facility"}</p>
            </div>
            <button className="inline-flex h-9 items-center gap-2 rounded border border-slate-200 px-3 text-xs font-bold text-slate-700" type="button" onClick={() => void loadData()}><RefreshCw size={14} /> Refresh</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs font-bold uppercase text-slate-500">
                <tr><th className="p-3">Report</th><th className="p-3">Format</th><th className="p-3">Status</th><th className="p-3">Generated by</th><th className="p-3">Created</th><th className="p-3">File</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {reports.length ? reports.map((report) => (
                  <tr key={report.id}>
                    <td className="p-3"><p className="font-bold capitalize text-slate-950">{label(report.report_type)}</p><p className="text-xs text-slate-500">{Object.keys(report.filters || {}).length} filters</p></td>
                    <td className="p-3 font-semibold uppercase text-slate-700">{report.file_format}</td>
                    <td className="p-3"><StatusBadge status={report.status} /></td>
                    <td className="p-3 text-slate-700">{report.generated_by_name || "System"}</td>
                    <td className="p-3 text-slate-700">{formatDate(report.created_at)}</td>
                    <td className="p-3">{report.file_url ? <a className="inline-flex items-center gap-1 font-bold text-brand-deep underline" href={report.file_url} rel="noreferrer" target="_blank"><Download size={14} /> Download</a> : "Preview only"}</td>
                  </tr>
                )) : (
                  <tr><td className="p-3 text-slate-500" colSpan={6}>No facility reports generated yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
