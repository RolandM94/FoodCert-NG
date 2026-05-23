"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, FlaskConical, RefreshCw, Upload } from "lucide-react";

import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { listLabRequests } from "@/lib/api/lab-tests";
import type { LabTest } from "@/types/assessments";

function label(value?: string) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

export default function Page() {
  const [rows, setRows] = useState<LabTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setRows(await listLabRequests());
    } catch {
      setError("Could not load lab dashboard.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const metrics = useMemo(() => ({
    queue: rows.filter((row) => ["requested", "sample_collection_pending"].includes(row.status)).length,
    collected: rows.filter((row) => row.status === "sample_collected").length,
    submitted: rows.filter((row) => Boolean(row.submitted_to_doctor_at)).length,
    flagged: rows.filter((row) => row.is_flagged).length,
  }), [rows]);

  return (
    <PortalShell role="lab_staff" title="Lab Dashboard" description="Manage sample collection, result entry, uploads, and pending doctor review.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading lab dashboard...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} />{error}</div> : null}
        <section className="grid gap-3 md:grid-cols-4">
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><FlaskConical className="text-brand-deep" size={18} /><p className="mt-2 text-xs font-bold uppercase text-slate-500">Queue</p><p className="text-2xl font-bold text-slate-950">{metrics.queue}</p></div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><RefreshCw className="text-brand-deep" size={18} /><p className="mt-2 text-xs font-bold uppercase text-slate-500">Collected</p><p className="text-2xl font-bold text-slate-950">{metrics.collected}</p></div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><Upload className="text-brand-deep" size={18} /><p className="mt-2 text-xs font-bold uppercase text-slate-500">Submitted</p><p className="text-2xl font-bold text-slate-950">{metrics.submitted}</p></div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><AlertCircle className="text-brand-deep" size={18} /><p className="mt-2 text-xs font-bold uppercase text-slate-500">Flagged</p><p className="text-2xl font-bold text-slate-950">{metrics.flagged}</p></div>
        </section>
        <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between gap-3 border-b border-slate-200 p-4">
            <h2 className="text-sm font-bold text-slate-950">Recent Requests</h2>
            <button className="inline-flex h-9 items-center gap-2 rounded border border-slate-200 px-3 text-xs font-bold text-slate-700" type="button" onClick={() => void loadData()}><RefreshCw size={14} /> Refresh</button>
          </div>
          <div className="divide-y divide-slate-200">
            {rows.slice(0, 8).map((row) => (
              <Link className="flex items-center justify-between gap-3 p-4 text-sm hover:bg-slate-50" href={`/lab/test-requests/${row.id}`} key={row.id}>
                <div><p className="font-bold text-slate-950">{row.food_handler_name}</p><p className="text-xs text-slate-500">{row.test_name || label(row.test_type)}</p></div>
                <StatusBadge status={row.status} />
              </Link>
            ))}
            {!rows.length && !loading ? <p className="p-4 text-sm text-slate-500">No lab requests yet.</p> : null}
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
