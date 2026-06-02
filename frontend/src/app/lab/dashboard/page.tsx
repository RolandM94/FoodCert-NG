"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { AlertCircle, Clock, FlaskConical, RefreshCw, Syringe, Upload } from "lucide-react";

import { KPICard } from "@/components/dashboards";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { apiClient } from "@/lib/api/client";

interface LabDashboardData {
  lab_staff: { id: string; name: string; facility: string };
  cards: Record<string, number | string>;
  sections: {
    pending_sample_collection: Array<{ id: string; food_handler: string; test_name: string; status: string; created_at: string }>;
    pending_result_upload: Array<{ id: string; food_handler: string; test_name: string; status: string }>;
    recent_results: Array<{ id: string; food_handler: string; test_name: string; result_summary: string; submitted_at: string }>;
    turnaround_chart: Array<{ month: string; avg_hours: number }>;
  };
}

export default function Page() {
  const [data, setData] = useState<LabDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await apiClient.get("/dashboard/lab/");
      setData(res.data.data);
    } catch {
      setError("Could not load lab dashboard.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  return (
    <PortalShell role="lab_staff" title="Lab Dashboard" description="Manage sample collection, result entry, uploads, and turnaround monitoring.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading dashboard...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} />{error}</div> : null}

        <section className="grid gap-3 md:grid-cols-4">
          <KPICard label="Pending Requests" value={data?.cards?.lab_requests_pending ?? 0} icon={FlaskConical} />
          <KPICard label="Samples to Collect" value={data?.cards?.samples_pending_collection ?? 0} icon={Syringe} subtitle="Collection pending" />
          <KPICard label="Results to Upload" value={data?.cards?.results_pending_upload ?? 0} icon={Upload} subtitle="Upload pending" />
          <KPICard label="Avg Turnaround" value={data?.cards?.average_turnaround_time ? `${data.cards.average_turnaround_time}h` : "—"} icon={Clock} subtitle="Hours" />
        </section>

        <div className="grid gap-5 lg:grid-cols-2">
          <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
            <div className="flex items-center justify-between gap-3 border-b border-slate-200 p-4">
              <h2 className="text-sm font-bold text-slate-950">Pending Sample Collection</h2>
              <span className="inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-800">{data?.sections?.pending_sample_collection?.length ?? 0}</span>
            </div>
            <div className="divide-y divide-slate-200">
              {data?.sections?.pending_sample_collection?.length ? (
                data.sections.pending_sample_collection.slice(0, 6).map((item) => (
                  <Link className="flex items-center justify-between gap-3 p-4 text-sm hover:bg-slate-50" href={`/lab/test-requests/${item.id}`} key={item.id}>
                    <div><p className="font-bold text-slate-950">{item.food_handler}</p><p className="text-xs text-slate-500">{item.test_name}</p></div>
                    <StatusBadge status={item.status} />
                  </Link>
                ))
              ) : (
                <p className="p-4 text-sm text-slate-500">No pending samples.</p>
              )}
            </div>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
            <div className="flex items-center justify-between gap-3 border-b border-slate-200 p-4">
              <h2 className="text-sm font-bold text-slate-950">Results to Upload</h2>
              <span className="inline-flex items-center rounded-full bg-sky-100 px-2 py-0.5 text-xs font-bold text-sky-800">{data?.sections?.pending_result_upload?.length ?? 0}</span>
            </div>
            <div className="divide-y divide-slate-200">
              {data?.sections?.pending_result_upload?.length ? (
                data.sections.pending_result_upload.slice(0, 6).map((item) => (
                  <Link className="flex items-center justify-between gap-3 p-4 text-sm hover:bg-slate-50" href={`/lab/test-requests/${item.id}`} key={item.id}>
                    <div><p className="font-bold text-slate-950">{item.food_handler}</p><p className="text-xs text-slate-500">{item.test_name}</p></div>
                    <StatusBadge status={item.status} />
                  </Link>
                ))
              ) : (
                <p className="p-4 text-sm text-slate-500">No results pending upload.</p>
              )}
            </div>
          </section>
        </div>

        <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between gap-3 border-b border-slate-200 p-4">
            <h2 className="text-sm font-bold text-slate-950">Recent Results</h2>
            <button className="inline-flex h-9 items-center gap-2 rounded border border-slate-200 px-3 text-xs font-bold text-slate-700" type="button" onClick={() => void loadData()}>
              <RefreshCw size={14} /> Refresh
            </button>
          </div>
          <div className="divide-y divide-slate-200">
            {data?.sections?.recent_results?.length ? (
              data.sections.recent_results.map((item) => (
                <div className="flex items-center justify-between gap-3 p-4 text-sm" key={item.id}>
                  <div><p className="font-bold text-slate-950">{item.food_handler}</p><p className="text-xs text-slate-500">{item.test_name} · {item.result_summary}</p></div>
                  <Link className="text-xs font-bold text-brand-green" href={`/lab/test-requests/${item.id}`}>View</Link>
                </div>
              ))
            ) : (
              <p className="p-4 text-sm text-slate-500">No results submitted yet.</p>
            )}
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
