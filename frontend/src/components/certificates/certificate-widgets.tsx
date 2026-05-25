"use client";

import { AlertTriangle, BadgeCheck, FileText, Flag, QrCode, RefreshCw, SearchCheck } from "lucide-react";
import { StatusBadge } from "@/components/status/status-badge";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import type { Certificate, PublicCertificateVerification } from "@/types/certificates";

export function CertificateStatusBadge({ status }: { status?: string | null }) {
  return <StatusBadge status={status} />;
}

export function QRCodeDisplay({ qrUrl, label = "Certificate QR code" }: { qrUrl?: string; label?: string }) {
  return (
    <div className="grid justify-items-center gap-2 rounded-lg border border-slate-200 bg-white p-4">
      {qrUrl ? (
        // QR URLs are generated certificate artifacts and must render exactly as issued.
        // eslint-disable-next-line @next/next/no-img-element
        <img alt={label} className="h-44 w-44 rounded border border-slate-200 bg-white p-2" src={qrUrl} />
      ) : (
        <div className="flex h-44 w-44 items-center justify-center rounded border border-dashed border-slate-300 bg-slate-50 text-slate-400">
          <QrCode size={48} />
        </div>
      )}
      <p className="text-xs font-semibold text-slate-500">{label}</p>
    </div>
  );
}

export function CertificatePreview({ certificate }: { certificate: Certificate }) {
  return (
    <section className="rounded-lg border border-emerald-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-xs font-bold uppercase text-slate-500">Certificate</p>
          <h2 className="mt-2 break-words text-xl font-bold text-slate-950">{certificate.certificate_number}</h2>
          <p className="mt-1 text-sm text-slate-600">{certificate.food_handler_name || "Food handler"}</p>
        </div>
        <CertificateStatusBadge status={certificate.effective_status || certificate.status} />
      </div>
    </section>
  );
}

export function CertificatePDFViewer({ pdfUrl }: { pdfUrl?: string }) {
  if (!pdfUrl) {
    return (
      <div className="flex min-h-40 items-center justify-center rounded-lg border border-dashed border-slate-300 bg-slate-50 text-sm font-semibold text-slate-500">
        PDF not available
      </div>
    );
  }
  return (
    <a className="inline-flex h-10 items-center gap-2 rounded border border-slate-200 px-4 text-sm font-bold text-slate-700 hover:bg-slate-50" href={pdfUrl}>
      <FileText size={16} />
      Open PDF
    </a>
  );
}

export function CertificateRenewalCard({ status, onRenew, disabled }: { status?: string; onRenew: () => void; disabled?: boolean }) {
  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
      <div className="flex items-start gap-3">
        <RefreshCw className="mt-0.5 text-amber-800" size={18} />
        <div className="min-w-0">
          <p className="font-bold text-amber-950">Renewal</p>
          <p className="mt-1 text-sm font-semibold capitalize text-amber-800">{(status || "not_started").replaceAll("_", " ")}</p>
        </div>
      </div>
      <button className="mt-3 inline-flex h-9 items-center gap-2 rounded border border-amber-300 px-3 text-sm font-bold text-amber-900 hover:bg-amber-100 disabled:opacity-50" disabled={disabled} onClick={onRenew} type="button">
        <RefreshCw size={15} />
        Start renewal
      </button>
    </div>
  );
}

export function CertificateAnalyticsCards({ cards }: { cards: Array<{ label: string; value: number | string; tone?: "default" | "warning" | "danger" }> }) {
  const toneClass = {
    default: "border-slate-200 bg-white text-slate-950",
    warning: "border-amber-200 bg-amber-50 text-amber-950",
    danger: "border-rose-200 bg-rose-50 text-rose-950",
  };
  return (
    <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <div key={card.label} className={`rounded-lg border p-3 text-center shadow-sm ${toneClass[card.tone || "default"]}`}>
          <BadgeCheck size={16} className="mx-auto mb-1 text-slate-400" />
          <p className="text-xl font-bold">{card.value}</p>
          <p className="text-xs font-semibold text-slate-500">{card.label}</p>
        </div>
      ))}
    </section>
  );
}

export function CertificateRegistryTable<T>({ columns, rows, empty }: { columns: DataTableColumn<T>[]; rows: T[]; empty?: string }) {
  return <DataTable columns={columns} empty={empty} rows={rows} />;
}

