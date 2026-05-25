"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, BadgeCheck, Copy, Download, ExternalLink } from "lucide-react";

import { CertificatePreview, CertificateRenewalCard, QRCodeDisplay } from "@/components/certificates/certificate-widgets";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { downloadCertificatePdf, listCertificateRequests, listCertificates, startCertificateRenewal } from "@/lib/api/certificates";
import type { Certificate, CertificateRequest } from "@/types/certificates";

function dateLabel(value?: string) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium" }).format(new Date(value));
}

function latestByDate<T extends { created_at: string }>(rows: T[]) {
  return [...rows].sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at))[0];
}

export default function Page() {
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [requests, setRequests] = useState<CertificateRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionMessage, setActionMessage] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [certificateRows, requestRows] = await Promise.all([listCertificates(), listCertificateRequests()]);
      setCertificates(certificateRows);
      setRequests(requestRows);
    } catch {
      setError("Could not load certificate records.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const latestCertificate = useMemo(() => latestByDate(certificates), [certificates]);
  const latestRequest = useMemo(() => latestByDate(requests), [requests]);
  const isRenewable = latestCertificate && ["expired", "active"].includes(latestCertificate.effective_status);

  async function handleDownload(certificate: Certificate) {
    setActionMessage("");
    try {
      await downloadCertificatePdf(certificate.id, certificate.certificate_number);
    } catch {
      setActionMessage("Could not download certificate PDF.");
    }
  }

  async function handleCopy(url: string) {
    try {
      await navigator.clipboard.writeText(url);
      setActionMessage("Verification link copied.");
    } catch {
      setActionMessage("Could not copy verification link.");
    }
  }

  async function handleRenewal(certificate: Certificate) {
    setActionMessage("");
    try {
      const updated = await startCertificateRenewal(certificate.id);
      setCertificates((current) => current.map((row) => row.id === updated.id ? updated : row));
      setActionMessage("Renewal started. Open assessments to begin a fresh medical assessment.");
    } catch {
      setActionMessage("Could not start certificate renewal.");
    }
  }

  return (
    <PortalShell role="food_handler" title="Certificate" description="Access issued certificate details, QR verification, and State validation status.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading certificate...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} />{error}</div> : null}
        {actionMessage ? <div className="rounded-lg border border-slate-200 bg-white p-3 text-sm font-semibold text-slate-700 shadow-sm">{actionMessage}</div> : null}

        {latestCertificate ? (
          <>
            <CertificatePreview certificate={latestCertificate} />
            <section className="grid gap-4 lg:grid-cols-[1fr_0.8fr]">
              <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                <h2 className="text-sm font-bold text-slate-950">Certificate Details</h2>
                <dl className="mt-4 grid gap-3 text-sm">
                  <div className="flex items-center justify-between gap-3"><dt className="text-slate-500">Facility</dt><dd className="font-bold text-slate-950">{latestCertificate.facility_name || "Medical facility"}</dd></div>
                  <div className="flex items-center justify-between gap-3"><dt className="text-slate-500">Doctor</dt><dd className="font-bold text-slate-950">{latestCertificate.doctor_name || "Doctor"}</dd></div>
                  <div className="flex items-center justify-between gap-3"><dt className="text-slate-500">State</dt><dd className="font-bold text-slate-950">{latestCertificate.issuing_state_name || "Issuing state"}</dd></div>
                  <div className="flex items-center justify-between gap-3"><dt className="text-slate-500">Issued</dt><dd className="font-bold text-slate-950">{dateLabel(latestCertificate.issue_date)}</dd></div>
                  <div className="flex items-center justify-between gap-3"><dt className="text-slate-500">Renewal</dt><dd className="font-bold capitalize text-slate-950">{latestCertificate.renewal_status?.replaceAll("_", " ") || "not started"}</dd></div>
                  <div className="flex items-center justify-between gap-3"><dt className="text-slate-500">Status</dt><dd><StatusBadge status={latestCertificate.effective_status} /></dd></div>
                </dl>
                <div className="mt-5 flex flex-wrap gap-2">
                  {latestCertificate.pdf_url ? <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white" onClick={() => void handleDownload(latestCertificate)} type="button"><Download size={16} /> PDF</button> : null}
                  {latestCertificate.verification_url ? <a className="inline-flex h-10 items-center gap-2 rounded border border-slate-200 px-4 text-sm font-bold text-slate-700" href={latestCertificate.verification_url}><ExternalLink size={16} /> Verify</a> : null}
                  {latestCertificate.verification_url ? <button className="inline-flex h-10 items-center gap-2 rounded border border-slate-200 px-4 text-sm font-bold text-slate-700" onClick={() => void handleCopy(latestCertificate.verification_url)} type="button"><Copy size={16} /> Share</button> : null}
                  <Link className="inline-flex h-10 items-center gap-2 rounded border border-slate-200 px-4 text-sm font-bold text-slate-700" href="/food-handler/assessments">Assessments</Link>
                </div>
                {isRenewable ? <div className="mt-4"><CertificateRenewalCard disabled={!isRenewable} onRenew={() => void handleRenewal(latestCertificate)} status={latestCertificate.renewal_status} /></div> : null}
              </div>
              <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                <h2 className="text-sm font-bold text-slate-950">QR Code</h2>
                <div className="mt-4"><QRCodeDisplay qrUrl={latestCertificate.qr_code_url} /></div>
              </div>
            </section>
          </>
        ) : (
          <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-start gap-3">
              <BadgeCheck className="text-brand-deep" size={22} />
              <div>
                <h2 className="text-sm font-bold text-slate-950">No Certificate Issued</h2>
                <p className="mt-2 text-sm text-slate-600">Latest request: {latestRequest ? latestRequest.status.replaceAll("_", " ") : "No request submitted"}</p>
                {latestRequest ? <p className="mt-1 text-xs text-slate-500">Requested {dateLabel(latestRequest.created_at)}</p> : null}
                <Link className="mt-4 inline-flex h-10 items-center rounded bg-brand-green px-4 text-sm font-bold text-white" href="/food-handler/assessments">Open assessments</Link>
              </div>
            </div>
          </section>
        )}
      </div>
    </PortalShell>
  );
}
