const STATUS_COLORS: Record<string, string> = {
  active: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  expired: "bg-red-50 text-red-700 ring-red-200",
  revoked: "bg-red-50 text-red-700 ring-red-200",
  suspended: "bg-amber-50 text-amber-700 ring-amber-200",
  pending_validation: "bg-slate-50 text-slate-500 ring-slate-200",
  replaced: "bg-slate-50 text-slate-500 ring-slate-200",
  valid: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  second_dose_due: "bg-amber-50 text-amber-700 ring-amber-200",
  dose_1_completed: "bg-blue-50 text-blue-700 ring-blue-200",
  complete: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  not_recorded: "bg-slate-50 text-slate-400 ring-slate-200",
};

export function CertificateStatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ${STATUS_COLORS[status] || "bg-slate-50 text-slate-600 ring-slate-200"}`}>
      {status === "active" ? "Active" : status === "expired" ? "Expired" : status === "revoked" ? "Revoked" : status.replace(/_/g, " ")}
    </span>
  );
}

export function VaccinationStatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ${STATUS_COLORS[status] || "bg-slate-50 text-slate-600 ring-slate-200"}`}>
      {status === "valid" ? "Valid" : status === "expired" ? "Expired" : status === "second_dose_due" ? "Dose 2 Due" : status === "dose_1_completed" ? "Dose 1 Done" : status === "complete" ? "Complete" : status === "not_recorded" ? "—" : status}
    </span>
  );
}
