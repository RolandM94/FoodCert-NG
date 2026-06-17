"use client";

interface TrendPoint {
  period: string;
  value: number;
  count?: number;
}

interface Props {
  trends: TrendPoint[];
  title?: string;
  subtitle?: string;
  emptyMessage?: string;
}

export function KPITrendChart({ trends, title = "KPI Trend", subtitle, emptyMessage = "No trend data available for the selected filters." }: Props) {
  const maxValue = Math.max(1, ...trends.map((p) => p.value));

  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-bold text-neutral-950">{title}</h3>
          {subtitle ? <p className="mt-1 text-xs text-neutral-500">{subtitle}</p> : null}
        </div>
        <span className="rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-semibold text-neutral-600">{trends.length} periods</span>
      </div>
      <div className="mt-4">
        {trends.length ? (
          <div className="grid gap-3">
            {trends.slice(-12).map((point) => (
              <div className="grid items-center gap-3 sm:grid-cols-[100px_minmax(0,1fr)_100px]" key={point.period}>
                <span className="text-xs font-semibold text-neutral-500">{point.period}</span>
                <div className="h-8 overflow-hidden rounded-full bg-neutral-100">
                  <div
                    className="h-8 rounded-full bg-brand-500 transition-all"
                    style={{ width: `${Math.max(4, Math.min(100, (point.value / maxValue) * 100))}%` }}
                  />
                </div>
                <div className="text-right">
                  <span className="text-sm font-semibold text-neutral-900">{point.value.toLocaleString()}</span>
                  {point.count != null && point.count > 1 ? (
                    <span className="ml-1 text-xs text-neutral-400">({point.count})</span>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="rounded border border-dashed border-neutral-300 p-6 text-center text-sm text-neutral-500">{emptyMessage}</div>
        )}
      </div>
    </div>
  );
}
