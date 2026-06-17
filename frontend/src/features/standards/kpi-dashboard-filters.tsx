"use client";

import { useCallback } from "react";

export type KPIDashboardFilterValues = {
  period_start: string;
  period_end: string;
  status: string;
  input_mode: string;
  data_source: string;
  state_id: string;
  lga_id: string;
  facility_type: string;
  test_center: string;
  certificate_status: string;
  test_status: string;
};

const KPI_DATA_SOURCES = [
  "manual",
  "food_handler_registry",
  "medical_test_records",
  "test_results",
  "certificate_records",
  "facility_records",
  "facility_handler_mapping",
  "test_centers_labs",
  "inspections",
  "training_orientation",
  "payments",
  "kpi",
];

function nice(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

interface Props {
  filters: KPIDashboardFilterValues;
  onChange: (field: keyof KPIDashboardFilterValues, value: string) => void;
  onReset: () => void;
  showGeography?: boolean;
  showFacilityFilters?: boolean;
}

export function KPIDashboardFilters({ filters, onChange, onReset, showGeography, showFacilityFilters }: Props) {
  const select = useCallback(
    (field: keyof KPIDashboardFilterValues) => (event: React.ChangeEvent<HTMLSelectElement>) => onChange(field, event.target.value),
    [onChange],
  );
  const dateInput = useCallback(
    (field: keyof KPIDashboardFilterValues) => (event: React.ChangeEvent<HTMLInputElement>) => onChange(field, event.target.value),
    [onChange],
  );
  const reset = useCallback(() => {
    onChange("period_start", "");
    onChange("period_end", "");
    onChange("status", "");
    onChange("input_mode", "");
    onChange("data_source", "");
    onChange("state_id", "");
    onChange("lga_id", "");
    onChange("facility_type", "");
    onChange("test_center", "");
    onChange("certificate_status", "");
    onChange("test_status", "");
    onReset();
  }, [onChange, onReset]);

  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <div className="flex flex-wrap items-end gap-3">
        <label className="text-sm font-medium text-neutral-700">
          Period start
          <input type="date" className="mt-1 h-10 rounded border border-neutral-200 px-3 text-sm w-full min-w-[160px]" value={filters.period_start} onChange={dateInput("period_start")} />
        </label>
        <label className="text-sm font-medium text-neutral-700">
          Period end
          <input type="date" className="mt-1 h-10 rounded border border-neutral-200 px-3 text-sm w-full min-w-[160px]" value={filters.period_end} onChange={dateInput("period_end")} />
        </label>
        <label className="text-sm font-medium text-neutral-700">
          KPI status
          <select className="mt-1 h-10 rounded border border-neutral-200 bg-white px-3 text-sm w-full min-w-[140px]" value={filters.status} onChange={select("status")}>
            <option value="">All statuses</option>
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="retired">Retired</option>
            <option value="archived">Archived</option>
          </select>
        </label>
        <label className="text-sm font-medium text-neutral-700">
          Input mode
          <select className="mt-1 h-10 rounded border border-neutral-200 bg-white px-3 text-sm w-full min-w-[140px]" value={filters.input_mode} onChange={select("input_mode")}>
            <option value="">All modes</option>
            <option value="manual">Manual</option>
            <option value="automated">Automated</option>
            <option value="hybrid">Hybrid</option>
          </select>
        </label>
        <label className="text-sm font-medium text-neutral-700">
          Source
          <select className="mt-1 h-10 rounded border border-neutral-200 bg-white px-3 text-sm w-full min-w-[160px]" value={filters.data_source} onChange={select("data_source")}>
            <option value="">All sources</option>
            {KPI_DATA_SOURCES.map((source) => <option key={source} value={source}>{nice(source)}</option>)}
          </select>
        </label>
        {showGeography ? (
          <>
            <label className="text-sm font-medium text-neutral-700">
              State
              <input className="mt-1 h-10 rounded border border-neutral-200 px-3 text-sm w-full min-w-[120px]" placeholder="Filter by state" value={filters.state_id} onChange={dateInput("state_id")} />
            </label>
            <label className="text-sm font-medium text-neutral-700">
              LGA
              <input className="mt-1 h-10 rounded border border-neutral-200 px-3 text-sm w-full min-w-[120px]" placeholder="Filter by LGA" value={filters.lga_id} onChange={dateInput("lga_id")} />
            </label>
          </>
        ) : null}
        {showFacilityFilters ? (
          <>
            <label className="text-sm font-medium text-neutral-700">
              Facility type
              <select className="mt-1 h-10 rounded border border-neutral-200 bg-white px-3 text-sm w-full min-w-[140px]" value={filters.facility_type} onChange={select("facility_type")}>
                <option value="">All types</option>
                <option value="hospital">Hospital</option>
                <option value="clinic">Clinic</option>
                <option value="lab">Laboratory</option>
                <option value="pharmacy">Pharmacy</option>
              </select>
            </label>
            <label className="text-sm font-medium text-neutral-700">
              Certificate
              <select className="mt-1 h-10 rounded border border-neutral-200 bg-white px-3 text-sm w-full min-w-[140px]" value={filters.certificate_status} onChange={select("certificate_status")}>
                <option value="">All certificate statuses</option>
                <option value="valid">Valid</option>
                <option value="expiring">Expiring</option>
                <option value="expired">Expired</option>
                <option value="revoked">Revoked</option>
              </select>
            </label>
            <label className="text-sm font-medium text-neutral-700">
              Test status
              <select className="mt-1 h-10 rounded border border-neutral-200 bg-white px-3 text-sm w-full min-w-[140px]" value={filters.test_status} onChange={select("test_status")}>
                <option value="">All test statuses</option>
                <option value="pending">Pending</option>
                <option value="in_progress">In progress</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
              </select>
            </label>
          </>
        ) : null}
        <button type="button" onClick={reset} className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50 whitespace-nowrap">
          Reset Filters
        </button>
      </div>
    </div>
  );
}
