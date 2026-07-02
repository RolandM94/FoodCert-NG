"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { getApiErrorMessage } from "@/lib/api/client";
import {
  adoptFederalIndicator,
  calculateIndicatorNow,
  cloneFederalIndicator,
  listPerformanceIndicators,
  publishPerformanceIndicator,
  setIndicatorLifecycle,
  shareIndicatorToStates,
} from "@/lib/api/performance-indicators";
import type { MEIndicator } from "@/types/standards";

const LIFECYCLE_TONES: Record<string, string> = {
  active: "bg-brand-50 text-brand-700",
  published: "bg-brand-50 text-brand-700",
  draft: "bg-neutral-100 text-neutral-700",
  under_review: "bg-info-50 text-info-700",
  paused: "bg-warning-50 text-warning-700",
  deprecated: "bg-warning-50 text-warning-700",
  archived: "bg-neutral-100 text-neutral-500",
};

export function LifecycleBadge({ status }: { status: string }) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${LIFECYCLE_TONES[status] ?? "bg-neutral-100 text-neutral-700"}`}>
      {status.replace(/_/g, " ")}
    </span>
  );
}

export function PILibraryTable({
  mode,
  filterParams,
  emptyMessage,
}: {
  mode: "federal" | "state-adopt" | "state-own";
  filterParams?: Record<string, string>;
  emptyMessage: string;
}) {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [feedback, setFeedback] = useState<{ tone: "ok" | "error"; text: string } | null>(null);

  const params = useMemo(() => ({ ...(filterParams ?? {}) }), [filterParams]);
  const { data, isLoading } = useQuery({
    queryKey: ["pi-library", mode, params],
    queryFn: () => listPerformanceIndicators(params),
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["pi-library"] });
    queryClient.invalidateQueries({ queryKey: ["pi-overview"] });
  };

  const runAction = useMutation({
    mutationFn: async ({ id, action }: { id: string; action: string }) => {
      if (action === "publish") return publishPerformanceIndicator(id);
      if (action === "pause") return setIndicatorLifecycle(id, "paused");
      if (action === "resume") return setIndicatorLifecycle(id, "active");
      if (action === "archive") return setIndicatorLifecycle(id, "archived");
      if (action === "share") return shareIndicatorToStates(id);
      if (action === "adopt") return adoptFederalIndicator(id);
      if (action === "clone") return cloneFederalIndicator(id);
      if (action === "calculate") return calculateIndicatorNow(id);
      throw new Error(`Unknown action ${action}`);
    },
    onSuccess: (_result, variables) => {
      setFeedback({ tone: "ok", text: `Action “${variables.action}” completed.` });
      invalidate();
    },
    onError: (error, variables) => {
      setFeedback({ tone: "error", text: getApiErrorMessage(error, `Could not ${variables.action} the indicator.`) });
    },
  });

  const rows = useMemo(() => {
    const all = Array.isArray(data) ? data : [];
    const needle = search.trim().toLowerCase();
    if (!needle) return all;
    return all.filter(
      (row) =>
        row.indicator_name.toLowerCase().includes(needle)
        || row.indicator_code.toLowerCase().includes(needle)
        || (row.category || "").toLowerCase().includes(needle),
    );
  }, [data, search]);

  const actionButton = (row: MEIndicator, action: string, label: string, tone: "primary" | "secondary" | "danger" = "secondary") => {
    const toneClass =
      tone === "primary"
        ? "bg-brand-600 text-white hover:bg-brand-700"
        : tone === "danger"
          ? "bg-danger-50 text-danger-700 hover:bg-danger-100"
          : "border border-neutral-200 bg-white text-neutral-700 hover:bg-neutral-50";
    return (
      <button
        key={action}
        className={`inline-flex h-8 items-center rounded-md px-2.5 text-xs font-semibold disabled:opacity-50 ${toneClass}`}
        disabled={runAction.isPending}
        onClick={() => {
          setFeedback(null);
          runAction.mutate({ id: row.id, action });
        }}
        type="button"
      >
        {label}
      </button>
    );
  };

  const columns: DataTableColumn<MEIndicator>[] = [
    {
      key: "name",
      header: "Indicator",
      render: (row) => (
        <div>
          <p className="font-semibold text-neutral-900">{row.indicator_name}</p>
          <p className="text-xs text-neutral-500">{row.indicator_code}</p>
        </div>
      ),
    },
    { key: "category", header: "Category", render: (row) => row.category || "—" },
    { key: "owner", header: "Owner", render: (row) => row.owner_type },
    { key: "frequency", header: "Frequency", render: (row) => row.reporting_frequency },
    { key: "lifecycle", header: "Status", render: (row) => <LifecycleBadge status={row.lifecycle_status} /> },
    {
      key: "latest",
      header: "Latest",
      render: (row) => (
        <span className="tabular-nums">
          {row.latest_value ?? "—"}
          {row.target_value != null ? <span className="text-xs text-neutral-500"> / {row.target_value}</span> : null}
        </span>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      render: (row) => (
        <div className="flex flex-wrap gap-1.5">
          {mode === "federal" && row.lifecycle_status === "draft" ? actionButton(row, "publish", "Publish", "primary") : null}
          {mode === "federal" && row.lifecycle_status === "active" ? actionButton(row, "share", "Share to states") : null}
          {mode === "federal" && row.lifecycle_status === "active" ? actionButton(row, "pause", "Pause") : null}
          {mode === "federal" && row.lifecycle_status === "paused" ? actionButton(row, "resume", "Resume", "primary") : null}
          {mode === "federal" && ["paused", "deprecated"].includes(row.lifecycle_status) ? actionButton(row, "archive", "Archive", "danger") : null}
          {mode === "federal" || mode === "state-own" ? actionButton(row, "calculate", "Calculate now") : null}
          {mode === "state-adopt" ? actionButton(row, "adopt", "Adopt", "primary") : null}
          {mode === "state-adopt" && row.allow_state_clone ? actionButton(row, "clone", "Clone") : null}
        </div>
      ),
    },
  ];

  return (
    <div className="grid gap-4">
      {feedback ? (
        <p className={`rounded px-3 py-2 text-sm font-semibold ${feedback.tone === "ok" ? "bg-brand-50 text-brand-700" : "bg-danger-50 text-danger-700"}`}>
          {feedback.text}
        </p>
      ) : null}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
        <input
          className="h-10 w-full max-w-xs rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm"
          placeholder="Search indicators…"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
        <span className="text-sm text-neutral-500">{rows.length} indicator{rows.length === 1 ? "" : "s"}</span>
      </div>
      {isLoading ? (
        <p className="text-sm text-neutral-500">Loading indicators…</p>
      ) : (
        <DataTable<MEIndicator> columns={columns} rows={rows} empty={emptyMessage} />
      )}
    </div>
  );
}
