"use client";

import type {
  AnalyticsWidget,
  AnalyticsWidgetPreviewResponse,
  AnalyticsWorksheet,
  PublishedDashboardSnapshotBlock,
} from "@/lib/api/analytics";

export type FilterStateValue = string | { from?: string; to?: string };

export type CompatibleFieldOption = {
  field: string;
  label: string;
  widgetIds: string[];
  widgetTitles: string[];
};

export function valuesForBlock(preview: AnalyticsWidgetPreviewResponse["preview"] | null | undefined) {
  if (!preview) return [];
  if (preview.series?.length) return preview.series;
  if (preview.rows?.length) return preview.rows;
  if (preview.items?.length) return preview.items;
  return [];
}

export function filterRowsByField(
  rows: Array<Record<string, string | number | null>>,
  field: string,
  value: FilterStateValue | undefined,
) {
  if (!field || value == null || value === "") return rows;
  if (typeof value === "string") {
    return rows.filter((row) => String(row[field] ?? "") === value);
  }
  const from = value.from ?? "";
  const to = value.to ?? "";
  return rows.filter((row) => {
    const current = String(row[field] ?? "");
    if (!current) return false;
    if (from && current < from) return false;
    if (to && current > to) return false;
    return true;
  });
}

export function applyFiltersToPreview(
  preview: AnalyticsWidgetPreviewResponse["preview"] | null | undefined,
  filters: Record<string, FilterStateValue>,
) {
  if (!preview) return null;

  const candidateRows = valuesForBlock(preview);
  if (!candidateRows.length) return preview;

  let filteredRows = candidateRows;
  for (const [field, value] of Object.entries(filters)) {
    const fieldExists = filteredRows.some((row) => field in row);
    if (!fieldExists) continue;
    filteredRows = filterRowsByField(filteredRows, field, value);
  }

  if (preview.series?.length) {
    return { ...preview, series: filteredRows, total_rows: filteredRows.length };
  }
  if (preview.rows?.length) {
    return { ...preview, rows: filteredRows, total_rows: filteredRows.length };
  }
  if (preview.items?.length) {
    return { ...preview, items: filteredRows, total_rows: filteredRows.length };
  }
  return preview;
}

export function buildFilterFieldOptions(widgets: AnalyticsWidget[], worksheets: AnalyticsWorksheet[]) {
  const byField = new Map<string, CompatibleFieldOption>();

  for (const widget of widgets) {
    const worksheet = worksheets.find((item) => item.id === widget.worksheet);
    if (!worksheet) continue;

    const candidateFields = new Set<string>();
    for (const dimension of worksheet.dimensions ?? []) {
      if (dimension.field) candidateFields.add(dimension.field);
    }
    for (const filter of worksheet.filters ?? []) {
      if (filter.field) candidateFields.add(filter.field);
    }
    for (const row of worksheet.preview_output?.rows ?? []) {
      Object.keys(row).forEach((key) => candidateFields.add(key));
    }

    for (const field of candidateFields) {
      const current = byField.get(field) ?? {
        field,
        label: field.replaceAll("_", " "),
        widgetIds: [],
        widgetTitles: [],
      };
      if (!current.widgetIds.includes(widget.id)) {
        current.widgetIds.push(widget.id);
        current.widgetTitles.push(widget.title);
      }
      byField.set(field, current);
    }
  }

  return Array.from(byField.values()).sort((left, right) => left.label.localeCompare(right.label));
}

export function applicableWidgetIdsForFilter(field: string, options: CompatibleFieldOption[]) {
  return options.find((option) => option.field === field)?.widgetIds ?? [];
}

export function filterOptionsFromPublishedBlocks(blocks: PublishedDashboardSnapshotBlock[]) {
  const entries = blocks
    .filter((block) => block.block_type === "filter")
    .map((block) => {
      const field = String(block.content.field ?? "");
      const values = blocks.flatMap((item) =>
        valuesForBlock(item.preview).map((row) => String(row[field] ?? "")).filter(Boolean),
      );
      return [field, Array.from(new Set(values))] as const;
    });
  return Object.fromEntries(entries);
}
