import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

interface KPICardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  subtitle?: string;
  children?: ReactNode;
}

export function KPICard({ label, value, icon: Icon, subtitle, children }: KPICardProps) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <Icon className="text-brand-700" size={18} aria-hidden="true" />
      <p className="mt-2 text-xs font-bold uppercase text-neutral-500">{label}</p>
      <p className="text-2xl font-bold text-neutral-900">{value}</p>
      {subtitle ? <p className="mt-1 text-xs text-neutral-400">{subtitle}</p> : null}
      {children}
    </div>
  );
}
