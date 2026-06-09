import { AlertCircle, BadgeCheck, UsersRound } from "lucide-react";
import { formatNumber } from "@/lib/formatters/status";

export function BranchComplianceCard({
  branchName,
  foodHandlers,
  certified,
  expired,
}: {
  branchName: string;
  foodHandlers: number;
  certified: number;
  expired: number;
}) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <p className="text-sm font-bold text-neutral-900">{branchName}</p>
      <div className="mt-3 grid grid-cols-3 gap-3">
        <div className="rounded bg-neutral-50 p-2 text-center">
          <UsersRound size={14} className="mx-auto text-neutral-400" />
          <p className="mt-1 text-lg font-bold text-neutral-800">{formatNumber(foodHandlers)}</p>
          <p className="text-[10px] font-semibold text-neutral-500">Handlers</p>
        </div>
        <div className="rounded bg-brand-50 p-2 text-center">
          <BadgeCheck size={14} className="mx-auto text-brand-600" />
          <p className="mt-1 text-lg font-bold text-brand-800">{formatNumber(certified)}</p>
          <p className="text-[10px] font-semibold text-brand-600">Certified</p>
        </div>
        <div className="rounded bg-warning-50 p-2 text-center">
          <AlertCircle size={14} className="mx-auto text-amber-600" />
          <p className="mt-1 text-lg font-bold text-warning-700">{formatNumber(expired)}</p>
          <p className="text-[10px] font-semibold text-amber-600">Expired</p>
        </div>
      </div>
    </div>
  );
}
