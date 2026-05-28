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
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <Icon className="text-brand-deep" size={18} aria-hidden="true" />
      <p className="mt-2 text-xs font-bold uppercase text-slate-500">{label}</p>
      <p className="text-2xl font-bold text-slate-950">{value}</p>
      {subtitle ? <p className="mt-1 text-xs text-slate-400">{subtitle}</p> : null}
      {children}
    </div>
  );
}
