"use client";

import Link from "next/link";

export interface ComparisonRow {
  id: string;
  name: string;
  code: string;
  latest_value: string | number | null;
  target: string | number | null;
  achievement: number | null;
  status?: string;
  input_mode?: string;
  data_source?: string;
  /** Optional - for geographic comparison */
  region?: string;
  /** Optional - extra columns for geographic drilldown */
  extra_columns?: Record<string, string | number>;
}

interface Props {
  title: string;
  subtitle?: string;
  rows: ComparisonRow[];
  emptyMessage?: string;
  detailHref?: (row: ComparisonRow) => string;
  /** Optional extra column headers for geographic comparison */
  extraHeaders?: Array<{ key: string; label: string }>;
}

function statusBadge(status: string) {
  const map: Record<string, string> = {
    active: "bg-brand-50 text-brand-700",
    draft: "bg-neutral-100 text-neutral-700",
    inactive: "bg-warning-50 text-warning-700",
    retired: "bg-neutral-100 text-neutral-500",
    archived: "bg-neutral-100 text-neutral-500",
  };
  return `rounded-full px-2 py-0.5 text-xs font-semibold ${map[status] || "bg-neutral-100 text-neutral-600"}`;
}

export function KPIComparisonTable({ title, subtitle, rows, emptyMessage, detailHref, extraHeaders }: Props) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <div>
        <h3 className="text-sm font-bold text-neutral-950">{title}</h3>
        {subtitle ? <p className="mt-1 text-xs text-neutral-500">{subtitle}</p> : null}
      </div>
      <div className="mt-4 overflow-x-auto">
        {rows.length ? (
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-neutral-200 text-left text-xs font-bold uppercase text-neutral-500">
                <th className="py-3 pr-4">Name</th>
                <th className="py-3 pr-4">Code</th>
                {extraHeaders?.map((header) => (
                  <th key={header.key} className="py-3 pr-4">{header.label}</th>
                ))}
                <th className="py-3 pr-4">Latest Value</th>
                <th className="py-3 pr-4">Target</th>
                <th className="py-3 pr-4">Achievement</th>
                <th className="py-3 pr-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {rows.map((row) => (
                <tr className="hover:bg-neutral-50" key={row.id}>
                  <td className="py-3 pr-4">
                    {detailHref ? (
                      <Link href={detailHref(row)} className="font-semibold text-brand-700 hover:underline">
                        {row.name}
                      </Link>
                    ) : (
                      <span className="font-semibold text-neutral-900">{row.name}</span>
                    )}
                  </td>
                  <td className="py-3 pr-4 font-mono text-xs text-neutral-500">{row.code}</td>
                  {extraHeaders?.map((header) => (
                    <td key={header.key} className="py-3 pr-4 text-neutral-700">{row.extra_columns?.[header.key] ?? "-"}</td>
                  ))}
                  <td className="py-3 pr-4 font-medium text-neutral-900">
                    {row.latest_value != null ? String(row.latest_value) : "-"}
                  </td>
                  <td className="py-3 pr-4 text-neutral-500">{row.target != null ? String(row.target) : "-"}</td>
                  <td className="py-3 pr-4">
                    {row.achievement != null ? (
                      <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${
                        row.achievement >= 90 ? "bg-brand-50 text-brand-700" :
                        row.achievement >= 70 ? "bg-warning-50 text-warning-700" :
                        "bg-danger-50 text-danger-700"
                      }`}>
                        {row.achievement}%
                      </span>
                    ) : (
                      <span className="text-neutral-400">-</span>
                    )}
                  </td>
                  <td className="py-3 pr-4">
                    {row.status ? (
                      <span className={statusBadge(row.status)}>
                        {row.status.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase())}
                      </span>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="rounded border border-dashed border-neutral-300 p-6 text-center text-sm text-neutral-500">
            {emptyMessage || "No comparison data available."}
          </div>
        )}
      </div>
    </div>
  );
}
