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
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-sm font-bold text-slate-950">{branchName}</p>
      <div className="mt-3 grid grid-cols-3 gap-3">
        <div className="rounded bg-slate-50 p-2 text-center">
          <UsersRound size={14} className="mx-auto text-slate-400" />
          <p className="mt-1 text-lg font-bold text-slate-800">{formatNumber(foodHandlers)}</p>
          <p className="text-[10px] font-semibold text-slate-500">Handlers</p>
        </div>
        <div className="rounded bg-emerald-50 p-2 text-center">
          <BadgeCheck size={14} className="mx-auto text-emerald-600" />
          <p className="mt-1 text-lg font-bold text-emerald-800">{formatNumber(certified)}</p>
          <p className="text-[10px] font-semibold text-emerald-600">Certified</p>
        </div>
        <div className="rounded bg-amber-50 p-2 text-center">
          <AlertCircle size={14} className="mx-auto text-amber-600" />
          <p className="mt-1 text-lg font-bold text-amber-800">{formatNumber(expired)}</p>
          <p className="text-[10px] font-semibold text-amber-600">Expired</p>
        </div>
      </div>
    </div>
  );
}
