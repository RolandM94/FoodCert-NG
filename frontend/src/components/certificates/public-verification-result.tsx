import { AlertTriangle, CheckCircle2, ShieldAlert } from "lucide-react";
import Link from "next/link";
import type { PublicCertificateVerification } from "@/types/certificates";

function statusCopy(status: PublicCertificateVerification["certificate_validity"]) {
  if (status === "valid") {
    return {
      title: "Certificate valid",
      tone: "emerald",
      message: "This certificate is authentic and currently valid.",
      icon: CheckCircle2,
    };
  }
  if (status === "expired") {
    return {
      title: "Certificate expired",
      tone: "amber",
      message: "This certificate has expired and is no longer valid for food handling.",
      icon: AlertTriangle,
    };
  }
  if (status === "revoked") {
    return {
      title: "Certificate revoked",
      tone: "red",
      message: "This certificate has been revoked and is not valid.",
      icon: ShieldAlert,
    };
  }
  if (status === "suspended") {
    return {
      title: "Certificate suspended",
      tone: "amber",
      message: "This certificate is temporarily suspended pending regulatory review.",
      icon: AlertTriangle,
    };
  }
  return {
    title: "Certificate not valid",
    tone: "slate",
    message: "Certificate not found or the verification code is invalid.",
    icon: ShieldAlert,
  };
}

function dateLabel(value?: string) {
  if (!value) return "Unavailable";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export function PublicVerificationResult({ certificate }: { certificate: PublicCertificateVerification }) {
  const copy = statusCopy(certificate.certificate_validity);
  const Icon = copy.icon;
  const toneClass = {
    emerald: "border-brand-200 bg-brand-50 text-brand-800",
    amber: "border-warning-100 bg-warning-50 text-warning-700",
    red: "border-danger-100 bg-danger-50 text-danger-700",
    slate: "border-neutral-200 bg-neutral-50 text-neutral-700",
  }[copy.tone];

  const rows = [
    ["Certificate number", certificate.certificate_number],
    ["Status", certificate.certificate_validity.replaceAll("_", " ")],
    ["Food handler", certificate.food_handler_name ?? "Unavailable"],
    ["Issuing authority", certificate.issuing_state_ministry ?? "Unavailable"],
    ["Medical facility", certificate.approved_medical_facility ?? "Unavailable"],
    ["Issue date", dateLabel(certificate.issue_date)],
    ["Expiry date", dateLabel(certificate.expiry_date)],
    ["Fitness status", certificate.fitness_status?.replaceAll("_", " ") ?? "Unavailable"],
    ["Last verified", certificate.last_verified_at ? new Date(certificate.last_verified_at).toLocaleString("en-NG") : "Just now"],
  ];

  return (
    <section className="mx-auto grid w-full max-w-2xl gap-5 rounded-lg border border-neutral-200 bg-white p-5 shadow-sm sm:p-6">
      <div className={`flex items-start gap-3 rounded-lg border p-4 ${toneClass}`}>
        <Icon aria-hidden="true" className="mt-0.5 shrink-0" size={24} />
        <div>
          <h1 className="text-xl font-bold text-neutral-900">{copy.title}</h1>
          <p className="mt-1 text-sm font-medium">{copy.message}</p>
        </div>
      </div>

      <dl className="grid gap-3 text-sm">
        {rows.map(([label, value]) => (
          <div key={label} className="grid gap-1 border-b border-neutral-100 pb-3 last:border-b-0">
            <dt className="text-xs font-bold uppercase tracking-wide text-neutral-500">{label}</dt>
            <dd className="font-semibold capitalize text-neutral-900">{value}</dd>
          </div>
        ))}
      </dl>

      <div className="flex flex-wrap gap-3">
        <Link className="rounded border border-neutral-200 px-3 py-2 text-sm font-semibold text-neutral-700 hover:bg-neutral-50" href="/verify">
          Verify another
        </Link>
        <Link className="rounded border border-warning-100 px-3 py-2 text-sm font-semibold text-warning-700 hover:bg-warning-50" href={`/report-suspicious-certificate?certificate=${encodeURIComponent(certificate.certificate_number)}`}>
          Report suspicious
        </Link>
      </div>
    </section>
  );
}