export function CertificateAuditTimeline({ items }: { items: Array<{ id: string; action: string; actor_name?: string; metadata: Record<string, unknown>; created_at: string }> }) {
  if (!items.length) return <p className="text-sm text-slate-500">No audit events found.</p>;
  return (
    <div className="grid gap-1">
      {items.map((item) => (
        <div key={item.id} className="border-b border-slate-100 py-3 text-sm last:border-b-0">
          <p className="font-bold capitalize text-slate-900">{String(item.metadata.event || item.action).replaceAll("_", " ")}</p>
          <p className="text-xs text-slate-500">{item.actor_name || "System"} - {new Date(item.created_at).toLocaleString("en-NG")}</p>
        </div>
      ))}
    </div>
  );
}

export function CertificateLifecycleModal({
  title,
  certificateNumber,
  reason,
  setReason,
  isPending,
  isError,
  onCancel,
  onSubmit,
}: {
  title: string;
  certificateNumber: string;
  reason: string;
  setReason: (value: string) => void;
  isPending?: boolean;
  isError?: boolean;
  onCancel: () => void;
  onSubmit: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
      <div className="w-full max-w-md rounded-lg border border-slate-200 bg-white shadow-xl">
        <div className="border-b border-slate-100 px-6 py-4">
          <h2 className="text-lg font-bold capitalize text-slate-950">{title}</h2>
          <p className="mt-1 break-words text-sm text-slate-500">{certificateNumber}</p>
        </div>
        <form className="grid gap-4 p-6" onSubmit={(event) => { event.preventDefault(); onSubmit(); }}>
          <label className="grid gap-1 text-sm font-semibold text-slate-700">
            Reason <span className="text-red-500">*</span>
            <textarea className="rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm" required rows={3} value={reason} onChange={(event) => setReason(event.target.value)} />
          </label>
          {isError ? <p className="rounded bg-red-50 px-3 py-2 text-sm font-semibold text-red-700">Could not complete this certificate action.</p> : null}
          <div className="flex justify-end gap-3">
            <button className="h-10 rounded border border-slate-200 px-4 text-sm font-semibold text-slate-600 hover:bg-slate-50" onClick={onCancel} type="button">Cancel</button>
            <button className="h-10 rounded bg-brand-green px-4 text-sm font-bold capitalize text-white hover:bg-brand-deep disabled:opacity-60" disabled={isPending} type="submit">{title.split(" ")[0]}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export function CertificateNumberVerificationForm({ value, setValue, loading, onSubmit }: { value: string; setValue: (value: string) => void; loading?: boolean; onSubmit: () => void }) {
  return (
    <div className="grid gap-2 sm:grid-cols-[1fr_auto]">
      <input
        className="h-11 min-w-0 rounded border border-slate-200 bg-slate-50 px-3 text-sm font-semibold text-slate-800 outline-none focus:border-brand-green"
        placeholder="Enter certificate number"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => event.key === "Enter" && onSubmit()}
      />
      <button className="inline-flex h-11 items-center justify-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep disabled:opacity-60" disabled={loading} onClick={onSubmit} type="button">
        <SearchCheck size={16} />
        Verify
      </button>
    </div>
  );
}

export function SuspiciousCertificateReportForm({ onSubmit, status }: { onSubmit: () => void; status: "idle" | "submitting" | "submitted" | "error" }) {
  return (
    <div className="grid gap-3">
      {status === "submitted" ? <p className="rounded bg-emerald-50 p-3 text-sm font-semibold text-emerald-800">Report submitted for review.</p> : null}
      {status === "error" ? <p className="rounded bg-red-50 p-3 text-sm font-semibold text-red-700">Certificate number and reason are required.</p> : null}
      <button className="inline-flex h-11 w-fit items-center justify-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep disabled:opacity-60" disabled={status === "submitting"} onClick={onSubmit} type="button">
        <Flag size={16} />
        Submit report
      </button>
    </div>
  );
}

export function InspectorVerificationPanel({ certificate }: { certificate: PublicCertificateVerification }) {
  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-bold uppercase text-slate-500">Verification result</p>
          <h2 className="mt-1 break-words text-lg font-bold text-slate-950">{certificate.certificate_number}</h2>
        </div>
        <CertificateStatusBadge status={certificate.certificate_validity} />
      </div>
    </div>
  );
}

export function EmployerCertificateTable<T>({ columns, rows, empty }: { columns: DataTableColumn<T>[]; rows: T[]; empty?: string }) {
  return <CertificateRegistryTable columns={columns} empty={empty} rows={rows} />;
}

export function EmptyCertificateState({ message }: { message: string }) {
  return (
    <section className="flex items-start gap-3 rounded-lg border border-dashed border-slate-300 bg-white p-5 text-sm text-slate-600">
      <AlertTriangle className="mt-0.5 shrink-0 text-slate-400" size={18} />
      <span>{message}</span>
    </section>
  );
}
