"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { listLabRequests } from "@/lib/api/lab-tests";
import type { LabTest } from "@/types/assessments";

function label(value?: string) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

const REQUEST_STATUSES = [
  ["", "All statuses"],
  ["sample_collection_pending", "Sample pending"],
  ["sample_collected", "Sample collected"],
  ["positive", "Positive"],
  ["negative", "Negative"],
  ["inconclusive", "Inconclusive"],
  ["result_uploaded", "Result uploaded"],
  ["submitted_to_doctor", "Submitted to doctor"],
  ["reviewed", "Reviewed"],
];

export function LabRequestBoard({
  title,
  description,
  basePath = "/lab/test-requests",
  initialStatus = "",
}: {
  title: string;
  description: string;
  basePath?: string;
  initialStatus?: string;
}) {
  const [rows, setRows] = useState<LabTest[]>([]);
  const [status, setStatus] = useState(initialStatus);
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

  useEffect(() => {
    setStatus(initialStatus);
  }, [initialStatus]);

  const metrics = useMemo(() => ({
    assigned: rows.length,
    pendingCollection: rows.filter((row) => row.status === "sample_collection_pending").length,
    pendingUpload: rows.filter((row) => ["sample_collected", "in_progress", "result_uploaded"].includes(row.status)).length,
    submitted: rows.filter((row) => Boolean(row.submitted_to_doctor_at)).length,
  }), [rows]);

  return (
    <PortalShell role="lab_staff" title={title} description={description}>
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading lab requests...</p> : null}

        <section className="grid gap-3 md:grid-cols-4">
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-neutral-500">Assigned</p><p className="text-2xl font-bold text-neutral-900">{metrics.assigned}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-neutral-500">Sample collection</p><p className="text-2xl font-bold text-neutral-900">{metrics.pendingCollection}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-neutral-500">Result work</p><p className="text-2xl font-bold text-neutral-900">{metrics.pendingUpload}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-neutral-500">Submitted</p><p className="text-2xl font-bold text-neutral-900">{metrics.submitted}</p></div>
        </section>

        <section className="flex items-center justify-between gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <p className="text-sm font-bold text-neutral-900">{rows.length} requests</p>
          <div className="flex flex-wrap items-center gap-2">
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
              {REQUEST_STATUSES.map(([value, text]) => <option key={value} value={value}>{text}</option>)}
            </select>
            <button className="inline-flex h-10 items-center gap-2 rounded border border-neutral-200 px-3 text-sm font-bold text-neutral-700" type="button" onClick={() => void loadData()}><RefreshCw size={16} /> Refresh</button>
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-neutral-50 text-xs font-bold uppercase text-neutral-500">
                <tr><th className="p-3">Food handler</th><th className="p-3">Test</th><th className="p-3">Assignment</th><th className="p-3">Status</th><th className="p-3">Action</th></tr>
              </thead>
              <tbody className="divide-y divide-neutral-200">
                {rows.length ? rows.map((row) => (
                  <tr key={row.id}>
                    <td className="p-3"><p className="font-bold text-neutral-900">{row.food_handler_name}</p><p className="text-xs text-neutral-500">{row.facility_name}</p></td>
                    <td className="p-3 capitalize">
                      <p className="font-semibold text-neutral-900">{row.test_name || label(row.test_type)}</p>
                      {row.parent_lab_test ? <p className="text-xs font-semibold text-warning-700">Repeat</p> : null}
                      {row.is_flagged ? <p className="text-xs font-semibold text-warning-700">Flagged</p> : null}
                    </td>
                    <td className="p-3 text-sm text-neutral-600">
                      <p>{row.assigned_lab_staff_name || "Unassigned user"}</p>
                      <p className="text-xs text-neutral-500">{row.assigned_lab_unit_name || "No lab unit"}</p>
                    </td>
                    <td className="p-3"><StatusBadge status={row.status} /></td>
                    <td className="p-3"><Link className="rounded border border-neutral-200 px-3 py-1.5 text-xs font-bold text-neutral-700" href={`${basePath}/${row.id}`}>Open</Link></td>
                  </tr>
                )) : <tr><td className="p-3 text-neutral-500" colSpan={5}>No requests yet.</td></tr>}
              </tbody>
            </table>
          </div>
        </section>
        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}
      </div>
    </PortalShell>
  );
}
