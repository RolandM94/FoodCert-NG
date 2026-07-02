"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { listIndicatorAdoptions } from "@/lib/api/performance-indicators";
import type { IndicatorAdoption } from "@/types/standards";

const STATUS_TONES: Record<string, string> = {
  adopted: "bg-brand-50 text-brand-700",
  cloned: "bg-info-50 text-info-700",
  available: "bg-neutral-100 text-neutral-700",
  declined: "bg-warning-50 text-warning-700",
  superseded: "bg-neutral-100 text-neutral-500",
};

export function PIAdoptionPanel() {
  const [statusFilter, setStatusFilter] = useState("");
  const params = useMemo(() => {
    const next: Record<string, string> = {};
    if (statusFilter) next.adoption_status = statusFilter;
    return next;
  }, [statusFilter]);
  const { data, isLoading } = useQuery({
    queryKey: ["pi-adoptions", params],
    queryFn: () => listIndicatorAdoptions(params),
  });
  const rows = Array.isArray(data) ? data : [];

  const columns: DataTableColumn<IndicatorAdoption>[] = [
    {
      key: "indicator",
      header: "Indicator",
      render: (row) => (
        <div>
          <p className="font-semibold text-neutral-900">{row.federal_indicator_name}</p>
          <p className="text-xs text-neutral-500">{row.federal_indicator_code}</p>
        </div>
      ),
    },
    { key: "state", header: "State", render: (row) => row.state_name || "—" },
    {
      key: "status",
      header: "Status",
      render: (row) => (
        <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_TONES[row.adoption_status] ?? "bg-neutral-100 text-neutral-700"}`}>
          {row.adoption_status}
        </span>
      ),
    },
    { key: "version", header: "Version", render: (row) => row.adopted_version || "—" },
    { key: "by", header: "Adopted by", render: (row) => row.adopted_by_name || "—" },
    { key: "at", header: "Adopted at", render: (row) => (row.adopted_at ? new Date(row.adopted_at).toLocaleDateString() : "—") },
  ];

  return (
    <div className="grid gap-4">
      <div className="flex flex-wrap items-center gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
        <label className="text-sm font-semibold text-neutral-700" htmlFor="pi-adoption-status">Status</label>
        <select
          id="pi-adoption-status"
          className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm"
          value={statusFilter}
          onChange={(event) => setStatusFilter(event.target.value)}
        >
          <option value="">All statuses</option>
          <option value="available">Available</option>
          <option value="adopted">Adopted</option>
          <option value="cloned">Cloned</option>
          <option value="declined">Declined</option>
          <option value="superseded">Superseded</option>
        </select>
        <span className="ml-auto text-sm text-neutral-500">{rows.length} record{rows.length === 1 ? "" : "s"}</span>
      </div>
      {isLoading ? (
        <p className="text-sm text-neutral-500">Loading adoption records…</p>
      ) : (
        <DataTable<IndicatorAdoption> columns={columns} rows={rows} empty="No adoption records yet. Share an active indicator with states to begin tracking adoption." />
      )}
    </div>
  );
}
