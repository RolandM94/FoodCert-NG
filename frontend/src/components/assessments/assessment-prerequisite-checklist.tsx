import { AlertCircle, CheckCircle2, Info } from "lucide-react";

import type { AssessmentWorkflowItem } from "@/types/assessments";

type AssessmentPrerequisiteChecklistProps = {
  blockers?: AssessmentWorkflowItem[];
  warnings?: AssessmentWorkflowItem[];
};

export function AssessmentPrerequisiteChecklist({ blockers = [], warnings = [] }: AssessmentPrerequisiteChecklistProps) {
  const ready = blockers.length === 0 && warnings.length === 0;
  const rows = [
    ...blockers.map((item) => ({ ...item, tone: "blocker" as const })),
    ...warnings.map((item) => ({ ...item, tone: "warning" as const }))
  ];

  if (ready) {
    return (
      <div className="rounded border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
        <div className="flex items-center gap-2 font-semibold">
          <CheckCircle2 size={16} />
          Assessment prerequisites are complete
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {rows.map((item) => {
        const isBlocker = item.tone === "blocker";
        return (
          <div
            key={`${item.tone}-${item.code}`}
            className={`rounded border px-3 py-2 text-sm ${
              isBlocker ? "border-rose-200 bg-rose-50 text-rose-900" : "border-amber-200 bg-amber-50 text-amber-900"
            }`}
          >
            <div className="flex items-start gap-2">
              {isBlocker ? <AlertCircle className="mt-0.5 shrink-0" size={16} /> : <Info className="mt-0.5 shrink-0" size={16} />}
              <div>
                <div className="font-semibold">{item.label}</div>
                {item.detail ? <div className="mt-1 text-xs leading-5 opacity-90">{item.detail}</div> : null}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
