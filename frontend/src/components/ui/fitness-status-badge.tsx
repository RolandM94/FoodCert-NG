const STATUS_COLORS: Record<string, string> = {
  fit_to_handle_food: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  certification_pending: "bg-amber-50 text-amber-700 ring-amber-200",
  certificate_expired: "bg-red-50 text-red-700 ring-red-200",
  certificate_expiring_soon: "bg-orange-50 text-orange-700 ring-orange-200",
  temporarily_not_fit: "bg-orange-50 text-orange-700 ring-orange-200",
  excluded_from_food_handling: "bg-red-50 text-red-700 ring-red-200",
  return_to_work_pending: "bg-amber-50 text-amber-700 ring-amber-200",
  cleared_to_return: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  vaccination_due: "bg-blue-50 text-blue-700 ring-blue-200",
  medical_review_required: "bg-purple-50 text-purple-700 ring-purple-200",
  invite_pending: "bg-slate-50 text-slate-500 ring-slate-200",
  not_linked: "bg-slate-50 text-slate-500 ring-slate-200",
  no_certificate: "bg-slate-50 text-slate-500 ring-slate-200",
  not_recorded: "bg-slate-50 text-slate-500 ring-slate-200",
};

const STATUS_LABELS: Record<string, string> = {
  fit_to_handle_food: "Fit to Handle Food",
  certification_pending: "Certification Pending",
  certificate_expired: "Certificate Expired",
  certificate_expiring_soon: "Expiring Soon",
  temporarily_not_fit: "Temporarily Not Fit",
  excluded_from_food_handling: "Excluded",
  return_to_work_pending: "RTW Pending",
  cleared_to_return: "Cleared to Return",
  vaccination_due: "Vaccination Due",
  medical_review_required: "Medical Review",
  invite_pending: "Invite Pending",
  not_linked: "Not Linked",
  not_recorded: "Not Recorded",
  complete: "Complete",
  dose_1_completed: "Dose 1 Done",
  active: "Active",
  expired: "Expired",
  revoked: "Revoked",
  no_certificate: "No Certificate",
};

export function FitnessStatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ${
        STATUS_COLORS[status] ?? "bg-slate-50 text-slate-600 ring-slate-200"
      }`}
    >
      {STATUS_LABELS[status] ?? status.replace(/_/g, " ")}
    </span>
  );
}
