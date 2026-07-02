"use client";

import { useQuery } from "@tanstack/react-query";

import { getPIOverview } from "@/lib/api/performance-indicators";

function StatTile({ label, value, tone = "neutral" }: { label: string; value: number | string; tone?: "neutral" | "good" | "warning" | "critical" }) {
  const toneClasses: Record<string, string> = {
    neutral: "text-neutral-900",
    good: "text-brand-700",
    warning: "text-warning-700",
    critical: "text-danger-700",
  };
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-neutral-500">{label}</p>
      <p className={`mt-1 text-2xl font-bold tabular-nums ${toneClasses[tone]}`}>{value}</p>
    </div>
  );
}

function MoverList({ title, rows, positive }: { title: string; rows: { indicator_id: string; indicator_name: string; change: number }[]; positive: boolean }) {
  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-neutral-900">{title}</h3>
      {rows.length === 0 ? (
        <p className="mt-2 text-sm text-neutral-500">Not enough history yet.</p>
      ) : (
        <ul className="mt-2 space-y-2">
          {rows.map((row) => (
            <li key={row.indicator_id} className="flex items-center justify-between gap-3 text-sm">
              <span className="truncate text-neutral-700">{row.indicator_name}</span>
              <span className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold tabular-nums ${positive ? "bg-brand-50 text-brand-700" : "bg-danger-50 text-danger-700"}`}>
                {row.change > 0 ? "+" : ""}{row.change}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export function PIOverviewPanel() {
  const { data, isLoading, isError } = useQuery({ queryKey: ["pi-overview"], queryFn: getPIOverview });

  if (isLoading) return <p className="text-sm text-neutral-500">Loading overview…</p>;
  if (isError || !data) return <p className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">Could not load the indicators overview.</p>;

  const { cards } = data;
  return (
    <div className="grid gap-5">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatTile label="Active Indicators" value={cards.total_active_indicators} />
        <StatTile label="Meeting Target" value={cards.indicators_meeting_target} tone="good" />
        <StatTile label="Below Target" value={cards.indicators_below_target} tone="critical" />
        <StatTile label="At Risk" value={cards.indicators_at_risk} tone="warning" />
        <StatTile label="Calculations (7d)" value={cards.recent_calculations} />
        <StatTile label="Failed Calculations (7d)" value={cards.failed_calculations} tone={cards.failed_calculations > 0 ? "critical" : "neutral"} />
      </div>
      <div className="grid gap-5 lg:grid-cols-2">
        <MoverList title="Top improving indicators" rows={data.top_improving} positive />
        <MoverList title="Top declining indicators" rows={data.top_declining} positive={false} />
      </div>
    </div>
  );
}
