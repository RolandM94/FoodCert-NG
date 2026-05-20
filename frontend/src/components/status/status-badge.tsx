import { titleCaseStatus } from "@/lib/formatters/status";

const toneByStatus: Record<string, string> = {
  active: "bg-emerald-50 text-emerald-800 ring-emerald-200",
  approved: "bg-emerald-50 text-emerald-800 ring-emerald-200",
  cleared: "bg-emerald-50 text-emerald-800 ring-emerald-200",
  valid: "bg-emerald-50 text-emerald-800 ring-emerald-200",
  fit: "bg-emerald-50 text-emerald-800 ring-emerald-200",
  pending: "bg-amber-50 text-amber-800 ring-amber-200",
  pending_validation: "bg-amber-50 text-amber-800 ring-amber-200",
  under_review: "bg-sky-50 text-sky-800 ring-sky-200",
  submitted: "bg-sky-50 text-sky-800 ring-sky-200",
  warning: "bg-orange-50 text-orange-800 ring-orange-200",
  rejected: "bg-rose-50 text-rose-800 ring-rose-200",
  revoked: "bg-rose-50 text-rose-800 ring-rose-200",
  suspended: "bg-rose-50 text-rose-800 ring-rose-200",
  expired: "bg-slate-100 text-slate-700 ring-slate-200",
  temporarily_excluded: "bg-orange-50 text-orange-800 ring-orange-200",
  temporarily_not_fit: "bg-orange-50 text-orange-800 ring-orange-200"
};

export function StatusBadge({ status }: { status?: string | null }) {
  const key = status ?? "unknown";
  return (
    <span className={`inline-flex w-fit items-center rounded px-2 py-1 text-xs font-bold ring-1 ${toneByStatus[key] ?? "bg-slate-50 text-slate-700 ring-slate-200"}`}>
      {titleCaseStatus(status)}
    </span>
  );
}
