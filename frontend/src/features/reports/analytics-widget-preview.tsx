"use client";

import { useState } from "react";

import { BrainCircuit, MapPinned, PanelTop, Table2 } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { AnalyticsWidget, AnalyticsWidgetPreviewResponse, AnalyticsWorksheet } from "@/lib/api/analytics";

const PALETTE = ["#16a34a", "#0f766e", "#2563eb", "#7c3aed", "#ea580c", "#dc2626"];

function normalizeChartRows(rows: Array<Record<string, string | number | null>> | undefined, keyOrder: string[]) {
  if (!rows?.length) return [];
  return rows.map((row) => {
    const normalized: Record<string, string | number> = {};
    keyOrder.forEach((key) => {
      const value = row[key];
      normalized[key] = typeof value === "number" ? value : Number(value ?? 0) || String(value ?? "");
    });
    return normalized;
  });
}

export function buildWidgetPreviewFromWorksheet(widget: AnalyticsWidget, worksheet: AnalyticsWorksheet | null | undefined): AnalyticsWidgetPreviewResponse["preview"] | null {
  const worksheetPreview = worksheet?.preview_output;
  if (!worksheetPreview) return null;

  const metrics = worksheetPreview.metrics ?? [];
  const rows = worksheetPreview.rows ?? [];
  const dimensions = worksheetPreview.dimensions ?? [];
  const summary = {
    title: widget.title,
    widget_type: widget.widget_type,
    chart_recommendation: worksheetPreview.chart_recommendation || "table",
    total_rows: worksheetPreview.total_rows || 0,
    dimensions,
  };

  if (widget.widget_type === "kpi_card") {
    const primary = metrics[0] ?? { label: "Value", value: worksheetPreview.total_rows || 0, aggregation: "count" };
    return { ...summary, cards: [primary], rows: rows.slice(0, 1) };
  }
  if (widget.widget_type === "grouped_kpi") {
    return { ...summary, cards: metrics.slice(0, 4), rows: rows.slice(0, 3) };
  }
  if (widget.widget_type === "bar_chart" || widget.widget_type === "line_chart" || widget.widget_type === "map") {
    return {
      ...summary,
      series: rows.slice(0, 8),
      x_axis: dimensions[0] || "",
      metrics,
      visual_config: widget.visual_config,
    };
  }
  if (widget.widget_type === "queue_card") {
    return {
      ...summary,
      items: rows.slice(0, 6),
      count_label: metrics[0]?.label || "Queue items",
    };
  }
  if (widget.widget_type === "ai_insight") {
    const topMetric = metrics[0] ?? { label: "Records", value: worksheetPreview.total_rows || 0, aggregation: "count" };
    return {
      ...summary,
      insights: [
        `${topMetric.label}: ${topMetric.value}`,
        `Preview rows available: ${worksheetPreview.total_rows || 0}`,
        "Insights are generated only from worksheet output and saved widget configuration.",
      ],
      metrics: metrics.slice(0, 3),
    };
  }
  return {
    ...summary,
    columns: rows[0] ? Object.keys(rows[0]) : dimensions,
    rows: rows.slice(0, 10),
    metrics,
  };
}

