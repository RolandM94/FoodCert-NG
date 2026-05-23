import { FileText } from "lucide-react";
import type { GeneratedReport } from "@/types/reports";

type AssessmentReportAction = {
  kind: "summary" | "medical" | "return-to-work";
  label: string;
};

type AssessmentReportsPanelProps = {
  report?: GeneratedReport | null;
  busy: boolean;
  actions?: AssessmentReportAction[];
  onGenerate: (kind: AssessmentReportAction["kind"]) => void;
};

const DEFAULT_ACTIONS: AssessmentReportAction[] = [
  { kind: "summary", label: "Summary" },
  { kind: "medical", label: "Medical" },
  { kind: "return-to-work", label: "Return to work" },
];

export function AssessmentReportsPanel({ report, busy, actions = DEFAULT_ACTIONS, onGenerate }: AssessmentReportsPanelProps) {
  const cards = report?.summary?.cards || {};
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <FileText className="text-brand-deep" size={18} />
        <h2 className="text-sm font-bold text-slate-950">Assessment Reports</h2>
      </div>
      <div className="flex flex-wrap gap-2">
        {actions.map((action) => (
          <button className="h-9 rounded border border-slate-200 px-3 text-xs font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-60" disabled={busy} key={action.kind} type="button" onClick={() => onGenerate(action.kind)}>
            {action.label}
          </button>
        ))}
      </div>
      {report ? (
        <div className="mt-4 grid gap-2 rounded border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700 sm:grid-cols-2">
          {Object.entries(cards).slice(0, 8).map(([key, value]) => (
            <div className="flex justify-between gap-3" key={key}>
              <span className="capitalize text-slate-500">{key.replaceAll("_", " ")}</span>
              <strong className="text-right text-slate-950">{String(value || "Not set")}</strong>
            </div>
          ))}
        </div>
      ) : <p className="mt-3 text-sm font-semibold text-slate-500">Generate a permitted report view for this assessment.</p>}
    </section>
  );
}
