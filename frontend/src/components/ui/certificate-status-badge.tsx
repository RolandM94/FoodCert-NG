const STATUS_COLORS: Record<string, string> = {
  active: "bg-brand-50 text-brand-700 ring-brand-200",
  expired: "bg-danger-50 text-danger-700 ring-danger-100",
  revoked: "bg-danger-50 text-danger-700 ring-danger-100",
  suspended: "bg-warning-50 text-warning-700 ring-warning-100",
  pending_validation: "bg-neutral-50 text-neutral-500 ring-neutral-200",
  replaced: "bg-neutral-50 text-neutral-500 ring-neutral-200",
  valid: "bg-brand-50 text-brand-700 ring-brand-200",
  second_dose_due: "bg-warning-50 text-warning-700 ring-warning-100",
  dose_1_completed: "bg-info-50 text-info-700 ring-blue-200",
  complete: "bg-brand-50 text-brand-700 ring-brand-200",
  not_recorded: "bg-neutral-50 text-neutral-400 ring-neutral-200",
};

export function CertificateStatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ${STATUS_COLORS[status] || "bg-neutral-50 text-neutral-600 ring-neutral-200"}`}>
      {status === "active" ? "Active" : status === "expired" ? "Expired" : status === "revoked" ? "Revoked" : status.replace(/_/g, " ")}
    </span>
  );
}

export function VaccinationStatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ${STATUS_COLORS[status] || "bg-neutral-50 text-neutral-600 ring-neutral-200"}`}>
      {status === "valid" ? "Valid" : status === "expired" ? "Expired" : status === "second_dose_due" ? "Dose 2 Due" : status === "dose_1_completed" ? "Dose 1 Done" : status === "complete" ? "Complete" : status === "not_recorded" ? "—" : status}
    </span>
  );
}
