"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, Award, ClipboardList, Download, RefreshCw } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { listCertificateRequests, listCertificates } from "@/lib/api/certificates";
import { getCurrentMedicalFacility } from "@/lib/api/facilities";
import type { Certificate, CertificateRequest, CertificateRequestStatus } from "@/types/certificates";
import type { MedicalFacility } from "@/types/facilities";

const REQUEST_TABS: Array<{ value: CertificateRequestStatus | "all"; label: string }> = [
  { value: "all", label: "All validations" },
  { value: "pending_validation", label: "Pending State" },
  { value: "correction_requested", label: "Clarification" },
  { value: "approved", label: "Approved" },
  { value: "rejected", label: "Rejected" },
];

function label(value?: string) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

function formatDate(value?: string) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium" }).format(new Date(value));
}

export default function Page() {
  const [facility, setFacility] = useState<MedicalFacility | null>(null);
  const [requests, setRequests] = useState<CertificateRequest[]>([]);
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [activeTab, setActiveTab] = useState<CertificateRequestStatus | "all">("pending_validation");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const profile = await getCurrentMedicalFacility();
      const [requestRows, certificateRows] = await Promise.all([
        listCertificateRequests({ assessment__facility: profile.id }),
        listCertificates({ facility: profile.id }),
      ]);
      setFacility(profile);
      setRequests(requestRows);
      setCertificates(certificateRows);
    } catch {
      setError("Could not load certificate validation records.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const filteredRequests = useMemo(() => {
    if (activeTab === "all") return requests;
    return requests.filter((row) => row.status === activeTab);
  }, [activeTab, requests]);

  const metrics = useMemo(() => ({
    pending: requests.filter((row) => row.status === "pending_validation").length,
    clarification: requests.filter((row) => row.status === "correction_requested").length,
    approved: requests.filter((row) => row.status === "approved").length,
    issued: certificates.filter((row) => row.effective_status === "active").length,
  }), [certificates, requests]);

  return (
    <PortalShell role="facility_admin" title="Certificates" description="Track State certificate validation, clarification requests, issued certificates, and public verification links.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading certificate records...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} />{error}</div> : null}

        <section className="grid gap-3 md:grid-cols-4">
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><ClipboardList className="text-brand-deep" size={18} /><p className="mt-2 text-xs font-bold uppercase text-slate-500">Pending State</p><p className="text-2xl font-bold text-slate-950">{metrics.pending}</p></div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><AlertCircle className="text-brand-deep" size={18} /><p className="mt-2 text-xs font-bold uppercase text-slate-500">Clarifications</p><p className="text-2xl font-bold text-slate-950">{metrics.clarification}</p></div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><RefreshCw className="text-brand-deep" size={18} /><p className="mt-2 text-xs font-bold uppercase text-slate-500">Approved</p><p className="text-2xl font-bold text-slate-950">{metrics.approved}</p></div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><Award className="text-brand-deep" size={18} /><p className="mt-2 text-xs font-bold uppercase text-slate-500">Issued Active</p><p className="text-2xl font-bold text-slate-950">{metrics.issued}</p></div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 p-4">
            <div>
              <h2 className="text-sm font-bold text-slate-950">State Validation Queue</h2>
              <p className="text-xs text-slate-500">{facility?.facility_name || "Current facility"}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {REQUEST_TABS.map((tab) => (
                <button className={`h-9 rounded border px-3 text-xs font-bold ${activeTab === tab.value ? "border-brand-green bg-brand-green text-white" : "border-slate-200 bg-white text-slate-700"}`} key={tab.value} type="button" onClick={() => setActiveTab(tab.value)}>
                  {tab.label}
                </button>
              ))}
              <button className="inline-flex h-9 items-center gap-2 rounded border border-slate-200 px-3 text-xs font-bold text-slate-700" type="button" onClick={() => void loadData()}><RefreshCw size={14} /> Refresh</button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs font-bold uppercase text-slate-500">
                <tr><th className="p-3">Food handler</th><th className="p-3">Status</th><th className="p-3">State feedback</th><th className="p-3">Facility response</th><th className="p-3">Action</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {filteredRequests.length ? filteredRequests.map((row) => (
                  <tr key={row.id}>
                    <td className="p-3"><p className="font-bold text-slate-950">{row.food_handler_name}</p><p className="text-xs text-slate-500">{row.issuing_state_name} · submitted {formatDate(row.created_at)}</p></td>
                    <td className="p-3"><StatusBadge status={row.status} /></td>
                    <td className="max-w-xs p-3 text-slate-700">{row.review_notes || "No State notes yet."}</td>
                    <td className="max-w-xs p-3 text-slate-700">{row.facility_response || "No response submitted."}</td>
                    <td className="p-3"><Link className="rounded border border-slate-200 px-3 py-1.5 text-xs font-bold text-slate-700" href={`/facility/assessments/${row.assessment}`}>{row.status === "correction_requested" ? "Respond" : "Open"}</Link></td>
                  </tr>
                )) : (
                  <tr><td className="p-3 text-slate-500" colSpan={5}>No validation records in this view.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 p-4">
            <h2 className="text-sm font-bold text-slate-950">Issued Certificates</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs font-bold uppercase text-slate-500">
                <tr><th className="p-3">Certificate</th><th className="p-3">Food handler</th><th className="p-3">Validity</th><th className="p-3">Verification</th><th className="p-3">PDF</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {certificates.length ? certificates.map((row) => (
                  <tr key={row.id}>
                    <td className="p-3"><p className="font-bold text-slate-950">{row.certificate_number}</p><p className="text-xs text-slate-500">{label(row.status)}</p></td>
                    <td className="p-3">{row.food_handler_name}</td>
                    <td className="p-3"><StatusBadge status={row.effective_status} /><p className="mt-1 text-xs text-slate-500">Expires {formatDate(row.expiry_date)}</p></td>
                    <td className="p-3">{row.verification_url ? <a className="font-bold text-brand-deep underline" href={row.verification_url} rel="noreferrer" target="_blank">Verify</a> : "Not available"}</td>
                    <td className="p-3">{row.pdf_url ? <a className="inline-flex items-center gap-1 font-bold text-brand-deep underline" href={row.pdf_url} rel="noreferrer" target="_blank"><Download size={14} /> Download</a> : "Not available"}</td>
                  </tr>
                )) : (
                  <tr><td className="p-3 text-slate-500" colSpan={5}>No certificates have been issued for this facility yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
