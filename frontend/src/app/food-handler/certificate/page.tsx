"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, BadgeCheck, Download, ExternalLink, QrCode } from "lucide-react";

import { CertificateCard } from "@/components/ui/certificate-card";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { listCertificateRequests, listCertificates } from "@/lib/api/certificates";
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

  return (
    <PortalShell role="food_handler" title="Certificate" description="Access issued certificate details, QR verification, and State validation status.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading certificate...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} />{error}</div> : null}

        {latestCertificate ? (
          <>
            <CertificateCard certificateNumber={latestCertificate.certificate_number} status={latestCertificate.effective_status} holder={latestCertificate.food_handler_name || "Food handler"} expiry={`Expires ${dateLabel(latestCertificate.expiry_date)}`} />
            <section className="grid gap-4 lg:grid-cols-[1fr_0.8fr]">
              <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                <h2 className="text-sm font-bold text-slate-950">Certificate Details</h2>
                <dl className="mt-4 grid gap-3 text-sm">
                  <div className="flex items-center justify-between gap-3"><dt className="text-slate-500">Facility</dt><dd className="font-bold text-slate-950">{latestCertificate.facility_name || "Medical facility"}</dd></div>
                  <div className="flex items-center justify-between gap-3"><dt className="text-slate-500">Doctor</dt><dd className="font-bold text-slate-950">{latestCertificate.doctor_name || "Doctor"}</dd></div>
                  <div className="flex items-center justify-between gap-3"><dt className="text-slate-500">State</dt><dd className="font-bold text-slate-950">{latestCertificate.issuing_state_name || "Issuing state"}</dd></div>
                  <div className="flex items-center justify-between gap-3"><dt className="text-slate-500">Issued</dt><dd className="font-bold text-slate-950">{dateLabel(latestCertificate.issue_date)}</dd></div>
                  <div className="flex items-center justify-between gap-3"><dt className="text-slate-500">Status</dt><dd><StatusBadge status={latestCertificate.effective_status} /></dd></div>
                </dl>
                <div className="mt-5 flex flex-wrap gap-2">
                  {latestCertificate.pdf_url ? <a className="inline-flex h-10 items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white" href={latestCertificate.pdf_url}><Download size={16} /> PDF</a> : null}
                  {latestCertificate.verification_url ? <a className="inline-flex h-10 items-center gap-2 rounded border border-slate-200 px-4 text-sm font-bold text-slate-700" href={latestCertificate.verification_url}><ExternalLink size={16} /> Verify</a> : null}
                </div>
              </div>
              <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                <h2 className="text-sm font-bold text-slate-950">QR Code</h2>
                {latestCertificate.qr_code_url ? (
                  // Certificate QR URLs are API/media-owned assets and should render exactly as issued.
                  // eslint-disable-next-line @next/next/no-img-element
                  <img alt="Certificate QR code" className="mt-4 h-44 w-44 rounded border border-slate-200 bg-white p-2" src={latestCertificate.qr_code_url} />
                ) : (
                  <div className="mt-4 flex h-44 w-44 items-center justify-center rounded border border-slate-200 bg-slate-50 text-slate-400"><QrCode size={48} /></div>
                )}
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
