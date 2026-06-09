import { CheckCircle2, Circle, CircleDashed } from "lucide-react";

import type { AssessmentWorkflowItem } from "@/types/assessments";

export function AssessmentStepper({ steps = [] }: { steps?: AssessmentWorkflowItem[] }) {
  return (
    <ol className="grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
      {steps.map((step) => {
        const complete = step.status === "complete";
        const pending = step.status === "pending";
        return (
          <li
            key={step.code}
            className={`rounded border bg-white p-3 ${
              complete ? "border-brand-200" : pending ? "border-neutral-200" : "border-warning-100"
            }`}
          >
            <div className="flex items-center gap-2">
              {complete ? (
                <CheckCircle2 className="text-brand-700" size={17} />
              ) : pending ? (
                <Circle className="text-neutral-400" size={17} />
              ) : (
                <CircleDashed className="text-warning-700" size={17} />
              )}
              <span className="text-sm font-semibold text-neutral-900">{step.label}</span>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
