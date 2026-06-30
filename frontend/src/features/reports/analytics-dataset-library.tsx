"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, ArrowLeft, ArrowRight, ChevronDown, Database, Loader2, Search, Settings2, X } from "lucide-react";

import {
  changeAnalyticsDatasetFieldType,
  checkAnalyticsDatasetFieldTypeCompatibility,
  getAnalyticsDatasetSample,
  listAnalyticsDatasets,
} from "@/lib/api/analytics";
import { getApiErrorMessage } from "@/lib/api/client";

type AnalyticsDatasetLibraryProps = {
  datasetId: string;
  homeHref: string;
  worksheetBuilderHref: string;
};

function formatLabel(value: string) {
  return value.replaceAll("__", " / ").replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function normalizeFieldType(value?: string) {
  if (!value) return "text";
  return value.replaceAll("_", " ").toLowerCase();
}

function displayFieldTypeLabel(value?: string) {
  const normalized = String(value || "").toLowerCase();
  if (normalized === "number_whole") return "Number whole";
  if (normalized === "number_decimal") return "Number decimal";
  if (normalized === "datetime") return "DateTime";
  if (normalized === "date") return "Date";
  return "String";
}

function isNumericValue(value: unknown) {
  return typeof value === "number" || (typeof value === "string" && value.trim() !== "" && !Number.isNaN(Number(value)));
}

function formatCellValue(value: unknown) {
  if (value == null || value === "") {
    return "—";
  }
  if (typeof value === "boolean") {
    return value ? "True" : "False";
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? value.toLocaleString() : value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }
  return String(value);
}

export function AnalyticsDatasetLibrary({
  datasetId,
  homeHref,
  worksheetBuilderHref,
}: AnalyticsDatasetLibraryProps) {
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [typeEditorField, setTypeEditorField] = useState<string | null>(null);
  const [targetFieldType, setTargetFieldType] = useState("string");
  const [confirmIncompatible, setConfirmIncompatible] = useState(false);
  const queryClient = useQueryClient();

  const datasetsQuery = useQuery({
    queryKey: ["analytics-datasets"],
    queryFn: listAnalyticsDatasets,
  });
  const sampleQuery = useQuery({
    queryKey: ["analytics-dataset-sample", datasetId],
    queryFn: () => getAnalyticsDatasetSample(datasetId),
    enabled: Boolean(datasetId),
  });

  const dataset = useMemo(
    () => (datasetsQuery.data ?? []).find((item) => item.id === datasetId),
    [datasetId, datasetsQuery.data],
  );
  const columns = useMemo(
    () => Object.keys(sampleQuery.data?.rows?.[0] ?? {}),
    [sampleQuery.data?.rows],
  );
  const filteredRows = useMemo(() => {
    const rows = sampleQuery.data?.rows ?? [];
    if (!columns.length) {
      return rows;
    }
    return rows.filter((row) =>
      columns.every((column) => {
        const filterValue = filters[column]?.trim().toLowerCase();
        if (!filterValue) {
          return true;
        }
        return String(row[column] ?? "").toLowerCase().includes(filterValue);
      }),
    );
  }, [columns, filters, sampleQuery.data?.rows]);
  const activeFilterCount = useMemo(
    () => Object.values(filters).filter((value) => value.trim().length > 0).length,
    [filters],
  );
  const selectedFieldMetadata = typeEditorField ? dataset?.field_type_metadata?.[typeEditorField] : undefined;
  const currentFieldType = selectedFieldMetadata?.type || (typeEditorField ? dataset?.field_types?.[typeEditorField] : "") || "string";
  const inferredFieldType = selectedFieldMetadata?.inferredType || currentFieldType;

  const compatibilityMutation = useMutation({
    mutationFn: (payload: { field: string; target_type: string }) =>
      checkAnalyticsDatasetFieldTypeCompatibility(datasetId, payload),
  });

  const changeTypeMutation = useMutation({
    mutationFn: (payload: { field: string; target_type: string; force?: boolean }) =>
      changeAnalyticsDatasetFieldType(datasetId, payload),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["analytics-datasets"] }),
        queryClient.invalidateQueries({ queryKey: ["analytics-dataset-sample", datasetId] }),
      ]);
      setTypeEditorField(null);
      setConfirmIncompatible(false);
    },
  });

  const workbookHref = useMemo(() => {
    const params = new URLSearchParams();
    if (datasetId) {
      params.set("dataset", datasetId);
    }
    return params.size ? `${worksheetBuilderHref}?${params.toString()}` : worksheetBuilderHref;
  }, [datasetId, worksheetBuilderHref]);

  function openFieldTypeEditor(fieldName: string) {
    const initialType = dataset?.field_type_metadata?.[fieldName]?.type || dataset?.field_types?.[fieldName] || "string";
    setTypeEditorField(fieldName);
    setTargetFieldType(initialType);
    setConfirmIncompatible(false);
    compatibilityMutation.reset();
    changeTypeMutation.reset();
  }

  async function runCompatibilityCheck() {
    if (!typeEditorField) return;
    await compatibilityMutation.mutateAsync({
      field: typeEditorField,
      target_type: targetFieldType,
    });
  }

  async function applyFieldTypeChange() {
    if (!typeEditorField) return;
    const compatibility =
      compatibilityMutation.data && compatibilityMutation.data.field === typeEditorField && compatibilityMutation.data.targetType === targetFieldType
        ? compatibilityMutation.data
        : await compatibilityMutation.mutateAsync({
            field: typeEditorField,
            target_type: targetFieldType,
          });
    await changeTypeMutation.mutateAsync({
      field: typeEditorField,
      target_type: targetFieldType,
      force: compatibility.requiresConfirmation ? confirmIncompatible : false,
    });
  }

  if (datasetsQuery.isLoading || sampleQuery.isLoading) {
    return (
      <div className="rounded-lg border border-neutral-200 bg-white p-8 text-sm text-neutral-500 shadow-sm">
        <div className="flex items-center gap-2">
          <Loader2 className="animate-spin text-brand-700" size={16} />
          Loading dataset library...
        </div>
      </div>
    );
  }

  if (datasetsQuery.isError || sampleQuery.isError) {
    return (
      <div className="rounded-lg border border-danger-200 bg-danger-50 px-4 py-3 text-sm font-medium text-danger-700">
        {getApiErrorMessage(datasetsQuery.error ?? sampleQuery.error, "Could not load dataset library.")}
      </div>
    );
  }

  if (!dataset) {
    return (
      <div className="rounded-lg border border-neutral-200 bg-white p-8 text-sm text-neutral-500 shadow-sm">
        Dataset not found.
      </div>
    );
  }

  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap items-center gap-2 text-sm text-neutral-400">
        <Link href={homeHref} className="inline-flex items-center gap-2 font-medium text-neutral-500 hover:text-brand-700">
          <ArrowLeft size={15} />
          Home
        </Link>
        <span>/</span>
        <span className="font-medium text-neutral-700">{dataset.name}</span>
      </div>

      <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4 px-5 py-4">
          <div className="min-w-0 space-y-3">
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-sky-50 text-sky-700">
                <Database size={18} />
              </div>
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-3">
                  <h2 className="text-[28px] font-bold leading-none text-neutral-950">{dataset.name}</h2>
                </div>
                <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-neutral-500">
                  <span>{filteredRows.length.toLocaleString()} of {(sampleQuery.data?.row_count ?? 0).toLocaleString()} rows loaded</span>
                  <span className="text-neutral-300">|</span>
                  <span>{dataset.available_fields.length} fields</span>
                </div>
              </div>
            </div>
            <p className="max-w-4xl text-sm leading-6 text-neutral-500">{dataset.description}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex h-8 items-center rounded-full bg-neutral-100 px-3 text-xs font-semibold text-neutral-600">
              Data table
            </span>
            <Link
              href={workbookHref}
              className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-semibold text-white"
            >
              Plot in Workbook
              <ArrowRight size={15} />
            </Link>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2 border-t border-neutral-200 bg-neutral-50 px-5 py-3 text-xs font-medium text-neutral-500">
          <span>Dataset key: <span className="font-semibold text-neutral-700">{dataset.code}</span></span>
          <span className="text-neutral-300">•</span>
          <span>Module: <span className="font-semibold text-neutral-700">{formatLabel(dataset.module_source || "dataset")}</span></span>
          <span className="text-neutral-300">•</span>
          <span>{activeFilterCount} active filters</span>
        </div>
      </section>

      <section className="overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-200 bg-white px-4 py-3">
          <div className="flex items-center gap-2">
            <p className="text-sm font-semibold text-neutral-800">Dataset preview</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {activeFilterCount ? (
              <button
                type="button"
                onClick={() => setFilters({})}
                className="inline-flex h-8 items-center gap-1 rounded-md border border-neutral-200 bg-white px-3 text-xs font-semibold text-neutral-600 hover:text-neutral-900"
              >
                <X size={13} />
                Clear filters
              </button>
            ) : null}
            <span className="text-xs font-medium text-neutral-500">
              {columns.length} columns
            </span>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1180px] text-left text-sm">
            <thead className="sticky top-0 z-10 border-b border-neutral-200 bg-white">
              <tr className="border-b border-neutral-200 bg-white text-[11px] font-bold uppercase tracking-[0.08em] text-neutral-500">
                {columns.map((column) => (
                  <th key={column} className="px-4 py-3 align-bottom">
                    <div className="space-y-2">
                      <span className="block leading-4">{dataset.field_labels?.[column] || formatLabel(column)}</span>
                      <button
                        type="button"
                        onClick={() => openFieldTypeEditor(column)}
                        className="inline-flex h-7 items-center gap-1 rounded-full bg-neutral-100 px-2.5 text-[10px] font-semibold normal-case tracking-normal text-neutral-500 transition hover:bg-neutral-200 hover:text-neutral-700"
                      >
                        {displayFieldTypeLabel(dataset.field_type_metadata?.[column]?.type || dataset.field_types?.[column])}
                        <ChevronDown size={11} />
                      </button>
                    </div>
                  </th>
                ))}
              </tr>
              <tr className="border-b border-neutral-200 bg-white">
                {columns.map((column) => (
                  <th key={`${column}-filter`} className="px-4 py-2">
                    <div className="relative">
                      <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-neutral-300" size={12} />
                      <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-neutral-300" size={12} />
                      <input
                        className="h-9 w-full rounded-md border border-neutral-200 bg-white pl-8 pr-8 text-xs font-medium text-neutral-700 outline-none placeholder:text-neutral-400 focus:border-brand-300"
                        placeholder={normalizeFieldType(dataset.field_types?.[column]) === "text" ? "default" : normalizeFieldType(dataset.field_types?.[column])}
                        value={filters[column] ?? ""}
                        onChange={(event) =>
                          setFilters((current) => ({
                            ...current,
                            [column]: event.target.value,
                          }))
                        }
                      />
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200">
              {filteredRows.map((row, rowIndex) => (
                <tr key={`${dataset.id}-${rowIndex}`} className="bg-white transition-colors hover:bg-neutral-50">
                  {columns.map((column) => (
                    <td
                      key={`${rowIndex}-${column}`}
                      className={`max-w-xs px-4 py-3 align-top text-sm ${isNumericValue(row[column]) ? "text-right font-medium tabular-nums text-neutral-800" : "text-neutral-700"}`}
                      title={formatCellValue(row[column])}
                    >
                      <div className="truncate">{formatCellValue(row[column])}</div>
                    </td>
                  ))}
                </tr>
              ))}
              {!filteredRows.length ? (
                <tr>
                  <td colSpan={Math.max(columns.length, 1)} className="px-4 py-10 text-center text-sm text-neutral-500">
                    No rows match the current filters.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>

      {typeEditorField ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-neutral-950/35 p-4">
          <div className="w-full max-w-2xl rounded-lg border border-neutral-200 bg-white shadow-xl">
            <div className="flex items-start justify-between gap-4 border-b border-neutral-200 px-6 py-5">
              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Change field type</p>
                <h3 className="mt-2 text-xl font-bold text-neutral-950">{dataset?.field_labels?.[typeEditorField] || formatLabel(typeEditorField)}</h3>
                <p className="mt-2 text-sm text-neutral-500">
                  Update analytics metadata only. Raw dataset rows will stay unchanged, but filters, charts, KPIs, and aggregations will use the active type.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setTypeEditorField(null)}
                className="grid h-9 w-9 place-items-center rounded-full bg-neutral-50 text-neutral-500 hover:text-neutral-900"
                aria-label="Close"
              >
                <X size={16} />
              </button>
            </div>

            <div className="space-y-5 px-6 py-5">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-lg border border-neutral-200 bg-neutral-50 p-4">
                  <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Inferred type</p>
                  <p className="mt-2 text-sm font-semibold text-neutral-900">{displayFieldTypeLabel(inferredFieldType)}</p>
                </div>
                <div className="rounded-lg border border-neutral-200 bg-neutral-50 p-4">
                  <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Current active type</p>
                  <p className="mt-2 text-sm font-semibold text-neutral-900">{displayFieldTypeLabel(currentFieldType)}</p>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wide text-neutral-500">New active type</label>
                <select
                  value={targetFieldType}
                  onChange={(event) => {
                    setTargetFieldType(event.target.value);
                    setConfirmIncompatible(false);
                    compatibilityMutation.reset();
                    changeTypeMutation.reset();
                  }}
                  className="mt-2 h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm font-medium text-neutral-800"
                >
                  {[
                    ["string", "String"],
                    ["number_whole", "Number Whole"],
                    ["number_decimal", "Number Decimal"],
                    ["date", "Date"],
                    ["datetime", "DateTime"],
                  ].map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="rounded-lg border border-neutral-200 bg-white p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-neutral-900">Compatibility check</p>
                    <p className="mt-1 text-sm text-neutral-500">Validate existing row values before applying the field type override.</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => void runCompatibilityCheck()}
                    disabled={compatibilityMutation.isPending}
                    className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700 disabled:opacity-60"
                  >
                    {compatibilityMutation.isPending ? <Loader2 className="animate-spin" size={15} /> : <Settings2 size={15} />}
                    Run check
                  </button>
                </div>

                {compatibilityMutation.isError ? (
                  <div className="mt-4 rounded-md border border-danger-200 bg-danger-50 px-4 py-3 text-sm text-danger-700">
                    {getApiErrorMessage(compatibilityMutation.error, "Could not run compatibility check.")}
                  </div>
                ) : null}

                {compatibilityMutation.data ? (
                  <div className="mt-4 space-y-4">
                    <div className="grid gap-3 md:grid-cols-4">
                      {[
                        ["Total rows", compatibilityMutation.data.totalRows],
                        ["Compatible", compatibilityMutation.data.compatibleRows],
                        ["Empty", compatibilityMutation.data.emptyRows],
                        ["Invalid", compatibilityMutation.data.incompatibleRows],
                      ].map(([label, value]) => (
                        <div key={String(label)} className="rounded-md border border-neutral-200 bg-neutral-50 px-3 py-3">
                          <p className="text-[11px] font-bold uppercase tracking-wide text-neutral-500">{label}</p>
                          <p className="mt-2 text-lg font-bold text-neutral-900">{Number(value).toLocaleString()}</p>
                        </div>
                      ))}
                    </div>

                    {compatibilityMutation.data.incompatibleRows > 0 ? (
                      <div className="rounded-md border border-amber-200 bg-amber-50 p-4">
                        <div className="flex items-start gap-2">
                          <AlertTriangle size={16} className="mt-0.5 text-amber-700" />
                          <div>
                            <p className="text-sm font-semibold text-amber-900">Some values do not match the selected type.</p>
                            <p className="mt-1 text-sm text-amber-800">
                              You can still save the override, but those rows may not behave as expected in filtering, grouping, or numeric aggregation.
                            </p>
                            {compatibilityMutation.data.invalidExamples.length ? (
                              <div className="mt-3">
                                <p className="text-xs font-bold uppercase tracking-wide text-amber-700">Example invalid values</p>
                                <div className="mt-2 flex flex-wrap gap-2">
                                  {compatibilityMutation.data.invalidExamples.map((value, index) => (
                                    <span key={`${value}-${index}`} className="rounded-full bg-white px-2.5 py-1 text-xs font-semibold text-amber-900">
                                      {value}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            ) : null}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800">
                        All checked values are compatible with the selected type.
                      </div>
                    )}
                  </div>
                ) : null}
              </div>

              {compatibilityMutation.data?.requiresConfirmation ? (
                <label className="flex items-start gap-3 rounded-md border border-neutral-200 bg-neutral-50 px-4 py-3 text-sm text-neutral-700">
                  <input
                    type="checkbox"
                    className="mt-1 h-4 w-4 rounded border-neutral-300"
                    checked={confirmIncompatible}
                    onChange={(event) => setConfirmIncompatible(event.target.checked)}
                  />
                  <span>I understand that incompatible values will remain unchanged in the raw dataset and I still want to save this field type override.</span>
                </label>
              ) : null}

              {changeTypeMutation.isError ? (
                <div className="rounded-md border border-danger-200 bg-danger-50 px-4 py-3 text-sm text-danger-700">
                  {getApiErrorMessage(changeTypeMutation.error, "Could not save field type change.")}
                </div>
              ) : null}
            </div>

            <div className="flex items-center justify-between gap-3 border-t border-neutral-200 px-6 py-4">
              <p className="text-xs text-neutral-500">Only field metadata is updated. Raw source values are never rewritten here.</p>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setTypeEditorField(null)}
                  className="h-10 rounded-md border border-neutral-200 px-4 text-sm font-semibold text-neutral-700"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => void applyFieldTypeChange()}
                  disabled={
                    compatibilityMutation.isPending ||
                    changeTypeMutation.isPending ||
                    !compatibilityMutation.data ||
                    (compatibilityMutation.data.requiresConfirmation && !confirmIncompatible)
                  }
                  className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-semibold text-white disabled:opacity-60"
                >
                  {changeTypeMutation.isPending ? <Loader2 className="animate-spin" size={15} /> : null}
                  Save field type
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
