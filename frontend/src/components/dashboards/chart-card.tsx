import type { ReactNode } from "react";

interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
}

export function ChartCard({ title, subtitle, children }: ChartCardProps) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="mb-3">
        <h3 className="text-sm font-bold text-neutral-900">{title}</h3>
        {subtitle ? <p className="mt-1 text-xs text-neutral-500">{subtitle}</p> : null}
      </div>
      {children}
    </div>
  );
}
