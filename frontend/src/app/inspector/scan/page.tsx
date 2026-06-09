"use client";

import { AlertTriangle, ClipboardCheck, Flag, QrCode, SearchCheck } from "lucide-react";
import { useMemo, useState } from "react";
import { InspectorVerificationPanel } from "@/components/certificates/certificate-widgets";
import { PortalShell } from "@/components/layout/portal-shell";
import {
  inspectorFlagCertificate,
  inspectorSaveCertificateToInspection,
  inspectorVerifyCertificateByNumber,
  listInspections,
} from "@/lib/api/inspections";
import type { Inspection, InspectorCertificateVerification } from "@/types/inspections";
import { useQuery } from "@tanstack/react-query";

function dateLabel(value?: string) {
  if (!value) return "Unavailable";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const [certificateNumber, setCertificateNumber] = useState("");
  const [result, setResult] = useState<InspectorCertificateVerification | null>(null);
  const [selectedInspection, setSelectedInspection] = useState("");
  const [flagReason, setFlagReason] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const inspectionsQuery = useQuery({ queryKey: ["inspector-inspections-for-scan"], queryFn: listInspections });
  const inspections = useMemo(
    () => (inspectionsQuery.data || []).filter((row: Inspection) => row.status !== "closed"),
    [inspectionsQuery.data]
  );

  async function verify() {
    const trimmed = certificateNumber.trim();
    if (!trimmed) {
      setMessage("Enter a certificate number.");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      setResult(await inspectorVerifyCertificateByNumber(trimmed));
    } catch {
      setResult({ certificate_number: trimmed, certificate_validity: "not_found" });
    } finally {
      setLoading(false);
    }
  }

  async function saveToInspection() {
    if (!result?.id || !selectedInspection) {
      setMessage("Select an inspection before saving this verification.");
      return;
    }
    try {
      await inspectorSaveCertificateToInspection(result.id, selectedInspection);
      setMessage("Verification saved to inspection.");
    } catch {
      setMessage("Could not save verification to inspection.");
    }
  }

  async function flagCertificate() {
    if (!result?.id || !flagReason.trim()) {
      setMessage("Enter a reason before flagging this certificate.");
      return;
    }
    try {
      await inspectorFlagCertificate(result.id, { reason: flagReason.trim() });
      setMessage("Certificate flagged for regulatory review.");
      setFlagReason("");
    } catch {
      setMessage("Could not flag certificate.");
    }
  }

  return (
    <PortalShell role="inspector" title="Scan certificate" description="Verify FoodCert NG certificates in the field and attach results to inspections.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[1fr_auto]">
            <label className="flex h-11 items-center gap-2 rounded border border-neutral-200 bg-neutral-50 px-3">
              <QrCode className="text-neutral-400" size={17} />
              <input
                className="min-w-0 flex-1 bg-transparent text-sm font-semibold outline-none"
                placeholder="Enter certificate number from QR or card"
                value={certificateNumber}
                onChange={(event) => setCertificateNumber(event.target.value)}
                onKeyDown={(event) => event.key === "Enter" && verify()}
              />
            </label>
            <button className="inline-flex h-11 items-center justify-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60" disabled={loading} onClick={verify} type="button">
              <SearchCheck size={16} />
              Verify
            </button>
          </div>
          {message ? <p className="mt-3 rounded bg-neutral-50 p-3 text-sm font-semibold text-neutral-700">{message}</p> : null}
        </section>

        {result ? (
          <section className="grid gap-4 rounded-lg border border-neutral-200 bg-white p-5 shadow-sm lg:grid-cols-[1fr_0.8fr]">
            <div>
              <InspectorVerificationPanel certificate={result} />
              <dl className="mt-5 grid gap-3 text-sm">
                <div className="flex justify-between gap-3"><dt className="text-neutral-500">Food handler</dt><dd className="font-bold text-neutral-900">{result.food_handler_name || "Unavailable"}</dd></div>
                <div className="flex justify-between gap-3"><dt className="text-neutral-500">Issuing authority</dt><dd className="font-bold text-neutral-900">{result.issuing_state_ministry || "Unavailable"}</dd></div>
                <div className="flex justify-between gap-3"><dt className="text-neutral-500">Facility</dt><dd className="font-bold text-neutral-900">{result.approved_medical_facility || "Unavailable"}</dd></div>
                <div className="flex justify-between gap-3"><dt className="text-neutral-500">Issued</dt><dd className="font-bold text-neutral-900">{dateLabel(result.issue_date)}</dd></div>
                <div className="flex justify-between gap-3"><dt className="text-neutral-500">Expiry</dt><dd className="font-bold text-neutral-900">{dateLabel(result.expiry_date)}</dd></div>
                <div className="flex justify-between gap-3"><dt className="text-neutral-500">Fitness</dt><dd className="font-bold capitalize text-neutral-900">{result.fitness_status?.replaceAll("_", " ") || "Unavailable"}</dd></div>
              </dl>
            </div>

            <div className="grid content-start gap-4">
              <label className="grid gap-1 text-sm font-semibold text-neutral-700">
                Save to inspection
                <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={selectedInspection} onChange={(event) => setSelectedInspection(event.target.value)}>
                  <option value="">Select active inspection</option>
                  {inspections.map((inspection) => (
                    <option key={inspection.id} value={inspection.id}>{inspection.employer_name || "Employer"} - {dateLabel(inspection.inspection_date)}</option>
                  ))}
                </select>
              </label>
              <button className="inline-flex h-10 items-center justify-center gap-2 rounded border border-neutral-200 px-3 text-sm font-bold text-neutral-700 hover:bg-neutral-50 disabled:opacity-50" disabled={!result.id} onClick={saveToInspection} type="button">
                <ClipboardCheck size={16} />
                Save result
              </button>
              <div className="grid gap-2 rounded bg-warning-50 p-3">
                <label className="grid gap-1 text-sm font-semibold text-amber-900">
                  Flag reason
                  <input className="h-10 rounded border border-warning-100 bg-white px-3 text-sm" value={flagReason} onChange={(event) => setFlagReason(event.target.value)} placeholder="Mismatch, suspected fraud..." />
                </label>
                <button className="inline-flex h-10 items-center justify-center gap-2 rounded border border-amber-300 px-3 text-sm font-bold text-amber-900 hover:bg-warning-100 disabled:opacity-50" disabled={!result.id} onClick={flagCertificate} type="button">
                  <Flag size={16} />
                  Flag certificate
                </button>
              </div>
            </div>
          </section>
        ) : (
          <section className="flex items-start gap-3 rounded-lg border border-dashed border-neutral-300 bg-white p-5 text-sm text-neutral-600">
            <AlertTriangle className="mt-0.5 text-neutral-400" size={18} />
            Enter a certificate number from the QR page or printed certificate to verify it.
          </section>
        )}
      </div>
    </PortalShell>
  );
}
