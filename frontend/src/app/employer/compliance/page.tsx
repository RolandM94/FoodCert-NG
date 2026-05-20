"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { FitnessStatusBadge } from "@/components/ui/fitness-status-badge";
import { apiClient, unwrap } from "@/lib/api/client";

type ExcludedHandler = {
  food_handler_id: string;
  food_handler_name: string;
  branch_name?: string;
  clearance_status: string;
  suspected_condition: string;
  exclusion_start_date?: string;
  earliest_return_date?: string;
};

export default function Page() {
  const router = useRouter();
  const [excluded, setExcluded] = useState<ExcludedHandler[]>([]);
  const [stats, setStats] = useState({ total: 0, fit: 0, excluded: 0, pending: 0, cleared: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("foodcert_access_token");
    if (!token) { router.push("/login"); return; }
    apiClient.get("/employers/me/").then((res) => {
      const empId = (unwrap(res.data) as { id: string }).id;
      // Load food handlers for stats
      apiClient.get(`/employers/${empId}/food-handlers/`).then((r2) => {
        const handlers = unwrap(r2.data) as { fitness_status: string; full_name: string }[];
        const fit = handlers.filter((h: { fitness_status: string }) => h.fitness_status === "fit_to_handle_food").length;
        const excl = handlers.filter((h: { fitness_status: string }) => h.fitness_status === "excluded_from_food_handling").length;
        setStats((prev) => ({ ...prev, total: handlers.length, fit, excluded: excl, pending: handlers.filter((h: { fitness_status: string }) => h.fitness_status === "return_to_work_pending").length, cleared: handlers.filter((h: { fitness_status: string }) => h.fitness_status === "cleared_to_return").length }));
      }).catch(() => {});
      // Load illness reports
      apiClient.get(`/employers/${empId}/illness-reports/`).then((r3) => {
        const reports = unwrap(r3.data) as ExcludedHandler[];
        setExcluded(reports.filter((r: ExcludedHandler) => r.clearance_status !== "cleared"));
      }).catch(() => {}).finally(() => setLoading(false));
    }).catch(() => {
      setError("Failed to load compliance data.");
      setLoading(false);
    });
  }, [router]);

  return (
    <PortalShell role="employer" title="Compliance" description="Monitor return-to-work status, excluded handlers, and regulatory compliance.">
      {loading && <p className="text-sm text-slate-500">Loading...</p>}
      {error && <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm font-semibold text-rose-700">{error}</div>}

      {!loading && (
        <>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5 mb-5">
            <div className="rounded-lg border border-slate-200 bg-white p-4 text-center"><p className="text-2xl font-bold text-slate-950">{stats.total}</p><p className="text-xs font-semibold text-slate-500">Total Handlers</p></div>
            <div className="rounded-lg border border-slate-200 bg-white p-4 text-center"><p className="text-2xl font-bold text-emerald-700">{stats.fit}</p><p className="text-xs font-semibold text-slate-500">Fit to Handle Food</p></div>
            <div className="rounded-lg border border-slate-200 bg-white p-4 text-center"><p className="text-2xl font-bold text-red-600">{stats.excluded}</p><p className="text-xs font-semibold text-slate-500">Excluded</p></div>
            <div className="rounded-lg border border-slate-200 bg-white p-4 text-center"><p className="text-2xl font-bold text-amber-600">{stats.pending}</p><p className="text-xs font-semibold text-slate-500">RTW Pending</p></div>
            <div className="rounded-lg border border-slate-200 bg-white p-4 text-center"><p className="text-2xl font-bold text-emerald-600">{stats.cleared}</p><p className="text-xs font-semibold text-slate-500">Cleared</p></div>
          </div>

          <h3 className="text-sm font-bold text-slate-950 mb-3 flex items-center gap-2"><AlertCircle size={16} className="text-amber-500" /> Excluded & Return-to-Work Pending</h3>
          {excluded.length === 0 ? (
            <div className="rounded-lg border border-slate-200 bg-white p-6 text-center text-sm text-slate-500">All food handlers are either fit or cleared to return to work.</div>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
              <table className="w-full text-sm">
                <thead><tr className="border-b border-slate-100 bg-slate-50 text-left"><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500">Handler</th><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500 hidden sm:table-cell">Condition</th><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500">Excluded Since</th><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500">Clearance</th><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500 hidden md:table-cell">RTW Date</th></tr></thead>
                <tbody className="divide-y divide-slate-50">
                  {excluded.map((r) => (
                    <tr key={r.food_handler_id} className="hover:bg-slate-50/50">
                      <td className="px-4 py-2"><span className="text-xs text-slate-700 font-medium">{r.food_handler_name}</span>{r.branch_name && <span className="text-[10px] text-slate-400 block">{r.branch_name}</span>}</td>
                      <td className="px-4 py-2 hidden sm:table-cell"><span className="text-xs text-slate-600 capitalize">{r.suspected_condition?.replace(/_/g, " ")}</span></td>
                      <td className="px-4 py-2"><span className="text-xs text-slate-600">{r.exclusion_start_date ? new Date(r.exclusion_start_date).toLocaleDateString() : "—"}</span></td>
                      <td className="px-4 py-2"><FitnessStatusBadge status={r.clearance_status || "pending"} /></td>
                      <td className="px-4 py-2 hidden md:table-cell"><span className="text-xs text-slate-500">{r.earliest_return_date ? new Date(r.earliest_return_date).toLocaleDateString() : "—"}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <p className="mt-4 text-xs text-slate-400">Illness reports are reviewed by a doctor. Return-to-work clearance can only be granted by authorised medical or regulatory users.</p>
        </>
      )}
    </PortalShell>
  );
}
