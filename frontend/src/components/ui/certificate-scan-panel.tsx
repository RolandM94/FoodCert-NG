"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { QrCode, SearchCheck } from "lucide-react";

export function CertificateScanPanel() {
  const router = useRouter();
  const [certificateNumber, setCertificateNumber] = useState("");
  const [error, setError] = useState("");

  function handleVerify() {
    const trimmed = certificateNumber.trim();
    if (!trimmed) {
      setError("Enter a certificate number.");
      return;
    }
    setError("");
    router.push(`/verify/${encodeURIComponent(trimmed)}`);
  }

  return (
    <div className="grid gap-5 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex aspect-video flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-slate-300 bg-slate-50 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-50 text-brand-deep">
          <QrCode size={24} />
        </div>
        <div>
          <p className="text-sm font-bold text-slate-700">Certificate verification</p>
          <p className="mt-1 text-xs text-slate-500">Enter the certificate number printed on the QR-coded certificate.</p>
        </div>
      </div>

      <div className="grid gap-2 sm:grid-cols-[1fr_auto]">
        <label className="flex h-11 items-center gap-2 rounded border border-slate-200 bg-slate-50 px-3">
          <QrCode size={15} className="shrink-0 text-slate-400" />
          <input
            className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-slate-400"
            onChange={(event) => {
              setCertificateNumber(event.target.value);
              setError("");
            }}
            onKeyDown={(event) => event.key === "Enter" && handleVerify()}
            placeholder="Enter certificate number"
            value={certificateNumber}
          />
        </label>
        <button
          className="inline-flex h-11 items-center justify-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep"
          onClick={handleVerify}
          type="button"
        >
          <SearchCheck size={16} />
          Verify
        </button>
      </div>
      {error && <p className="text-xs font-semibold text-red-600">{error}</p>}
    </div>
  );
}
