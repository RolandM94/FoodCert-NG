"use client";

import type { LucideIcon } from "lucide-react";
import {
  Activity,
  AlertTriangle,
  BadgeCheck,
  Banknote,
  Building2,
  ClipboardCheck,
  Clock3,
  FileCheck2,
  Gauge,
  RefreshCw,
  Scale,
  ShieldCheck,
  TrendingDown,
  TrendingUp,
  UsersRound,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { listKpiCards, resolveKpiCard } from "@/lib/api/kpi-cards";
import type { KpiCard as KpiCardConfig, KpiCardResolved } from "@/types/kpi-cards";

/** Registry icon names -> lucide components (extend as the library grows). */
const ICON_MAP: Record<string, LucideIcon> = {
  Activity,
  AlertTriangle,
  BadgeCheck,
  Banknote,
  Building2,
  ClipboardCheck,
  Clock3,
  FileCheck2,
  Gauge,
  RefreshCw,
  Scale,
  ShieldCheck,
  UsersRound,
};

const STATUS_STYLES: Record<string, { border: string; iconWrap: string; value: string }> = {
  good: { border: "border-neutral-200", iconWrap: "bg-brand-50 text-brand-700", value: "text-neutral-900" },
  warning: { border: "border-warning-500", iconWrap: "bg-warning-50 text-warning-700", value: "text-warning-700" },
  critical: { border: "border-danger-500", iconWrap: "bg-danger-50 text-danger-700", value: "text-danger-700" },
  none: { border: "border-neutral-200", iconWrap: "bg-brand-50 text-brand-700", value: "text-neutral-900" },
};

function TrendChip({ trend }: { trend: NonNullable<KpiCardResolved["trend"]> }) {
  const rising = trend.direction === "up";
  const flat = trend.direction === "flat";
  const Icon = rising ? TrendingUp : TrendingDown;
  return (
    <span className="mt-2 inline-flex items-center gap-1 rounded-full bg-neutral-100 px-2 py-0.5 text-xs font-semibold text-neutral-700">
      {flat ? null : <Icon aria-hidden size={12} />}
      {flat ? "no change" : `${rising ? "↑" : "↓"}${Math.abs(trend.delta)}`} {trend.label}
    </span>
  );
}

/**
 * The single, surface-agnostic KPI card renderer.
 *
 * Give it a `config` (registry entry) — it resolves its own value — or pass
 * pre-resolved data (published snapshots) via `resolved` to skip fetching.
 */
export function KpiCard({ config, resolved: preResolved }: { config: KpiCardConfig; resolved?: KpiCardResolved | null }) {
  const resolveQuery = useQuery({
    queryKey: ["kpi-card-resolve", config.id],
    queryFn: () => resolveKpiCard(config.id),
    enabled: !preResolved,
    staleTime: 60_000,
  });
  const resolved = preResolved ?? resolveQuery.data ?? null;
  const status = resolved?.status ?? null;
  const styles = STATUS_STYLES[status ?? "none"] ?? STATUS_STYLES.none;
  const Icon = ICON_MAP[config.icon] ?? Gauge;

  return (
    <div className={`rounded-lg border bg-white p-4 shadow-sm ${styles.border}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">{config.title}</p>
          <p className={`mt-2 text-2xl font-bold tabular-nums ${styles.value}`}>
            {resolveQuery.isLoading && !preResolved ? "…" : resolved?.formatted ?? "—"}
          </p>
          {resolved?.trend ? <TrendChip trend={resolved.trend} /> : null}
        </div>
        <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${styles.iconWrap}`}>
          <Icon aria-hidden size={20} />
        </div>
      </div>
      {config.detail ? <p className="mt-3 text-sm text-neutral-600">{config.detail}</p> : null}
      {resolveQuery.isError && !preResolved ? (
        <p className="mt-2 text-xs font-semibold text-danger-700">Could not load this KPI.</p>
      ) : null}
    </div>
  );
}

/** Convenience: mount a card straight from the shared library by its registry code. */
export function KpiCardByCode({ code }: { code: string }) {
  const libraryQuery = useQuery({ queryKey: ["kpi-card-library"], queryFn: () => listKpiCards(), staleTime: 300_000 });
  const config = (libraryQuery.data ?? []).find((card) => card.code === code);
  if (libraryQuery.isLoading) {
    return <div className="rounded-lg border border-neutral-200 bg-white p-4 text-sm text-neutral-500 shadow-sm">Loading KPI…</div>;
  }
  if (!config) {
    return <div className="rounded-lg border border-dashed border-neutral-300 bg-white p-4 text-sm text-neutral-500">KPI card “{code}” is not in the library.</div>;
  }
  return <KpiCard config={config} />;
}
