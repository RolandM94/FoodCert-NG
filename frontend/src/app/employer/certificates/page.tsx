"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Download, ExternalLink, Send } from "lucide-react";
import { CertificateAnalyticsCards, EmployerCertificateTable } from "@/components/certificates/certificate-widgets";
import { PortalShell } from "@/components/layout/portal-shell";
import { CertificateStatusBadge } from "@/components/ui/certificate-status-badge";
import { apiClient, unwrap } from "@/lib/api/client";
import { downloadCsv } from "@/lib/export/csv";

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
  effective_status: string;
  verification_url: string;
  can_download: boolean;
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
  const [actionMessage, setActionMessage] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [expiryWindow, setExpiryWindow] = useState("");

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
    if (expiryWindow) params.set("expiry_window", expiryWindow);
    apiClient.get(`/employers/${employerId}/certificates/?${params.toString()}`)
      .then((res) => {
        const data = unwrap(res.data) as { metrics: Metrics; certificates: CertRow[] };
        setMetrics(data.metrics);
        setCerts(data.certificates);
      })
      .catch(() => setError("Failed to load certificates."))
      .finally(() => setLoading(false));
  }, [employerId, statusFilter, expiryWindow]);

  async function downloadCertificate(row: CertRow) {
    if (!employerId) return;
    setActionMessage("");
    try {
      const response = await apiClient.get(`/employers/${employerId}/certificates/${row.id}/download/`, { responseType: "blob" });
      const url = window.URL.createObjectURL(response.data as Blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${row.certificate_number}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      setActionMessage("Could not download certificate.");
    }
  }

  async function sendReminder(row: CertRow) {
    if (!employerId) return;
    setActionMessage("");
    try {
      await apiClient.post(`/employers/${employerId}/certificates/${row.id}/send-renewal-reminder/`);
      setActionMessage(`Renewal reminder sent to ${row.food_handler_name}.`);
    } catch {
      setActionMessage("Could not send renewal reminder.");
    }
  }

  return (
    <PortalShell role="employer" title="Certificates" description="Monitor certificate status, expiry dates, and compliance across your food handlers.">
      {loading && <p className="text-neutral-500 text-sm">Loading...</p>}
      {error && <div className="rounded-lg border border-danger-100 bg-danger-50 p-4 text-sm font-semibold text-danger-700">{error}</div>}
      {actionMessage && <div className="mb-4 rounded-lg border border-neutral-200 bg-white p-3 text-sm font-semibold text-neutral-700 shadow-sm">{actionMessage}</div>}

      {metrics && (
        <>
          <div className="mb-5">
            <CertificateAnalyticsCards cards={[
              { label: "Total", value: metrics.total },
              { label: "Active", value: metrics.active },
              { label: "Expired", value: metrics.expired, tone: "warning" },
              { label: "Expiring <=30d", value: metrics.expiring_30d, tone: "warning" },
              { label: "Expiring <=7d", value: metrics.expiring_7d, tone: "warning" },
              { label: "Revoked", value: metrics.revoked, tone: "danger" },
            ]} />
          </div>

          <div className="mb-4 grid gap-3 md:grid-cols-[180px_180px_auto]">
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All statuses</option>
              <option value="active">Active</option>
              <option value="expired">Expired</option>
              <option value="suspended">Suspended</option>
              <option value="revoked">Revoked</option>
            </select>
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={expiryWindow} onChange={(e) => setExpiryWindow(e.target.value)}>
              <option value="">Any expiry</option>
              <option value="7">Expiring 7d</option>
              <option value="30">Expiring 30d</option>
              <option value="expired">Expired</option>
            </select>
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded border border-neutral-200 bg-white px-3 text-sm font-bold text-neutral-700 hover:bg-neutral-50 disabled:opacity-50"
              disabled={!certs.length}
              onClick={() => downloadCsv("employer-certificates.csv", certs, [
                { header: "Certificate", value: (row) => row.certificate_number },
                { header: "Food handler", value: (row) => row.food_handler_name },
                { header: "Branch", value: (row) => row.branch_name || "" },
                { header: "Facility", value: (row) => row.facility_name },
                { header: "State", value: (row) => row.issuing_state_name },
                { header: "Issue date", value: (row) => row.issue_date },
                { header: "Expiry date", value: (row) => row.expiry_date },
                { header: "Status", value: (row) => row.effective_status || row.status },
              ])}
              type="button"
            >
              <Download size={16} />
              Export
            </button>
          </div>

          <EmployerCertificateTable<CertRow>
            columns={[
              { key: "certificate", header: "Certificate", render: (c) => <div><p className="font-mono text-xs font-bold text-neutral-800">{c.certificate_number}</p><p className="text-xs text-neutral-500 sm:hidden">{c.food_handler_name}</p></div> },
              { key: "handler", header: "Handler", render: (c) => <div><p className="font-semibold text-neutral-800">{c.food_handler_name}</p>{c.branch_name ? <p className="text-xs text-neutral-500">{c.branch_name}</p> : null}</div> },
              { key: "facility", header: "Facility", render: (c) => c.facility_name },
              { key: "expiry", header: "Expiry", render: (c) => new Date(c.expiry_date).toLocaleDateString("en-NG") },
              { key: "status", header: "Status", render: (c) => <CertificateStatusBadge status={c.effective_status || c.status} /> },
              { key: "actions", header: "Actions", render: (c) => <div className="flex flex-wrap gap-2"><a className="inline-flex h-8 items-center gap-1 rounded border border-neutral-200 px-2 text-xs font-bold text-neutral-700 hover:bg-neutral-50" href={c.verification_url}><ExternalLink size={13} /> Verify</a><button className="inline-flex h-8 items-center gap-1 rounded border border-neutral-200 px-2 text-xs font-bold text-neutral-700 hover:bg-neutral-50 disabled:opacity-50" disabled={!c.can_download} onClick={() => void downloadCertificate(c)} type="button"><Download size={13} /> PDF</button><button className="inline-flex h-8 items-center gap-1 rounded border border-warning-100 px-2 text-xs font-bold text-warning-700 hover:bg-warning-50" onClick={() => void sendReminder(c)} type="button"><Send size={13} /> Remind</button></div> },
            ]}
            rows={certs}
            empty="No certificates found."
          />
        </>
      )}
    </PortalShell>
  );
}
