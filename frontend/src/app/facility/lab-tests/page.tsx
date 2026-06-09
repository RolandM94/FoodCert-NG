"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, FlaskConical, RefreshCw, TestTube2, Upload } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { listLabRequests } from "@/lib/api/lab-tests";
import type { LabTest } from "@/types/assessments";

const STATUS_FILTERS = [
  ["", "All statuses"],
  ["requested", "Requested"],
  ["sample_collected", "Sample collected"],
  ["in_progress", "In progress"],
  ["positive", "Positive"],
  ["negative", "Negative"],
  ["inconclusive", "Inconclusive"],
  ["repeat_required", "Repeat required"],
  ["reviewed", "Reviewed"],
];

function label(value?: string) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

function formatDate(value?: string) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function Page() {
  const [rows, setRows] = useState<LabTest[]>([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setRows(await listLabRequests(status ? { status } : undefined));
    } catch {
      setError("Could not load lab requests.");
    } finally {
      setLoading(false);
    }
  }, [status]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const metrics = useMemo(() => ({
    total: rows.length,
    requested: rows.filter((row) => row.status === "requested").length,
    submitted: rows.filter((row) => Boolean(row.submitted_to_doctor_at)).length,
    flagged: rows.filter((row) => ["positive", "inconclusive", "repeat_required"].includes(row.status)).length,
  }), [rows]);

  return (
    <PortalShell role="facility_admin" title="Lab Tests" description="Track requested tests, sample collection, result entry, uploads, and doctor review status.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading lab requests...</p> : null}
        <section className="grid gap-3 md:grid-cols-4">
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><FlaskConical className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Requests</p><p className="text-2xl font-bold text-neutral-900">{metrics.total}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><TestTube2 className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Awaiting sample</p><p className="text-2xl font-bold text-neutral-900">{metrics.requested}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><Upload className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Submitted</p><p className="text-2xl font-bold text-neutral-900">{metrics.submitted}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><AlertCircle className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Flagged</p><p className="text-2xl font-bold text-neutral-900">{metrics.flagged}</p></div>
        </section>

        <section className="flex flex-wrap items-center gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
            {STATUS_FILTERS.map(([value, text]) => <option key={value} value={value}>{text}</option>)}
          </select>
          <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-600 px-3 text-sm font-bold text-white" type="button" onClick={() => void loadData()}><RefreshCw size={16} /> Apply</button>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
          <div className="border-b border-neutral-200 p-4"><h2 className="text-sm font-bold text-neutral-900">Lab Request Queue</h2></div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-neutral-50 text-xs font-bold uppercase text-neutral-500">
                <tr><th className="p-3">Food handler</th><th className="p-3">Test</th><th className="p-3">Sample</th><th className="p-3">Submitted</th><th className="p-3">Status</th><th className="p-3">Action</th></tr>
              </thead>
              <tbody className="divide-y divide-neutral-200">
                {rows.length ? rows.map((row) => (
                  <tr key={row.id}>
                    <td className="p-3 font-bold text-neutral-900">{row.food_handler_name}</td>
                    <td className="p-3 capitalize">{row.test_name || label(row.test_type)}</td>
                    <td className="p-3">{formatDate(row.sample_collected_at)}</td>
                    <td className="p-3">{formatDate(row.submitted_to_doctor_at)}</td>
                    <td className="p-3"><StatusBadge status={row.status} /></td>
                    <td className="p-3"><Link className="rounded border border-neutral-200 px-3 py-1.5 text-xs font-bold text-neutral-700" href={`/lab/test-requests/${row.id}`}>Open</Link></td>
                  </tr>
                )) : <tr><td className="p-3 text-neutral-500" colSpan={6}>No lab requests found.</td></tr>}
              </tbody>
            </table>
          </div>
        </section>
        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}
      </div>
    </PortalShell>
  );
}
