import { AlertTriangle } from "lucide-react";

export function ConfirmDialog({
  title,
  description,
  actionLabel
}: {
  title: string;
  description: string;
  actionLabel: string;
}) {
  return (
    <div className="rounded-lg border border-warning-100 bg-warning-50 p-4">
      <div className="flex gap-3">
        <AlertTriangle aria-hidden="true" className="mt-0.5 text-warning-700" size={18} />
        <div>
          <h3 className="text-sm font-bold text-amber-950">{title}</h3>
          <p className="mt-1 text-sm text-amber-900">{description}</p>
          <button className="mt-3 rounded bg-warning-700 px-3 py-2 text-sm font-bold text-white">{actionLabel}</button>
        </div>
      </div>
    </div>
  );
}
