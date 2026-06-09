import { AlertCircle, CheckCircle2, Clock, FlaskConical } from "lucide-react";
import { formatNumber } from "@/lib/formatters/status";

const DEPT_ICONS: Record<string, typeof FlaskConical> = {
  clinical_department: Clock,
  lab_department: FlaskConical,
  records_department: CheckCircle2,
};

export function DepartmentWorkloadCard({
  departmentName,
  departmentType,
  pendingTasks,
  completedTasks,
}: {
  departmentName: string;
  departmentType: string;
  pendingTasks: number;
  completedTasks: number;
}) {
  const Icon = DEPT_ICONS[departmentType] ?? AlertCircle;

  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm font-bold text-neutral-900">{departmentName}</p>
        <span className="rounded bg-neutral-100 px-2 py-0.5 text-[10px] font-semibold text-neutral-500 uppercase">
          {departmentType.replace(/_/g, " ")}
        </span>
      </div>
      <div className="mt-3 flex items-center gap-3">
        <div className="flex items-center gap-2 rounded bg-warning-50 px-3 py-2">
          <Icon size={14} className="text-amber-600" />
          <div>
            <p className="text-lg font-bold text-warning-700">{formatNumber(pendingTasks)}</p>
            <p className="text-[10px] font-semibold text-amber-600">Pending</p>
          </div>
        </div>
        <div className="flex items-center gap-2 rounded bg-brand-50 px-3 py-2">
          <CheckCircle2 size={14} className="text-brand-600" />
          <div>
            <p className="text-lg font-bold text-brand-800">{formatNumber(completedTasks)}</p>
            <p className="text-[10px] font-semibold text-brand-600">Completed</p>
          </div>
        </div>
      </div>
    </div>
  );
}
