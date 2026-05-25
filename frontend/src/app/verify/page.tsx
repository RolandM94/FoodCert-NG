"use client";

import { ShieldCheck } from "lucide-react";
import { useState } from "react";
import { CertificateNumberVerificationForm } from "@/components/certificates/certificate-widgets";
import { PublicVerificationResult } from "@/components/certificates/public-verification-result";
import { publicVerifyCertificateByNumber } from "@/lib/api/certificates";
import type { PublicCertificateVerification } from "@/types/certificates";

export default function VerifyPage() {
  const [certificateNumber, setCertificateNumber] = useState("");
  const [result, setResult] = useState<PublicCertificateVerification | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function verify() {
    const trimmed = certificateNumber.trim();
    if (!trimmed) {
      setError("Enter a certificate number.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      setResult(await publicVerifyCertificateByNumber(trimmed));
    } catch {
      setResult({ certificate_validity: "not_found", certificate_number: trimmed });
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f7faf8] px-4 py-8 text-slate-950 sm:px-6 lg:px-8">
      <section className="mx-auto mb-6 grid max-w-2xl gap-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-emerald-50 text-brand-deep">
            <ShieldCheck aria-hidden="true" size={23} />
          </div>
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-slate-500">FoodCert NG Verification</p>
            <h1 className="text-xl font-bold text-slate-950">Verify a certificate</h1>
          </div>
        </div>
        <CertificateNumberVerificationForm loading={loading} onSubmit={verify} setValue={(value) => { setCertificateNumber(value); setError(""); }} value={certificateNumber} />
        {error ? <p className="text-sm font-semibold text-red-700">{error}</p> : null}
      </section>

      {result ? <PublicVerificationResult certificate={result} /> : null}
    </main>
  );
}
