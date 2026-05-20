"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Syringe, CheckCircle2 } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { VaccinationStatusBadge } from "@/components/ui/certificate-status-badge";
import { apiClient, unwrap } from "@/lib/api/client";

type VaxRow = {
  food_handler_id: string;
  food_handler_name: string;
  branch_name?: string;
  typhoid_status: string;
  typhoid_expiry_date?: string;
  hepatitis_a_dose_1_date?: string;
  hepatitis_a_dose_2_date?: string;
  hepatitis_a_status: string;
  next_due_date?: string;
};

type VaxMetrics = {
  total_handlers: number;
  typhoid_valid: number;
  typhoid_expired: number;
  typhoid_missing: number;
  hepatitis_a_dose_1: number;
  hepatitis_a_complete: number;
  hepatitis_a_dose_2_pending: number;
  hepatitis_a_missing: number;
};

export default function Page() {
  const router = useRouter();
  const [employerId, setEmployerId] = useState<string | null>(null);
  const [rows, setRows] = useState<VaxRow[]>([]);
  const [metrics, setMetrics] = useState<VaxMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("foodcert_access_token");
    if (!token) { router.push("/login"); return; }
    apiClient.get("/employers/me/").then((res) => setEmployerId((unwrap(res.data) as { id: string }).id)).catch(() => {});
  }, [router]);

  useEffect(() => {
    if (!employerId) return;
    setLoading(true);
    apiClient.get(`/employers/${employerId}/vaccinations/`)
      .then((res) => {
        const data = unwrap(res.data) as { metrics: VaxMetrics; handlers: VaxRow[] };
        setMetrics(data.metrics);
        setRows(data.handlers);
      })
      .catch(() => setError("Failed to load vaccination data."))
      .finally(() => setLoading(false));
  }, [employerId]);

  return (
    <PortalShell role="employer" title="Vaccination Compliance" description="Track typhoid and hepatitis A vaccination status across your food handlers.">
      {loading && <p className="text-slate-500 text-sm">Loading...</p>}
      {error && <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm font-semibold text-rose-700">{error}</div>}

      {metrics && (
        <>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 mb-5">
            <div className="rounded-lg border border-slate-200 bg-white p-4">
              <p className="text-xs font-bold uppercase text-slate-500 mb-2">Typhoid</p>
              <div className="flex gap-3 text-sm">
                <span className="text-emerald-700 font-bold">{metrics.typhoid_valid} valid</span>
                <span className="text-red-600 font-bold">{metrics.typhoid_expired} expired</span>
                <span className="text-slate-400">{metrics.typhoid_missing} missing</span>
              </div>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-4">
              <p className="text-xs font-bold uppercase text-slate-500 mb-2">Hepatitis A</p>
              <div className="flex gap-3 text-sm">
                <span className="text-emerald-700 font-bold">{metrics.hepatitis_a_complete} complete</span>
                <span className="text-blue-600 font-bold">{metrics.hepatitis_a_dose_1} dose 1</span>
                <span className="text-amber-600 font-bold">{metrics.hepatitis_a_dose_2_pending} pending</span>
                <span className="text-slate-400">{metrics.hepatitis_a_missing} missing</span>
              </div>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-4 flex items-center gap-3">
              <CheckCircle2 size={18} className="text-emerald-500" />
              <div><p className="text-xs text-slate-500">Total handlers</p><p className="text-lg font-bold text-slate-950">{metrics.total_handlers}</p></div>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-4 flex items-center gap-3">
              <Syringe size={18} className="text-brand-deep" />
              <div><p className="text-xs text-slate-500">Coverage</p><p className="text-lg font-bold text-slate-950">{metrics.total_handlers > 0 ? Math.round((metrics.typhoid_valid / metrics.total_handlers) * 100) : 0}% typhoid</p></div>
            </div>
          </div>

          <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-slate-100 bg-slate-50 text-left"><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500">Handler</th><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500">Typhoid</th><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500">Typhoid Expiry</th><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500">Hep. A Dose 1</th><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500">Hep. A Dose 2</th><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500">Hep. A Status</th><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500">Next Due</th></tr></thead>
              <tbody className="divide-y divide-slate-50">
                {rows.map((r) => (
                  <tr key={r.food_handler_id} className="hover:bg-slate-50/50">
                    <td className="px-4 py-2"><span className="text-xs text-slate-700 font-medium">{r.food_handler_name}</span>{r.branch_name && <span className="text-[10px] text-slate-400 block">{r.branch_name}</span>}</td>
                    <td className="px-4 py-2"><VaccinationStatusBadge status={r.typhoid_status} /></td>
                    <td className="px-4 py-2"><span className="text-xs text-slate-500">{r.typhoid_expiry_date ? new Date(r.typhoid_expiry_date).toLocaleDateString() : "—"}</span></td>
                    <td className="px-4 py-2"><span className="text-xs text-slate-500">{r.hepatitis_a_dose_1_date ? new Date(r.hepatitis_a_dose_1_date).toLocaleDateString() : "—"}</span></td>
                    <td className="px-4 py-2"><span className="text-xs text-slate-500">{r.hepatitis_a_dose_2_date ? new Date(r.hepatitis_a_dose_2_date).toLocaleDateString() : "—"}</span></td>
                    <td className="px-4 py-2"><VaccinationStatusBadge status={r.hepatitis_a_status} /></td>
                    <td className="px-4 py-2"><span className="text-xs text-slate-500">{r.next_due_date ? new Date(r.next_due_date).toLocaleDateString() : "—"}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
            {rows.length === 0 && <p className="py-8 text-center text-sm text-slate-400">No vaccination records found.</p>}
          </div>
        </>
      )}
    </PortalShell>
  );
}
