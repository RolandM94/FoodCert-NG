"use client";

export interface StateComparisonRow {
  state: string;
  kpi_count: number;
  total_value: number;
  achievement: number | null;
}

interface Props {
  rows: StateComparisonRow[];
  onDrilldown?: (state: string) => void;
}

function achievementBadge(value: number | null) {
  if (value == null) return <span className="text-neutral-400">-</span>;
  const cls = value >= 90 ? "bg-brand-50 text-brand-700" :
    value >= 70 ? "bg-warning-50 text-warning-700" :
    "bg-danger-50 text-danger-700";
  return <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${cls}`}>{value}%</span>;
}

export function KPIStateComparisonTable({ rows, onDrilldown }: Props) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-bold text-neutral-950">State KPI Comparison</h3>
          <p className="mt-1 text-xs text-neutral-500">Per-state KPI achievement based on disaggregated indicator values.</p>
        </div>
        <span className="rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-semibold text-neutral-600">{rows.length} states</span>
      </div>
      <div className="mt-4 overflow-x-auto">
        {rows.length ? (
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-neutral-200 text-left text-xs font-bold uppercase text-neutral-500">
                <th className="py-3 pr-4">State</th>
                <th className="py-3 pr-4">KPIs Tracked</th>
                <th className="py-3 pr-4">Total Value</th>
                <th className="py-3 pr-4">Avg Achievement</th>
                <th className="py-3 pr-4" />
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {rows.map((row) => (
                <tr className="hover:bg-neutral-50" key={row.state}>
                  <td className="py-3 pr-4 font-bold text-neutral-900">{row.state}</td>
                  <td className="py-3 pr-4 text-neutral-700">{row.kpi_count}</td>
                  <td className="py-3 pr-4 font-medium text-neutral-900">{row.total_value.toLocaleString()}</td>
                  <td className="py-3 pr-4">{achievementBadge(row.achievement)}</td>
                  <td className="py-3 pr-4">
                    {onDrilldown ? (
                      <button
                        type="button"
                        onClick={() => onDrilldown(row.state)}
                        className="rounded border border-brand-200 px-3 py-1 text-xs font-semibold text-brand-700 hover:bg-brand-50"
                      >
                        Drill down
                      </button>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="rounded border border-dashed border-neutral-300 p-6 text-center text-sm text-neutral-500">
            No state-level KPI data available. Disaggregated values with &quot;state&quot; dimension are needed for state comparison.
          </div>
        )}
      </div>
    </div>
  );
}
