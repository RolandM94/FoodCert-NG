import type { LucideIcon } from "lucide-react";
import { formatNumber } from "@/lib/formatters/status";

export function DashboardCard({
  label,
  value,
  icon: Icon,
  detail
}: {
  label: string;
  value: string | number | null | undefined;
  icon: LucideIcon;
  detail?: string;
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-slate-500">{label}</p>
          <p className="mt-2 text-2xl font-bold text-slate-950">{formatNumber(value)}</p>
        </div>
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-50 text-brand-deep">
          <Icon aria-hidden="true" size={20} />
        </div>
      </div>
      {detail ? <p className="mt-3 text-sm text-slate-600">{detail}</p> : null}
    </div>
  );
}
