import { History } from "lucide-react";
import type { AssessmentAuditTimelineItem } from "@/types/assessments";

type AssessmentAuditTimelineProps = {
  items: AssessmentAuditTimelineItem[];
  loading?: boolean;
};

function dateLabel(value: string) {
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export function AssessmentAuditTimeline({ items, loading = false }: AssessmentAuditTimelineProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <History className="text-brand-deep" size={18} />
        <h2 className="text-sm font-bold text-slate-950">Audit Timeline</h2>
      </div>
      {loading ? <p className="text-sm font-semibold text-slate-500">Loading timeline...</p> : null}
      {!loading && !items.length ? <p className="text-sm font-semibold text-slate-500">No audit events available.</p> : null}
      <ol className="grid gap-3">
        {items.map((item) => (
          <li className="rounded border border-slate-200 bg-slate-50 p-3" key={item.id}>
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p className="text-sm font-bold text-slate-950">{item.label}</p>
                <p className="text-xs capitalize text-slate-500">{item.action.replaceAll("_", " ")} {item.actor_role ? `by ${item.actor_role.replaceAll("_", " ")}` : ""}</p>
              </div>
              <time className="text-xs font-semibold text-slate-500">{dateLabel(item.created_at)}</time>
            </div>
            {item.actor_name ? <p className="mt-2 text-xs text-slate-600">{item.actor_name}</p> : null}
          </li>
        ))}
      </ol>
    </section>
  );
}