export function WidgetPreviewSurface({ preview }: { preview: AnalyticsWidgetPreviewResponse["preview"] | null }) {
  const [page, setPage] = useState(1);
  if (!preview) {
    return <div className="rounded-lg border border-dashed border-neutral-300 bg-white p-8 text-sm text-neutral-500">Pick a worksheet and widget type to preview the visual output.</div>;
  }

  if (preview.widget_type === "kpi_card") {
    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {(preview.cards ?? []).map((card) => (
          <div key={`${card.label}-${card.aggregation}`} className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-2">
              <PanelTop className="text-brand-700" size={16} />
              <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">{card.label}</p>
            </div>
            <p className="mt-3 text-3xl font-bold text-neutral-950">{card.value ?? "—"}</p>
          </div>
        ))}
      </div>
    );
  }

  if (preview.widget_type === "grouped_kpi") {
    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {(preview.cards ?? []).map((card) => (
          <div key={`${card.label}-${card.aggregation}`} className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">{card.label}</p>
            <p className="mt-2 text-2xl font-bold text-neutral-950">{card.value ?? "—"}</p>
          </div>
        ))}
      </div>
    );
  }

  if (preview.widget_type === "bar_chart") {
    const keyOrder = preview.series?.[0] ? Object.keys(preview.series[0]) : [];
    const xKey = preview.x_axis || keyOrder[0];
    const yKey = keyOrder.find((key) => key !== xKey) || keyOrder[1];
    const chartData = normalizeChartRows(preview.series, keyOrder);
    return (
      <div className="h-[360px] rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey={yKey} fill="#16a34a" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  if (preview.widget_type === "line_chart") {
    const keyOrder = preview.series?.[0] ? Object.keys(preview.series[0]) : [];
    const xKey = preview.x_axis || keyOrder[0];
    const yKey = keyOrder.find((key) => key !== xKey) || keyOrder[1];
    const chartData = normalizeChartRows(preview.series, keyOrder);
    return (
      <div className="h-[360px] rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Line type="monotone" dataKey={yKey} stroke="#2563eb" strokeWidth={3} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  }

  if (preview.widget_type === "map") {
    const rows = preview.series ?? [];
    const keyOrder = rows[0] ? Object.keys(rows[0]) : [];
    const labelKey = preview.x_axis || keyOrder[0];
    const valueKey = keyOrder.find((key) => key !== labelKey) || keyOrder[1];
    return (
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_280px]">
        <div className="rounded-lg border border-neutral-200 bg-neutral-50 p-5 shadow-sm">
          <div className="flex h-full min-h-[320px] items-center justify-center rounded-md border border-dashed border-neutral-300 bg-white">
            <div className="text-center">
              <MapPinned className="mx-auto text-brand-700" size={28} />
              <p className="mt-3 text-sm font-semibold text-neutral-900">Geographic comparison preview</p>
              <p className="mt-1 text-sm text-neutral-500">This widget uses scoped worksheet rows to drive state or LGA performance views.</p>
            </div>
          </div>
        </div>
        <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <p className="text-sm font-bold text-neutral-900">Geography ranking</p>
          <div className="mt-4 space-y-3">
            {rows.slice(0, 6).map((row, index) => (
              <div key={`${String(row[labelKey])}-${index}`} className="flex items-center justify-between rounded-md bg-neutral-50 px-3 py-2">
                <span className="text-sm text-neutral-700">{String(row[labelKey] ?? "Unknown")}</span>
                <span className="text-sm font-bold text-neutral-950">{String(row[valueKey] ?? "—")}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (preview.widget_type === "queue_card") {
    const items = preview.items ?? [];
    const pageSize = preview.pagination?.page_size ?? 6;
    const totalPages = Math.max(1, Math.ceil(items.length / pageSize));
    const pagedItems = items.slice((page - 1) * pageSize, page * pageSize);
    return (
      <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <Table2 className="text-brand-700" size={16} />
              <p className="text-sm font-bold text-neutral-900">{preview.count_label || "Queue"}</p>
            </div>
            <p className="mt-1 text-sm text-neutral-500">{items.length} items surfaced from the worksheet preview.</p>
          </div>
          <span className="rounded-full bg-brand-50 px-3 py-1 text-sm font-bold text-brand-700">{items.length}</span>
        </div>
        <div className="mt-4 space-y-3">
          {pagedItems.map((item, index) => (
            <div key={index} className="rounded-md border border-neutral-200 p-3">
              {Object.entries(item).slice(0, 3).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between gap-3 text-sm">
                  <span className="text-neutral-500">{key.replaceAll("_", " ")}</span>
                  <span className="font-medium text-neutral-900">{value == null || value === "" ? "—" : String(value)}</span>
                </div>
              ))}
            </div>
          ))}
        </div>
        {totalPages > 1 ? (
          <div className="mt-4 flex items-center justify-end gap-2">
            <button type="button" onClick={() => setPage((current) => Math.max(1, current - 1))} className="rounded-md border border-neutral-200 px-3 py-2 text-xs font-semibold text-neutral-700">
              Prev
            </button>
            <span className="text-xs text-neutral-500">Page {page} of {totalPages}</span>
            <button type="button" onClick={() => setPage((current) => Math.min(totalPages, current + 1))} className="rounded-md border border-neutral-200 px-3 py-2 text-xs font-semibold text-neutral-700">
              Next
            </button>
          </div>
        ) : null}
      </div>
    );
  }

  if (preview.widget_type === "ai_insight") {
    const chartData = (preview.metrics ?? []).map((metric) => ({
      name: metric.label,
      value: typeof metric.value === "number" ? metric.value : Number(metric.value ?? 0) || 0,
    }));
    return (
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <BrainCircuit className="text-brand-700" size={18} />
            <p className="text-sm font-bold text-neutral-900">Insight summary</p>
          </div>
          <div className="mt-4 space-y-3">
            {(preview.insights ?? []).map((line) => (
              <p key={line} className="rounded-md bg-neutral-50 px-3 py-2 text-sm text-neutral-700">{line}</p>
            ))}
          </div>
        </div>
        <div className="h-[320px] rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={chartData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={92}>
                {chartData.map((entry, index) => (
                  <Cell key={entry.name} fill={PALETTE[index % PALETTE.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  const columns = preview.columns ?? Object.keys(preview.rows?.[0] ?? {});
  const rows = preview.rows ?? [];
  const pageSize = preview.pagination?.page_size ?? 10;
  const totalPages = Math.max(1, Math.ceil(rows.length / pageSize));
  const pagedRows = rows.slice((page - 1) * pageSize, page * pageSize);
  return (
    <div className="overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-neutral-200 text-sm">
          <thead className="bg-neutral-50">
            <tr>
              {columns.map((column) => (
                <th key={column} className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-neutral-500">
                  {column.replaceAll("_", " ")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100 bg-white">
            {pagedRows.map((row, index) => (
              <tr key={index}>
                {columns.map((column) => (
                  <td key={column} className="px-4 py-3 text-neutral-700">{row[column] == null || row[column] === "" ? "—" : String(row[column])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {totalPages > 1 ? (
        <div className="flex items-center justify-end gap-2 border-t border-neutral-200 bg-neutral-50 px-4 py-3">
          <button type="button" onClick={() => setPage((current) => Math.max(1, current - 1))} className="rounded-md border border-neutral-200 bg-white px-3 py-2 text-xs font-semibold text-neutral-700">
            Prev
          </button>
          <span className="text-xs text-neutral-500">Page {page} of {totalPages}</span>
          <button type="button" onClick={() => setPage((current) => Math.min(totalPages, current + 1))} className="rounded-md border border-neutral-200 bg-white px-3 py-2 text-xs font-semibold text-neutral-700">
            Next
          </button>
        </div>
      ) : null}
    </div>
  );
}
