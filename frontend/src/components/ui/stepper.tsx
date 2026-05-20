import { CheckCircle2, Circle } from "lucide-react";

export function Stepper({ steps, current = 0 }: { steps: string[]; current?: number }) {
  return (
    <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
      {steps.map((step, index) => {
        const done = index < current;
        const active = index === current;
        return (
          <li key={step} className={`rounded-lg border bg-white p-3 ${active ? "border-emerald-300 ring-2 ring-emerald-100" : "border-slate-200"}`}>
            <div className="flex items-center gap-2">
              {done ? <CheckCircle2 className="text-brand-deep" size={17} /> : <Circle className={active ? "text-brand-deep" : "text-slate-400"} size={17} />}
              <span className="text-sm font-semibold text-slate-900">{step}</span>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
