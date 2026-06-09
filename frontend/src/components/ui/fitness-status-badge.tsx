const STATUS_COLORS: Record<string, string> = {
  fit_to_handle_food: "bg-brand-50 text-brand-700 ring-brand-200",
  certification_pending: "bg-warning-50 text-warning-700 ring-warning-100",
  certificate_expired: "bg-danger-50 text-danger-700 ring-danger-100",
  certificate_expiring_soon: "bg-warning-50 text-warning-700 ring-warning-100",
  temporarily_not_fit: "bg-warning-50 text-warning-700 ring-warning-100",
  excluded_from_food_handling: "bg-danger-50 text-danger-700 ring-danger-100",
  return_to_work_pending: "bg-warning-50 text-warning-700 ring-warning-100",
  cleared_to_return: "bg-brand-50 text-brand-700 ring-brand-200",
  vaccination_due: "bg-info-50 text-info-700 ring-blue-200",
  medical_review_required: "bg-neutral-100 text-neutral-700 ring-neutral-200",
  invite_pending: "bg-neutral-50 text-neutral-500 ring-neutral-200",
  not_linked: "bg-neutral-50 text-neutral-500 ring-neutral-200",
  no_certificate: "bg-neutral-50 text-neutral-500 ring-neutral-200",
  not_recorded: "bg-neutral-50 text-neutral-500 ring-neutral-200",
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
        STATUS_COLORS[status] ?? "bg-neutral-50 text-neutral-600 ring-neutral-200"
      }`}
    >
      {STATUS_LABELS[status] ?? status.replace(/_/g, " ")}
    </span>
  );
}
