"use client";

import type { LucideIcon } from "lucide-react";
import { AlertCircle } from "lucide-react";

import { DashboardCard } from "@/components/ui/dashboard-card";

type SnapshotCard = {
  label: string;
  value: string | number | null | undefined;
  icon: LucideIcon;
  detail?: string;
};

export function OperationalSnapshot({
  title,
  description,
  cards,
  loading = false,
  error = "",
}: {
  title: string;
  description: string;
  cards: SnapshotCard[];
  loading?: boolean;
  error?: string;
}) {
  return (
    <section className="grid gap-4">
      <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-brand-700">{title}</p>
            <p className="mt-2 max-w-3xl text-sm text-neutral-600">{description}</p>
          </div>
        </div>
        {loading ? (
          <p className="mt-4 text-sm font-semibold text-neutral-500">Loading operational snapshot...</p>
        ) : null}
        {error ? (
          <div className="mt-4 flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        ) : null}
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {cards.map((card) => (
          <DashboardCard
            key={card.label}
            label={card.label}
            value={card.value}
            icon={card.icon}
            detail={card.detail}
          />
        ))}
      </div>
    </section>
  );
}
