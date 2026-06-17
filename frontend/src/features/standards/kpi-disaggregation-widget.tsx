"use client";

export interface DisaggregationItem {
  dimension: string;
  value: string | number;
  percentage?: number;
}

interface Props {
  title: string;
  subtitle?: string;
  items: DisaggregationItem[];
  emptyMessage?: string;
  maxItems?: number;
}

export function KPIDisaggregationWidget({ title, subtitle, items, emptyMessage, maxItems = 10 }: Props) {
  const displayed = items.slice(0, maxItems);
  const remaining = items.length - maxItems;
  const maxVal = Math.max(1, ...displayed.map((i) => Number(i.value) || 0));

  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <div>
        <h3 className="text-sm font-bold text-neutral-950">{title}</h3>
        {subtitle ? <p className="mt-1 text-xs text-neutral-500">{subtitle}</p> : null}
      </div>
      <div className="mt-4">
        {displayed.length ? (
          <div className="grid gap-2">
            {displayed.map((item) => (
              <div key={item.dimension} className="flex items-center gap-3 text-sm">
                <span className="w-32 shrink-0 truncate font-medium text-neutral-700">{item.dimension}</span>
                <div className="flex-1 overflow-hidden rounded-full bg-neutral-100">
                  <div
                    className="h-5 rounded-full bg-brand-500 transition-all"
                    style={{ width: `${Math.max(3, Math.min(100, (Number(item.value) / maxVal) * 100))}%` }}
                  />
                </div>
                <span className="w-20 text-right text-xs font-semibold text-neutral-900">
                  {typeof item.value === "number" ? item.value.toLocaleString() : item.value}
                </span>
                {item.percentage != null ? (
                  <span className="w-12 text-right text-xs text-neutral-400">{item.percentage}%</span>
                ) : null}
              </div>
            ))}
            {remaining > 0 ? (
              <p className="text-center text-xs text-neutral-400">+ {remaining} more</p>
            ) : null}
          </div>
        ) : (
          <div className="rounded border border-dashed border-neutral-300 p-6 text-center text-sm text-neutral-500">
            {emptyMessage || "No disaggregation data available."}
          </div>
        )}
      </div>
    </div>
  );
}
