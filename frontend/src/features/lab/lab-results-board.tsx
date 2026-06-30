"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { listLabRequests } from "@/lib/api/lab-tests";
import type { LabTest } from "@/types/assessments";

const RESULT_STATUSES = ["positive", "negative", "inconclusive", "repeat_required", "result_uploaded", "submitted_to_doctor", "reviewed"];

function label(value?: string) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

export function LabResultsBoard({
  title,
  description,
  basePath = "/lab/test-requests",
}: {
  title: string;
  description: string;
  basePath?: string;
}) {
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
      setError("Could not load lab results.");
    } finally {
      setLoading(false);
    }
  }, [status]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const metrics = useMemo(() => ({
    flagged: rows.filter((row) => row.is_flagged).length,
    repeats: rows.filter((row) => row.repeat_required || row.parent_lab_test).length,
    submitted: rows.filter((row) => row.submitted_to_doctor_at).length,
  }), [rows]);

  return (
    <PortalShell role="lab_staff" title={title} description={description}>
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading lab results...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}

        <section className="grid gap-3 md:grid-cols-3">
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-neutral-500">Submitted</p><p className="text-2xl font-bold text-neutral-900">{metrics.submitted}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-neutral-500">Flagged</p><p className="text-2xl font-bold text-neutral-900">{metrics.flagged}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-neutral-500">Repeats</p><p className="text-2xl font-bold text-neutral-900">{metrics.repeats}</p></div>
        </section>

        <section className="flex flex-wrap items-center gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
            <option value="">All result statuses</option>
            {RESULT_STATUSES.map((value) => <option key={value} value={value}>{label(value)}</option>)}
          </select>
          <button className="inline-flex h-10 items-center gap-2 rounded border border-neutral-200 px-3 text-sm font-bold text-neutral-700" type="button" onClick={() => void loadData()}><RefreshCw size={16} /> Refresh</button>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-neutral-50 text-xs font-bold uppercase text-neutral-500">
                <tr><th className="p-3">Food handler</th><th className="p-3">Test</th><th className="p-3">Result</th><th className="p-3">Doctor</th><th className="p-3">Action</th></tr>
              </thead>
              <tbody className="divide-y divide-neutral-200">
                {rows.map((row) => (
                  <tr key={row.id}>
                    <td className="p-3 font-bold text-neutral-900">{row.food_handler_name}</td>
                    <td className="p-3"><p className="font-semibold capitalize text-neutral-900">{row.test_name || label(row.test_type)}</p>{row.parent_lab_test ? <p className="text-xs font-semibold text-warning-700">Repeat</p> : null}</td>
                    <td className="p-3"><StatusBadge status={row.status} />{row.is_flagged ? <p className="mt-1 text-xs font-semibold text-warning-700">Flagged</p> : null}</td>
                    <td className="p-3 text-neutral-600">{row.reviewed_at ? "Reviewed" : row.submitted_to_doctor_at ? "Submitted" : "Not submitted"}</td>
                    <td className="p-3"><Link className="rounded border border-neutral-200 px-3 py-1.5 text-xs font-bold text-neutral-700" href={`${basePath}/${row.id}`}>Open</Link></td>
                  </tr>
                ))}
                {!rows.length && !loading ? <tr><td className="p-3 text-neutral-500" colSpan={5}>No lab results match the current filters.</td></tr> : null}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
