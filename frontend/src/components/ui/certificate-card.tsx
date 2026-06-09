import { BadgeCheck, QrCode } from "lucide-react";
import { StatusBadge } from "@/components/status/status-badge";

export function CertificateCard({
  certificateNumber = "No certificate issued yet",
  status = "pending",
  holder = "Food handler",
  expiry = "Awaiting issuance"
}: {
  certificateNumber?: string;
  status?: string;
  holder?: string;
  expiry?: string;
}) {
  return (
    <div className="rounded-lg border border-brand-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Certificate</p>
          <h2 className="mt-2 text-xl font-bold text-neutral-900">{certificateNumber}</h2>
          <p className="mt-1 text-sm text-neutral-600">{holder}</p>
        </div>
        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-brand-50 text-brand-700">
          <BadgeCheck aria-hidden="true" size={24} />
        </div>
      </div>
      <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-neutral-100 pt-4">
        <StatusBadge status={status} />
        <div className="flex items-center gap-2 text-sm font-semibold text-neutral-700">
          <QrCode aria-hidden="true" size={16} />
          <span>{expiry}</span>
        </div>
      </div>
    </div>
  );
}
