"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { BadgeCheck, AlertCircle, Clock } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { CertificateStatusBadge } from "@/components/ui/certificate-status-badge";
import { apiClient, unwrap } from "@/lib/api/client";

type CertRow = {
  id: string;
  certificate_number: string;
  food_handler_name: string;
  branch_name?: string;
  facility_name: string;
  issuing_state_name: string;
  issue_date: string;
  expiry_date: string;
  status: string;
};

type Metrics = {
  total: number;
  active: number;
  expired: number;
  expiring_30d: number;
  expiring_7d: number;
  revoked: number;
};

export default function Page() {
  const router = useRouter();
  const [employerId, setEmployerId] = useState<string | null>(null);
  const [certs, setCerts] = useState<CertRow[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("foodcert_access_token");
    if (!token) { router.push("/login"); return; }
    apiClient.get("/employers/me/").then((res) => setEmployerId((unwrap(res.data) as { id: string }).id)).catch(() => {});
  }, [router]);

  useEffect(() => {
    if (!employerId) return;
    setLoading(true);
    const params = new URLSearchParams();
    if (statusFilter) params.set("status", statusFilter);
    apiClient.get(`/employers/${employerId}/certificates/?${params.toString()}`)
      .then((res) => {
        const data = unwrap(res.data) as { metrics: Metrics; certificates: CertRow[] };
        setMetrics(data.metrics);
        setCerts(data.certificates);
      })
      .catch(() => setError("Failed to load certificates."))
      .finally(() => setLoading(false));
  }, [employerId, statusFilter]);

  return (
    <PortalShell role="employer" title="Certificates" description="Monitor certificate status, expiry dates, and compliance across your food handlers.">
      {loading && <p className="text-slate-500 text-sm">Loading...</p>}
      {error && <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm font-semibold text-rose-700">{error}</div>}

      {metrics && (
        <>
          <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-6 mb-5">
            <div className="rounded-lg border border-slate-200 bg-white p-3 text-center"><BadgeCheck size={16} className="mx-auto text-slate-400 mb-1" /><p className="text-xl font-bold text-slate-950">{metrics.total}</p><p className="text-xs font-semibold text-slate-500">Total</p></div>
            <div className="rounded-lg border border-slate-200 bg-white p-3 text-center"><BadgeCheck size={16} className="mx-auto text-slate-400 mb-1" /><p className="text-xl font-bold text-slate-950">{metrics.active}</p><p className="text-xs font-semibold text-slate-500">Active</p></div>
            <div className="rounded-lg border border-slate-200 bg-white p-3 text-center"><AlertCircle size={16} className="mx-auto text-slate-400 mb-1" /><p className="text-xl font-bold text-slate-950">{metrics.expired}</p><p className="text-xs font-semibold text-slate-500">Expired</p></div>
            <div className="rounded-lg border border-slate-200 bg-white p-3 text-center"><Clock size={16} className="mx-auto text-slate-400 mb-1" /><p className="text-xl font-bold text-slate-950">{metrics.expiring_30d}</p><p className="text-xs font-semibold text-slate-500">Expiring ≤30d</p></div>
            <div className="rounded-lg border border-slate-200 bg-white p-3 text-center"><Clock size={16} className="mx-auto text-slate-400 mb-1" /><p className="text-xl font-bold text-slate-950">{metrics.expiring_7d}</p><p className="text-xs font-semibold text-slate-500">Expiring ≤7d</p></div>
            <div className="rounded-lg border border-slate-200 bg-white p-3 text-center"><AlertCircle size={16} className="mx-auto text-slate-400 mb-1" /><p className="text-xl font-bold text-slate-950">{metrics.revoked}</p><p className="text-xs font-semibold text-slate-500">Revoked</p></div>
          </div>

          <div className="flex items-center gap-3 mb-4">
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All statuses</option>
              <option value="active">Active</option>
              <option value="expired">Expired</option>
              <option value="revoked">Revoked</option>
            </select>
          </div>

          <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-slate-100 bg-slate-50 text-left"><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500">Certificate</th><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500 hidden sm:table-cell">Handler</th><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500 hidden md:table-cell">Facility</th><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500 hidden md:table-cell">Issued</th><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500">Expiry</th><th className="px-4 py-2 text-xs font-bold uppercase text-slate-500">Status</th></tr></thead>
              <tbody className="divide-y divide-slate-50">
                {certs.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-50/50">
                    <td className="px-4 py-2"><span className="font-mono text-xs text-slate-700">{c.certificate_number}</span></td>
                    <td className="px-4 py-2 hidden sm:table-cell"><span className="text-xs text-slate-700">{c.food_handler_name}</span>{c.branch_name && <span className="text-[10px] text-slate-400 block">{c.branch_name}</span>}</td>
                    <td className="px-4 py-2 hidden md:table-cell"><span className="text-xs text-slate-500">{c.facility_name}</span></td>
                    <td className="px-4 py-2 hidden md:table-cell"><span className="text-xs text-slate-500">{new Date(c.issue_date).toLocaleDateString()}</span></td>
                    <td className="px-4 py-2"><span className="text-xs text-slate-700">{new Date(c.expiry_date).toLocaleDateString()}</span></td>
                    <td className="px-4 py-2"><CertificateStatusBadge status={c.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
            {certs.length === 0 && <p className="py-8 text-center text-sm text-slate-400">No certificates found.</p>}
          </div>
        </>
      )}
    </PortalShell>
  );
}
