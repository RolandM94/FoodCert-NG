"use client";

import { AlertTriangle } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { useState } from "react";
import { SuspiciousCertificateReportForm } from "@/components/certificates/certificate-widgets";
import { reportSuspiciousCertificate } from "@/lib/api/certificates";

function ReportSuspiciousCertificateForm() {
  const searchParams = useSearchParams();
  const initialCertificate = searchParams.get("certificate") ?? "";
  const [certificateNumber, setCertificateNumber] = useState(initialCertificate);
  const [reason, setReason] = useState("");
  const [details, setDetails] = useState("");
  const [reporterContact, setReporterContact] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "submitted" | "error">("idle");

  async function submit() {
    if (!certificateNumber.trim() || !reason.trim()) {
      setStatus("error");
      return;
    }
    setStatus("submitting");
    try {
      await reportSuspiciousCertificate({
        certificate_number: certificateNumber.trim(),
        reporter_contact: reporterContact.trim(),
        reason: reason.trim(),
        details: details.trim(),
      });
      setStatus("submitted");
    } catch {
      setStatus("error");
    }
  }

  return (
    <main className="min-h-screen bg-neutral-50 px-4 py-8 text-neutral-900 sm:px-6 lg:px-8">
      <section className="mx-auto grid max-w-2xl gap-5 rounded-lg border border-neutral-200 bg-white p-5 shadow-sm sm:p-6">
        <div className="flex items-start gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-warning-50 text-warning-700">
            <AlertTriangle aria-hidden="true" size={23} />
          </div>
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">FoodCert NG Verification</p>
            <h1 className="text-xl font-bold text-neutral-900">Report suspicious certificate</h1>
          </div>
        </div>

        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Certificate number
          <input className="h-11 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={certificateNumber} onChange={(event) => setCertificateNumber(event.target.value)} />
        </label>
        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Reason
          <input className="h-11 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Suspected fraud, mismatch, copied certificate..." />
        </label>
        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Contact
          <input className="h-11 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={reporterContact} onChange={(event) => setReporterContact(event.target.value)} placeholder="Optional email or phone" />
        </label>
        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Details
          <textarea className="min-h-28 rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm" value={details} onChange={(event) => setDetails(event.target.value)} />
        </label>

        <SuspiciousCertificateReportForm onSubmit={submit} status={status} />
      </section>
    </main>
  );
}

export default function ReportSuspiciousCertificatePage() {
  return (
    <Suspense fallback={<main className="min-h-screen bg-neutral-50 px-4 py-8 text-neutral-900"><section className="mx-auto max-w-2xl rounded-lg border border-neutral-200 bg-white p-5 text-sm font-semibold text-neutral-600 shadow-sm">Loading report form...</section></main>}>
      <ReportSuspiciousCertificateForm />
    </Suspense>
  );
}
